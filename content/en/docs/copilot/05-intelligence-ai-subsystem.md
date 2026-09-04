+++
author = "Thomas Evensen"
title = "Intelligence and AI Subsystem"
linkTitle = "Intelligence / AI"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "RawCull's on-device similarity, semantic search, burst analysis, and deep-review architecture."
tags = ["rawcull", "ai", "similarity", "semantic-search"]
categories = ["technical details"]
weight = 50
+++

# Intelligence / AI Subsystem

`RawCull/Intelligence/` is where RawCull's on-device machine-learning
features live: grouping near-duplicate "burst" shots, ranking them by
sharpness/subject focus, letting the user search photos by natural-language
description, and (optionally) running a heavier "Deep Review" AI pass that
recommends a winner within a burst. All of it runs **locally** — no photo
data or embeddings leave the machine, and every optional model requires an
explicit license acceptance and download before RawCull will use it.

This subsystem depends on sibling packages that own the actual model
execution, and the CLIP/segmentation models themselves are run through
**Apple's CoreAI framework** (`import CoreAI` / `CoreAIImageSegmenter`,
from Apple's `coreai-models` package, macOS 27+) — RawCull does **not**
ship a hand-rolled CoreML pipeline for these features. The package
boundaries are:

- **`PhotoAIContracts`** — shared value types/protocols
  (`SimilarityArtifact`, `SimilarityBackendDescriptor`, `ModelIdentity`,
  etc.) with no model code of their own.
- **`PhotoAIKit`** — the package that actually wraps Apple's CoreAI
  framework, split into several library products RawCull links
  individually: **`CoreAICLIPBackend`** (`CoreAICLIPProvider`, CLIP/SigLIP2
  image+text embeddings via `import CoreAI`/`CoreAIImageSegmenter`),
  **`CoreAISAM3Backend`** and **`CoreAIEfficientSAMBackend`** (subject
  segmentation, same CoreAI foundation, two swappable model families), and
  **`VisionFeaturePrintBackend`** (a CoreAI-independent fallback similarity
  provider built on Apple's Vision framework, always available with no
  download). `PhotoAIWorkflows`/`PhotoAIStorage` provide shared
  indexing/storage helpers used by these backends.
- **`PhotoAnalysisKit`** — a separate, unrelated package used only for
  **sharpness/focus scoring** (the Laplacian-based focus-mask and
  subject-focus algorithms described in
  [Settings and Configuration](../07-settings-and-configuration/) and
  the Deep Review section below). It's built on Vision/CoreImage/Accelerate,
  not CoreAI, and has no CLIP or segmentation model code.

RawCull's `Intelligence/` folder is the integration and orchestration layer
on top of all of these — it owns configuration, caching, lifecycle, and how
results reach the SwiftUI layer, not the models themselves. It never calls
`CoreAI`/`CoreAIImageSegmenter` directly — only through the `CoreAI*Backend`
provider types PhotoAIKit exposes.

## Folder map

| Folder | Role |
|---|---|
| `Contracts/` | `RawCullAIModels.swift` — the shared data types every other Intelligence file depends on (capability status enums, paths, model IDs). |
| `Composition/` | `RawCullIntelligenceRuntime` + `RawCullAIIntegration` — the subsystem's own composition root and configuration-application logic. |
| `Similarity/` | Groups near-duplicate images into bursts and ranks/scores their visual similarity. |
| `SemanticSearch/` | Natural-language photo search via CLIP text/image embeddings. |
| `BurstAnalysis/` | Orchestrates sharpness scoring + similarity grouping into one cached "burst analysis" pass per catalog. |
| `DeepReview/` | Optional, heavier AI pass: subject segmentation + focus scoring to recommend a burst winner. |
| `ModelManagement/` | Downloading, licensing, and validating optional model bundles (CLIP, SAM3/EfficientSAM). |
| `Persistence/` | Actor-isolated disk caches for burst-analysis snapshots and per-file similarity artifacts. |
| `Presentation/` | Small UI-facing presentation helpers (e.g. semantic search result formatting). |

## Contracts: the shared vocabulary

`Intelligence/Contracts/RawCullAIModels.swift` defines the types every other
file in this subsystem builds on:

- **`RawCullCLIPModel`** (`.dataComp` / `.openAI`) and
  **`RawCullSegmentationModel`** (`.sam3` / `.efficientSAM`) — the mutually
  exclusive model choices for semantic search and Deep Review, respectively.
  `RawCullAIModelInclusion` is a compile-time switch table deciding which of
  these are actually offered in this build (currently: DataComp CLIP + SAM3).
