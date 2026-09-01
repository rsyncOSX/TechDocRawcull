+++
author = "Thomas Evensen"
title = "AI Model Download Service"
linkTitle = "AI Model Downloads"
date = "2026-08-10"
lastmod = "2026-09-01"
description = "Build, validate, package, and download the four optional RawCull AI models."
tags = ["ai", "models", "downloads", "clip", "efficient-sam", "sam3", "background-assets", "self-hosting", "apple-hosting"]
categories = ["technical details"]
weight = 30
+++

# AI model download service

RawCull's managed-download schema recognizes four optional model
bundles:

| Model         | PhotoAIKit bundle | Runtime asset                                            | Use                            |
| ------------- | ----------------- | -------------------------------------------------------- | ------------------------------ |
| DataComp CLIP | `CLIP-DataComp`   | `ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel` | Similarity and semantic search |
| OpenAI CLIP   | `CLIP-OpenAI`     | `clip-vit-base-patch32_float16_static.aimodel`           | Similarity and semantic search |
| EfficientSAM  | `EfficientSAM`     | `efficient_sam_vitt_float16_static_q64.aimodel`          | Point-prompted segmentation    |
| Meta SAM 3    | `SAM3`            | `sam3_float16.aimodel`                                   | Promptable segmentation        |

SigLIP2 is not part of the RawCull download catalogue or release manifest. Do
not include its bundle, notices, archive, or asset-pack ID in a RawCull model
release.

EfficientSAM is the lightweight segmentation model planned for RawCull 3.3.0.
It is not retroactively part of the current `v2` model release. Prepare it under
a new immutable release tag and enable it only after the pinned conversion,
runtime, licence, provenance, packaging, and download checks in this page pass.

RawCull uses Managed Background Assets. The app asks `AssetPackManager` for a
known asset-pack ID, resolves the catalogue-owned model path, and gives that
directory to PhotoAIKit for validation. RawCull does not unpack an AAR itself.

The current production manifest is pinned to:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/manifest.json
```

The current production release enables DataComp CLIP and OpenAI CLIP. Both are
published in `v2`, have `.ready` production descriptors, and appear in Settings.
EfficientSAM is being prepared for RawCull 3.3.0. SAM 3 remains excluded by
`includeSAM3 = false` and release-blocked. The four-model release procedure is
documented in
[Publishing new RawCull AI models](../newmodels/).

## Runtime architecture

`RawCullAIModelDownloadCatalog.production` is the application-owned authority
for model identity, asset-pack ID, expected managed path, archive evidence,
licence metadata, and release readiness. Inclusion switches filter that catalog
before Settings sees it; a blocked or excluded model cannot become downloadable
merely because a host manifest contains an asset with the same ID.

For the self-hosted Developer ID build, `RawCullModelDownloader` is a
`ManagedDownloaderExtension`. The app and extension are configured with the same
`v2` `BAManifestURL` and App Group. The compile-time
`RAWCULL_APPLE_HOSTED_MODEL_ASSETS` variant instead uses
`StoreDownloaderExtension`; one product must not mix the two hosting modes.

The app-facing service always uses `AssetPackManager`:

1. `snapshot()` maps every included descriptor to a user-visible state.
2. `ensureLocalAvailability(requireLatestVersion: true)` downloads or updates
   the exact asset-pack ID and supplies progress events.
3. `AssetPackManager.url(for:)` resolves the descriptor's managed destination.
   The resulting URL is ephemeral and must be resolved again after relaunch;
   RawCull never persists it as a stable filesystem path.
4. `RawCullAISettingsModel` passes the snapshot's managed locations to
   `RawCullAIIntegration.setManagedModelLocations`, refreshes capabilities, and
   reapplies the selected similarity provider.
5. After a download, the settings model enters `validating`, installs the new
   managed location into the integration, and calls `refresh()` before showing
   the final installed/capability state. Removal clears that location and runs
   the same refresh path.

The downloader installs the directory selected by `assetPackModelPath`, not an
archive filename. The current contract is:

| Model         | Asset-pack ID                              | Managed destination    | Published archive evidence                                                                    |
| ------------- | ------------------------------------------ | ---------------------- | --------------------------------------------------------------------------------------------- |
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` | 282,966,632 bytes; SHA-256 `cf433dcd199b44635a4ff0260bd8e79177e4907a4cfcb2f72043066b8cbe4ef7` |
| OpenAI CLIP   | `no.blogspot.RawCull.models.clip-openai`   | `Models/CLIP-OpenAI`   | 282,866,068 bytes; SHA-256 `e9181157c2d4012db2e6478949488f9906696a4ed78ecaa10235d9762621136c` |
| EfficientSAM  | `no.blogspot.RawCull.models.efficient-sam` | `Models/EfficientSAM`  | Planned for RawCull 3.3.0; record the generated archive checksum and sizes   |
| SAM 3         | `no.blogspot.RawCull.models.sam3`          | `Models/SAM3`          | Not published; checksum and sizes remain `nil`                                                |

