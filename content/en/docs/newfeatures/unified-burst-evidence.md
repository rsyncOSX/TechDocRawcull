+++
author = "Thomas Evensen"
title = "P0: Unified Burst Evidence"
linkTitle = "P0: Unified Burst Evidence"
date = "2026-11-05"
lastmod = "2026-11-06"
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


## 13. RawBrowse prototype and PhotoEvidenceKit — 2026-11-06

The manual inspection/comparison stage is now implemented in RawBrowse using a
new sibling local Swift package, `PhotoEvidenceKit`. This is a working prototype
host integration, not completion of the full RawCull P0 or a published release.
The package preserves the existing MIT license and attribution and is prepared
for separate public hosting; no repository URL or release tag is assumed.

### Implemented

- A right-side Close-ups panel for all selected images, with scrollable cards,
  per-image manual regions, overview click/drag, sliders and reset.
- Explicit Fit region / Source pixels modes, source dimensions and attribution.
- Pin / Replace / Unpin reference, retained across selection changes, distinct
  from host selection and photographer winners. Reference appears once.
- Current / Reference labels and an explicit host Show image action for selected
  inputs; background image completion cannot activate a different frame.
- Independent or linked inspection pan/zoom around each frame's own region,
  unlink and reset. Linking does not copy subject coordinates across frames.
- Source-bound manual regions restored through an injected storage contract.
  RawBrowse uses small versioned UserDefaults records and stable source
  fingerprints, not session UUIDs. Reset region is durable; pin/pan/zoom remain
  session state. Storage failures are visible and retained for retry.
- Bounded raster artifacts, serialized host loading and stale-result protection.

### Actual package boundaries

| Product | Owns |
| --- | --- |
| `PhotoEvidenceContracts` | `CloseUpFrame`, `CloseUpRegion`, `CloseUpViewport`, `CloseUpRequest`, versioned region records and storage interface |
| `PhotoEvidenceEngine` | Shared crop/overlay/pan geometry, owned bounded rasterization and `CloseUpRendering` |
| `PhotoEvidenceUI` | Embeddable `CloseUpPanel`, session model, retained reference and inspection controls |

RawBrowse retains frame/fingerprint, access/image, storage and activation adapters.
SwiftPM enforces the package dependency direction; package source imports neither
RawBrowse nor RawCull. A synthetic standalone demo consumes public APIs only.
Package documentation defines coordinates, source-pixel scale, persistence and
host scheduling responsibilities. The initial package targets Swift 6.2+ and
macOS 26+.

### Still required for the full P0

RawCull review integration; arbitrary rectangle drawing/edge resizing and main
photograph overlays; undo policy; RawCull-specific decoded-source wiring; subject/mask
proposal and confirmation; validated cross-frame matching; unified AF/detail
snapshots and typed availability; measurement provenance/comparability;
independent technical suggestions and protected durable decisions; optional
Combined Review escalation; and the orientation/performance/photographer
qualification specified above.

The existing generated sketches remain references, not a specification of the
current prototype. The chosen right-side selected-image layout supersedes their
placement for the RawBrowse prototype. Numerical memory/latency budgets and
production acceptance still need measurement; bounded output and passing unit
tests alone do not establish those results.


## 14. Implemented package API and ownership

This section records the implementation present on 2026-11-06. Sections 6 and 12
remain the broader target architecture: their proposed evidence/recommendation
contracts must not be mistaken for APIs already exported by the package.

### 14.1 Repository and products

The package is a sibling of the two application projects:

```text
RawCull/                         # shared parent directory
├── PhotoEvidenceKit/
│   ├── Package.swift
│   ├── Sources/PhotoEvidenceContracts/
│   ├── Sources/PhotoEvidenceEngine/
│   ├── Sources/PhotoEvidenceUI/
│   ├── Examples/PhotoEvidenceDemo/
│   ├── Tests/PhotoEvidenceKitTests/
│   └── Documentation/
├── RawBrowse/
└── RawCull/
```

Its three library products are imported as `PhotoEvidenceContracts`,
`PhotoEvidenceEngine` and `PhotoEvidenceUI`; there is currently no umbrella
`import PhotoEvidenceKit`. `PhotoEvidenceDemo` is an executable example and is
not an application dependency. The manifest specifies Swift tools 6.2, Swift 6
language mode and macOS 26 minimum. The package has no external dependencies.

