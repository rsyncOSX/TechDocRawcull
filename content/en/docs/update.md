---
title: Documentation Review Record
description: November 9 branch review, per-page change triggers, and the next incremental documentation baseline.
weight: 95
lastmod: 2026-11-09
reviewed_commit: "a68253b73cbad14a7b1030dba6b439e6bce7d3da"
reviewed_version: "3.4.5"
reviewed_build: 436
reviewed_on: "2026-11-09"
review_scope: "source delta and reference check; content updated"
---

# Documentation Review Record

## Next Update Starts Here

Reviewed on **9 November 2026** against **RawCull 3.4.5, build 436**,
commit [`a68253b73cbad14a7b1030dba6b439e6bce7d3da`](https://github.com/rsyncOSX/RawCull/commit/a68253b73cbad14a7b1030dba6b439e6bce7d3da) on `version-3.4.5`. This development branch is awaiting
stability verification and merge into `main`.

The lockfile contains **17 remote pins**. PhotoAnalysisKit and PhotoEvidenceKit
resolve from sibling checkouts. See the [package snapshot]({{< relref "/docs/packages/_index.md" >}}). Historical audits and measurements
retain their original source revisions.

The previous baseline was RawCull **3.4.0 build 434** at `a5f35b05c1e206ed4d6aa599522f5c8622b5308a`.
This incremental pass inspected 20 changed source, test, project and planning
files, including the Close Up integration and two local package references.

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
git -C /path/to/RawCull log --oneline a68253b73cbad14a7b1030dba6b439e6bce7d3da..HEAD
git -C /path/to/RawCull diff --stat a68253b73cbad14a7b1030dba6b439e6bce7d3da..HEAD
```

After reviewing the candidate pages, record the new actual commit, project
version/build, full lockfile pins, per-page dispositions and document hashes in
`data/documentation-review.json`; update this page and the documentation index.
Advance a page's `reviewed_*` front matter only after checking its relevant delta.
An unchanged subsystem can receive a delta-verification marker while preserving
its content `lastmod` and historical audit links. Never advance the baseline just
because the selector ran or the site rebuilt.

## November 9 Findings And Verification

- Human face crops and local preview detail are implemented, with disposable
  per-file evidence caching. Vision animal head and eye crops are a pilot.
- The automatic strip follows the active frame and pauses during similarity
  indexing. Manual crops retain their independent source and region controls.
- Two package entries moved from remote pins to sibling checkout references.
  The remaining 17 remote records match the previous snapshot.
- The earlier Close Up implementation pass recorded a passing macOS build and
  seven focused tests. This site-wide documentation pass checks source deltas,
  links and review metadata. Branch-wide stability, human TestFlight and
  representative wildlife validation are still pending.

## November 8 Findings And Corrections

- The shared burst workspace now embeds PhotoEvidenceKit **1.0.7**, revision
  `7614fd1528bb7cf2549799fb937678ea39d90228`; the older roadmap pin was 1.0.5.
- Close-ups is exposed in the shared burst/**Single Images** workspace. The old
  roadmap's burst-only restriction no longer matches the inspected source.
- The JPG/RAW picker shares main-stage source selection. Its RAW 9 wording checks
  comparison, current and retained-reference URLs, while each crop labels its source.
- AF-overlay and close-up session preferences are synchronized. Group changes
  create a new close-up model while preserving the AF-overlay preference.
- Native-control key ownership is checked by the burst workspace's focused
  SwiftUI handlers as well as its existing local-monitor routing.
- Manual-region UserDefaults records are separate from saved ratings and caches;
  current cleanup paths do not explicitly remove the region-key namespace.
- Close-up decoding, bounded card artifacts and the stage's three-frame cache
  have different lifetimes and budgets. No new performance benefit is claimed.
- The homepage's older macOS Tahoe wording was corrected to the project's macOS
  27 target. XMP exchange and unified scored evidence remain planned capabilities.

The lockfile contains **19 pins**. Relative to the previous review, it adds
PhotoEvidenceKit and updates EventSource, swift-asn1, swift-collections,
swift-jinja, swift-transformers and yyjson. PhotoAIKit, PhotoAnalysisKit,
RawCullCore and RawParserKit retain their previous resolved revisions; no new
algorithm audit is inferred from transitive updates. Exact pin states are stored
in the machine-readable baseline and linked from the
[package catalog]({{< relref "packages/_index.md" >}}).

## November 8 Per-Page Disposition

At that review, every page below had `reviewed_commit`, `reviewed_version`, `reviewed_build`,
`reviewed_on` and `review_scope` front matter. These identify this source-delta
review separately from original publication dates and dated empirical evidence.
The JSON map supplies the more detailed review triggers; the table records the
human-readable outcome.

| Page | Review outcome |
| --- | --- |
| [_index.md]({{< relref "/_index.md" >}}) | editorial/reference check; no application-runtime contract |
| [about/index.md]({{< relref "/about/index.md" >}}) | editorial/reference check; no application-runtime contract |
| [_index.md]({{< relref "/docs/_index.md" >}}) | content updated; source delta and references checked |
| [ai/_index.md]({{< relref "/docs/ai/_index.md" >}}) | source delta/reference check; existing content retained |
| [ai/aicombined.md]({{< relref "/docs/ai/aicombined.md" >}}) | source delta/reference check; existing content retained |
| [ai/aidiagnostics.md]({{< relref "/docs/ai/aidiagnostics.md" >}}) | source delta/reference check; existing content retained |
| [ai/aiinrawcull.md]({{< relref "/docs/ai/aiinrawcull.md" >}}) | source delta/reference check; existing content retained |
| [ai/airuntime.md]({{< relref "/docs/ai/airuntime.md" >}}) | source delta/reference check; existing content retained |
| [ai/rawcullai.md]({{< relref "/docs/ai/rawcullai.md" >}}) | source delta/reference check; existing content retained; historical exporter recipe not rerun or externally requalified |
| [apidocs/_index.md]({{< relref "/docs/apidocs/_index.md" >}}) | content updated; source delta and references checked |
| [apidocs/rawcull-internal-api.md]({{< relref "/docs/apidocs/rawcull-internal-api.md" >}}) | content updated; source delta and references checked |
| [apidocs/rawcullapidoc.md]({{< relref "/docs/apidocs/rawcullapidoc.md" >}}) | content updated; source delta and references checked |
| [burstgroup.md]({{< relref "/docs/burstgroup.md" >}}) | content updated; source delta and references checked |
| [cache-accounting.md]({{< relref "/docs/cache-accounting.md" >}}) | source delta/reference check; existing content retained |
| [cache.md]({{< relref "/docs/cache.md" >}}) | content updated; source delta and references checked |
| [concurrency.md]({{< relref "/docs/concurrency.md" >}}) | content updated; source delta and references checked |
| [detailsfocusmask.md]({{< relref "/docs/detailsfocusmask.md" >}}) | source delta/reference check; existing content retained |
| [detailsharpnessscoring.md]({{< relref "/docs/detailsharpnessscoring.md" >}}) | source delta/reference check; existing content retained |
| [filereadandwrite.md]({{< relref "/docs/filereadandwrite.md" >}}) | content updated; source delta and references checked |
| [focusmask.md]({{< relref "/docs/focusmask.md" >}}) | content updated; source delta and references checked |
| [heavy.md]({{< relref "/docs/heavy.md" >}}) | content updated; source delta and references checked |
| [memorypressure.md]({{< relref "/docs/memorypressure.md" >}}) | content updated; source delta and references checked |
| [newfeatures/_index.md]({{< relref "/docs/newfeatures/_index.md" >}}) | content updated; source delta and references checked; proposals remain proposals; vendor comparison remains dated 2026-11-05 |
| [newfeatures/newfeatures.md]({{< relref "/docs/newfeatures/newfeatures.md" >}}) | content updated; source delta and references checked; proposals remain proposals; vendor comparison remains dated 2026-11-05 |
| [newfeatures/unified-burst-evidence.md]({{< relref "/docs/newfeatures/unified-burst-evidence.md" >}}) | content updated; source delta and references checked; proposals remain proposals; vendor comparison remains dated 2026-11-05 |
| [newfeatures/xmp-editor-handoff.md]({{< relref "/docs/newfeatures/xmp-editor-handoff.md" >}}) | source delta/reference check; existing content retained; proposals remain proposals; vendor comparison remains dated 2026-11-05 |
| [performance.md]({{< relref "/docs/performance.md" >}}) | content updated; source delta and references checked |
| [pushpull.md]({{< relref "/docs/pushpull.md" >}}) | editorial/reference check; no application-runtime contract |
| [raw-inspection.md]({{< relref "/docs/raw-inspection.md" >}}) | content updated; source delta and references checked |
| [security.md]({{< relref "/docs/security.md" >}}) | content updated; source delta and references checked |
| [sonymakernoteparser.md]({{< relref "/docs/sonymakernoteparser.md" >}}) | content updated; source delta and references checked |
| [thumbnail.md]({{< relref "/docs/thumbnail.md" >}}) | content updated; source delta and references checked |
| [update.md]({{< relref "/docs/update.md" >}}) | content updated; source delta and references checked |
| [viewer-architecture.md]({{< relref "/docs/viewer-architecture.md" >}}) | content updated; source delta and references checked |
| [search.md]({{< relref "/search.md" >}}) | editorial/reference check; no application-runtime contract |
| [site.md]({{< relref "/site.md" >}}) | editorial/reference check; no application-runtime contract |

## November 8 Verification And Limits

Static checks passed for **36 page headers and fenced-block structures**,
**166 local `relref` destinations**, **312 unique revision-pinned source
references**, document hashes and **all 19 exact resolved pin records**. Pinned references
are verified against local Git objects; this does not establish remote HTTP
availability. The source-change selector was checked at the recorded HEAD and
with temporary Git fixtures for changed, dirty, added, removed and unmapped inputs.
It does not execute code examples or prove that its dependency map captures every
semantic relationship.

Application/UI tests, package tests, real photographs, installed-model inference,
benchmarks, vendor comparisons and exporter recipes were **not rerun**. Inspected
new fixtures include `BurstCloseUpTests` and the group-reset AF-preference test.
Historical test failures and benchmark limits remain historical and are not
converted into a current passing result.

The full Hugo build was previously blocked by unavailable Dart Sass support in
the installed Hugo setup. Content rendering and source-reference checks are
separate from full theme/stylesheet and visual validation. No release artifact
was built or published during this review.
