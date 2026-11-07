+++
author = "Thomas Evensen"
title = "P0: Unified Burst Evidence"
linkTitle = "P0: Unified Burst Evidence"
date = "2026-11-05"
lastmod = "2026-11-07"
description = "Implemented Close-ups, remaining evidence integration, and possible next features for RawCull burst review."
tags = ["roadmap", "planning", "culling"]
categories = ["technical details"]
weight = 30
+++

# Unified Burst Evidence: Current State and Next Features

**Manual Close-ups is complete.** RawCull imports the tested
[PhotoEvidenceKit](https://github.com/rsyncOSX/PhotoEvidenceKit) package from
GitHub. The current project and lockfile pin **1.0.5**, revision
`59554c504eb0eb8ea4452471475bb9ff13557d79`. Package development and required testing
are complete; importing the package, building the manual panel and qualifying
its shared inspection behavior are no longer roadmap tasks.

The remaining opportunity is to connect RawCull's existing analysis to this
inspection workflow. This page distinguishes that missing integration from
optional new features. See the [feature overview]({{< relref "newfeatures.md" >}})
for the broader roadmap and [XMP handoff plan]({{< relref "xmp-editor-handoff.md" >}})
for editor interoperability.

## Implemented in RawCull

| Capability | Current behavior |
| --- | --- |
| Burst workspace | A Close-ups button shows a right-side panel beside the main photograph and filmstrip. It is available for burst groups, not the single-images group. |
| Comparison selection | Command-click toggles frames; Shift-click selects a range in displayed order; Command-Shift-click adds a range. Filmstrip controls also toggle inclusion. With no explicit selection, Close-ups uses the current frame. |
| Manual regions | Each frame has its own region center and size. The overview supports click/drag placement; region-size controls and reset are available. |
| Inspection scale | Fit region and Source pixels modes, zoom, crop panning with drag or focused arrow keys, and view reset are implemented. Fit-region magnification can differ between frames. |
| Linked inspection | Pan/zoom can be linked around each frame's own region. Linking does not identify or track the same subject across frames. |
| Retained reference | A frame can be pinned, replaced or unpinned independently of current selection. Group changes create a new inspection session. Pinning is separate from declaring a burst winner. |
| AF placement | Use AF point centers a region on valid recorded camera AF metadata, transformed for image orientation. Missing or invalid metadata has an explanation. |
| Image sources | The host supplies full-size preview or developed-RAW output. Cards show the actual source label and decoded dimensions. Preview labels distinguish sidecar JPG from embedded preview; developed output is a full-size JPEG, labeled RAW 9 where supported. |
| Region persistence | Versioned region records are saved in UserDefaults under standardized URL identity and checked against file revisions. New sessions restore valid records; replaced files invalidate them. A moved file has a different URL identity. |
| Rendering lifecycle | The renderer retains catalog access, serializes native decoding, checks file/source revisions before and after loading, and produces bounded raster artifacts. The package rejects obsolete results and releases card imagery on disappearance. |
| Navigation | Show image activates the selected file and opens RawCull's zoom overlay with burst navigation and the selected source. |
| Review decisions | RawCull already owns ratings, manual winners, recommendations and review/defer state. Inspection regions and pinned references do not replace these decision stores. |

PhotoEvidenceKit supplies `PhotoEvidenceContracts`, `PhotoEvidenceEngine` and
`PhotoEvidenceUI`. RawCull supplies file identity, permissions, source loading,
AF metadata, persistence and workspace activation. RAW decoding and durable
culling decisions remain host responsibilities.

Source identity is distinct from render identity: a sidecar preview can change
without changing the RAW file revision. The current developed-RAW descriptor
uses RawCull's default full-size JPEG pipeline; it does not establish a
persistent per-image editing workflow or a sensor-domain RAW measurement.

## What is still missing from unified evidence

These are integration gaps in the Close-ups workflow, not missing manual crop
controls or a request to recreate analyses that already exist elsewhere.

| Area | Already in code | Missing integration | Completion criterion |
| --- | --- | --- | --- |
| Evidence beside crops | RawCull has AF-region, whole-frame and subject-detail measurements; Close-ups accepts AF placement metadata. | Project the relevant measurements into each card with their measured region, source, algorithm/settings revision and availability. The current panel has no scored-evidence input. | The photographer can see which pixels and render produced each value, and distinguish missing, loading, failed and stale evidence. |
| Intended subject | Manual regions and Use AF point work. RawCull separately has SAM 3 segmentation and subject-mask scoring. | Offer a subject-derived region, let the photographer confirm or correct it, and associate that choice with the analysis. | A corrected subject invalidates dependent evidence; manual inspection remains usable without models. |
| Numerical comparability | Render descriptors and stale-render protection exist. | Define compatibility rules for metric version, preprocessing, source class, region and sampling. Matching render identities alone does not establish comparable sharpness scores. | Incompatible or stale values are withheld from numerical ranking and carry a reason; comparable values identify their basis. |
| Explanation of a burst suggestion | Burst ranking, a recommended frame and manual winner selection already exist. | Explain a suggestion through the inspected subject and eligible measurements, with uncertainty and abstention when evidence is insufficient. | A photographer can inspect the reason without losing an independent manual winner. A higher detail score is not presented as universal photographic merit. |
| Combined Review from Close-ups | RawCull already supports bounded 1–8-image Combined Review elsewhere. | Explicitly submit the chosen Close-ups shortlist with frozen source/region inputs and connect the resulting report to those inputs. | Reports identify inputs and model/run provenance; changes to those inputs mark a report stale or require an explicit rerun. |

A recorded AF point is camera metadata, not proof of sharp focus. A segmentation
mask identifies pixels, not eye state or photographic quality. Generated
observations must remain distinguishable from measured detail. Existing scores
should be reused where their provenance is sufficient; otherwise recompute or
show why the result cannot be used.

## Possible new features

These are candidates for later work, not prerequisites for the completed
Close-ups delivery or commitments to ship.

| Candidate | Added value beyond current code | Boundary |
| --- | --- | --- |
| Region editing on the main photograph | Draw or resize a region directly on the large burst image, with undo. | Overview placement and region-size controls already exist; the new work is stage interaction and undo ownership. |
| Cross-frame subject matching | Follow a moving bird, athlete or other intended subject without manually positioning every region. | Linked pan/zoom currently copies inspection state, not subject identity. Matching needs confidence, correction and a manual fallback. |
| Face and eye inspection | Provide dedicated face/eye crops and, if qualified, eye-state or eye-sharpness assessments for portraits and groups. | Neither a camera AF point nor Qwen commentary is a calibrated blink detector. Include unknown results for small or occluded faces. |
| Close-ups in single-image review | Make the same detail-inspection panel available outside a burst. | The current workspace deliberately gates the panel to burst groups. |
| Richer development-aware inspection | Support explicit per-file development settings and crop/straighten transforms in the host adapter if RawCull gains that workflow. | The package has render-source/coordinate contracts; RawCull currently supplies its default development pipeline, not a persistent editor. |

XMP exchange remains a separate adoption priority. Full RAW editing, whole-catalog
autonomous culling and automatic rejection are outside the scope of this page.

## Suggested next delivery

1. Add a revisioned evidence projection for the selected Close-ups frames, reusing
   RawCull's existing analysis owners. Start with AF and detail evidence; expose
   availability and source attribution before adding another score.
2. Add explicit compatibility rules and explanations. Test preview/developed
   source changes, region changes and delayed analysis publication so values
   cannot silently describe an earlier crop.
3. Add optional subject-region proposals and confirmation using existing
   segmentation. Keep manual correction and manual winner choice authoritative.
4. Connect explicit Combined Review escalation only after the shortlist's inputs
   and report staleness can be represented reliably.

Validate each new integration where it changes behavior. For evidence, test
revision invalidation and incompatible measurements. For subject proposals, use
moving subjects and sharp backgrounds. For recommendations, measure missed
keepers and agreement with photographers' acceptable alternatives. These are
checks for new functionality, not unfinished qualification of the delivered
package.

## Implementation references

RawCull source baseline: commit
[`8b07828`](https://github.com/rsyncOSX/RawCull/tree/8b07828530dc85d74b003900784531e6c88df4aa),
with dependency configuration checked in the current checkout on 7 November 2026.

- `RawCull/Views/ComparisonGridView/BurstCullingWorkspaceView.swift`: host model,
  visibility, comparison selection, group lifecycle and zoom activation.
- `RawCull/Views/ComparisonGridView/BurstWorkspaceFilmstrip.swift`: comparison
  selection and existing review indicators.
- `RawCull/Views/ComparisonGridView/BurstCloseUpsView.swift`: frame/source
  adapters, renderer, AF orientation and preference storage.
- `RawCullTests/BurstCloseUpTests.swift`: AF orientation and invalid metadata,
  selection ranges, region restoration and file/sidecar revision identity.
- `RawCull.xcodeproj/project.pbxproj` and the workspace `Package.resolved`:
  remote PhotoEvidenceKit dependency and resolved version.

This update records the completed package testing and inspected integration;
it does not claim a new test run or a newly published application release.
