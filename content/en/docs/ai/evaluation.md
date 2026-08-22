+++
author = "Thomas Evensen"
title = "CLIP Model Evaluation Results"
linkTitle = "CLIP Evaluation Results"
date = "2026-08-12"
lastmod = "2026-08-22"
description = "Detailed comparison of OpenAI CLIP ViT-B/32 and OpenCLIP DataComp ViT-B/32-256 using RawCullFB semantic-search and image-similarity reports."
tags = ["ai", "clip", "openai", "datacomp", "evaluation", "semantic-search", "image-similarity", "rawcullfb"]
categories = ["technical details"]
weight = 32
+++

# CLIP Model Evaluation Results

**Report date:** 2026-08-12

**Evidence re-audited:** 2026-08-22

**Immutable run directory:**
`/Users/thomas/Library/Mobile Documents/com~apple~CloudDocs/TestPhotos/CLIPModelEvaluations/20260812T123105Z`

This is a dated evidence report, not timeless architecture and not a current
release approval. Later package, model, fixture, or catalog state must be
evaluated in a new run.

This report compares the product-behavior results produced by RawCullFB for:

- OpenAI CLIP ViT-B/32 at 224 × 224; and
- OpenCLIP DataComp ViT-B/32-256 using the `datacomp_s34b_b86k`
  checkpoint.

The runs follow the product-behavior portion of
[Evaluating CLIP Models](../evaluateclipmodels/). They cover the canonical 77
semantic queries and a complete all-pairs image-similarity pass over 453 indexed
images.

The product reports show that both integrations completed their recorded
workloads, neither shows semantic collapse, and both produce coherent
image-neighbourhood structures.
DataComp is modestly faster and more consistent across paraphrases. Those are
promising sanity-check results, but they are not labeled accuracy metrics.

No final release-model selection can be made from this evidence package. It
contains parity artifacts, but DataComp fails the `0.998` end-to-end parity
gate. It also combines product reports from 9–10 August with an environment and
model inspection captured on 12 August, and the recorded fingerprints are not
fully consistent. Pooled relevance labels, a calibrated similarity benchmark,
and full operational measurements are also absent.

## 1. Evidence analyzed

### 1.1 Product-report inputs

| Evidence | OpenAI | DataComp |
|---|---|---|
| RawCullFB report | `ViT-B-32-semantic-test-results.txt` | `datacomp_s34b_b86k-semantic-test-results.txt` |
| Model label | `ViT-B-32` | `datacomp_s34b_b86k` |
| Run started, UTC | 2026-08-09 15:56:46 | 2026-08-10 05:07:09 |
| Report updated, UTC | 2026-08-09 15:56:53 | 2026-08-10 05:07:16 |
| Catalog recorded by report | `/Users/thomas/Downloads/testphotos` | `/Users/thomas/Downloads/testphotos` |
| Result limit | 50 | 50 |

The canonical query bytes archived later have SHA-256
`2dfc0f4c2ff83146bd36c5b99fa78a3e99bc843edc2c9602d816ff663f89c604`.
The two reports say only that they used 77 queries; they do not embed that
digest, so the association is documentary rather than cryptographically bound
to each report. `catalog-files.txt` lists 453 paths, but no per-file catalog
content hashes or aggregate catalog digest were archived. Exact catalog-byte
identity therefore remains unproved.

### 1.2 Environment and tool identities

The 12 August archive records:

| Field | Recorded value |
|---|---|
| Environment capture | 2026-08-12 12:31:16 UTC |
| macOS | 27.0, build `26A5406e` |
| Xcode | 27.0, build `27A5237l` |
| Swift | 6.4, `swiftlang-6.4.0.30.4`, target `arm64-apple-macosx27.0.0` |
| `uv` | 0.12.3, Homebrew 2026-08-07, aarch64 |
| RawCullFB revision | `5f90688984672244b82b4d588567b4b68f159b18` |
| PhotoAIKit revision | `6e3216027b267c27ccaf99d334807b18ea1aaec9` |
| CLIPBench revision | `d7a2b11cfdc6e0d5d8ab37a51c61219dfe5b6766` |
| Mac hardware model/RAM | Not recorded |
| RawParserKit and complete package locks | Not archived |

Because this capture post-dates both product reports, it cannot by itself prove
the environment used on 9–10 August.

### 1.3 Model and fingerprint records

The complete model fingerprints recorded in the product reports are:

```text
OpenAI
clip:clip-vit-base-patch32_float16_static:openai/clip-vit-base-patch32:clip-vit-base-patch32_float16_static.aimodel:0.4:directory-tree-sha256-v1:a71ceca116e13b334b0679c95bd85d7ecda14fd68bd7a3ea84b83c286005f45b

DataComp
clip:ViT-B-32-256-datacomp_s34b_b86k_float16_static:mlfoundations/open_clip:ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel:0.4:directory-tree-sha256-v1:6a3639a2049b8a4ea23fe04c3083e199a4f505433f7c8bd0748b3c8d4fcb1572
```

The 12 August metadata files have SHA-256
`049fb9163608ee81b3a9e7fa49b29764958518ed8009e671e146ea3aeef6dbc0`
for OpenAI and
`d6ccb58bd7bfe2cbe917a9dd25addd20c17d3492a1581920c981b2ea6f650bdd`
for DataComp. Their declared runtime fingerprints and CLIPBench's captured
inspection fingerprints compare as follows:

| Identity source | OpenAI | DataComp |
|---|---|---|
| 9–10 August RawCullFB report | `a71ceca1…005f45b` | `6a3639a2…fcb1572` |
| 12 August metadata `asset_fingerprints.main` | `24a20d7c…fc48f4914` | `6a3639a2…fcb1572` |
| 12 August CLIPBench inspection | `2e285bb7…9bda32c` | `19a8acb3…3983f08` |

Distinct report fingerprints prove that the two product reports used different
embedding spaces, but the cross-artifact mismatch means the archived parity
inspection cannot be assumed to identify the exact same bundle bytes used by
each earlier product report. This is a reproducibility failure and blocks a
release decision from this run.

### 1.4 Adjacent parity evidence

The archive also contains ten-image/ten-text parity outputs. The fixture file
hashes are present, and the canonical fixture manifest currently has SHA-256
`8687bb47c43e3a0a573210bd8f1d548ac2482d958a8cb8cec20d9f9ddcedd6ff`;
that manifest digest was not itself written into the run directory.

| Gate | OpenAI | DataComp |
|---|---:|---:|
| Minimum text cosine | `1.0000` | `1.0000` |
| Minimum end-to-end fixture cosine | `0.9988` | `0.9908` |
| Required minimum | `0.998` | `0.998` |
| Archived result | Pass | **Fail** |

The DataComp minimum occurs on `04-city-night.jpg`; several other DataComp
image rows are also below `0.998`. These parity files were not inputs to the
original product-report calculations and do not alter those measured retrieval
metrics. They do change the overall gate decision: DataComp cannot be promoted
from this archived run.

## 2. Report-integrity checks

| Integrity check | OpenAI | DataComp | Result |
|---|---:|---:|---|
| Overall status | `completed` | `completed` | Pass |
| Completed queries | 77/77 | 77/77 | Pass |
| Result limit | 50 | 50 | Pass |
| Similarity status | `completed` | `completed` | Pass |
| Similarity anchors | 453 | 453 | Pass |
| Pair comparisons | 102,378 | 102,378 | Pass |
| Incompatible pairs | 0 | 0 | Pass |

For 453 images, the number of unique unordered pairs is:

```text
453 × 452 / 2 = 102,378
```

The reported pair count is therefore complete for both product reports. Within
those files there is no evidence of a partial query run, partial similarity
run, incompatible vector, or reuse of one fingerprint for both models. This
does not resolve the cross-date fingerprint mismatch described in Section 1.

## 3. Semantic sanity-check methodology

The following report-derived diagnostics were calculated independently for each
model:

- distinct images returned at rank one across all 77 queries;
- the most frequently reused rank-one image;
- unique images appearing anywhere in the 77 top-50 result sets;
- mean rank-one minus rank-two score margin;
- mean shared images between the top ten of every pair of unrelated and related
  queries;
- mean shared top-ten images within the five three-query paraphrase groups;
- first-query latency; and
- warmed mean, median, and P95 latency, excluding the first query.

These are collapse, diversity, consistency, and operational diagnostics. They
do not establish whether an image is relevant to a query. Relevance must be
judged from the image itself using the pooled labeling procedure in the main
evaluation guide.

## 4. Semantic retrieval results

### 4.1 Diversity and hub behavior

