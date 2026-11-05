+++
author = "Thomas Evensen"
title = "P0: Unified Burst Evidence"
linkTitle = "P0: Unified Burst Evidence"
date = "2026-11-05"
lastmod = "2026-11-05"
description = "Functional scope and implementation plan for comparable subject crops and inspectable burst decisions."
tags = ["roadmap", "planning", "culling"]
categories = ["technical details"]
weight = 30
+++

# P0: Unified Burst Evidence and Comparable Subject Crops

**Status:** proposed plan, not a released feature. **Priority:** second P0.
**Outcome:** a photographer can compare the intended subject across a difficult
burst, inspect what was measured, understand uncertainty and retain a preferred
frame even when its technical score is lower.

This plan expands the [feature overview]({{< relref "newfeatures.md" >}}).
RawCull already has burst ranking, manual review decisions, AF information,
sharpness evidence, subject segmentation and bounded Combined Review. The work
here unifies those capabilities into a dependable comparison workflow; it does
not presume that every frame has every kind of evidence.

## 1. Scope and product boundaries

The first delivery focuses on wildlife and sports bursts already grouped by
RawCull. A photographer chooses a group, compares a small working set, confirms
the intended subject, and records a decision. Ordinary burst review remains
usable without downloading optional models or running a VLM.

| Included | Deferred |
| --- | --- |
| Common evidence presentation for candidate frames | Whole-catalog autonomous culling |
| Subject-centered crops with explicit scale and source | Automatic anatomical eye-quality claims |
| Manual correction of intended subject and comparison region | Face identity recognition or persistent subject tracking across a shoot |
| Clear separation of AF location, measured detail and observations | One universal photographic quality score |
| Reasons for unavailable or incomparable evidence | Automatic rejection based on a weak measurement |
| Optional escalation into existing 1–8-image Combined Review | Running Combined Review over every image by default |
| Manual winner protection and review/defer continuity | Replacement of burst grouping or a new RAW editor |

An AF point records camera information, a mask identifies image pixels, and a
detail score measures a particular render and region. None alone proves that
an eye is sharp or that a frame is artistically preferable. The interface must
preserve these distinctions in its labels and explanations.

## 2. Worked example: a bird against a sharp background

A burst has 18 frames. The current ranking places a frame with a crisp branch
near the top, while the photographer cares about a moving bird. Opening the
burst presents the full frame, a candidate strip, a pinned reference and a
subject comparison area. The initial working set contains the current candidate,
reference and nearby alternatives; the remaining frames remain accessible.

The photographer clicks the bird in the reference. If segmentation has found
multiple subjects, RawCull shows the selectable masks and highlights the chosen
one. If no suitable mask exists, the photographer draws a rectangular inspection
region. A rectangle is labeled **Manual region**, never a segmentation result.

RawCull proposes matching regions in the other frames. The photographer sees
the region on each full-frame thumbnail and corrects the one that accidentally
selected a branch. Uncertain matches are marked **Confirm subject**; those
frames cannot receive a confident subject-based recommendation until confirmed.
A proposed match is not permission to silently reuse the same coordinates when
the bird has moved.

The comparison shows crops at a shared display scale, source information and
per-frame evidence. For one frame it might say: “Recorded AF region overlaps
the selected subject; subject detail available.” For another: “Recorded AF
region falls outside the selected region; subject detail unavailable.” It must
not convert this into “focus missed” without valid subject detail evidence.

The photographer switches to source-pixel inspection and notices that a
slightly lower-detail frame has the best wing position. They mark it as the
manual winner. Later measurements may update the technical suggestion, but the
manual winner remains unchanged. The comparison explains the difference:
**Your winner** and **Technical suggestion** are separate states.

If two frames remain difficult to distinguish, the photographer sends that
shortlist to Combined Review. Its observations appear as an optional, attributed
report linked to the run and selected inputs. The photographer can defer the
group, retain multiple alternatives or return to ordinary review at any point.

## 3. Workspace and interaction rules

The proposed workspace has a full-frame stage, filmstrip and evidence inspector.
Start with two simultaneous crops and allow up to four if the layout remains
readable; finalize this limit through usability measurement. Larger bursts use
the filmstrip rather than shrinking all crops into unreadable tiles.

