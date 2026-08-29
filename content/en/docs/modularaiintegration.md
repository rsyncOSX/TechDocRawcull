+++
author = "Thomas Evensen"
title = "Modular AI Integration"
date = "2026-08-29"
lastmod = "2026-08-29"
description = "How RawCull's modular AI runtime, configuration, model management, semantic search, and similarity features were implemented through Phases 0–6, with the planned Phase 7 burst-analysis extraction."
weight = 58
tags = ["ai", "architecture", "modularization", "semantic-search", "similarity", "burst-analysis"]
categories = ["technical details"]
mermaid = true
+++

# Modular AI Integration

RawCull's modular AI work reorganizes application ownership around stable,
focused feature boundaries. It does not replace Vision, CLIP, SAM 3, or
EfficientSAM with one new machine-learning model. In this documentation,
"model" can mean either an inference model installed on disk or an observable
application model that owns presentation state and actions. The refactoring is
primarily about the second meaning.

The implementation keeps PhotoAIKit as the reusable AI layer while RawCull owns
application composition, settings, catalog identity, task lifetime, culling
policy, and SwiftUI presentation. Phases 0–6 establish and migrate this
architecture. Phase 7 is the next planned step: extracting burst-analysis
computation and cache decisions from `RawCullViewModel` without moving culling
commands or review policy out of the application model.

> **Implementation status, 2026-08-29:** Phases 0–6 are implemented. The
> automated Phase 6 gates pass, while its interactive acceptance matrix remains
> to be completed. Model downloads for the DataComp and OpenAI CLIP variants
> were manually verified during Phase 4. Phase 7 has not started; its section
> below records the intended boundary and acceptance criteria so this page can
> be updated when the extraction is complete.

## Why The Architecture Changed

AI behavior originally accumulated in several places at once:

- `RawCullViewModel` coordinated catalog state, semantic search, image
  similarity, burst analysis, persistence, selection, and review actions.
- settings used multiple callbacks to push related provider choices into the
  application;
- the app and settings could each appear to own parts of the AI lifetime;
- views reached through the central view model for operations that belonged to
  focused features;
- configuration, hydration, indexing, ranking, and cancellation did not have
  equally explicit request identities.

The modularization introduces one stable composition root and moves one vertical
slice at a time. Product behavior, cache formats, preference keys, backend
selection, and user-visible workflows remain compatible while ownership becomes
testable and easier to reason about.

## Architecture At The Phase 6 Stopping Point

```mermaid
flowchart TD
    App["RawCullApp<br/>stable @State roots"] --> State["RawCullApplicationState"]
    State --> Runtime["RawCullIntelligenceRuntime"]
    State --> VM["RawCullViewModel"]

    Runtime --> Integration["RawCullAIIntegration<br/>provider composition"]
    Runtime --> Settings["RawCullAISettingsModel"]
    Runtime --> Management["RawCullAIModelManagementModel"]
    Runtime --> Similarity["RawCullSimilarityFeature"]
    Runtime --> Semantic["RawCullSemanticSearchFeature"]
    Runtime --> DeepReview["DeepAIReviewFeature"]
    Runtime --> SharedModel["SimilarityScoringModel<br/>single shared state owner"]

    Similarity --> SharedModel
    Semantic --> SharedModel
    Semantic -. "weak app target" .-> VM
    Similarity -. "weak app context" .-> VM
    Settings -. "weak configuration consumer" .-> Runtime
    Management -. "weak locations consumer" .-> Settings

    Integration --> Contracts["PhotoAIKit protocols"]
    Contracts --> Backends["Vision, CLIP, and segmentation backends"]
```

Solid arrows show lifetime ownership or dependency use. Dotted arrows are weak
application coordination edges. The weak edges allow a feature to request the
small amount of app behavior it needs without owning the app model and without
creating a retain cycle.

### Responsibility map