| Metric | OpenAI | DataComp | Interpretation |
|---|---:|---:|---|
| Distinct rank-one images | 53/77 | **58/77** | DataComp uses a slightly broader set of winners |
| Largest rank-one hub | 4/77 | 4/77 | Neither model has a universal winner |
| Unique images across all top-50 results | 418/453 | **423/453** | Both search broadly across the catalog |
| Mean top-one minus top-two margin | 0.00737 | 0.00994 | DataComp has wider within-model separation on this run |
| Median top-one minus top-two margin | 0.00533 | 0.00708 | Same direction as the mean |

The most frequently returned rank-one image for OpenAI is
`62480371.jpg`, selected for four queries. The most frequent DataComp winner is
`2132732266.jpg`, also selected for four queries.

Both results are consistent with healthy retrieval diversity. The established
OpenAI sanity reference in the evaluation procedure is 53 distinct top-one
images and a maximum hub frequency of 4/77; this run reproduces those exact
values. DataComp slightly increases rank-one and top-50 coverage without
creating a larger semantic hub.

The score-margin values may be compared between ranks from the same model, but
not treated as calibrated confidence or compared directly as accuracy between
models. The two models produce different embedding spaces and score
distributions.

### 4.2 Paraphrase consistency

Across all 2,926 pairs of queries, the mean number of shared images in two
top-ten result lists is low, as expected:

| Metric | OpenAI | DataComp |
|---|---:|---:|
| Mean shared top-ten images, all query pairs | 0.724 | 0.703 |
| Median shared top-ten images, all query pairs | 0 | 0 |
| Mean shared top-ten images, paraphrase pairs | 4.93 | **5.60** |
| Median shared top-ten images, paraphrase pairs | 5 | 5 |
| Paraphrase/general overlap ratio | 6.82× | **7.97×** |

Paraphrases are materially more consistent than unrelated prompts for both
models. This is an important sanity check: changing the wording while retaining
the intent produces strongly overlapping results, without causing unrelated
queries to collapse onto a common result pool.

The group-level mean shared top-ten counts are:

| Paraphrase group | OpenAI | DataComp |
|---|---:|---:|
| Dog on a beach | 6.00 | **6.33** |
| City street at night | 7.33 | **7.67** |
| Sharp portrait | 3.33 | **4.67** |
| Blurry photograph | 3.67 | **4.33** |
| Beautiful landscape | 4.33 | **5.00** |

DataComp has higher top-ten overlap in all five groups. Its largest advantage is
on the sharp-portrait group. This is the clearest positive signal for DataComp
in the current unlabeled reports.

Top-one identity is less stable than top-ten membership for both models. That
is not necessarily a failure: several images can have near-equal relevance,
and a small score change can reorder the first few results. Graded relevance
labels and nDCG@5 are needed to distinguish harmless reordering from a real
quality difference.

### 4.3 Agreement between models

The models return the same rank-one image for 19 of 77 queries, or 24.7%. Their
top-ten lists contain an average of 4.69 identical images, or 46.9% of a
ten-result list.

| Query category | Queries | Same rank one | Mean shared top-ten images |
|---|---:|---:|---:|
| Objects and scenes | 16 | 6 | 5.63 |
| Colors and attributes | 9 | 4 | 5.56 |
| Actions and relations | 7 | 2 | 5.00 |
| Photographic quality and style | 13 | 2 | 4.54 |
| Composition and subjective judgment | 9 | 1 | 2.44 |
| Count, spatial relation, and negation | 8 | 3 | 3.63 |
| Paraphrases | 15 | 1 | 5.07 |

Concrete objects, scenes, colors, and attributes show the strongest agreement.
Composition and subjective photographic judgments show the weakest agreement,
followed by count, spatial, and negative-language prompts.

The strongest top-ten agreement includes:

- `a yellow flower`: 10/10 shared results;
- `a lake surrounded by mountains`: 9/10;
- `food on a plate`: 8/10;
- `dog on a beach`: 8/10; and
- `canine at the seaside`: 8/10.

The most model-sensitive prompts include:

- `a subject positioned using the rule of thirds`: 0/10 shared results;
- `a photograph with strong leading lines`: 1/10;
- `a candid emotional moment`: 1/10;
- `a reflection of a person in a mirror`: 1/10;
- `sharp portrait`: 1/10; and
- `a photograph where the subject is not sharply focused`: 1/10.

Disagreement is not itself proof that either result is wrong. It identifies the
queries that should receive the closest attention during blind relevance
labeling.

## 5. Query latency

