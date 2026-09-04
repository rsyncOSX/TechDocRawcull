+++
author = "Thomas Evensen"
title = "Image Pipeline and Caching"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "The RawCull scan, decode, thumbnail, preview, memory-cache, and disk-cache pipeline."
tags = ["rawcull", "images", "thumbnails", "caching"]
categories = ["technical details"]
weight = 20
+++

# Image Pipeline and Caching

This is the path a RAW file takes from "user picked a folder" to "sharp
preview pixels on screen", and the multi-layer cache system that keeps that
fast on repeat visits. Read
[Concurrency Architecture](../01-concurrency-architecture/) first — this
document assumes you know the actor/TaskGroup/Sendable vocabulary from there.

## End-to-end flow

```
User selects folder
        │
        ▼
DiscoverFiles (actor)  ──►  finds candidate RAW file URLs
        │
        ▼
ScanFiles (actor)      ──►  reads EXIF/metadata per file → [FileItem]
        │                    (feeds RawCullViewModel.files)
        ▼
ScanAndCreateThumbnails (actor, background, low priority)
        │                    proactively decodes + caches grid thumbnails
        ▼
   ┌─────────────────────────────┐
   │   SharedMemoryCache (RAM)   │   ← only RequestThumbnail admits here
   │   DiskCacheManager (disk)   │   ← both scan-preload and requests write here
   └─────────────────────────────┘
        ▲
        │  (user scrolls the grid / opens loupe)
        │
RequestThumbnail (actor)  ──►  coalesces duplicate concurrent requests,
        │                       checks memory cache → disk cache → decode
        ▼
   CGImage/NSImage rendered by a SwiftUI Image/ThumbnailComponents view
```

For full-size zoom/export, a parallel path exists through
`ScanAndExtractJPGs` / `ExtractAndSaveJPGs` / `SaveJPGImage`, backed by
`FullSizeJPGDiskCache` instead of `DiskCacheManager`.

## Discovery and metadata scanning

- **`DiscoverFiles`** walks the selected folder (non-recursive) and returns
  candidate RAW file URLs.
- **`ScanFiles`** turns URLs into `FileItem`s, reading EXIF metadata, capture
  date, and focus-point data (via `RawParserKit`/exiftool-backed helpers).
  This populates `RawCullViewModel.files`, the root array everything else —
  filtering, rating lookup, grid rendering — derives from.

Both run as `actor`s so metadata extraction happens off the main actor while
still reporting progress (count, ETA) back to the UI via `@MainActor
@Sendable` callback closures defined in `Model/Handlers/CreateFileHandlers.swift`.

## Two cache tiers, two purposes

RawCull deliberately keeps **two separate NSCache-backed stores**, because
the grid and the loupe/zoom view have very different quality/size needs:

| Tier | Actor | Content | Typical size |
|---|---|---|---|
| Grid | `SharedMemoryCache` (grid cache) + `DiskCacheManager` | ~200px JPEG thumbnails, quality ~0.7 | Hundreds of items, small footprint |
| Preview | `SharedMemoryCache` (preview cache) + `FullSizeJPGDiskCache` | Full-size decoded previews, quality ~0.85 | Dozens of items, large footprint |

Don't confuse the two when debugging a "wrong image size" issue — a file can
be present in one tier and absent from the other.

### Cache sizing

`CacheConfig` / `CacheRecommendationPolicy` (`Model/Cache/CacheConfig.swift`)
compute memory-cache byte limits from the machine's physical RAM tier
(≥64 GB / ≥32 GB / below), with an **adaptive** mode that grows the limits
further when a large fraction of RAM is currently free, and shrinks them
under memory pressure (see the pressure handling in
[Concurrency Architecture](../01-concurrency-architecture/)). The user
can also set explicit MB caps in Settings, which act as a hard ceiling on
top of whatever the adaptive policy recommends
(`CacheSettingsLimits.memoryMinMB/MaxMB`, `gridMinMB/MaxMB`).

## `RequestThumbnail`: the single front door for grid images