Pinning a reference keeps it stable while advancing the candidate. Navigation
must preserve per-frame subject choices and group decisions. Keep existing
keyboard commands where possible and expose all controls to keyboard navigation
and accessibility. A rating action changes the intended frame, even if another
frame's asynchronous evidence finishes at the same time.

The inspector presents the same rows for every compared frame:

| Evidence | What the photographer sees |
| --- | --- |
| Source | Embedded preview or developed RAW; dimensions and crop scale |
| Intended subject | Mask/manual region, selection origin and confirmation state |
| Subject detail | Value, metric identity and region used, or reason unavailable |
| AF evidence | Recorded region/point and supported availability state |
| Whole-frame detail | Separate context, explicitly distinct from subject detail |
| Recommendation | Reasons, excluded evidence and uncertainty |
| Optional generated observations | Model/run attribution, inspectable source and limitations |
| Decision | Manual winner, rating and review/defer state |

Do not fill missing evidence with zero. Use specific states such as **Not
analyzed**, **Model unavailable**, **Subject not confirmed**, **Unsupported AF
metadata**, **Source changed**, **Analysis failed** and **Not comparable**. Only
transient work displays progress. Error and unavailable states offer an
appropriate action, such as retry, select region or inspect manually.

### 3.1 Close-ups concepts for further study

The following sketches were discussed on 2026-11-05 using the supplied RawCull
review screenshots. They are **AI-generated design references, not implemented
UI or acceptance-ready specifications**. Enlarged details are illustrative,
including the alternative frame in the burst sketch; they are not extracted
full-resolution RAW crops and must not be used to judge photographic sharpness.
The built-in image generation tool produced both sketches.

The proposed home is a **collapsible Close-ups panel inside the existing review
screen**, beside the full photograph and above the existing filmstrip. Burst
review is the primary P0 workflow. The same inspection component could also
serve single-image review, without implying that unrelated single images form
a burst or are automatically comparable. Narrative's context-and-detail layout
is the reference; study the interaction carefully before committing the layout.

![Burst review concept showing the full photograph, current and pinned close-ups, and filmstrip.](/images/newfeatures/burst-close-ups-concept.png)

**Sketch A — Burst review.** Keep the whole composition visible while comparing
two subject crops: **Current** and **Reference**. The filmstrip remains available
for navigation and ratings. The drawn panel uses **Pinned** for the reference;
final terminology should be consistent. Add explicit **Pin reference** and
**Replace reference** controls: these are missing from the sketch. Pinning a
reference must remain distinct from marking a frame as the photographer's winner.

![Single-image review concept showing the full photograph and one selected-region close-up.](/images/newfeatures/single-image-close-ups-concept.png)

**Sketch B — Single-image review.** The second supplied screenshot is labeled
**Single Images**. Show one larger inspection crop here, with **Choose region**
and **Reset**. Keep the same panel location and crop controls as burst review;
a pinned comparison is not required for this basic inspection state.

### 3.2 Proposed framing and comparison interactions

These interaction notes are proposals for study, not claims about current
automatic detection or tracking:

1. **Propose a region.** Start from an available subject mask or region. A head
   crop is useful for these deer only when suitable head-region evidence exists;
   otherwise use subject bounds or ask for a manual region. Do not silently
   label a general subject crop as a detected head or eye.
2. **Let the photographer correct it.** Clicking a detail centers the inspection
   region there; dragging a rectangle defines its bounds. Allow moving and
   resizing the region. Show the corresponding blue rectangle on the full
   photograph. Manual regions remain labeled as manual selections.
3. **Pin a reference.** Open a frame and select **Pin reference** on its crop
   card. Then select another frame in the filmstrip to populate **Current**.
   Advancing the candidate leaves the reference fixed. **Replace reference**
   deliberately changes it; unpinning returns to a single-crop inspection state.
4. **Match the intended subject.** Propose the corresponding region in each
   candidate, but expose uncertainty and allow correction by clicking the
   correct subject. Reusing the same image coordinates is insufficient when
   the animal moves. Automatic cross-frame matching needs separate validation.
