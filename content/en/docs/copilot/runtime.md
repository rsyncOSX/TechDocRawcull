+++
author = "Thomas Evensen"
title = "The Intelligence Runtime"
linkTitle = "Intelligence Runtime"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "How RawCull constructs, refreshes, and safely extends its long-lived intelligence runtime."
tags = ["rawcull", "ai", "runtime", "dependency-injection"]
categories = ["technical details"]
weight = 55
+++

# The Intelligence Runtime

This document is a deep dive into `RawCullIntelligenceRuntime` and its
composition partner `RawCullAIIntegration` — together "the runtime" — which
is only summarized in
[Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/#composition-root-rawcullintelligenceruntime--rawcullaiintegration).
Read that doc first for the subsystem's overall shape (folders, backends,
CoreAI attribution); this document explains **how the runtime object itself
is built, how it reacts when a part of its configuration changes, how to
extend it safely, and why it's built this way**.

## What "the runtime" actually is

Two collaborating types, both `@MainActor`, with a strict division of
responsibility:

| Type | Role | Lives in |
|---|---|---|
| `RawCullAIIntegration` | Owns every concrete provider (CoreAI CLIP/SAM providers, the Vision fallback, model-resource managers, the subject-mask repository) and knows how to (re)validate and (re)build them. Never seen by views or `RawCullViewModel`. | `Intelligence/Composition/RawCullAIIntegration.swift` |
| `RawCullIntelligenceRuntime` | The stable, long-lived object `RawCullApp` actually holds. Owns the feature-facing models (`similarityFeature`, `semanticSearchFeature`, `deepAIReviewController`, `settingsModel`, `modelManagementModel`) and the **single entry point** through which a settings change is turned into "swap this one service, leave everything else alone." | `Intelligence/Composition/RawCullIntelligenceRuntime.swift` |