### macOS 27 development-build guard

Two macOS 27 seed builds were observed to trap inside Background Assets while
validating an Xcode development-signed application. Before obtaining
`AssetPackManager.shared`, `RawCullBackgroundAssetsRuntime` checks both:

- whether `ProcessInfo.operatingSystemVersionString` contains an exact build in
  `affectedMacOS27Builds`; and
- whether the running executable has the `com.apple.security.get-task-allow`
  entitlement.

Only that exact combination disables live downloads. A Developer ID distribution
build on the same operating-system build remains eligible, and a new macOS build
is allowed by default until it is independently confirmed affected. The UI uses
`unavailable(reason:)` with the development-build explanation; it must not
report the model as missing, release-blocked, or improperly licensed.

XCTest is handled separately. Xcode relocates the test host bundle, so
`liveManifestURL` uses the non-routable `example.invalid` manifest under XCTest
and transfer tests inject a deterministic service. Do not add test-host failures
to the operating-system build denylist.

When Apple publishes another beta, RC, or public build, test the live download,
cancellation, removal, and redownload paths before changing the denylist. A
macOS update does not by itself require a RawCull version bump. The app and
downloader extension must nevertheless retain matching RawCull marketing/build
values, signing, App Group, sandbox, manifest, and hosting configuration. The
complete release checklist lives in `Docs/macos-background-assets-release.md` in
the RawCull repository.

### User-visible states, failure, and retry

| State                    | Meaning and available action                                                                             |
| ------------------------ | -------------------------------------------------------------------------------------------------------- |
| `checking`               | Refresh is resolving release, licence, manifest, and local-install state.                                |
| `unavailable(reason:)`   | The descriptor is release-blocked. No download action is offered.                                        |
| `licenceRequired`        | A ready descriptor requires acceptance of the verified bundled licence text before download.             |
| `notConfigured`          | The selected hosting source is not valid; no Background Assets request is made.                          |
| `ready`                  | The manifest contains the pack and Download is enabled.                                                  |
| `downloading(progress:)` | Progress is shown and Cancel is enabled.                                                                 |
| `validating`             | The pack is local; RawCull is refreshing the managed location and model capability.                      |
| `installed(location:)`   | The managed pack resolved and validated sufficiently to expose its current location; Remove is enabled.  |
| `removing`               | Managed removal and capability refresh are in progress.                                                  |
| `failed(message:)`       | The exact manifest, Background Assets, path, licence, or validation error is shown and Retry is enabled. |

Cancellation does not pretend the pack was removed. The task is cancelled, a
fresh coordinator snapshot determines whether the pack is now `ready` or already
`installed`, and the UI returns to that state. Retry starts a new
`ensureLocalAvailability` request. A failed validation retains an explicit
failure/capability reason; RawCull does not activate a provider from an
unverified directory. Vision feature-print similarity remains available when
neither CLIP capability is ready.

## Release-operator procedure

The commands below create and publish model artifacts. They are release-operator
work and are not executed by RawCull at runtime.

### Release gates

A working local conversion is not automatically publishable. Every downloadable
model must pass all of these gates:

1. Pin and verify the exact upstream checkpoint.
2. Record source file checksums, PhotoAIKit revision, conversion command,
   runtime fingerprint, and archive checksum.
3. Confirm that the exact trained weights may be converted, used, and
   redistributed through the chosen hosting channel.
4. Include the applicable complete licence and notice files in the pack.
5. Validate the generated bundle with PhotoAIKit and RawCull.
6. Package only runtime files; never publish conversion intermediates.