5. **Make selection unambiguous.** Give both cards filenames and clear
   **Current / Reference** labels, with matching filmstrip highlights. Clicking
   a crop makes that frame active for rating; distinguish the active target
   from the pinned-reference state. Keyboard focus and asynchronous updates
   must not redirect a rating to another frame.
6. **Keep scale explicit.** Offer **Fit subject** for pose inspection and
   **Source pixels** for detail at a consistent source-pixel-to-screen-point
   ratio. Link pan/zoom around each region's local anchor, with unlink/reset.
   Begin with two crops; study up to four only if they remain readable.

Study panel width, visibility of the full composition, region editing, pinning
discoverability, active-frame feedback, keyboard operation and smaller windows.
Verify that the controls above can be used without repeatedly opening another
screen. Do not reproduce generated text, altered photo details or incidental
spacing from these sketches as implementation requirements.

### 3.3 Existing human-subject support and its limits

Local source inspection on 2026-11-05 confirms coarse human-subject support:
`RawCullSemanticSearchModel.classifySubjects` compares existing CLIP artifacts
against six prompts, including **a photo of a person**, and assigns the
highest-scoring label. This is relative classification, not calibrated proof
that a person is present, a count of people, or a localized face detection.
When the required model/runtime is available, Deep Review's SAM prompt selection
for person/people/human/face labels tries **face → person → subject**. The
segmentation contract supports both person and face prompts.

This provides an existing route toward human or face inspection regions, but
is not evidence of named-person recognition, reliable enumeration of every face,
eye landmarks, blink detection or eye-sharpness assessment. A usable mask from a
face prompt does not prove verified facial anatomy. Those capabilities must be
verified or scoped separately before promising Narrative-style face assessments.
See [Deep Analysis: SAM 3 and CLIP]({{< relref "../ai/aiinrawcull.md" >}})
for the documented pipeline and fallback behavior.

Source checkpoints for later study:

- `RawCull/Intelligence/SemanticSearch/RawCullSemanticSearchModel.swift`,
  `classifySubjects(in:)`.
- `RawCull/Intelligence/DeepReview/DeepAIReviewFeature.swift`,
  prompt selection and requested-prompt/fallback handling.
- `PhotoAIKit/Sources/PhotoAIContracts/SubjectSegmentation.swift`,
  `SubjectSegmentationPrompt`.

## 4. Crop and comparison semantics

Provide two explicitly named modes:

- **Fit subject:** center each selected region in a common viewport with a
  consistent padding policy. This helps compare gesture and composition, but
  different magnification must be shown and must not imply equivalent detail.
- **Source pixels:** use the same source-pixel-to-screen-point ratio across
  crops, expose that ratio and account for display backing scale. This supports
  detail inspection; a smaller subject stays smaller rather than being enlarged
  to look equivalent.

Pan and zoom are linked around each selected region's local anchor. They are
not a claim of optical registration across moving subjects. Offer unlink/reset
controls. Preserve enough surrounding context to detect an incorrect subject
match. Do not use a tightly clipped mask as the only view of the photograph.

Define image orientation once and carry transforms from source pixels through
normalized regions, preview/developed render, mask coordinates, crop and view.
Test rotation, mirroring, portrait frames, edge-clipped subjects and mismatched
render aspect ratios. Apply the same transforms to AF overlays and subject
outlines. A region outside valid rendered bounds produces an explicit failure.

Comparability is a computed property with reasons. Measurements must use a
compatible metric version, preprocessing, source class, region policy and
sampling scale. Normalizing two scores to percentages does not make them
comparable. If one frame uses a small embedded preview and another a developed
RAW, offer a consistent-source recomputation where possible; otherwise show
both crops with a warning and withhold the numerical comparison.

A user may inspect any chosen subregion, including a visible eye, but it remains
an inspection region. Dedicated eye detection or blink assessment is outside
this P0. General model prose must not appear as a measured eye-quality result.

## 5. Recommendation and manual control

Keep the existing ranking available as context. Introduce evidence eligibility
before changing ranking logic: identify the confirmed subject, establish source
compatibility, validate measurements, then make a bounded technical suggestion.
List the main reasons and missing evidence. If the intended subject is uncertain,
results conflict or values are too close under the qualified policy, abstain.

