+++
author = "Thomas Evensen"
title = "Culling and Persistence"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "RawCull ratings, filters, catalog switching, and debounced persistent storage."
tags = ["rawcull", "culling", "ratings", "persistence"]
categories = ["technical details"]
weight = 30
+++

# Culling and Persistence

"Culling" is RawCull's core job: attach a rating/status to each RAW file so
the photographer can filter down to keepers and export just those. This
document covers the model that owns that decision, how it's filtered for
display, and how it's saved to disk.

## The model: `CullingModel`

`CullingModel` (`Model/ViewModels/CullingModel.swift`) is a
`@MainActor @Observable` class, constructed exactly once by
`RawCullViewModel` (`var cullingModel = CullingModel()` — the comment above
it says explicitly "This is the only place CullingModel is initialised").
It holds:

```swift
private(set) var savedFiles = [SavedFiles]()
private(set) var persistenceError: String?
private(set) var persistenceLoadFailure: SavedFilesReadFailure?
private(set) var hasUnsavedChanges = false
```

`SavedFiles` (`Model/JSON/SavedFiles.swift`) is a `Codable` struct keyed by
catalog: one entry per source folder the user has ever culled, each holding
an array of `FileRecord`s (filename, rating, tagged date, and related
metadata). Because the model is keyed by catalog URL rather than a single
flat list, switching between catalogs never loses another catalog's ratings
— they simply live at a different index in `savedFiles`.

### Dependency injection for testability

`CullingModel.init` takes its save delay, save handler, and load handler as
injectable parameters with production defaults:

```swift
init(
    saveDelayNanoseconds: UInt64 = 350_000_000,
    saveHandler: @escaping @Sendable ([SavedFiles]) async throws -> Void
        = { try await WriteSavedFilesJSON.write($0) },
    loadHandler: @escaping @MainActor () -> SavedFilesReadResult
        = { ReadSavedFilesJSON().read() },
)
```