- **`RawCullAIPaths`** — computes every on-disk location the subsystem uses,
  all rooted under RawCull's existing `Application Support`/`Caches`
  directories rather than a separate namespace (models under
  `Application Support/RawCull/Models/<ModelName>/`, subject masks under
  `Caches/no.blogspot.RawCull/SAM3Masks/`, burst analysis under
  `Application Support/RawCull/BurstAnalysis/`).
- **`RawCullAICapabilityStatus`** / **`RawCullSemanticSearchCapabilityStatus`**
  — structured "is this feature usable right now" enums
  (`checking`/`available`/`missing`/`invalid`/`unavailable`, plus a
  semantic-search-specific `ready(location:backend:)`). Semantic search has
  its own status type because Vision alone is a valid *similarity* backend
  but text search specifically requires a validated CLIP provider.
- **`RawCullAICapabilities`** — the full readiness snapshot (per
  segmentation model, per CLIP model, per semantic-search variant, plus
  Vision feature-print and subject-mask storage) that Settings UI reads.
- **`RawCullSavedBurstEvidenceScanner`** — a read-only, cancellable
  `@concurrent` scan of the existing burst cache directory that counts how
  many CLIP vs. Vision embeddings are already saved, purely for a
  diagnostics panel in Settings; it never mutates the cache.

## Composition root: `RawCullIntelligenceRuntime` + `RawCullAIIntegration`

`Intelligence/Composition/RawCullIntelligenceRuntime.swift` is this
subsystem's own composition root, nested inside the app-wide one described in
[Architecture Overview](../). `RawCullApplicationState.make(...)` builds,
in order: `RawCullAIModelManagementModel` → `RawCullAISettingsModel` →
`SimilarityScoringModel` → `RawCullSimilarityFeature` →
`RawCullSemanticSearchFeature` → `DeepAIReviewController` →
`RawCullViewModel` → `RawCullIntelligenceRuntime`, then wires bidirectional
references (`similarityFeature.bindApplicationContext(viewModel)`,
`settingsModel.bindConfigurationConsumer(intelligenceRuntime)`) and asserts
identity equality everywhere a shared instance is expected
(`assert(viewModel.similarityFeature === intelligenceRuntime.similarityFeature)`),
specifically to catch an accidental duplicate instance during future
refactors.

`RawCullIntelligenceRuntime.apply(configuration:)` is the single choke point
through which **settings changes reach running features**. It compares an
incoming `RawCullIntelligenceConfiguration`'s *identity* (backend
descriptors + capability statuses, all `Sendable`, computed via
`configuration.identity`) against the last-applied one, using a monotonic
`revision: UInt64` to reject stale/out-of-order configuration pushes, and
only calls `similarityFeature.replaceSimilarityService(...)` /
`replaceSemanticSearchConfiguration(...)` for the parts that actually
changed:

```swift
func apply(configuration: RawCullIntelligenceConfiguration) -> RawCullAICapabilities {
    let incomingIdentity = configuration.identity
    guard configuration.revision > lastAcceptedConfigurationRevision ?? 0 else {
        return integration.capabilities()   // stale push, ignore
    }
    guard previousIdentity != incomingIdentity else {
        lastAcceptedConfigurationRevision = configuration.revision
        return integration.capabilities()   // no-op, nothing actually changed
    }
    // ... replace only the changed sub-configuration ...
}
```

Note the deliberate `Sendable`/non-`Sendable` split: `identity` is
`Sendable` value data that's safe to compare and log, while the actual
`service: any RawCullSimilarityServicing` (the concrete Vision/CLIP
provider) stays `@MainActor`-only and never crosses an isolation boundary —
only its `backendDescriptor` (a `Sendable` value) does.

> **Deep dive:** see [Intelligence Runtime](../runtime/) for the full lifecycle —
> construction order and identity assertions, exactly how a settings change
> or a completed model download reaches `apply(configuration:)`, what each
> per-field diff actually swaps downstream, and how to safely add a new
> runtime-configurable setting or AI feature.

## Similarity and burst grouping

`SimilarityScoringModel` (`Similarity/SimilarityScoringModel.swift`) is the
`@MainActor @Observable` state machine behind both similarity grouping and
semantic search indexing. It talks to a pluggable backend behind
`RawCullSimilarityServicing` — currently either Vision's on-device feature
print (`RawCullVisionSimilarityService`, built on PhotoAIKit's
`VisionFeaturePrintBackend`, always available, no download required) or
CLIP embeddings (`RawCullSemanticSearchService`, backed by PhotoAIKit's
`CoreAICLIPBackend` — i.e. Apple's CoreAI framework — and requires a
downloaded model), selected via Settings
(`RawCullAISettingsModel.useCLIPForSimilarity`). It also owns
**indexing**, i.e. computing and persisting embeddings for a catalog's
files, tracked through phases (`idle` → `generating` → `saving`) so the UI
can show progress and so a stale indexing run can be safely discarded if the
catalog changes mid-flight.