Contracts contain Foundation/CoreGraphics coordinate values, not image buffers
or SwiftUI views. Engine depends on Contracts. UI depends on Engine and Contracts.
The package does not import either app, RawParserKit or optional AI runtimes.
Raw decoding, permissions and physical storage remain host responsibilities.

The MIT license and attribution are preserved. Public API documentation lives in
`README.md`, `Documentation/Integration.md` and `Documentation/Architecture.md`.
The demo consumes public APIs using synthetic portrait/landscape images, so it
can be built and run without either app or private photographs. Public hosting,
a remote dependency URL and a release version are separate publication steps.

### 14.2 Actual input/output contracts

| API | Current contract |
| --- | --- |
| `CloseUpFrame` | Source URL identity, display name and stable string source revision; no FileItem, catalog or view-model dependency |
| `CloseUpRegion` | Manual center and fraction in normalized oriented-image coordinates; top-left origin, x right, y down; bounds are clamped and persistence uses a finite normalized representation |
| `CloseUpViewport` | Temporary zoom and region-relative pan offset; linking copies this inspection state, never another frame's region |
| `CloseUpRequest` | Frame, region, render-source descriptor, scale mode, display scale, viewport state and viewport size; default viewport is 280 × 210 points |
| `CloseUpRender` | Bounded crop/overview CGImage artifacts, actual source dimensions, source label, matching render-source descriptor, coordinate transform and displayed normalized bounds; this is a rendering result, not a scored evidence snapshot |
| `CloseUpRendering` | Async Sendable service accepting a request and returning a render or error; the host supplies source access and scheduling |
| `CloseUpRegionRecord` | Codable schema-versioned region bound to source URL and revision; no images, permissions, ratings or model outputs |
| `CloseUpRegionStoring` | Injected main-actor, synchronous, preference-sized load/save interface; use fast cached storage, not blocking catalog-file I/O |

`CloseUpCropGeometry` is shared by rendering and overlays, including source-pixel
scale, edge clamping and pan conversion. `CloseUpRasterizer` redraws crops into
independently owned buffers: a small CGImage slice must not retain a complete
full-resolution source. At the default viewport and maximum backing scale of 4,
artifacts are limited to 1120 pixels on their longest edge. The host still owns
source-decode concurrency and source-cache limits.

The host must normalize orientation once before rasterization and supply truthful
source attribution. **Source pixels** at zoom 1 means one source pixel per display
point, not per physical display pixel. Fit region can use different magnification
per frame. Neither mode establishes measurement comparability.

### 14.3 Presentation model, reference and linked inspection

The host creates one `CloseUpModel`, optionally injecting a region store, and
passes it to `CloseUpPanel` with selected frames, an optional current frame URL,
a renderer, an optional activation callback and a close callback. The panel is
304 points wide; the host chooses its position. RawBrowse embeds it on the right.

The model reconciles frame updates and owns only inspection presentation state.
The reference appears once, first, and remains available after deselection.
Pin/Replace/Unpin never changes a rating or selects a photographer winner. The
optional Show image action supplies an explicit frame to the host and is offered
for selected inputs; the host validates activation against its current context.

Choose each image's region independently, then enable Link pan/zoom. Linking
starts from the current frame's viewport when available and applies relative
pan/zoom around every frame's own region. New candidates inherit the shared
inspection. Unlink keeps the current views and permits independent changes.
Reset view affects one card, or all linked cards; Reset views resets the working
set. Reset region saves the default manual region for that image only.

The overview changes the manual region. Dragging the enlarged crop changes the
temporary inspection offset. These actions remain separate, including while
rendering completes asynchronously. Linking is not optical registration,
segmentation or moving-subject tracking.

### 14.4 Persistence and work lifecycle

RawBrowse's `BrowserCloseUpRegionStore` stores small JSON-encoded records in
UserDefaults, under source-URL-derived keys. A record restores only when schema,
source identity and source revision match. Its frame adapter computes stable file
fingerprints off the UI actor; session UUIDs are not persistence revisions.
Moving to a new URL currently creates a new identity, with no automatic relinking.

Manual regions survive navigation and relaunch through the store. Reference,
zoom and pan are session state. Storage failures remain visible and unsaved
records are retained for retry. A different durable backend belongs in a RawCull
adapter; an asynchronous database backend needs an explicit write-through/cache
policy rather than claiming success before a write is committed.

