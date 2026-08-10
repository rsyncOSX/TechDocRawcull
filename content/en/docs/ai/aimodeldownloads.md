+++
author = "Thomas Evensen"
title = "AI Model Download Service"
linkTitle = "AI Model Downloads"
date = "2026-08-10"
description = "Build, validate, package, and download the three optional RawCull AI models."
tags = ["ai", "models", "downloads", "clip", "sam3", "background-assets", "self-hosting", "apple-hosting"]
categories = ["technical details"]
weight = 30
+++

# AI model download service

RawCull supports exactly three optional model bundles:

| Model | PhotoAIKit bundle | Runtime asset | Use |
|---|---|---|---|
| DataComp CLIP | `CLIP-DataComp` | `ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel` | Similarity and semantic search |
| OpenAI CLIP | `CLIP-OpenAI` | `clip-vit-base-patch32_float16_static.aimodel` | Similarity and semantic search |
| Meta SAM 3 | `SAM3` | `sam3_float16.aimodel` | Promptable segmentation |

SigLIP2 and EfficientSAM are not part of the RawCull download catalogue or
release manifest. Do not include their bundles, notices, archives, or asset-pack
IDs in a RawCull model release.

RawCull uses Managed Background Assets. The app asks `AssetPackManager` for a
known asset-pack ID, resolves the catalogue-owned model path, and gives that
directory to PhotoAIKit for validation. RawCull does not unpack an AAR itself.

The current production manifest is pinned to:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/manifest.json
```

The current RawCull source enables DataComp only. OpenAI CLIP and SAM 3 remain
hidden and release-blocked until their redistribution reviews and new archives
are complete. The three-model release procedure is documented in
[Publishing new RawCull AI models](../newmodels/).

## Release gates

A working local conversion is not automatically publishable. Every downloadable
model must pass all of these gates:

1. Pin and verify the exact upstream checkpoint.
2. Record source file checksums, PhotoAIKit revision, conversion command, runtime
   fingerprint, and archive checksum.
3. Confirm that the exact trained weights may be converted, used, and
   redistributed through the chosen hosting channel.
4. Include the applicable complete licence and notice files in the pack.
5. Validate the generated bundle with PhotoAIKit and RawCull.
6. Package only runtime files; never publish conversion intermediates.

DataComp is currently the only `.ready` production descriptor. OpenAI CLIP is
blocked pending weight-level redistribution clearance. SAM 3 is gated upstream
and remains blocked until ungated redistribution of the converted derivative is
confirmed. SAM 3 also requires explicit in-app licence acceptance.

## Use the reviewed PhotoAIKit revision

The procedures below are verified against PhotoAIKit commit:

```text
6e3216027b267c27ccaf99d334807b18ea1aaec9
```

That revision exports CLIP metadata version `0.4`, SAM 3 metadata version `0.3`,
separate CLIP `image_encoder` and `text_encoder` functions, normalized
embeddings, and the corrected Pillow-compatible bicubic CLIP preprocessing.

Use a clean detached checkout for release evidence:

```sh
PHOTOAIKIT_REVISION='6e3216027b267c27ccaf99d334807b18ea1aaec9'
PHOTOAIKIT_DIR='/Users/thomas/ModelAssets/ReleaseEvidence/PhotoAIKit'