Do not add incomparable evidence into a new weighted total merely to populate a
badge. Calibrate any thresholds on representative labeled bursts and version
the policy. Where comparative confidence has not been calibrated, describe
availability and ambiguity without presenting an invented probability.

Manual winners, stars and deferrals are durable domain decisions. Reanalysis,
provider replacement, viewport recreation and cache hydration must not reset
them. Distinguish a refreshed suggestion from a deliberate user action. Support
undo for changing the winner or subject; selecting a new subject invalidates
only dependent evidence and recommendations, not the photographer's decision.

## 6. Existing integration points and proposed contracts

At pickup, inspect these current application files before choosing ownership:

- `RawCull/Views/ComparisonGridView/BurstCullingWorkspaceView.swift`,
  `BurstImageStage.swift`, `BurstEvidenceShelf.swift` and
  `BurstComparisonEvidenceView.swift` for workspace presentation.
- `RawCull/Model/ViewModels/BurstReviewSessionModel.swift` and
  `BurstWorkspaceSessionModel.swift` for durable versus viewport state.
- `RawCull/Model/Handlers/BurstWorkspaceImageCoordinator.swift` and the
  frame cache policy/key types for image requests and cache limits.
- `RawCull/Intelligence/BurstAnalysis/` for existing measurements, ranking,
  cache compatibility and analysis lifecycle.
- `RawCull/Intelligence/CombinedReview/CombinedReviewFeature.swift` for
  explicit shortlist escalation and run provenance.

Proposed value contracts, with final names decided during implementation:

| Contract | Minimum content |
| --- | --- |
| Frame evidence snapshot | Stable frame ID, source fingerprint, render descriptor, evidence revisions and availability reasons |
| Subject selection | Frame ID, normalized region/mask reference, origin, revision and user confirmation |
| Crop request | Source identity, orientation transform, region, padding, scale mode and output bounds |
| Comparability result | Eligible metrics, incompatible pairs and human-readable reasons |
| Comparison session | Group ID, pinned reference, candidates, mode and current request generation |
| Recommendation | Policy version, candidate IDs, supporting evidence revisions, reasons and abstention state |

Keep these as inspectable values rather than embedding model runtime objects in
views. The existing durable review owner remains authoritative for manual
decisions. The workspace consumes projections and issues explicit intents;
it must not become a second decision store. Persist subject choices separately
if they should survive reopening, with schema migration and source invalidation.
Derived crops can be evicted; durable choices cannot depend on cache survival.

## 7. Work scheduling and stale-result protection

Load visible previews first, then visible crops and already available evidence.
Schedule optional measurements only for the working set or an explicit user
request. Use bounded background work and a measured memory budget; avoid one
full-resolution decoded image per frame in a large burst. Cache keys include
source fingerprint, render descriptor, orientation, region revision, algorithm
version and crop parameters that affect output.

Changing group, subject, source or provider increments a request generation.
Cancel obsolete work and validate identity and generation before publishing
results. Cancellation alone is insufficient because a completed callback may
already be queued. A stale result may enter a correctly keyed reusable cache,
but cannot replace the evidence currently displayed for another selection.

Memory pressure releases derived crops and inactive decoded images. Navigating
back reconstructs them from source and saved choices. Missing models retain
preview/manual-region inspection. A failed developed render can fall back to
an embedded preview with explicit source and comparability changes, never an
invisible source substitution under an unchanged score.

## 8. Implementation sequence

1. **Trace and fixtures.** Record existing ownership, source transforms and
   ranking semantics. Build a fixture set including wrong-subject masks,
   unsupported AF, tiny previews, moving subjects and intentional motion blur.
2. **Evidence projection.** Introduce a unified snapshot and availability states;
   show existing evidence without changing ranking. Verify durable decision
   protection and correct source attribution.
3. **Comparable crops.** Add reference/candidate layout, explicit scale modes,
   region overlays and manual correction. Prove coordinate transforms and
   bounded memory before integrating more inference.
4. **Subject evidence.** Connect confirmed masks/regions, versioned measurement
   provenance and comparability gating. Add cancellation and stale-result checks.
5. **Explanations and escalation.** Add a conservative technical suggestion,
   abstention, inspectable reasons and explicit Combined Review handoff. Returned
   reports reference frozen inputs and are marked outdated after subject changes.
