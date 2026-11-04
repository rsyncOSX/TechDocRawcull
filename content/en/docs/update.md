---
title: Documentation Review Record
description: November 4 review of commits through November 3, affected pages and next-update baseline.
weight: 95
lastmod: 2026-11-04
---

# Documentation Review Record

## Next update starts here

Reviewed on **4 November 2026** through RawCull
[`f75adff751e5f636f69d4cc40141c314b47ebb21`](https://github.com/rsyncOSX/RawCull/commit/f75adff751e5f636f69d4cc40141c314b47ebb21),
committed **3 November 2026**, on `version-3.3.6`: **3.3.6 build 429**.
The application and documentation working trees were clean before this pass.
This identifies inspected source, not published release status.

```sh
git log --oneline f75adff751e5f636f69d4cc40141c314b47ebb21..HEAD
git diff --stat f75adff751e5f636f69d4cc40141c314b47ebb21..HEAD
```

## Scope

Compared all five commits after the previous reviewed baseline,
`dc048db4ded7b324bbf8cfe4e3f0275302f4f298` (31 October, build 428),
against the 36-page documentation inventory. Changed behavior is confined to RAW
preview result metadata, progress/quality chrome and request timing. November 1
also expands the README/scripts guide and makes source formatting changes.
Existing fit/native rendering, cache budgets, inspection, export, security and
package contracts remain unchanged. The lockfile still contains the same 18 pins,
including RawParserKit 1.3.3; no package algorithm re-audit was needed.

## Affected pages

| Page | Update |
| --- | --- |
| [Documentation index]({{< relref "_index.md" >}}) | Reviewed baseline and build-429 status overview |
| [RAW inspection]({{< relref "raw-inspection.md" >}}) | Preparing/completed labels, actual reduction flag and timing semantics |
| [Viewer architecture]({{< relref "viewer-architecture.md" >}}) | Result ownership, publication, preservation, clearing and regression fixture |
| [Internal API]({{< relref "apidocs/rawcull-internal-api.md" >}}) | Preview flag and optional view-model metadata |
| [Application walkthrough]({{< relref "apidocs/rawcullapidoc.md" >}}) | Preview presentation and script entry points |
| [Concurrency]({{< relref "concurrency.md" >}}) | Main-actor metadata publication and independent pending state |
| [Performance]({{< relref "performance.md" >}}) | Badge limits, standalone runner, script checks and historical failures |
| [Review record]({{< relref "update.md" >}}) | This scope, evidence and next starting commit |

The other 28 pages retain their previous reviewed contracts, dates and immutable
source revisions. Updated guides advance live implementation links; historical
measurement/design links retain their original commits. RawBrowse and package
baselines are unchanged.

## Verification and limits

Static validation checks front matter, fenced blocks, local `relref` targets,
RawCull immutable source paths against local Git objects and unchanged dependency
pins. These checks do not establish remote HTTP availability or final rendering.
No application tests, model inference, photograph benchmarks or camera
qualification were rerun. The new gated replacement test was inspected in source.
The October 31 measurement record and its 696-test/three-failure result remain
historical; README corrections do not establish a new passing run.

Static checks passed across 36 pages: 112 local `relref` targets, 259 unique
immutable RawCull source paths and all 18 unchanged lockfile pins. Other repository
links retain their previous review status. Hugo rendering is not included in
these static checks.