git clone https://github.com/rsyncOSX/PhotoAIKit.git "$PHOTOAIKIT_DIR"
git -C "$PHOTOAIKIT_DIR" switch --detach "$PHOTOAIKIT_REVISION"
test "$(git -C "$PHOTOAIKIT_DIR" rev-parse HEAD)" = "$PHOTOAIKIT_REVISION"
test -z "$(git -C "$PHOTOAIKIT_DIR" status --porcelain)"
```

If a later PhotoAIKit revision is used, review changes to `Tools/export_clip.py`,
`Tools/export_sam3.py`, preprocessing, metadata, and runtime validation. Record
the exact revision actually executed; do not silently reuse the value above.

## Create the DataComp CLIP bundle

The release model is OpenCLIP `ViT-B-32-256` with the registered
`datacomp_s34b_b86k` pretrained tag.

| Field | Required value |
|---|---|
| Checkpoint repository | `laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K` |
| Revision | `4afec35ffe57a943d569ff7ee888061830164da8` |
| Weight file | `open_clip_model.safetensors` |
| Weight bytes | `605189364` |
| Weight SHA-256 | `92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27` |

Create an evidence-specific Hugging Face cache and verify that its `main`
resolution is the pinned revision required by OpenCLIP:

```sh
DATACOMP_REPOSITORY='laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K'
DATACOMP_REVISION='4afec35ffe57a943d569ff7ee888061830164da8'
DATACOMP_SHA256='92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27'
DATACOMP_BYTES='605189364'
DATACOMP_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/CLIP-DataComp/$DATACOMP_REVISION"
DATACOMP_HF_HOME="$DATACOMP_ROOT/huggingface"
DATACOMP_EXPORT_DIR="$DATACOMP_ROOT/export"

mkdir -p "$DATACOMP_HF_HOME" "$DATACOMP_EXPORT_DIR"
export HF_HOME="$DATACOMP_HF_HOME"

DATACOMP_SNAPSHOT="$(hf download "$DATACOMP_REPOSITORY" \
  open_clip_model.safetensors open_clip_config.json README.md \
  --revision "$DATACOMP_REVISION" --quiet)"
DATACOMP_MAIN_SNAPSHOT="$(hf download "$DATACOMP_REPOSITORY" \
  open_clip_model.safetensors open_clip_config.json README.md \
  --revision main --quiet)"

test "$(basename "$DATACOMP_SNAPSHOT")" = "$DATACOMP_REVISION"
test "$DATACOMP_MAIN_SNAPSHOT" = "$DATACOMP_SNAPSHOT"
test "$(shasum -a 256 "$DATACOMP_SNAPSHOT/open_clip_model.safetensors" | cut -d ' ' -f 1)" = "$DATACOMP_SHA256"
test "$(stat -f '%z' "$DATACOMP_SNAPSHOT/open_clip_model.safetensors")" = "$DATACOMP_BYTES"
```

Export with PhotoAIKit's registered preset:

```sh
HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
uv run --script "$PHOTOAIKIT_DIR/Tools/export_clip.py" \
  --model openclip-datacomp \
  --architecture ViT-B-32-256 \
  --pretrained datacomp_s34b_b86k \
  --output-dir "$DATACOMP_EXPORT_DIR" \
  --bundle-name CLIP-DataComp \
  --dtype float16
```

Do not pass `open_clip_model.safetensors` as `--pretrained`. That creates the
historical custom-named bundle and bypasses the registered preset identity. The
tested, non-collapsing bundle uses `datacomp_s34b_b86k` and must contain:

```text
CLIP-DataComp/
├── metadata.json
├── tokenizer/
├── ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel/
└── ViT-B-32-256-datacomp_s34b_b86k_float16_static_source.aimodel/
```

The `_source.aimodel` directory is private conversion evidence. Exclude it from
the downloadable pack. `metadata.json` must select the optimized directory in
`assets.main` and contain its `asset_fingerprints.main` value.

## Create the OpenAI CLIP bundle

| Field | Required value |
|---|---|
| Checkpoint repository | `openai/clip-vit-base-patch32` |
| Revision | `3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268` |
| Weight file | `pytorch_model.bin` |
| Weight bytes | `605247071` |
| Weight SHA-256 | `a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f` |

The exporter loads the repository ID for both the model and tokenizer. Use an
evidence-specific Hugging Face cache, require its `main` reference to resolve to
the pinned revision, and then run offline. Loading through that verified cache
also lets Transformers record the immutable source revision in the generated
metadata:

```sh
OPENAI_REVISION='3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268'
OPENAI_SHA256='a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f'
OPENAI_BYTES='605247071'
OPENAI_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/CLIP-OpenAI/$OPENAI_REVISION"
OPENAI_HF_HOME="$OPENAI_ROOT/huggingface"
OPENAI_EXPORT_DIR="$OPENAI_ROOT/export"

