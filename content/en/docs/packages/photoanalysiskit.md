+++
author = "Thomas Evensen"
title = "How PhotoAnalysisKit Is Constructed"
linkTitle = "PhotoAnalysisKit Architecture"
date = "2026-08-21"
lastmod = "2026-11-25"
description = "A detailed guide to PhotoAnalysisKit's image-analysis boundary, sharpness pipeline, focus evidence, masks, calibration, batching, feature prints, resources, and concurrency."
tags = ["image-analysis", "sharpness", "focus-mask", "vision", "swift-package", "architecture"]
categories = ["technical details"]
mermaid = true
weight = 20
reviewed_commit = "328b570bf14d44bcf33efc58dc23da94bfadf439"
reviewed_version = "3.5.0"
reviewed_build = 469
reviewed_on = "2026-11-25"
review_scope = "Audited 1.4.1: capture fallbacks, fixed threshold, descriptor 2/7, Vision queue and calibration scale."
+++

# How PhotoAnalysisKit Is Constructed

> **Revision audited:** PhotoAnalysisKit `1.4.1` at
> `2f41e8b756f006e0218f86b103801ebb47cf8983`, the version RawCull 3.5.0 resolves.

PhotoAnalysisKit is the reusable measurement layer extracted from RawCull. It
turns a decoded `CGImage` plus neutral capture metadata into sharpness,
saliency, focus evidence, and an optional focus-mask image. It can also create
opaque Apple Vision feature prints.

The package measures a photo; it does not decide whether to keep it. That
distinction prevents image-processing code from becoming coupled to RawCull's
files, settings, views, caches, or culling policy.

## What the 1.4 line changed

Version 1.4.0 moved blocking saliency, classification, face, animal and
feature-print requests onto the shared Vision gate. Version 1.4.1 shares one lazily
initialized Core Image context across focus engine instances. Treat queue admission
and render reuse separately when investigating latency. The real-catalog comparison
in the performance guide evaluated the gate change.
[VisionRequestGate](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/VisionRequestGate.swift) · [FocusMaskEngine](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskEngine.swift) · [Performance measurements]({{< relref "/docs/performance.md" >}})

