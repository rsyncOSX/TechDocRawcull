+++
author = "Thomas Evensen"
title = "Concurrency Architecture"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "RawCull actor isolation, structured concurrency, backpressure, cancellation, and request coalescing."
tags = ["rawcull", "swift", "concurrency", "actors"]
categories = ["technical details"]
weight = 10
+++

# Concurrency Architecture

RawCull is a Swift 6 / strict-concurrency codebase. Almost every piece of
mutable shared state — caches, in-flight request tables, coordinators, view
models — is isolated to either an `actor` or `@MainActor`, and cross-boundary
data is required to be `Sendable`. This document is an inventory of that
system and the patterns it relies on, so you can extend it safely.

## The two isolation domains

RawCull's concurrency model boils down to two kinds of isolated types:

1. **`@MainActor @Observable` view/feature models** — own UI-visible state
   and are read/written from SwiftUI views. Examples: `RawCullViewModel`,
   `SettingsViewModel`, `GridThumbnailViewModel`, `MemoryViewModel`,
   `SimilarityScoringModel`, `BurstAnalysisCoordinator`,
   `DeepAIReviewController`, `RawCullIntelligenceRuntime`.
2. **`actor` workers** — own I/O-bound or CPU-bound background work (disk
   caches, file scanning, RAW/JPEG extraction, request coalescing). They are
   invoked with `await` from a `Task` started on the main actor, and they
   report progress back via `@MainActor @Sendable` callback closures rather
   than by mutating view-model state directly.

### Actor inventory

| Actor | File | Responsibility |
|---|---|---|
| `DiskCacheManager` | `Actors/DiskCacheManager.swift` | Grid-thumbnail JPEG disk cache, keyed by a hash of the source file. |
| `FullSizeJPGDiskCache` | `Actors/FullSizeJPGDiskCache.swift` | Full-resolution JPEG disk cache for zoom/loupe. |
| `SharedMemoryCache` | `Actors/SharedMemoryCache.swift` | In-memory `NSCache`-backed image cache with kernel memory-pressure response. |
| `RequestThumbnail` | `Actors/RequestThumbnail.swift` | De-duplicates concurrent thumbnail requests for the same file. |
| `ScanFiles` | `Actors/ScanFiles.swift` | Discovers and reads metadata for RAW files in a folder. |
| `ScanAndCreateThumbnails` | `Actors/ScanAndCreateThumbnails.swift` | Proactively preloads grid thumbnails after a scan. |
| `ScanAndExtractJPGs` | `Actors/ScanAndExtractJPGs.swift` | Extracts full-size preview JPEGs in bulk. |
| `ExtractAndSaveJPGs` | `Actors/ExtractAndSaveJPGs.swift` | User-triggered "export embedded/demosaiced JPEGs" batch job. |
| `SaveJPGImage` | `Actors/SaveJPGImage.swift` | JPEG encode + file write. |
| `ThumbnailLoader` | `Actors/ThumbnailLoader.swift` | Rate-limits concurrent grid-image decode (max ~6 in flight). |
| `ThumbnailPreloadGate` | `Actors/ThumbnailPreloadGate.swift` | De-duplicates grid decode requests that race with preload. |
| `SettingsFileWriter` (private) | `Model/ViewModels/SettingsViewModel.swift` | Atomic settings JSON writes. |
| `WriteSavedFilesJSON` | `Model/JSON/WriteSavedFilesJSON.swift` | Atomic culling-state JSON writes. |
| `BurstAnalysisCache` | `Intelligence/Persistence/BurstAnalysisCache.swift` | Persists burst-analysis snapshots per catalog. |
| `PerFileAnalysisArtifactStore` | `Intelligence/Persistence/PerFileAnalysisArtifactStore.swift` | Persists similarity embeddings per file/backend. |
| `RawCullAIModelResourceManager` | `Intelligence/ModelManagement/RawCullAIModelResourceManager.swift` | Validates AI model bundles, constructs providers. |
| `RawCullAIModelDownloadCoordinator` / `...DownloadService` | `Intelligence/ModelManagement/RawCullAIModelDownloadService.swift` | Background Assets model downloads. |

