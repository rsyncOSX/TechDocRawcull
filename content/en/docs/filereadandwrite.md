---
title: File Read and Write Reference
description: Files, folders, and persistent data touched by RawCull
weight: 70
mermaid: true
lastmod: 2026-10-25
---

# File Read and Write Reference

This page lists the main places RawCull reads and writes files. Use it before
changing sandbox access, cache locations, persistence, or export behavior.

## File Map

| File/folder                                        | Access                                   | Owner                                                                |
| -------------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------- |
| User-selected catalog folder                       | Read                                     | `RawCullViewModel`, `ScanFiles`, `DiscoverFiles`, parser package     |
| RAW files (dedicated and generic registered extensions)                 | Read                                     | scan, thumbnails, focus parsing, zoom, export, diagnostics           |
| `focuspoints.json` beside catalog                  | Read optional                            | `ScanFiles` fallback                                                 |
| App Support `savedfiles.json` and backups          | Read/write/move                          | `CullingModel`, `ReadSavedFilesJSON`, `WriteSavedFilesJSON`          |
| App Support `settings.json`                        | Read/write                               | `SettingsViewModel`, `SettingsFileWriter`                            |
| App Support analysis artifacts and burst snapshots | Read/write/delete                        | `PerFileAnalysisArtifactStore`, `BurstAnalysisCache`                 |
| App Support AI models and licence acceptance       | Read/write                               | AI model download/resource and licence services                      |
| Thumbnail cache directory                          | Read/write/delete                        | `DiskCacheManager`                                                   |
| Full-size JPEG preview cache                       | Read/write/prune                         | `FullSizeJPGDiskCache`, `ZoomPreviewHandler`                         |
| Subject-mask cache                                 | Read/write/delete                        | PhotoAIKit subject-mask stores configured by `RawCullAIModelRuntime`  |
| Exported `.jpg` files in a chosen destination      | Write                                    | `ExtractAndSaveJPGs`, `SaveJPGImage`                                 |
| Temporary rsync include lists / process streams    | Write/delete/read                        | `ExecuteCopyFiles`, `ArgumentsSynchronize`, `PrepareOutputFromRsync` |
| Destination security-scoped bookmark               | Read/write UserDefaults                  | `OpencatalogView`, copy workflow                                     |
| AI selections and managed-model metadata           | Read/write UserDefaults and app metadata | `RawCullAISettingsModel`, model download service                     |

## Catalog Reads

The active catalog comes from the sidebar folder selection.
`RawCullViewModel.startCatalogLoad(for:)` starts security-scoped access and then
runs the scan.

Catalog reads include:

- directory enumeration,
- URL resource values,
- EXIF metadata via ImageIO,
- MakerNote focus points via `RawParserKit`,
- embedded thumbnails/JPEGs,
- optional `focuspoints.json`.

`DiscoverFiles` uses `RawFormatRegistry.allExtensions` so it follows the parser
registry.

## App Support Files

Application Support is used for durable app-owned data:

```text
~/Library/Application Support/RawCull/
```

Important files:

| File                                  | Purpose                                                                              |
| ------------------------------------- | ------------------------------------------------------------------------------------ |
| `savedfiles.json`                     | Ratings, sharpness/saliency persistence, and manual burst winner overrides           |
| `savedfiles.backup.json`              | Atomic backup of the previous valid saved-file store before replacement              |
| `savedfiles-corrupt-<timestamp>.json` | User-approved archive of a store that failed decoding                                |
| `settings.json`                       | Thumbnail, cache, scoring, and focus-mask settings                                   |
| `AnalysisArtifacts/`                  | Per-file, descriptor-valid Vision/CLIP similarity artifacts                          |
| `BurstAnalysis/`                      | Derived catalog snapshots containing grouping, ranking, artifacts, and review states |
| `Models/`                             | Installed AI model bundles grouped by model identity                                 |
| `ModelLicenceAcceptances.json`        | Recorded model-licence acceptance state                                              |
| `CopyLists/`                          | Operation-unique NUL-separated rsync include lists, removed during cleanup           |

