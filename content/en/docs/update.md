---
title: Documentation Update Plan
description:
  Prioritized backlog for keeping RawCull technical documentation aligned with
  the code
weight: 95
lastmod: 2026-08-20
---

# Documentation Update Plan

This page is the working backlog for future TechDocRawCull updates. It is
ordered by the risk that stale documentation will teach the wrong architecture,
not simply by the age or length of an article.

The intended reader understands Swift and SwiftUI at an intermediate level. Each
article should therefore explain ownership, data flow, cancellation,
persistence, and extension points before presenting low-level formulas or
implementation details.

## Recently Completed Baseline

The following pages were reconciled with the RawCull source on 20 August 2026
and form the current learning path:

| Page                                          | Current baseline                                                                                         |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| [RawCull Tech Documentation](../)             | Repository map, composition root, architecture, and reading order                                        |
| [Burst Groups](../burstgroup/)                | Backend-selectable similarity artifacts, per-file persistence, cache schema 9, and the current workspace |
| [Thumbnails and Scan Pipeline](../thumbnail/) | Preload gating, request coalescing, replacement-safe identity, and current cache admission rules         |
| [Cache System](../cache/)                     | Representation-aware thumbnail caches and two-level similarity persistence                               |
| [File Read and Write](../filereadandwrite/)   | Settings JSON, saved-data recovery, exports, security scopes, diagnostics, and rsync cleanup             |

These pages still need review whenever their source areas change, but they are
not part of the immediate stale-document backlog below.

## Priority Definitions

| Priority | Meaning                                                                                                                | Target                                            |
| -------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| P0       | The article may currently teach an incorrect runtime model or important invariant                                      | Update before using it as an implementation guide |
| P1       | The article is broadly useful but lacks current ownership, UI flow, testing, or failure behavior                       | Update after P0                                   |
| P2       | The article is specialized or operational and should be checked against current packages, release tooling, or evidence | Update after core architecture pages              |
| P3       | The content is stable process guidance with low architectural risk                                                     | Review when the workflow changes                  |

## P0 — Correct The Core Runtime Model

Status: **Completed**

### 1. Concurrency

Page: [Concurrency](../concurrency-revised/)

Why first:

- The introduction still names the `RawCullAIModels` branch rather than
  documenting the current repository state.
- The article predates the latest thumbnail contention work and should
  explicitly include `ThumbnailPreloadGate`, exact-key request coalescing,
  waiter cancellation, and replacement-safe cache identity.
- It should connect application termination, persistence flushing, catalog
  security scope, JPG export scope, and rsync operation scope to their actual
  owners.

Required update:

- Start at `RawCullApp`, `RawCullMainView`, and the
  `@MainActor RawCullViewModel` composition and presentation boundaries.
- Add a hop diagram for catalog load, visible thumbnail demand, burst indexing,
  and application termination.
- Distinguish actor serialization, bounded task groups, explicit
  `Task.detached`, and framework callbacks.
- Document generation checks, latest-wins behavior, continuation ownership, and
  cancellation cleanup.
- Add a source-to-test table for concurrency invariants.

Completion evidence:

- Every named actor and task owner exists in the current source.
- `ThumbnailContentionTests`, `ThumbnailLoaderConcurrencyTests`, persistence
  tests, and security-scope tests support the documented rules.

### 2. Focus Mask And Sharpness Overview

Page: [Focus Mask and Sharpness](../focusmask/)

Why now:

- It is the bridge between the UI, `SharpnessScoringModel`, `FocusMaskModel`,
  PhotoAnalysisKit, saved culling data, and burst ranking.
- Recent scoring settings, source selection, calibration, and cache-signature
  changes should be reflected before readers use the detailed algorithm pages.

Required update:

- Add an ownership diagram from `SharpnessControlsView` and scoring sheets
  through the main-actor models into PhotoAnalysisKit.