`RawImageLoadingConcurrency` (`Model/RawImageLoadingConcurrency.swift`) is a
tiny `nonisolated enum` that centralizes the concurrency *limits* everything
above uses:

```swift
nonisolated enum RawImageLoadingConcurrency {
    static var batchExtractionLimit: Int {
        max(1, ProcessInfo.processInfo.activeProcessorCount * 2)
    }
    static var thumbnailPreloadLimit: Int {
        min(4, max(1, ProcessInfo.processInfo.activeProcessorCount / 2))
    }
}
```

Preloading is deliberately capped lower than explicit export, because it's
lower priority than interactive grid browsing and AI inference, which compete
for the same CPU/disk.

## Structured concurrency: `TaskGroup` with manual backpressure

Every batch operation (thumbnail preload, JPEG extraction) uses the same
shape: a `withTaskGroup` loop that calls `await group.next()` once the number
of started tasks reaches the configured limit, so at most N tasks are ever
in flight — no unbounded queue of pending work:

```swift
return await withTaskGroup(of: Void.self) { group in
    let maxConcurrent = RawImageLoadingConcurrency.thumbnailPreloadLimit
    for (index, url) in urls.enumerated() {
        if Task.isCancelled { group.cancelAll(); break }
        if index >= maxConcurrent { await group.next() }   // backpressure
        group.addTask { await self.processSingleFile(url, ...) }
    }
    await group.waitForAll()
}
```
*(`ScanAndCreateThumbnails.swift`)*

Cancellation is checked at multiple points (before the loop, at task entry,
after each `await` boundary, and again before committing results), so a
cancelled batch unwinds quickly instead of finishing wasted work.

## Request coalescing via `CheckedContinuation`

`RequestThumbnail` avoids decoding the same image twice when several UI
elements ask for it concurrently (e.g. scroll-fling revisits a cell that's
already loading). The pattern:

```swift
private struct InFlightRequest {
    let generation: UUID
    let task: Task<Void, Never>
    var waiters: [UUID: CheckedContinuation<CGImage?, Never>]
}
```

- The **first** caller for a given cache key creates a `generation` UUID,
  spawns the decode `Task`, and registers its own continuation as a waiter.
- **Subsequent** callers for the *same key* just add their continuation to
  `waiters` and return — no new work is started.
- When the task finishes, every waiter's continuation is resumed with the
  same result, validated against the stored `generation` so a resumed-but-
  stale finish can't clobber a newer request.
- `withTaskCancellationHandler` removes a waiter's continuation if its own
  `Task` is cancelled while waiting, so continuations can't leak.

`ThumbnailLoader` and `ThumbnailPreloadGate` use the same
continuation/queue idiom to rate-limit and de-duplicate grid decodes.

## Sendable rules at actor boundaries

`CGImage` and `NSImage` are **not** `Sendable` and must never cross an actor
boundary directly. The codebase's consistent rule: **encode to `Data` (or
otherwise convert to a value type) before crossing.**

```swift
/// Accepts pre-encoded JPEG `Data` so callers never need to send a `CGImage`
/// across an actor/task boundary. Encode with `DiskCacheManager.jpegData(from:)`
/// inside the actor that owns the image, then pass the resulting `Data` here.
func save(_ jpegData: Data, for key: ThumbnailCacheKey) async
```

Callers follow the same discipline explicitly, capturing only the
actor reference (never `self`) before hopping to a detached task:

```swift
let dcache = diskCache                       // capture the actor-isolated let
Task.detached(priority: .background) {
    await dcache.save(jpegData, for: cacheKey)   // no implicit self capture
}
```