`RawCullSimilarityFeature` is the thin `@MainActor @Observable` boundary the
rest of the app (views, `RawCullViewModel`) actually talks to — it exposes
burst-group lookups and grouping actions without leaking
`SimilarityScoringModel`'s internal indexing machinery.

## Burst analysis: tying sharpness + similarity together

A "burst analysis" run combines two independently-computed signals —
sharpness score (per file) and similarity distance (between files) — into
grouped bursts with a per-group ranking. `BurstAnalysisCoordinator`
(`BurstAnalysis/BurstAnalysisCoordinator.swift`, `@MainActor @Observable`)
owns this orchestration, kept deliberately separate from
`RawCullViewModel` (which only supplies burst-analysis *inputs* — the
ordered file list, catalog identity — and applies the *result* back into its
own `burstAnalysisResults`/`burstReviewStates` once accepted).

`run(request:initialReviewStates:fullCatalogFileIDs:callbacks:)` is the
pipeline entry point:

1. `callbacks.isCurrent()` — bail out immediately if the caller already
   knows this run is stale (catalog switched, generation advanced).
2. **Load cache** — `prepareCache(for:...)` checks
   `BurstAnalysisCacheRepository` for a compatible snapshot (see cache
   versioning below); a full cache hit skips straight to applying results.
3. **Score sharpness** for files that don't have a cached score.
4. **Score similarity** for file pairs that don't have a cached embedding.
5. **Group into bursts** via `similarityModel.groupBursts(files:configuration:)`.
6. **Restore or seed review states** — if a compatible legacy cache snapshot
   exists, prior "reviewed"/"deferred" per-group states are migrated onto
   the newly computed groups; otherwise the caller's `initialReviewStates`
   (typically empty) are used.
7. Publish through `callbacks.applyResult(...)`, which itself re-validates
   currency before mutating `RawCullViewModel` state.

Every step checks `callbacks.isCurrent()` again before proceeding —
identical in spirit to the generation-check pattern from
[Concurrency Architecture](../01-concurrency-architecture/).

### Cache versioning

`BurstAnalysisCacheSnapshot` (`Persistence/BurstAnalysisCache.swift`) is the
`Codable` structure written to
`Application Support/RawCull/BurstAnalysis/<catalog>.json`. It's explicitly
versioned on **three independent axes** so a stale or incompatible cache is
never blindly trusted:

- `schemaVersion` — the on-disk JSON shape.
- `algorithmVersion` — the burst-grouping/ranking algorithm itself.
- `BurstSimilaritySignature.artifactSchemaVersion` /
  `embeddingPipelineVersion` — the similarity backend and how its
  embeddings were produced.

If any of these mismatch, RawCull treats the cache as stale for that part of
the pipeline and recomputes just the affected signal (e.g. a CLIP model
upgrade recomputes similarity but not sharpness), rather than discarding
everything.

## Semantic search

`RawCullSemanticSearchFeature` (`SemanticSearch/RawCullSemanticSearchFeature.swift`)
is the UI-facing surface for natural-language photo search, backed by the
same `SimilarityScoringModel` used for burst grouping (asserted via
`sharesSimilarityModelIdentity(with:)` in `RawCullViewModel.init`) so a
photo's embedding is computed once and reused for both features.
`RawCullSemanticSearchService` performs CLIP text-vs-image cosine scoring
via PhotoAIKit's `CoreAICLIPProvider` (Apple's CoreAI framework); if no CLIP
model is downloaded/valid, semantic search reports
`.unavailable`/`.failed` capability rather than silently falling back —
unlike plain similarity grouping, which *can* fall back to the CoreAI-free
Vision feature-print backend.
Results are modeled as an explicit state machine
(`RawCullSemanticSearchState`: `.idle` / `.searching` / `.results` /
`.emptyIndex` / `.failed`) so the UI never has to infer "are we loading or
just have zero matches" from ambiguous nil/empty checks.

## Deep Review