mkdir -p "$OPENAI_HF_HOME" "$OPENAI_EXPORT_DIR"
export HF_HOME="$OPENAI_HF_HOME"

OPENAI_SNAPSHOT="$(hf download openai/clip-vit-base-patch32 \
  config.json pytorch_model.bin merges.txt preprocessor_config.json \
  special_tokens_map.json tokenizer.json tokenizer_config.json vocab.json README.md \
  --revision "$OPENAI_REVISION" --quiet)"
OPENAI_MAIN_SNAPSHOT="$(hf download openai/clip-vit-base-patch32 \
  config.json pytorch_model.bin merges.txt preprocessor_config.json \
  special_tokens_map.json tokenizer.json tokenizer_config.json vocab.json README.md \
  --revision main --quiet)"

test "$(basename "$OPENAI_SNAPSHOT")" = "$OPENAI_REVISION"
test "$OPENAI_MAIN_SNAPSHOT" = "$OPENAI_SNAPSHOT"
test "$(shasum -a 256 "$OPENAI_SNAPSHOT/pytorch_model.bin" | cut -d ' ' -f 1)" = "$OPENAI_SHA256"
test "$(stat -f '%z' "$OPENAI_SNAPSHOT/pytorch_model.bin")" = "$OPENAI_BYTES"

HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
uv run --script "$PHOTOAIKIT_DIR/Tools/export_clip.py" \
  --model openai \
  --output-dir "$OPENAI_EXPORT_DIR" \
  --bundle-name CLIP-OpenAI \
  --dtype float16
```

The result must contain:

```text
CLIP-OpenAI/
├── metadata.json
├── tokenizer/
├── clip-vit-base-patch32_float16_static.aimodel/
└── clip-vit-base-patch32_float16_static_source.aimodel/
```

`metadata.json` must report source revision
`3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268`. Exclude the `_source.aimodel`
directory from the downloadable pack.

## Create the Meta SAM 3 bundle

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

The exporter loads the literal path `facebook/sam3` three times. As with OpenAI
CLIP, stage that relative local path and force offline conversion:

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

## Validate every generated bundle

Do not use `--dynamic` or `--overwrite` for a release conversion. Preserve the
terminal log and record `uv --version`, `sw_vers`, `xcodebuild -version`, the
PhotoAIKit commit, source checksums, generated metadata, and runtime fingerprint.

For each runtime asset, compare the generated fingerprint with
`asset_fingerprints.main`:

```sh
python3 "$PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  /path/to/bundle/runtime.aimodel
```

Run PhotoAIKit's package tests:

```sh
swift test --package-path "$PHOTOAIKIT_DIR"
```

For each CLIP bundle, generate PyTorch reference embeddings from the same model
identity and compare them with the Core AI bundle using `clipbench`. The fixture
set must contain representative portraits, animals, vehicles, landscapes,
interiors, night scenes, macro images, motion blur, readable signs, and flowers.

```sh
cd "$PHOTOAIKIT_DIR"
swift build -c release --product clipbench

uv run --script Tools/generate_clip_reference.py \
  --model openclip-datacomp \
  --architecture ViT-B-32-256 \
  --pretrained datacomp_s34b_b86k \
  --image /path/to/01-dog-outdoors.jpg \
  --text 'a woman with a dog outdoors' \
  --output /private/tmp/datacomp-clip-reference.json

.build/release/clipbench parity \
  --reference /private/tmp/datacomp-clip-reference.json \
  --model /path/to/CLIP-DataComp \
  --minimum-cosine 0.998
