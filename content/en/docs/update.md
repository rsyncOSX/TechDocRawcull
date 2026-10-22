---
title: Documentation Review Record
description: Reviewed source baseline, page dispositions, verification limits and maintenance triggers.
weight: 95
lastmod: 2026-10-22
---

# Documentation Review Record

## Source baseline — 22 October 2026

This review covers all **36 existing Markdown pages** under `content/en`, plus
three new pages. It reconciles implementation changes since the preceding
RawCull baseline `23de7bec3063cab0f8466e8367921841c5ab5a1d` with the latest
checked-in source available in the local repositories:

| Repository | Reviewed commit / version | Scope |
| --- | --- | --- |
| [RawCull](https://github.com/rsyncOSX/RawCull/tree/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91) | `b46501739f6a09c0e2df352fc3ed2bf8e10a0e91`; 3.3.5, build 425; `version-3.3.5` | Application, focused tests, project metadata, dependency lockfile and recent commit diff |
| [RawParserKit](https://github.com/rsyncOSX/RawParserKit/tree/07801a34a82d7720d301a80724c36a5b8c9f1d6c) | 1.3.2; `07801a34a82d7720d301a80724c36a5b8c9f1d6c` | Actual RawCull dependency pin, including generic-format additions |
| [RawBrowse](https://github.com/rsyncOSX/RawBrowse/tree/5815fd64ca02185c1ca6300311794a3ecacf6ec8) | `5815fd64ca02185c1ca6300311794a3ecacf6ec8` | Companion API guide, source-link repair and changes since October 17 |

The [package overview]({{< relref "packages/_index.md" >}}) records every RawCull
resolved dependency. PhotoAnalysisKit 1.3.1, RawCullCore 1.1.2 and PhotoAIKit 1.0.0
remain at their preceding pins. Their package algorithms are not rewritten as
if a UI refactor changed them. Package walkthroughs explicitly retain earlier
audit scopes where applicable and add current integration/delta sections.

Current implementation links use immutable commits. Model-preparation recipes,
dated cache archaeology and historical evaluation references retain their
original pins. A repository branch or a separately newer sibling checkout is
not a substitute for the application's resolved dependency. No remote fetch,
release publication or installed-model qualification is implied by this review.

## Structural decisions

The new [Viewer Architecture]({{< relref "viewer-architecture.md" >}}) guide
explains session state, task identity, shared geometry and keyboard ownership
across screens. The new [RAW Formats and Exposure Inspection]({{< relref
"raw-inspection.md" >}}) guide separates registry admission, actual OS decoding,
export, development and display-referred inspection evidence.

The large RawCull API article is split into an
[application walkthrough]({{< relref "apidocs/rawcullapidoc.md" >}}) and an
[internal Swift method reference]({{< relref "apidocs/rawcull-internal-api.md" >}}).
The old main-reference section remains as a forwarding section. Existing page
names, the concurrency slug and the RawBrowse filename are retained to preserve
published entry points.

Important corrections include the synthetic Single Images ID −1 versus real
persisted group states, deletion of Combined evidence under Delete Cache,
complete preference clearing after Objects focus abstention, and the histogram's
any-channel versus clipping overlay's all-channel predicates. Historical model
results and roadmap research are identified as dated rather than presented as
qualification of this build.

The former accumulated update plan is available in
[the preceding documentation revision](https://github.com/rsyncOSX/TechDocRawcull/blob/b7ed15c667fc13a6db8bbf7b438a505f4810e776/content/en/docs/update.md).
It is historical context, not the current outstanding-work list.

## Page-by-page disposition

| Page | Review result |
| --- | --- |
| [_index.md]({{< relref "/_index.md" >}}) | Clarified that this site teaches how RawCull is built; retained the landing layout. |
| [about/index.md]({{< relref "/about/index.md" >}}) | Preserved personal/project background; corrected notarization and automatic-document-freshness wording. |
| [search.md]({{< relref "/search.md" >}}) | Retained search layout; no application behavior is described. |
| [site.md]({{< relref "/site.md" >}}) | Removed the Docsy example-team build placeholder; linked source and review provenance. |
| [docs/_index.md]({{< relref "/docs/_index.md" >}}) | Updated baseline, source map and reading order; linked the new architecture guides. |
| [docs/thumbnail.md]({{< relref "/docs/thumbnail.md" >}}) | Added generic registry admission and current viewer ownership; distinguished normal development from inspection. |
| [docs/viewer-architecture.md]({{< relref "/docs/viewer-architecture.md" >}}) | New end-to-end guide to sessions, async publication, rendering, geometry and keyboard ownership. |
| [docs/raw-inspection.md]({{< relref "/docs/raw-inspection.md" >}}) | New guide to format admission, generic extractors, development/export boundaries and temporary EV inspection. |
| [docs/cache.md]({{< relref "/docs/cache.md" >}}) | Documented combined cleanup and the deletion of stored review evidence; separated the burst session cache. |
| [docs/cache-accounting.md]({{< relref "/docs/cache-accounting.md" >}}) | Retained the dated commit walkthrough; wrapper implementation and package boundary are unchanged. |
| [docs/memorypressure.md]({{< relref "/docs/memorypressure.md" >}}) | Refreshed source references; removed the contradictory pressure-event-counter assertion. |
| [docs/concurrency.md]({{< relref "/docs/concurrency.md" >}}) | Added viewer task/controller owners and explicit inspection-render placement; retained actor/continuation invariants. |
| [docs/focusmask.md]({{< relref "/docs/focusmask.md" >}}) | Updated app presentation ownership; retained the unchanged PhotoAnalysisKit measurement boundary. |
| [docs/detailsfocusmask.md]({{< relref "/docs/detailsfocusmask.md" >}}) | Retained package stages at the unchanged pin; added the new publication/geometry boundary. |
| [docs/detailsharpnessscoring.md]({{< relref "/docs/detailsharpnessscoring.md" >}}) | Retained formulas at the unchanged PhotoAnalysisKit pin; refreshed app implementation links. |
| [docs/burstgroup.md]({{< relref "/docs/burstgroup.md" >}}) | Documented synthetic Single Images workspace, actual persisted states and extracted dashboard/workspace components. |
| [docs/filereadandwrite.md]({{< relref "/docs/filereadandwrite.md" >}}) | Added Saved Files size/reset path, review/cache deletion order and inspection/export distinctions. |
| [docs/security.md]({{< relref "/docs/security.md" >}}) | Added inspection grant retention and links to current privacy-manifest metadata/tests. |
| [docs/heavy.md]({{< relref "/docs/heavy.md" >}}) | Added generic extractor bridges and the separate serialized native exposure renderer. |
| [docs/sonymakernoteparser.md]({{< relref "/docs/sonymakernoteparser.md" >}}) | Updated parser pin; explained generic EXIF fallback without claiming new vendor MakerNote support. |
| [docs/newfeatures.md]({{< relref "/docs/newfeatures.md" >}}) | Preserved dated research; marked broader-format and exposure-inspection implementation deltas. |
| [docs/pushpull.md]({{< relref "/docs/pushpull.md" >}}) | Retained documentation-repository workflow guidance; it does not describe the app repository history. |
| [docs/update.md]({{< relref "/docs/update.md" >}}) | Replaced the accumulated historical backlog with this baseline, disposition and maintenance record. |
| [docs/ai/_index.md]({{< relref "/docs/ai/_index.md" >}}) | Updated baseline/navigation and replaced stale test-release claims with dated evidence guidance. |
| [docs/ai/airuntime.md]({{< relref "/docs/ai/airuntime.md" >}}) | Added extracted model/download presentation boundaries while retaining stable feature/provider ownership. |
| [docs/ai/aiinrawcull.md]({{< relref "/docs/ai/aiinrawcull.md" >}}) | Explained typed Objects sanitation, complete preference clearing and current preview ownership. |
| [docs/ai/aicombined.md]({{< relref "/docs/ai/aicombined.md" >}}) | Reconfirmed v22/per-stage compatibility; added shared input policy and saved-review deletion behavior. |
| [docs/ai/aidiagnostics.md]({{< relref "/docs/ai/aidiagnostics.md" >}}) | Replaced the removed-report dependency and added presentation regression entry points. |
| [docs/ai/rawcullai.md]({{< relref "/docs/ai/rawcullai.md" >}}) | Retained reproducible weight/exporter pins; distinguished historical preparation from current installation and qualification. |
| [docs/ai/rawbrowseai.md]({{< relref "/docs/ai/rawbrowseai.md" >}}) | Retained the pinned companion-app preparation recipe and clarified review/qualification limits. |
| [docs/packages/_index.md]({{< relref "/docs/packages/_index.md" >}}) | Reconciled all resolved pins with the current app lockfile; RawParserKit advances to 1.3.2. |
| [docs/packages/rawparserkit.md]({{< relref "/docs/packages/rawparserkit.md" >}}) | Preserved the scoped original audit and added a linked 1.3.2 generic-format delta. |
| [docs/packages/photoanalysiskit.md]({{< relref "/docs/packages/photoanalysiskit.md" >}}) | Retained package architecture at the unchanged 1.3.1 pin; refreshed host links. |
| [docs/packages/rawcullcore.md]({{< relref "/docs/packages/rawcullcore.md" >}}) | Retained pure models/grouping/ranking/histogram architecture at the unchanged 1.1.2 pin; refreshed host links. |
| [docs/packages/photoaikit.md]({{< relref "/docs/packages/photoaikit.md" >}}) | Retained explicitly scoped package architecture at the unchanged app pin; refreshed host links. |
| [docs/apidocs/_index.md]({{< relref "/docs/apidocs/_index.md" >}}) | Added the split internal API guide and links to the viewer/RAW guides. |
| [docs/apidocs/rawcullapidoc.md]({{< relref "/docs/apidocs/rawcullapidoc.md" >}}) | Kept the application journey, setup and recovery; moved method tables into a focused reference. |
| [docs/apidocs/rawcull-internal-api.md]({{< relref "/docs/apidocs/rawcull-internal-api.md" >}}) | New split-out internal method reference plus current viewer/inspection/persistence entry points. |
| [docs/apidocs/rabrowsweapidoc.md]({{< relref "/docs/apidocs/rabrowsweapidoc.md" >}}) | Fixed site-relative code links; documented deferred per-folder RAW 9 probing and its separate dependency baseline. |

## Verification and limits

Static checks cover TOML/YAML front-matter syntax, unique page routes,
balanced fenced blocks, internal page links and `relref` targets. GitHub source
paths are checked with local Git objects at their stated commits, including
historical revisions. This confirms repository path identity; it does not test
remote HTTP availability or external vendor/Hugging Face services.

Source diffs and relevant test fixtures were inspected to explain the changed
behavior. **Hugo was not compiled**, as requested. Application/package tests,
model conversion, installed-model inference and photographic/performance
qualification were not run by this documentation pass. Referenced tests are
executable contracts to consult, not newly reported passing runs.

## Maintain the learning path

When app code changes, start with its commit diff and the resolved lockfile.
Update the owning page and its overview together. Explain the trigger, owner,
input, result, cancellation/publication guard, persistence identity and failure
path before listing low-level APIs. Link the implementation and the test that
protects the contract. Preserve the distinction between supported structure and
photographic correctness.

Revisit the viewer guide when screen/task/controller ownership changes; the RAW
guide when formats, decoding, histogram/clipping or inspection policy changes;
the persistence/cache pages when cleanup semantics change; and the AI pages when
providers, contracts, response schemas or stored-run compatibility change.
Advance package pins only from the app lockfile, and qualify model-release
recipes independently from normal application documentation updates.