Tests can substitute an in-memory handler or a different delay without
touching disk — this pattern (protocol/closure injection with a live
default) recurs throughout the codebase (`ScanAndExtractJPGs`'s `rawLoader`,
`ExecuteCopyFiles`'s `fileManager`, etc.).

## Rating flow

1. **UI action** (star key, menu command, batch rating) calls into
   `RawCullViewModel+Culling.updateRating(for:rating:)`.
2. That calls `CullingModel.updateRating(fileName:rating:in:)` →
   `updateRatings(fileNames:rating:in:)`, which:
   - Resolves (or creates) the catalog's entry in `savedFiles` via
     `ensureCatalog(_:dateStart:)`.
   - Upserts a `FileRecord` per filename (`upsertRecord`), updating rating +
     tagged date if a record already exists, appending a new one otherwise.
   - Calls `scheduleSave()`.
3. `refreshCullingDerivedState()` back on `RawCullViewModel+Culling` rebuilds
   the O(1) `ratingCache: [String: Int]` (filename → rating) and
   `taggedNamesCache: Set<String>`, then re-applies the active
   `RatingFilter` to recompute `filteredFiles`.

`ratingCache` exists purely for performance: without it, checking a file's
rating while rendering hundreds of grid cells would be an O(n) linear scan
of `savedFiles` per cell. It's rebuilt lazily, only after a mutation, not on
every filter/render pass.

## Debounced, revisioned persistence

`scheduleSave()` doesn't write to disk synchronously — rapid rating changes
(rating ten photos in a few seconds) would otherwise cause ten redundant
disk writes. Instead:

```swift
private func scheduleSave() {
    persistenceRevision &+= 1
    let snapshot = savedFiles          // capture value-type snapshot now
    let revision = persistenceRevision
    saveTask?.cancel()                 // supersede any pending save
    hasUnsavedChanges = true
    saveTask = Task {
        try? await Task.sleep(nanoseconds: saveDelayNanoseconds)   // 350ms
        guard !Task.isCancelled else { return }
        _ = await persist(snapshot, revision: revision)
    }
}
```

Every mutation cancels the previous pending save and schedules a new one, so
only the *last* snapshot within a 350ms debounce window actually reaches
disk. `persist(_:revision:)` only clears `hasUnsavedChanges` if its
`revision` still matches the model's current `persistenceRevision` — if a
newer save has already been scheduled by the time an older one's write
completes, the older write doesn't incorrectly mark state as "saved".

`persist` delegates the actual write to `saveHandler`, whose production
implementation is `WriteSavedFilesJSON.write(_:)`
(`Model/JSON/WriteSavedFilesJSON.swift`), an `actor` that:

1. Encodes `[SavedFiles]` to JSON.
2. Backs up the existing file to `savedfiles.backup.json`.
3. Writes atomically (`Data.write(options: .atomic)`) to
   `~/Library/Application Support/RawCull/savedfiles.json`.

## Failure handling and recovery

`CullingModel` surfaces both load and save failures as `@Observable` state
rather than throwing past its callers, so the UI can react:

- **Load failure** — `persistenceLoadFailure: SavedFilesReadFailure?`
  (a corrupted or unreadable `savedfiles.json`). The UI offers to archive the
  broken file (renamed with a timestamp, e.g.
  `savedfiles-corrupt-<timestamp>.json`) and start over with an empty rating
  set, rather than crashing or silently discarding user data.
- **Save failure** — `persistenceError: String?`, with `hasUnsavedChanges`
  left `true` so the user isn't falsely told their ratings are safe; the
  next successful save clears both.

## Filtering: `RatingFilter` and `filteredFiles`

`RatingFilter` (defined in `Main/RawCullFileItem.swift`) is a small enum:

```swift
enum RatingFilter: Hashable {
    case all
    case rejected   // rating == -1
    case keepers    // rating == 0
    case stars(Int) // rating in 2...5
}
```

`RawCullViewModel.filteredFiles` is the projection actually rendered by grid
views; it's recomputed from `files` (all scanned RAW files) through
`catalogDisplayCandidates` (name-sorted/search-filtered) and then
`applyFilters(to:)`, which consults `ratingCache`/`taggedNamesCache` for the
active `ratingFilter`. Grid views never filter `savedFiles` directly — they
always go through this derived, cached projection.

## Catalog model and switching

`ARWSourceCatalog` (`typealias` for `RawCullCore.RawCullSourceCatalog`, an
external-package type) represents one source folder: its URL, display name,
and a macOS **security-scoped bookmark** so RawCull can re-open it across
launches without re-prompting through the file picker (App Sandbox
requirement). `RawCullViewModel` tracks which catalog currently has an
active `startAccessingSecurityScopedResource()` grant
(`activeSecurityScopedURL`) and guarantees it's released
(`stopActiveSecurityScopedAccess()`) both when switching catalogs and in
`isolated deinit`.

Switching `selectedSource` triggers a rescan (`DiscoverFiles`/`ScanFiles`,
see [Image Pipeline and Caching](../02-image-pipeline-and-caching/)) and
reloads that catalog's ratings from the already-in-memory `savedFiles`
(`rebuildRatingCache()`) — no new disk read is needed unless the app just
launched, since all catalogs' records live in the one JSON file.

## Where to look when extending this

- **New per-file culling attribute** (e.g. a new flag) → add a field to
  `FileRecord`, thread it through `upsertRecord`, and expose a cache similar
  to `ratingCache` if it needs O(1) lookup during rendering.
- **New filter** → extend `RatingFilter` and `applyFilters(to:)`, not a
  parallel ad hoc filtering path.
- **Persistence format changes** → `SavedFiles`/`FileRecord` are plain
  `Codable`; bump/handle schema compatibility in `DecodeSavedFiles.swift` and
  `ReadSavedFilesJSON.swift` the same way the Intelligence subsystem
  versions its caches (see
  [Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/)).