```

Repeat with `--model openai` and the OpenAI bundle. Add every fixture image and
matching prompt with repeated `--image` and `--text` arguments. Investigate any
result below the chosen threshold; do not lower the threshold merely to publish
the pack.

Finally, install each complete candidate in RawCullFB, rebuild its model-specific
index, and run the same `semantictest.txt` for both CLIP models. Compare:

- query-by-query top results and scores;
- image-to-image nearest-neighbour results;
- duplicate or near-duplicate retrieval;
- score spread and repeated ranking patterns;
- missing results, errors, and elapsed time.

A new model fingerprint requires a new index. Never compare one model against an
index created by another model or by an older conversion.

For SAM 3, install the candidate in RawCull and verify text-prompt segmentation,
mask dimensions, mask placement, licence acceptance, relaunch, and removal.

## Prepare the release staging tree

Only the optimized runtime assets belong in the pack:

```text
ModelAssets/Release/
├── Models/
│   ├── CLIP-DataComp/
│   │   ├── metadata.json
│   │   ├── tokenizer/
│   │   └── ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel/
│   ├── CLIP-OpenAI/
│   │   ├── metadata.json
│   │   ├── tokenizer/
│   │   └── clip-vit-base-patch32_float16_static.aimodel/
│   └── SAM3/
│       ├── metadata.json
│       ├── tokenizer/
│       └── sam3_float16.aimodel/
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

Each packaging manifest must select exactly `metadata.json`, `tokenizer`, the
optimized runtime directory, and the matching notice directory. Example:

```json
{
  "assetPackID": "no.blogspot.RawCull.models.clip-datacomp",
  "downloadPolicy": { "onDemand": {} },
  "fileSelectors": [
    { "file": "Models/CLIP-DataComp/metadata.json" },
    { "directory": "Models/CLIP-DataComp/tokenizer" },
    { "directory": "Models/CLIP-DataComp/ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel" },
    { "directory": "Notices/CLIP-DataComp" }
  ],
  "platforms": ["macOS"]
}
```

The three stable asset-pack IDs and installed paths are:

| Model | Asset-pack ID | Installed model path |
|---|---|---|
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` |
| OpenAI CLIP | `no.blogspot.RawCull.models.clip-openai` | `Models/CLIP-OpenAI` |
| SAM 3 | `no.blogspot.RawCull.models.sam3` | `Models/SAM3` |

Generate one `.aar` per manifest from the release staging root:

```sh
cd /Users/thomas/ModelAssets/Release
xcrun ba-package package Packaging/clip-datacomp.json --output-path Output/clip-datacomp.aar
xcrun ba-package package Packaging/clip-openai.json --output-path Output/clip-openai.aar
xcrun ba-package package Packaging/sam3.json --output-path Output/sam3.aar

shasum -a 256 Output/*.aar
stat -f '%N %z bytes' Output/*.aar
```

Treat published archives as immutable. Record each AAR checksum and byte count
in provenance and the matching RawCull catalogue descriptor. Upload archives
before uploading the generated download `manifest.json`.

## Runtime download and activation

Self-hosting is used for the Developer ID distribution. The app and downloader
extension share `group.no.blogspot.RawCull.model-assets`. For an App Store build,
the downloader can instead use Apple hosting; do not enable both hosting modes
in one product.

When the user selects **Download**, RawCull:

1. checks inclusion and release readiness;
2. verifies any required licence acceptance;
3. asks Managed Background Assets for the exact asset-pack ID;
4. reports download progress and supports cancellation;
5. resolves the catalogue-owned installed model path;
6. validates metadata, tokenizer, runtime asset, fingerprint, and configuration;
7. constructs the matching CLIP or SAM 3 provider only after validation passes.

Removing a model asks Managed Background Assets to remove its pack and then
refreshes RawCull capabilities. Manually installed models and managed packs must
not be merged into the same candidate directory.

## Signing and provisioning

The application, downloader extension, and App Group identifiers are:

| Purpose | Identifier |
|---|---|
| RawCull application | `no.blogspot.RawCull` |
| Model downloader extension | `no.blogspot.RawCull.ModelDownloader` |
| Shared App Group | `group.no.blogspot.RawCull.model-assets` |

Both App IDs must have the App Group capability. The app and extension use the
same development team and provisioning setup. Verify the final archive contains
and signs the nested downloader extension before notarizing the Developer ID
release.
