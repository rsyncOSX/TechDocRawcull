+++
author = "Thomas Evensen"
title = "Publishing and Testing RawCull AI Models"
date = "2026-08-22"
lastmod = "2026-09-26"
description = "Current model-pack identities, release procedure, and AI Analysis test-release checks."
weight = 30
tags = ["ai", "release", "models", "background-assets"]
categories = ["technical details"]
+++

# Publishing and Testing RawCull AI Models

This page describes the **3.2.6 code and model catalog reviewed on September 26,
2026**. It is a release runbook, not a claim that a particular build or asset-pack
version has passed App Review. Check App Store Connect and the signed build before
making an availability claim.

RawCull uses three managed model packs. The App Store configuration requests
Apple-hosted Managed Background Assets; the Direct/Developer ID configuration
continues to point to the historical self-hosted `v3` manifest. That manifest
does not provide the current managed Qwen pack; do not use that build to claim
a complete managed Objects installation. The
hosting route, asset-pack version, app version/build, model revision, and
PhotoAIKit revision are separate identities. Do not replace one with another.

## Current model and code identities

| Model | Asset-pack ID | Installed path | Archive bytes | Archive SHA-256 |
|---|---|---|---:|---|
| DataComp CLIP | `rawcull-clip-datacomp` | `Models/CLIP-DataComp` | 282,967,354 | `994939e74dbbe9844214d509267642939f5ddc535ae3bce4be36c8855bdfa600` |
| Meta SAM 3 | `rawcull-sam3` | `Models/SAM3` | 1,542,689,931 | `08c9a4f58242d6eecaa322d65521fd788589ea682aa92a5cea03fa1e2f2681d4` |
| Qwen3-VL-2B-Instruct | `rawcull-qwen3-vl-2b` | `Models/Qwen/qwen3_vl_2b` | 3,754,599,603 | `115eebbfdff7cb688b26dd6e2dd6c110b3fce5d27f6d5e8f40f69192d1ca2364` |

These hashes and sizes are the **recorded Apple-hosted archive evidence** in
`RawCullAIModelDownloadCatalog` and `ModelAssets/README.md`; they do not prove
that a particular tester installed those bytes. The catalog marks all three
packs ready and includes them in production. SAM 3 requires explicit acceptance
of its bundled licence. OpenAI CLIP is excluded from production, and
EfficientSAM is not a production download.

The catalog records upstream revisions `4afec35ffe57a943d569ff7ee888061830164da8`
for DataComp, `3c879f39826c281e95690f02c7821c4de09afae7` for SAM 3, and
`78448d793a7eb2f7a987a1da76d464384aa1becd` for Qwen. The 3.2.6 workplan
pins PhotoAIKit revision `77cc1d84a5d98a485caa15be102c8a55eb3d7698`.
Read the actual `Package.resolved`, installed pack record, and signed app build
when recording a test result; source labels alone are not runtime fingerprints.

## What each model does

- **DataComp CLIP:** image embeddings for similarity, burst grouping, and
  semantic search. Similarity is relative ranking, not a probability that a
  photograph contains an object.
- **SAM 3:** masks for prompted visible subjects in Deep Review and separate
  candidate instances in **AI Analysis → Objects**. Its retained count is a
  count of matches for the selected concepts after filtering and deduplication,
  not an inventory of everything in the scene.
- **Qwen3-VL-2B-Instruct:** local photo critique in **Qwen Vision**. In
  **Objects**, it first proposes visible concepts in Automatic mode, then
  assesses a board containing the overview and numbered SAM 3 crops. Specific
  Concepts mode lets the user enter concepts directly. Qwen's text and its
  displayed confidence are model output, not independently verified facts.

The app supports selected and tagged images. A failed structured Objects
assessment remains visible and retryable; cached masks may be reused when their
source and model keys still match. Qwen Vision may display free-form answers
when a request or response does not fit its structured photo-assessment schema.
The photographer remains responsible for culling decisions.

## Decision for an Objects test release

The current pipeline has successful in-app Automatic runs on selected puffin and
mixed-subject photographs. The September 24 packaged-model rerun produced
structured assessments with all expected board IDs for eight puffin photos in
both Automatic and Specific Concepts modes. These are useful functional checks,
not a visual-accuracy benchmark or a clean-install TestFlight result.

Known examples to disclose and retest:

- A two-puffin photograph produced two retained SAM 3 objects, but Qwen's scene
  summary claimed a third puffin. Its object-specific text described the two
  visible birds correctly. The result was marked Complete with 95% Qwen-reported
  confidence because structural validation cannot establish visual truth.
- In another two-puffin photograph, clicking the numbered objects showed a
  reported crop/description mismatch. The source may be Qwen board grounding
  or the app's crop association; it has not been isolated.
- Earlier two-bird tests also produced swapped or nearly repeated descriptions.
  One-object examples and valid JSON do not settle this risk.

