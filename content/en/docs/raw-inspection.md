+++
author = "Thomas Evensen"
title = "RAW Formats and Exposure Inspection"
date = "2026-10-22"
lastmod = "2026-10-22"
description = "Distinguish extension admission, macOS decoding, embedded export, RAW development and display-referred exposure inspection."
weight = 16
mermaid = true
+++

# RAW Formats and Exposure Inspection

RawCull 3.3.5 resolves RawParserKit **1.3.2** at `07801a34a82d7720d301a80724c36a5b8c9f1d6c`.
This adds a generic macOS-backed format route alongside the dedicated Sony,
Nikon and DNG parsers. The app also has a temporary zoom exposure-inspection
mode. These capabilities have separate contracts: discovering a file is not
proof of camera-specific decoding, AF metadata, embedded-byte export or RAW 9.

## Extension admission and camera support

[RawFormatRegistry.swift](https://github.com/rsyncOSX/RawParserKit/blob/07801a34a82d7720d301a80724c36a5b8c9f1d6c/Sources/RawParserKit/RawFormatRegistry.swift) registers
`SonyRawFormat`, `NikonRawFormat`, `DNGRawFormat`, then `GenericRawFormat`.
`format(for:)` lowercases the extension; `allExtensions` is their union. App
discovery and scan admission consume that registry.

| Route | Extensions | Implementation boundary |
| --- | --- | --- |
| Dedicated Sony | `arw` | MakerNote/embedded ranges plus ImageIO and development helpers |
| Dedicated Nikon | `nef` | Nikon MakerNote/embedded ranges plus ImageIO |
| Dedicated DNG | `dng` | TIFF/SubIFD parsing plus ImageIO |
| Generic | `cr2 cr3 crw raf orf rw2 pef ptx srw x3f iiq 3fr fff dcr kdc mrw erf mef mos nrw rwl bay sr2 srf` | System ImageIO/Core Image decoding; no dedicated vendor binary fallback |

The exact generic list is defined in
[GenericRawFormat.swift](https://github.com/rsyncOSX/RawParserKit/blob/07801a34a82d7720d301a80724c36a5b8c9f1d6c/Sources/RawParserKit/GenericRawFormat.swift).
The extension set admits a file for an attempt. Actual camera support depends
on the installed macOS decoder and the file. A recognized extension can still
fail to decode; do not describe the list as a tested camera matrix.

`GenericRawFormat.focusLocation` returns nil. `RawImageLoader.metadata` can
still obtain an AF point from standard EXIF SubjectArea. It does not invent
vendor MakerNote evidence. Generic size thresholds are 25/10 megapixels and
compression labels cover the small standardized TIFF subset; unknown codes
remain explicitly unknown.

## Follow a generic thumbnail and preview

[GenericRawThumbnailExtractor.swift](https://github.com/rsyncOSX/RawParserKit/blob/07801a34a82d7720d301a80724c36a5b8c9f1d6c/Sources/RawParserKit/GenericRawThumbnailExtractor.swift)
uses `CancellableImageIOWork` at user-initiated QoS. It asks ImageIO for a
bounded, transformed thumbnail, then redraws it to 8-bit sRGB RGBA with the
requested interpolation quality. Source creation, generation and context
failures stay typed thumbnail errors. There is no manual search through an
unknown vendor container when ImageIO fails.

[GenericEmbeddedPreviewExtractor.swift](https://github.com/rsyncOSX/RawParserKit/blob/07801a34a82d7720d301a80724c36a5b8c9f1d6c/Sources/RawParserKit/GenericEmbeddedPreviewExtractor.swift)
has a default two-operation limiter and a utility-QoS blocking bridge. It scans
ImageIO subimages, accepts JFIF or TIFF compression 6/7 as JPEG candidates and
chooses the greatest reported width. The target cap is 4320 px normally or
8640 px for `fullSize`. Wider candidates use native downsampling. The extractor
leaves preview orientation unapplied so the facade can apply source orientation
once. Missing candidates return nil; cancellation checkpoints and cache cleanup
surround the synchronous ImageIO work.

The generic heuristic has no vendor-specific TIFF classifier. Keep dedicated
DNG parsing rules distinct from this ImageIO-only candidate search. Package
fixtures in [GenericEmbeddedPreviewExtractorTests.swift](https://github.com/rsyncOSX/RawParserKit/blob/07801a34a82d7720d301a80724c36a5b8c9f1d6c/Tests/RawParserKitTests/GenericEmbeddedPreviewExtractorTests.swift)
protect the implemented behavior, not every real camera container.

## Display, inspection and export are different paths

| Operation | Current input and behavior |
| --- | --- |
| Browsing thumbnail | Registry and `RawImageLoader` facade; may decode a generic RAW |
| Embedded display preview | `FullSizePreviewLoader` can use a sidecar, display cache or package preview |
| Embedded JPEG export | `EmbeddedJPGExportLoader` reads ARW/NEF/DNG byte ranges; other extensions return nil |
| Normal developed-RAW display | `ZoomPreviewHandler` uses the helper named `SonyRawFormat.createFullSizeJPEG`, requests RAW 9 and caches `.developedRAW` |
| Exposure inspection | Separate serialized `CIRAWFilter` renderer with temporary EV/tone settings; no export/cache write |

The helper name is a concrete call boundary, not a guarantee that every
registry extension supports full development. The system filter determines
whether an attempted input can be developed. In particular, generic browsing
support does not extend the export loader's explicit three-format switch.
See [EmbeddedJPGExportLoader.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/EmbeddedJPGExportLoader.swift) and
[ZoomPreviewHandler.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/Handlers/ZoomPreviewHandler.swift).

## Enter and leave exposure inspection

[ZoomSessionModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/ZoomSessionModel.swift) snapshots source
selection, current/committed EV and clipping visibility before selecting
`.developedRAW` and enabling inspection. Ending inspection restores that
snapshot. A selected-file reset ends inspection and resets EV to zero.
No editing sidecar is written by this mode.

[RAWExposureInspectionControls.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Views/ZoomViews/RAWExposureInspectionControls.swift) keeps a
local slider draft from −5 to +5 EV in 0.1 steps. Dragging updates the small
control view; release updates committed EV and triggers rendering. Reset
commits zero. Closing inspection or pressing Escape restores the earlier
session state; Escape during inspection does not close the entire zoom overlay.
Navigation is blocked by session policy, and the keyboard controller suppresses
recognized navigation/rating/source actions. This is an inspection workflow,
not RawBrowse's persistent RAW 9 editor.

## Rendering and resource ownership

The private `RAWExposurePreviewRenderer` actor in `ZoomPreviewHandler.swift`
serializes inspection renders and lazily constructs its `CIContext` on its own
executor. The operation retains catalog access through completion and checks
cancellation before and after expensive phases. Its synchronous Core Image
portion cannot be interrupted in the middle of a native render.

The current sequence is:

1. Create `CIRAWFilter`; select a preferred RAW 9 decoder if available.
2. Apply requested exposure; set `boostShadowAmount = 2`.
3. On macOS 26 or later, enable highlight recovery when the filter supports it.
4. Apply `CIHighlightShadowAdjust` with highlight amount 0.25 and shadow amount 0.
5. Render through a half-float working context to an 8-bit sRGB display image.

These adjustments change the inspected render. The result bypasses the normal
developed-JPEG cache and export pipeline. Serialization bounds simultaneous
inspection work; it does not make a full-resolution render inexpensive or
establish a free-memory admission budget.

## Histogram and clipping have different predicates

Both products sample the completed display render, after its EV and tone
adjustments. They cannot establish sensor saturation or recoverable RAW detail.

| Product | Sample cap | Near-white rule | Near-black rule |
| --- | --- | --- | --- |
| [Raster warning overlay](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/Handlers/RAWPreviewClippingOverlay.swift) | Longest side 2048 px | All RGB channels ≥254 | All RGB channels ≤1 |
| [RGB histogram and percentages](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Views/Histogram/RAWExposureHistogramView.swift) | Longest side 512 px | Any RGB channel ≥254 | Any RGB channel ≤1 |

The overlay draws near-white pixels red and near-black pixels blue with alpha
180. The histogram has 256 bins per channel, normalized against the largest
bin across channels. Its fractions count a pixel once when any channel meets
the threshold. A saturated red pixel can contribute to the near-white
percentage without a white-clipping overlay pixel. That difference follows
the current code; the two displays must not be described as identical tests.

Both calculations run through explicit concurrent functions and check
cancellation. Their view tasks key off image object identity; the clipping
task also includes whether the warning is enabled for a developed source.

## Read and verify the boundaries

Start with registry tests, then generic preview tests in RawParserKit. In
RawCull, read [RawImageLoadingIntegrationTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/RawImageLoadingIntegrationTests.swift) for
display/export separation, [ZoomSessionModelTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/ZoomSessionModelTests.swift)
for snapshot/restore, and [ZoomKeyboardControllerTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/ZoomKeyboardControllerTests.swift)
for suppressed inspection actions. Those tests do not qualify camera coverage,
exposure recovery accuracy or the current histogram predicates on real files.
Record OS/decoder, camera, render source and actual pixels when validating
those photographic behaviors.