DataComp CLIP and OpenAI CLIP are the current `.ready` production descriptors
and their `v2` archives are published. EfficientSAM is the RawCull 3.3.0
candidate; do not mark it `.ready` until its new archive evidence and complete
Apache 2.0 and Apple BSD 3-Clause notices are recorded. SAM 3 is gated upstream
and remains blocked until ungated redistribution of the converted derivative is
confirmed. Its descriptor also requires explicit in-app licence acceptance if
it later becomes ready.

### Use the reviewed PhotoAIKit revision

The CLIP and SAM 3 procedures below are verified against PhotoAIKit commit:

```text
6e3216027b267c27ccaf99d334807b18ea1aaec9
```

That revision exports CLIP metadata version `0.4`, SAM 3 metadata version `0.3`,
separate CLIP `image_encoder` and `text_encoder` functions, normalized
embeddings, and the corrected Pillow-compatible bicubic CLIP preprocessing. The
checked-in blocked SAM 3 candidate still records metadata version `0.2`; it is
evidence of the older conversion, not the output contract for a future rebuild.
Any SAM 3 release candidate must be regenerated and revalidated with the actual
exporter revision recorded for that candidate.

EfficientSAM uses Apple's separate `coreai-models` exporter and the PhotoAIKit
validation revision pinned in its own section. Do not substitute the CLIP/SAM 3
exporter revision for either of those values.

Use a clean detached checkout for release evidence:

```sh
PHOTOAIKIT_REVISION='6e3216027b267c27ccaf99d334807b18ea1aaec9'
PHOTOAIKIT_DIR='/Users/thomas/ModelAssets/ReleaseEvidence/PhotoAIKit'

git clone https://github.com/rsyncOSX/PhotoAIKit.git "$PHOTOAIKIT_DIR"
git -C "$PHOTOAIKIT_DIR" switch --detach "$PHOTOAIKIT_REVISION"
test "$(git -C "$PHOTOAIKIT_DIR" rev-parse HEAD)" = "$PHOTOAIKIT_REVISION"
test -z "$(git -C "$PHOTOAIKIT_DIR" status --porcelain)"
```

If a later PhotoAIKit revision is used, review changes to
`Tools/export_clip.py`, `Tools/export_sam3.py`, preprocessing, metadata, and
runtime validation. Record the exact revision actually executed; do not silently
reuse the value above.

### Create the DataComp CLIP bundle

The release model is OpenCLIP `ViT-B-32-256` with the registered
`datacomp_s34b_b86k` pretrained tag.

| Field                 | Required value                                                     |
| --------------------- | ------------------------------------------------------------------ |
| Checkpoint repository | `laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K`                   |
| Revision              | `4afec35ffe57a943d569ff7ee888061830164da8`                         |
| Weight file           | `open_clip_model.safetensors`                                      |
| Weight bytes          | `605189364`                                                        |
| Weight SHA-256        | `92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27` |

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

### Create the OpenAI CLIP bundle

| Field                 | Required value                                                     |
| --------------------- | ------------------------------------------------------------------ |
| Checkpoint repository | `openai/clip-vit-base-patch32`                                     |
| Revision              | `3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268`                         |
| Weight file           | `pytorch_model.bin`                                                |
| Weight bytes          | `605247071`                                                        |
| Weight SHA-256        | `a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f` |

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

### Create the EfficientSAM bundle for RawCull 3.3.0

RawCull uses EfficientSAM ViT-Tiny through PhotoAIKit's
`CoreAIEfficientSAMBackend`. It is point-prompted rather than text-prompted. The
release configuration uses 64 one-point queries; the runtime places them on an
8 × 8 grid and returns the highest-confidence mask. EfficientSAM does not need
a tokenizer.

| Field                      | Required value                                                     |
| -------------------------- | ------------------------------------------------------------------ |
| Implementation repository  | `yformer/EfficientSAM`                                             |
| Implementation revision    | `d525f622e6f640acf5a0fc37c7ca1f243da5bde0`                         |
| Checkpoint repository      | `merve/EfficientSAM`                                               |
| Checkpoint revision        | `517e547d40d8d5b5fc9bc8c8334414ce9a0927e6`                         |
| Source file                | `efficient_sam_vitt.pt`                                            |
| Source bytes               | `40982470`                                                         |
| Source SHA-256             | `dff858b19600a46461cbb7de98f796b23a7a888d9f5e34c0b033f7d6eb9e4e6a` |
| Apple converter revision   | `c2a0274af289bf481e2d6fd292a86a5bff038f12`                         |
| Python conversion packages | `coreai-core 1.0.0b2`, `coreai-torch 0.4.1`                        |
| Export configuration       | Float16, static batch, 64 queries, one point per query             |

