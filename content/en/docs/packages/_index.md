+++
author = "Thomas Evensen"
title = "RawCull Packages"
linkTitle = "Packages"
date = "2026-07-18"
description = "Architecture guide to the four reusable Swift packages used by RawCull."
tags = ["ai", "analysis", "raw", "swift-package", "packages"]
categories = ["technical details"]
mermaid = true
weight = 60
+++

# RawCull Packages

RawCull is split across four reusable Swift packages. Each package owns one kind of knowledge and deliberately avoids importing the others. RawCull is the composition root: it decodes a file with RawParserKit, asks PhotoAnalysisKit or PhotoAIKit to measure it, translates the result into RawCullCore values and decisions, and presents or persists the outcome.

```mermaid
flowchart LR
    Files["ARW, NEF, and rendered files"] --> Parser["RawParserKit\ndecode + vendor metadata"]
    Parser --> Host["RawCull adapters\nsource and cache policy"]
    Host --> Analysis["PhotoAnalysisKit\nsharpness + focus evidence"]
    Host --> AI["PhotoAIKit\nembeddings + segmentation"]
    Analysis --> Host
    AI --> Host
    Host --> Core["RawCullCore\nburst grouping + ranking"]
    Core --> App["RawCull UI, persistence, and culling actions"]
```

The arrows are runtime data flow, not package dependencies. The four sibling packages do not depend on one another; the RawCull application imports and adapts them.

| Package | Owns | Deliberately leaves to RawCull |
|---|---|---|
| [PhotoAIKit](photoaikit/) | Model validation, CLIP and SAM 3 backends, Vision similarity artifacts, AI workflows, and optional storage codecs | Model installation, RAW decoding, UI state, cache locations, and culling policy |
| [PhotoAnalysisKit](photoanalysiskit/) | Sharpness scoring, saliency and classification, focus evidence and masks, calibration, and Vision feature prints | File decoding, source identity, persistence, settings wording, and culling decisions |
| [RawCullCore](rawcullcore/) | Package-safe metadata, focus-point normalization, burst grouping and ranking, and luminance histograms | RAW parsing, image analysis, application state, storage, and presentation |
| [RawParserKit](rawparserkit/) | Vendor dispatch, MakerNote and embedded-JPEG parsing, image loading, orientation, metadata extraction, and bounded decode work | Analysis, scoring, catalogs, cache policy, and UI |

## Recommended Reading Order

1. Start with RawParserKit to see how a file becomes a normalized image and metadata.
2. Continue with PhotoAnalysisKit to see how a decoded image becomes sharpness and focus evidence.
3. Read RawCullCore to see how measurements become burst boundaries and recommendations.
4. Read PhotoAIKit for optional CLIP similarity and SAM 3 segmentation workflows.

The source for this section comes from the sibling `PhotoAIKit`, `PhotoAnalysisKit`, `RawCullCore`, `RawParserKit`, and `RawCull` projects. In each package guide, paths beginning with `Sources/` and `Tests/` are relative to that package. RawCull paths such as `Model/`, `Main/`, `Views/`, and `Actors/` refer to the application target.
