---
title: File Read and Write Reference
description: Files, folders, and persistent data touched by RawCull
weight: 70
mermaid: true
---

# File Read and Write Reference

This page lists the main places RawCull reads and writes files. Use it before changing sandbox access, cache locations, persistence, or export behavior.

## File Map

| File/folder | Access | Owner |
|---|---|---|
| User-selected catalog folder | Read | `RawCullViewModel`, `ScanFiles`, `DiscoverFiles`, parser package |
| RAW files (`.arw`, `.nef`) | Read | scan, thumbnails, focus parsing, zoom, export, diagnostics |
| `focuspoints.json` beside catalog | Read optional | `ScanFiles` fallback |
| App Support `savedfiles.json` | Read/write | `CullingModel`, `ReadSavedFilesJSON`, `WriteSavedFilesJSON` |
| App Support burst cache | Read/write/delete | `BurstAnalysisCache` |
| Thumbnail cache directory | Read/write/delete | `DiskCacheManager` |
| Full-size JPEG preview cache | Read/write/prune | `FullSizeJPGDiskCache`, `ZoomPreviewHandler` |
| Extracted `.jpg` sidecars | Write | `ExtractAndSaveJPGs`, `SaveJPGImage` |
| rsync include files / process output | Write/read process stream | `ExecuteCopyFiles`, `ArgumentsSynchronize`, `PrepareOutputFromRsync` |
| Security-scoped bookmarks | Read/write UserDefaults | `OpencatalogView`, copy workflow |
| Settings | Read/write UserDefaults | `SettingsViewModel` |

## Catalog Reads

The active catalog comes from the sidebar folder selection. `RawCullViewModel.startCatalogLoad(for:)` starts security-scoped access and then runs the scan.

Catalog reads include:

- directory enumeration,
- URL resource values,
- EXIF metadata via ImageIO,
- MakerNote focus points via `RawParserKit`,
- embedded thumbnails/JPEGs,
- optional `focuspoints.json`.

`DiscoverFiles` uses `RawFormatRegistry.allExtensions` so it follows the parser registry.

## App Support Files

Application Support is used for durable app-owned data:

```text
~/Library/Application Support/RawCull/
```

Important files:

| File | Purpose |
|---|---|
| `savedfiles.json` | Ratings, sharpness/saliency persistence, manual burst winner overrides |
| burst-analysis cache files | Derived similarity/sharpness/grouping/ranking artifacts |

`savedfiles.json` is written atomically. Burst-analysis cache validity is checked against file metadata and algorithm/signature versions before reuse.

## Cache Files

Generated caches live under the user cache directory for the RawCull app identifier. They are performance data, not source-of-truth data.

| Cache | Purpose |
|---|---|
| Thumbnail disk cache | Stores generated JPEG thumbnails for preload/on-demand loading |
| Full-size JPEG disk cache | Stores larger embedded JPEG previews for zoom |

Deleting these caches should only make RawCull slower until they are rebuilt. It should not lose ratings or manual decisions.

## Exported JPEGs

`ExtractAndSaveJPGs` extracts embedded JPEG previews from RAW files and writes `.jpg` files next to the source RAW files through `SaveJPGImage`.

Because this writes into user-selected folders, it depends on the active security-scoped catalog access. The export path encodes image data before crossing concurrency boundaries where needed.

## rsync Copy Workflow

The copy workflow is separate from thumbnail/scoring export. It uses `rsync` to copy selected RAW files based on rating/tag choices.

Main files:

| File | Role |
|---|---|
| `CopyFilesView.swift` | UI and execution lifecycle |
| `OpencatalogView.swift` | Source/destination picker and bookmark creation |
| `ExecuteCopyFiles.swift` | Process owner and progress/result state |
| `ArgumentsSynchronize.swift` | Builds rsync arguments |
| `PrepareOutputFromRsync.swift` | Parses process output |
| `RemoteDataNumbers.swift` | Summarizes copied file counts and sizes |

Source and destination folders are restored from security-scoped bookmarks or fall back to selected paths.

## Security-Scoped Bookmarks

The copy workflow stores bookmarks in `UserDefaults` after the user picks folders. The catalog browsing flow uses an active security-scoped URL owned by `RawCullViewModel` instead of creating a bookmark at picker time.

See [Security-Scoped URLs](../security/) for lifecycle details.

## Settings

`SettingsViewModel` stores user settings with `UserDefaults`. Settings affect:

- thumbnail sizes,
- cache size maximums,
- focus/scoring options,
- memory/cache defaults.

Background actors use `SettingsViewModel.shared.asyncgetsettings()` to snapshot settings into a `SavedSettings` value before using them off the main actor.

## Diagnostics Reads

`RawFileDiagnostics` reads RAW files and parser metadata for developer-facing reports. It can call both Sony and Nikon parser diagnostics and report ImageIO properties, embedded JPEG locations, focus-parser output, and format classification.

Diagnostics should be read-only.

## What To Check When Changing This Area

- Writes outside the app container need active security-scoped access.
- App-owned durable data belongs in Application Support, not Caches.
- Rebuildable performance data belongs in Caches, not Application Support.
- If a cache stores derived algorithm output, include enough version/signature metadata to reject stale data.
- Keep process-output parsing separate from process lifecycle management.