6. **Photographer qualification.** Compare the current workflow with the new
   workspace on the same difficult bursts and revise the UI/policy from results.

Each stage should leave a usable manual review path. The first P0's XMP service
is independent: this feature supplies explicit decisions to normal persistence,
not direct sidecar writes from a view.

## 9. Acceptance and evidence required for release

Functional acceptance includes a complete bird/background example, a sports
sequence with subject movement, multiple similar subjects, failed segmentation,
unsupported AF, mixed render sources, cancelled analysis and source replacement.
For each, inspect whether the shown region actually belongs to the intended
subject and whether every numerical comparison meets the declared policy.

Exercise frame/group navigation while analysis completes out of order. Verify
that no stale result changes the active frame, manual winner or subject choice.
Verify winner persistence across reopening and reanalysis. Check crop alignment
with known pixel landmarks, including orientation and display-scale cases.

Compare old and new workflows with photographers using acceptable alternatives,
not a forced single ground-truth winner. Measure time to a confident decision,
zoom/pan actions, subject corrections, missed acceptable frames, overrides and
abstentions. Record dataset, hardware, model versions and render settings.
Measure first crop latency, navigation tail latency, cancellation recovery and
peak memory separately for cold and warm runs. Set numerical budgets after the
baseline measurement, before final qualification.

Release requires faster difficult-burst review with equal or fewer missed
keepers in the agreed evaluation, correct provenance and no lost manual
decisions. A structurally valid model report is insufficient evidence of visual
accuracy. If recommendation quality fails qualification, retain manual crop and
evidence inspection while revising or withholding the recommendation policy.

## 10. Reference applications and workflow patterns

The following applications provide useful references for parts of this workflow.
These observations are based on their published documentation, reviewed on
2026-11-05, rather than a hands-on comparative evaluation. They are complementary
design references, not evidence that any one application implements this entire
P0.