- Explain `SharpnessAnalysisDescriptor`, effective thumbnail size, source
  choice, calibration lifetime, and persistence validation.
- Separate scalar sharpness, saliency evidence, focus-point evidence, and the
  rendered focus mask.
- Document cancellation, bounded scoring, progress publication, and stale-result
  prevention.
- Replace broad file lists with a guided “read these files in order” section.

### 3. Detailed Sharpness Scoring

Page: [Detailed Sharpness Scoring](../detailsharpnessscoring/)

Required update:

- Revalidate every constant, default, formula, quality preset, source choice,
  and score range against the pinned PhotoAnalysisKit revision.
- Label package-owned behavior separately from RawCull-owned orchestration and
  UI normalization.
- Add one compact worked example for a medium-level reader before the
  formula-by-formula reference.
- Link each major step to the test that protects it.
- Remove duplicated explanation already covered by the overview and retain this
  page as the algorithm-level reference.

### 4. Detailed Focus Mask Computation

Page: [Detailed Focus Mask Computation](../detailsfocusmask/)

Required update:

- Revalidate mask stages, region-selection rules, AF weighting, patch ranking,
  thresholds, and debug modes against PhotoAnalysisKit.
- Explain which values change the scalar score, which change only mask
  presentation, and which are calibration output.
- Add a data-shape diagram showing `CGImage`/`CIImage`, analysis values, mask
  output, and the SwiftUI overlay boundary.
- Reduce repetition with the overview while preserving the step-by-step source
  walkthrough.

## P1 — Complete The Architecture Learning Path

Status: **Completed**

### 5. AI Section Overview

Page: [Artificial Intelligence in RawCull](../ai/)

Required update:

- Present `RawCullAIIntegration` as the composition root and list the narrow
  services passed into feature models.
- Separate burst similarity, semantic search, and Deep Review; they use related
  packages but have different capability and persistence rules.
- Explain Vision availability, optional CLIP selection, CLIP-to-Vision recovery,
  segmentation model selection, and capability refresh.
- Align its learning order with the main documentation index and remove
  duplicated model-download instructions.

### 6. CLIP Runtime Integration

Page: [How RawCull Loads and Uses CLIP](../ai/clip-in-rawcull/)

Required update:

- Verify startup behavior, managed model locations, bundle validation, provider
  reuse, model fingerprints, and settings callbacks.
- Add the current boundary between burst similarity artifacts and
  semantic-search artifacts.
- Document partial CLIP generation, whole-batch Vision fallback, diagnostic
  logging, and descriptor validation.
- Explain per-file artifact hydration and why changing backend descriptors
  invalidates reuse.

### 7. Package Overview And Reading Order

Page: [RawCull Packages](../packages/)

Required update:

- Derive the package list and revisions from `Package.resolved`.
- Show which products are imported by the app and which types form each
  boundary.
- Add a dependency-direction diagram covering RawCullCore, RawParserKit,
  PhotoAnalysisKit, PhotoAIKit, and the rsync support packages.
- State that package repositories are separately versioned and are not source
  snapshots inside TechDocRawCull.

### 8. PhotoAIKit

Page: [How PhotoAIKit Is Constructed](../packages/photoaikit/)

Required update:

- Compare the article with the exact pinned package revision.
- Recheck product names, contract types, backend actors, artifact descriptors,
  storage APIs, fallback behavior, and segmentation workflows.
- Add a RawCull integration section mapping package protocols to
  `RawCullAIIntegration`, `SimilarityScoringModel`, semantic search, and Deep
  Review.
- Identify which behavior belongs to the package and which policy remains in
  RawCull.

### 9. PhotoAnalysisKit

Page: [How PhotoAnalysisKit Is Constructed](../packages/photoanalysiskit/)

Required update:

- Reconcile the package facade, analysis descriptors, presets, batch limits,
  calibration, focus evidence, and mask APIs with the pinned revision.
