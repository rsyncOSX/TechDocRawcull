+++
author = "Thomas Evensen"
title = "New RawCull AI models"
linkTitle = "New RawCull AI models"
date = "2026-08-10"
description = "Release runbook for publishing DataComp CLIP, OpenAI CLIP, and Meta SAM 3."
tags = ["ai", "models", "downloads", "clip", "sam3", "background-assets", "self-hosting", "apple-hosting"]
categories = ["technical details"]
weight = 31
+++

# Publishing new RawCull AI models

This runbook publishes exactly three optional models:

| Model | Asset-pack ID | Installed destination |
|---|---|---|
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` |
| OpenAI CLIP | `no.blogspot.RawCull.models.clip-openai` | `Models/CLIP-OpenAI` |
| Meta SAM 3 | `no.blogspot.RawCull.models.sam3` | `Models/SAM3` |

SigLIP2 and EfficientSAM are deliberately excluded. Do not add them to the
release staging tree, packaging manifests, download manifest, production
catalogue, settings UI, notices, or tests.

The examples use a new immutable `v2` release in
[`RawCull-AI-Models`](https://github.com/rsyncOSX/RawCull-AI-Models/releases).
Tag names and GitHub release URLs are case-sensitive. If another tag is chosen,
replace `v2` everywhere and keep both RawCull manifest URLs identical.

## 1. Build the three canonical bundles

Follow [AI Model Download Service](../aimodeldownloads/) for the pinned source
checks, exact PhotoAIKit commands, runtime validation, and packaging layout.
The canonical release outputs are:

```text
CLIP-DataComp/
├── metadata.json
├── tokenizer/
└── ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel/

CLIP-OpenAI/
├── metadata.json
├── tokenizer/
└── clip-vit-base-patch32_float16_static.aimodel/

SAM3/
├── metadata.json
├── tokenizer/
└── sam3_float16.aimodel/
```

Use PhotoAIKit revision
`6e3216027b267c27ccaf99d334807b18ea1aaec9`, or document and review the exact
later revision actually used. Release CLIP bundles must use Float16, static
batch dimensions, metadata version `0.4`, separate `image_encoder` and
`text_encoder` functions, and corrected bicubic preprocessing. The SAM 3 bundle
must use metadata version `0.3`.

DataComp must be exported with:

```sh
uv run --script Tools/export_clip.py \
  --model openclip-datacomp \
  --architecture ViT-B-32-256 \
  --pretrained datacomp_s34b_b86k \
  --output-dir /path/to/export \
  --bundle-name CLIP-DataComp \
  --dtype float16
