+++
author = "Thomas Evensen"
title = "Detailed Focus Mask Computation"
date = "2026-08-21"
lastmod = "2026-11-25"
weight = 42
tags = ["focus mask", "sharpness", "focus", "vision", "metal", "saliency"]
categories = ["technical details"]
mermaid = true

reviewed_commit = "328b570bf14d44bcf33efc58dc23da94bfadf439"
reviewed_version = "3.5.0"
reviewed_build = 469
reviewed_on = "2026-11-25"
review_scope = "Rewrote for PhotoAnalysisKit 1.4.1: fixed threshold, capture fallbacks, gate order and calibration scale."
+++

# Detailed Focus Mask Computation

This page follows visible focus-mask rendering at **PhotoAnalysisKit 1.4.1**,
revision **2f41e8b756f006e0218f86b103801ebb47cf8983**, the version RawCull 3.5.0
resolves. The largest change since the earlier edition (1.3.1) is the threshold: it
is now a fixed cutoff and no longer adapts to each image.

The focus mask is not the camera's AF-point marker. The marker reports where the
camera attempted focus. The mask is a package-generated bitmap of selected
edge-detail evidence. The AF point can guide selection, but it is never painted
as the mask by itself.

RawCull owns the SwiftUI trigger, image and metadata supplied to the package,
task lifetime, and overlay presentation. PhotoAnalysisKit owns normalization,
saliency, evidence selection, Laplacian generation, patch ranking, thresholding,
morphology, colorization, clipping, and mask diagnostics.

For shared ownership, persistence, calibration, and scalar score behavior, see
[Focus Mask And Sharpness](../focusmask/).

## Data Shapes And The Overlay Boundary

```mermaid
flowchart LR
    VIEW["SwiftUI view<br/>NSImage or CGImage"] --> FM["@MainActor FocusMaskModel"]
    FM --> INPUT["PhotoAnalysisInput<br/>CGImage<br/>ISO, aperture, AF CGPoint?"]
    INPUT --> PA["PhotoAnalyzer"]
    PA --> NORM["normalized sRGB CGImage"]
    NORM --> CI["CIImage RGBAf analysis"]
    CI --> VALUES["Float edge samples<br/>saliency rectangles<br/>FocusPatchRanking[]"]
    VALUES --> EVIDENCE["FocusEvidence<br/>regions, confidence, threshold, coverage"]
    VALUES --> MASKCI["thresholded/colorized CIImage"]
    MASKCI --> OUT["CGImage focus mask"]
    OUT --> ADAPT["NSImage when required"]
    ADAPT --> OVERLAY["SwiftUI Image overlay<br/>presentation boundary"]
    EVIDENCE --> BREAKDOWN["SharpnessBreakdown diagnostics"]
```

`CGImage` is the public decoded-image boundary. Package internals create
`CIImage` values and render RGBAf edge-energy samples with a reusable
`CIContext`. The returned `CGImage` contains only the overlay bitmap; RawCull
positions it over the displayed image. The package does not retain a SwiftUI
view, app model, URL, or persistence object.

## Call Paths

| RawCull context       | Model call                       | Package facade                       | Evidence behavior                                                                                                               |
| --------------------- | -------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| Main thumbnail/detail | `generateFocusMask`              | `PhotoAnalyzer.focusMask`            | Can reuse existing `FocusEvidence`; classification is skipped and a saved winning saliency rectangle avoids a new saliency pass |
| Zoom overlay          | `generateFocusMaskWithBreakdown` | `PhotoAnalyzer.analyzeWithFocusMask` | Recomputes saliency, scalar breakdown, evidence, and mask together                                                              |
| Comparison grid       | `generateFocusMaskWithBreakdown` | `PhotoAnalyzer.analyzeWithFocusMask` | Same aligned diagnostic path per comparison image                                                                               |
| Review photo layer    | `generateFocusMask`              | `PhotoAnalyzer.focusMask`            | No saved evidence, so subject isolation runs a saliency pass on the retained overview                                           |

The RawCull entry files are:

- [Views/ThumbnailComponents/LoupeMainImageView.swift](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Views/ThumbnailComponents/LoupeMainImageView.swift);
- [Views/ZoomViews/ZoomOverlayView.swift](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Views/ZoomViews/ZoomOverlayView.swift);
- [Views/ComparisonGridView/ComparisonGridImageCoordinator.swift](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Views/ComparisonGridView/ComparisonGridImageCoordinator.swift);
- [Model/ViewModels/FocusandSharpness/FocusMaskModel.swift](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Model/ViewModels/FocusandSharpness/FocusMaskModel.swift).

Views snapshot the effective config, inject ISO, aperture, and normalized AF
point, cancel a previous mask task when image or config identity changes, and
check cancellation before publishing the result.

## Which Values Affect What

The categories below are important when tuning the mask.

### Scalar Score Values

These change package scalar analysis and therefore belong in
`SharpnessAnalysisDescriptor`:

- pre-blur radius;
- border inset;
- salient weight and explicit override;
- subject-size factor;
- silhouette-penalty strength;
- broad/center/neighborhood AF radii used by scoring evidence;
- fine-detail blend;
- classification policy;
- the stable scoring gain and algorithm/policy versions.

ISO and aperture also change scalar analysis, but are per-image inputs rather
than descriptor configuration. Photo type and quality change scalar output
indirectly by applying the values above.

### Mask Presentation Values

These change only the rendered overlay or its visibility:

| Value                           | Current default | Effect                                                              |
| ------------------------------- | --------------: | ------------------------------------------------------------------- |
| `threshold`                     |            0.46 | The cutoff itself, in edge-energy units, clamped to 0.01–0.95       |
| `dilationRadius`                |             0.0 | Optionally connects thresholded edge pixels                         |
| `erosionRadius`                 |             0.0 | Optionally removes isolated/small responses                         |
| `featherRadius`                 |             0.5 | Softens the clipped mask alpha                                      |
| `showRawLaplacian`              |           false | Debug early return before threshold, patches, color, and morphology |
| `guaranteeVisibleFocusEvidence` |           false | Compatibility property; no longer lowers the render threshold      |
| `minimumEvidenceCoverage`       |           0.001 | Compatibility property retained with the public configuration       |
| `isolateMaskToSubject`          |            true | Chooses subject/AF search regions rather than the whole frame       |

The final mask uses a single warm red/orange color matrix: red 1.0, green 0.22,
blue 0.02, alpha 0.92 before SwiftUI compositing.

### Shared Evidence Values

Some values affect both analysis evidence and rendering even though the final
mask threshold itself never becomes a scalar multiplier:

- pre-blur radius, energy gain, ISO, aperture blur damp, and image resolution
  determine the shared primary Laplacian;
- border inset excludes scalar border samples (the mask has no border inset, its
  input is clamped to the extent instead);
- saliency candidates and AF point determine scoring regions and potential mask
  search regions;
- AF radii determine scalar evidence regions and which mask region can be
  selected;
- existing `FocusEvidence` can make mask selection follow a previous score.

### Calibration Output

Calibration returns
`FocusCalibrationResult(threshold, sampleCount, p50, p90, p95, p99, measuredLongSide)`.
RawCull applies only **threshold** to the active config. The percentiles and sample
count are diagnostics. `measuredLongSide` is the median long side of the images the
energies came from. Edge energy depends on decode size, so a threshold fits masks
drawn from images near that size. Calibration changes visual threshold policy; it does not
rescale stored scalar scores.

## Stage 1: Normalize And Resolve Per-Image Configuration

`PhotoAnalyzer.focusMask` and `analyzeWithFocusMask` normalize the input
`CGImage` to sRGB. They copy the caller's `SharpnessConfiguration`, then override
it with capture metadata that exists:

```text
config.iso          = capture ISO, else the configured ISO
config.apertureHint = from a finite, positive aperture, else the configured hint
```

Aperture at or below f/5.6 is wide, at or above f/8 is landscape, and the interval
between is mid.

Saliency is awaited through `VisionRequestGate` *before* the render worker starts, so
no pool thread waits for Vision. The Core Image work then runs in an explicitly
`@concurrent` task with a cancellation handler. A result that arrives after
cancellation is discarded.