Deep Review is an optional, user-triggered, heavier analysis of a *single*
burst group: it segments the subject in each frame using PhotoAIKit's
CoreAI-backed segmentation (SAM3 or EfficientSAM, whichever the user
selected — both are `CoreAI`/`CoreAIImageSegmenter` model families exposed
via `CoreAISAM3Backend`/`CoreAIEfficientSAMBackend`) and scores focus
specifically on that subject region (`SubjectMaskFocusScorer`, from
`PhotoAnalysisKit`, edge-energy based — not a CoreAI model), then
recommends which frame in the group is sharpest **on the subject**, which
can differ from a naive whole-frame sharpness ranking (e.g. a
background-blurred portrait where the subject is what matters).

`DeepAIReviewController` (`@MainActor @Observable`) is the runtime-owned
boundary views talk to; it delegates actual scoring/state work to
`DeepAIReviewFeature` and adapts `RawCullViewModel`'s burst data into a
`DeepAIReviewGroupContext` through the small
`DeepAIReviewApplicationContext` protocol RawCullViewModel conforms to —
another instance of the "protocol-shaped seam between the central view
model and a feature controller" pattern used throughout this codebase.
Progress is modeled as `DeepAIReviewPresentationState` (`checking` →
`ready`/`unavailable` → `preparing` → `running` → `completing` →
`completed`/`failed`/`cancelled`), and the UI shows an inline spinner via
`deepAIReviewController.isRunning(groupID:)` while a specific group is being
analyzed.

## Model management and licensing

`RawCullAIModelManagementModel` and `RawCullAISettingsModel`
(`ModelManagement/`) handle the optional model bundles (CLIP variants, SAM
variants) that aren't bundled with the app — they're multi-hundred-MB to
multi-GB downloads the user opts into:

- **`RawCullAIModelDownloadCatalog`** — the production catalog of
  downloadable model IDs (`RawCullAIModelDownloadID`: `clipDataComp`,
  `clipOpenAI`, `efficientSAM`, `sam3`), gated by the
  `RawCullAIModelInclusion` compile-time flags mentioned above.
- **`RawCullAIModelDownloadService`** — an `actor`-based coordinator
  integrating with Apple's Background Assets framework so large downloads
  survive app relaunch/backgrounding.
- **`RawCullAIModelLicenceAcceptance`** — persists which model licenses the
  user has explicitly accepted (with RawCull version + timestamp) to
  `ModelLicenceAcceptances.json`; a model isn't used until its license is
  accepted, even if already downloaded.
- **`RawCullAIModelResourceManager`** — a generic actor that validates a
  downloaded bundle and constructs the concrete provider for it, caching the
  validated provider so re-validation doesn't happen on every use.
- **`RawCullAISettingsModel`** — the `@Observable @MainActor` model the
  Settings UI actually binds to. Per its own doc comment, it "intentionally
  does not expose PhotoAIKit providers, repositories, or the composition
  root" — it only exposes capability statuses and simple preference toggles
  (`useCLIPForSimilarity`, `selectedCLIPModel`, `selectedSegmentationModel`),
  persisted to `UserDefaults`, and forwards changes to the runtime via
  `bindConfigurationConsumer`.

## Persistence layer

Two actors persist Intelligence results to disk, independent of
`CullingModel`'s rating persistence:

- **`PerFileAnalysisArtifactStore`** — stores each file's similarity
  embedding (`SimilarityArtifact`, `Sendable Codable`) keyed by file ID and
  backend, so re-opening a catalog doesn't require re-embedding every photo.
- **`BurstAnalysisCache`** — stores the full `BurstAnalysisCacheSnapshot`
  per catalog described above.

Both use atomic writes and are safe to interrupt mid-write (a cancelled
indexing run can't corrupt an already-persisted artifact for a different
file).

## Where to look when extending this

- **Adding a new similarity/segmentation backend** → implement the relevant
  protocol (`RawCullSimilarityServicing`, etc.) in `PhotoAIKit` (not
  `PhotoAnalysisKit`, which is sharpness-only), add a case to the relevant
  enum in `RawCullAIModels.swift`, and thread it through
  `RawCullAIModelDownloadCatalog` + `RawCullAISettingsModel` — don't bypass
  `RawCullIntelligenceRuntime.apply(configuration:)`.
- **Changing cache-invalidation behavior** → bump the relevant version field
  in `BurstSimilaritySignature`/`BurstAnalysisCacheSnapshot`, don't add a
  parallel invalidation check.
- **New Deep-Review-style heavy analysis** → follow
  `DeepAIReviewController`/`DeepAIReviewFeature`'s split (runtime-owned
  controller + protocol-based application context) rather than adding logic
  directly to `RawCullViewModel`.
