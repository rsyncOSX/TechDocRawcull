---
title: Documentation Review Record
description: Source baseline, page-by-page dispositions, static verification and limits of the October 23 documentation review.
weight: 95
lastmod: 2026-10-23
---

# Documentation Review Record

## Source baseline — 23 October 2026

This pass reviewed all **35 existing Markdown pages** under
`content/en/docs` and added one performance guide. Pages outside that requested
subtree were not edited. Their routes/front matter were read where necessary
to resolve links from the documentation.

| Repository | Reviewed baseline | Scope |
| --- | --- | --- |
| [RawCull](https://github.com/rsyncOSX/RawCull/tree/2ca891be5c013dc38fe3c931a829a04083b69c2a) | `2ca891be5c013dc38fe3c931a829a04083b69c2a`, 3.3.5 build 426, `version-3.3.5` | Current application, tests, project metadata, Makefile, lockfile and changes since the preceding documentation snapshot |
| [RawParserKit](https://github.com/rsyncOSX/RawParserKit/tree/07801a34a82d7720d301a80724c36a5b8c9f1d6c) | 1.3.2, `07801a34a82d7720d301a80724c36a5b8c9f1d6c` | Actual app pin and existing scoped package guide |
| [PhotoAnalysisKit](https://github.com/rsyncOSX/PhotoAnalysisKit/tree/2a1466e04d821fa2628d6985296643e0d0c7e465) | 1.3.1, `2a1466e04d821fa2628d6985296643e0d0c7e465` | Actual app pin; distinguish package formulas from host AF evidence hydration |
| [PhotoAIKit](https://github.com/rsyncOSX/PhotoAIKit/tree/4b85056e6c2603b5e382987710ca2f16f4c5c155) | 1.0.0, `4b85056e6c2603b5e382987710ca2f16f4c5c155` | Actual app pin; distinguish package services from extracted host state |
| [RawCullCore](https://github.com/rsyncOSX/RawCullCore/tree/d25a51e65ad32a82bf82f86fa0ec07d6e14498e9) | 1.1.2, `d25a51e65ad32a82bf82f86fa0ec07d6e14498e9` | Actual app pin; live review/persistence ownership remains app-side |
| [RawBrowse](https://github.com/rsyncOSX/RawBrowse/tree/5815fd64ca02185c1ca6300311794a3ecacf6ec8) | Retained companion baseline `5815fd64ca02185c1ca6300311794a3ecacf6ec8` | Validate pinned source references; no claim of a new companion-app qualification |

The preceding app documentation baseline was
`b46501739f6a09c0e2df352fc3ed2bf8e10a0e91`, build 425. Since then, the `quality`
changes were merged into `version-3.3.5`, the build advanced to 426, AF evidence
backfill/comparison tooling was added, and formatting/source organization changed.
Current app implementation links use the reviewed immutable commit, not a moving
branch. The [package overview]({{< relref "packages/_index.md" >}}) matches all
18 lockfile entries; those revisions have not changed from the preceding app baseline.

Package walkthroughs retain their explicitly dated audit scopes. Historical
model/exporter recipes, cache archaeology and competitor research keep their
original revisions and qualification limits. This pass does not present unchanged
package algorithms or historical model observations as newly validated behavior.

## Material corrections

- `BurstReviewSessionModel` owns live decisions; view-model properties forward
  to it. Result/state dictionaries are externally read-only and use commands.
  The grid projection key includes the session revision.
- `BurstReviewStateMapping` shares membership-signature snapshot/restore rules
  between live review and cached analysis without a stored-schema change.
- `RawCullSemanticSearchModel` owns semantic evidence, capability, hydration,
  query lifetime and presentation; the similarity facade remains stable.
- Combined Review orchestration, work support and comparison extensions share
  one mutable feature/run owner. `ReviewRunError` now has a separate file.
- Preload releases file gates before awaiting saves, but retains worker slots
  and the catalog grant through saving. Interactive save behavior is unchanged.
- `@concurrent` changes isolation/work placement; it does not make an unstructured
  `Task` structured or automatically propagate cancellation.
- Older burst results can hydrate missing AF-center evidence without replacing
  blended scores or winner recommendations. The real-photo AF comparison is opt-in.
- The [performance guide]({{< relref "performance.md" >}}) distinguishes cached
  measurements, differing workloads and logging failures from unproven speedups.

## Page-by-page disposition

Every existing page received a front-matter/route/link check. Current app links
and review metadata were advanced where present; unchanged content is retained
when the source delta does not alter its stated contract.

| Page | Disposition |
| --- | --- |
| [_index.md]({{< relref "_index.md" >}}) | Build-426 baseline, dedicated owners, package continuity and performance reading route |
| [thumbnail.md]({{< relref "thumbnail.md" >}}) | Awaited worker saves, gate ordering, cancellation/access lifetime, actual loading protocol and new tests |
| [viewer-architecture.md]({{< relref "viewer-architecture.md" >}}) | Separate review and viewport owners; review revision and AF backfill; retain viewer/keyboard contracts |
| [raw-inspection.md]({{< relref "raw-inspection.md" >}}) | Refresh app links; retain unchanged decoder/export/inspection and histogram predicates |
| [cache.md]({{< relref "cache.md" >}}) | Bound pending preload saves; distinguish thumbnail budgets from full-size/process memory |
| [cache-accounting.md]({{< relref "cache-accounting.md" >}}) | Retain the dated accounting walkthrough and historical source pin; refresh current integration links |
| [memorypressure.md]({{< relref "memorypressure.md" >}}) | Add measured workload context and explicit limits of footprint conclusions |
| [concurrency.md]({{< relref "concurrency.md" >}}) | Correct structured-task wording, add state owners and bounded-save cancellation contract |
| [focusmask.md]({{< relref "focusmask.md" >}}) | Add missing AF-center hydration without reranking; retain package/presentation contracts |
| [detailsfocusmask.md]({{< relref "detailsfocusmask.md" >}}) | Refresh host links; retain pinned package pipeline and geometry/publication boundaries |
| [detailsharpnessscoring.md]({{< relref "detailsharpnessscoring.md" >}}) | Add AF backfill and optional operator-comparison protocol; retain the package formula |
| [burstgroup.md]({{< relref "burstgroup.md" >}}) | Document session commands, review revisions, membership mapping and AF evidence hydration |
| [filereadandwrite.md]({{< relref "filereadandwrite.md" >}}) | Shared review serialization and awaited preload ownership; existing schemas/cleanup retained |
| [security.md]({{< relref "security.md" >}}) | Explain retained grant through worker/save drain and limits of cancellation |
| [heavy.md]({{< relref "heavy.md" >}}) | Separate background placement from backpressure; encoding remains in its owner |
| [sonymakernoteparser.md]({{< relref "sonymakernoteparser.md" >}}) | Retain unchanged parser pin, AF fallback and generic-format caveats |
| [newfeatures.md]({{< relref "newfeatures.md" >}}) | Update current implementation note; retain explicitly historical roadmap/research |
| [pushpull.md]({{< relref "pushpull.md" >}}) | Retain documentation-repository workflow; do not impose it on app merge history |
| [update.md]({{< relref "update.md" >}}) | Replace the preceding record with this scoped baseline and dispositions |
| [ai/_index.md]({{< relref "ai/_index.md" >}}) | Current semantic/review owners and build metadata |
| [ai/airuntime.md]({{< relref "ai/airuntime.md" >}}) | Dedicated semantic model, topology, generation guards and stable runtime identity |
| [ai/aiinrawcull.md]({{< relref "ai/aiinrawcull.md" >}}) | Correct source/assembly/classification ownership; retain unchanged provider behavior |
| [ai/aicombined.md]({{< relref "ai/aicombined.md" >}}) | Split execution source map and error declaration; retain stage/prompt/schema contracts |
| [ai/aidiagnostics.md]({{< relref "ai/aidiagnostics.md" >}}) | Point diagnostics to work-execution support; retain opt-in qualification boundaries |
| [ai/rawcullai.md]({{< relref "ai/rawcullai.md" >}}) | Retain pinned historical preparation recipe, licences and model qualification limits |
| [ai/rawbrowseai.md]({{< relref "ai/rawbrowseai.md" >}}) | Retain companion model recipe and historical exporter pins |
| [packages/_index.md]({{< relref "packages/_index.md" >}}) | Reconcile all 18 resolved package entries; update snapshot date |
| [packages/rawparserkit.md]({{< relref "packages/rawparserkit.md" >}}) | Separate new host save ownership from unchanged package decode/coalescing contracts |
| [packages/photoanalysiskit.md]({{< relref "packages/photoanalysiskit.md" >}}) | Separate AF evidence hydration from unchanged 1.3.1 formula |
| [packages/rawcullcore.md]({{< relref "packages/rawcullcore.md" >}}) | Keep live review state and snapshot orchestration outside the pure package |
| [packages/photoaikit.md]({{< relref "packages/photoaikit.md" >}}) | Distinguish extracted host semantic state from unchanged package services |
| [apidocs/_index.md]({{< relref "apidocs/_index.md" >}}) | Add owner-command and performance navigation |
| [apidocs/rawcullapidoc.md]({{< relref "apidocs/rawcullapidoc.md" >}}) | Build-426 ownership, preload lifetime, 401 smoke identifiers and opt-in AF workflow |
| [apidocs/rawcull-internal-api.md]({{< relref "apidocs/rawcull-internal-api.md" >}}) | Explicit review/semantic commands, read-only results/states and AF hydration interface |
| [apidocs/rabrowsweapidoc.md]({{< relref "apidocs/rabrowsweapidoc.md" >}}) | Retain pinned companion API/decoder behavior and existing public route |
| [performance.md]({{< relref "performance.md" >}}) | New guide to real-catalog results, ownership invariants, trace failures and comparison limits |

## Verification and limits

Static validation parses TOML/YAML front matter, checks unique routes and fenced
blocks, resolves internal Markdown links and Hugo `relref` targets, verifies
GitHub source paths against local Git trees at their stated immutable revisions,
and compares every package-table row with `Package.resolved`. Pinned package and
companion revisions were fetched into a separate review workspace for source
identity checks; application dependencies and documentation recipes were not changed.
This verifies path identity, not remote HTTP availability or model download services.

The content review follows app changes since the preceding baseline and relevant
implementation/test contracts. Retained package audits are not represented as a
new exhaustive line-by-line algorithm audit. Historical vendor/model research
was not requalified. Code examples remain scoped excerpts or illustrative calls;
the documentation is not a standalone compilable Swift target.

**Hugo was not compiled**, as requested. Application/package suites, real-model
inference, model conversion and photographic qualification were not run by this
documentation pass. The earlier preload implementation phase's 36-test result
and October 23 performance recording are dated evidence in the app repository,
not fresh qualification of every build-426 behavior. The performance page retains
the corrupt/incomplete logging-stream limits and unresolved reopening observations.

The final static pass checked 36 documentation pages, 112 `relref` targets,
765 Markdown links, four local heading anchors, 336 unique immutable source
paths across 11 source revisions, and all 18 package pins, with no unresolved
checks. Thirty-four existing pages changed and the performance page was added;
`pushpull.md` was reviewed and retained unchanged.

## Maintenance triggers

Update the owning page and overview together when app ownership changes.
Describe trigger, owner, input/result, cancellation/publication checks,
persistence identity and failure handling before listing APIs. Keep current
source links immutable and advance package pins only from the app lockfile.
Preserve the difference between task correctness, runtime speed and photographic
quality. Add a new measured claim only with its source/model identity, workload,
cache preparation, phase boundaries and known recording limitations.