## Stage 2: Obtain Saliency And Score Evidence

The simple facade follows this rule:

```text
saved evidence supplied      -> use its winningSaliencyRect, even when that is nil
else isolateMaskToSubject    -> run saliency, without classification
else                         -> no salient region
```

The diagnostic facade always detects saliency, optionally classifies, computes a
`SharpnessBreakdown`, then gives the resulting evidence to mask rendering. That
keeps the displayed patch, score diagnostics, and saliency decision from the
same analysis pass.

The evidence can request one of:

- AF center;
- AF neighborhood;
- broad AF point;
- saliency;
- mixed AF and saliency;
- global;
- none.

If the requested evidence is unavailable, rendering falls back in this order:
broad AF, saliency, then global.

## Stage 3: Scale And Build The Primary Laplacian

The input `CIImage` is transformed by the requested mask scale. RawCull's
`FocusMaskAnalysisResolutionPolicy.prepare` returns every decoded preview pixel,
so view code must choose an appropriate decode before this call. The package
builds a dedicated native-pixel focus-mask detail image with clamped edges and
the following pre-blur:

```text
focus-mask pre-blur = max(0.35, primary preBlurRadius * 0.52)
```

Native-mask mode disables resolution scaling and preserves the input extent.
The scalar scoring path continues to use its resolution-aware primary and
optional fine-detail passes.

The underlying scalar edge pipeline is:

```text
ISO factor:
  below 800          1.0
  800...3199         linear 1.0 -> 1.6
  3200 and above     linear tail capped at 2.2

resolution factor =
  clamp(sqrt(max(longestSide, 512) / 512), 1, 3)

blur radius =
  min(preBlurRadius * ISO factor * resolution factor * aperture damp, 100)

Laplacian =
  abs(8 * center - 8 neighbors)
  collapsed with [0.299, 0.587, 0.114]
  multiplied by energyMultiplier
```

Landscape aperture damp is 0.8; wide and mid are 1.0. The input is clamped to its
extent before the blur, so the photo border is not turned into a false edge.

### Raw Laplacian Debug Mode

When `showRawLaplacian` is true, the package crops the boosted Laplacian to the
scaled image extent and returns it immediately. It records the saliency/AF
region source, but does **not**:

- build or select patches;
- apply the visual threshold;
- threshold or colorize edges;
- erode, dilate, thin, clip, or feather the mask.

Use this mode to inspect the edge-energy input, not the final overlay.

## Stage 4: Resolve Search Regions

With subject isolation enabled, the package converts normalized Vision and AF
coordinates into pixel rectangles. AF Y is inverted when moving between the
view/AF convention and Core Image pixel space.

It also creates two tighter AF rectangles from defaults:

```text
AF center half-radius       0.025 of image dimensions
AF neighborhood half-radius 0.075
broad AF half-radius         config.afRegionRadius
```

Search regions are selected from the requested evidence. Mixed evidence searches
AF and saliency separately. Global/none searches the whole image. With subject
isolation disabled, the whole image becomes the saliency-shaped selection and
the search is effectively global.

Every focus-mask region uses the same native-pixel detail source described in
Stage 3. The mask is not center-weighted around the AF point. This 0.52 factor
is **mask selection and rendering policy**; scalar quality's second pass uses a
different 0.58 factor and blend.

## Stage 5: Generate Candidate Patches

For each bounded search region:

```text
patch width =
  min(max(region width * 0.34, image width * 0.035), image width * 0.14)

patch height =
  min(max(region height * 0.34, image height * 0.035), image height * 0.14)

grid step = patch dimension * 0.50
```

If the AF-centered patch overlaps at least 75% of its intended size, it is
added. The renderer also appends a separate 6%-of-image AF patch when an AF
point exists.

Each patch records:

- robust p90...p97 tail detail relative to p20;
- micro-contrast standard deviation;
- coverage above an adaptive patch threshold;
- normalized distance to AF and whether it contains AF;
- interior versus silhouette fraction;
- ring, compact-detail, and linear-edge shape evidence;
- a below-AF penalty and eye/head heuristic adjustment.