Do not reuse the earlier output produced with `coreai-core 1.0.0b1` and
`coreai-torch 0.4.0`; that output can fail portable Core AI compilation. Create
an evidence workspace and verify the source checkpoint before conversion:

```sh
EFFICIENTSAM_IMPLEMENTATION_REVISION='d525f622e6f640acf5a0fc37c7ca1f243da5bde0'
EFFICIENTSAM_CHECKPOINT_REPOSITORY='merve/EfficientSAM'
EFFICIENTSAM_CHECKPOINT_REVISION='517e547d40d8d5b5fc9bc8c8334414ce9a0927e6'
EFFICIENTSAM_SOURCE_FILENAME='efficient_sam_vitt.pt'
EFFICIENTSAM_EXPECTED_BYTES='40982470'
EFFICIENTSAM_EXPECTED_SHA256='dff858b19600a46461cbb7de98f796b23a7a888d9f5e34c0b033f7d6eb9e4e6a'
EFFICIENTSAM_COREAI_REVISION='c2a0274af289bf481e2d6fd292a86a5bff038f12'
EFFICIENTSAM_PHOTOAIKIT_REVISION='1e2eaccd00947fbadda300e4a617842479cae7b9'

EFFICIENTSAM_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/EfficientSAM/$EFFICIENTSAM_CHECKPOINT_REVISION"
EFFICIENTSAM_SOURCE_DIR="$EFFICIENTSAM_ROOT/source"
EFFICIENTSAM_COREAI_DIR="$EFFICIENTSAM_ROOT/coreai-models"
EFFICIENTSAM_PHOTOAIKIT_DIR="$EFFICIENTSAM_ROOT/PhotoAIKit"
EFFICIENTSAM_EXPORT_DIR="$EFFICIENTSAM_ROOT/export"
EFFICIENTSAM_TORCH_HOME="$EFFICIENTSAM_ROOT/torch"

mkdir -p "$EFFICIENTSAM_SOURCE_DIR" "$EFFICIENTSAM_EXPORT_DIR" \
  "$EFFICIENTSAM_TORCH_HOME/hub/checkpoints"

git clone https://github.com/apple/coreai-models.git "$EFFICIENTSAM_COREAI_DIR"
git -C "$EFFICIENTSAM_COREAI_DIR" switch --detach "$EFFICIENTSAM_COREAI_REVISION"
git clone https://github.com/rsyncOSX/PhotoAIKit.git "$EFFICIENTSAM_PHOTOAIKIT_DIR"
git -C "$EFFICIENTSAM_PHOTOAIKIT_DIR" switch --detach "$EFFICIENTSAM_PHOTOAIKIT_REVISION"

hf download "$EFFICIENTSAM_CHECKPOINT_REPOSITORY" \
  "$EFFICIENTSAM_SOURCE_FILENAME" \
  --revision "$EFFICIENTSAM_CHECKPOINT_REVISION" \
  --local-dir "$EFFICIENTSAM_SOURCE_DIR"

test "$(shasum -a 256 "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME" | cut -d ' ' -f 1)" = \
  "$EFFICIENTSAM_EXPECTED_SHA256"
test "$(stat -f '%z' "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME")" = \
  "$EFFICIENTSAM_EXPECTED_BYTES"
ditto "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME" \
  "$EFFICIENTSAM_TORCH_HOME/hub/checkpoints/$EFFICIENTSAM_SOURCE_FILENAME"
```

Apple's exporter pins the Core AI packages but its EfficientSAM Git dependency
must also resolve to the implementation revision above. Generate and inspect the
script lock, then export only from the isolated verified checkpoint cache:

```sh
cd "$EFFICIENTSAM_COREAI_DIR"
uv lock --script models/efficient-sam/export.py
rg "$EFFICIENTSAM_IMPLEMENTATION_REVISION" models/efficient-sam/export.py.lock

TORCH_HOME="$EFFICIENTSAM_TORCH_HOME" \
uv run --locked --script models/efficient-sam/export.py \
  --model efficient_sam_vitt \
  --dtype float16 \
  --num-queries 64 \
  --num-pts 1 \
  --output-dir "$EFFICIENTSAM_EXPORT_DIR"
```