- Add call maps from RawCull's sharpness and focus models into the package.
- Link package tests for scalar scoring, cancellation, configuration identity,
  and mask rendering.

### 10. RawCullCore

Page: [How RawCullCore Is Constructed](../packages/rawcullcore/)

Required update:

- Verify domain models, `FileItem` typealias boundaries, burst grouping/ranking
  defaults, review states, and histogram behavior.
- Explain why pure `nonisolated` value logic belongs here while orchestration
  and persistence remain in the app.
- Add extension guidance for new grouping evidence and cache-version
  consequences.

### 11. RawParserKit

Page: [How RawParserKit Is Constructed](../packages/rawparserkit/)

Required update:

- Verify format registration, metadata normalization, thumbnail/preview
  strategies, coalescing, decode limits, and cancellation bridges.
- Map `RawParserKitImageLoader` to the package facade and show where
  non-Sendable images are consumed or converted.
- Include the current Sony and Nikon behavior without implying that app code
  should call vendor conformers directly.

### 12. Sony/Nikon MakerNote Parser

Page: [Sony/Nikon MakerNote Parser](../sonymakernoteparser/)

Required update:

- Reconcile parser type names and file locations with RawParserKit.
- Walk one Sony and one Nikon focus-location result through normalization into
  `FileItem` and focus UI.
- Document fallback to EXIF subject area and catalog-wide `focuspoints.json`
  behavior.
- Add a checklist and tests required when introducing another RAW format.

## P1 — Operational Correctness References

### 13. Security-Scoped URLs

Page: [Security-Scoped URLs](../security/)

Required update:

- Keep the already-current AI indexing and semantic-search scope explanation.
- Add the selected JPG export destination lifetime and app-termination
  persistence flush.
- Cross-check rsync bookmark fallback, idempotent cleanup, and exact ownership
  of every successful scope start.
- Add a table for catalog, scan, export, copy, diagnostics, and AI operations
  showing owner, start, stop, and failure cleanup.

### 14. Memory Pressure

Page: [Memory Pressure](../memorypressure/)

Required update:

- Recheck adaptive cache recommendations, user maxima, warning/critical
  responses, and recovery behavior.
- Connect pressure state to both grid and preview caches and to diagnostics
  counters.
- Explain the lock-backed synchronous read without teaching that every cache
  operation bypasses actor isolation.
- Add the tests and diagnostic measurements used to validate limit changes.

### 15. Synchronous Code

Page: [Synchronous Code](../heavy/)

Required update:

- Audit all current blocking ImageIO, filesystem, RAW parsing, JPEG encoding,
  and process operations.
- Distinguish short `@concurrent` work from operations intentionally moved to a
  detached task or dedicated GCD continuation bridge.
- Add decision rules for when a synchronous call is safe inside an actor and
  when it would occupy Swift's cooperative executor too long.
- Remove types or paths that no longer exist.

## P2 — AI Distribution, Evidence, And Release Procedures

### 16. AI Model Downloads

Page: [AI Model Download Service](../ai/aimodeldownloads/)

Required update:

- Reconcile the procedure with the current download catalog, downloader target,
  managed locations, activation callbacks, and release metadata tests.
- Separate runtime architecture from release-operator commands.
- Add failure/retry behavior and the user-visible capability states.

### 17. Publishing New AI Models

Page: [Publishing New RawCull AI Models](../ai/newmodels/)

Required update:

- Verify archive names, manifest schema, checksums, release tags, model
  identities, and staging paths against `ModelAssets` and current release tests.
- Replace any historical one-off commands with parameterized examples or clearly
  label them as records.
- Add a final reproducibility and licence gate before publishing.

### 18. AI Licence And Provenance Procedure

Page: [AI Model Licence and Provenance Clearance](../ai/licenceprocedure/)

Required update:

- Separate current legal/provenance status from the reusable clearance
  procedure.
- Verify notices, provenance JSON, upstream licences, acceptance requirements,
  and distribution restrictions for every shipped model.