```

Do not use `--pretrained open_clip_model.safetensors`. The historical bundle
with `open_clip_model.safetensors` in its runtime name produced collapsed
semantic rankings. The corrected tested bundle uses the registered
`datacomp_s34b_b86k` identity and runtime filename.

Keep every `*_source.aimodel` as private conversion evidence. Never select it in
a packaging manifest or place it in a downloadable pack.

## 2. Validate model behavior before packaging

For each bundle:

1. Confirm `metadata.json` selects the optimized runtime in `assets.main`.
2. Recompute the runtime directory fingerprint with
   `PhotoAIKit/Tools/model_fingerprint.py` and compare it with
   `asset_fingerprints.main`.
3. Run `swift test` for the exact PhotoAIKit revision used to convert it.
4. Install the complete candidate in a clean RawCull or RawCullFB model path.
5. Rebuild all model-specific indexes after every model or fingerprint change.

For both CLIP models, run PyTorch/Core AI parity and then the same RawCullFB
`semantictest.txt`. The report must include semantic-search rankings and
image-to-image similarity comparisons. Review rankings, score spread, repeated
results, failures, and elapsed time. Do not compare models against a reused
index.

For SAM 3, test text prompts, mask dimensions and placement, licence acceptance,
relaunch, and removal.

## 3. Clear release blockers

Do not mark a model `.ready` because it works locally.

### DataComp CLIP

Confirm that the new archive uses the pinned DataComp checkpoint and corrected
runtime filename. Replace the existing archive checksum and byte count whenever
the bundle or packaging changes. Update its notice and provenance records; do
not reuse values from the old custom-named runtime.

### OpenAI CLIP

Before enabling the OpenAI pack:

1. bind the pinned checkpoint revision and source SHA-256 to the conversion
   evidence;
2. confirm that the applicable terms cover the exact trained weights and their
   redistribution, not only source code and tokenizer files;
3. record the PhotoAIKit revision, command, tokenizer checksum, runtime
   fingerprint, AAR checksum, and byte count;
4. include the complete required notices in `Notices/CLIP-OpenAI`.

Leave the descriptor blocked and omit its pack from a public manifest while
weight-level redistribution clearance is unresolved.

### Meta SAM 3

Before enabling the SAM 3 pack:

1. preserve the accepted gated-source revision and source SHA-256 as private
   evidence;
2. confirm that an ungated GitHub release of the converted derivative complies
   with the SAM License and Meta's gated checkpoint access conditions;
3. record the PhotoAIKit revision, command, tokenizer checksum, runtime
   fingerprint, AAR checksum, and byte count;
4. include the complete SAM License and notices in `Notices/SAM3`;
5. keep explicit in-app licence acceptance enabled.

Technical provenance does not resolve the redistribution decision. Omit SAM 3
from the public manifest until that review is complete.

## 4. Prepare release staging

The staging tree must contain only the three approved runtime bundles and their
notice catalogues:

```text
ModelAssets/Release/
├── Models/
│   ├── CLIP-DataComp/
│   ├── CLIP-OpenAI/
│   └── SAM3/
├── Notices/
│   ├── CLIP-DataComp/
│   ├── CLIP-OpenAI/
│   └── SAM3/
├── Packaging/
│   ├── clip-datacomp.json
│   ├── clip-openai.json
│   └── sam3.json
└── Output/
```

Each packaging manifest selects only:

- the bundle's `metadata.json`;
- its `tokenizer` directory;
- its optimized runtime `.aimodel` directory;
- its matching notice directory.

The DataComp selector must be:

```text
Models/CLIP-DataComp/ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel
```

If any checked-in packaging manifest still selects
`ViT-B-32-256-open_clip_model.safetensors_float16_static.aimodel`, it is stale
and must be corrected before packaging.

## 5. Generate and record the AAR files

Check the selected Xcode tool before every release:

```sh
xcrun --find ba-package
xcrun ba-package --version
xcrun ba-package help package
```

Run one package operation per model from the staging root:

```sh
cd /Users/thomas/ModelAssets/Release

xcrun ba-package package Packaging/clip-datacomp.json \
  --output-path Output/clip-datacomp.aar
xcrun ba-package package Packaging/clip-openai.json \
  --output-path Output/clip-openai.aar
xcrun ba-package package Packaging/sam3.json \
  --output-path Output/sam3.aar