The host owns the model and renderer lifetime. Card tasks cancel and release
artifacts on disappearance. Generation checks reject late provider results;
cancellation alone is insufficient. The RawBrowse renderer serializes requests
across suspension points, checks source fingerprints before/after loading and
uses the existing image loader/access leases. Closing the panel can preserve its
host-owned model while releasing rendered images.

## 15. RawCull import and integration checklist

**Importing the package supplies the manual inspection UI and engine.** RawCull
still needs its own composition and adapters. No RawCull burst workspace has been
wired to the package by the RawBrowse implementation.

### 15.1 Package setup and ownership

1. Add `../PhotoEvidenceKit` as a local Swift package reference to RawCull's Xcode
   project. Link only the library products required by the app/test targets.
   For a public release later, replace the local reference with the actual remote
   URL and qualified version; do not fabricate a tag or add duplicate local and
   remote copies of the same package.
2. Create a small RawCull evidence integration folder. The proposed names below
   describe new work, not files already present. Keep package imports/composition
   there and at the workspace boundary, rather than spreading them through
   RawCullViewModel.
3. Own the inspection model at review-session scope, independent of individual
   crop-card recreation. Keep the existing BurstReviewSessionModel authoritative
   for winners/review state and the rating repository authoritative for ratings.
   The CloseUpModel must not become another decision store.

### 15.2 Required RawCull adapters

| Proposed adapter | RawCull work required |
| --- | --- |
| `RawCullEvidenceFrameAdapter` | Map the chosen burst working set from FileItem to stable URL/revision values; retain a validated URL ↔ current FileItem.ID map; avoid basenames and transient group IDs as durable keys |
| `RawCullEvidenceRenderer` | Implement CloseUpRendering using existing image-loading/access services; supply oriented images and actual source labels; reuse the frame-cache policy rather than introduce another unbounded decoded-image cache |
| `RawCullEvidenceRegionStore` | Implement the region storage interface, decide preference versus catalog scope, expose failures, and document source/move/schema behavior; do not mix region records into rating semantics |
| `RawCullEvidenceHost` | Supply ordered frames/current URL, validate Show image activation, preserve keyboard focus and existing filmstrip/rating behavior, and own visibility/group lifecycle |

Inspect `BurstWorkspaceImageCoordinator` and the `BurstFrameCacheKey`/policy types
before deciding image-service reuse. The current coordinator is tied to workspace
state: extract or expose a narrow image-service boundary if necessary instead of
making PhotoEvidenceKit depend on the coordinator or RawCullViewModel.

Choose an explicit source policy for the first RawCull integration. The package
now supplies render descriptors/revisions and coordinate mapping; RawBrowse
implements JPG/RAW/RAW9 switching as described in section 17. RawCull still needs
to map its own image pipeline and development settings into those contracts.
A file fingerprint alone does not describe development settings or render aspect
ratio. Never change source silently while keeping a score or crop attribution
that describes the previous source.

### 15.3 Workspace behavior to resolve before implementation

- Embed the collapsible panel beside `BurstImageStage` while retaining
  `BurstWorkspaceFilmstrip`, the full composition and normal burst navigation.
  Use the chosen right-side layout as the initial prototype reference; verify
  smaller windows against the fixed panel width.
- Define an initial bounded working set, such as current plus nearby alternatives
  and the retained reference. Larger groups remain accessible through the filmstrip.
  The panel supports a scrollable selection; that does not authorize decoding the
  entire burst concurrently.
- Keep a reference while navigating candidates in the same burst. Initially clear
  it deliberately on a group change, so an unrelated burst is not compared by
  accident. Cross-group references require a separate explicit product policy.
- Route activation through authoritative host selection. Existing rating actions
  must capture the intended FileItem.ID at invocation; crop completion must never
  retarget a rating. Pinning must remain separate from a manual winner.
- Reconcile workspace keyboard monitors/focus with crop controls. Arrow keys used
  by a focused slider must not also navigate frames through the outer burst key
  handler. Preserve existing review shortcuts and an accessible close action.
- Preserve saved regions when viewport/session state resets. Explicitly clear
  temporary inspection on the selected lifecycle boundary; do not delete durable
  regions merely because `resetForGroupChange` clears the image cache.

### 15.4 Minimum manual-integration acceptance

The first RawCull delivery is complete only when a photographer can open a burst,
choose independent regions, pin a reference, advance the current frame, link and
unlink inspection, save/reset regions and reopen the group without losing its
manual decisions. Check that the reference is shown once and cleared according
to group policy. Show image must activate the intended file without changing a
winner or a rating.