| Application | Documented workflow | What to study for RawCull |
| --- | --- | --- |
| [Narrative Select](https://narrative.so/select) | Close-ups keeps enlarged faces or details beside the full photograph, with separate eye/expression and focus indicators. On Macs running macOS 14 or later, it can show a non-face **Key Element**, falling back to the image center when none is found. | Full-frame context alongside subject detail, distinct evidence indicators, and clear handling of missing detections. |
| [Aftershoot](https://aftershoot.com/) | Survey Mode compares duplicate groups side by side with synchronized zoom. Loupe View combines Key Faces, duplicate alternatives and image scores with hover explanations. | Efficient burst navigation, comparison of alternatives, and explanations close to the evidence being reviewed. |
| [FastRawViewer](https://www.fastrawviewer.com/) | Two- or four-image comparison supports synchronized zoom/pan and inspection modes, including focus peaking. | Manual technical comparison, linked inspection controls and direct examination of RAW detail. |

Supporting documentation and examples:

- Narrative: [Zoom and Close-ups](https://help.narrative.so/en/articles/7337371-zoom-and-close-ups-in-narrative)
  explains full-photo context, subject details, platform limitations and missing
  detections. Its [Quickstart tutorial](https://narrative.so/select/lessons/quickstart-guide)
  describes assessments as relative guidance between images in a scene rather
  than an objective rating of a single image. This is a useful precedent for
  RawCull's bounded technical suggestions.
- Aftershoot: [Grid, Loupe and Survey Mode](https://support.aftershoot.com/en/articles/9189985-using-grid-loupe-and-survey-mode-views)
  documents duplicate comparison, Key Faces, image-score explanations and
  synchronized zoom. Synchronizing the same image location is a useful
  interaction reference, but does not establish that a moving subject has been
  matched across frames.
- FastRawViewer: [Multi-window guide, pages 3–12](https://updates.fastrawviewer.com/data/pdf/About_FastRawViewer_2-0.pdf)
  documents the comparison layout and synchronization controls. Use it as a
  reference for manual inspection, without treating focus peaking alone as proof
  that the intended subject is sharp.

Narrative is the first reference to study for the context-and-detail layout,
Aftershoot for group review, and FastRawViewer for technical inspection. RawCull's
proposed combination additionally makes confirmed wildlife subjects, crop-source
provenance, measurement comparability, unavailable evidence and protected manual
winners explicit. The documentation reviewed here does not establish that any
one of these applications provides that complete combination; this is a design
opportunity to validate, not a claim of unique market coverage.

## 11. Open decisions and revision record

Resolve the simultaneous-crop limit, default source policy, region persistence,
manual region scoring method, subject matching strategy, score eligibility,
abstention thresholds and memory/latency budgets. Track each with an owner,
date, rationale, fixture or experiment and effect on scope. Prototype subject
matching separately: a robust manual correction path must precede any promise
of automatic tracking.

For later pickup, begin with the source ownership trace and fixtures, then revise
this document with confirmed contracts and stage acceptance results. The related
[XMP plan]({{< relref "xmp-editor-handoff.md" >}}) defines how the resulting
photographer decisions eventually reach an editor.


## 12. Modular implementation blueprint

### 12.1 Evaluation and ownership

**Recommendation:** implement Close-ups and unified evidence as a self-contained
feature comprising a view, presentation model, value contracts and injected
workers. Self-contained means a small integration surface, not a single large
class owning decoding, inference, persistence and review decisions. Burst review
embeds the feature; single-image review can supply the same contract with one
frame and comparison disabled.

Source inspection on 2026-11-05 found useful existing boundaries:
`BurstWorkspaceSessionModel` owns viewport/image-cache state;
`BurstReviewSessionModel` owns application-lifetime review state;
`ImageReviewFeatureDependencies.swift` already separates selection, rating reads
and rating actions through narrow protocols. Build on that direction. The
current manual-winner method changes `recommendedFileID`; the adapter must expose
manual choice and technical suggestion separately. Do not invent a second
technical suggestion from an already overridden result: retain/recompute an
independent analysis projection as part of that integration change.

### 12.2 Module layout and dependency direction

Start with explicit feature folders/targets; extract Swift packages when the
contracts stabilize. Enforce the same dependency rules from the first slice.
Suggested names below are architectural proposals, not existing APIs.

| Boundary | Owns | Must not depend on |
| --- | --- | --- |
| `EvidenceContracts` | IDs, source descriptors, regions, snapshots, requests, outcomes and intents | SwiftUI, AppKit images, RawCullViewModel, inference runtimes |
| `EvidenceEngine` | Geometry, comparability, recommendation policy and bounded crop scheduling | App views, JSON decision storage, concrete model providers |
| `EvidenceUI` | `BurstEvidencePanel`, `BurstEvidenceModel`, crop cards, local interaction state | RawCullViewModel, catalog storage, global model managers |
| RawCull integration adapters | FileItem mapping, source access, existing analysis/image services, decision commands and persistence | Internal panel layout or worker implementation details |

Dependencies flow UI → contracts and engine interfaces; engine → contracts;
application composition → all required implementations. Keep geometry and
eligibility policy as pure functions. Workers use explicit concurrency isolation;
the presentation model is main-actor isolated. Render handles remain confined to
the rendering adapter rather than crossing the value-only contracts as NSImage.
Avoid exporting all these types through a general-purpose core package simply
to make imports convenient.

### 12.3 Required host data contract

The host supplies an immutable `EvidenceContext` and revisioned updates. It does
not hand over the entire catalog or view model.

| Value | Required fields and invariants |
| --- | --- |
| Context | Session ID, optional stable group identity, ordered frame summaries, current frame ID, context revision and capabilities; current/reference IDs must belong to this context |
| Frame summary | Stable source identity, current-session FileItem ID mapping, display name, source revision and read-only photographer decision projection |
| Render descriptor | Source fingerprint/class, dimensions, orientation, coordinate transform, development/preprocessing revision and available resolution; no implicit source fallback |
| Evidence snapshot | Frame/source/region revisions, typed availability per evidence item, metric identity/version/units, sampling policy and provenance |
| Region selection | Frame identity, normalized oriented-image bounds, optional mask artifact reference, origin, revision and confirmation; reject non-finite or invalid bounds |
| Decision projection | Manual winner, stars and review/defer state, each with authoritative revision; separate technical recommendation |
| Capabilities | Available source classes, manual-region editing, subject proposals, scoring and Combined Review availability, with disabled reasons |

Normalized coordinates use one documented oriented-image convention: origin,
axis directions and edge inclusion are fixed in the contract. Conversion from
camera/mask/render coordinates happens through explicit transforms. Session-only
UUIDs and integer group IDs are insufficient persistence keys: resolve durable
identity in the application adapter, including regrouping/moved-file behavior.

Represent evidence as `notRequested`, `loading`, `available(value, provenance)`,
`unavailable(reason)`, `failed(retryInformation)` or `stale(previousRevision)`.
Comparability is a separate policy result, not inferred from presence of scores.
A mask reference identifies a versioned artifact, not a model instance or an
unbounded pixel buffer in every snapshot.

### 12.4 Service and action contracts

Inject only services used by the current delivery slice:

- `EvidenceProviding`: load/observe evidence for explicit frame/source/region
  revisions; return typed results carrying the same identities.
- `CropRendering`: accept a crop request with region, transform, scale, target
  pixel bounds and generation; return a bounded render handle plus actual source
  and scale information. Reject unsupported requests explicitly.
- `SubjectRegionProposing`: optional proposals with origin, uncertainty and
  confirmation requirements. Absence leaves manual inspection usable.
- `SubjectSelectionStoring`: load and commit durable subject choices with expected
  revision; storage schema and migrations belong to the host adapter.
- `EvidenceActionHandling`: accept typed intents with explicit target IDs and
  expected context/decision revisions; return applied, rejected or conflict.

Intents include activate frame, commit subject region, set manual winner, rate,
defer, retry evidence and request Combined Review for an explicit shortlist.
Local pin/unpin, panel collapse and linked pan/zoom stay in the panel model.
When activation changes the rating target, await host acknowledgement and render
the returned authoritative selection. A rating command captures its frame ID
when invoked; asynchronous evidence cannot retarget it. Failed durable commands
remain visible and do not appear successfully saved.

The host constructs one model per review session, passes it to the panel and
feeds authoritative context updates back. The panel emits intents through the
injected handler; there is no bidirectional binding to arbitrary host internals.
Closing/collapsing the panel cancels unnecessary work and releases render leases;
reopening restores choices through the adapter. Define whether temporary pin and
viewport state survive collapse separately from durable subject persistence.

### 12.5 Incremental implementation and integration gates

1. **Contracts and ownership audit.** Map the existing source/image/rating paths;
   document durable identity and orientation. Add representative value fixtures.
   Gate: a fake host can supply all required inputs without RawCullViewModel.
2. **Read-only panel.** Implement a model and view showing existing snapshots and
   unavailable reasons. Integrate through a small `BurstEvidenceAdapter` at the
   workspace composition boundary. Gate: opening/closing changes no decisions
   and does not start optional inference.
3. **Manual crops.** Implement one-frame inspection, then current/reference,
   explicit scale and linked viewport transforms. Reuse existing image services
   through adapters and one bounded cache policy rather than double-caching full
   frames. Gate: orientation fixtures, memory limits and rapid-navigation stale
   results pass; single-image integration needs no burst-specific model.
4. **Subject persistence and evidence eligibility.** Add revisioned region
   commits, invalidation, comparability and independent technical suggestions.
   Gate: manual winners survive reload/reanalysis and rejected commands stay
   recoverable; region changes invalidate only dependent results.
5. **Optional providers and escalation.** Add subject proposal/scoring adapters
   and bounded Combined Review. Gate: removing optional providers still leaves
   the manual feature fully usable; uncertain matching requires confirmation.
6. **Extraction and cleanup.** Move stable contracts/engine/UI into targets or
   packages, remove duplicate evidence presentation after parity, and document
   the small host setup API. Gate: compile/test with a fixture host and no app
   view-model import. Existing ordinary review remains a usable fallback.

Use focused geometry/eligibility tests, adapter identity and decision tests,
worker cancellation/race tests, and UI checks for pinning, active rating target,
keyboard use and narrow windows. Acceptance from sections 8–9 still applies.
Record numeric memory/latency budgets before stage 3 is accepted. Changing a
provider, storage implementation or panel layout must not require changes across
all four boundaries; demonstrate that with a fake provider and storage adapter.