## Stage 6: Rank Patches

The current composite is:

```text
robust tail
+ micro contrast * 0.35
+ coverage * 0.08
+ AF proximity * 0.12
+ interior bonus (0.03 when not touching search border)
- silhouette * (0.18 for AF-anchored regions, otherwise 0.45)
+ eye/head adjustment

eye/head adjustment =
  ring detail * 0.10
+ compact detail * 0.08
- linear edge * 0.10
- below-AF penalty

below-AF penalty =
  clamp((distance below AF - 0.025) / 0.15, 0, 1) * 0.18
```

AF proximity falls linearly to zero at normalized distance 0.20. Composite
scores are floored at zero.

For AF-anchored evidence, the nearest patch is promoted ahead of the strongest
only when it is not already strongest and the strongest is less than 1.15 times
the nearest. Selection then walks descending composite score, rejects patches
with overlap ratio 0.55 or greater, and keeps at most three.

These rankings are visual-evidence selection and diagnostics. Scalar scoring
does use the best AF-local and salient-interior patch's **robust tail score** as
a conservative 25% refinement of broad subject evidence, but it does not use the
rendered mask threshold, morphology, color, or rendered coverage.

## Stage 7: Choose The Visual Threshold

```text
threshold = clamp(config.threshold, 0.01, 0.95)     // default 0.46, or the calibration result
```

That is all. The same cutoff applies to every evidence region and every image.
Earlier versions took a percentile of *each image's own* samples. Such a mask always
shows something: a blurred frame gets a low cutoff and lights up as readily as a
sharp one, so two frames of a burst cannot be compared by looking at them. With a
fixed cutoff, less red means less measured edge energy.

The price is that the cutoff must fit the image scale. Calibration measures embedded
previews at a 1616 px target. A mask drawn from a much larger image, for example the
2048 px overview behind the Review photo layer, is judged by a threshold measured at
another scale. `FocusMaskAnalysisResolutionPolicy.calibrationScaled` exists to
resample an image to the calibration size, but no view calls it at this revision.
The views call `prepare`, which returns the image unchanged.

Ranked patches summarize and order local evidence; they do not truncate the visible
map. An adaptive threshold still exists inside patch ranking, where it measures how
much of a patch is covered (percentile 0.88, capped at 0.46). It never reaches the
overlay. The threshold is not relaxed for visibility, `relaxedForVisibility` is
always false, and weak images may return an empty mask.

## Stage 8: Render And Clip

The package performs this sequence:

1. copy the Laplacian red channel into grayscale;
2. apply `CIColorThreshold`;
3. apply morphology minimum with `erosionRadius`, when positive;
4. apply morphology maximum with `dilationRadius`, when positive;
5. colorize to warm red/orange with alpha 0.92;
6. clip the result to the union of the selected search regions;
7. Gaussian-feather with `featherRadius`, when positive;
8. crop to the scaled image extent and create the output `CGImage`.

After morphology and feathering, GPU area reductions compute the fraction of the
selected regions with alpha above 0.05. This final rendered coverage—not a
pre-render sample estimate—is stored in the evidence.

## Stage 9: Return Diagnostics

The mask result updates `FocusEvidence` with:

- visualized region and overlay style;
- all sorted patch rankings;
- effective threshold, coverage, and relaxation flag;
- visualized centroid distance from AF;
- spatial-alignment score and best/second-best dominance;
- silhouette indication;
- high, medium, or low evidence confidence plus a reason.

Confidence rules are intentionally readable:

- no viable patch -> low;
- rendered coverage below 0.001, robust-tail below 0.01, micro-contrast below
  0.005, or patch coverage below 0.001 -> low;
- "strong detail" means robust tail at least 0.05 and micro-contrast at least 0.02;
- AF anchored within normalized distance 0.05 with strong detail -> high;
- AF aligned with measurable but weaker detail -> medium;
- AF farther than 0.05 -> low;
- global with composite at least 0.10 -> medium, otherwise low;
- non-AF subject with strong detail, silhouette below 0.20, and dominance at
  least 1.08 -> high;