`savedfiles.json` is written atomically after the old data is copied atomically
to `savedfiles.backup.json`. A decode failure is surfaced to the UI; rating
mutations are blocked until the user retries or explicitly archives the damaged
store. `settings.json`, per-file artifacts, and burst snapshots also use atomic
replacement. Burst-analysis validity is checked against file metadata,
descriptors, artifact digest, and algorithm/signature versions before reuse.

## Cache Files

Generated caches live under the user cache directory for the RawCull app
identifier. They are performance data, not source-of-truth data.

| Cache                                | Purpose                                                                                                            |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Schema-specific thumbnail disk cache | Stores generated JPEG representations keyed by source fingerprint, purpose, requested size, and orientation policy |
| Full-size JPEG disk cache            | Stores larger embedded JPEG previews for zoom                                                                      |
| Subject-mask cache                   | Stores reusable segmentation masks outside the durable app-data namespace                                          |

Deleting these caches should only make RawCull slower until they are rebuilt. It
should not lose ratings or manual decisions.

## Exported JPEGs

`ExtractAndSaveJPGs` exports the current selection into a user-selected
destination catalog. It supports two modes:

| Mode           | Input path                                  | Output name                            |
| -------------- | ------------------------------------------- | -------------------------------------- |
| Embedded JPG   | `EmbeddedJPGExportLoader.jpegData(for:)` | Original basename plus `.jpg`          |
| Demosaiced RAW | `SonyRawFormat.createFullSizeJPEG`          | Original basename plus `_demosaic.jpg` |

The actor bounds parallel extraction, tracks progress and per-file failures, and
passes JPEG `Data` to `SaveJPGImage`; non-Sendable image objects do not cross
the save boundary. `SaveJPGImage` creates files without overwriting. If a name
already exists, it retries with ` (1)`, ` (2)`, and so on; the filesystem
enforces exclusivity for case-insensitive and simultaneous-export collisions.
`RawCullViewModel.startSelectedJPGExtraction` starts destination security-scoped
access before constructing the actor and stops it on the main actor after the
awaited result returns.

## rsync Copy Workflow

The copy workflow is separate from thumbnail/scoring export. It uses `rsync` to
copy selected RAW files based on rating/tag choices.

Main files:

| File                           | Role                                            |
| ------------------------------ | ----------------------------------------------- |
| [CopyFilesView.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Views/CopyFiles/CopyFilesView.swift)          | UI and execution lifecycle                      |
| [OpencatalogView.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Views/CopyFiles/OpencatalogView.swift)        | Destination picker and bookmark creation        |
| [ExecuteCopyFiles.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Model/ParametersRsync/ExecuteCopyFiles.swift)       | Process owner and progress/result state         |
| [ArgumentsSynchronize.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Model/ParametersRsync/ArgumentsSynchronize.swift)   | Builds rsync arguments                          |
| [PrepareOutputFromRsync.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Model/ParametersRsync/PrepareOutputFromRsync.swift) | Parses process output                           |
| [RemoteDataNumbers.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Model/ParametersRsync/RemoteDataNumbers.swift)      | Summarizes copied file counts and sizes         |

`ExecuteCopyFiles.startcopyfiles` first derives the selected filenames from the
current `RawCullViewModel`. It then creates an operation-unique file under
`Application Support/RawCull/CopyLists/`. Each UTF-8 filename is terminated by
NUL, and rsync receives `--from0` plus `--files-from=<path>`. This preserves
spaces and newlines without converting the list into command-line arguments.

The source is the currently selected catalog URL and the destination is restored
only from `destBookmark`; there is no arbitrary path fallback. Both successful
scope acquisitions remain owned by the `ExecuteCopyFiles` instance while
`/usr/bin/rsync` runs. A stale destination bookmark is refreshed while its
resolved grant is active. Process handlers stream progress and a typed
`CopyOutcome` (`success`, `failed`, or `cancelled`) back to main-actor state.

