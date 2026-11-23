---
title: Documentation Review Record
description: Build 466 source review, per-page dispositions, and the incremental documentation baseline.
weight: 95
lastmod: 2026-11-23
reviewed_commit: "0513a30e4567b4b5e3093e10791d49c86ecfe7e6"
reviewed_version: "3.4.9"
reviewed_build: 466
reviewed_on: "2026-11-23"
review_scope: "Reconciled the current page inventory, changed pins, source findings and validation record."
---

# Documentation Review Record

## Reviewed source

On **23 November 2026** the review compared **RawCull 3.4.9 build 466**, commit [0513a30e](https://github.com/rsyncOSX/RawCull/commit/0513a30e4567b4b5e3093e10791d49c86ecfe7e6), with the previous build 462 baseline, [a0c72d11](https://github.com/rsyncOSX/RawCull/commit/a0c72d11b6dea1f409542faf90f76fba43cdb0f5). The clean application checkout was on `version-3.4.9`. The local `main` branch also contains the reviewed commit. Build 466 identifies the Xcode project configuration. The local release tag points to an earlier commit of that version.

The comparison covered 181 added, modified or deleted paths when renames are counted as deletion and addition. The site has 37 technical pages and four site pages. The previous inventory still listed four retired pages. Review and diagnostics are covered by the AI guides, and the XMP and unified burst evidence proposals are in the roadmap.

## Findings that affect readers

- **Review.** The current entry point accepts one to eight selected or tagged photos. Focus check needs SAM 3. Describe and Full need Qwen. The inspector links findings to regions, and the separate Review Record window follows the selection. Acting on a saved result requires a matching live file. [Review guide]({{< relref "/docs/ai/aiinrawcull.md" >}})
- **Burst assessment.** The burst list can assess the ranked pair from each eligible group. Completed results with usable findings appear in the session’s AI Assessments window. An MCP follow-up publishes through a separate authorized job. [Burst groups]({{< relref "/docs/burstgroup.md" >}}) · [MCP]({{< relref "/docs/mcp.md" >}})
- **Vision scheduling.** PhotoAIKit 3.1.0 forwards feature-print work through an injected serializer, and RawCull connects it to PhotoAnalysisKit’s gate. The 275-photo comparison covers the gate change. PhotoAnalysisKit 1.4.1 separately adds focus-engine context reuse. PhotoEvidenceKit’s repository URL changed at the same revision. [Performance]({{< relref "/docs/performance.md" >}}) · [Package snapshot]({{< relref "/docs/packages/_index.md" >}})
- **Developer commands.** The Makefile requires a clean, version-tagged HEAD for release preflight. The release checklist uploads the candidate for testing through TestFlight. A stale README example still names `releaseaiobjectstest`. The Makefile defines the current Review probes. [Developer guide]({{< relref "/docs/apidocs/rawcullapidoc.md" >}})

## Validation and limits

The documentation site built with Hugo. Rendered internal page links and fragment targets were checked, and immutable GitHub source paths were resolved against their named revisions in the local repositories. The application version and build were checked in the Xcode project. The package snapshot and review manifest were compared with the app’s lockfile.

This was a source and documentation review. The app UI, Swift test suites, installed models, TestFlight upload, photographic benchmarks and vendor comparisons were not rerun. The performance guide attributes measurements to the original source-project runs. The model recipe and competitor comparison retain their original dates.

## Page dispositions

| Page | Review outcome |
| --- | --- |
| [_index.md]({{< relref "/docs/_index.md" >}}) | Updated the application map, Review entry point, smoke count and source baseline. |
| [ai/_index.md]({{< relref "/docs/ai/_index.md" >}}) | Replaced the tab tour with task, input and storage choices for Review, burst assessments and MCP. |
| [ai/aiinrawcull.md]({{< relref "/docs/ai/aiinrawcull.md" >}}) | Rebuilt the Review guide around preset requirements, registered evidence, decision guards, outlines and resume. Preserved the CLIP walkthrough and a link to the historical evaluation. |
| [ai/airuntime.md]({{< relref "/docs/ai/airuntime.md" >}}) | Traced model activation, live backend admission, Qwen generation, the shared lease and Vision scheduling. |
| [ai/rawcullai.md]({{< relref "/docs/ai/rawcullai.md" >}}) | Corrected the app pin and replaced the retired diagnostic runner. The dated exporter and model recipe remains historical. |
| [apidocs/_index.md]({{< relref "/docs/apidocs/_index.md" >}}) | Updated the developer reading route for Review, batch assessment and release checks. |
| [apidocs/rawcull-internal-api.md]({{< relref "/docs/apidocs/rawcull-internal-api.md" >}}) | Replaced removed controller calls with the current Review, batch plan and culling action interfaces. |
| [apidocs/rawcullapidoc.md]({{< relref "/docs/apidocs/rawcullapidoc.md" >}}) | Updated launch code, Review flow, smoke inventory, model probes and tag-to-TestFlight release procedure. |
| [burstgroup.md]({{< relref "/docs/burstgroup.md" >}}) | Documented eligibility, preview inputs, rubric, cancellation and session lifetime for Assess All Bursts. Updated mask lookup. |
| [cache-accounting.md]({{< relref "/docs/cache-accounting.md" >}}) | Retained the owned-eviction-delegate walkthrough. The cache bookkeeping implementation has no relevant delta. |
| [cache.md]({{< relref "/docs/cache.md" >}}) | Distinguished obsolete Objects cache cleanup from retained Review masks and reports. |
| [closeups.md]({{< relref "/docs/closeups.md" >}}) | Checked manual crop and AF behavior and documented scheduling of automatic face and animal detection. |
| [concurrency.md]({{< relref "/docs/concurrency.md" >}}) | Replaced the temporary processor cap with the implemented Vision gate, cancellation semantics and quality limits. |
| [detailsfocusmask.md]({{< relref "/docs/detailsfocusmask.md" >}}) | Updated viewer ownership and distinguished the calibrated focus overlay from a retained Review subject mask. |
| [detailsharpnessscoring.md]({{< relref "/docs/detailsharpnessscoring.md" >}}) | Corrected effective concurrency for embedded previews and RAW demosaics. The formula audit retains its original revision. |
| [filereadandwrite.md]({{< relref "/docs/filereadandwrite.md" >}}) | Updated Review inspection and distinguished in-memory burst entries from shared MCP records. |
| [focusmask.md]({{< relref "/docs/focusmask.md" >}}) | Identified the current package pin and removed the deleted AI preview helper from the viewer map. |
| [heavy.md]({{< relref "/docs/heavy.md" >}}) | Replaced retired Deep Review paths with the scoring, Review source and outline renderers that reuse Core Image contexts. |
| [mcp.md]({{< relref "/docs/mcp.md" >}}) | Checked helper schemas and controller admission. Documented shared inference and the two result lifetimes. |
| [memorypressure.md]({{< relref "/docs/memorypressure.md" >}}) | Retained the pressure-event and cache-budget guide. Review memory eligibility is documented with the presets. |
| [newfeatures/_index.md]({{< relref "/docs/newfeatures/_index.md" >}}) | Checked the roadmap destination and its distinction between implemented features and proposals. |
| [newfeatures/newfeatures.md]({{< relref "/docs/newfeatures/newfeatures.md" >}}) | Updated source and tag evidence, assessment scope and Vision qualification. Competitor evidence remains dated 5 November. |
| [packages/_index.md]({{< relref "/docs/packages/_index.md" >}}) | Reconciled all 24 app pins and distinguished the helper lockfile and earlier package snapshots. |
| [packages/package-modules.md]({{< relref "/docs/packages/package-modules.md" >}}) | Confirmed the PhotoEvidenceKit revision and library products. The repository transport change leaves the module example intact. |
| [packages/photoaikit.md]({{< relref "/docs/packages/photoaikit.md" >}}) | Checked the 3.1.0 serializer against its resolved source. Distinguished current integration from the October audit. |
| [packages/photoanalysiskit.md]({{< relref "/docs/packages/photoanalysiskit.md" >}}) | Checked 1.4.0 queue admission and the 1.4.1 shared focus-engine context at the resolved revision. |
| [packages/photoevidencekit.md]({{< relref "/docs/packages/photoevidencekit.md" >}}) | Verified the HTTPS repository change at the same 1.1.5 revision. |
| [packages/rawcullcore.md]({{< relref "/docs/packages/rawcullcore.md" >}}) | Confirmed the app pin and distinguished it from the original domain-model walkthrough. |
| [packages/rawparserkit.md]({{< relref "/docs/packages/rawparserkit.md" >}}) | Confirmed 1.3.3 at the recorded revision. The change to Review consumers does not change parser dispatch. |
| [performance.md]({{< relref "/docs/performance.md" >}}) | Added the source project’s 275-ARW gate comparison, stress run, Release sharpness evidence and limits. |
| [pushpull.md]({{< relref "/docs/pushpull.md" >}}) | Retained the documentation-repository Git workflow. App release tagging is covered in the developer guide. |
| [raw-inspection.md]({{< relref "/docs/raw-inspection.md" >}}) | Checked viewer changes against the guide. Review rendering and outline changes leave the zoom exposure policy intact. |
| [security.md]({{< relref "/docs/security.md" >}}) | Traced the separate session-catalog and MCP-grant access paths used by the assessment window. |
| [sonymakernoteparser.md]({{< relref "/docs/sonymakernoteparser.md" >}}) | Confirmed the current parser pin and retained the historical MakerNote walkthrough. |
| [thumbnail.md]({{< relref "/docs/thumbnail.md" >}}) | Updated the Review consumer name and checked grid/preload admission against the source delta. |
| [update.md]({{< relref "/docs/update.md" >}}) | Reconciled the current page inventory, changed pins, source findings and validation record. |
| [viewer-architecture.md]({{< relref "/docs/viewer-architecture.md" >}}) | Updated outline lookup, Review geometry, inspector navigation and the source baseline. |

The four site pages cover the home page, About, site information and search. The home and About text was revised for platform and distribution accuracy. Their individual review records are in the manifest.

## Next review

Run the read-only selector from the documentation repository:

```sh
python3 scripts/review_docs.py --source /path/to/RawCull
```

For a committed target other than the checkout's HEAD:

```sh
python3 scripts/review_docs.py --source /path/to/RawCull --target COMMIT
```

The selector reads `data/documentation-review.json`. It compares committed paths,
flags staged/unstaged/untracked source paths when reviewing HEAD, checks resolved
pins, and detects documentation edits using recorded SHA-256 hashes. Each page
has explicit source-path patterns and package identities in that file. Immutable
source references also contribute exact-path triggers.

A report is a **review candidate list**, not a semantic approval. It never edits
files or advances the baseline. Unmapped source changes are printed prominently
and return exit status 2; inspect them and extend the map before deciding which
pages can be skipped. If source ownership moves across subsystems, review the map
itself. Externally dated research, recipes and historical measurements are not
silently requalified by an empty app diff.

For a manual comparison:

```sh
git -C /path/to/RawCull log --oneline 0513a30e4567b4b5e3093e10791d49c86ecfe7e6..HEAD
git -C /path/to/RawCull diff --stat 0513a30e4567b4b5e3093e10791d49c86ecfe7e6..HEAD
```

After reviewing the candidate pages, record the new actual commit, project
version/build, full lockfile pins, per-page dispositions and document hashes in
`data/documentation-review.json`; update this page and the documentation index.
Advance a page's `reviewed_*` front matter only after checking its relevant delta.
An unchanged subsystem can receive a delta-verification marker while preserving
its content `lastmod` and historical audit links. Never advance the baseline just
because the selector ran or the site rebuilt.