A monitored user test is reasonable if the release describes Objects as
**advisory and under evaluation**, gives a way to report inaccurate results,
and does not promise exhaustive detection, correct counts in generated prose,
or verified photographic judgments. These known issues should remain open in
the engineering release record. A public test is a way to gather evidence; it
is not itself evidence that the feature has passed the visual-quality gate.

## Before sending a build to testers

1. Record the exact Git commit, RawCull marketing version and build number,
   macOS version, Xcode configuration, PhotoAIKit revision, and model-pack IDs
   and versions. The 3.2.6 workplan refers to app/downloader build 389, but
   confirm the values in the *signed artifact*.
2. Run `make verify-model-provenance`, `make verify-ai-import-boundary`, the
   model-catalog and release-metadata tests, focused Qwen/Object tests, and
   the normal release test plan. Save the
   result; do not infer that a prior test run covered the new build.
3. Build with the `AppStore` configuration for TestFlight. Confirm both the app
   and downloader extension use the same App Group and Apple-hosted settings.
   The App Store plist has `BAUsesAppleHosting = YES` and no self-hosted
   `BAManifestURL`.
4. In App Store Connect, verify the exact versions of all three packs have
   completed processing and are available to the intended TestFlight audience.
   A local `.ready` catalog value or processed archive does not establish
   external-test or App Store approval.
5. On a clean test account, install through TestFlight; download CLIP, SAM 3,
   and Qwen through **Settings → AI → Download AI Models**. Confirm licence
   acceptance, activation, an actual inference, relaunch rediscovery, removal,
   and reinstall. Cancel a download and remove a model during active analysis
   to check that the app stays stable.
6. Run **SAM 3 + CLIP**, **Qwen Vision**, and **Objects** on selected and tagged
   photos. For Objects, test Automatic and Specific Concepts, no match, one
   subject, several same-category subjects, mixed categories, overlap, small
   subjects, partial occlusion, and RAW/JPEG versions of the same scene. Use
   **Clear Results** before rerunning an already Complete image with different
   concepts or criteria. Compare every number, crop, mask, description, and
   relationship with the source.
7. Check result-table responsiveness, cancellation latency, memory use, keyboard
   navigation, and accessibility on the signed build. The September 24
   in-process eight-photo run reached a 9.47 GiB process peak; that value is
   not a release-build memory measurement.
8. Provide testers a feedback channel and ask for the photo (only if they agree
   to share it), concept mode/text, visible source truth, selected object ID,
   crop and description, app build, macOS version, and installed model versions.
   Do not add private photos or raw model responses to ordinary logs or Git.

If a failure is reproduced, classify it as detection/mask, object-to-crop
mapping, Qwen grounding, schema/decode, model lifecycle, cancellation, or UI.
Record its frequency and impact before deciding whether to change prompt,
model, board, decoder, or presentation. Do not convert a factual contradiction
into a generic “success” metric merely because the response parsed.

## Publishing a new or revised model pack

This section applies when the **model asset changes**. Shipping the existing
packs in a new app build does not by itself require repackaging them.

1. Keep the permanent pack ID for a new version of the same model. For a new
   model family, allocate a new ID accepted by App Store Connect, and update
   the packaging manifest, Swift catalog, notices, provenance, and tests.
2. Freeze the upstream checkpoint, conversion tools, tokenizer/support files,
   complete applicable licences, notices, and checksums. Verify that the
   exporter consumed the pinned source, rather than merely recording a nearby
   downloaded file.
3. Generate a Managed Background Assets `.aar` with the release Xcode tools.
   Record its byte size and SHA-256. Never edit the archive after recording the
   digest. Keep binaries and credentials out of Git.
4. Update `ModelAssets/manifest.template.json`,
   `RawCullAIModelDownloadCatalog.swift`, the matching `PROVENANCE.json` and
   `NOTICE.md`, inclusion switches, and the model/release tests. The installed
   destination must match across the manifest and catalog.
5. Run `make verify-model-provenance`, the focused tests, and the release
   preflight. Upload the archive to its existing App Store Connect pack record,
   wait for processing, and record the Apple-assigned version and Internal Beta
   Release state. An internal beta is not automatically available externally.
6. Test a clean download and real inference with the signed build and exact
   pack version. Verify relaunch, removal/reinstall, cancellation, and upgrade
   from the previous installed pack. Submit the intended app and pack versions
   for their required beta or App Store review only after that evidence exists.

The repository runbook [`Docs/newmodels.md`](https://github.com/rsyncOSX/RawCull/blob/version-3.2.6/Docs/newmodels.md)
contains the packaging manifest, `xcrun altool`, provenance, and TestFlight
commands. Use its current revision with the release checkout. The older
self-hosted `v3` and draft `v4` recipes are historical; do not use their IDs,
URLs, or manual Qwen setup instructions for the Apple-hosted 3.2.6 catalog.
