+++
author = "Thomas Evensen"
title = "Publishing New AI Model Releases"
date = "2026-08-22"
lastmod = "2026-09-15"
description = "Release runbook for advancing RawCull's Managed Background Assets model release."
weight = 30
tags = ["ai", "release", "models", "background-assets"]
categories = ["technical details"]
+++

# Publishing New RawCull AI Models

Production currently uses model release `v3`. The next manifest release is
reserved as `v4`. At the 2026-09-15 verification point, GitHub had no published
`v4` tag or manifest, so this runbook must not be read as evidence that `v4` is
already downloadable.

The release tag, each pack's manifest version, RawCull's marketing/build
version, model architecture version, provenance `catalog_version`, and macOS
version are independent values. Do not update them with a global replacement.

## Stable Model Identities

| Model | Asset-pack ID | Manifest destination | Source directory |
|---|---|---|---|
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` | `CLIP-DataComp` |
| Meta SAM 3 | `no.blogspot.RawCull.models.sam3` | `Models/SAM3` | `SAM3` |

Keep IDs and destinations stable across release versions unless intentionally
creating a different pack or moving its installed contents. The generated
manifest must agree with `RawCullAIModelDownloadCatalog.production` exactly.

Qwen3-4B is not in this table because RawCull does not currently declare a Qwen
download descriptor or import a PhotoAIKit language-model provider. The build
recipe later on this page creates a developer Core AI LLM bundle; adding it to
`v4` is a separate product and integration decision.

## Verified Baseline For v4

The release input must start from known-good evidence. On 2026-09-15, the
published `v3` manifest and both archives were downloaded again and checked
byte-for-byte:

| Artifact | Manifest version | Bytes | SHA-256 |
|---|---:|---:|---|
| `manifest.json` | — | 771 | `a7e6d97d9055288cd430f80a30416e59705557c97d9d0de0cf2ad226415bc2b4` |
| DataComp CLIP pack | 3 | 282,966,632 | `cf433dcd199b44635a4ff0260bd8e79177e4907a4cfcb2f72043066b8cbe4ef7` |
| Meta SAM 3 pack | 3 | 1,542,689,157 | `dd0adc697060129435d4a70515011a37f547e1ad7cd530d943341bf3ca9184a9` |

The manifest IDs, URLs, versions, and `downloadSize` values agree with the
release assets and RawCull's production catalog. These are verified `v3`
values, not values to copy into a rebuilt `v4` archive.

RawCull resolves PhotoAIKit release `v2.4.1` at revision
`20e57359603313af7c2d38cae3e8b6e37f8838ef`. That release includes the updated
SAM 3 multi-subject result handling and pins `apple/coreai-models` at
`cc812078731871574c9b2eb620aa40734c4b89ee`. Validate every rebuilt model with
that exact resolved package graph, or record the newer graph if the pin changes
before publication.

## 1. Freeze And Verify Each Pack

For every released model:

1. build the final model bundle and required tokenizer/support resources;
2. record immutable upstream revisions and source-file checksums where available;
3. record the converted-model fingerprint and conversion/dependency revisions;
4. include complete applicable licence and third-party notice files;
5. validate inference with the exact PhotoAIKit revision RawCull resolves;
6. freeze the source directory selected by `manifest.template.json`;
7. generate the deployable asset pack with the release Xcode tools;
8. measure SHA-256 and byte size from that exact generated archive.

For DataComp, preserve the OpenCLIP/DataComp, tokenizer, and Apple conversion
notices and validate similarity plus semantic-search embeddings. For SAM 3,
preserve the complete SAM License and conversion notice, verify explicit licence
acceptance, and test text prompts, multi-subject masks, dimensions, placement,
and provider identity.

The output of `ba-package` is an extensionless Managed Background Assets pack,
not an Android `.aar` file.

### Freeze the PhotoAIKit exporter

RawCull resolves PhotoAIKit `v2.4.1` at
`20e57359603313af7c2d38cae3e8b6e37f8838ef`. The current local PhotoAIKit
development checkout has the same exporter tree through its `3a54e999` parent,
but release evidence must name the tagged merge revision, not a branch name or
an abbreviated commit.

```sh
PHOTOAIKIT_DIR='/Users/thomas/GitHub/RawCull/PhotoAIKit'
PHOTOAIKIT_REVISION='20e57359603313af7c2d38cae3e8b6e37f8838ef'
PHOTOAIKIT_EXPORT_SAM3_SHA256='2b2044d6809619c7e80732e80936b1dd38660a82487d0e032e0f69d3c05afd48'
PHOTOAIKIT_PACKAGE_RESOLVED_SHA256='ba91ddb6c29ade2605e5681c1e57e904bc218498aebdf96310157a5a5cb08aaa'

