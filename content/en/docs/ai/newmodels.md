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

Qwen is not in this table because RawCull does not currently declare a managed
Qwen download descriptor. RawCull does import PhotoAIKit's Qwen provider, but
the person using the app selects a local vision-language bundle. The build
recipe later on this page creates that developer bundle; adding it to `v4` is a
separate product and integration decision.

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

## Create A Qwen3-VL Bundle For Image Prompts

Yes, image prompts require a new model export. The earlier `Qwen3-4B` recipe
creates a text-only bundle whose `metadata.json` has `kind: llm` and only a main
decoder asset. RawCull deliberately rejects that bundle before inference.
Changing the metadata string cannot add vision support: a usable bundle needs
the Qwen3-VL checkpoint, `kind: vlm`, and separate `main`, `embedding`, and
`vision` Core AI assets.

RawCull currently resolves PhotoAIKit at
`c5c76590c3d79ad508d24d893cd7d8d6aa873355`, which resolves Apple's
`coreai-models` at `7359dbcf6c3babb4fbfadfd015ffcc1cb6d87420`.
That Core AI revision provides the `qwen3-vl` recipe for
`Qwen/Qwen3-VL-2B-Instruct`. Use that exact exporter revision:

```sh
COREAI_MODELS_REVISION='7359dbcf6c3babb4fbfadfd015ffcc1cb6d87420'
COREAI_MODELS_DIR='/Users/thomas/ModelAssets/coreai-models'

git clone https://github.com/apple/coreai-models.git "$COREAI_MODELS_DIR"
git -C "$COREAI_MODELS_DIR" checkout --detach "$COREAI_MODELS_REVISION"
cd "$COREAI_MODELS_DIR"

uv run coreai.vlm.export --list-models
uv run coreai.vlm.export qwen3-vl \
  --max-context-length 4096 \
  --output-dir "$PWD/exports"
```

Do not pass `--skip-vision`; it intentionally omits the vision encoder and does
not produce a bundle RawCull can use for photos. The exporter downloads the
Qwen3-VL checkpoint and creates:

```text
exports/qwen3_vl_2b/
├── metadata.json
├── tokenizer/
├── qwen3_vl_2b.aimodel
├── embed.aimodel
└── vision.aimodel
```

Before selecting the directory in RawCull, verify that `metadata.json` contains
`"kind": "vlm"`, that `assets.main`, `assets.embedding`, and `assets.vision`
name those three existing assets, and that `source.hf_model_id` is
`Qwen/Qwen3-VL-2B-Instruct`. Select the `qwen3_vl_2b` directory, not one of the
individual `.aimodel` directories.

The VLM exporter uses Hugging Face `snapshot_download` but does not expose a
`--revision` option. For a release-quality or reproducible artifact, first pin
and record the resolved Qwen3-VL snapshot revision and source-file hashes, then
ensure the exporter consumed that cached snapshot. Do not reuse the Qwen3-4B
revision or hashes: Qwen3-4B and Qwen3-VL-2B-Instruct are different checkpoints.

Ahead-of-time compilation is optional because RawCull and PhotoAIKit accept
both `.aimodel` and `.aimodelc`. If compiling, compile all three assets for the
current Mac architecture, not only the main decoder:

```sh
MODEL_DIR="$PWD/exports/qwen3_vl_2b"
ARCHITECTURE=$(xcrun swift -e \
  'import CoreAI; print(AIModel.deviceArchitectureName)')

xcrun coreai-build compile "$MODEL_DIR/qwen3_vl_2b.aimodel" \
  --output "$MODEL_DIR/qwen3_vl_2b.aimodelc" \
  --platform macOS --min-deployment-version 27.0 \
  --architecture "$ARCHITECTURE" --preferred-compute gpu
xcrun coreai-build compile "$MODEL_DIR/embed.aimodel" \
  --output "$MODEL_DIR/embed.aimodelc" \
  --platform macOS --min-deployment-version 27.0 \
  --architecture "$ARCHITECTURE" --preferred-compute gpu
xcrun coreai-build compile "$MODEL_DIR/vision.aimodel" \
  --output "$MODEL_DIR/vision.aimodelc" \
  --platform macOS --min-deployment-version 27.0 \
  --architecture "$ARCHITECTURE" --preferred-compute gpu
```

With those exact basename-plus-`c` output names, the Core AI bundle resolver
can fall back from each `.aimodel` metadata entry to its `.aimodelc` counterpart
when the source asset is absent. If different compiled names are used, update
all three entries in `metadata.json`. Compiled assets are
architecture-specific; keep the uncompiled bundle for portability or build and
label separate bundles for each supported architecture.

Validate the completed bundle with an actual image before relying on RawCull:

```sh
swift run -c release llm-runner \
  --model "$MODEL_DIR" \
  --image /absolute/path/to/test-photo.jpg \
  --prompt "Describe this image."
```

This creates a developer-selected local bundle only. It does not add Qwen to
RawCull's Managed Background Assets catalog or the `v4` manifest.

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