Neither type is a singleton (no `static let shared`) — instead, exactly one
of each is constructed by `RawCullApplicationState`, once, at app launch, and
threaded everywhere else by reference. This is deliberate: see
["Why this design is good"](#why-this-design-is-good) below.

## Creating the runtime

`RawCullApp.init()` calls `RawCullApplicationState.live()`, which forwards to
`RawCullApplicationState.make(integration:...)` (`RawCullIntelligenceRuntime.swift`,
lines ~151-224). `make(...)` takes every external dependency as a
parameter with a production default (`RawCullAIIntegration()`,
`PerFileAnalysisArtifactStore.shared`, `UserDefaults.standard`,
`RawCullAIModelDownloadCatalog.production`, ...) — this is what lets
`RawCullTests` construct a fully wired runtime against fakes without
touching the real filesystem or downloading real models.

Construction happens in a fixed, dependency-respecting order:

```swift
1. modelManagementModel = RawCullAIModelManagementModel(...)      // download/licence lifecycle
2. settingsModel = RawCullAISettingsModel(integration:, modelManagementModel:)
3. initialConfiguration = settingsModel.configurationSnapshot()   // revision 0, synchronous, no I/O
4. similarityModel = SimilarityScoringModel(similarityService: initialConfiguration.similarity.service, ...)
5. similarityFeature = RawCullSimilarityFeature(similarityModel:)
6. semanticSearchFeature = RawCullSemanticSearchFeature(similarityModel:, similarityFeature:)
7. deepAIReviewController = DeepAIReviewController(feature: integration.deepAIReviewFeature)
8. viewModel = RawCullViewModel(similarityModel:, similarityFeature:, semanticSearchFeature:, deepAIReviewController:)
9. intelligenceRuntime = RawCullIntelligenceRuntime(integration:, similarityFeature:, semanticSearchFeature:,
                                                     deepAIReviewController:, settingsModel:,
                                                     applicationContext: viewModel)
10. semanticSearchFeature.bindApplicationTarget(viewModel)
11. settingsModel.bindConfigurationConsumer(intelligenceRuntime)
```

Two things are worth noticing about this order:

- **Step 3 reads `settingsModel`'s *synchronous* snapshot** (whatever
  `UserDefaults` says the user last chose, paired with whatever
  `integration.capabilities()` already knows at construction time — before
  any async model validation has run). This is intentionally cheap and
  synchronous so the app can finish building its object graph and show a UI
  immediately; it does **not** wait for model files to be validated on disk.
  The real, validated capabilities arrive later (see
  ["The first refresh"](#the-first-refresh-after-launch) below) and flow
  through the exact same `apply(configuration:)` path as any other runtime
  settings change — there is no separate "initial capability" code path.
- **`bindConfigurationConsumer` is called last**, and it is itself what
  triggers the *first* `apply(configuration:)` call (see
  `RawCullAISettingsModel.bindConfigurationConsumer`, which calls
  `publishConfiguration()` immediately after storing the weak reference).
  So even though step 3's snapshot was never explicitly "applied," its
  *equivalent* — freshly recomputed at bind time — is applied as revision 1
  once the whole graph exists and can safely receive it.

### Post-construction identity assertions

`make(...)` ends with a block of `assert(...)` calls
(`viewModel.similarityFeature === intelligenceRuntime.similarityFeature`,
`semanticSearchFeature.sharesSimilarityFeatureIdentity(with:)`,
`settingsModel.modelManagementModel === intelligenceRuntime.modelManagementModel`,
etc.) — debug-only checks (compiled out in Release via `assert`) that fail
loudly if a future refactor accidentally constructs a second instance of any
of these objects instead of reusing the one built here. Because nothing
else in the app is allowed to call these initializers directly (by
convention, not by access control), these assertions are effectively a
regression test for "the composition root is still the only place that
builds these."

### The first refresh after launch

`RawCullMainView`'s `.task { await intelligenceRuntime.settingsModel.refresh() }`
(`RawCullApp.swift`) is the very first thing that happens once the main
window's view tree appears. This is what actually validates model bundles on
disk and reconciles the runtime with reality — see the full flow in the next
section, since it's the same machinery used for every later settings/model
change, not a special-cased startup routine.

## How a change flows through the runtime

There are exactly two kinds of events that can change what the runtime's
features are backed by, and both end up going through the same funnel:

1. **The user changes an AI setting** — `RawCullAISettingsModel.setUseCLIPForSimilarity(_:)`,
   `setSelectedCLIPModel(_:)`, or `setSelectedSegmentationModel(_:)`, each
   bound to a SwiftUI control in `Views/Settings/AISettingsTab.swift`.
2. **Model availability changes** — a model finishes downloading, a licence
   is accepted, a model is removed, or the app performs its first
   post-launch validation pass. All of these go through
   `RawCullAIModelManagementModel.refresh()` (called directly, or as the
   tail end of `startModelDownload`/`acceptModelLicence`/`removeManagedModel`).

Both paths converge on `RawCullAISettingsModel.publishConfiguration()`:

```swift
private func publishConfiguration() {
    guard let configurationConsumer else { return }
    configurationRevision &+= 1
    capabilities = configurationConsumer.apply(
        configuration: configurationSnapshot(revision: configurationRevision),
    )
}
```

Full call graph for path 2 (the more involved one):

```
RawCullAIModelManagementModel.refresh()
  → coordinator.snapshot()                          // Background Assets download states
  → apply(snapshot:)                                 // updates `presentations` for Settings UI
  → locationsConsumer.applyManagedModelLocations(_:) // = RawCullAISettingsModel
      → integration.setManagedModelLocations(_:)     // tell each resource manager the on-disk URL
      → integration.refreshCapabilities()  ─┐ concurrently
      → evidenceScan()                     ─┘
          // refreshCapabilities() re-validates every model bundle off the
          // main actor via `async let`, rebuilds `clipSimilarityProviders`/
          // `segmentationProviders`, and returns a fresh `RawCullAICapabilities`
      → self.capabilities = <fresh capabilities>
      → publishConfiguration()
          → configurationConsumer.apply(configuration:)  // = RawCullIntelligenceRuntime
              → compares identity, replaces only what changed (see below)
              → returns integration.capabilities()
      → self.capabilities = <returned capabilities>      // published a second time, now via apply()'s return value
```

Path 1 (user flips a setting) is the same tail: `set...(_:)` mutates the one
`@Observable` field, persists it to `UserDefaults`, and calls
`publishConfiguration()` directly — no re-validation needed since the model
files on disk haven't changed, only which validated provider the user wants
used.

### `RawCullIntelligenceConfiguration`: the message passed at each step

Every `apply(configuration:)` call receives one of these
(`RawCullIntelligenceRuntime.swift`, lines 27-43):

```swift
@MainActor
struct RawCullIntelligenceConfiguration {
    let revision: UInt64
    let similarity: RawCullSimilarityConfiguration       // wraps `any RawCullSimilarityServicing`
    let semanticSearch: RawCullSemanticSearchConfiguration // capability + optional `any RawCullSemanticSearchServicing`
    let segmentationModel: RawCullSegmentationModel        // .sam3 / .efficientSAM

    var identity: RawCullIntelligenceConfigurationIdentity { ... }
}
```

Note the `@MainActor` isolation and the concrete `any RawCullSimilarityServicing`
provider reference inside it — this whole struct, and the CoreAI-backed
providers it can carry, **never crosses an actor/task boundary**. Only its
computed `.identity` does real comparison work, and `identity` is a separate,
`Sendable`, value-only struct:

```swift
nonisolated struct RawCullIntelligenceConfigurationIdentity: Equatable, Sendable {
    let similarityBackend: SimilarityBackendDescriptor
    let similarityArtifactBackends: [SimilarityBackendDescriptor]
    let semanticSearchCapability: RawCullSemanticSearchCapabilityStatus
    let semanticSearchBackend: SimilarityBackendDescriptor?
    let segmentationModel: RawCullSegmentationModel
}
```

`SimilarityBackendDescriptor` (from `PhotoAIContracts`) is a small value type
(backend name, model fingerprint, preprocessing/normalization versions) — it
describes a provider well enough to detect "did the effective backend
actually change" without needing the provider itself to be `Sendable` or
`Equatable`. This is the same "encode identity as a small Sendable value,
keep the real object `@MainActor`-only" pattern the disk-cache/thumbnail
pipeline uses for `CGImage`/`Data` (see
[Concurrency Architecture](../01-concurrency-architecture/)) — here
applied to service *instances* rather than pixel buffers.

### `apply(configuration:)`: revision gate, then identity diff

```swift
func apply(configuration: RawCullIntelligenceConfiguration) -> RawCullAICapabilities {
    let incomingIdentity = configuration.identity

    if let lastAcceptedConfigurationRevision {
        guard configuration.revision > lastAcceptedConfigurationRevision else {
            assert(
                configuration.revision < lastAcceptedConfigurationRevision
                    || incomingIdentity == lastAppliedConfigurationIdentity,
                "One configuration revision described multiple identities.",
            )
            return integration.capabilities()
        }
    }

    let previousIdentity = lastAppliedConfigurationIdentity
    guard previousIdentity != incomingIdentity else {
        lastAcceptedConfigurationRevision = configuration.revision
        return integration.capabilities()
    }

    if previousIdentity?.segmentationModel != incomingIdentity.segmentationModel {
        integration.setSelectedSegmentationModel(configuration.segmentationModel)
    }
    if previousIdentity?.similarityBackend != incomingIdentity.similarityBackend
        || previousIdentity?.similarityArtifactBackends != incomingIdentity.similarityArtifactBackends {
        similarityFeature.replaceSimilarityService(configuration.similarity.service)
    }
    if previousIdentity?.semanticSearchCapability != incomingIdentity.semanticSearchCapability
        || previousIdentity?.semanticSearchBackend != incomingIdentity.semanticSearchBackend {
        similarityFeature.replaceSemanticSearchConfiguration(
            capability: configuration.semanticSearch.capability,
            service: configuration.semanticSearch.service,
        )
    }

    lastAppliedConfigurationIdentity = incomingIdentity
    lastAcceptedConfigurationRevision = configuration.revision
    return integration.capabilities()
}
```

Three distinct guards, in order:

1. **Staleness/ordering guard** (`configuration.revision > lastAcceptedConfigurationRevision`).
   `configurationRevision` on `RawCullAISettingsModel` only ever increments,
   and every `publishConfiguration()` call is synchronous on the main actor,
   so in practice revisions cannot actually arrive out of order today — but
   the guard exists so that if a future change ever made `publishConfiguration()`
   async (e.g. awaiting something before calling `apply`), an old,
   slow-to-arrive configuration could never clobber a newer one. This is the
   same generation/revision-counter idiom used throughout the codebase
   (`RequestThumbnail.generation`, `BurstAnalysisCoordinator.generation`,
   `CullingModel.persistenceRevision` — see
   [Concurrency Architecture](../01-concurrency-architecture/) and
   [Culling and Persistence](../03-culling-and-persistence/)). The
   nested `assert` is a correctness canary, not a runtime safeguard: it
   would only fire if a caller reused the same revision number for two
   genuinely different configurations, which would indicate a bug in the
   revision-incrementing logic itself.
2. **No-op guard** (`previousIdentity != incomingIdentity`). A configuration
   can have a strictly newer revision but describe the *same* effective
   backends — e.g. the user toggled a segmentation model preference that
   happens to already be selected, or `refreshCapabilities()` ran but every
   provider it found was identical to what was already active. In that case
   the revision bookkeeping still advances (so a later out-of-order push is
   still rejected correctly), but no feature is touched.
3. **Per-field diff** — the three `if previousIdentity?.field != incomingIdentity.field`
   checks are the heart of the design: each compares only the slice of
   identity relevant to one feature and calls the *one* corresponding
   mutator. A CLIP model swap only ever calls
   `similarityFeature.replaceSimilarityService(...)` (and, if semantic
   search's capability/backend also changed, `replaceSemanticSearchConfiguration(...)`)
   — it never touches segmentation, and vice versa.

### What "replacing a service" actually does downstream

- **Segmentation**: `integration.setSelectedSegmentationModel(_:)` updates
  `capabilitySnapshot`, then calls `activateSelectedSegmentationProvider(availability:)`,
  which looks up the already-validated provider for the newly selected model
  in `segmentationProviders[selectedSegmentationModel]` (populated by the
  most recent `refreshCapabilities()` — swapping the *selection* never
  re-validates a model from disk; that only happens during a `refresh()`
  cycle) and calls `installSegmentationProviderIfNeeded(_:)`. That method
  compares `provider.modelIdentity` against the currently active one and,
  only if it actually differs, rebuilds the small dependent object graph
  (`SubjectMaskRepositoryConfiguration` → `SubjectMaskRepository` →
  `SegmentationService` → `SubjectMaskSelector`) and reinstalls the Deep
  Review pipeline (`deepAIReviewFeature.install(service:maskLoader:availability:)`).
  If no validated provider exists yet for the selection, an
  `UnavailableSegmentationProvider` is installed instead, which throws a
  clear `SubjectSegmentationError.providerFailure` if Deep Review is invoked
  — there's no silent no-op mode.
- **Similarity**: `similarityFeature.replaceSimilarityService(_:)` swaps the
  backend `SimilarityScoringModel` uses for grouping/indexing. Because the
  configuration always carries a *concrete, already-constructed* service
  (Vision fallback or a validated CoreAI CLIP provider — decided by
  `RawCullAIIntegration.similarityService(prefersCLIP:clipModel:)`, which
  itself falls back to Vision and logs a warning if the requested CLIP
  provider isn't validated/available), the swap is just a reference
  assignment plus whatever bookkeeping `SimilarityScoringModel` does
  internally to invalidate in-flight indexing — it is not a re-index of
  every photo from scratch.
- **Semantic search**: `replaceSemanticSearchConfiguration(capability:service:)`
  updates the feature's reported capability status and, if a validated CLIP
  provider exists, wires up `RawCullCLIPSemanticSearchService`; otherwise it
  reports `.unavailable`/`.failed` per
  [Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/#semantic-search).

## Why this design is good

- **Single choke point, no scattered mutation.** Nothing outside
  `RawCullIntelligenceRuntime.apply(configuration:)` is allowed to call
  `similarityFeature.replaceSimilarityService(...)` or
  `integration.setSelectedSegmentationModel(...)` directly — every settings
  change and every model-download completion funnels through the exact same
  function. A new engineer adding a new toggle only has to make sure it ends
  up inside a `RawCullIntelligenceConfiguration` and bumps a revision; they
  don't need to learn a second wiring path.
- **Cheap no-ops by construction.** Because identity comparison happens
  before any mutation, a spurious `refresh()` (the download-progress
  callback fires often, and `refresh()` is also called unconditionally at
  launch) costs one struct comparison, not a service teardown/rebuild —
  this matters because `refreshCapabilities()` runs on every model download
  completion and could otherwise cascade into unnecessary re-indexing.
- **Minimal blast radius per change.** The three independent `if` guards
  mean a segmentation-model change can never accidentally also swap the
  similarity backend, and vice versa — each feature is only ever told to
  update when *its own* piece of identity actually changed, which is only
  possible because identity is modeled as one struct with independently
  comparable fields rather than one opaque hash.
- **Sendability is enforced by the type system, not convention.**
  `RawCullIntelligenceConfigurationIdentity` is the only thing that's
  `Sendable`/comparable across isolation boundaries; the actual providers
  stay `@MainActor`-confined inside `RawCullIntelligenceConfiguration`. A
  future contributor cannot accidentally make a CoreAI provider cross an
  actor boundary through this path — the compiler would reject it, since
  `RawCullIntelligenceConfiguration` itself is explicitly `@MainActor` and
  not `Sendable`.
- **Ordering safety without complexity.** The revision counter handles the
  theoretical async-reordering case cheaply (one integer comparison) instead
  of requiring `apply` to be reentrant-safe or serialized behind a task
  queue — appropriate given today's call sites are all synchronous, but it
  costs nothing to keep it correct if that ever changes.
- **Composition root discipline is self-enforcing.** The `assert(x === y)`
  calls in `RawCullApplicationState.make(...)` turn "don't build a second
  instance of this" from a code-review convention into something that fails
  a debug build immediately if violated.
- **Dependency injection for free.** Every collaborator `RawCullAIIntegration`
  and `RawCullApplicationState.make(...)` need is a constructor parameter
  with a production default, so tests can substitute fakes
  (`similarityArtifactStore:`, `evidenceScan:`, `modelDownloadCoordinator:`,
  `userDefaults:`) without touching real models, real downloads, or real
  `UserDefaults`.

## How to update or extend the runtime

- **Add a new user-facing AI setting that changes runtime behavior**
  (e.g. a new backend choice): add the stored property + persistence to
  `RawCullAISettingsModel` next to `selectedCLIPModel`/`selectedSegmentationModel`,
  add the corresponding field to `RawCullIntelligenceConfiguration` *and*
  `RawCullIntelligenceConfigurationIdentity`, populate it in
  `configurationSnapshot()`, and add one more `if previousIdentity?.field != incomingIdentity.field`
  branch in `apply(configuration:)` that calls the one method responsible
  for swapping that feature's backend. Do **not** have the setting call a
  feature model directly — always go through `publishConfiguration()`.
- **Add a new downloadable model type**: extend
  `RawCullAIModelDownloadCatalog`/`RawCullAIModelDownloadID`, add a
  `RawCullAIModelResourceManager<YourProvider>` to `RawCullAIIntegration`
  (mirroring `clipDataCompModelResourceManager`), include it in the
  `async let` group inside `refreshCapabilities()`, and fold its status into
  `RawCullAICapabilities`. The settings/model-management flow
  (`refresh()` → `applyManagedModelLocations(_:)` → `refreshCapabilities()`)
  needs no changes — it's already generic over "however many resource
  managers exist."
- **Add a brand-new AI feature** (beyond similarity/semantic search/deep
  review): give it its own feature model analogous to
  `RawCullSimilarityFeature`, construct it in
  `RawCullApplicationState.make(...)` alongside the existing features, hold
  it on `RawCullIntelligenceRuntime`, and — only if its backend can actually
  change at runtime — add it to `RawCullIntelligenceConfiguration`/`Identity`
  and a diff branch in `apply(configuration:)`. If it has no swappable
  backend (e.g. it's a pure consumer of an already-configured feature, like
  Deep Review is a consumer of the segmentation provider `RawCullAIIntegration`
  already manages), it doesn't need its own configuration field at all.
- **Never** construct a second `RawCullAIIntegration`,
  `RawCullIntelligenceRuntime`, or `SimilarityScoringModel` outside
  `RawCullApplicationState.make(...)` — if a test needs an isolated runtime,
  call `make(...)` again with fresh fakes rather than reaching into an
  existing one, and add an `assert(x === y)` identity check alongside the
  existing ones if you introduce a new "these two references must be the
  same object" invariant.

## Where this fits in the documentation catalog

This document sits underneath
[Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/) as an
optional deep dive — read 05 first for the subsystem's overall shape, then
come here when you need to actually change how settings propagate, add a new
AI backend, or understand why a particular `apply(configuration:)` guard
exists. It assumes the actor/Sendable vocabulary from
[Concurrency Architecture](../01-concurrency-architecture/) and the
generation-counter pattern also used in
[Culling and Persistence](../03-culling-and-persistence/).
