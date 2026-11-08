+++
title = "AI Diagnostics and Validation"
date = "2026-10-16"
lastmod = "2026-10-31"
weight = 70
description = "Trace AI failures and retained evidence from structured validation to opt-in model qualification."

reviewed_commit = "a5f35b05c1e206ed4d6aa599522f5c8622b5308a"
reviewed_version = "3.4.0"
reviewed_build = 434
reviewed_on = "2026-11-08"
review_scope = "source delta and reference verification"
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
| Similarity/semantic | [SimilarityScoringModel.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/Similarity/SimilarityScoringModel.swift), [RawCullVisionSimilarityService.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/Similarity/RawCullVisionSimilarityService.swift) | Active backend, valid artifact coverage, descriptor/source mismatch and per-file failures |
| Deep Review | [DeepAIReviewFeature.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/DeepReview/DeepAIReviewFeature.swift), [SubjectMaskFocusScorer.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/DeepReview/SubjectMaskFocusScorer.swift) | Admitted candidates, mask foreground, relative detail values and recommendation limits |
| Standalone Qwen | [RawCullQwenAnalysisFeature.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/Qwen/RawCullQwenAnalysisFeature.swift) | First response, bounded repair, cancellation and model generation |
| Objects | [RawCullObjectAnalysisFeature.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/ObjectAnalysis/RawCullObjectAnalysisFeature.swift), [ObjectAnalysisResponseDecoder.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/ObjectAnalysis/ObjectAnalysisResponseDecoder.swift) | Concept ownership, numbered board/crop mapping, missing IDs, paired evidence and focus abstention |
| Combined | [CombinedReviewWorkExecution.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/CombinedReview/CombinedReviewWorkExecution.swift), [ReviewDiagnostics.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/CombinedReview/ReviewDiagnostics.swift) | Stage dependencies, validation code, source/region identity, admitted evidence and incomplete coverage |

For Objects, a no-match segmentation result is different from an invalid board
response. Retry Failed is a later operation and may reuse segmentation only if
source/model/concept/cache identity remains valid. The automatic response repair
is bounded inside one operation. After that repair, structurally valid unsupported
focus claims may be removed while preserving the other supported object findings.

## Combined Review stores a typed technical record

[ReviewArtifactStore.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Intelligence/CombinedReview/ReviewArtifactStore.swift) defaults to
`Application Support/RawCull/AnalysisArtifacts/CombinedReview`. Its run manifests
record work states, compatibility identities and artifact keys. Stage artifacts,
retained input PNGs and opt-in rejected responses are distinct storage categories.
The input budget defaults to 256,000,000 bytes. Compact retention does not erase
typed evidence; exact-input retention preserves the submitted image before model
preprocessing, not the original sensor data or the final model tensor.

[CombinedReviewView.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCull/Views/AIAnalysis/CombinedReviewView.swift) exposes Run history & diagnostics. The Evidence
workspace separates Findings, Coverage & limits and Technical record. Inspect
accepted observations, failure/skip reasons and report coverage even when the
worker has completed. Missing retained input images do not erase saved reports.
Resume additionally requires current compatible source/model/stage contracts;
Rerun creates a new snapshot using current controls.

## Choose a verification level deliberately

| Level | Source/command | What it establishes |
| --- | --- | --- |
| Fast regression gate | `make test-smoke`, `TestManifests/SmokeTests.txt` | The checked-in smoke selection and its enumeration contract |
| Focused model-free tests | [ReviewRunContractTests.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/ReviewRunContractTests.swift), [ObjectAnalysisBoundaryTests.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/ObjectAnalysisBoundaryTests.swift), [CombinedReviewPresentationTests.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/CombinedReviewPresentationTests.swift) | Contract validation, ownership, abstention and presentation behavior with fixtures |
| Standalone model diagnostics | [Scripts/RunAIAnalysis.py](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Scripts/RunAIAnalysis.py) | SAM/Deep Review, Qwen and Objects plus a separate CLIP probe; not Combined |
| Combined model diagnostics | [Scripts/RunCombinedReviewSix.py](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Scripts/RunCombinedReviewSix.py), [CombinedReviewRealModelTests.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/CombinedReviewRealModelTests.swift) | Opt-in Combined stages and selection comparison on the supplied cohort |
| Release input probe | [RawCullReleaseTests/CombinedReviewInputProbe.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullReleaseTests/CombinedReviewInputProbe.swift), `make combinedinputstest` | The release probe's admitted input/model boundary, not all photographic judgments |

Read the current script arguments and opt-in environment variables before a
model run. Record the app commit/build, resolved packages, macOS/hardware, model
fingerprints, source-file hashes, source preference, render sizes, run contract,
retention settings and result/log locations. A directory name is not an input
inventory: different cohorts may have occupied the same directory.

`Docs/ai-verification-summary.md` has been removed from the current application
tree. Earlier references to its v21 evaluations describe historical runs; they
do not qualify the current v22 pipeline or this build. Use the checked-in
diagnostic scripts and test sources above to prepare a new evaluation. This documentation review did not rerun
model inference. Keep retained photographs, raw responses and private diagnostics
out of public reports unless explicitly intended for sharing.

## Regression tests follow ownership boundaries

`RawCullTests/TEST_ARCHITECTURE.md` describes isolated fixtures, test plans and
manifest selection. [TestIsolationHelpers.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/TestIsolationHelpers.swift) supplies unique temporary
settings and cache roots. Tests must not silently fall back to the user's
production thumbnail storage, model state or photograph collection.

See [Combined Review]({{< relref "aicombined.md" >}}) for stage semantics and
[Concurrency]({{< relref "../concurrency.md" >}}) for cancellation and stale-result
publication guards.

## Presentation regressions added with the viewer refactor

[OverlayPresentationModelTests.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/OverlayPresentationModelTests.swift) exercises late focus
and outline completions plus debounce cancellation.
[ReviewViewBoundaryTests.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/ReviewViewBoundaryTests.swift) checks section observation
and renders selected components at 520 and 1024 points.
[ZoomKeyboardControllerTests.swift](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/RawCullTests/ZoomKeyboardControllerTests.swift) checks inspection
shortcut suppression. These model-free contracts answer different questions
from image-quality evaluation; neither a rendering snapshot nor valid JSON
proves the model chose the intended subject.