Test selection/group/source changes with out-of-order results; persistence failure
and retry; portrait/rotated/mirrored images with known landmarks; source-pixel
scale on different displays; focus/keyboard conflicts; narrow windows and memory
pressure. Measure cold/warm first-crop latency, navigation latency and peak memory
in RawCull. Package tests and RawBrowse UI checks do not substitute for those host
integration checks.

## 16. Remaining full-P0 capabilities after manual integration

These are feature/policy extensions beyond simply importing the existing package.
Several underlying analyses already exist in RawCull; the missing work is a
qualified, consistent projection and workflow, not necessarily a new algorithm.

| Capability | Missing implementation and ownership |
| --- | --- |
| Main-photograph region editing | Shared overlay/transform binding to the stage, arbitrary rectangle drawing, edge resizing and undo; current package has center/fraction controls and overview dragging |
| Developed RAW inspection | Package contract and RawBrowse implementation now exist; RawCull still needs its own decoder/source/settings adapter and host qualification |
| Subject assistance | Optional mask/region proposal provider, provenance, confirmation and manual correction; validated cross-frame matching must precede automatic subject-based suggestions |
| Unified evidence | Revisioned snapshots for AF, subject detail, whole-frame detail and generated observations; typed loading/unavailable/failed/stale states and appropriate actions |
| Comparability | Versioned rules for source class, metric/preprocessing, region and sampling compatibility; incompatible values must not enter a common numerical comparison |
| Technical recommendations | Independent suggestion/reasons, calibrated eligibility and abstention; never overwrite or reinterpret a manual winner |
| Durable review actions | RawCull-host integration of ratings, winners, review/defer, expected revisions and undo; current package does not expose a general rating/winner command interface |
| Combined Review | Explicit bounded shortlist request, frozen source/region inputs, run/model attribution and stale-report handling after inputs change |
| Release qualification | Full difficult-burst fixtures, orientation/display checks, measured budgets and photographer evaluation from sections 8–9 |

The current CloseUpFrame/Request/Render interfaces are sufficient for manual
inspection, not the entire EvidenceContext/EvidenceSnapshot/Recommendation design
in section 12. Add those as explicit versioned contracts when their delivery
stage begins. Keep AI providers, the RawCull decision repository and XMP exchange
outside the package UI, and preserve a fully usable manual path throughout.


## 17. Decoded-source contract and RawBrowse wiring — 2026-11-06

PhotoEvidenceKit now distinguishes file identity from render identity. The new
`CloseUpRenderSource` value contains a source kind, backend identifier and settings
revision. CloseUpRequest carries it, and CloseUpRender must echo it. The panel
accepts descriptors keyed by frame URL, including a pinned reference. Changed
source/settings descriptors rerender the crop; they do not erase saved regions.
Mismatched results and late results from earlier requests are rejected.

The new `CloseUpCoordinateTransform` maps canonical oriented-image regions into
the actual developed output. Rasterization, overview rectangles, inverse region
editing and pan math share that mapping. A region outside a developed crop yields
an explicit error instead of inspecting an unrelated part of the image. Existing
single-source clients retain identity mapping and an unspecified-source default.

RawBrowse now follows the main preview's JPG/RAW selection for all cards and the
retained reference. Supported files use native RAW9 output and its bit depth;
other RAW files use the existing development service. Rendered image files retain
their original-image path. Each card uses its own saved adjustments or its own
live/unsaved snapshot; selecting one photograph does not apply its settings to
other photographs. Exposure/color, crop, straighten and bit-depth changes enter
the render revision. The adapter maps RAW9's straighten-then-crop geometry, and
labels the actual output source and dimensions. Those dimensions may differ
from the embedded preview because of a saved development crop.

RAW decoding stays in RawBrowse. PhotoEvidenceKit receives a decoded CGImage
through its rendering/rasterization boundary and has no decoder dependency.
Source-pixel inspection uses native decoded dimensions rather than a reduced
fit preview. Native loading is serialized through the host renderer and reuses
existing bounded decode/cache services; production memory/latency qualification
remains required. Decode failure does not silently substitute a JPG.

During this update, RawBrowse's Xcode dependency is intentionally changed to the
local sibling `../PhotoEvidenceKit`, linking only Contracts, Engine and UI.
Switching to the user's published package version is a later project-reference
change. RawCull's integration remains pending: it must supply its own source
selection, settings revisions, permissions, decoded images and geometry mapping
through these same contracts.
