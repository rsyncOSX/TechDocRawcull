---
title: Documentation Review Record
description: Build 469 source review, per-page dispositions, and the incremental documentation baseline.
weight: 95
lastmod: 2026-11-25
reviewed_commit: "5169ffd3487fe4ddc005d511fffa38172657d703"
reviewed_version: "3.5.0"
reviewed_build: 469
reviewed_on: "2026-11-25"
review_scope: "Reconciled the 3.5.0 delta, stale-formula findings, open source findings and validation limits."
---

# Documentation Review Record

## Reviewed source

On **25 November 2026** the review compared **RawCull 3.5.0 build 469**, commit [5169ffd3](https://github.com/rsyncOSX/RawCull/commit/5169ffd3487fe4ddc005d511fffa38172657d703), with the previous build 466 baseline, [0513a30e](https://github.com/rsyncOSX/RawCull/commit/0513a30e4567b4b5e3093e10791d49c86ecfe7e6). The application checkout was clean, on `version-3.5.0`. `main` contains the reviewed commit. All 24 package pins are unchanged.

The source delta covers 33 paths. The review went further than the delta. Every page with a source link to an older revision was compared with the current file, because a page can be out of date without any recent commit touching its subject. That found most of the errors below.

The site has 38 technical pages and four site pages. `ai/full-review.md` is now in the review manifest.

## Findings that affect readers

- **Sharpness formula.** The scoring guide described scalar algorithm 4. The app ships algorithm 7, where a frame without a detected subject keeps its global score, the AF region is shifted inside the frame, and missing measurements no longer count as zero. [Detailed Sharpness Scoring]({{< relref "/docs/detailsharpnessscoring.md" >}}#what-changed-since-algorithm-4)
- **Focus-mask threshold.** The mask guide described a threshold that adapts to each image. The current cutoff is fixed. [Detailed Focus Mask]({{< relref "/docs/detailsfocusmask.md" >}})
- **AF coordinates.** AF points are rotated to the upright image once, at scan time. Several pages said each consumer does it. [Metadata parsers]({{< relref "/docs/sonymakernoteparser.md" >}})
- **Burst review.** The target order follows capture time. A high-confidence recommendation still needs review. No screen sets a manual winner. [Burst Groups]({{< relref "/docs/burstgroup.md" >}})
- **Review in 3.5.0.** Focus check is preselected, the button names the run, and the photo has focus and magnifier layers. [AI Models]({{< relref "/docs/ai/aiinrawcull.md" >}})
- **AI runtime.** An earlier edit removed most of the object-graph walkthrough. It is restored from current source, including the lease and the generation gate. [AI Runtime]({{< relref "/docs/ai/airuntime.md" >}})

## Open source findings

These are limits in the application source at build 469. They are listed so that the guides do not describe intended behavior as actual behavior. RC numbers refer to the app's own [3.4.9 engineering review](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/Docs/review349.md). Every item was checked by reading the current source. None was reproduced at run time in this review.

| ID | What happens | Where | The rule it breaks |
| --- | --- | --- | --- |
| RC-02 | Reviewed and deferred marks share the burst snapshot. Its filename is the Base64 of the catalog path, which is too long for paths of about 188 bytes or more. The failed save of a mark is discarded, and Delete Cache removes the marks. | [BurstAnalysisCache](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Intelligence/Persistence/BurstAnalysisCache.swift), [BurstAnalysisCoordinator](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Intelligence/BurstAnalysis/BurstAnalysisCoordinator.swift) | Keep decisions apart from derived data, and report failed saves |
| RC-03 | Reloading one comparison pane can discard a bulk load that other panes still need. | [ComparisonSessionModel](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Model/ViewModels/ComparisonSessionModel.swift) | Match the unit of invalidation to the unit of publication |
| RC-04 | A late focus result can restore the previous group's images. | [ComparisonSessionModel](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Model/ViewModels/ComparisonSessionModel.swift) | Publish only the fields the work produced |
| RC-05 | The rsync details table drops its last 11 records, including failure diagnostics. | [DetailsView](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Views/OutputViews/DetailsView.swift) | Filter by meaning, not by count |
| RC-06 | The burst workspace builds a catalog-wide lookup several times per update. The cost is unmeasured. | [BurstCullingWorkspaceView](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Views/ComparisonGridView/BurstCullingWorkspaceView.swift) | Derive once, then reuse |
| RC-01 | A thumbnail request for size 0 could be answered by a cached 200 px image. No caller passes 0. | [ThumbnailLoader](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Actors/ThumbnailLoader.swift) | Resolve defaults before choosing a path |
| RC-07 | The similarity comparator orders the anchor before itself. | [CatalogController+Loading](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Model/ViewModels/CatalogController+Loading.swift) | A sort predicate must be a strict weak ordering |
| DOC-01 | `BurstBatchAssessment.run` and the MCP follow-up refresh models while holding the AI lease, if Qwen has no identity yet. The refresh invalidates the lease owner, which is the caller, so the preparation cancels itself. | [BurstBatchAssessment](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Model/ViewModels/BurstBatchAssessment.swift), [MCPAnalysisController+FollowUp](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Main/MCPAnalysisController+FollowUp.swift), [RawCullAIModelRuntime](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Intelligence/Composition/RawCullAIModelRuntime.swift) | Do not wait for a resource you hold |
| DOC-02 | `FocusMaskAnalysisResolutionPolicy.calibrationScaled` is tested but no view calls it. A mask drawn from an image of another size uses a threshold calibrated near 1616 px. | [FocusMaskTypes](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Model/ViewModels/FocusandSharpness/FocusMaskTypes.swift) | A threshold is valid only at the scale where it was measured |
| DOC-03 | The subject-mask stores, repository and segmentation service are rebuilt with the SAM provider, and no feature reads them. `upsertBurstWinnerOverride` has no app caller. | [RawCullAIModelRuntime](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Intelligence/Composition/RawCullAIModelRuntime.swift), [CullingModel](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Model/ViewModels/CullingModel.swift) | Remove or reconnect what a retired feature left behind |
| DOC-04 | Several labels still say “Deep Review” or “Combined Review”, for example in AI settings and the subject-outline help. | [AISettingsTab](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Views/Settings/AISettingsTab.swift), [SubjectOutlineControlsView](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/RawCull/Views/FocusPeek/SubjectOutlineControlsView.swift) | Rename visible text together with the feature |

## Validation and limits

The review ran scripts over all pages. They checked that every immutable GitHub source link resolves in the local repositories, that every linked file is identical to the current revision except for deliberately historical links, that code-formatted Swift names exist in current source, and that excerpts labelled as source match it. Line anchors in the Full Review guide were compared with the linked lines. Internal links and heading anchors were checked against the content files.

The site was not built with Hugo in this review. The app UI, Swift test suites, installed models, TestFlight upload and benchmarks were not run. Historical links remain in the performance guide, the model recipe and one viewer design note, because those documents were removed from the app repository. Competitor research keeps its date, 5 November 2026.

## Page dispositions

| Page | Review outcome |
| --- | --- |
| [_index.md]({{< relref "/docs/_index.md" >}}) | Moved the baseline to 3.5.0 build 469, added the 3.5.0 change table and a reading route to the open findings. |
| [ai/_index.md]({{< relref "/docs/ai/_index.md" >}}) | Updated the Review entry for the preselected Focus check. |
| [ai/aiinrawcull.md]({{< relref "/docs/ai/aiinrawcull.md" >}}) | Corrected the default preset, run controls and CLIP uses. Added photo layers, the preset contract, depth table, model inventory and source catalog. |
| [ai/airuntime.md]({{< relref "/docs/ai/airuntime.md" >}}) | Rebuilt topology, construction order, configuration apply, lease and gate, isolation, stale-result and fallback sections from current source. |
| [ai/full-review.md]({{< relref "/docs/ai/full-review.md" >}}) | Rechecked every source anchor at build 469 and updated the preset control and run button. |
| [ai/rawcullai.md]({{< relref "/docs/ai/rawcullai.md" >}}) | Updated the current build reference. The dated exporter and model recipe remains historical. |
| [apidocs/_index.md]({{< relref "/docs/apidocs/_index.md" >}}) | Checked the reading route. |
| [apidocs/rawcull-internal-api.md]({{< relref "/docs/apidocs/rawcull-internal-api.md" >}}) | Corrected scan failure, comparison entry and AF adapter contracts. Added frame marks and assessment navigation. |
| [apidocs/rawcullapidoc.md]({{< relref "/docs/apidocs/rawcullapidoc.md" >}}) | Updated test commands, scan failure handling, Review start and troubleshooting for build 469. |
| [burstgroup.md]({{< relref "/docs/burstgroup.md" >}}) | Corrected target order, review-state rule, queue rules, R and P keys and the removed manual-pick action. Added frame marks, reassess confirmation and persistence limits. |
| [cache-accounting.md]({{< relref "/docs/cache-accounting.md" >}}) | Reread the walkthrough against unchanged source. Only source links moved. |
| [cache.md]({{< relref "/docs/cache.md" >}}) | Documented snapshot key checks, digest failure, face-evidence lifetime and the review marks that Delete Cache removes. |
| [closeups.md]({{< relref "/docs/closeups.md" >}}) | Corrected AF orientation, the multi-frame detection strip and the decision controls. |
| [concurrency.md]({{< relref "/docs/concurrency.md" >}}) | Added the detachedCancellable walkthrough, lease waiters and the stale-publication example. Corrected actor and guard tables. |
| [detailsfocusmask.md]({{< relref "/docs/detailsfocusmask.md" >}}) | Rewrote for PhotoAnalysisKit 1.4.1: fixed threshold, capture fallbacks, gate order and calibration scale. |
| [detailsharpnessscoring.md]({{< relref "/docs/detailsharpnessscoring.md" >}}) | Rewrote the formula for scalar algorithm 7 and added a table of changes since algorithm 4. |
| [filereadandwrite.md]({{< relref "/docs/filereadandwrite.md" >}}) | Corrected copy startup, artifact folders, the unused mask cache and Delete Cache scope. Added the rsync detail limit. |
| [focusmask.md]({{< relref "/docs/focusmask.md" >}}) | Moved to PhotoAnalysisKit 1.4.1 descriptors, calibration source and shared context. |
| [heavy.md]({{< relref "/docs/heavy.md" >}}) | Corrected which image work uses detachedCancellable and moved parser links to 1.3.3. |
| [mcp.md]({{< relref "/docs/mcp.md" >}}) | Checked tool flow against unchanged helper sources and moved the source map to build 469. |
| [memorypressure.md]({{< relref "/docs/memorypressure.md" >}}) | Checked limits against source and documented that repeated warnings compound. |
| [newfeatures/_index.md]({{< relref "/docs/newfeatures/_index.md" >}}) | Updated the destination for 3.5.0. |
| [newfeatures/newfeatures.md]({{< relref "/docs/newfeatures/newfeatures.md" >}}) | Recorded the 3.5.0 delta, removed the manual-winner claim and kept the ranked plan. Competitor evidence remains dated 5 November. |
| [packages/_index.md]({{< relref "/docs/packages/_index.md" >}}) | Confirmed all 24 pins, corrected boundary types and removed superseded snapshots. |
| [packages/package-modules.md]({{< relref "/docs/packages/package-modules.md" >}}) | Moved the worked example to the resolved 1.1.5 manifest. |
| [packages/photoaikit.md]({{< relref "/docs/packages/photoaikit.md" >}}) | Audited 3.1.0, corrected the dependency diagram and added serializer, Qwen and instance-segmentation sections. |
| [packages/photoanalysiskit.md]({{< relref "/docs/packages/photoanalysiskit.md" >}}) | Audited 1.4.1: capture fallbacks, fixed threshold, descriptor 2/7, Vision queue and calibration scale. |
| [packages/photoevidencekit.md]({{< relref "/docs/packages/photoevidencekit.md" >}}) | Audited 1.1.5: device-pixel scale and owned detected-face crops. |
| [packages/rawcullcore.md]({{< relref "/docs/packages/rawcullcore.md" >}}) | Audited 1.1.5, which has the same sources as 1.1.2, and corrected the saliency rule. |
| [packages/rawparserkit.md]({{< relref "/docs/packages/rawparserkit.md" >}}) | Audited 1.3.3, added the generic conformer to the main walkthrough and the host orientation rule. |
| [performance.md]({{< relref "/docs/performance.md" >}}) | Stated what 3.5.0 leaves unmeasured. Recorded measurements are unchanged. |
| [pushpull.md]({{< relref "/docs/pushpull.md" >}}) | Retained the documentation-repository Git workflow. |
| [raw-inspection.md]({{< relref "/docs/raw-inspection.md" >}}) | Checked renderer, registry and session against source at build 469. |
| [security.md]({{< relref "/docs/security.md" >}}) | Corrected copy access ownership and added the MCP bookmark pattern. |
| [sonymakernoteparser.md]({{< relref "/docs/sonymakernoteparser.md" >}}) | Moved to 1.3.3 and explained sensor-to-upright AF conversion. |
| [thumbnail.md]({{< relref "/docs/thumbnail.md" >}}) | Corrected size resolution, AF orientation, loader requirements and test references. |
| [update.md]({{< relref "/docs/update.md" >}}) | Reconciled the 3.5.0 delta, stale-formula findings, open source findings and validation limits. |
| [viewer-architecture.md]({{< relref "/docs/viewer-architecture.md" >}}) | Replaced the removed Objects screen, added Review layers, the assessment window and the comparison publication gap. |

The four site pages cover the home page, About, site information and search. They were checked and have no relevant delta. Their records are in the manifest.

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
git -C /path/to/RawCull log --oneline 5169ffd3487fe4ddc005d511fffa38172657d703..HEAD
git -C /path/to/RawCull diff --stat 5169ffd3487fe4ddc005d511fffa38172657d703..HEAD
```

After reviewing the candidate pages, record the new actual commit, project
version/build, full lockfile pins, per-page dispositions and document hashes in
`data/documentation-review.json`; update this page and the documentation index.
Advance a page's `reviewed_*` front matter only after checking its relevant delta.
An unchanged subsystem can receive a delta-verification marker while preserving
its content `lastmod` and historical audit links. Never advance the baseline just
because the selector ran or the site rebuilt.
