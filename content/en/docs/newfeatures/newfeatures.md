+++
author = "Thomas Evensen"
title = "RawCull 3.3.6: Features and Competitive Opportunities"
linkTitle = "Features and Competition"
date = "2026-09-01"
lastmod = "2026-11-05"
description = "RawCull 3.3.6 features, a cross-platform photo-culling comparison, and prioritized opportunities for evidence-based review and editor interoperability."
tags = ["roadmap", "features", "culling", "ai", "competition", "xmp", "faces"]
categories = ["technical details"]
weight = 10
+++

# RawCull 3.3.6: Features and Competitive Opportunities

RawCull's most promising position is **local, evidence-based selection for RAW
photographers who want to understand and control the decision**. Version 3.3.6
already combines fast preview review, camera autofocus evidence, subject-detail
measurements, semantic search and optional multi-model review. The next gains
should come from making those capabilities easier to use and easier to connect
to an editor.

This review replaces the September 2026 roadmap and its October implementation
notes. RawCull was checked against application commit
[`f75adff`](https://github.com/rsyncOSX/RawCull/tree/f75adff751e5f636f69d4cc40141c314b47ebb21)
on **5 November 2026**. The main app configurations identify version **3.3.6,
build 429**; some ancillary targets still identify build 428. This is a checkout
baseline, not confirmation of the build distributed through any store.

Competitor facts below come from vendor documentation checked on the same date.
They describe advertised capabilities, not independently measured accuracy,
latency, market share or customer satisfaction. Recommendations are product
judgments inferred from those capabilities and RawCull's implementation. No
hands-on comparative benchmark was performed. Availability can vary by plan,
platform and release; prices and minimum OS versions should be checked before
purchase.

## What RawCull 3.3.6 already provides

| Area | Implemented capability | Boundary that matters |
| --- | --- | --- |
| RAW browsing | Dedicated ARW, NEF and DNG paths, embedded previews, cached thumbnails and developed-RAW display | Generic formats use macOS decoding; extension recognition is not a tested camera-support guarantee |
| Broader format admission | Canon CR2/CR3/CRW, Fujifilm RAF, Olympus ORF, Panasonic RW2, Pentax PEF and other registered RAW extensions | Camera, compression and OS support still require qualification; generic admission does not add dedicated vendor AF parsing |
| Focus inspection | Camera AF overlays where available, focus masks, full-frame, salient-subject and AF-region sharpness evidence | A recorded AF location is not proof that the intended subject is sharp; scores depend on the analyzed render |
| Burst review | Similarity grouping, ranked candidates, comparison, manual winners and review/defer state | Grouping and ranking assist the photographer; they do not establish a universally best photograph |
| Similarity and search | Optional OpenAI/DataComp CLIP image similarity and natural-language search; Vision similarity fallback | Text search requires CLIP; Vision fallback is not semantic text search |
| Deep Review | Optional SAM 3 subject segmentation, subject-mask detail scoring and cached subject outlines | Segmentation identifies pixels, not photographic merit or eye state |
| Qwen Vision | Optional local Qwen3-VL-2B-Instruct photo assessment | Generated observations can be wrong; they are not measured focus evidence |
| Objects | Qwen concept discovery, SAM 3 object instances, numbered review crops and per-object findings | Object descriptions and confidence require visual checking; an object mask is not qualified anatomical detection |
| Combined Review | Criteria-based review of 1–8 images, with registered masks, observations, measurements, evidence inspection and multi-image comparison | Bounded shortlist review, not an unattended whole-catalog culling engine; comparison can abstain |
| Decisions and handoff | Batch selection/rating, saved decisions, JPEG export and rsync-based copying of tagged or minimum-rated RAW files | Ratings are app JSON data, not standard XMP interchange; embedded-byte JPEG export remains ARW/NEF/DNG-specific |
| Exposure inspection | Temporary EV/tone inspection, histogram and clipping overlays in zoom | Display-referred inspection is not a sensor-domain RAW histogram, persistent editing or an export adjustment |
| Model management | Optional model download, validation, licence presentation and resource controls | First use requires obtaining compatible assets; local analysis does not mean zero setup, storage or memory cost |

The current project targets **Apple silicon and macOS 27**. This narrow platform
baseline is an adoption constraint compared with many competitors. It should be
communicated clearly rather than treating every Mac owner as an eligible user.

See [RAW Formats and Exposure Inspection]({{< relref "raw-inspection.md" >}}),
[AI Models in RawCull]({{< relref "/docs/ai/aiinrawcull.md" >}}), and
[Combined Review]({{< relref "/docs/ai/aicombined.md" >}}) for detailed behavior.
The source boundaries include
[model choices](https://github.com/rsyncOSX/RawCull/blob/f75adff751e5f636f69d4cc40141c314b47ebb21/RawCull/Intelligence/Contracts/RawCullAIModels.swift),
[decision persistence](https://github.com/rsyncOSX/RawCull/blob/f75adff751e5f636f69d4cc40141c314b47ebb21/RawCull/Model/JSON/WriteSavedFilesJSON.swift),
[Combined Review](https://github.com/rsyncOSX/RawCull/blob/f75adff751e5f636f69d4cc40141c314b47ebb21/RawCull/Intelligence/CombinedReview/CombinedReviewFeature.swift),
and [build settings](https://github.com/rsyncOSX/RawCull/blob/f75adff751e5f636f69d4cc40141c314b47ebb21/RawCull.xcodeproj/project.pbxproj).

### Important changes from the old roadmap

Qwen, Objects and Combined Review are implemented capabilities, not future model
ideas. Broader RAW admission is also implemented, although a camera-qualified
support matrix remains work to do. XMP exchange and dedicated face/eye quality
inspection remain gaps in the inspected application.

EfficientSAM assets and a linked package product do not establish a selectable
feature: the current application segmentation enum exposes **SAM 3 only**.
Reintroducing an alternative should depend on a measured user benefit, not on
its presence in the package. The roadmap should no longer be organized around
adding more models.

## Competitive landscape across operating systems

The comparison covers direct AI cullers, fast manual review tools and editors
that can absorb the culling step. Linux alternatives are included because they
show how much local functionality is available without a commercial cloud
workflow. Desktop capability should not be assumed to exist in a vendor's
mobile app.

| Application | Desktop platforms | Main reason to choose it | Implication for RawCull |
| --- | --- | --- | --- |
| Aftershoot | macOS, Windows | Automated/assisted/manual culling, duplicate groups, blur and closed-eye checks, target yield and editor handoff | Workflow completeness and automation are strong competition; offline culling is already offered [A] |
| Narrative | macOS, Windows | Face close-ups, focus/eye assessments, scene grouping and sharpness ranking | Excellent reference for reducing zooming and comparison effort [N] |
| Lightroom Classic | macOS, Windows | Assisted Culling inside the existing editor/catalog, including subject/eye criteria and face scores | RawCull must save enough time or provide enough evidence to justify another application [L] |
| Capture One | macOS, Windows | Integrated Cull view plus Assisted Review for technical portrait issues | Compare against its current assisted workflow, not an obsolete manual-only baseline [C] |
| Imagen | macOS, Windows | Best-of-group or requested-count culling connected to editing | Local analysis is a meaningful alternative to its upload-based workflow, but integration remains a strength [I] |
| FilterPixel DeepCull | macOS, Windows | Genre-based criteria, explanations, burst grouping and target counts | Explanations and wildlife/sports criteria alone are not unique; DeepCull documents cloud AI scoring [F] |
| Photo Mechanic | macOS, Windows | Fast manual review, multi-card ingest, renaming and metadata workflows | Responsiveness and dependable ingest can matter more than another AI score [P] |
| FastRawViewer | macOS, Windows | RAW rendering, RAW histogram/statistics, exposure and focus inspection | Technical RAW evaluation is established competition; keep RawCull's render semantics explicit [R] |
| Excire Foto 2027 | macOS, Windows | Local search, people/content organization, grouping and quality-assisted selection | Local semantic search and privacy are shared strengths, not exclusive advantages [E] |
| digiKam | macOS, Windows, Linux | Open-source DAM, local optional AI, face recognition, duplicates and quality labels | Free local AI is a credible alternative; a focused, efficient review experience must earn adoption [D] |
| darktable | macOS, Windows, Linux | Open-source RAW editor with side-by-side culling and synchronized inspection | Manual culling plus editing is already available without buying a specialist culler [T] |

### Direct AI culling competitors

**Aftershoot** offers automatic selection as well as assisted and manual modes.
Its documentation describes blur/closed-eye checks, duplicate grouping, key
faces, configurable ratings and Cull to Target. RawCull's opportunity is a
more inspectable technical comparison for difficult bursts, rather than merely
matching another automatic score. Its larger gap is the complete journey from
first pass to editor. [Aftershoot guide](https://support.aftershoot.com/en/articles/5223473-get-started-with-aftershoot-culling),
[offline/platform FAQ](https://aftershoot.com/culling-faq/) [A].

**Narrative** makes close inspection efficient through face crops, eye/focus
assessments and scene-based ranking. It also documents non-face close-ups and
wildlife sharpness ranking, so RawCull should not assume that non-portrait
subjects are uncontested. The useful design lesson is to reduce the number of
manual zoom-and-pan actions. Windows support is now documented alongside macOS.
[Narrative Select](https://narrative.so/select),
[platform support](https://help.narrative.so/en/articles/7337410-can-i-use-narrative-on-windows) [N].

**Imagen** supports selecting the best photographs in a group or a specified
number, reviewing the choices and continuing into editing. Its FAQ describes
uploading low-resolution files for culling/editing. RawCull can appeal to users
working with unreliable connectivity or keeping analysis on their own machine.
That advantage does not establish better selection quality.
[Culling workflow](https://support.imagen-ai.com/hc/en-us/articles/17225669268253-Get-started-with-AI-culling),
[upload behavior](https://imagen-ai.com/faq/),
[desktop requirements](https://support.imagen-ai.com/hc/en-us/articles/4445860985361-Minimum-hardware-and-software-requirements-and-supported-file-formats) [I].

**FilterPixel DeepCull** advertises genre-dependent criteria, explanations,
best-of-burst selection and target counts. Its current specification explicitly
says **cloud AI scoring** while original RAWs remain local. Keeping RAW originals
on disk does not mean analysis is offline. RawCull's possible advantage is
local, inspectable region evidence; genre-aware explanations by themselves
are already offered. The page contains inconsistent genre counts, so this
review does not treat its exact count as a qualified capability.
[DeepCull specifications](https://filterpixel.com/deepcull) [F].

### Editors that reduce the need for a separate culler

**Lightroom Classic** documents subject sharpness, eye sharpness and eye-open
criteria, per-face scores, reviewable selection reasons and batch actions.
This weakens a generic “AI first pass” pitch: existing customers already have
one in their catalog. RawCull needs a demonstrable benefit on difficult
shortlists and a reliable return path for decisions.
[Adobe Assisted Culling](https://helpx.adobe.com/lightroom-classic/desktop/organize-photos-in-lightroom-classic/assisted-culling.html) [L].

**Capture One** offers grouped review and introduced Assisted Review for closed
eyes, missed focus and exposure problems in May 2026; the current vendor release
page still labels it Beta and reports subsequent updates. This makes
studio/portrait displacement a harder initial target. RawCull can instead
complement the editor for challenging technical comparisons.
[Cull workflow](https://learn.captureone.com/page/17/),
[Assisted Review introduction](https://www.captureone.com/en/explore-features/whats-new/16-8),
[current release overview](https://www.captureone.com/en/explore-features/whats-new) [C].

### Manual review, RAW inspection and local library tools

**Photo Mechanic** is a benchmark for working while ingest continues, multi-card
copying, metadata templates, renaming and fast preview review. RawCull should
measure its basic browsing and handoff against this workflow before adding
complex analysis to every image. **FastRawViewer** emphasizes RAW-based exposure
statistics, focus inspection and converter handoff. RawCull must distinguish
its temporary rendered exposure view from those RAW-data measurements.
[Photo Mechanic tour](https://home.camerabits.com/tour-photo-mechanic/),
[platform requirements](https://docs.camerabits.com/support/solutions/articles/48001080502-system-recommendations-compatibility) [P];
[FastRawViewer features and platforms](https://www.fastrawviewer.com/) [R].

**Excire Foto 2027**, the product currently promoted by the vendor, combines local
semantic search, people/content organization, scene grouping and image-quality
selection. That is direct overlap with RawCull's CLIP search and local AI pitch.
RawCull's better opportunity is focused selection with camera and region
evidence, rather than rebuilding a general photo library.
[Excire Foto](https://excire.com/en/excire-foto/),
[platforms and current products](https://excire.com/en/) [E].

**digiKam** documents optional on-device models, face recognition, similarity
search and quality-based pick labels. Face recognition identifies people; it
should not be confused with dedicated blink or eye-sharpness assessment.
**darktable** offers side-by-side culling with zoom and pan, integrated with RAW
editing. These are meaningful Linux choices as well as alternatives on Mac and
Windows, but neither cited feature set establishes the same automatic
best-of-burst workflow as the specialist products.
[digiKam features](https://www.digikam.org/about/features/),
[platform documentation](https://www.digikam.org/documentation/faq/) [D];
[darktable culling](https://docs.darktable.org/usermanual/development/en/lighttable/lighttable-modes/culling/),
[downloads/platforms](https://www.darktable.org/install/) [T].

## Where RawCull could gain momentum

### 1. Explain difficult wildlife and sports burst decisions

This is the strongest initial hypothesis. RawCull already has camera AF
evidence, subject masks, detail scoring, manual winners and bounded Combined
Review. Bring those together into a short comparison: which subject was
measured, which render was used, where the AF point falls, and why the result
is uncertain. Let the photographer identify the intended subject when automatic
selection finds the wrong one.

A useful example is a bird burst where the background is sharp but the bird is
soft. Whole-frame sharpness is insufficient. Show comparable subject crops,
mask coverage and detail evidence; distinguish a missing eye assessment from
an actual eye-quality result. Preserve a photographer's preferred gesture even
when another frame has a higher technical score.

This is not an uncontested market: Narrative ranks wildlife sharpness and
FilterPixel markets wildlife/sports criteria. The defensible opportunity is
**a better, faster, verifiable decision on difficult bursts**. It requires
photographer trials, not a uniqueness claim based on model names.

### 2. Remove the cost of using an extra application

XMP interoperability is the highest-priority general adoption improvement.
Copying selected RAWs is useful, but users also need decisions to survive in
Lightroom Classic, Capture One and other editors without reconstructing them.

Define a deliberate mapping for RawCull's reject/neutral/star states to XMP
ratings and editor-specific flags or labels. Read existing metadata, preserve
unknown fields, detect external changes and make conflicts visible. Avoid
claiming that every editor interprets pick flags or color labels identically.
Qualify both directions with existing sidecars, mixed selections and externally
changed ratings. This is proposed work, not a 3.3.6 capability.

### 3. Make the first pass simple; reserve deep analysis for shortlists

Present existing evidence through conservative **Keep**, **Review** and
**Likely Reject** queues, with explicit reasons and easy overrides. Preserve
manual winners and keep uncertain cases visible. The current 1–8-image Combined
workflow should remain an escalation path for difficult choices; running a VLM
on every photograph needs a separate throughput and quality justification.

Target yield can follow once basic selection is trustworthy. A requested count
must not silently discard unique moments or hide uncertain cases. This closes
a workflow gap against Aftershoot, Imagen and FilterPixel, rather than creating
a unique feature by itself.

### 4. Add face and eye inspection if portraits become a target market

Narrative, Aftershoot, Adobe and Capture One make this an important competitive
requirement for weddings, events and groups. Start with synchronized face crops
and eye-region inspection, then evaluate a calibrated eye-state classifier.
Support glasses, small faces, profiles, occlusion and low light; expose
“unknown” rather than treating every detection as reliable.

Do not position general Qwen observations as a validated blink detector. For
group photos, show each relevant face rather than hiding one poor face inside
an average score. Face identity recognition is a separate product choice and
is not required to solve this inspection problem.

### 5. Earn trust through supported cameras and predictable performance

Publish a tested camera/format table distinguishing browsing, embedded preview,
RAW development, AF metadata and JPEG extraction. Add real samples across
compression variants. A long extension list is less useful than knowing that a
particular camera workflow works.

Keep ordinary browsing responsive while optional models load or run. Clearly
show model size, setup progress, cancellation and recovery. Investigate the
cost and reach of the macOS 27 baseline before promising broader Mac adoption;
a Windows/Linux port would be a much larger undertaking because the current
implementation depends on Apple frameworks. XMP handoff can improve mixed-OS
workflows much sooner than a port.

## Priorities after 3.3.6

These are recommendations, not release commitments. Effort is relative and
includes integration and qualification, not just UI implementation.

| Priority | Work | Expected benefit | Relative effort | Evidence required before release |
| --- | --- | --- | --- | --- |
| P0 | XMP import/export and editor handoff | Removes a broad adoption blocker | Medium–large | Round-trip results in Lightroom Classic and Capture One; no loss of unrelated metadata |
| P0 | Unified burst evidence and comparable subject crops | Strengthens the most credible niche using existing capabilities | Medium | Faster difficult-burst decisions with equal or fewer missed keepers |
| P1 | Conservative first-pass queues with override protection | Makes existing analysis usable at shoot scale | Medium–large | Lower total review time, measured false rejects and retained manual decisions |
| P1 | Camera qualification and browsing/model performance | Makes product claims dependable | Ongoing | Camera-specific outcomes, cold/warm latency, memory and cancellation measurements |
| P1 if targeting portraits | Face/eye inspection | Opens portrait/event workflows | Large | Per-face quality across difficult conditions and reduced manual zooming |
| P2 | Ingest backups, renaming and metadata templates | Improves professional field workflow | Medium–large | Interrupted-copy recovery, verified output and metadata preservation |
| P2 | Target yield and genre presets | Helps deadline-driven users after trust is established | Medium | Moment diversity, unique-frame retention and transparent target compromises |
| Research | Alternative segmentation or other new models | Only worthwhile for demonstrated quality, latency or memory gains | Variable | Same-case improvement over current SAM 3/non-model baselines |

Full RAW editing, retouching, cloud delivery and a broad model marketplace would
spread effort across areas already served by established products. The immediate
opportunity is to finish the selection-to-editor workflow and make RawCull's
existing evidence easier to act on.

## How to test the opportunity

Use the same labeled shoots in RawCull and selected competitors. Include birds
and wildlife, sports action, portraits/groups, landscapes and low-light scenes.
Test supported camera/compression combinations, embedded versus developed
renders, difficult subjects and intentional creative blur. Let photographers
record acceptable alternatives rather than forcing a single subjective winner.

Measure end-to-end time from opening a shoot to accepted editor handoff,
including setup, uploads where applicable, review and correcting mistakes.
Report first-use model preparation separately from warm use. Run realistic
500-, 2,000- and 10,000-image catalogs; record hardware, storage, app versions,
settings, failures, peak memory and tail latency.

For selection quality, measure missed keepers, preferred-frame agreement,
manual overrides and time spent inspecting faces or subject crops. Audit all
Likely Reject placements in the labeled sample. For Combined Review, distinguish
valid structured output from visually correct observations and useful final
comparisons. For handoff, verify ratings and unrelated metadata after a round
trip through the target editor.

The commercial hypothesis is that photographers will adopt RawCull when it
**reduces difficult review time while preserving control and dependable editor
handoff**. Local processing supports that promise, but it cannot substitute for
measured workflow value.

## Detailed P0 plans

The following proposed plans expand the two P0 entries into workflows, scope,
implementation stages and release evidence:

1. [XMP import/export and editor handoff]({{< relref "xmp-editor-handoff.md" >}}).
2. [Unified burst evidence and comparable subject crops]({{< relref "unified-burst-evidence.md" >}}).
