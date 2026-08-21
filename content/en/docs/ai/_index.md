+++
author = "Thomas Evensen"
title = "Artificial Intelligence"
linkTitle = "AI"
date = "2026-08-21"
description = "Learning guide to PhotoAIKit and RawCull's AI integration."
tags = ["ai", "clip", "sam3", "photoaikit"]
categories = ["technical details"]
mermaid = true
weight = 60
+++

# Artificial Intelligence in RawCull

This section explains how RawCull uses reusable AI components without allowing model-runtime details to spread through the application. It is written as a learning path: first understand the boundary between RawCull and PhotoAIKit, then study the package itself, and finally follow CLIP from application startup to a persisted similarity artifact.

The source for this section comes from the sibling `PhotoAIKit` and `RawCull` projects. Paths beginning with `Sources/` refer to PhotoAIKit. Paths beginning with `Model/`, `Main/`, `Views/`, or `Actors/` refer to the RawCull app target.

## What This Section Documents

| Document | Main question | Start here when |
|---|---|---|
| This overview | Where does AI belong in the system? | You need the vocabulary and responsibility split |
| [How RawCull Enables and Uses CLIP](clip-in-rawcull/) | How does the CLIP preference become a running backend? | You are tracing model discovery, activation, RAW decoding, inference, fallback, distance calculation, or persistence |
| [AI Model Downloads](aimodeldownloads/) | Where do model assets come from? | You are changing download, acceptance, or installation behavior |


PhotoAIKit contains three backend families used by RawCull:

- **CLIP image embeddings** for visual similarity and semantic search.
- **SAM 3 and EfficientSAM subject segmentation** for subject masks.
- **Apple Vision feature prints** for always-available image similarity.

Vision is the startup and service-selection fallback: RawCull uses it when CLIP
is disabled or the selected CLIP bundle cannot produce a validated provider. A
selected CLIP indexing pass keeps its valid per-file artifacts and records the
files that fail; it does not mix Vision artifacts into that pass or
automatically rerun the whole batch.

The detailed CLIP document follows code that is connected to RawCull's similarity and burst-analysis features. The package architecture document also covers the SAM 3 contracts, workflows, and storage so that the complete package design is understandable. Not every reusable package capability is necessarily exposed as a finished RawCull user workflow.

## The Central Design Idea

RawCull and PhotoAIKit answer different kinds of questions.

**PhotoAIKit asks:**

- What does an image source look like at a package boundary?
- How is a model bundle validated and identified?
- How does a backend produce and compare a similarity artifact?
- How is bounded indexing or segmentation orchestrated?
- How can reusable artifacts and masks be encoded or cached?

**RawCull asks:**

- Where are models installed for this application?
- How is a Sony or Nikon RAW file decoded for AI input?
- Which backend did the user request?
- When should a catalog be indexed or reindexed?
- How do similarity distances affect burst grouping and culling?
- What state and wording should SwiftUI present?

This is dependency inversion in practical form. PhotoAIKit defines small protocols such as `ImageDecoding`, `ImageSimilarityArtifactProviding`, and `ImageSimilarityArtifactComparing`. RawCull injects app-specific implementations and keeps its file model, UI, sandbox policy, and culling decisions outside the package.

```mermaid
flowchart LR
    UI["RawCull SwiftUI and settings"] --> Integration["RawCullAIIntegration composition root"]
    Integration --> AppAdapter["RawCull adapters: paths, RAW decoding, policy"]
    AppAdapter --> Contracts["PhotoAIContracts"]
    Integration --> CLIP["CoreAICLIPBackend"]
    Integration --> SAM3["CoreAISAM3Backend"]
    Integration --> Vision["VisionFeaturePrintBackend"]
    AppAdapter --> Workflows["PhotoAIWorkflows"]
    Workflows --> Contracts
    Storage["PhotoAIStorage"] --> Contracts
    CLIP --> Contracts
    SAM3 --> Contracts
    Vision --> Contracts
```

The arrow direction matters: PhotoAIKit does not import RawCull. A reusable package should not need to know what `FileItem`, `RawCullViewModel`, an app-specific model folder, or a burst winner means.

## Responsibility Boundary

| Concern | Owner | Reason |
|---|---|---|
| Typed model, image, artifact, and segmentation contracts | PhotoAIKit | Backends and hosts need one stable language |
| Core AI CLIP and SAM 3 inference | PhotoAIKit backend products | Framework-specific tensor and inference code is reusable |
| Vision feature-print generation and native distance | PhotoAIKit backend product | The opaque Vision payload stays behind its backend boundary |
| Bounded indexing, optional fallback mechanisms, segmentation, and mask selection | PhotoAIKit workflows | These mechanisms do not depend on RawCull UI or culling policy |
| Optional embedding codecs and mask stores | PhotoAIKit storage | Persistence mechanics are reusable, but locations are not |
| Model installation directories and candidate order | RawCull | Paths and sandbox policy belong to the host application |
| RAW decoding | RawCull | PhotoAIKit should not depend on `RawParserKit` or camera formats |
| Settings and capability wording | RawCull | User-facing state and localization belong to the app |
| Similarity ranking adjustments and burst grouping | RawCull | These are photo-culling product decisions, not CLIP behavior |
| Burst-analysis cache location and lifecycle | RawCull | The host owns when and where catalog results persist |