- Add an evidence date and owner to decisions that can expire or change.
- Keep legal conclusions explicitly evidence-based and avoid inferring
  permission from model availability.

### 19. Evaluating CLIP Models

Page: [Evaluating CLIP Models](../ai/evaluateclipmodels/)

Required update:

- Verify package revisions, fixture identities, scripts, commands, thresholds,
  and report paths.
- Separate parity testing, semantic retrieval evaluation, performance
  measurement, and RawCull integration testing.
- Add a reproducibility checklist including hardware, OS, toolchain, model
  fingerprint, and immutable fixture digest.

### 20. CLIP Evaluation Results

Page: [CLIP Model Evaluation Results](../ai/evaluation/)

Required update:

- Treat this as a dated evidence report rather than timeless architecture.
- Record exact inputs, model fingerprints, query set, metrics, hardware, and
  report generation date.
- Link conclusions to generated artifacts and clearly distinguish measured
  results from recommendations.
- Add a superseded-results policy so later evaluations do not silently overwrite
  historical evidence.

## P3 — Stable Workflow Guidance

### 21. Repository Git Workflow

Page: [Repository Git Workflow](../pushpull/)

Required update:

- Confirm that the documented rebase and fast-forward policy still matches
  repository practice.
- Add the documentation validation commands: Prettier, Hugo build, and
  internal-link check.
- Remove duplicated Git basics if the page is intended only for this
  repository's policy.
- Review when branch protection, deployment, or contribution rules change.

## Proposed New Pages

These pages should be added only after the existing P0 and P1 articles are
accurate.

| Priority | Proposed page            | Purpose                                                                                                                                |
| -------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| P1       | `swiftuiarchitecture.md` | Main window modes, `NavigationSplitView` composition, environment injection, sheets, overlays, commands, and reusable inspection views |
| P1       | `persistence.md`         | `CullingModel`, saved-file schema, backup/corruption recovery, debounced writes, flush-on-termination, and migration rules             |
| P2       | `testing.md`             | Test plans, smoke/performance manifests, package tests, isolation helpers, fixtures, and how tests encode architecture invariants      |
| P2       | `diagnostics.md`         | Memory, similarity, contention, and RAW diagnostics; log locations, privacy boundaries, and troubleshooting workflow                   |

## Standard Required For Every Update

Every revised architecture article should contain:

1. **Purpose and boundary** — what the subsystem owns and deliberately does not
   own.
2. **Source map** — exact repository-relative files and package revision where
   relevant.
3. **Read order** — the shortest path through the code for a new contributor.
4. **End-to-end flow** — trigger, main-actor orchestration, background owner,
   persistence, and UI publication.
5. **State and lifetime** — actor ownership, cancellation, generation guards,
   security scopes, and cleanup.
6. **Failure behavior** — what the user sees and what remains recoverable.
7. **Cache or persistence identity** — descriptors, fingerprints, versions, and
   invalidation rules.
8. **Tests** — executable evidence for important invariants.
9. **Change checklist** — related files, versions, docs, and tests to update
   together.
10. **Last reviewed date** — the date the article was checked against source,
    not merely reformatted.

Avoid absolute developer-machine paths, undocumented source snapshots,
unverified constants, and claims that `await` automatically moves work to a
background thread.

## Review Triggers

Update the relevant article in the same change whenever any of these occur:

- a source file is renamed or ownership moves between view, model, actor, and
  package;
- a package revision changes a public contract or default;
- a cache key, schema, descriptor, algorithm version, or persistence format
  changes;
- a new task, actor, continuation, security scope, or cancellation path is
  introduced;
- a new model backend, RAW format, view mode, export mode, or diagnostics store
  is added;
- tests establish a new invariant that the current article does not explain.

After each documentation batch, run the configured formatter, render the
complete Hugo site, validate internal links, and check the diff for stale
filenames and obsolete constants.