test "$(git -C "$PHOTOAIKIT_DIR" rev-parse "$PHOTOAIKIT_REVISION^{commit}")" = \
  "$PHOTOAIKIT_REVISION"
test "$(git -C "$PHOTOAIKIT_DIR" show "${PHOTOAIKIT_REVISION}:Tools/export_sam3.py" | shasum -a 256 | cut -d ' ' -f 1)" = \
  "$PHOTOAIKIT_EXPORT_SAM3_SHA256"
test "$(git -C "$PHOTOAIKIT_DIR" show "${PHOTOAIKIT_REVISION}:Package.resolved" | shasum -a 256 | cut -d ' ' -f 1)" = \
  "$PHOTOAIKIT_PACKAGE_RESOLVED_SHA256"
```

Run the exporter from a worktree detached at that revision, or record the exact
different revision and dependency lockfile if PhotoAIKit changes before the
release. The `Package.resolved` file at this revision pins
`apple/coreai-models` to
`cc812078731871574c9b2eb620aa40734c4b89ee`.

### Prepare the DataComp CLIP source

| Field | Required value |
|---|---|
| Checkpoint repository | `laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K` |
| Revision | `4afec35ffe57a943d569ff7ee888061830164da8` |
| Weight file | `open_clip_model.safetensors` |
| Weight bytes | `605189364` |
| Weight SHA-256 | `92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27` |
| Architecture | `ViT-B-32-256` |
| Pretrained tag | `datacomp_s34b_b86k` |

Download and verify the complete pinned source snapshot before conversion:

```sh
DATACOMP_REVISION='4afec35ffe57a943d569ff7ee888061830164da8'
DATACOMP_SHA256='92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27'
DATACOMP_BYTES='605189364'
DATACOMP_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/CLIP-DataComp/$DATACOMP_REVISION"
DATACOMP_SOURCE_DIR="$DATACOMP_ROOT/source"
DATACOMP_EXPORT_DIR="$DATACOMP_ROOT/export"

mkdir -p "$DATACOMP_SOURCE_DIR" "$DATACOMP_EXPORT_DIR"
hf download laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K \
  open_clip_model.safetensors open_clip_config.json README.md \
  merges.txt vocab.json tokenizer.json tokenizer_config.json \
  special_tokens_map.json \
  --revision "$DATACOMP_REVISION" --local-dir "$DATACOMP_SOURCE_DIR"

test "$(shasum -a 256 "$DATACOMP_SOURCE_DIR/open_clip_model.safetensors" | cut -d ' ' -f 1)" = \
  "$DATACOMP_SHA256"
test "$(stat -f '%z' "$DATACOMP_SOURCE_DIR/open_clip_model.safetensors")" = \
  "$DATACOMP_BYTES"
```

Do not use the following ordinary exporter invocation for a `v4` release until
PhotoAIKit accepts the verified local checkpoint or an immutable revision:

```sh
uv run --script "$PHOTOAIKIT_DIR/Tools/export_clip.py" \
  --model openclip-datacomp \
  --architecture ViT-B-32-256 \
  --pretrained datacomp_s34b_b86k \
  --output-dir "$DATACOMP_EXPORT_DIR" \
  --bundle-name CLIP-DataComp \
  --dtype float16
```

At PhotoAIKit `v2.4.1`, `export_clip.py` passes only the architecture and
pretrained tag to OpenCLIP. OpenCLIP then resolves the checkpoint from the Hub
without passing the pinned revision, and the exporter writes
`source_revision: null`. Merely downloading and hashing the pinned file beside
the export does not prove that the conversion consumed it. Add a local
checkpoint/revision option to the exporter, re-export from that verified file,
and record the binding in `PROVENANCE.json` before publishing DataComp `v4`.
The expected output bundle contains `metadata.json`, `tokenizer/`, the runtime
`.aimodel`, and a `_source.aimodel`; exclude the `_source.aimodel` from the
downloadable pack.

### Create the Meta SAM 3 bundle

| Field | Required value |
|---|---|
| Checkpoint repository | `facebook/sam3` |
| Revision | `3c879f39826c281e95690f02c7821c4de09afae7` |
| Weight file | `model.safetensors` |
| Weight bytes | `3439938512` |
| Weight SHA-256 | `6d06f0a5f84e435071fe6603e61d0b4cc7b40e0d39d487cfd4d67d8cc11cc14a` |
| SAM License SHA-256 | `b08db9d32c687054e99cbd41eb1dad19c76936dfb9e2b58e186a01204d8be9ab` |

SAM 3 is gated. Complete Meta's Hugging Face access flow and authenticate with
`hf auth login`. Never put the token in a command transcript, provenance file,
or archive.

The exporter loads the literal path `facebook/sam3` three times. Stage that
relative local path and force offline conversion:

```sh
SAM3_REVISION='3c879f39826c281e95690f02c7821c4de09afae7'
SAM3_SHA256='6d06f0a5f84e435071fe6603e61d0b4cc7b40e0d39d487cfd4d67d8cc11cc14a'
SAM3_BYTES='3439938512'
SAM3_LICENSE_SHA256='b08db9d32c687054e99cbd41eb1dad19c76936dfb9e2b58e186a01204d8be9ab'
SAM3_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/SAM3/$SAM3_REVISION"
SAM3_SOURCE_ROOT="$SAM3_ROOT/source"
SAM3_SOURCE_DIR="$SAM3_SOURCE_ROOT/facebook/sam3"
SAM3_EXPORT_DIR="$SAM3_ROOT/export"