- other usable subject evidence -> medium.

The diagnostic facade also records `FocusMaskRegionSource` and the visual
threshold in `SharpnessBreakdown`. RawCull adapts that package breakdown only to
add the selected scoring source.

## SwiftUI Publication And Cancellation

RawCull views own their mask tasks:

- a new image, config, source, or explicit regeneration cancels the old task;
- view disappearance/toggle-off cancels and clears mask state;
- package workers check cancellation before and after Vision, Laplacian, patch,
  and render stages;
- views check cancellation before assigning the returned mask and breakdown.

The package result is a value. It cannot publish into an old view on its own;
the owning SwiftUI task is the final stale-result boundary.

## Debugging A Surprising Mask

1. Confirm the input image, mask scale, ISO, aperture, and normalized AF point.
2. Inspect `winningRegion`, winning saliency rectangle, and region source.
3. Compare AF-center, AF-neighborhood, broad AF, saliency, and global scores.
4. Inspect sorted patch composite components, especially AF distance,
   silhouette, linear-edge, and below-AF penalties.
5. Check the visual threshold, the size it was calibrated at, and the final rendered
   coverage.
6. Enable raw Laplacian mode to separate edge-energy input from threshold and
   morphology.
7. Remember that a strong scalar score and a sparse mask are compatible: the
   mask is permitted to be empty when the evidence gates are not met.

## Protecting Tests

| Stage                                                                                   | Tests                                                          |
| --------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| RawCull facade, Metal resource, returned breakdown, scoring-source adaptation           | [RawCullTests/PhotoAnalysisKitIntegrationTests.swift](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCullTests/PhotoAnalysisKitIntegrationTests.swift)          |
| Public analyze/mask/calibration behavior and cancellation                               | [PhotoAnalysisKitTests/PhotoAnalyzerTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/PhotoAnalyzerTests.swift)               |
| Native-pixel mask detail, full-region rendering, empty weak masks, and final coverage   | [PhotoAnalysisKitTests/FocusMaskAccuracyTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/FocusMaskAccuracyTests.swift)           |
| Robust tail, micro-contrast, ISO curve, aperture gates, failure classification, presets | [PhotoAnalysisKitTests/SharpnessMetricsTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/SharpnessMetricsTests.swift)            |
| Descriptor excludes mask-only presentation and includes scalar policy                   | [PhotoAnalysisKitTests/SharpnessAnalysisDescriptorTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/SharpnessAnalysisDescriptorTests.swift) |
| Bounded input loading and analysis cancellation                                         | [PhotoAnalysisKitTests/PhotoAnalysisBatchTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/PhotoAnalysisBatchTests.swift)          |

## Change Checklist

When changing the mask:

1. classify the value as scalar-affecting, mask-only, shared evidence, or
   calibration output;
2. update the descriptor only for scalar-affecting behavior;
3. verify simple rendering can reuse score evidence without repeating Vision;
4. verify AF and Vision coordinate conversion;
5. test cancellation at the package worker and SwiftUI publication boundaries;
6. inspect raw Laplacian, patch diagnostics, threshold coverage, and final
   overlay as separate stages;
7. update this page and the overview together.

## Presentation after the October viewer refactor

The formula walkthrough above uses the dated package revision. The app's
publication boundary now includes `LoupeFocusPresentationModel` and
`ZoomOverlayAnalysisCoordinator`, with focused raster/canvas views for rendering.
The zoom coordinator snapshots selected file, image identity and source and
rechecks them after analysis. Follow [Viewer Architecture]({{< relref "viewer-architecture.md" >}})
for the current task owners; the small raster view is not an analysis engine.

## Focus overlay and Review subject outline

The host calibrates the focus overlay on embedded previews at a fixed scale. A Review subject outline comes from a retained segmentation mask. Focus check or Full must first produce a usable subject for that photo. The viewer checks the file fingerprint before drawing the retained mask. [Review presets and subject masks]({{< relref "/docs/ai/aiinrawcull.md" >}})