Everything else that legitimately crosses isolation is either a primitive
(`Int`, `Bool`), a `Sendable` value type (`URL`, `Date`, `CGPoint`), or an
explicitly-marked `nonisolated struct ...: Sendable` (e.g.
`RawImageFileMetadata`, `JPGExportResult`, similarity/burst artifacts used by
the Intelligence layer). Callback closures passed into actors are typed as
`@MainActor @Sendable (Int) -> Void` and only ever move primitive progress
counts back to the main actor.

## Custom synchronization primitives

`SharedMemoryCache` needs synchronous, lock-free reads of counters that
`NSCache` doesn't expose (its cost/count), so it uses `OSAllocatedUnfairLock`
instead of actor hops for those specific fields:

```swift
private let _memCost = OSAllocatedUnfairLock(initialState: 0)
_memCost.withLock { $0 = max(0, $0 - existing.cost) }
```

It also listens for kernel memory-pressure transitions with
`DispatchSource.makeMemoryPressureSource`, bridging the callback (which fires
on a background dispatch queue) back into actor isolation with a plain
`Task { await self.handleMemoryPressureEvent() }`. No `DispatchQueue`,
`NSLock`, or semaphore is used anywhere else — everything else is structured
concurrency plus these two primitives.

Memory pressure response is graduated, not all-or-nothing:

- **Normal** → restore full cache size limits from settings.
- **Warning** → shrink both cache limits to 60% of current *in place*
  (existing entries are evicted lazily by `NSCache`, not flushed), to avoid a
  cascade of re-fetches if the pressure spike is transient.
- **Critical** → flush all cache entries and clamp to a 50 MiB floor.

## A deliberate cache-admission invariant

`ScanAndCreateThumbnails` (background preload) intentionally **never**
admits images into `SharedMemoryCache`'s full-size memory cache — only
`RequestThumbnail` (driven by actual UI requests) does. The code comments
explain why: admitting during scan would immediately evict ~180 items in
LRU order before the user ever looks at them, guaranteeing a near-100%
cache-miss ("boomerang") rate on first browse. Preload still writes to the
**disk** JPEG cache, so `RequestThumbnail`'s disk-cache branch can serve the
first UI request cheaply without a cold RAW decode — it just doesn't warm
the memory cache. If you're debugging "why doesn't this show up after
preload", this is usually why: it's working as designed.

## Generation counters prevent stale results

Several long-running coordinators guard against a slow background
computation completing *after* the user has already moved on (switched
catalogs, started a new burst analysis, etc.) by stamping a `generation`
value at the start of a run and checking it before publishing results:

- `RequestThumbnail.InFlightRequest.generation`
- `BurstAnalysisCoordinator.generation`
- `SimilarityScoringModel`'s indexing/grouping generation tracking

The pattern is always: capture the generation before the `await`, do the
work, then only apply results if the generation (or an `isCurrent()`
callback) still matches on return.

## Cancellation checkpoints

Long batch jobs (`ExtractAndSaveJPGs`, `ScanAndExtractJPGs`) check
`Task.isCancelled` at several points, not just once:

1. Before starting the next item in the loop.
2. On entry to each per-item task.
3. After any `await` boundary (RAW decode, disk I/O).
4. Before committing results/counters.

This keeps a cancelled operation (e.g. the user closes the zoom window or
switches catalogs mid-extraction) from doing meaningfully more work than
necessary, without needing cooperative cancellation to be checked on every
single line.

## Why this matters when you extend the app

- **New background work** should be a new `actor`, not a class with manual
  locking — follow the existing actors as templates.
- **New batch operations** should follow the `TaskGroup` + `group.next()`
  backpressure shape, sized from `RawImageLoadingConcurrency` (or a sibling
  limit you add there) rather than an ad hoc constant.
- **Never pass `CGImage`/`NSImage` across an actor boundary** — encode to
  `Data` first, exactly like `DiskCacheManager.save(_:for:)`.
- **If a computation can outlive its relevance** (catalog switch, cancel,
  settings change), add a generation/identity check before applying its
  result, following `BurstAnalysisCoordinator`'s or `RequestThumbnail`'s lead.