Do not add `--dynamic` or `--overwrite` to the release conversion. The result
must contain:

```text
efficient_sam_vitt_float16_static_q64/
├── metadata.json
└── efficient_sam_vitt_float16_static_q64.aimodel/
```

Verify that `metadata.json` identifies a `segmenter` and selects the runtime in
`assets.main`. Recompute its fingerprint with the exact PhotoAIKit revision,
run that checkout's tests, and exercise the complete bundle in RawCull 3.3.0:

```sh
EFFICIENTSAM_BUNDLE="$EFFICIENTSAM_EXPORT_DIR/efficient_sam_vitt_float16_static_q64"
EFFICIENTSAM_RUNTIME="$EFFICIENTSAM_BUNDLE/efficient_sam_vitt_float16_static_q64.aimodel"

test -f "$EFFICIENTSAM_BUNDLE/metadata.json"
test -d "$EFFICIENTSAM_RUNTIME"
python3 "$EFFICIENTSAM_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$EFFICIENTSAM_RUNTIME"
swift test --package-path "$EFFICIENTSAM_PHOTOAIKIT_DIR"
```

Record the exporter and lock checksums, resolved dependencies, source checksum,
runtime fingerprint, `main.mlirb` checksum, archive checksum, archive byte count,
and exact RawCull/PhotoAIKit revisions. Package the complete Apache License 2.0
and applicable Apple `coreai-models` BSD 3-Clause notice. Successful conversion
alone is not release approval.

### Create the Meta SAM 3 bundle

| Field                 | Required value                                                     |
| --------------------- | ------------------------------------------------------------------ |
| Checkpoint repository | `facebook/sam3`                                                    |
| Revision              | `3c879f39826c281e95690f02c7821c4de09afae7`                         |
| Weight file           | `model.safetensors`                                                |
| Weight bytes          | `3439938512`                                                       |
| Weight SHA-256        | `6d06f0a5f84e435071fe6603e61d0b4cc7b40e0d39d487cfd4d67d8cc11cc14a` |
| SAM License SHA-256   | `b08db9d32c687054e99cbd41eb1dad19c76936dfb9e2b58e186a01204d8be9ab` |

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

### Validate every generated bundle

Do not use `--dynamic` or `--overwrite` for a release conversion. Preserve the
terminal log and record `uv --version`, `sw_vers`, `xcodebuild -version`, the
PhotoAIKit commit, source checksums, generated metadata, and runtime
fingerprint.

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

Finally, install each complete candidate in RawCullFB, rebuild its
model-specific index, and run the same `semantictest.txt` for both CLIP models.
Compare:

- query-by-query top results and scores;
- image-to-image nearest-neighbour results;
- duplicate or near-duplicate retrieval;
- score spread and repeated ranking patterns;
- missing results, errors, and elapsed time.

A new model fingerprint requires a new index. Never compare one model against an
index created by another model or by an older conversion.

For SAM 3, install the candidate in RawCull and verify text-prompt segmentation,
mask dimensions, mask placement, licence acceptance, relaunch, and removal.

### Prepare the release staging tree

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
│   ├── EfficientSAM/
│   │   ├── metadata.json
│   │   └── efficient_sam_vitt_float16_static_q64.aimodel/
│   └── SAM3/
│       ├── metadata.json
│       ├── tokenizer/
│       └── sam3_float16.aimodel/
├── Notices/
│   ├── CLIP-DataComp/
│   ├── CLIP-OpenAI/
│   ├── EfficientSAM/
│   └── SAM3/
├── Packaging/
│   ├── clip-datacomp.json
│   ├── clip-openai.json
│   ├── efficient-sam.json
│   └── sam3.json
└── Output/
```

Each packaging manifest must select exactly `metadata.json`, the optimized
runtime directory, and the matching notice directory. CLIP and SAM 3 packs also
select `tokenizer`; EfficientSAM has no tokenizer. Example:

```json
{
  "assetPackID": "no.blogspot.RawCull.models.clip-datacomp",
  "downloadPolicy": { "onDemand": {} },
  "fileSelectors": [
    { "file": "Models/CLIP-DataComp/metadata.json" },
    { "directory": "Models/CLIP-DataComp/tokenizer" },
    {
      "directory": "Models/CLIP-DataComp/ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel"
    },
    { "directory": "Notices/CLIP-DataComp" }
  ],
  "platforms": ["macOS"]
}
```

The four stable asset-pack IDs and installed paths are:

| Model         | Asset-pack ID                              | Installed model path   |
| ------------- | ------------------------------------------ | ---------------------- |
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` |
| OpenAI CLIP   | `no.blogspot.RawCull.models.clip-openai`   | `Models/CLIP-OpenAI`   |
| EfficientSAM  | `no.blogspot.RawCull.models.efficient-sam` | `Models/EfficientSAM`  |
| SAM 3         | `no.blogspot.RawCull.models.sam3`          | `Models/SAM3`          |