| Component | Current responsibility |
|---|---|
| `RawCullApp` | Retains one `RawCullApplicationState` in `@State` and exposes stable models to SwiftUI. |
| `RawCullApplicationState` | Assembles the live object graph in a deterministic order and asserts shared object identity. |
| `RawCullIntelligenceRuntime` | Owns the intelligence integration and feature models, accepts complete revisioned configurations, and applies meaningful changes. |
| `RawCullAIIntegration` | Composes concrete PhotoAIKit providers, validates model resources, reports capabilities, and provides narrow similarity, semantic, and segmentation services. |
| `RawCullAISettingsModel` | Owns user choices and capability presentation, persists preferences, and publishes one complete configuration snapshot. |
| `RawCullAIModelManagementModel` | Owns model-download presentation, licence state, managed locations, download tasks, validation, cancellation, and removal actions. |
| `SimilarityScoringModel` | Remains the single observable state store for similarity artifacts, indexing, distances, and semantic-search state. |
| `RawCullSimilarityFeature` | Provides the Phase 6 API for catalog hydration, indexing, image ranking, backend presentation, cancellation, and stale-result protection. |
| `RawCullSemanticSearchFeature` | Provides semantic-search presentation and actions while projecting, rather than copying, state from the shared scoring model. |
| `RawCullViewModel` | Still owns catalog, selection, navigation, culling, review policy, and the burst pipeline that Phase 7 will extract. |

## Invariants Preserved Across Every Phase

The refactoring is constrained by behavior rather than by file layout. These
invariants are especially important:

1. Vision feature prints remain the safe startup similarity backend.
2. CLIP is selected only when enabled and the chosen model produces a validated
   provider.
3. Semantic search requires compatible CLIP image artifacts and never performs
   hidden image indexing while executing a text query.
4. Similarity artifacts remain descriptor-validated. Backend, model,
   preprocessing, normalization, configuration, schema, and source fingerprint
   must be compatible before reuse.
5. A catalog change, backend change, cancellation, or superseding generation
   prevents late asynchronous work from publishing stale results.
6. Existing cache schemas, persisted descriptors, remapping behavior, ratings,
   selection, navigation, manual winners, undo, and review state remain intact.
7. SwiftUI observes one authoritative state owner for each value; feature
   boundaries do not introduce mirrored observable state.
8. PhotoAIKit remains independent of RawCull types and product policy.

## Phase 0 — Establish A Trustworthy Baseline

Phase 0 made the existing behavior measurable before changing ownership. The
baseline was recorded from the `version-3.1.1` reference and covered Debug,
Release, smoke, full, and performance gates as appropriate. It also captured
the resolved package state and the behavior of the important AI workflows.

The characterization suite established contracts for:

- application composition with Vision available before CLIP validation;
- saved burst evidence and compatible cache loading;
- similarity hydration, missing-only indexing, persistence, ranking, and
  cancellation;
- semantic-search completion, empty-index behavior, cancellation, and catalog
  restoration;
- burst analysis, regrouping, cache hits, manual overrides, and review state;
- Deep Review completion, cancellation, provider unavailability, and applying a
  recommended winner;
- model discovery, download state, licence acceptance, validation, and removal.

Phase 0 is part of the implementation because later phases use these tests as a
behavioral fence. A structural change is accepted only when it preserves the
characterized result, ordering, cache identity, and cancellation semantics.

## Phase 1 — Define And Enforce The Dependency Boundary

Phase 1 established the permitted dependency direction before moving code.

```mermaid
flowchart LR
    Views["SwiftUI views"] --> Presentation["RawCull feature presentation + actions"]
    Presentation --> Orchestration["RawCull application orchestration"]
    Orchestration --> Ports["RawCull protocols and repositories"]
    Ports --> Contracts["PhotoAIKit contracts and workflows"]
    Contracts --> Implementations["Concrete AI backends"]
```

The important rule is that UI and application policy depend on narrow feature
surfaces, not on concrete backend products. `Scripts/VerifyAIImportBoundary.sh`
mechanically checks the app source for forbidden imports. A small, documented
set of existing `PhotoAIContracts` exposures remains as non-blocking migration
debt; the script prevents that surface from growing accidentally.

