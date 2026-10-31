---
title: Documentation Review Record
description: October 31 source baseline, documentation dispositions and next-update starting commit.
weight: 95
lastmod: 2026-10-31
---

# Documentation Review Record

## Next update starts here

The latest RawCull commit reviewed by this update is
[`dc048db4ded7b324bbf8cfe4e3f0275302f4f298`](https://github.com/rsyncOSX/RawCull/commit/dc048db4ded7b324bbf8cfe4e3f0275302f4f298),
committed **31 October 2026**, on `version-3.3.6`: **3.3.6 build 428**.
The app working tree was clean at review. This is an inspected source baseline,
not a claim about published release status.

For the next pass, compare from this exact commit:

```sh
git log --oneline dc048db4ded7b324bbf8cfe4e3f0275302f4f298..HEAD
git diff --stat dc048db4ded7b324bbf8cfe4e3f0275302f4f298..HEAD
```

## Scope and previous baselines

Reviewed all 36 Markdown pages under `content/en/docs`. No Hugo compilation was
run; the site owner will compile it. No application or package files were changed.

The preceding comprehensive review record used RawCull
`2ca891be5c013dc38fe3c931a829a04083b69c2a` (3.3.5 build 426, October 23).
Some pages had already incorporated October 24–25 work through
`7b8e200f07ceb8a6f10947236a5f3de5a099fb45`. This pass reconciles both baselines:
progress coalescing, grid resizing/navigation projections and measurement limits
remain documented; new RAW ZoomView policy and the parser pin are added.

Current app implementation links advance to the reviewed commit when their paths
still exist. Deleted design/test documents retain their immutable historical
revisions; dated performance evidence is not relabeled as a fresh measurement.
RawBrowse and model-export recipes retain their explicitly scoped baselines.

## Dependency baseline

The app lockfile contains 18 pins. Only RawParserKit changes from the October 23
snapshot: **1.3.3**, `26df4abc2178d5c07d08f3883d84d0648f5141d3`, previously 1.3.2
at `07801a34a82d7720d301a80724c36a5b8c9f1d6c`. Its source diff and evaluation
were reviewed locally. The other 17 version/revision pairs are unchanged;
[the package table]({{< relref "packages/_index.md" >}}) records all entries.

PhotoAIKit remains 1.0.0 (`4b85056e6c2603b5e382987710ca2f16f4c5c155`),
PhotoAnalysisKit 1.3.1 (`2a1466e04d821fa2628d6985296643e0d0c7e465`) and
RawCullCore 1.1.2 (`d25a51e65ad32a82bf82f86fa0ec07d6e14498e9`).

## Material changes

- Bounded fit RAW previews use eagerly completed sRGB pixels and separate native geometry.
- Native zoom keeps the established JPEG/disk-cache path; inspection remains native and transient.
- A separate 256 MiB completed-preview LRU has explicit source/EV identity and cleanup rules.
- Resize requests coalesce; load IDs and cancellation protect completion/publication.
- Display pixels can publish before the analysis thumbnail completes.
- RawParserKit 1.3.3 moves thumbnail decoding to `@concurrent` under its existing six-slot bound.
- The performance guide distinguishes six-photo preview results, historical catalog findings,
  deferred source-load tails and package/companion experiments.

## Page-by-page disposition

| Page | Review outcome |
| --- | --- |
| [_index.md]({{< relref "_index.md" >}}) | RAW viewing and resource lifetime |
| [ai/_index.md]({{< relref "ai/_index.md" >}}) | Current app/API baseline |
| [ai/aicombined.md]({{< relref "ai/aicombined.md" >}}) | Current app/API baseline |
| [ai/aidiagnostics.md]({{< relref "ai/aidiagnostics.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [ai/aiinrawcull.md]({{< relref "ai/aiinrawcull.md" >}}) | Current app/API baseline |
| [ai/airuntime.md]({{< relref "ai/airuntime.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [ai/rawbrowseai.md]({{< relref "ai/rawbrowseai.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [ai/rawcullai.md]({{< relref "ai/rawcullai.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [apidocs/_index.md]({{< relref "apidocs/_index.md" >}}) | Current app/API baseline |
| [apidocs/rabrowsweapidoc.md]({{< relref "apidocs/rabrowsweapidoc.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [apidocs/rawcull-internal-api.md]({{< relref "apidocs/rawcull-internal-api.md" >}}) | Current app/API baseline |
| [apidocs/rawcullapidoc.md]({{< relref "apidocs/rawcullapidoc.md" >}}) | Current app/API baseline |
| [burstgroup.md]({{< relref "burstgroup.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [cache-accounting.md]({{< relref "cache-accounting.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [cache.md]({{< relref "cache.md" >}}) | RAW viewing and resource lifetime |
| [concurrency.md]({{< relref "concurrency.md" >}}) | RAW viewing and resource lifetime |
| [detailsfocusmask.md]({{< relref "detailsfocusmask.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [detailsharpnessscoring.md]({{< relref "detailsharpnessscoring.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [filereadandwrite.md]({{< relref "filereadandwrite.md" >}}) | RAW viewing and resource lifetime |
| [focusmask.md]({{< relref "focusmask.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [heavy.md]({{< relref "heavy.md" >}}) | RAW viewing and resource lifetime |
| [memorypressure.md]({{< relref "memorypressure.md" >}}) | RAW viewing and resource lifetime |
| [newfeatures.md]({{< relref "newfeatures.md" >}}) | Current app/API baseline |
| [packages/_index.md]({{< relref "packages/_index.md" >}}) | Package pin and decode execution |
| [packages/photoaikit.md]({{< relref "packages/photoaikit.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [packages/photoanalysiskit.md]({{< relref "packages/photoanalysiskit.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [packages/rawcullcore.md]({{< relref "packages/rawcullcore.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [packages/rawparserkit.md]({{< relref "packages/rawparserkit.md" >}}) | Package pin and decode execution |
| [performance.md]({{< relref "performance.md" >}}) | Updated measurement guide |
| [pushpull.md]({{< relref "pushpull.md" >}}) | Retained contract or historical audit; source/metadata links reviewed |
| [raw-inspection.md]({{< relref "raw-inspection.md" >}}) | RAW viewing and resource lifetime |
| [security.md]({{< relref "security.md" >}}) | RAW viewing and resource lifetime |
| [sonymakernoteparser.md]({{< relref "sonymakernoteparser.md" >}}) | Package pin and decode execution |
| [thumbnail.md]({{< relref "thumbnail.md" >}}) | Package pin and decode execution |
| [update.md]({{< relref "update.md" >}}) | Review record and next-update baseline |
| [viewer-architecture.md]({{< relref "viewer-architecture.md" >}}) | RAW viewing and resource lifetime |

## Verification and limits

Static checks cover front matter, fenced blocks, local `relref` targets, immutable
GitHub source paths against available local Git trees, and the dependency table
against all 18 app lockfile pins. They verify source/path identity, not remote
HTTP availability or final Hugo rendering. Historical walkthroughs retain their
qualification limits; unchanged AI/package algorithms were not exhaustively
reaudited. Model downloads, real inference, camera qualification and app/package
tests were not rerun by this documentation update.

The source measurement record reports 32 passing focused tests and a 696-test
full run with three pre-existing failures; see [performance]({{< relref "performance.md" >}})
for the specific mismatches and cohort limitations. This documentation pass does
not present those runs as fresh release certification.

Static validation completed with 36 pages, 136 `relref` targets, 346 unique
immutable source paths and all 18 dependency pins resolving against local source.