Startup returns a typed `CopyStartupFailure` for unavailable arguments, missing
model state, an empty selection, Application Support/include-list failures,
security-scope failures, and process-launch failures. All failure paths call the
same idempotent cleanup used by completion, cancellation, `close()`, and
deinitialization. Cleanup finishes the progress stream, stops both acquired
scopes exactly once, removes only this operation's include-list file, and
releases process handlers.

## Security-Scoped Bookmarks

The copy workflow stores destination bookmark `Data` in `UserDefaults` after the
user picks a folder. Picker access is balanced immediately after bookmark
creation. At execution time, `ExecuteCopyFiles` starts a fresh scope for the
active catalog URL and resolves `destBookmark` with `.withSecurityScope` for the
operation-lifetime destination scope. Failure asks the user to reopen the
catalog or reselect the destination rather than attempting a plain-path fallback.

The catalog browsing flow is different: `RawCullViewModel` owns one active
security-scoped catalog URL and stops it during catalog transition or successful
application termination. Do not transfer that ownership implicitly to a child
actor.

See [Security-Scoped URLs](../security/) for lifecycle details.

## Settings

`SettingsViewModel` stores its `SavedSettings` value as pretty-printed, sorted
JSON in `Application Support/RawCull/settings.json`, not in `UserDefaults`.
Settings affect:

- thumbnail sizes,
- cache size maximums,
- focus/scoring options,
- memory/cache defaults.

The main-actor model loads once through `ensureLoaded()`. Encoding happens on
the main actor from a consistent observable snapshot, and `SettingsFileWriter`
performs directory creation and atomic writing through an actor. Background
actors use `SettingsViewModel.shared.asyncgetsettings()` to obtain a Sendable
`SavedSettings` value rather than reading observable properties across isolation
boundaries.

AI model selection and copy bookmarks are separate preferences and may still use
`UserDefaults`; do not treat those as part of `settings.json` without an
explicit migration.

## Diagnostics Reads

Combined Review has durable diagnostic/evidence storage in
`Application Support/RawCull/AnalysisArtifacts/CombinedReview/`, owned by
`ReviewArtifactStore`. It stores run manifests, typed stage artifacts, optional
exact PNG inputs and opt-in rejected responses. `maximumInputBytes` defaults to
256,000,000 bytes for retained inputs; this is not a universal limit on every
artifact category. Run inspection is backed by `ReviewDiagnostics` and the
Combined diagnostic views. Retained inputs and rejected model text can contain
photographic content: follow the selected retention policy when sharing bundles.
OSLog and focused tests remain separate diagnostic channels.

## What To Check When Changing This Area

- Writes outside the app container need active security-scoped access.
- App-owned durable data belongs in Application Support, not Caches.
- Rebuildable performance data belongs in Caches, not Application Support.
- Keep `savedfiles.json` backup/corruption recovery semantics when changing
  culling persistence.
- Keep `settings.json` separate from bookmarks and AI-selection preferences
  unless a migration is designed.
- If a cache stores derived algorithm output, include enough version/signature
  metadata to reject stale data.
- Keep process-output parsing separate from process lifecycle management.
- Keep rsync include lists operation-unique and remove them on success, failure,
  cancellation, and deinitialization.
- Balance every successful security-scope start exactly once at the layer that
  owns its lifetime.

## Persistence initialization and recovery

The live `CullingModel` begins `.unloaded`. `ensureLoaded()` coalesces concurrent
callers onto one load task; mutation is admitted only in `.ready` with no load
failure. A missing store means a valid empty start, while a decoding/read failure
preserves the original and enters `.failed`. `flushPersistence()` also ensures
initialization, so switching catalog cannot overwrite an unread store with an
empty snapshot.