mkdir -p "$SAM3_SOURCE_DIR" "$SAM3_EXPORT_DIR"
hf download facebook/sam3 \
  model.safetensors config.json processor_config.json tokenizer.json \
  tokenizer_config.json special_tokens_map.json merges.txt vocab.json LICENSE README.md \
  --revision "$SAM3_REVISION" --local-dir "$SAM3_SOURCE_DIR"

test "$(shasum -a 256 "$SAM3_SOURCE_DIR/model.safetensors" | cut -d ' ' -f 1)" = "$SAM3_SHA256"
test "$(stat -f '%z' "$SAM3_SOURCE_DIR/model.safetensors")" = "$SAM3_BYTES"
test "$(shasum -a 256 "$SAM3_SOURCE_DIR/LICENSE" | cut -d ' ' -f 1)" = "$SAM3_LICENSE_SHA256"

cd "$SAM3_SOURCE_ROOT"
HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
uv run --script "$PHOTOAIKIT_DIR/Tools/export_sam3.py" \
  --model facebook/sam3 \
  --output-dir "$SAM3_EXPORT_DIR" \
  --bundle-name SAM3 \
  --dtype float16
```

The result must contain:

```text
SAM3/
├── metadata.json
├── tokenizer/
├── sam3_float16.aimodel/
└── sam3_float16_source.aimodel/
```

The current SAM 3 exporter records the model ID but not the upstream commit.
Keep the verified source manifest and PhotoAIKit revision in `PROVENANCE.json`;
do not claim that `metadata.json` alone binds the revision. Exclude
`sam3_float16_source.aimodel` from the downloadable pack.

## Create A Compiled Qwen3-4B Bundle

This optional procedure produces a macOS Core AI language-model bundle with an
ahead-of-time compiled `.aimodelc`. It does not by itself add Qwen to
PhotoAIKit, RawCull's catalog, or the `v4` manifest.

Use the same Core AI exporter revision resolved through PhotoAIKit:

```sh
QWEN_REVISION='1cfa9a7208912126459214e8b04321603b3df60c'
QWEN_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/Qwen3-4B/$QWEN_REVISION"
QWEN_SOURCE_DIR="$QWEN_ROOT/source"

mkdir -p "$QWEN_SOURCE_DIR"
hf download Qwen/Qwen3-4B \
  config.json generation_config.json model.safetensors.index.json \
  model-00001-of-00003.safetensors model-00002-of-00003.safetensors \
  model-00003-of-00003.safetensors tokenizer.json tokenizer_config.json \
  merges.txt vocab.json LICENSE README.md \
  --revision "$QWEN_REVISION" --local-dir "$QWEN_SOURCE_DIR"

test "$(stat -f '%z' "$QWEN_SOURCE_DIR/model-00001-of-00003.safetensors")" = '3957900840'
test "$(stat -f '%z' "$QWEN_SOURCE_DIR/model-00002-of-00003.safetensors")" = '3987450520'
test "$(stat -f '%z' "$QWEN_SOURCE_DIR/model-00003-of-00003.safetensors")" = '99630640'
test "$(stat -f '%z' "$QWEN_SOURCE_DIR/tokenizer.json")" = '11422654'

test "$(shasum -a 256 "$QWEN_SOURCE_DIR/model-00001-of-00003.safetensors" | cut -d ' ' -f 1)" = \
  '328a91d3122359d5547f9d79521205bc0a46e1f79a792dfe650e99fc2d651223'
