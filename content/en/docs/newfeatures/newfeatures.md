+++
author = "Thomas Evensen"
title = "RawCull 3.5.0: Features, Competition and Plan"
linkTitle = "Features and Competition"
date = "2026-09-01"
lastmod = "2026-11-25"
description = "RawCull 3.5.0 features, a cross-platform photo-culling comparison, and a prioritized plan."
tags = ["roadmap", "features", "culling", "ai", "competition", "xmp", "faces", "mcp"]
categories = ["technical details"]
weight = 10

reviewed_commit = "328b570bf14d44bcf33efc58dc23da94bfadf439"
reviewed_version = "3.5.0"
reviewed_build = 469
reviewed_on = "2026-11-25"
review_scope = "Recorded the 3.5.0 delta, removed the manual-winner claim and kept the ranked plan. Competitor evidence remains dated 5 November."
+++

# RawCull 3.5.0: Features, Competition and Plan

RawCull's strongest position is **local, evidence-based selection for RAW
photographers who want to understand and control the decision**. Version 3.5.0
combines fast preview review, camera autofocus evidence, burst ranking, face and
animal close-ups, semantic search, a single AI **Review** with three presets, and
an MCP server for desktop AI clients. The next gains should come from getting
decisions into an editor and from making the existing evidence easier to act
on, not from adding more models.

## Baseline and evidence