This phase deliberately did not reorganize directories or extract another
package. Logical dependency direction came first so later ownership changes
could be evaluated independently from physical movement.

## Phase 2 — Introduce A Stable Intelligence Runtime

Phase 2 created a lifetime container without moving feature behavior. The app
constructs one `RawCullApplicationState`, which contains exactly one
`RawCullIntelligenceRuntime` and one `RawCullViewModel`. The runtime retains the
integration, settings, model management, similarity, semantic-search, and Deep
Review objects needed for the full application lifetime.

`RawCullApplicationState.make(...)` assembles the graph in this order:

1. Create `RawCullAIModelManagementModel`.
2. Create `RawCullAISettingsModel` with that exact management model.
3. Ask settings for the initial typed configuration.
4. Create one `SimilarityScoringModel` from its initial similarity and semantic
   services.
5. Create `RawCullSimilarityFeature` over that scoring model.
6. Create `RawCullSemanticSearchFeature` over the same scoring model and the
   same similarity feature.
7. Create `RawCullViewModel` with those exact feature instances.
8. Create the runtime, bind its weak application edges, and bind settings to the
   runtime as its configuration consumer.

Identity assertions in the assembly method guard against accidentally creating
a second scoring model or feature instance. This matters because two otherwise
identical observable objects would split state updates between the UI and the
running operation.

Phase 2 preserves the distinction between ownership and coordination. Runtime
objects strongly own the features. Features refer back to the application only
through narrow weak protocols.

## Phase 3 — Replace Settings Callbacks With One Typed Configuration Path

Phase 3 replaces separate settings callbacks with a single revisioned
`RawCullIntelligenceConfiguration`. A snapshot carries:

- the selected similarity service;
- all artifact backend descriptors accepted by that service;
- semantic-search capability and its optional service;
- the selected segmentation model;
- a monotonically increasing revision.

The sendable identity contains descriptors and enum values, while service
existentials remain main-actor confined. This prevents concrete provider
objects from crossing concurrency domains merely to compare configuration.

```mermaid
sequenceDiagram
    participant User as Settings UI
    participant Settings as RawCullAISettingsModel
    participant Runtime as RawCullIntelligenceRuntime
    participant Integration as RawCullAIIntegration
    participant Similarity as RawCullSimilarityFeature

    User->>Settings: Change CLIP or segmentation selection
    Settings->>Settings: Persist existing preference key
    Settings->>Settings: Build complete snapshot and increment revision
    Settings->>Runtime: apply(configuration)
    Runtime->>Runtime: Reject stale revision or identical identity
    opt Segmentation changed
        Runtime->>Integration: setSelectedSegmentationModel(...)
    end
    opt Similarity identity changed
        Runtime->>Similarity: replaceSimilarityService(...)
    end
    opt Semantic capability or backend changed
        Runtime->>Similarity: replaceSemanticSearchConfiguration(...)
    end
    Runtime-->>Settings: Refreshed capabilities
```

The apply order is intentional: segmentation, then similarity, then semantic
search. Older revisions are ignored. A newer revision with the same identity is
accepted without resetting feature state. Reusing one complete snapshot avoids
transient combinations such as a new capability paired with an old provider.

The existing preference keys are preserved:

- `RawCullAI.useCLIPForSimilarity`
- `RawCullAI.selectedCLIPModel`
- `RawCullAI.selectedSegmentationModel`

## Phase 4 — Separate Settings From Model Management

Phase 4 extracts downloadable-model lifecycle state into
`RawCullAIModelManagementModel`. SwiftUI receives prepared
`RawCullAIModelDownloadPresentation` values and focused actions rather than the
catalog, coordinator, acceptance store, install locations, or task dictionary.

The management model owns:

- the production model catalog and per-model state;
- licence acceptance state;
- download, progress, validation, cancellation, removal, and refresh actions;
- top-level download tasks keyed by model ID;
- the complete set of successfully managed model locations.

The settings model retains the exact child management model and implements the
weak `RawCullAIManagedModelLocationsApplying` consumer. When managed locations
change, the sequence is:

