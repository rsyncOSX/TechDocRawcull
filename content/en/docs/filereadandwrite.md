---
title: File Read and Write Reference
description: Files, folders, and persistent data touched by RawCull
weight: 70
mermaid: true
lastmod: 2026-08-20
---

# File Read and Write Reference

This page lists the main places RawCull reads and writes files. Use it before
changing sandbox access, cache locations, persistence, or export behavior.

## File Map

| File/folder                                        | Access                                   | Owner                                                                |
| -------------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------- |
| User-selected catalog folder                       | Read                                     | `RawCullViewModel`, `ScanFiles`, `DiscoverFiles`, parser package     |
| RAW files (`.arw`, `.nef`)                         | Read                                     | scan, thumbnails, focus parsing, zoom, export, diagnostics           |
| `focuspoints.json` beside catalog                  | Read optional                            | `ScanFiles` fallback                                                 |
| App Support `savedfiles.json` and backups          | Read/write/move                          | `CullingModel`, `ReadSavedFilesJSON`, `WriteSavedFilesJSON`          |
| App Support `settings.json`                        | Read/write                               | `SettingsViewModel`, `SettingsFileWriter`                            |
| App Support analysis artifacts and burst snapshots | Read/write/delete                        | `PerFileAnalysisArtifactStore`, `BurstAnalysisCache`                 |
| App Support AI models and licence acceptance       | Read/write                               | AI model download/resource and licence services                      |
| Thumbnail cache directory                          | Read/write/delete                        | `DiskCacheManager`                                                   |
| Full-size JPEG preview cache                       | Read/write/prune                         | `FullSizeJPGDiskCache`, `ZoomPreviewHandler`                         |
| Subject-mask cache                                 | Read/write/delete                        | PhotoAIKit subject-mask stores configured by `RawCullAIIntegration`  |
| Exported `.jpg` files in a chosen destination      | Write                                    | `ExtractAndSaveJPGs`, `SaveJPGImage`                                 |
| Temporary rsync include lists / process streams    | Write/delete/read                        | `ExecuteCopyFiles`, `ArgumentsSynchronize`, `PrepareOutputFromRsync` |
| Security-scoped bookmarks                          | Read/write UserDefaults                  | `OpencatalogView`, copy workflow                                     |
| AI selections and managed-model metadata           | Read/write UserDefaults and app metadata | `RawCullAISettingsModel`, model download service                     |
| Similarity diagnostics log                         | Append/read/truncate                     | `SimilarityDiagnosticsLog`                                           |

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
| Embedded JPG   | `FullSizePreviewLoader.loadEmbeddedPreview` | Original basename plus `.jpg`          |
| Demosaiced RAW | `SonyRawFormat.createFullSizeJPEG`          | Original basename plus `_demosaic.jpg` |

The actor bounds parallel extraction, tracks progress and per-file failures, and
passes JPEG `Data` to `SaveJPGImage`; non-Sendable image objects do not cross
the save boundary. `SaveJPGImage` writes atomically.
`RawCullViewModel.startSelectedJPGExtraction` starts destination security-scoped
access before constructing the actor and stops it on the main actor after the
awaited result returns.

## rsync Copy Workflow

The copy workflow is separate from thumbnail/scoring export. It uses `rsync` to
copy selected RAW files based on rating/tag choices.

Main files:

| File                           | Role                                            |
| ------------------------------ | ----------------------------------------------- |
| `CopyFilesView.swift`          | UI and execution lifecycle                      |
| `OpencatalogView.swift`        | Source/destination picker and bookmark creation |
| `ExecuteCopyFiles.swift`       | Process owner and progress/result state         |
| `ArgumentsSynchronize.swift`   | Builds rsync arguments                          |
| `PrepareOutputFromRsync.swift` | Parses process output                           |
| `RemoteDataNumbers.swift`      | Summarizes copied file counts and sizes         |

`ExecuteCopyFiles.startcopyfiles` first derives the selected filenames from the
current `RawCullViewModel`. It then creates an operation-unique file under
`Application Support/RawCull/CopyLists/`. Each UTF-8 filename is terminated by
NUL, and rsync receives `--from0` plus `--files-from=<path>`. This preserves
spaces and newlines without converting the list into command-line arguments.

Source and destination folders are restored from security-scoped bookmarks or
fall back to selected paths. Both successful scope acquisitions remain owned by
the `ExecuteCopyFiles` instance while `/usr/bin/rsync` runs. Process handlers
stream progress and output back to main-actor state.

Startup returns a typed `CopyStartupFailure` for unavailable arguments, missing
model state, an empty selection, Application Support/include-list failures,
security-scope failures, and process-launch failures. All failure paths call the
same idempotent cleanup used by completion, cancellation, `close()`, and
deinitialization. Cleanup finishes the progress stream, stops both acquired
scopes exactly once, removes only this operation's include-list file, and
releases process handlers.

## Security-Scoped Bookmarks

The copy workflow stores source and destination bookmark `Data` in
`UserDefaults` after the user picks folders. Picker access is balanced
immediately after bookmark creation. At execution time, `ExecuteCopyFiles`
resolves each bookmark with `.withSecurityScope` and starts a new
operation-lifetime scope.

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

`RawFileDiagnostics` reads RAW files and parser metadata for developer-facing
reports. It can call both Sony and Nikon parser diagnostics and report ImageIO
properties, embedded JPEG locations, focus-parser output, and format
classification.

`SimilarityDiagnosticsLog` appends structured backend/fallback events to an
Application Support log. It replaces the log after it reaches 5 MiB and supports
read and clear operations for the diagnostics window. Diagnostics should avoid
exposing full user paths in ordinary presentation.

RAW-file diagnostics are read-only. Similarity diagnostics may write only their
bounded app-owned log.

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