| Item | Value |
| --- | --- |
| Application source | [`328b570b`](https://github.com/rsyncOSX/RawCull/commit/328b570bf14d44bcf33efc58dc23da94bfadf439) on `version-3.5.0`, not yet on `main`, **3.5.0 build 469**, checked 25 November 2026 |
| Release status | No `v3.5.0` tag exists yet. The local `v3.4.9` tag points to [3c8e7aba](https://github.com/rsyncOSX/RawCull/commit/3c8e7aba0c72e00b05f2f6c88a1868565075e6b3). App Store availability was outside this source review. |
| Platform | Apple silicon, macOS 27 |
| Competitor evidence | Vendor documentation checked **5 November 2026**, not requalified for this revision |

Competitor facts describe advertised capabilities, not independently measured
accuracy, latency, market share or customer satisfaction. Recommendations are
product judgments based on those capabilities and RawCull's implementation. No
hands-on comparative benchmark was performed. Availability can vary by plan,
platform and release. Check prices and minimum OS versions before purchase.

## What RawCull 3.5.0 provides

| Area | Implemented capability | Boundary that matters |
| --- | --- | --- |
| RAW browsing | Dedicated ARW, NEF and DNG paths, embedded previews, cached thumbnails, viewport-sized and full-resolution developed-RAW display | Generic formats use macOS decoding; extension recognition is not a tested camera-support guarantee |
| Broader format admission | Canon CR2/CR3/CRW, Fujifilm RAF, Olympus ORF, Panasonic RW2, Pentax PEF and other registered RAW extensions | Camera, compression and OS support still need qualification; generic admission adds no vendor AF parsing |
| Focus inspection | Sony and Nikon AF points rotated into the upright frame, focus masks, full-frame, salient-subject and AF-region sharpness | A recorded AF location is not proof that the intended subject is sharp; scores depend on the analyzed render |
| Burst review | Similarity grouping, ranked candidates with confidence and cautions, comparison, review/defer state, and a bar that names the measured, ranked and AI best frames when they differ | Grouping and ranking assist the photographer; they do not establish a universally best photograph |
| Close Up | Manual crop comparison across frames with pinned references, saved regions, linked pan/zoom, JPG or developed-RAW source and **Use AF point** | Linked pan/zoom copies inspection state; it does not track the same subject across frames |
| Faces and animals | Automatic strip with human face crops and a local preview detail value, plus animal head and eye crops from Vision landmarks; **People Ranking** reorders a group by face evidence | No eye-open/closed assessment. Apple documents cat and dog support; birds and other wildlife are unvalidated |
| Similarity and search | Optional DataComp CLIP similarity and natural-language search; Vision similarity fallback | Text search requires CLIP; the Vision fallback is not semantic search |
| Review (single AI entry point) | **Focus check** (SAM 3 masks, subject focus measurement, CLIP; no Qwen), **Describe** (one Qwen assessment) and **Full** (all stages, per-object crops, written report) for 1–8 selected or tagged images. Results offer Tag and Rate for eligible catalog files, plus Mark Reviewed for an unambiguous burst | Bounded shortlist review, not whole-catalog culling. Qwen output is advisory. Describe and Full need 16 GB of unified memory, 32 GB recommended |
| Burst AI assessment | Local Qwen assessment of the recommended and alternate frame of every burst, with progress and cancel; results in the AI Assessments window, AI scores on both filmstrips, and a way back to the burst you came from | Up to two distinct ranked frames per eligible burst. Results last for the app session |
| MCP server | Bundled local helper: catalog queries while RawCull is closed, approved catalog setup, burst analysis, ranked recommendations and optional Qwen photo assessments from a desktop AI client | Authorization can be one-time or remembered. The AI client may send returned results to its own model provider |
| Decisions and handoff | Batch tag/reject/rating, saved decisions, JPEG export and rsync copying of tagged or minimum-rated RAW files with live progress | Ratings are RawCull JSON, **not XMP**. Embedded-JPEG export is ARW/NEF/DNG-specific |
| Exposure inspection | Temporary EV/tone inspection, histogram and clipping overlays in zoom | Display-referred; not a sensor-domain RAW histogram, persistent edit or export adjustment |
| Model management | Optional download, validation, licence presentation and resource controls for CLIP, SAM 3 and Qwen3-VL-2B | Local analysis still costs setup time, storage and memory |

The macOS 27 and Apple silicon baseline is an adoption constraint compared with
most competitors. Communicate it clearly rather than treating every Mac owner as
an eligible user.

Detailed behavior: [RAW Formats and Exposure Inspection]({{< relref "/docs/raw-inspection.md" >}}),
[Close Up]({{< relref "/docs/closeups.md" >}}),
[Burst Groups]({{< relref "/docs/burstgroup.md" >}}),
[RawCull MCP]({{< relref "/docs/mcp.md" >}}) and
[AI Models in RawCull]({{< relref "/docs/ai/aiinrawcull.md" >}}). Source
boundaries:
[model choices](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Intelligence/Contracts/RawCullAIModels.swift),
[decision persistence](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Model/JSON/WriteSavedFilesJSON.swift),
[Review](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull/Intelligence/CombinedReview/CombinedReviewFeature.swift)
and [build settings](https://github.com/rsyncOSX/RawCull/blob/328b570bf14d44bcf33efc58dc23da94bfadf439/RawCull.xcodeproj/project.pbxproj).

### What changed in 3.5.0

| Change | Effect |
| --- | --- |
| Focus check is preselected, and choosing a review type is separate from running it | Review works on every supported Mac without a Qwen download, and cannot be started by accident |
| Focus point, focus mask and magnifier on the Review photo | Camera focus, measured focus and pixels can be compared without leaving Review |
| AI top, Sharpest and Best Frame marks in both filmstrips | Disagreement between methods is visible. Nothing is merged or rated automatically |
| Confirmation before reassessing, and toolbar and maintenance actions disabled during a batch | Session results are not lost by one click |

None of the eight ranked items below is complete in this build. The release was
used for review ergonomics. The ranking stands as the plan for the next versions.

### What changed between 3.4.0 and 3.4.9

| Change | Effect on the competitive picture |
| --- | --- |
| Close Up gained automatic human face crops and animal head/eye crops (3.4.5) | Narrows the close-inspection gap to Narrative and Aftershoot. Eye-state assessment is still missing |
| People Ranking in the comparison workspace | First face-informed ordering. It is a session reorder, not a persisted recommendation |
| MCP server with approval, recovery and shared results | No direct competitor documents an equivalent. It is an integration differentiator, not a culling-quality claim |
| Deep AI Review, Qwen Vision and Objects tabs replaced by one Review with three presets | One place to ask "what is wrong with this photo?", with culling controls alongside eligible results |
| Burst AI assessment of the top two frames | A first step toward a whole-shoot first pass |
| Vision concurrency work, AF orientation fix, resolution/ISO-normalized subject detail, safer burst caches | Improves trust in the numbers; none of it is visible as a new feature |
| Large view-model refactoring into workspace models | Lowers the cost of the 3.5.0 work; automated workspace tests cover part of the refactor and the release checklist adds manual UI checks |

EfficientSAM assets in a linked package do not make a selectable feature: the
segmentation enum exposes **SAM 3 only**. XMP exchange and eye-state assessment
remain the two largest functional gaps.

## Competitive landscape across operating systems

The comparison covers direct AI cullers, fast manual review tools and editors
that can absorb the culling step. Linux alternatives show how much local
functionality is available without a commercial cloud workflow. Do not assume
that desktop capability exists in a vendor's mobile app.

| Application | Desktop platforms | Main reason to choose it | Implication for RawCull |
| --- | --- | --- | --- |
| Aftershoot | macOS, Windows | Automated/assisted/manual culling, duplicate groups, blur and closed-eye checks, target yield and editor handoff | Workflow completeness and automation are strong competition; offline culling is already offered [A] |
| Narrative | macOS, Windows | Face close-ups, focus/eye assessments, scene grouping and sharpness ranking | RawCull now has face and animal crops; Narrative still leads on eye assessment and fewer zoom actions [N] |
| Lightroom Classic | macOS, Windows | Assisted Culling inside the editor/catalog, with subject/eye criteria and face scores | RawCull must save enough time or give enough evidence to justify another app, and must hand decisions back [L] |
| Capture One | macOS, Windows | Integrated Cull view plus Assisted Review for technical portrait issues | Compare against its assisted workflow, not an obsolete manual-only baseline [C] |
| Imagen | macOS, Windows | Best-of-group or requested-count culling connected to editing | Local analysis is a real alternative to its upload-based workflow; its editing integration remains a strength [I] |
| FilterPixel DeepCull | macOS, Windows | Genre-based criteria, explanations, burst grouping and target counts | Explanations and wildlife/sports criteria alone are not unique; DeepCull documents cloud AI scoring [F] |
| Photo Mechanic | macOS, Windows | Fast manual review, multi-card ingest, renaming and metadata workflows | Responsiveness and dependable ingest can matter more than another AI score [P] |
| FastRawViewer | macOS, Windows | RAW rendering, RAW histogram/statistics, exposure and focus inspection | Technical RAW evaluation is established; keep RawCull's render semantics explicit [R] |
| Excire Foto 2027 | macOS, Windows | Local search, people/content organization, grouping and quality-assisted selection | Local semantic search and privacy are shared strengths, not exclusive advantages [E] |
| digiKam | macOS, Windows, Linux | Open-source DAM, optional local AI, face recognition, duplicates and quality labels | Free local AI is a credible alternative; a focused, efficient review must earn adoption [D] |
| darktable | macOS, Windows, Linux | Open-source RAW editor with side-by-side culling and synchronized inspection | Manual culling plus editing is available without buying a specialist culler [T] |

### Where RawCull 3.5.0 stands

A condensed view of the capabilities that decide adoption. "Common" means
several of the products above document it.

| Capability | RawCull 3.5.0 | Competitors | Assessment |
| --- | --- | --- | --- |
| Decisions reach the editor (XMP or catalog) | No | Common | **Largest gap** |
| Closed-eye / eye-sharpness assessment | No (face crops only) | Aftershoot, Narrative, Lightroom, Capture One | Gap for portrait and event work |
| Burst grouping and best-frame ranking | Yes, with confidence and cautions | Common | Parity |
| Camera AF point shown with sharpness evidence | Yes (Sony, Nikon) | Rare among cullers; FastRawViewer for inspection | Differentiator |
| Subject-mask focus measurement | Yes (Focus check) | Subject sharpness criteria in Lightroom, Narrative | Parity on intent, stronger on inspectability |
| Explained, inspectable AI findings | Yes (Review drill-down with regions and provenance) | Explanations in FilterPixel, reasons in Lightroom | Differentiator in depth, not in kind |
| Local, offline analysis | Yes | Aftershoot, Excire, digiKam; not Imagen or DeepCull scoring | Shared strength |
| Natural-language search | Yes (CLIP) | Excire, digiKam | Shared strength |
| AI-agent access (MCP) | Yes | None documented | Unique, niche audience |
| Whole-shoot first pass / target yield | Partial (burst AI assessment of two frames) | Aftershoot, Imagen, FilterPixel | Gap |
| Ingest, renaming, metadata templates | No (rsync copy only) | Photo Mechanic | Gap, lower priority |
| Windows / Linux | No | Most | Structural; XMP helps mixed-OS users sooner |

### Direct AI culling competitors

**Aftershoot** offers automatic, assisted and manual modes. Its documentation
describes blur and closed-eye checks, duplicate grouping, key faces,
configurable ratings and Cull to Target. RawCull's opportunity is a more
inspectable technical comparison for difficult bursts, not another automatic
score. Its larger gap is the complete journey from first pass to editor.
[Aftershoot guide](https://support.aftershoot.com/en/articles/5223473-get-started-with-aftershoot-culling),
[offline/platform FAQ](https://aftershoot.com/culling-faq/) [A].

**Narrative** reduces close inspection effort with face crops, eye and focus
assessments and scene-based ranking. It also documents non-face close-ups and
wildlife sharpness ranking, so non-portrait subjects are contested too. RawCull's
3.4.5 face and animal tiles follow the same design lesson: fewer manual zoom and
pan actions. Windows is documented alongside macOS.
[Narrative Select](https://narrative.so/select),
[platform support](https://help.narrative.so/en/articles/7337410-can-i-use-narrative-on-windows) [N].

**Imagen** selects the best photographs in a group or a requested number, lets
the user review the choices and continues into editing. Its FAQ describes
uploading low-resolution files for culling and editing. RawCull can appeal to
users with unreliable connectivity or who keep analysis on their own machine.
That does not establish better selection quality.
[Culling workflow](https://support.imagen-ai.com/hc/en-us/articles/17225669268253-Get-started-with-AI-culling),
[upload behavior](https://imagen-ai.com/faq/),
[desktop requirements](https://support.imagen-ai.com/hc/en-us/articles/4445860985361-Minimum-hardware-and-software-requirements-and-supported-file-formats) [I].

**FilterPixel DeepCull** advertises genre-dependent criteria, explanations,
best-of-burst selection and target counts. Its specification says **cloud AI
scoring** while original RAWs stay local, so keeping RAWs on disk does not mean
offline analysis. RawCull's possible advantage is local, inspectable region
evidence. The page gives inconsistent genre counts, so this review does not
treat an exact count as a qualified capability.
[DeepCull specifications](https://filterpixel.com/deepcull) [F].

### Editors that reduce the need for a separate culler

**Lightroom Classic** documents subject sharpness, eye sharpness and eye-open
criteria, per-face scores, reviewable selection reasons and batch actions. Its
customers already have an AI first pass in their catalog. RawCull needs a
demonstrable benefit on difficult shortlists and a reliable return path for
decisions.
[Adobe Assisted Culling](https://helpx.adobe.com/lightroom-classic/desktop/organize-photos-in-lightroom-classic/assisted-culling.html) [L].

**Capture One** offers grouped review and introduced Assisted Review for closed
eyes, missed focus and exposure problems in May 2026. On 5 November the vendor
release page still labelled it Beta. This makes studio and portrait displacement
a hard initial target; RawCull can instead complement the editor for difficult
technical comparisons.
[Cull workflow](https://learn.captureone.com/page/17/),
[Assisted Review introduction](https://www.captureone.com/en/explore-features/whats-new/16-8),
[current release overview](https://www.captureone.com/en/explore-features/whats-new) [C].

### Manual review, RAW inspection and local library tools

**Photo Mechanic** is the benchmark for working while ingest continues,
multi-card copying, metadata templates, renaming and fast preview review.
Measure RawCull's basic browsing and handoff against it before adding analysis
to every image. **FastRawViewer** emphasizes RAW-based exposure statistics,
focus inspection and converter handoff. RawCull must keep its temporary
rendered exposure view distinct from those RAW-data measurements.
[Photo Mechanic tour](https://home.camerabits.com/tour-photo-mechanic/),
[platform requirements](https://docs.camerabits.com/support/solutions/articles/48001080502-system-recommendations-compatibility) [P];
[FastRawViewer features and platforms](https://www.fastrawviewer.com/) [R].

**Excire Foto 2027** combines local semantic search, people and content
organization, scene grouping and image-quality selection. That overlaps
directly with RawCull's CLIP search and local AI pitch. RawCull's better
opportunity is focused selection with camera and region evidence, not a general
photo library.
[Excire Foto](https://excire.com/en/excire-foto/),
[platforms and current products](https://excire.com/en/) [E].

**digiKam** documents optional on-device models, face recognition, similarity
search and quality-based pick labels. Face recognition identifies people; it is
not blink or eye-sharpness assessment. **darktable** offers side-by-side culling
with zoom and pan, integrated with RAW editing. Both are real choices on Linux,
Mac and Windows, but neither documents the automatic best-of-burst workflow of
the specialist products.
[digiKam features](https://www.digikam.org/about/features/),
[platform documentation](https://www.digikam.org/documentation/faq/) [D];
[darktable culling](https://docs.darktable.org/usermanual/development/en/lighttable/lighttable-modes/culling/),
[downloads/platforms](https://www.darktable.org/install/) [T].

## Where RawCull can gain momentum

### 1. Get decisions into the editor

XMP interoperability is still the largest adoption blocker, and nothing changed
here between 3.4.0 and 3.4.9. Copying selected RAWs is useful, but decisions
must survive in Lightroom Classic, Capture One and other editors without being
rebuilt by hand. Every other improvement is worth less while the photographer
has to redo the cull in the editor.

### 2. Explain difficult wildlife and sports burst decisions

RawCull has camera AF evidence, subject masks, normalized detail scoring,
Close Up, frame marks and Review. The missing piece is bringing them together
on the frames being compared: which subject was measured, on which render,
where the AF point falls and why the result is uncertain.

A bird burst where the background is sharp but the bird is soft is the test
case. Show comparable subject crops, mask coverage and detail values, and
distinguish a missing eye assessment from an actual eye result. Keep the
photographer's preferred gesture even when another frame scores higher.
Narrative ranks wildlife sharpness and FilterPixel markets wildlife and sports
criteria, so the claim to make is **a faster, verifiable decision on difficult
bursts**, backed by photographer trials.

### 3. Make the first pass simple; keep deep analysis for shortlists

Use the existing burst ranking and burst AI assessment to fill conservative
**Keep**, **Review** and **Likely Reject** queues with explicit reasons and easy
overrides. Keep uncertain cases visible. Review's 1–8-image limit should stay an
escalation path; running a VLM on every photograph needs its own throughput and
quality justification. Target yield can follow once the queues are trusted, and
must not silently drop unique moments.

### 4. Add eye-state assessment for portraits and groups

Face crops exist; eye state does not. Narrative, Aftershoot, Adobe and Capture
One make closed-eye detection a baseline requirement for weddings and events.
Add a calibrated open/closed/unknown result per face, handle glasses, small
faces, profiles, occlusion and low light, and show each face in a group rather
than one average. Qwen observations are not a blink detector.

### 5. Earn trust through supported cameras and predictable performance

Publish a tested camera and format table that separates browsing, embedded
preview, RAW development, AF metadata and JPEG extraction. A long extension list
is less useful than knowing a specific camera workflow works. Keep browsing
responsive while models load or run, and show model size, setup progress,
cancellation and recovery. A Windows or Linux port would be far larger than any
item here because the app depends on Apple frameworks; XMP serves mixed-OS
workflows much sooner.

## Prioritized plan after 3.5.0

These are recommendations, not release commitments. Order reflects adoption
value first, then the risk carried over from the 3.4.9 refactoring. Effort is
relative and includes qualification, not only implementation.

| Rank | Work | Why now | Effort | Done when |
| --- | --- | --- | --- | --- |
| **1** | **XMP sidecar export and import of decisions** | Largest adoption gap; unchanged since 3.4.0 | Large | Lightroom Classic and Capture One round-trip; no loss of unrelated XMP; conflicts and failed writes visible per file |
| **2** | **Qualify the 3.4.9–3.5.0 consolidation: fix the open source findings, CI, lint baseline, Vision hang regression test, Review preset comparison** | The Vision gate has measured catalog results. CI and a photographic comparison of the new Review presets with the retired tabs are separate qualification work | Medium | CI runs lint and smoke tests on pull requests; Focus check/Describe/Full compared with the old tabs on 20 real photos and every difference decided |
| **3** | **Evidence on Close Up cards and an explained burst recommendation** | Turns existing measurements into the burst-decision differentiator | Medium | Each card shows AF and detail values with source, region and availability; incompatible values are withheld with a reason; the recommended frame explains itself |
| **4** | **Eye open/closed/unknown per detected face** | Closes the main portrait gap on top of the existing face strip and People Ranking | Medium–large | Per-face results across glasses, profiles, small faces and low light, with a measured false-closed rate |
| **5** | **Camera qualification table and performance baseline** | Makes product claims dependable before wider promotion | Ongoing, start small | Published per-camera matrix; cold/warm latency and peak memory for 500, 2,000 and 10,000 images |
| 6 | Conservative Keep / Review / Likely Reject queues | Makes analysis usable at shoot scale; builds on burst AI assessment | Medium–large | Lower total review time; every Likely Reject audited in a labelled sample; manual decisions never overwritten |
| 7 | Wildlife animal-eye validation (birds, deer) and subject proposals in Close Up | Current animal support is documented for cats and dogs only | Medium | Measured detection rate on real bird and wildlife bursts; manual fallback stays authoritative |
| 8 | Review presets over MCP; shared MCP IPC module | Extends the unique integration once the in-app presets are qualified | Small–medium | MCP clients can request Focus check; one shared module replaces duplicated helper sources |

**Recommended scope for the next version:** items 1–3, with 4 if time allows.
Items 5–8 can run alongside. The confirmed defects behind item 2 are listed under
[open source findings]({{< relref "/docs/update.md" >}}#open-source-findings).

### Scope for item 1: XMP exchange

The detailed P0 pages were retired; this is the scope to carry forward.

| First version | Deferred |
| --- | --- |
| Export chosen ratings and reject state to XMP sidecars beside the originals, with a preview of every file and value | Writing metadata into RAW files |
| Read existing sidecars on catalog open or on request, with an import preview | Background two-way sync and folder watching |
| Preserve unrelated XMP, including editor adjustments | RAW development settings exchange |
| Detect changes since the last exchange and show conflicts; never resolve by newest timestamp | Universal pick flags or colour labels |
| Copy RAW plus sidecar together in the rsync handoff | Burst winners, AI findings and caches in XMP |
| Qualified Lightroom Classic and Capture One procedures | Editing editor databases directly |

No AI recommendation becomes a rating because export was opened. A failed write
stays retryable and is never reported as handed off. A written sidecar does not
mean an open editor catalog has re-read it; document each editor's read step.

### Scope for item 3: unified burst evidence

1. Project existing AF and detail measurements onto the selected Close Up frames
   with region, render and algorithm revision, and show missing, loading, failed
   and stale states.
2. Define when two values are comparable (metric version, preprocessing, source
   class, region). Withhold incomparable values from ranking and say why.
3. Offer a subject-derived region from existing segmentation that the
   photographer can confirm or correct. A correction invalidates dependent
   evidence.
4. Only then send a Close Up shortlist to Review with frozen inputs, and mark the
   report stale when those inputs change.

### Not planned now

Full RAW editing, retouching, cloud delivery, a model marketplace and new or
alternative segmentation models. A new model is worth adding only for a measured
gain in quality, latency or memory over the current SAM 3 and non-model
baselines. Ingest backups, renaming and metadata templates remain a later
professional-workflow item.

## How to test the opportunity

Use the same labelled shoots in RawCull and selected competitors: birds and
wildlife, sports, portraits and groups, landscapes and low light. Test supported
camera and compression combinations, embedded versus developed renders,
difficult subjects and intentional creative blur. Let photographers record
acceptable alternatives rather than forcing one winner.

Measure end-to-end time from opening a shoot to accepted editor handoff,
including setup, uploads where applicable, review and corrections. Report
first-use model preparation separately from warm use. Run 500-, 2,000- and
10,000-image catalogs and record hardware, storage, app versions, settings,
failures, peak memory and tail latency.

For selection quality, measure missed keepers, preferred-frame agreement, manual
overrides and time spent inspecting faces or subject crops. Audit every Likely
Reject in the labelled sample. For Review, separate valid structured output from
visually correct observations and useful comparisons. For handoff, check ratings
and unrelated metadata after a round trip through each target editor.

The commercial hypothesis is that photographers will adopt RawCull when it
**reduces difficult review time while preserving control and dependable editor
handoff**. Local processing supports that promise; it does not replace measured
workflow value.
