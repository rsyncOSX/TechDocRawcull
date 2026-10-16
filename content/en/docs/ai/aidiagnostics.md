+++
title = "AI Diagnostics and Validation"
date = "2026-10-16"
lastmod = "2026-10-16"
weight = 70
description = "Trace AI failures and retained evidence from structured validation to opt-in model qualification."
+++

# AI Diagnostics and Validation

A successful model generation, a valid structured response and a photographically
correct conclusion are different outcomes. RawCull can verify schemas, ownership,
source identity and evidence references in code. Visual accuracy still requires
inspection of the original and the admitted crop. Confidence from Qwen, SAM or
CLIP is not a calibrated measure of sharpness.

## Start with the workflow that failed

| Workflow | Entry points | Inspect |
| --- | --- | --- |
| Similarity/semantic | [SimilarityScoringModel.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/Similarity/SimilarityScoringModel.swift), [RawCullVisionSimilarityService.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/Similarity/RawCullVisionSimilarityService.swift) | Active backend, valid artifact coverage, descriptor/source mismatch and per-file failures |
| Deep Review | [DeepAIReviewFeature.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/DeepReview/DeepAIReviewFeature.swift), [SubjectMaskFocusScorer.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/DeepReview/SubjectMaskFocusScorer.swift) | Admitted candidates, mask foreground, relative detail values and recommendation limits |
| Standalone Qwen | [RawCullQwenAnalysisFeature.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/Qwen/RawCullQwenAnalysisFeature.swift) | First response, bounded repair, cancellation and model generation |
| Objects | [RawCullObjectAnalysisFeature.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/ObjectAnalysis/RawCullObjectAnalysisFeature.swift), [ObjectAnalysisResponseDecoder.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/ObjectAnalysis/ObjectAnalysisResponseDecoder.swift) | Concept ownership, numbered board/crop mapping, missing IDs, paired evidence and focus abstention |
| Combined | [CombinedReviewExecution.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/CombinedReview/CombinedReviewExecution.swift), [ReviewDiagnostics.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/CombinedReview/ReviewDiagnostics.swift) | Stage dependencies, validation code, source/region identity, admitted evidence and incomplete coverage |

For Objects, a no-match segmentation result is different from an invalid board
response. Retry Failed is a later operation and may reuse segmentation only if
source/model/concept/cache identity remains valid. The automatic response repair
is bounded inside one operation. After that repair, structurally valid unsupported
focus claims may be removed while preserving the other supported object findings.

## Combined Review stores a typed technical record

[ReviewArtifactStore.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Intelligence/CombinedReview/ReviewArtifactStore.swift) defaults to
`Application Support/RawCull/AnalysisArtifacts/CombinedReview`. Its run manifests
record work states, compatibility identities and artifact keys. Stage artifacts,
retained input PNGs and opt-in rejected responses are distinct storage categories.
The input budget defaults to 256,000,000 bytes. Compact retention does not erase
typed evidence; exact-input retention preserves the submitted image before model
preprocessing, not the original sensor data or the final model tensor.

[CombinedReviewView.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCull/Views/AIAnalysis/CombinedReviewView.swift) exposes Run history & diagnostics. The Evidence
workspace separates Findings, Coverage & limits and Technical record. Inspect
accepted observations, failure/skip reasons and report coverage even when the
worker has completed. Missing retained input images do not erase saved reports.
Resume additionally requires current compatible source/model/stage contracts;
Rerun creates a new snapshot using current controls.

## Choose a verification level deliberately

| Level | Source/command | What it establishes |
| --- | --- | --- |
| Fast regression gate | `make test-smoke`, `TestManifests/SmokeTests.txt` | The checked-in smoke selection and its enumeration contract |
| Focused model-free tests | [ReviewRunContractTests.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCullTests/ReviewRunContractTests.swift), [ObjectAnalysisBoundaryTests.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCullTests/ObjectAnalysisBoundaryTests.swift), [CombinedReviewPresentationTests.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCullTests/CombinedReviewPresentationTests.swift) | Contract validation, ownership, abstention and presentation behavior with fixtures |
| Standalone model diagnostics | [Scripts/RunAIAnalysis.py](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/Scripts/RunAIAnalysis.py) | SAM/Deep Review, Qwen and Objects plus a separate CLIP probe; not Combined |
| Combined model diagnostics | [Scripts/RunCombinedReviewSix.py](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/Scripts/RunCombinedReviewSix.py), [CombinedReviewRealModelTests.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCullTests/CombinedReviewRealModelTests.swift) | Opt-in Combined stages and selection comparison on the supplied cohort |
| Release input probe | [RawCullReleaseTests/CombinedReviewInputProbe.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCullReleaseTests/CombinedReviewInputProbe.swift), `make combinedinputstest` | The release probe's admitted input/model boundary, not all photographic judgments |

Read the current script arguments and opt-in environment variables before a
model run. Record the app commit/build, resolved packages, macOS/hardware, model
fingerprints, source-file hashes, source preference, render sizes, run contract,
retention settings and result/log locations. A directory name is not an input
inventory: different cohorts may have occupied the same directory.

The maintained source report `Docs/ai-verification-summary.md` records earlier
installed-model evaluations and their limits. Its dated v21 passes remain
historical evidence; the current pipeline is v22, so they do not qualify a new
build or prove general visual accuracy. This documentation review did not rerun
model inference. Keep retained photographs, raw responses and private diagnostics
out of public reports unless explicitly intended for sharing.

## Regression tests follow ownership boundaries

`RawCullTests/TEST_ARCHITECTURE.md` describes isolated fixtures, test plans and
manifest selection. [TestIsolationHelpers.swift](https://github.com/rsyncOSX/RawCull/blob/23de7bec3063cab0f8466e8367921841c5ab5a1d/RawCullTests/TestIsolationHelpers.swift) supplies unique temporary
settings and cache roots. Tests must not silently fall back to the user's
production thumbnail storage, model state or photograph collection.

See [Combined Review]({{< relref "aicombined.md" >}}) for stage semantics and
[Concurrency]({{< relref "../concurrency.md" >}}) for cancellation and stale-result
publication guards.