```mermaid
flowchart TD
    Refresh["Model management refresh"] --> Snapshot["Coordinator snapshot"]
    Snapshot --> Present["Publish download presentations"]
    Snapshot --> Locations["Deliver complete managed-location map"]
    Locations --> Install["AI integration updates resource locations"]
    Install --> Parallel["Refresh capabilities and scan saved burst evidence"]
    Parallel --> Settings["Settings publishes updated capability state"]
    Settings --> Config["Publish complete Phase 3 configuration"]
    Config --> Runtime["Runtime applies only meaningful changes"]
```

This is a complete-state handoff, not a stream of individual path mutations.
It makes refresh, removal, and replacement converge on the same state. The model
download UI for both DataComp and OpenAI CLIP resources was manually exercised
after this phase; the broader cancellation and corrupt-download matrix remains
part of ongoing interactive qualification.

## Phase 5 — Migrate Semantic Search As A Vertical Slice

Phase 5 adds `RawCullSemanticSearchFeature` as the stable semantic-search UI and
action boundary. It does not introduce another semantic state store.
Properties such as capability, progress, indexed counts, selected IDs, result
order, rank, and score are computed projections of the shared
`SimilarityScoringModel`.

The feature has one narrow weak application target,
`RawCullSemanticSearchApplicationTarget`, for behavior that genuinely belongs
to RawCull:

- admit the current catalog files to a query;
- prepare selection and presentation for a new query;
- invalidate scoped burst state when semantic selection changes;
- apply the semantic result selection;
- restore normal catalog order when a query is cleared or cancelled.

### Query behavior

```mermaid
flowchart TD
    Query["User submits text"] --> Validate{"Non-empty query?"}
    Validate -->|"no"| Clear["Clear semantic state and restore catalog"]
    Validate -->|"yes"| Generation["Advance action generation"]
    Generation --> Admit["Request admitted catalog snapshot"]
    Admit --> Prepare["Prepare app for new results"]
    Prepare --> Rank["Create text embedding and rank cached compatible image artifacts"]
    Rank --> Current{"Generation still current?"}
    Current -->|"yes"| Apply["Apply result selection and order"]
    Current -->|"no"| Drop["Discard stale completion"]
```

`search(for:)` ranks only files with compatible cached CLIP artifacts. Source
decoding and image indexing are intentionally absent from the query action.
Indexing is an explicit similarity-feature action, so the UI can explain when
the semantic index is empty rather than starting expensive work invisibly.

The feature also owns an action generation. Clearing, cancelling, or starting a
new query advances that generation, ensuring a late result cannot reapply an old
selection. Semantic-search view-model forwarders were removed after callers
migrated to the feature directly.

## Phase 6 — Put Similarity Hydration, Indexing, And Ranking Behind One API

Phase 6 introduces `RawCullSimilarityFeature` as the application boundary for
image similarity. `SimilarityScoringModel` continues to own observable data;
the feature owns operation lifetime, typed requests, validation, and focused
presentation.

### Typed catalog and operation identities

The Phase 6 request values make the assumptions of an async operation explicit:

| Type | Purpose |
|---|---|
| `RawCullSimilarityCatalogIdentity` | Identifies the catalog URL and catalog generation. |
| `RawCullSimilarityCatalogSnapshot` | Couples ordered files to that identity. |
| `RawCullSimilarityCatalogHydrationRequest` | Hydrates both image and semantic artifacts for one catalog generation. |
| `RawCullSimilarityIndexRequest` | Carries files, catalog identity, thumbnail size, and force-refresh policy. |
| `RawCullSimilarityRankingRequest` | Carries anchor, ordered files, saliency information, and catalog identity. |
| `RawCullSimilarityRankingCompletion` | Records the anchor, catalog identity, and backend identity that produced a valid completion. |

The feature owns separate hydration generations for image artifacts, semantic
artifacts, and catalog hydration, plus a ranking generation. Every completion
checks cancellation and the current catalog identity. Ranking additionally
checks that the backend is unchanged and that the model's final anchor matches
the request.