test "$(shasum -a 256 "$QWEN_SOURCE_DIR/model-00002-of-00003.safetensors" | cut -d ' ' -f 1)" = \
  '6cd087b316306a68c562436b5492edbcf6e16c6dba3a1308279caa5a58e21ca5'
test "$(shasum -a 256 "$QWEN_SOURCE_DIR/model-00003-of-00003.safetensors" | cut -d ' ' -f 1)" = \
  'e4bf436957184f4eeb86a80e9db394503f1f56446b2e6b7edeac5b81470f4ca1'
test "$(shasum -a 256 "$QWEN_SOURCE_DIR/tokenizer.json" | cut -d ' ' -f 1)" = \
  'aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4'

git clone https://github.com/apple/coreai-models.git
cd coreai-models
git checkout --detach cc812078731871574c9b2eb620aa40734c4b89ee

uv run coreai.model.registry \
  --model-info qwen3-4b-8bit-kv \
  --type llm \
  --platform macOS

uv run coreai.llm.export qwen3-4b-8bit-kv \
  --platform macOS \
  --output-dir "$PWD/exports" \
  --output-name qwen3_4b_4bit_weights_8bit_kv_cache_dynamic
```

This preset exports Qwen3-4B with INT4 per-block weights, an INT8 per-tensor KV
cache, float16 compute, and the 40,960-token registry context limit. At the
verification point, `Qwen/Qwen3-4B` resolved to immutable Hugging Face revision
`1cfa9a7208912126459214e8b04321603b3df60c` under Apache-2.0. Record that
revision and verify the downloaded source blobs before conversion:

| Source blob | Bytes | SHA-256 |
|---|---:|---|
| `model-00001-of-00003.safetensors` | 3,957,900,840 | `328a91d3122359d5547f9d79521205bc0a46e1f79a792dfe650e99fc2d651223` |
| `model-00002-of-00003.safetensors` | 3,987,450,520 | `6cd087b316306a68c562436b5492edbcf6e16c6dba3a1308279caa5a58e21ca5` |
| `model-00003-of-00003.safetensors` | 99,630,640 | `e4bf436957184f4eeb86a80e9db394503f1f56446b2e6b7edeac5b81470f4ca1` |
| `tokenizer.json` | 11,422,654 | `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` |

The exporter at this revision does not expose a Hugging Face `--revision`
option. Preserve the resolved snapshot revision from the export environment and
fail the release if it is not the recorded revision above; do not assume that a
future `main` snapshot has the same bytes.

Compile for the current Mac's Core AI architecture with Xcode 27 or newer:

```sh
MODEL_DIR="$PWD/exports/qwen3_4b_4bit_weights_8bit_kv_cache_dynamic"
MODEL_NAME="qwen3_4b_4bit_weights_8bit_kv_cache_dynamic"
ARCHITECTURE=$(xcrun swift -e \
  'import CoreAI; print(AIModel.deviceArchitectureName)')

xcrun coreai-build compile \
  "$MODEL_DIR/$MODEL_NAME.aimodel" \
  --output "$MODEL_DIR/$MODEL_NAME-$ARCHITECTURE.aimodelc" \
  --platform macOS \
  --min-deployment-version 27.0 \
  --architecture "$ARCHITECTURE" \
  --preferred-compute gpu
```

Then change `metadata.json` so `assets.main` names the compiled directory, for
example `qwen3_4b_4bit_weights_8bit_kv_cache_dynamic-h16s.aimodelc`. Do not guess
the architecture suffix; use the value printed by Core AI. Keep the tokenizer
directory and all other bundle metadata beside the compiled asset.

An `.aimodelc` is architecture-specific. A downloadable pack containing it
must target only compatible Macs, or the release must provide separate packs
and manifest entries per architecture. If portability is required, distribute
the uncompiled `.aimodel` and accept runtime compilation instead. Before
packaging, run `llm-runner` against the final bundle, hash the complete compiled
directory with the repository's deterministic tree-fingerprint method, and
record the Xcode/Core AI build versions, architecture, source revision, source
blob hashes, metadata, licence, and final asset-pack hash and size.

## 2. Generate The Manifest

Use `ModelAssets/manifest.template.json` only as developer-side selector input.
Change it when adding/removing a model or changing an ID, source, destination,
platform, or download policy. Let Apple's tooling generate the supported
download-manifest fields.

For the planned `v4` release, the final manifest should point to files such as:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v4/no.blogspot.RawCull.models.clip-datacomp
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v4/no.blogspot.RawCull.models.sam3
```