shasum -a 256 Output/*.aar
stat -f '%N %z bytes' Output/*.aar
```

Do not copy old archive checksums into the catalogue. A changed model,
metadata file, tokenizer, notice, selector, or packaging tool can change the
archive. Record the newly generated SHA-256 and exact byte count for every pack.

## 6. Generate the download manifest

Create a self-hosted manifest from the exact approved AAR files. The generated
manifest must contain only packs that have passed both technical and legal
release gates. It may contain one, two, or all three packs while reviews are in
progress; RawCull must expose only the same ready set.

Verify every entry before publishing:

- exact asset-pack ID;
- monotonically increasing asset-pack version;
- exact download byte count;
- tag-pinned HTTPS archive URL;
- correct destination selected by RawCull's catalogue.

Do not use GitHub's `/releases/latest/download/` redirect. It excludes
prereleases and makes the resolved version less explicit. Use URLs under:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/
```

## 7. Publish the immutable GitHub release

Create the `v2` tag and release, then verify its state:

```sh
gh release view v2 \
  --repo rsyncOSX/RawCull-AI-Models \
  --json tagName,isDraft,isPrerelease
```

`tagName` must be `v2` and `isDraft` must be `false`. A tag-pinned URL can use
a published prerelease, but record that decision. Upload files in this order:

1. all approved AAR files;
2. download each AAR anonymously and verify its checksum and size;
3. upload `manifest.json` last;
4. download and inspect the published manifest anonymously.

```sh
curl --fail --location --output /tmp/rawcull-v2-manifest.json \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/manifest.json
jq empty /tmp/rawcull-v2-manifest.json
```

Never replace files under a published tag. Publish a corrected immutable tag,
for example `v2.0.1`, and update both RawCull manifest URLs.

## 8. Update RawCull's production catalogue

RawCull currently has these inclusion switches:

```swift
static let includeOpenAICLIP = false
static let includeDataCompCLIP = true
static let includeSAM3 = false
```

This correctly exposes only the currently ready DataComp pack. After each new
pack is published and cleared, change only its switch to `true`. The final
three-model configuration is:

```swift
static let includeOpenAICLIP = true
static let includeDataCompCLIP = true
static let includeSAM3 = true
```

For every rebuilt archive, update its production descriptor with actual values:

```swift
upstreamRevision: "<verified immutable source revision>",
expectedArchiveSHA256: "<64 lowercase hexadecimal characters>",
downloadByteCount: <exact AAR bytes>,
installedByteCount: <exact installed bytes or nil>,
releaseReadiness: .ready,
```

Do not change `.blocked` to `.ready` until the corresponding pack is present in
the published manifest and every release gate is complete. Keep the verified SAM
3 licence resource, SHA-256, and `requiresExplicitAcceptance: true` synchronized
with its notice catalogue.

## 9. Point both configurations to the release

Update both locations to the same exact URL:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/manifest.json
```

The locations are:

- `RawCullAIModelDownloadSource.productionManifestURL` in
  `RawCullAIModelDownloadService.swift`;
- `BAManifestURL` in `RawCull-Info.plist`.

Keep `BAUsesAppleHosting` false for GitHub self-hosting. Do not point RawCull to
the new manifest until every referenced archive is anonymously downloadable and
verified.

## 10. Update provenance, documentation, and tests

For every released pack, update `ModelAssets/Notices/<model>/PROVENANCE.json`
and `NOTICE.md` with the source revision, source checksum, PhotoAIKit revision,
command, runtime filename, model fingerprint, AAR checksum, byte count, and
review status. Update `ModelAssets/README.md` to list the exact release URL and
available packs.

Tests must verify:

- the catalogue contains exactly the enabled ready models;
- every ready model has an exact archive checksum and byte count;
- bundled licence texts match their recorded checksums;
- both manifest URL locations use the same tag;
- provenance and notice records describe the generated archives;
- excluded models do not appear in settings or the production catalogue.

Run the focused download and release-metadata tests, then the full suite:

```sh
xcodebuild \
  -project RawCull.xcodeproj \
  -scheme RawCull \
  -destination 'platform=macOS' \
  -only-testing:RawCullTests/RawCullAIModelDownloadsTests \
  -only-testing:RawCullTests/ReleaseMetadataTests \
  test

xcodebuild \
  -project RawCull.xcodeproj \
  -scheme RawCull \
  -destination 'platform=macOS' \
  test
```

## 11. Perform a clean-machine test

Before shipping:

1. confirm Settings lists only the enabled subset of DataComp, OpenAI, and SAM
   3;
2. download each enabled model through Managed Background Assets;
3. rebuild each CLIP index and test semantic search and similarity;
4. verify that DataComp and OpenAI artifacts never cross-load;
5. accept the SAM 3 licence and verify segmentation;
6. relaunch and verify installation and selection persistence;
7. remove each pack independently;
8. interrupt a download and verify retry;
9. verify Vision feature-print similarity remains the safe fallback when no
   CLIP model is available.

## Release checklist

- [ ] Exactly DataComp CLIP, OpenAI CLIP, and SAM 3 are in release scope.
- [ ] DataComp uses `datacomp_s34b_b86k`, not the custom filename preset.
- [ ] Exact upstream revisions and source checksums are recorded.
- [ ] The exact PhotoAIKit revision and conversion commands are recorded.
- [ ] Runtime fingerprints match `metadata.json`.
- [ ] CLIP parity, semantic search, and image similarity are reviewed.
- [ ] SAM 3 segmentation and licence acceptance are tested.
- [ ] OpenAI and SAM 3 redistribution blockers are resolved before release.
- [ ] Only optimized runtime assets are packaged.
- [ ] Fresh AAR checksums and byte counts are in provenance and RawCull.
- [ ] Archives are uploaded and verified before `manifest.json`.
- [ ] Both RawCull manifest URLs point to the same immutable tag.
- [ ] Inclusion flags and readiness values match the published manifest.
- [ ] Focused, full, and clean-machine tests pass.

## Rollback

Before an app release, restore both manifest URLs and catalogue readiness to the
last known-good release if the new model release fails. After publication, do
not mutate an existing tag. Publish a corrected tag, verify it, and update both
RawCull URLs together.