### Service replacement

When the Phase 3 runtime replaces the similarity service, the feature:

1. compares both the primary backend descriptor and the ordered accepted
   artifact descriptors;
2. asks the application context to cancel and reset backend-sensitive burst
   analysis;
3. installs the new service in the shared model;
4. cancels the prior image hydration generation;
5. hydrates compatible artifacts for the current catalog.

Semantic configuration replacement follows the same principle with its own
task and generation. This separation is necessary because burst similarity may
use Vision while semantic search requires CLIP artifacts from a matching model.

### Catalog hydration and indexing

Normal catalog indexing remains behaviorally compatible:

1. Hydrate descriptor-valid image-similarity artifacts.
2. Confirm that the catalog identity is still current.
3. Hydrate descriptor-valid semantic artifacts.
4. Confirm the identity again.
5. Index only missing files unless force refresh was requested.
6. Retain valid partial successes and report generation and persistence failures
   separately.
7. Persist reusable per-file artifacts without changing their existing schema.

Image-to-image ranking first ensures the requested file set has a complete
compatible index. It then ranks from the requested anchor and returns a typed
completion only if generation, catalog, backend, and anchor still match.

SwiftUI now calls focused feature actions and reads focused presentation values.
The main toolbar uses the feature's combined busy projection, and burst views use
the same feature surface where Phase 6 owns the behavior. Unused transitional
properties and cancellation forwarders were removed after caller and Periphery
audits.

### The intentional compatibility seam

The runtime and view model still retain the exact shared
`SimilarityScoringModel` for burst analysis and persistence. This is explicitly
marked as a Phases 7/9 compatibility reference, not as a second state owner.
Removing it during Phase 6 would have mixed the similarity UI migration with a
large burst-analysis rewrite.

## Phase 7 — Planned Burst-Analysis Extraction

Phase 7 has not yet been implemented. It is divided into small subphases so
cache compatibility, compute orchestration, and view-model reduction can be
reviewed independently.

### Phase 7A: immutable requests and results

Introduce pure request and result values that capture everything needed to
identify a burst run:

- catalog identity and ordered files;
- sharpness and similarity configuration signatures;
- analysis generation;
- selected backend and compatible artifact descriptors;
- typed groups, rankings, restored review state, cache outcome, and diagnostics.

The existing view-model pipeline should initially build and consume these
values without moving behavior. This first step makes hidden inputs visible and
creates test seams before ownership changes.

### Phase 7B: cache hydration and compatibility decisions

Move per-file hydration, legacy import, derived cache loading, artifact digests,
and cache-hit decisions behind a repository or coordinator boundary. Preserve:

- current cache schemas and backend descriptors;
- file-ID remapping when a saved catalog is reopened;
- source-fingerprint and configuration compatibility checks;
- migrate-once behavior for legacy data;
- partial artifact reuse and invalid-entry rejection.

### Phase 7C: compute orchestration

Add a stable `BurstAnalysisCoordinator` that performs missing sharpness work,
missing similarity indexing, grouping, ranking, and cache-save preparation.
It should accept immutable snapshots, report progress explicitly, and expose
cancellation checkpoints between expensive phases.

```mermaid
flowchart TD
    Request["Immutable burst request"] --> Hydrate["Hydrate per-file artifacts and derived cache"]
    Hydrate --> Cache{"Compatible cache hit?"}
    Cache -->|"yes"| Restore["Return remapped typed result"]
    Cache -->|"no"| Sharpness{"Sharpness missing?"}
    Sharpness -->|"yes"| Score["Compute missing sharpness"]
    Sharpness -->|"no"| Similarity
    Score --> Similarity{"Similarity artifacts missing?"}
    Similarity -->|"yes"| Index["Index missing files through similarity feature"]
    Similarity -->|"no"| Group
    Index --> Group["Group adjacent frames"]
    Group --> Rank["Rank multi-frame groups"]
    Rank --> Prepare["Prepare typed result and cache record"]
    Restore --> Validate["MainActor validates generation and catalog"]
    Prepare --> Validate
    Validate --> Apply["RawCullViewModel applies result"]
```

