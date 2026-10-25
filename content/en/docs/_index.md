---
title: RawCull Tech Documentation
linkTitle: Documentation
menu: { main: { weight: 20 } }
lastmod: 2026-10-25
---

## RawCull Developer Notes

These pages explain RawCull from a developer's point of view. They are intended
for readers who already understand Swift and SwiftUI and now need to learn where
behavior lives, how data moves through the app, and which invariants must
survive a change.

Source paths in these pages are relative to the named repository. App paths such
as [RawCull/Model/ViewModels/RawCullViewModel.swift](https://github.com/rsyncOSX/RawCull/blob/7b8e200f07ceb8a6f10947236a5f3de5a099fb45/RawCull/Model/ViewModels/RawCullViewModel.swift) belong to the RawCull
repository. Package paths belong to the separately versioned Swift packages
referenced by `RawCull.xcodeproj`; this documentation repository does not
contain or compile source snapshots.

## Start Here

Read these pages in this order when learning the project:

1. [Thumbnails and Scan Pipeline](thumbnail/) follows a selected catalog from
   directory discovery to visible images.
2. [Viewer Architecture and Keyboard Ownership]({{< relref "viewer-architecture.md" >}})
   follows screen sessions, task identity, overlays and keyboard routing.
3. [Concurrency](concurrency-revised/) explains `@MainActor`, actor ownership,
   cancellation, and bounded parallelism across that pipeline.
4. [Cache System](cache/) explains why grid, preview, disk, full-size, and
   analysis caches are separate.
5. [Focus Mask and Sharpness](focusmask/) follows scoring and focus evidence
   into persisted culling data.
6. [Burst Groups](burstgroup/) combines sharpness, similarity artifacts,
   grouping, ranking, and the burst-review UI.
7. [Artificial Intelligence](ai/) and [RawCull Packages](packages/) explain the
   reusable package boundaries behind the app.

Use [File Read and Write](filereadandwrite/) and
[Security-Scoped URLs](security/) whenever a change touches persistence, caches,
user-selected folders, export, or copying.

## Repository And Target Map

| Area                       | Primary source                                                            | Responsibility                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| App composition            | [RawCull/Main/RawCullApp.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Main/RawCullApp.swift)                                           | Uses `RawCullApplicationState.live()` to assemble stable models/features, inject environment state, and define windows and commands |
| Main presentation          | [RawCull/Main/RawCullMainView.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Main/RawCullMainView.swift)                                      | Switches between loupe, grid, similarity, rated, and comparison modes and owns top-level sheets and overlays                  |
| App orchestration          | [RawCull/Model/ViewModels/RawCullViewModel.swift](https://github.com/rsyncOSX/RawCull/blob/7b8e200f07ceb8a6f10947236a5f3de5a099fb45/RawCull/Model/ViewModels/RawCullViewModel.swift) plus feature extensions | Coordinates catalog, selection, navigation, progress and feature actions; dedicated models own review and semantic state                         |
| Background ownership       | `RawCull/Actors/`                                                         | Serializes scans, thumbnail requests, caches, persistence, extraction, and contention gates                                   |
| App services and adapters  | `RawCull/Model/`                                                          | Connects the UI model to RAW parsing, sharpness analysis, AI providers, persistence, diagnostics, and rsync                   |
| Reusable domain logic      | `RawCullCore` package                                                     | Value models and pure algorithms such as burst grouping and ranking                                                           |
| RAW decoding               | `RawParserKit` package                                                    | Dedicated ARW/NEF/DNG and generic macOS-backed RAW dispatch, metadata normalization, MakerNote parsing, thumbnail extraction, and preview creation              |
| Image analysis             | `PhotoAnalysisKit` package                                                | Sharpness, saliency, focus evidence, masks, and analysis descriptors                                                          |
| AI contracts and workflows | `PhotoAIKit` package products                                             | Typed similarity artifacts, Vision/CLIP backends, semantic search, segmentation, and storage contracts                        |
| Tests                      | `RawCullTests/` and package test targets                                  | Executable behavior contracts, concurrency checks, cache identity checks, and integration coverage                            |

## Architectural Shape

```mermaid
flowchart TD
    App["RawCullApp: composition root"] --> Main["RawCullMainView: presentation router"]
    Main --> VM["RawCullViewModel: @MainActor orchestration"]
    VM --> Feature["Feature models: culling, sharpness, similarity, Deep Review, settings"]
    VM --> Actors["Actors: scan, thumbnail, cache, persistence, export"]
    Feature --> Analysis["PhotoAnalysisKit"]
    Feature --> AI["PhotoAIKit services and typed artifacts"]
    Actors --> Parser["RawParserKit"]
    VM --> Core["RawCullCore pure models and algorithms"]
    Actors --> Storage["Application Support, Caches, selected folders"]
```

The boundaries are based on ownership:

- SwiftUI views render observable state and translate gestures, commands, and
  bindings into model actions.
- `RawCullViewModel` and feature view models are `@MainActor` because their
  state drives presentation.
- Actors own shared mutable background state and serialize work such as cache
  access, thumbnail coalescing, and writes.
- `RawCullCore` contains reusable value models and pure decisions that do not
  need UI isolation.
- `RawParserKit`, `PhotoAnalysisKit`, and `PhotoAIKit` hide specialized parsing
  and analysis implementations behind typed boundaries.
- Security-scoped access remains alive at the app or operation boundary for as
  long as user-selected files are used.

## Follow One Feature Through The Code

When investigating a behavior, read it in this direction:

1. Find the SwiftUI control or lifecycle trigger.
2. Find the `RawCullViewModel` or feature-model method it calls.
3. Identify which actor, adapter, or package owns the expensive or mutable work.
4. Follow the value returned to main-actor state.
5. Read the tests named after the actor, model, or feature before changing the
   invariant.

This approach is more reliable than starting with an individual utility type
because it shows both ownership and the complete lifetime of the operation.

## Focused References

| Page                                                  | Use it when changing                                          |
| ----------------------------------------------------- | ------------------------------------------------------------- |
| [Memory Pressure](memorypressure/)                    | Cache limits, pressure events, or diagnostics                 |
| [Detailed Sharpness Scoring](detailsharpnessscoring/) | Formula-level sharpness behavior and score-impacting factors  |
| [Detailed Focus Mask Computation](detailsfocusmask/)  | Focus-mask rendering, region selection, and visual thresholds |
| [Synchronous Code](heavy/)                            | Blocking ImageIO, RAW parsing, or explicit executor bridges   |
| [Sony/Nikon MakerNote Parser](sonymakernoteparser/)   | Focus-point metadata and vendor-specific parsing              |
| [AI Model Downloads](ai/rawcullai/)            | Model installation, validation, signing, and activation       |
| [Repository Git Workflow](pushpull/)                  | The documentation repository's linear-history workflow        |

## Reviewed source baseline

Reviewed on **23 October 2026** against **RawCull 3.3.5, build 426**, commit
`2ca891be5c013dc38fe3c931a829a04083b69c2a` on `version-3.3.5`. GitHub links to current app code use that immutable
commit. This is the inspected checkout, not a claim about the newest published
release. Packages follow [Package.resolved](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved).
RawParserKit remains 1.3.2. All resolved package revisions are unchanged from
the October 22 source baseline.

Read [Viewer Architecture and Keyboard Ownership]({{< relref "viewer-architecture.md" >}})
for the October viewer refactor and
[RAW Formats and Exposure Inspection]({{< relref "raw-inspection.md" >}})
for generic RAW admission, temporary EV rendering, histogram and clipping.
The [review record]({{< relref "update.md" >}}) lists every page's disposition
and validation limits. The [developer guide]({{< relref "apidocs/rawcullapidoc.md" >}})
provides the application tour; its detailed method reference is now separate.

## State ownership and performance in build 426

`RawCullViewModel` retains [BurstReviewSessionModel.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Model/ViewModels/BurstReviewSessionModel.swift)
for review decisions, independently of viewport/image sessions.
`SimilarityScoringModel` retains [RawCullSemanticSearchModel.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Intelligence/SemanticSearch/RawCullSemanticSearchModel.swift)
for semantic evidence, provider configuration and queries, while keeping its
existing forwarding API. Combined Review still has one mutable feature/run
owner, with orchestration, work support and comparison in separate extensions.

Preload workers await disk saves before releasing worker slots, but release
each file's grid gate before the save. See
[Performance Measurement]({{< relref "performance.md" >}}) for real-catalog
the October 25 reference, coalesced progress, cache-state limits and deferred
validation. Encoder, grid and source-load optimizations were deferred; reduced
sampled main-thread work does not establish faster loading or smoother frames.
The smoke inventory expects 401 unique identifiers; that enumeration is not a
claim that every test was rerun during this documentation pass.