`retryCullingPersistence()` retries a failed load or pending save. After a load
recovery, `restoreCullingPresentation()` rebuilds rating lookups, valid scores,
filters and selection. Archive/reset also refreshes the UI when the subsequent
write fails, because the in-memory store has already changed. Failed saves remain
dirty. Rating edits refresh `dateTagged`, including edits of existing records.
See [CullingModel.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Model/ViewModels/CullingModel.swift), [RawCullViewModel+Culling.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Model/ViewModels/RawCullViewModel+Culling.swift) and
[RawCullTests/ReviewPersistenceTests.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCullTests/ReviewPersistenceTests.swift).

`loadPersistedScoringandSaliency()` builds a filename lookup once, validates
signature/size/modification date, and publishes score dictionaries in a batch.
It keeps the first legacy duplicate and accepts AF scores only with a valid AF
point and a finite positive score. This avoids repeated normalization after each
restored item. See [RawCullViewModel+Sharpness.swift](https://github.com/rsyncOSX/RawCull/blob/7b8e200f07ceb8a6f10947236a5f3de5a099fb45/RawCull/Model/ViewModels/RawCullViewModel+Sharpness.swift).

Settings failures are represented separately by `SettingsPersistenceFailure`
with `.load` or `.save`. `SettingsView` exposes the failure and retry/dismiss
controls; a missing settings file uses defaults without reporting corruption.
See [RawCullTests/SettingsPersistenceTests.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCullTests/SettingsPersistenceTests.swift).

## Embedded export is independent of display preview

`EmbeddedJPGExportLoader` reads camera JPEG ranges from ARW, NEF or DNG parser
locations. It validates candidate data as JPEG and returns the original bytes
when standalone orientation is present or the RAW orientation is upright.
Otherwise it normalizes orientation and encodes a standalone JPEG. It does not
export a same-basename sidecar or a lossy display-cache entry. No usable embedded
JPEG is a per-file export failure. The Sony demosaic mode remains a separate
path. [RawCullTests/RawImageLoadingIntegrationTests.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCullTests/RawImageLoadingIntegrationTests.swift) protects this boundary.

## Saved Files and cache deletion in Settings

The old Saved Files menu/sheet presentation has been removed from
`RawCullMainView`. [RawCullApp.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Main/RawCullApp.swift) passes the stable
view model into Settings; [CacheSettingsTab.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Views/Settings/CacheSettingsTab.swift)
shows Saved Files separately from the cache total.

`WriteSavedFilesJSON.diskUsage()` runs through the shared writer actor and sums
the current `savedfiles.json` and `savedfiles.backup.json` sizes. It does not
count corrupt archives or every file in Application Support. The confirmed
Delete Saved Files action calls `clearAllCullingState()`, awaits
`flushPersistence()` and refreshes the size. Persistence errors retain their
existing failure/dirty-state contract; a refreshed byte count is not proof of
a successful write. This operation resets culling records, not source photos.

Delete Cache is a different confirmed operation: it removes saved Combined
Reviews before clearing thumbnail, full-size, similarity and burst caches.
The confirmation includes report history, masks and retained inputs. The button
is disabled while the Combined lease is held. If review deletion throws, the
later purge steps are not executed and the error is surfaced. See
[Cache System]({{< relref "cache.md" >}}) for the category boundary.

Temporary exposure inspection writes neither a RAW editing sidecar nor an
exported JPEG. Generic RAW browsing does not extend embedded-byte export beyond
the loader's ARW/NEF/DNG cases. See
[RAW Formats and Exposure Inspection]({{< relref "raw-inspection.md" >}}).

## Shared review-state serialization

[BurstReviewStateMapping.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Intelligence/BurstAnalysis/BurstReviewStateMapping.swift)
implements snapshot/restore rules for cached analysis and live review. It derives
membership signatures, omits `.none`, filters missing file references and
restores compatible decisions onto current group IDs. Groups without a valid
signature cannot restore state. The stored schema is unchanged.

`BurstReviewSessionModel` owns live decisions; the view model and coordinator
retain persistence orchestration. Thumbnail preload now also owns its saves
through completion: each worker awaits saving before returning its slot. The
interactive save path is unchanged.