| Metric | OpenAI | DataComp | DataComp difference |
|---|---:|---:|---:|
| First query | 157 ms | **130 ms** | 17.2% faster |
| Warm mean | 67.25 ms | **65.67 ms** | 2.3% faster |
| Warm median | 66 ms | **65 ms** | 1.5% faster |
| Warm P95 | 72 ms | **69 ms** | 4.2% faster |
| Warm range | 63–130 ms | 61–129 ms | Similar |

DataComp is consistently but only modestly faster in this report. The first
query is the largest difference. Warmed latency is effectively in the same
operational class for both models.

These timings are useful observations, not the complete operational benchmark
required by the evaluation procedure. The reports do not establish that 30
unmeasured warm-up queries were run, and they do not contain P99 latency, model
load time, indexing throughput, peak memory, energy impact, bundle size, or
index size.

## 6. Image-similarity results

| Metric | OpenAI | DataComp |
|---|---:|---:|
| Similarity pass duration | 861 ms | **842 ms** |
| Mutual top-one pairs | 122 | **124** |
| Unique top-one targets | 298 | **318** |
| Maximum top-one target reuse | **7** | 9 |
| Nearest-distance minimum | 0.00082 | 0.00586 |
| Nearest-distance median | 0.17191 | 0.30235 |
| Nearest-distance mean | 0.16290 | 0.27934 |
| Nearest-distance P95 | 0.30612 | 0.50179 |
| Nearest-distance maximum | 0.45259 | 0.78558 |

DataComp completes the all-pairs similarity pass 19 ms, or 2.2%, faster. It
produces two more mutual top-one pairs and a broader set of unique top-one
targets. OpenAI has a lower maximum target-reuse count.

OpenAI's distances are numerically lower throughout the distribution. This does
not mean that OpenAI is more accurate: distance and cosine values are calibrated
differently in the two embedding spaces. A threshold selected for one model
must never be copied to the other model.

As an additional, non-gating diagnostic, 50 obvious two-file groups were
identified from shared numeric filename prefixes under `images/`. This gives
100 eligible anchors. Both models retrieved the apparent partner at the same
rates:

| Heuristic paired-file recovery | OpenAI | DataComp |
|---|---:|---:|
| Recall at rank 1 | 98/100 | 98/100 |
| Recall within rank 3 | 99/100 | 99/100 |
| Recall within rank 5 | 100/100 | 100/100 |

This heuristic is encouraging, but filenames are not ground-truth labels. It
must not replace the labeled pair set prescribed by the evaluation procedure:
exact duplicates, re-encodes, edits, crops, burst frames, same-subject images,
hard negatives, and unrelated negatives.

## 7. What the reports establish

The two product reports directly establish that:

1. RawCullFB completed the same 77-query and 453-anchor workload for both
   distinct model fingerprints.
2. No incompatible image pairs were encountered.
3. Neither model exhibits obvious semantic collapse or a universal top-one
   image.
4. Both models distinguish paraphrases from unrelated queries.
5. DataComp has stronger paraphrase overlap in this run.
6. DataComp has slightly broader retrieval diversity.
7. DataComp is modestly faster for semantic queries and the all-pairs
   similarity pass.
8. The models disagree most on composition, subjective photographic quality,
   counting, spatial relations, and negation.

The product reports do **not** establish that:

- the exact bundle bytes used for product behavior are the same bytes inspected
  and parity-tested on 12 August;
- one model has higher semantic Precision@1, Precision@5, MRR, or nDCG@5;
- one model has a better duplicate-detection ROC-AUC or precision-recall AUC;
- a shared image-similarity threshold is valid;
- all catalog bytes, query bytes, software revisions, and index identities were
  frozen and archived; or
- either model has acceptable indexing throughput, memory, energy, and storage
  costs for release.

## 8. Provisional decision table

| Gate or metric | OpenAI ViT-B/32 | DataComp ViT-B/32-256 | Current decision |
|---|---:|---:|---|
| Distinct model identity in report | Pass | Pass | Both fingerprints recorded |
| Complete RawCullFB report | Pass | Pass | Both completed |
| Source identity verified against archive | Fingerprints conflict | Fingerprints conflict across inspection/report | **Blocked** |
| Minimum text parity in adjacent 12 August artifact | `1.0000` | `1.0000` | Pass for inspected candidates only |
| Minimum end-to-end parity in adjacent artifact | `0.9988` | `0.9908` | OpenAI pass; **DataComp fail** |
| Semantic collapse diagnostic | Pass | Pass | Both healthy |
| Distinct semantic rank-one images | 53 | **58** | DataComp signal |
| Largest semantic hub | 4/77 | 4/77 | Tie |
| Mean paraphrase top-ten overlap | 4.93 | **5.60** | DataComp signal |
| Precision@1 | Not labeled | Not labeled | Open |
| Precision@5 | Not labeled | Not labeled | Open |
| MRR | Not labeled | Not labeled | Open |
| nDCG@5 | Not labeled | Not labeled | Open |
| Similarity PR-AUC | Not labeled | Not labeled | Open |
| Similarity FPR at selected recall | Not labeled | Not labeled | Open |
| First-query latency | 157 ms | **130 ms** | DataComp signal |
| Warm P95 latency | 72 ms | **69 ms** | Small DataComp signal |
| Indexing throughput | Not provided | Not provided | Open |
| Peak memory | Not provided | Not provided | Open |
| Bundle and index size | Not provided | Not provided | Open |