Generate one `.aar` per cleared manifest from a clean release work tree. The
current `v2` ready set contains the two CLIP packs, so its reproducibility
record is:

```sh
RELEASE_WORK_ROOT=/Users/thomas/ModelAssets/Release
cd "$RELEASE_WORK_ROOT"
xcrun ba-package package Packaging/clip-datacomp.json --output-path Output/clip-datacomp.aar
xcrun ba-package package Packaging/clip-openai.json --output-path Output/clip-openai.aar

shasum -a 256 Output/clip-datacomp.aar Output/clip-openai.aar
stat -f '%N %z bytes' Output/clip-datacomp.aar Output/clip-openai.aar
```

Generate `sam3.aar` only after its descriptor and dated clearance decision are
ready. For RawCull 3.3.0, generate `efficient-sam.aar` from its cleared manifest
and include it with the two CLIP archives under a new immutable release tag:

```sh
xcrun ba-package package Packaging/efficient-sam.json \
  --output-path Output/efficient-sam.aar
```

Treat published archives as immutable. Record each AAR checksum and byte count
in the external release record and matching RawCull catalogue descriptor; do
not place an archive checksum inside that same archive's provenance file. Upload
approved archives before uploading the generated download `manifest.json`.

## Runtime download and activation

Self-hosting is used for the Developer ID distribution. The app and downloader
extension share `group.no.blogspot.RawCull.model-assets`. For an App Store
build, the downloader can instead use Apple hosting; do not enable both hosting
modes in one product.

When the user selects **Download**, RawCull:

1. checks inclusion and release readiness;
2. verifies any required licence acceptance;
3. asks Managed Background Assets for the exact asset-pack ID;
4. reports download progress and supports cancellation;
5. resolves the catalogue-owned installed model path;
6. validates metadata, required resources, runtime asset, fingerprint, and
   configuration;
7. constructs the matching CLIP, EfficientSAM, or SAM 3 provider only after
   validation passes.

Removing a model asks Managed Background Assets to remove its pack and then
refreshes RawCull capabilities. Manually installed models and managed packs must
not be merged into the same candidate directory.

## Release metadata tests

`RawCullTests/ReleaseMetadataTests.swift` is the executable consistency contract
for distribution metadata. It checks:

- application and downloader-extension versions, sandboxing, hardened runtime,
  architecture, deployment target, and shared App Group;
- `BAManifestURL`, `BAUsesAppleHosting`, Background Assets download
  restrictions, allowed domains, and the downloader extension point;
- the exact `ModelAssets/manifest.template.json` asset-pack IDs and managed
  destinations against `RawCullAIModelDownloadCatalog.swift`;
- every blocked descriptor has missing archive evidence, and every ready
  descriptor has a recorded archive checksum and byte count;
- ready/blocked `PROVENANCE.json` states and every notice-file SHA-256; and
- the hashes of the bundled licence texts used by acceptance and review UI.

`RawCullAIModelDownloadsTests.swift` additionally pins the enabled production
set, both published CLIP archive hashes and byte counts, manifest configuration,
release blocking before service invocation, verified licence acceptance,
cancellation/retry state, and checksum-based invalidation of old acceptance. Run
both focused suites for every manifest, catalog, notice, entitlement, hosting,
archive, or inclusion change.

## Signing and provisioning

The application, downloader extension, and App Group identifiers are:

| Purpose                    | Identifier                               |
| -------------------------- | ---------------------------------------- |
| RawCull application        | `no.blogspot.RawCull`                    |
| Model downloader extension | `no.blogspot.RawCull.ModelDownloader`    |
| Shared App Group           | `group.no.blogspot.RawCull.model-assets` |

Both App IDs must have the App Group capability. The app and extension use the
same development team and provisioning setup. Verify the final archive contains
and signs the nested downloader extension before notarizing the Developer ID
release.