Earlier 1.3.x releases changed the numbers themselves. Scalar algorithm 7 and the
fixed mask threshold are described in [Detailed Sharpness Scoring]({{< relref "/docs/detailsharpnessscoring.md" >}}#what-changed-since-algorithm-4)
and [Detailed Focus Mask Computation]({{< relref "/docs/detailsfocusmask.md" >}}).

## 1. Begin With The Package Boundary

PhotoAnalysisKit owns:

- sRGB normalization for predictable analysis input;
- Core Image and Metal Laplacian processing;
- Vision saliency and optional subject classification;
- scalar sharpness metrics and failure classification;
- AF-point, subject, local-patch, and global focus evidence;
- focus-mask selection and rendering;
- numeric configuration, presets, quality levels, and analysis identity;
- bounded batch analysis and calibration;
- Vision feature-print generation and native comparison;
- face evidence and animal head/eye regions;
- the process-wide `VisionRequestGate`.

The host application owns:

- RAW, JPEG, or other source decoding;
- file URLs, security-scoped access, and sandbox bookmarks;
- source identity, cache keys, cache directories, and persistence;
- observable task state, progress presentation, and cancellation policy;
- settings labels and saved-settings migration;
- sorting, ratings, burst decisions, and culling actions.

The input boundary is intentionally small:

```mermaid
flowchart LR
    Source["RAW or rendered source"] --> Decoder["Host decoder"]
    Decoder --> Input["PhotoAnalysisInput\nCGImage + ISO + aperture + AF point"]
    Input --> Analyzer["PhotoAnalyzer"]
    Analyzer --> Result["PhotoAnalysisResult\nsaliency + breakdown + optional mask"]
    Result --> Host["Host cache, UI, and culling policy"]
```

PhotoAnalysisKit does not import RawParserKit or RawCullCore. RawCull provides
the adapters between them.

## 2. Read [Package.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Package.swift) As The First Design Document

The manifest declares Swift tools 6.2, Swift 6 language mode, macOS 26, one
library product, and one test target.

```text
PhotoAnalysisKit package
├── PhotoAnalysisKit library
│   ├── public contracts and facade
│   ├── Core Image, Vision, and Accelerate implementation
│   └── packaged default.metallib
└── PhotoAnalysisKitTests
```

There are no third-party package dependencies. The implementation uses Apple
frameworks including Core Graphics, Core Image, Vision, Accelerate, and
Foundation.

The target enables `InferIsolatedConformances` and
`NonisolatedNonsendingByDefault`. The package is therefore built under the same
strict Swift 6 concurrency assumptions as the host without adopting UI
isolation.

## 3. `PhotoAnalysisInput` Is The Decoding Boundary

[Sources/PhotoAnalysisKit/PhotoAnalysisInput.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/PhotoAnalysisInput.swift) defines the package's source
value:

```swift
public struct PhotoAnalysisInput: Sendable {
    public let image: CGImage
    public let iso: Int
    public let aperture: Double?
    public let normalizedAFPoint: CGPoint?
}
```

The AF point uses normalized `0...1` coordinates with the origin at the visual
top-left. This matches the camera metadata shape used by RawCull. Vision uses a
bottom-left coordinate system, so the package performs the vertical conversion
internally.

There are two initializers. The one with `iso:` clamps the value to at least 1 and
records it as capture ISO. The one without it leaves capture ISO unknown. `iso` then
reports 400, but analysis uses the *configured* ISO. Aperture and AF point are
optional because not every image or camera provides them. The package can still
compute a global result when either is absent. `resolvingCaptureSettings(in:)` is
the single place where capture metadata overrides configuration.

This value has no URL or file identifier. Two consequences follow:

1. The package cannot reopen a source behind the host's back.
2. The host must associate returned results with the correct file and invalidate
   them when that file or decode policy changes.

RawCull makes that ownership concrete in `RawCullPhotoAnalysisAdapter`. The
adapter chooses an embedded-preview decode through RawParserKit or a host-owned
RAW demosaic, bounds the requested pixel size, and then constructs
`PhotoAnalysisInput`. It also translates the returned neutral saliency value
into RawCullCore's `SaliencyInfo`. Neither package needs to import the other to
participate in that flow.

`PhotoAnalysisResult` returns:

| Field       | Meaning                                             |
| ----------- | --------------------------------------------------- |
| `saliency`  | Optional neutral subject label and confidence       |
| `breakdown` | Scalar score plus detailed evidence and diagnostics |
| `focusMask` | Optional rendered overlay image                     |
| `score`     | Convenience access to `breakdown.finalScore`        |

An absent breakdown means analysis could not produce a valid result or was
cancelled. It is different from a valid score of zero.

## 4. `PhotoAnalyzer` Is The Public Facade

[Sources/PhotoAnalysisKit/PhotoAnalyzer.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/PhotoAnalyzer.swift) keeps the public entry points
small:

| API                    | Work performed                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------- |
| `analyze`              | Saliency, classification, scalar scoring, and focus evidence; no overlay rendering |
| `analyzeWithFocusMask` | Analysis plus a mask derived from the same evidence                                |
| `focusMask`            | Mask rendering, optionally reusing previously computed evidence                    |
| `calibrate`            | Catalog-sample calibration of the visual edge threshold                            |
| `sharpnessDescriptor`  | Stable identity for cacheable non-mask analysis behavior                           |

The facade contains an immutable `FocusMaskEngine`. Both types are
`@unchecked Sendable` because `CIContext` does not declare sendability even
though this package holds no mutable model or UI state. Every engine uses the same
static `sharedContext`, so creating a `PhotoAnalyzer` is cheap.

For each input, `PhotoAnalyzer` copies the supplied configuration and overrides ISO
and aperture hint where the input has them. Callers can safely reuse one base
configuration across many files.

When a host already stores `SharpnessBreakdown.focusEvidence`, passing it to
`focusMask` avoids repeating the saliency selection step. This makes the
measurement result useful as an input to later presentation work.

## 5. Follow The Scalar Sharpness Pipeline

The core implementation is in [FocusMaskEngine+Scoring.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskEngine+Scoring.swift).

```mermaid
flowchart TD
    Image["CGImage"] --> SRGB["8-bit sRGB normalization"]
    SRGB --> Vision["Vision saliency + optional classification"]
    SRGB --> Preblur["ISO- and aperture-aware Gaussian pre-blur"]
    Preblur --> Laplacian["Metal focusLaplacian kernel"]
    Laplacian --> Samples["Global, saliency, AF, and local-patch samples"]
    Vision --> Samples
    Samples --> Tail["Robust p90-p97 tail scores"]
    Tail --> Blend["Subject/global blend"]
    Blend --> Adjust["Silhouette, subject-size, and blur-gate adjustments"]
    Adjust --> Breakdown["SharpnessBreakdown"]
```

### 5.1 Normalize Before Measuring

`normalizeToSRGB` redraws the input into an 8-bit sRGB RGBA bitmap. The Metal
pipeline therefore receives a predictable pixel format regardless of the source
image's bit depth or color space. If the redraw fails, the function returns nil and
the analysis has no score. Energies are measured on encoded sRGB; a linear working
space would change both calibration and scores.

### 5.2 Find Candidate Subject Regions

`VNGenerateAttentionBasedSaliencyImageRequest` supplies salient-object
rectangles. Small weak objects are removed, and candidates are ordered using AF
overlap or distance, saliency confidence, interior detail, area, and
deterministic coordinates.

When classification is enabled and a candidate was found, `VNClassifyImageRequest`
supplies a neutral subject label. The package filters out broad environment descriptions and
prefers likely subjects such as animals or people. This label is evidence, not a
keep/reject decision.

### 5.3 Build Edge Energy

The packaged `focusLaplacian` Metal kernel runs after Gaussian pre-blur. The
pre-blur grows with ISO so high-frequency sensor noise is less likely to
masquerade as detail. Aperture hints damp or strengthen parts of this behavior
for wide, middle, and landscape apertures.

The result is rendered as floating-point RGBA data. The red channel carries edge
energy.

### 5.4 Score Several Regions

The engine samples:

- the full image after excluding a configurable border;
- the selected salient region;
- the camera AF region;
- smaller AF-center and AF-neighborhood regions;
- ranked local patches within subject or AF regions.

`robustTailScore` sorts the sample values, measures the p90-p97 energy band
relative to a p20 noise floor, and penalizes a band that is too sparse.
`microContrast` computes the standard deviation of finite edge samples.

The normal blend combines full-frame and subject evidence. When both AF and
saliency scores exist, AF has the larger share of the subject score. A
conservative local-detail component can then refine the broad subject
measurement.

The final value may be adjusted for:

- a silhouette-dominated subject whose strongest energy is mostly at the outer
  rim;
- the area of a saliency-only subject;
- an aperture-aware soft blur gate driven by subject micro-contrast.

`SharpnessBreakdown` preserves the component scores and selected evidence so a
host can explain the result instead of presenting a single unexplained number.

### 5.5 Distinguish Failure Shapes

`FocusFailureKind` classifies the evidence as:

- `.motionBlur` when global, subject, and AF detail were all measured, all are weak,
  and measured micro-contrast is low;
- `.missedFocus` when the frame has usable global detail but the subject is much
  weaker;
- `.none` when neither pattern is established.

These are algorithmic classifications, not final user-facing copy or culling
actions.

## 6. Focus Evidence And Mask Rendering Are Related But Separate

Scalar scoring answers “how much reliable detail is present?” Mask rendering
answers “where should the UI draw visible focused edges?” They share evidence
but have different configuration needs.

`FocusEvidence` records the winning region, AF scores, selected patch rankings,
spatial alignment, dominance, silhouette handling, visual threshold, coverage,
and confidence diagnostics. `FocusPatchRanking` exposes the detail, coverage,
shape, position, and penalty components behind each candidate patch.

The overlay pipeline:

1. chooses AF-center, AF-neighborhood, AF, saliency, mixed, or global evidence;
2. builds one native-pixel fine-detail Laplacian with clamped edges for every region;
3. ranks local patches and selects the best evidence patches;
4. applies the configured threshold, clamped to 0.01–0.95, as one fixed cutoff;
5. applies optional erosion and dilation to the binary edge mask;
6. colorizes, clips to the full search regions, feathers, and crops the mask;
7. measures the fraction of the regions with alpha above 0.05, using GPU reductions;
8. returns updated evidence and render diagnostics with the image.

The renderer deliberately does not lower the threshold to force visible pixels.
`guaranteeVisibleFocusEvidence` remains in the public configuration for source
compatibility, but a weak or unfocused image may produce an empty mask.

`FocusMaskRegionSource` describes whether saliency, AF, both, or neither
provided the overlay region. `FocusEvidenceOverlayStyle` distinguishes subject
edges from global edges. RawCull decides how these neutral values appear in its
interface.

## 7. Configuration, Presets, And Cache Identity

`SharpnessConfiguration` is a value snapshot containing numeric algorithm
settings. It separates host-editable behavior from observable settings models.

Notable groups are:

| Configuration group | Examples                                                     |
| ------------------- | ------------------------------------------------------------ |
| Edge pipeline       | `preBlurRadius`, `threshold`, `energyMultiplier`             |
| Mask morphology     | `dilationRadius`, `erosionRadius`, `featherRadius`           |
| Visibility          | `guaranteeVisibleFocusEvidence`, `minimumEvidenceCoverage`   |
| Region selection    | AF radii, border inset, saliency weight                      |
| Scoring adjustments | subject-size factor, silhouette strength, fine-detail weight |
| Capture hints       | `iso`, `apertureHint`                                        |

`SharpnessPreset` applies high-level subject tuning for automatic, birds and
wildlife, portrait, landscape, or general action use. `SharpnessQuality` selects
fast, balanced, or high-precision fine-detail work. The host may persist its own
UI enums, but should map them into these package values instead of duplicating
constants.

Persisted results need more than a filename. `SharpnessAnalysisDescriptor`
records:

- descriptor schema version;
- scalar algorithm version;
- ISO-scaling policy version;
- aperture-hint policy version;
- every host-configurable value that affects non-mask scoring;
- the fallback ISO and aperture hint (schema 2);
- the stable scoring energy multiplier.

The current values are schema 2, algorithm 7, ISO policy 1 and aperture policy 1.
The descriptor deliberately excludes actual capture ISO and aperture, mask-only
presentation settings, decoded dimensions, source choice, and source-file
identity. A host must account for changes in those inputs and decode policy when
deciding whether a persisted result is reusable.

```text
RawCull persisted sharpness identity
├── PhotoAnalysisKit SharpnessAnalysisDescriptor
├── selected embedded-preview or RAW source
├── effective maximum pixel size
├── app input pipeline version
└── source file size and modification date
```

RawCull's signature records requested effective size rather than every actual
decoded dimension. Per-image metadata is supplied with each analysis input;
source size/modification checks invalidate replaced input files. See
[Focus Mask and Sharpness]({{< relref "../focusmask.md" >}}) for the exact
host signature and restoration contract.

## 8. Bounded Batch Analysis

`PhotoAnalysisBatchRequest<Identifier>` contains an identifier and an async
input provider. The provider inversion is important: PhotoAnalysisKit
coordinates work, while the host retains file access and decoding policy.

`analyzeBatch` starts only up to `maximumConcurrentTasks` child tasks. When one
completes, it enqueues one more request. This prevents a large catalog from
creating an unbounded number of decoded bitmaps.

The API has three ordering and failure guarantees:

- progress is emitted in completion order;
- the returned results preserve request order;
- a decode failure is represented by a result whose `analysis` is `nil`.

If the parent task is cancelled, the method cancels the group and returns `nil`,
telling the host to discard partial results rather than mistake them for a
complete batch.

## 9. Calibration Changes The Overlay, Not The Score

Calibration samples Laplacian energies from host-provided decoded inputs with
bounded concurrency. It downsamples the collected sample set, sorts it, and
returns p50, p90, p95, and p99 statistics plus a clamped threshold at the
requested percentile. `measuredLongSide` reports the median size of the measured
images, because the threshold only fits masks drawn near that size.

At least `minimumSuccessfulImages` inputs must succeed. Cancellation or too few
samples returns `nil`.

Calibration changes only the visual edge threshold. Core sharpness scores keep a
stable gain and do not depend on the current catalog. This prevents the same
photo from receiving a different scalar score merely because unrelated photos
were added or removed.

## 10. Vision Feature Prints Stay Opaque

`VisionFeaturePrintBackend` is an actor that creates a
`VNFeaturePrintObservation` using Vision revision 2 by default. The observation
is securely archived inside `VisionFeaturePrint.payload`.

The value also stores its Vision revision and representation version. Before
comparison, the backend verifies both values, securely unarchives each
observation, and calls Vision's native `computeDistance`.

The host can persist the opaque payload, but it must associate it with
source-file identity. Incompatible prints return `nil`; corrupt archives or
failed Vision operations throw a typed `VisionFeaturePrintError`.

PhotoAnalysisKit intentionally does not copy PhotoAIKit's general similarity
artifact descriptors, CLIP fallback, or batch indexing. It supplies only the
focused Vision measurement primitive.

## 11. Metal Resources Are Part Of The Algorithm

[Sources/PhotoAnalysisKit/Resources/Kernels.ci.metal](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/Resources/Kernels.ci.metal) is the source for the Core
Image kernel. SwiftPM copies Metal source resources but does not compile them
for command-line builds, so the package also checks in `default.metallib`.

[Tools/build_metallib.sh](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tools/build_metallib.sh) regenerates the binary. A kernel change is incomplete
until the checked-in library has been rebuilt and tests have been run. The
binary resource affects algorithm output and must be treated like source, not an
optional deployment file.

## 12. Concurrency And Cancellation

The package uses four complementary techniques:

- **Immutable facade and engine:** callers pass input and configuration
  snapshots; no app state is retained.
- **Explicit concurrent workers:** synchronous Core Image work runs outside caller
  UI isolation while retaining task priority and task-local context. A result that
  arrives after cancellation is dropped.
- **One Vision queue:** every Vision request body runs on `VisionRequestGate.shared`,
  a serial dispatch queue. Callers suspend while they wait, and no cooperative
  thread is blocked. A body must never call the gate again.
- **Bounded task groups:** batch analysis and calibration cap simultaneous
  inputs.
- **Cooperative checks:** expensive stages test cancellation before Vision work,
  rendering, large loops, and result publication.

`@unchecked Sendable` is confined to the immutable Core Image facade and engine.
Public transport values are `Sendable` value types.

## 13. RawCull Call Maps

The app has two deliberate entry paths into the same `PhotoAnalyzer` facade.

```mermaid
flowchart LR
    Settings["Settings + photo-type preset"] --> Sharp["SharpnessScoringModel"]
    Sharp --> Adapter["RawCullPhotoAnalysisAdapter"]
    Adapter --> Input["PhotoAnalysisInput: decoded CGImage + neutral metadata"]
    Input --> Batch["PhotoAnalyzer.analyzeBatch"]
    Batch --> Results["PhotoAnalysisResult per FileItem"]
    Results --> Core["RawCullCore ranking evidence + BurstAnalysisCache"]
```

`SharpnessScoringModel` applies the selected package preset, builds requests
through `RawCullPhotoAnalysisAdapter`, and calls the facade's bounded batch API.
The adapter owns source loading and file-to-identifier mapping; the package owns
measurement and its descriptor. `BurstAnalysisCache` records
`PhotoAnalyzer.sharpnessDescriptor(for:)`, so a configuration-identity change
invalidates incompatible cached scores.

```mermaid
flowchart LR
    UI["Focus overlay or calibration action"] --> Model["FocusMaskModel"]
    Model --> Analyze["PhotoAnalyzer.analyzeWithFocusMask / focusMask / calibrate"]
    Analyze --> Evidence["FocusEvidence + FocusCalibrationResult + CGImage mask"]
    Evidence --> Presentation["RawCull FocusMaskResult + overlay state"]
```

[FocusMaskTypes.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskTypes.swift) aliases neutral package types such as `FocusEvidence`,
`FocusFailureKind`, and `FocusCalibrationResult`, then layers RawCull
presentation metadata over `SharpnessBreakdown`. `FocusMaskModel` consumes the
returned mask image on app-owned isolation; scoring and evidence remain package
values.

## 14. Testing The Public Contract

The executable contracts are split by concern:

| Package test                                                         | Required behavior                                                       |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [Tests/PhotoAnalysisKitTests/SharpnessMetricsTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/SharpnessMetricsTests.swift)            | Scalar metric and normalized sharpness calculations                     |
| [Tests/PhotoAnalysisKitTests/PhotoAnalysisBatchTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/PhotoAnalysisBatchTests.swift)          | Bounded batch completion, ordering, failure isolation, and cancellation |
| [Tests/PhotoAnalysisKitTests/SharpnessAnalysisDescriptorTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/SharpnessAnalysisDescriptorTests.swift) | Stable configuration identity and descriptor changes                    |
| [Tests/PhotoAnalysisKitTests/PhotoAnalyzerTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/PhotoAnalyzerTests.swift)               | Facade behavior, focus evidence, calibration, and mask rendering        |
| [Tests/PhotoAnalysisKitTests/VisionFeaturePrintTests.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Tests/PhotoAnalysisKitTests/VisionFeaturePrintTests.swift)          | Opaque Vision feature-print creation and comparison                     |

`Tests/PhotoAnalysisKitTests/` imports the library through
`import PhotoAnalysisKit`, not `@testable import`. Tests therefore exercise the
public surface used by a host.

The suite covers:

- end-to-end sharpness analysis with the packaged Metal kernel;
- focus-mask images, evidence, and diagnostics;
- calibration from decoded images and neutral metadata;
- bounded concurrency, order preservation, progress, decode failure, and
  cancellation;
- descriptor encoding and changes in identity-affecting settings;
- robust-tail, micro-contrast, ISO scaling, and focus-failure metrics;
- configuration presets and aperture behavior;
- Vision feature-print compatibility, round trips, and malformed payloads.

Synthetic images keep the suite deterministic and independent of RAW files,
model downloads, cache directories, and application state.

## 15. How To Add Another Analysis

Use the existing boundary as a checklist:

1. Accept `CGImage` and only the neutral metadata the algorithm needs.
2. Keep URLs, camera decoding, settings state, and source selection in the host.
3. Return a `Sendable` package-owned result with enough evidence to explain it.
4. Put numeric tuning in a value configuration, not UI preferences.
5. Define a versioned descriptor when hosts may persist the output.
6. Make synchronous framework work cancellation-aware and independent of UI
   isolation.
7. Bound multi-image work instead of spawning one live task per catalog item.
8. Test through the public API with synthetic images and values.

If the proposed API needs `FileItem`, SwiftUI, a cache directory, or a rating,
that concern belongs in RawCull's adapter or policy layer.

## Source Map

| Topic                                | PhotoAnalysisKit source                                                           |
| ------------------------------------ | --------------------------------------------------------------------------------- |
| Product and resource declaration     | [Package.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Package.swift)                                                                   |
| Input and result boundary            | [Sources/PhotoAnalysisKit/PhotoAnalysisInput.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/PhotoAnalysisInput.swift)                               |
| Public analysis facade and metrics   | [Sources/PhotoAnalysisKit/PhotoAnalyzer.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/PhotoAnalyzer.swift)                                    |
| Batch orchestration                  | [Sources/PhotoAnalysisKit/PhotoAnalysisBatch.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/PhotoAnalysisBatch.swift)                               |
| Configuration and presets            | [Sources/PhotoAnalysisKit/SharpnessConfiguration.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/SharpnessConfiguration.swift), [SharpnessPresets.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/SharpnessPresets.swift) |
| Cache descriptor                     | [Sources/PhotoAnalysisKit/SharpnessAnalysisDescriptor.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/SharpnessAnalysisDescriptor.swift)                      |
| Public evidence values               | [Sources/PhotoAnalysisKit/FocusMaskTypes.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskTypes.swift)                                   |
| Engine isolation                     | [Sources/PhotoAnalysisKit/FocusMaskEngine.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskEngine.swift)                                  |
| Saliency and scalar scoring          | [Sources/PhotoAnalysisKit/FocusMaskEngine+Scoring.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskEngine+Scoring.swift)                          |
| Overlay generation and patch ranking | [Sources/PhotoAnalysisKit/FocusMaskEngine+MaskGeneration.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskEngine+MaskGeneration.swift)                   |
| Calibration                          | [Sources/PhotoAnalysisKit/FocusMaskCalibration.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FocusMaskCalibration.swift)                             |
| Vision request serialization         | [Sources/PhotoAnalysisKit/VisionRequestGate.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/VisionRequestGate.swift) |
| Face and animal evidence             | [Sources/PhotoAnalysisKit/FaceEvidenceAnalyzer.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/FaceEvidenceAnalyzer.swift), [AnimalCloseUpDetector.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/AnimalCloseUpDetector.swift) |
| Vision feature prints                | [Sources/PhotoAnalysisKit/VisionFeaturePrintBackend.swift](https://github.com/rsyncOSX/PhotoAnalysisKit/blob/2f41e8b756f006e0218f86b103801ebb47cf8983/Sources/PhotoAnalysisKit/VisionFeaturePrintBackend.swift)                        |
| Metal source and compiled resource   | `Sources/PhotoAnalysisKit/Resources/`                                             |
| Extraction decisions                 | `Documentation/ExtractionMap.md`                                                  |
| Public behavior tests                | `Tests/PhotoAnalysisKitTests/`                                                    |
| RawCull decode and result adapter    | [RawCull/Model/ViewModels/FocusandSharpness/RawCullPhotoAnalysisAdapter.swift](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Model/ViewModels/FocusandSharpness/RawCullPhotoAnalysisAdapter.swift)    |

Next, see how package-neutral measurements become culling-domain decisions in
[How RawCullCore Is Constructed](../rawcullcore/).

## Current host AF evidence hydration

RawCull's workspace fills missing AF-center evidence from older cached analysis
without replacing blended scores or recommended winners. Cancellation and
scoring identity guard publication. The host's optional `releaseafcomparison` workflow exports crops
for a separately labeled comparison; it is not photographic qualification.

## Measurement And Inspection Stay Separate

PhotoAnalysisKit's measurement boundary does not involve
[PhotoEvidenceKit]({{< relref "photoevidencekit.md" >}}). The latter displays manually chosen regions; it does not call `PhotoAnalyzer`
or recompute a score when a photographer moves or zooms a crop.

### Build Cache Identity Around The Actual Analysis Input

`SharpnessAnalysisDescriptor` describes algorithm/policy versions and configurable
non-mask analysis settings. The host must additionally identify the source file,
the chosen decoding path and decoded resolution. A score computed from an embedded
preview must not silently become the score for a developed RAW image after a
source toggle. Per-image ISO and aperture belong to `PhotoAnalysisInput` and must
remain consistent with the metadata used for that cached computation.

A manual inspection's `CloseUpRenderSource` is a separate identity. It enables
fresh display pixels without overwriting analysis identity or implying that a
previous score was computed from the newly displayed crop.

### Interpret Batch Outcomes Precisely

| Batch outcome | Meaning | Host behavior |
| --- | --- | --- |
| Empty input | Successful empty array | Finish with no work |
| Result with `analysis == nil` | That input provider failed to supply a usable image | Retain the item's failure state rather than inventing a zero score |
| Outer result is `nil` | Parent task was cancelled | Discard partial publication for that batch |
| Progress callback | Next completion, not next input position | Update progress using the supplied identifier |
| Final result array | Original request order | Associate results with their stable identifiers |

The default `maximumConcurrentTasks` is eight; the implementation clamps it to
at least one and at most the request count. Input providers execute within that
bounded work, so hosts can avoid eagerly decoding a whole catalog. This bounds
active batch tasks, not every cache or retained image elsewhere in the app.

### Keep AF Evidence And Manual Placement Distinct

Analysis AF evidence contributes to measurement interpretation. PhotoEvidenceKit's
recorded AF point assists region placement in canonical oriented coordinates.
Neither the presence of an AF location nor successful region placement establishes
that the subject is sharp. Supply metadata appropriate to each API and perform
sensor-to-oriented coordinate conversion in the host adapter.


## Close Up Integration

`FaceEvidenceAnalyzer` runs Vision face rectangle detection on an upright
embedded preview and can return a local luminance-gradient measurement for
each face. RawCull owns the disposable evidence cache. It keys compatibility
on the source revision, preview configuration and dimensions, algorithm
version, Vision revision and OS version.

RawCull calls the package’s `AnimalCloseUpDetector` for animal head and eye crops. Animal
tiles are visual crops. The human face detail measurement stays with the
human tiles. See the [Close Up guide]({{< relref "closeups.md" >}}) for how
these tiles appear beside manual comparisons.