Background computation must not mutate observable state directly. The
coordinator returns values; `RawCullViewModel` applies them on `MainActor` only
after checking the current generation and catalog.

### Phase 7D: reduce the central view model

Once callers and tests use the coordinator, `RawCullViewModel` should retain:

- one stable coordinator reference;
- minimal progress and result projections needed by the UI;
- ratings, selection, navigation, manual winner overrides, undo, review state,
  and other application commands.

Transitional helpers and direct storage access can then be removed after call
site, test, and unused-code audits. The final manual qualification must exercise
analyze, cancel, restore, regroup, cached reopen, manual winner, and review flows
end to end.

### Phase 7 completion criteria

Phase 7 is complete when:

- burst computation and persistence decisions can be tested without creating
  the full `RawCullViewModel`;
- the view model applies typed results and continues to own app commands;
- cache reuse, legacy compatibility, grouping, ranking, and partial-success
  behavior match the baseline;
- cancellation and stale-result rejection are explicit at each async boundary;
- the temporary direct burst access to `SimilarityScoringModel` is reduced to
  the narrowest downstream persistence compatibility required for Phase 9.

## End-To-End Configuration And Operation Flow

The completed phases produce a consistent path from a user choice to a guarded
operation:

```mermaid
flowchart LR
    Choice["User setting or managed model change"] --> Settings["Settings builds revisioned configuration"]
    Settings --> Runtime["Runtime compares identity"]
    Runtime --> Feature["Feature replaces changed service"]
    Feature --> Cancel["Cancel incompatible task generation"]
    Cancel --> Hydrate["Hydrate compatible artifacts"]
    Hydrate --> Action["Explicit index, image-rank, or semantic-search action"]
    Action --> Validate["Validate catalog + backend + generation"]
    Validate --> UI["Publish current presentation state"]
```

This flow prevents a settings change from reaching around the runtime, prevents
views from selecting concrete providers, and prevents async work from applying
results to the wrong catalog.

## Source Map

| Concern | Primary RawCull source |
|---|---|
| Composition and runtime | `RawCull/Model/AIIntegration/RawCullIntelligenceRuntime.swift` |
| Concrete provider composition | `RawCull/Model/AIIntegration/RawCullAIIntegration.swift` |
| Similarity feature API | `RawCull/Model/AIIntegration/RawCullSimilarityFeature.swift` |
| Semantic-search feature API | `RawCull/Model/AIIntegration/RawCullSemanticSearchFeature.swift` |
| Shared scoring state | `RawCull/Model/ViewModels/SimilarityScoringModel.swift` |
| Settings and configuration publication | `RawCull/Model/ViewModels/RawCullAISettingsModel.swift` |
| Download and installed-model lifecycle | `RawCull/Model/ViewModels/RawCullAIModelManagementModel.swift` |
| Current burst orchestration | `RawCull/Model/ViewModels/RawCullViewModel+BurstGrouping.swift` |
| Dependency-boundary verification | `Scripts/VerifyAIImportBoundary.sh` |
| Detailed migration record | `Docs/modularai.md` |

For the reusable backend and contract design, continue with [Artificial
Intelligence](ai/) and [How PhotoAIKit Is Constructed](packages/photoaikit/).
For the existing burst algorithm and persistence behavior that Phase 7 must
preserve, see [Burst Groups](burstgroup/).

## Updating This Page After Phase 7

When Phase 7 is completed, update this page from the implementation rather than
only from the plan:

1. Replace the Phase 7 status note and planned wording with the completion date
   and validation evidence.
2. Replace proposed type names with their final names and add their actual
   source paths to the source map.
3. Update the runtime ownership diagram if the compatibility reference to
   `SimilarityScoringModel` changes.
4. Confirm the cache and compute diagram against the coordinator's real phases
   and cancellation checkpoints.
5. Record automated gates and the manual burst-analysis acceptance results.
6. Run a caller and unused-code audit and document any intentionally retained
   downstream compatibility seams.