Each entry needs the stable ID, intended pack version, final archive byte size,
on-demand policy, platform, and third-party hosted URL. Do not invent repository
provenance fields such as `archive_sha256` inside Apple's manifest schema.
For this release, each generated pack entry must use manifest `"version": 4`;
`v4` in the URL alone does not set or prove the per-pack version.

## 3. Update RawCull

Update both production manifest URLs to the same release:

- `RawCull-Info.plist` — `BAManifestURL`;
- `RawCullAIModelDownloadService.swift` —
  `RawCullAIModelDownloadSource.productionManifestURL`.

For each descriptor in `RawCullAIModelDownloadCatalog.swift`, update only the
fields that changed: model version, upstream revision, archive SHA-256, download
and installed sizes, source/model-card/conversion URLs, licence identity/hash,
and readiness. Set `.ready` only when archive, licence, provenance, release
decision, and validation evidence are complete.

Update `RawCullAIModelInclusion` when changing visibility. SAM 3 currently needs
both `includeSAM3` for selection/loading and `includeSAM3Download` for the
download sheet.

## 4. Update Provenance And Notices

Update the production directories:

```text
ModelAssets/Notices/CLIP-DataComp/
ModelAssets/Notices/SAM3/
```

Each repository `PROVENANCE.json` must record release status, tag, immutable
asset URL, final archive SHA-256 and byte count, upstream/source evidence,
tokenizer evidence where applicable, converted runtime fingerprint, and
conversion revisions. These values must agree with the application catalog.

If provenance is embedded in the pack, freeze a staging copy before packaging.
Write final archive evidence to the repository/external release record after
packaging; copying that digest back into the pack and rebuilding changes the
archive and invalidates the digest.

Update `NOTICE.md` when release status, evidence, or attribution changes. Replace
a licence text only when the applicable complete text changes, then update every
checksum referring to it, including bundled app resources.

## 5. Update Tests And Documentation

Update `RawCullAIModelDownloadsTests.swift` for production IDs, readiness,
revisions, hashes, sizes, licence behavior, and runtime states. Update
`ReleaseMetadataTests.swift` for both manifest URLs, descriptor readiness,
template IDs/destinations, and notice/provenance status.

Update `ModelAssets/README.md`, this documentation, and any recorded model
validation decision with the actual new tag and evidence. Do not copy the
known-v3 values into a future release:

| Pack | v3 archive bytes | v3 archive SHA-256 |
|---|---:|---|
| DataComp CLIP | 282,966,632 | `cf433dcd199b44635a4ff0260bd8e79177e4907a4cfcb2f72043066b8cbe4ef7` |
| Meta SAM 3 | 1,542,689,157 | `dd0adc697060129435d4a70515011a37f547e1ad7cd530d943341bf3ca9184a9` |

## 6. Verify Before Publication

```sh
python3 Scripts/VerifyModelProvenance.py
python3 Scripts/TestModelProvenance.py

xcodebuild test \
  -project RawCull.xcodeproj \
  -scheme RawCull \
  -destination 'platform=macOS' \
  -only-testing:RawCullTests/RawCullAIModelDownloadsTests \
  -only-testing:RawCullTests/ReleaseMetadataTests
```

Also test download, provider validation, inference, removal/redownload, and an
upgrade from an installed previous version. `state(for:)` reports an already
local pack as installed before consulting the manifest, so an installed label
alone does not prove that an old pack upgraded.

## 7. Publish In Dependency Order

1. Create the new GitHub release or prerelease.
2. Upload every final extensionless asset pack.
3. Download each hosted pack and verify its size and SHA-256.
4. Upload the generated `manifest.json` last.
5. Verify every production ID, version, size, and immutable URL.
6. Ship a RawCull build pointing to the new manifest only after the hosted set passes.

If any archive changes after publication, generate a new version and evidence;
do not replace a file behind a published immutable manifest.

## Release Checklist

- [ ] Production pack IDs and destinations are unchanged or deliberately migrated.
- [ ] Source, conversion, licence, notice, fingerprint, archive hash, and size evidence is complete.
- [ ] SAM 3's release decision and explicit acceptance behavior are preserved.
- [ ] Template, generated manifest, application catalog, and production URLs agree.
- [ ] Packs are uploaded and verified before `manifest.json`.
- [ ] Provenance and mutation validation pass.
- [ ] Focused release metadata and download tests pass.
- [ ] Clean install, upgrade, inference, removal, and redownload are verified.

Rollback by restoring both manifest URL declarations and catalog evidence to a
known-good immutable release. Do not leave the plist and Swift URL on different
tags.