## Current Runtime Shape

`RawCullAIIntegration` is the AI composition root. It owns the resource
managers, validated provider reuse, the always-available Vision backend, mask
stores, the segmentation service and selector, and `DeepAIReviewFeature`. The
app passes feature models narrow services instead of the composition root:

| Consumer | Narrow dependency | Capability and persistence rule |
|---|---|---|
| `SimilarityScoringModel` through `RawCullViewModel` | `RawCullSimilarityServicing` | Uses Vision or the selected CLIP provider; hydrates and persists descriptor-validated per-file artifacts and burst-analysis state |
| Semantic-search state in `RawCullViewModel` | `RawCullSemanticSearchServicing?` and `RawCullSemanticSearchCapability` | Exists only for a validated selected CLIP model; reuses compatible CLIP image artifacts, creates an ephemeral text embedding, and never persists the query |
| Deep Review | `DeepAIReviewFeature` | Uses the active segmentation service and mask cache; it is independent of the CLIP toggle and semantic-search readiness |
| AI settings | capability and service callbacks | Refreshes status, installs the selected similarity service, and updates semantic-search capability without rebuilding the app graph |

The safe startup and refresh path is:

1. `RawCullApp` creates one `RawCullAIIntegration`.
2. `RawCullViewModel` initially receives `visionSimilarityService`, the saved
   semantic capability snapshot, and `deepAIReviewFeature`.
3. `RawCullAISettingsModel.refresh()` asks the integration to validate both
   CLIP and both segmentation-model candidates.
4. PhotoAIKit validates model bundles and derives model-asset fingerprints.
5. A valid selected CLIP provider may replace the Vision burst-similarity
   service and enable semantic search.
6. Missing, invalid, or disabled CLIP leaves burst similarity on Vision and
   semantic search unavailable.
7. CLIP indexing retains valid files and logs per-file failures; Vision is not
   inserted into that CLIP result set.
8. Changing the segmentation selection immediately updates the active provider.
   A full refresh rechecks every candidate and saved-evidence state.

```mermaid
stateDiagram-v2
    [*] --> VisionStartup
    VisionStartup --> CheckingModels: refresh capabilities
    CheckingModels --> VisionSelected: CLIP disabled, missing, or invalid
    CheckingModels --> CLIPSelected: preference enabled and provider ready
    CLIPSelected --> CLIPArtifacts: keep valid per-file artifacts
    CLIPSelected --> PartialCLIP: record and exclude failed files
    VisionSelected --> VisionArtifacts: index catalog
    CheckingModels --> SegmentationSelected: activate SAM 3 or EfficientSAM
```

Burst similarity, semantic search, and Deep Review are separate features even
when they share package code. Burst similarity may use Vision or CLIP. Semantic
search requires CLIP image artifacts whose descriptor exactly matches the text
provider. Deep Review uses segmentation masks and has its own availability,
selection, and storage lifecycle.

## Vocabulary

| Term | Meaning in this codebase |
|---|---|
| **Provider** | A backend object that performs inference or creates an artifact |
| **Backend descriptor** | Identity of the backend, model, representation, preprocessing, normalization, and configuration |
| **Similarity artifact** | A descriptor plus a backend-owned payload; CLIP stores an encoded vector, while Vision stores an opaque archived observation |
| **Source fingerprint** | Standardized file path, size, and modification date used to detect changed source images |
| **Model fingerprint** | Identity derived from the selected `.aimodel` or `.aimodelc`, cryptographically verified when the manifest provides a checksum |
| **Composition root** | The one place where concrete providers, stores, paths, and app adapters are assembled |
| **Partial CLIP result** | Valid CLIP artifacts plus per-file failures; failed files remain unavailable to similarity and burst grouping until a later successful index |
| **Host** | The application integrating PhotoAIKit; here, RawCull |

## Suggested Learning Order

This section follows the main documentation index: first read the scan,
concurrency, cache, focus/sharpness, and burst-group pages. Then read this
overview and [RawCull Packages](../packages/) for the boundaries. Continue with
[How PhotoAIKit Is Constructed](../packages/photoaikit/), then follow the live
path in [How RawCull Loads and Uses CLIP](clip-in-rawcull/) and [AI Runtime Step
by Step](stepbystepAI/).

Installation and acceptance steps intentionally live only in [AI Model
Downloads](aimodeldownloads/). The architecture pages describe managed
locations and validation but do not duplicate download procedures.