`Actors/RequestThumbnail.swift` is the only actor that **admits** images into
`SharedMemoryCache`'s memory cache. Its `requestThumbnail(for:targetSize:purpose:)`
does, in order:

1. Coalesce with any in-flight request for the same `ThumbnailCacheKey` (see
   the `CheckedContinuation` pattern in the concurrency doc) — if a decode
   for this exact file/size/purpose is already running, just wait for it.
2. Check `SharedMemoryCache` — a hit returns immediately with no disk I/O.
3. Check `DiskCacheManager`'s on-disk JPEG cache — a hit decodes the cached
   JPEG (cheaper than a fresh RAW decode) and **then** admits it to memory.
4. Fall back to a full RAW decode via `rawLoader` (`RawParserKitImageLoader`,
   backed by the external `RawParserKit` package), encode a JPEG, save it to
   disk in a detached background task, and admit the decoded image to
   memory.

### The scan-never-admits invariant

`ScanAndCreateThumbnails` (the proactive preloader that runs right after a
folder scan) explicitly **does not** call into `SharedMemoryCache`'s
admission path — it only writes to the **disk** cache. Only
`RequestThumbnail`, driven by genuine UI requests (scrolling, opening the
loupe), admits to the memory cache. This is a deliberate LRU-ordering
decision: if preload admitted eagerly, it would evict already-cached
UI-relevant items in scan order, and the user's first real browse would see
a near-100% cache miss rate. Preloading still pays off because the *disk*
cache is warm, so `RequestThumbnail`'s disk-hit branch is cheap even on a
cold memory cache.

## RAW decoding

`RawImageLoading` (`Model/RawImageLoading.swift`) defines the
`RawImageLoading` protocol RawCull decodes RAW files through, implemented by
`RawParserKitImageLoader` (backed by the external `RawParserKit` package).
Two extraction modes exist, selectable per-export
(`RawCull/Model/ViewModels` / `ExtractJPGExportMode`):

- **`embeddedJPG`** — pull the small preview JPEG most RAW files already
  embed; fast, but limited resolution/quality.
  Wired to `ExtractAndSaveJPGs.exportFailureMessage(for:)` and
  `SaveJPGImage`.
- **`demosaicedRAW`** — fully demosaic the RAW sensor data into a full-size
  JPEG (`SonyRawFormat.createFullSizeJPEG`); slower but full resolution.

`RawImageLoadingConcurrency.batchExtractionLimit` governs how many of these
decodes run concurrently in a batch export (scaled to
`ProcessInfo.activeProcessorCount`).

## Cache keys and orientation

`ThumbnailCacheKey` (`Model/Cache/ThumbnailCacheKey.swift`) identifies a
cached image by source file + requested pixel size + purpose (grid vs.
preview), so the same file can have independent grid- and preview-tier cache
entries without collision. `FullSizeJPGDiskCache` normalizes EXIF orientation
during **load** (not encode), via an `OrientationNormalizedImageLoader` — if
you see an image rotated wrong, check that path first.

## Memory pressure adaptation (recap)

`SharedMemoryCache` listens for kernel memory-pressure events and adjusts
both cache tiers' limits live: 60% shrink in place on `.warning`, full flush
plus a 50 MiB floor on `.critical`, restore to the computed adaptive limit on
`.normal`. `MemoryViewModel` (`Model/ViewModels/MemoryViewModel.swift`)
surfaces `SharedMemoryCache.shared.currentPressureLevel` plus system/app
memory stats (read via `mach`/`vm_statistics64` calls, moved off the main
actor with `Task.detached`) for the Settings memory-usage UI.

## Where to look when extending this

- Adding a new derived-image size/purpose → extend `ThumbnailCacheKey.Purpose`
  and thread it through `RequestThumbnail`, not a new ad hoc cache.
- Adding a new batch background job → model it as an `actor` with a
  `TaskGroup` + `RawImageLoadingConcurrency`-style limit, following
  `ScanAndCreateThumbnails`/`ScanAndExtractJPGs`.
- Changing cache size defaults → `CacheConfig`/`CacheRecommendationPolicy`,
  not scattered literals.