## 9. Measured findings and recommendation

The tables in Sections 2–6 are measured or directly derived from the two
RawCullFB result files. Statements about relevance, release suitability, and
which model to prefer are recommendations constrained by missing labels and the
evidence-integrity issues above; they are not measured accuracy results.

DataComp is the more promising candidate in this unlabeled RawCullFB run. It is
more paraphrase-consistent, slightly more diverse, and modestly faster, while
retaining healthy similarity-neighbourhood behavior.

The current evidence is not sufficient to prefer DataComp for release. The
evaluation procedure explicitly requires a material **labeled-quality**
improvement before replacing the established OpenAI control. If labeled quality
is effectively tied, OpenAI remains the simpler established choice and DataComp
may remain experimental.

Independently of that product-quality comparison, DataComp fails the archived
parity gate and both candidates have unresolved cross-artifact fingerprint
binding. Those are hard blockers for using this run as release evidence.

Complete the following work before making the model decision:

1. Create a new run in which environment, source revisions, package locks,
   model metadata, runtime fingerprints, catalog manifest/content hashes, and
   query hash are captured before any evaluation command.
2. Re-run OpenAI Hugging Face and DataComp OpenCLIP parity against the exact
   bundle fingerprints used by RawCullFB. Investigate and fix DataComp's
   `0.9908` minimum rather than lowering the `0.998` gate.
3. Pool and blind-label the union of both models' top five results for every
   query using relevance grades 0, 1, and 2.
4. Calculate Precision@1, Precision@5, MRR, and nDCG@5 overall and by query
   category.
5. Prioritize manual review of composition, subjective-quality, count, spatial,
   and negation prompts because those categories differ most strongly.
6. Build the labeled image-pair benchmark and calculate ROC-AUC, PR-AUC,
   false-positive rate, false-negative rate, and a model-specific threshold.
7. Measure indexing throughput, peak memory, P99 latency, bundle size, index
   size, and energy impact under controlled conditions.
8. Revisit the provisional decision using the completed decision table.

Until those steps are complete, the defensible conclusion is:

> Both models pass the RawCullFB report-integrity and semantic-collapse sanity
> checks. DataComp shows better paraphrase consistency and small operational
> advantages, but this archived run is not release-qualifying: DataComp fails
> parity, bundle identity is not consistently bound across artifacts, and
> blinded relevance and similarity labels are missing.

## 10. Artifact map and superseded-results policy

The report's evidence files are the named artifacts under the immutable run
directory shown at the top of this page. In particular:

| Conclusion type | Generated artifacts |
|---|---|
| Environment and source identity | `environment.txt`, both `*-metadata.json`, `model-metadata-sha256.txt`, both `*-model-inspection.txt` |
| Fixture and source parity | `fixture-sha256.txt`, both `*-reference-sha256.txt`, both normal and strict `*-parity*.txt` files |
| Product behavior | `openai-rawcullfb-results.txt`, `datacomp-rawcullfb-results.txt`, `catalog-files.txt`, `semantic-query-sha256.txt` |
| Missing required evidence | catalog content/aggregate digests, package locks, hardware model/RAM, blind relevance labels, calibrated similarity labels, complete operational measurements |

Treat this directory and page as immutable historical evidence. A later
evaluation must:

1. create a new UTC-named run directory and a new dated report;
2. record `supersedes` and `superseded_by` links in the two reports, without
   replacing old artifacts;
3. explain every changed model, source, package, fixture, catalog, query,
   hardware, threshold, and analysis method;
4. point the current release recommendation only at the newest run that passes
   every applicable gate; and
5. retain failed and incomplete runs so that a later result cannot silently
   erase contrary evidence.
