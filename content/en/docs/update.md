---
title: Documentation Review Record
description: Build 462 source review, per-page dispositions, and the incremental documentation baseline.
weight: 95
lastmod: 2026-11-21
reviewed_commit: "a0c72d11b6dea1f409542faf90f76fba43cdb0f5"
reviewed_version: "3.4.9"
reviewed_build: 462
reviewed_on: "2026-11-21"
review_scope: "Content and references updated"
---

# Documentation Review Record

## Next Update Starts Here

Reviewed on **21 November 2026** against **RawCull 3.4.9 build 462**,
commit [a0c72d11](https://github.com/rsyncOSX/RawCull/commit/a0c72d11b6dea1f409542faf90f76fba43cdb0f5).
The review covers all 41 pages in `content/en/docs`. The previous
application baseline was build 436 at `a68253b73cbad14a7b1030dba6b439e6bce7d3da`.

The app lockfile has 24 remote pins. The previous local
PhotoAnalysisKit and PhotoEvidenceKit references are now remote pins. The
[package snapshot]({{< relref "/docs/packages/_index.md" >}}) records their exact revisions.

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
git -C /path/to/RawCull log --oneline a0c72d11b6dea1f409542faf90f76fba43cdb0f5..HEAD
git -C /path/to/RawCull diff --stat a0c72d11b6dea1f409542faf90f76fba43cdb0f5..HEAD
```

After reviewing the candidate pages, record the new actual commit, project
version/build, full lockfile pins, per-page dispositions and document hashes in
`data/documentation-review.json`; update this page and the documentation index.
Advance a page's `reviewed_*` front matter only after checking its relevant delta.
An unchanged subsystem can receive a delta-verification marker while preserving
its content `lastmod` and historical audit links. Never advance the baseline just
because the selector ran or the site rebuilt.

## Build 462 Findings

- The workspace root assembles state, controllers and feature objects. Views
  use environment slices and explicit inputs. Catalog and rating operations,
  zoom navigation, file operations and burst review now have dedicated owners.
- The MCP controller uses explicit activity and lifecycle state. Setup, burst
  analysis and photo assessment live in separate controller extensions.
- The app shares one Vision feature-print backend and a face analyzer, and
  caps sharpness concurrency by processor count. The source test record
  reports three completed test-plan runs. Real-catalog throughput and
  simultaneous indexing and scoring remain unmeasured in that record.
- Close Up uses remotely pinned packages and source-pixel mode follows
  physical display pixels. People Ranking is a comparison order in the burst
  workspace. XMP handoff and unified scored evidence remain proposals.

## Per-Page Disposition

| Page | Review outcome |
| --- | --- |
| [_index.md]({{< relref "/docs/_index.md" >}}) | Content and references updated |
| [ai/_index.md]({{< relref "/docs/ai/_index.md" >}}) | Content and references updated |
| [ai/aicombined.md]({{< relref "/docs/ai/aicombined.md" >}}) | Content and references updated |
| [ai/aidiagnostics.md]({{< relref "/docs/ai/aidiagnostics.md" >}}) | Content and references updated |
| [ai/aiinrawcull.md]({{< relref "/docs/ai/aiinrawcull.md" >}}) | Content and references updated |
| [ai/airuntime.md]({{< relref "/docs/ai/airuntime.md" >}}) | Content and references updated |
| [ai/rawcullai.md]({{< relref "/docs/ai/rawcullai.md" >}}) | Existing content retained after delta and reference checks; historical recipe or vendor evidence retained |
| [apidocs/_index.md]({{< relref "/docs/apidocs/_index.md" >}}) | Existing content retained after delta and reference checks |
| [apidocs/rawcull-internal-api.md]({{< relref "/docs/apidocs/rawcull-internal-api.md" >}}) | Content and references updated |
| [apidocs/rawcullapidoc.md]({{< relref "/docs/apidocs/rawcullapidoc.md" >}}) | Content and references updated |
| [burstgroup.md]({{< relref "/docs/burstgroup.md" >}}) | Content and references updated |
| [cache-accounting.md]({{< relref "/docs/cache-accounting.md" >}}) | Existing content retained after delta and reference checks |
| [cache.md]({{< relref "/docs/cache.md" >}}) | Content and references updated |
| [closeups.md]({{< relref "/docs/closeups.md" >}}) | Content and references updated |
| [concurrency.md]({{< relref "/docs/concurrency.md" >}}) | Content and references updated |
| [detailsfocusmask.md]({{< relref "/docs/detailsfocusmask.md" >}}) | Content and references updated |
| [detailsharpnessscoring.md]({{< relref "/docs/detailsharpnessscoring.md" >}}) | Content and references updated |
| [filereadandwrite.md]({{< relref "/docs/filereadandwrite.md" >}}) | Content and references updated |
| [focusmask.md]({{< relref "/docs/focusmask.md" >}}) | Content and references updated |
| [heavy.md]({{< relref "/docs/heavy.md" >}}) | Content and references updated |
| [mcp.md]({{< relref "/docs/mcp.md" >}}) | Content and references updated |
| [memorypressure.md]({{< relref "/docs/memorypressure.md" >}}) | Existing content retained after delta and reference checks |
| [newfeatures/_index.md]({{< relref "/docs/newfeatures/_index.md" >}}) | Content and references updated |
| [newfeatures/newfeatures.md]({{< relref "/docs/newfeatures/newfeatures.md" >}}) | Existing content retained after delta and reference checks; historical recipe or vendor evidence retained |
| [newfeatures/unified-burst-evidence.md]({{< relref "/docs/newfeatures/unified-burst-evidence.md" >}}) | Content and references updated |
| [newfeatures/xmp-editor-handoff.md]({{< relref "/docs/newfeatures/xmp-editor-handoff.md" >}}) | Content and references updated |
| [packages/_index.md]({{< relref "/docs/packages/_index.md" >}}) | Content and references updated |
| [packages/package-modules.md]({{< relref "/docs/packages/package-modules.md" >}}) | Existing content retained after delta and reference checks |
| [packages/photoaikit.md]({{< relref "/docs/packages/photoaikit.md" >}}) | Existing content retained after delta and reference checks; historical package audit retained |
| [packages/photoanalysiskit.md]({{< relref "/docs/packages/photoanalysiskit.md" >}}) | Content and references updated; historical package audit retained |
| [packages/photoevidencekit.md]({{< relref "/docs/packages/photoevidencekit.md" >}}) | Content and references updated; historical package audit retained |
| [packages/rawcullcore.md]({{< relref "/docs/packages/rawcullcore.md" >}}) | Content and references updated; historical package audit retained |
| [packages/rawparserkit.md]({{< relref "/docs/packages/rawparserkit.md" >}}) | Existing content retained after delta and reference checks; historical package audit retained |
| [performance.md]({{< relref "/docs/performance.md" >}}) | Content and references updated |
| [pushpull.md]({{< relref "/docs/pushpull.md" >}}) | Existing content retained after delta and reference checks |
| [raw-inspection.md]({{< relref "/docs/raw-inspection.md" >}}) | Existing content retained after delta and reference checks |
| [security.md]({{< relref "/docs/security.md" >}}) | Content and references updated |
| [sonymakernoteparser.md]({{< relref "/docs/sonymakernoteparser.md" >}}) | Existing content retained after delta and reference checks |
| [thumbnail.md]({{< relref "/docs/thumbnail.md" >}}) | Content and references updated |
| [update.md]({{< relref "/docs/update.md" >}}) | Content and references updated |
| [viewer-architecture.md]({{< relref "/docs/viewer-architecture.md" >}}) | Content and references updated |

## Validation

The review checked Markdown structure, local page destinations, pinned source
paths against local Git objects, and the exact application lockfile. The
documentation pass did not run Hugo, app or package tests, model recipes,
vendor evaluations, or performance benchmarks. Dated measurements still
describe their original builds and fixtures.
