+++
author = "Thomas Evensen"
title = "Evaluating CLIP Models"
linkTitle = "Evaluating CLIP Models"
date = "2026-08-12"
description = "Evaluating CLIP Models Against Source-Framework Cosine Values and RawCullFB"
tags = ["ai", "models", "downloads", "clip", "sam3", "background-assets", "self-hosting", "apple-hosting"]
categories = ["technical details"]
weight = 31
+++

# Evaluating CLIP Models Against Source-Framework Cosine Values and RawCullFB

This document is the complete repeatable procedure for validating CLIP model bundles used by RawCullFB. It covers both supported candidates:

- OpenAI CLIP ViT-B/32 at 224 × 224.
- OpenCLIP DataComp ViT-B/32-256 with `datacomp_s34b_b86k` weights.

SigLIP2 is outside the current evaluation scope.

The procedure has two independent validation layers:

1. **Numerical parity:** compare embeddings produced by the Core AI bundle with reference embeddings produced by the original Hugging Face Transformers or OpenCLIP implementation.
2. **Product behavior:** use RawCullFB to build a real catalog index, execute the same 77 semantic queries, inspect image-similarity neighborhoods, and measure labeled retrieval quality.

A model must pass both layers. Numerical parity proves that the conversion and integration reproduce the source model; it does not prove that the model retrieves useful photographs. Conversely, plausible search results do not prove that the converted model is correct.

## 1. What cosine parity means

For a reference embedding `r` and Core AI embedding `c`, CLIPBench calculates:

```text
cosine(r, c) = dot(r, c) / (norm(r) × norm(c))
```

It also reports the largest element-wise difference:

```text
max_absolute_error = max(abs(r[i] - c[i]))
```

Both source and exported models produce L2-normalized embeddings. Identical normalized vectors have cosine `1.0`. Float16 conversion, platform image decoding, and framework implementation details can produce small differences.

Use these gates:

| Test path | Minimum cosine | Purpose |
|---|---:|---|
| Text embeddings | `0.999` | Tokenizer, text encoder, output selection, and normalization |
| Canonical lossless image inputs | `0.999` | Resize, crop, normalization, image encoder, and output selection |
| End-to-end JPEG/PNG fixtures | `0.998` | Real platform decoding plus preprocessing and inference |

The existing ten-image fixture set contains JPEG files and one PNG. Its release gate is therefore `0.998`. A strict `0.999` run is useful diagnostically but can fail because Apple ImageIO and Pillow decode some JPEG pixels differently. Do not lower a threshold to hide a broad or unexplained mismatch.

Raw semantic-search scores are different from parity cosine values:

- **Parity cosine** compares the same embedding from two implementations.
- **Semantic score** compares a text embedding with an image embedding.
- **Image-similarity score** compares two image embeddings.

Do not apply the parity threshold to semantic search or duplicate detection.

## 2. Current validated components

Record the live values again whenever this procedure is run. As of 2026-08-12, the relevant local state is:

| Component | Current identity/path |
|---|---|
| PhotoAIKit used by RawCullFB | revision `6e3216027b267c27ccaf99d334807b18ea1aaec9` |
| OpenAI bundle | `/Users/thomas/ModelAssets/Release/Models/CLIP-OpenAI` |
| OpenAI source revision | `3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268` |
| DataComp bundle | `/Users/thomas/ModelAssets/Release/Models/CLIP-DataComp` |
| DataComp preset | `ViT-B-32-256` / `datacomp_s34b_b86k` |
| CLIPBench | `/Users/thomas/GitHubCLIPtests/CLIPBench` |
| RawCullFB | `/Users/thomas/GitHub/RawCull/RawCullFB` |
| PhotoAIKit source tools | `/Users/thomas/GitHub/RawCull/PhotoAIKit` |
| Fixture set | `/Users/thomas/Library/Mobile Documents/com~apple~CloudDocs/TestPhotos/CLIPParityFixtures` |
| Semantic catalog | `/Users/thomas/Library/Mobile Documents/com~apple~CloudDocs/TestPhotos/testphotos` |
| Canonical 77 queries | `/Users/thomas/GitHub/RawCull/RawCullFB/semantictest.txt` |

The DataComp metadata now explicitly identifies `datacomp_s34b_b86k`; older bundles containing only a generic `open_clip_model.safetensors` label must not be reused without proving their weight identity.

## 3. Requirements

- Apple Silicon Mac.
- macOS 27 or the version required by the current projects.
- Xcode 27 and its command-line tools.
- `uv` for the pinned Python environments declared in the PhotoAIKit scripts.
- Access to the Hugging Face/OpenCLIP weights when regenerating references or bundles.
- Enough disk space for Python model caches, Core AI bundles, Xcode DerivedData, and two catalog indexes.
- The exact same image bytes for source-framework and Core AI parity.

The Python reference scripts declare pinned package versions in their inline `uv` metadata. Do not change those dependencies during a comparison.

## 4. Establish one evaluation workspace

Open a new `zsh` terminal and define the paths once:

```sh
RAW_CULL_ROOT=/Users/thomas/GitHub/RawCull/RawCull
RAW_CULL_FB_ROOT=/Users/thomas/GitHub/RawCull/RawCullFB
PHOTO_AI_KIT_ROOT=/Users/thomas/GitHub/RawCull/PhotoAIKit
CLIP_BENCH_ROOT=/Users/thomas/GitHubCLIPtests/CLIPBench

FIXTURE_ROOT='/Users/thomas/Library/Mobile Documents/com~apple~CloudDocs/TestPhotos/CLIPParityFixtures'
REFERENCE_ROOT="$FIXTURE_ROOT/reference"
CATALOG_ROOT='/Users/thomas/Library/Mobile Documents/com~apple~CloudDocs/TestPhotos/testphotos'
QUERY_FILE="$RAW_CULL_FB_ROOT/semantictest.txt"

OPENAI_BUNDLE=/Users/thomas/ModelAssets/Release/Models/CLIP-OpenAI
DATACOMP_BUNDLE=/Users/thomas/ModelAssets/Release/Models/CLIP-DataComp

EVALUATION_ROOT='/Users/thomas/Library/Mobile Documents/com~apple~CloudDocs/TestPhotos/CLIPModelEvaluations'
mkdir -p "$REFERENCE_ROOT" "$EVALUATION_ROOT"
```

Keep these variables in the same terminal session. If a path changes, update it here rather than editing individual commands later.

Create a run identifier so reports are not overwritten:

```sh
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ROOT="$EVALUATION_ROOT/$RUN_ID"
mkdir -p "$RUN_ROOT"
```

## 5. Record the software and model identities

Record source revisions before building or generating references:

```sh
{
  date -u
  sw_vers
  xcodebuild -version
  xcrun swift --version
  uv --version
  git -C "$RAW_CULL_FB_ROOT" rev-parse HEAD
  git -C "$PHOTO_AI_KIT_ROOT" rev-parse HEAD
  git -C "$CLIP_BENCH_ROOT" rev-parse HEAD
} > "$RUN_ROOT/environment.txt"
```

Save the model metadata and hashes:

```sh
cp "$OPENAI_BUNDLE/metadata.json" "$RUN_ROOT/openai-metadata.json"
cp "$DATACOMP_BUNDLE/metadata.json" "$RUN_ROOT/datacomp-metadata.json"

shasum -a 256 \
  "$OPENAI_BUNDLE/metadata.json" \
  "$DATACOMP_BUNDLE/metadata.json" \
  > "$RUN_ROOT/model-metadata-sha256.txt"
```

Verify the important fields manually:

```sh
sed -n '1,130p' "$OPENAI_BUNDLE/metadata.json"
sed -n '1,130p' "$DATACOMP_BUNDLE/metadata.json"
```

Required OpenAI identity:

```text
source_model: openai/clip-vit-base-patch32
source_revision: 3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268
architecture: ViT-B-32
input: 1 × 3 × 224 × 224
resize/crop/interpolation: shortest-side / center / bicubic
embedding dimensions: 512
token context: 77
padding token: 49407
```

Required DataComp identity:

```text
source_model: mlfoundations/open_clip
architecture: ViT-B-32-256
pretrained: datacomp_s34b_b86k
input: 1 × 3 × 256 × 256
resize/crop/interpolation: shortest-side / center / bicubic
embedding dimensions: 512
token context: 77
padding token: 0
```

Stop if a bundle's checkpoint, input size, tokenizer, normalization, function names, or preprocessing metadata differs from the source reference that will be generated.

### 5.1 Optional: recreate the Core AI bundles

Skip this subsection when testing the existing release bundles. Use it when the converted assets themselves must be rebuilt. Export into an isolated staging directory; do not overwrite the release bundles before parity succeeds.

```sh
STAGING_MODEL_ROOT=/Users/thomas/ModelAssets/Staging/CLIP-Model-Evaluation
mkdir -p "$STAGING_MODEL_ROOT"

cd "$PHOTO_AI_KIT_ROOT"

uv run Tools/export_clip.py \
  --model openai \
  --dtype float16 \
  --output-dir "$STAGING_MODEL_ROOT" \
  --bundle-name CLIP-OpenAI

uv run Tools/export_clip.py \
  --model openclip-datacomp \
  --architecture ViT-B-32-256 \
  --pretrained datacomp_s34b_b86k \
  --dtype float16 \
  --output-dir "$STAGING_MODEL_ROOT" \
  --bundle-name CLIP-DataComp
```

The DataComp exporter verifies tokenizer IDs against OpenCLIP before completing. Inspect both staged metadata files and run the entire parity procedure against the staged paths. Promote a staged bundle only after it passes. If a staging bundle already exists, choose a new staging directory or intentionally use the exporter's `--overwrite` option after verifying the exact target.

To evaluate the staged bundles in the remaining commands, replace the definitions from Section 4:

```sh
OPENAI_BUNDLE="$STAGING_MODEL_ROOT/CLIP-OpenAI"
DATACOMP_BUNDLE="$STAGING_MODEL_ROOT/CLIP-DataComp"
```

## 6. Verify PhotoAIKit and RawCullFB use the same implementation

RawCullFB currently pins PhotoAIKit remotely. Confirm the project and resolved lock file agree:

```sh
rg -n -C 5 'PhotoAIKit|photoaikit' \
  "$RAW_CULL_FB_ROOT/RawCullFB.xcodeproj/project.pbxproj" \
  "$RAW_CULL_FB_ROOT/RawCullFB.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved"
```

CLIPBench currently uses `/Users/thomas/GitHubCLIPtests/PhotoAIKit` through `../PhotoAIKit`. Confirm that checkout is the same revision and contains the Pillow-compatible preprocessing fix:

```sh
git -C /Users/thomas/GitHubCLIPtests/PhotoAIKit rev-parse HEAD
rg -n 'pillowBicubicPreprocessingVersion' \
  /Users/thomas/GitHubCLIPtests/PhotoAIKit/Sources/CoreAICLIPBackend/CoreAICLIPProvider.swift
```

The revision must equal the PhotoAIKit revision resolved by RawCullFB. If it does not, update the dependency or checkout before proceeding. Otherwise CLIPBench and RawCullFB would test different implementations.

## 7. Verify the immutable fixture set

The fixture set must contain ten exact images plus `manifest.json`:

```sh
find "$FIXTURE_ROOT/images" -maxdepth 1 -type f -print | sort
sed -n '1,220p' "$FIXTURE_ROOT/manifest.json"
```

Expected images:

```text
01-dog-outdoors.jpg
02-person-portrait.jpg
03-car-road.jpg
04-city-night.jpg
05-mountain-landscape.png
06-beetle-macro.jpg
07-kitchen-interior.jpg
08-motion-blur.jpg
09-sign-text.jpg
10-yellow-sunflower.jpg
```

Compute and save their hashes:

```sh
shasum -a 256 "$FIXTURE_ROOT"/images/0*.* \
  "$FIXTURE_ROOT"/images/10-yellow-sunflower.jpg \
  > "$RUN_ROOT/fixture-sha256.txt"
```

Compare every hash with `manifest.json`. Stop if a file is missing or changed. A regenerated reference from different image bytes is a different benchmark.

The ten prompts come from `manifest.json` and must remain in the same order as the images.

## 8. Test PhotoAIKit before model parity

Run the focused preprocessing/text tests and then the complete package suite:

```sh
cd "$PHOTO_AI_KIT_ROOT"
swift test --filter CLIPTextCapabilityTests
swift test
```

Required result: all tests pass. In particular, the suite must cover:

- tokenizer construction and padding behavior;
- center crop rather than stretch;
- integer-floor crop origin;
- Pillow-compatible bicubic pixels;
- top-to-bottom orientation;
- output shape and L2 normalization; and
- preprocessing-version cache invalidation.

Do not start model parity if these tests fail.

## 9. Generate the OpenAI Hugging Face reference

Use the fixture-specific script because it writes:

- normalized embeddings consumed by CLIPBench;
- exact preprocessed pixel tensors;
- token IDs and attention masks;
- raw and normalized image/text embeddings;
- the 10 × 10 image-to-text cosine matrix; and
- reference rankings.

Generate all artifacts:

```sh
cd "$FIXTURE_ROOT"

uv run Scripts/generate_openai_clip_reference.py \
  --manifest "$FIXTURE_ROOT/manifest.json" \
  --output-directory "$REFERENCE_ROOT"
```

Expected outputs:

```text
openai-clip-reference.json
openai-clip-reference-details.json
openai-clip-reference-tensors.npz
```

Verify that the Hugging Face revision recorded in the details file exactly equals the bundle's `source_revision`:

```sh
rg -n 'model_id|model_revision|transformers_version|torch_version' \
  "$REFERENCE_ROOT/openai-clip-reference-details.json"

rg -n 'source_model|source_revision' "$OPENAI_BUNDLE/metadata.json"
```

If the revisions differ, the reference and Core AI bundle do not represent the same source model. Stop and regenerate one side from the intended pinned revision.

Save reference hashes:

```sh
shasum -a 256 \
  "$REFERENCE_ROOT/openai-clip-reference.json" \
  "$REFERENCE_ROOT/openai-clip-reference-details.json" \
  "$REFERENCE_ROOT/openai-clip-reference-tensors.npz" \
  > "$RUN_ROOT/openai-reference-sha256.txt"
```

## 10. Generate the DataComp OpenCLIP reference

DataComp weights may be hosted through model registries, but the authoritative runtime behavior for this model is the pinned OpenCLIP implementation—not the OpenAI Hugging Face Transformers class. Use the same architecture and pretrained tag used to export the Core AI bundle.

First record the OpenCLIP registry configuration:

```sh
cd "$PHOTO_AI_KIT_ROOT"

uv run --with open_clip_torch==3.2.0 python -c \
  'import json, open_clip; print(json.dumps(open_clip.get_pretrained_cfg("ViT-B-32-256", "datacomp_s34b_b86k"), indent=2, default=str))' \
  > "$RUN_ROOT/datacomp-openclip-registry.json"
```

Generate the reference directly under the fixture reference directory so all image paths remain valid relative paths:

```sh
uv run Tools/generate_clip_reference.py \
  --model openclip-datacomp \
  --architecture ViT-B-32-256 \
  --pretrained datacomp_s34b_b86k \
  --image "$FIXTURE_ROOT/images/01-dog-outdoors.jpg" \
  --image "$FIXTURE_ROOT/images/02-person-portrait.jpg" \
  --image "$FIXTURE_ROOT/images/03-car-road.jpg" \
  --image "$FIXTURE_ROOT/images/04-city-night.jpg" \
  --image "$FIXTURE_ROOT/images/05-mountain-landscape.png" \
  --image "$FIXTURE_ROOT/images/06-beetle-macro.jpg" \
  --image "$FIXTURE_ROOT/images/07-kitchen-interior.jpg" \
  --image "$FIXTURE_ROOT/images/08-motion-blur.jpg" \
  --image "$FIXTURE_ROOT/images/09-sign-text.jpg" \
  --image "$FIXTURE_ROOT/images/10-yellow-sunflower.jpg" \
  --text "a woman with a dog outdoors" \
  --text "a portrait of a woman wearing sunglasses" \
  --text "an old car driving on a country road" \
  --text "an illuminated city building at night" \
  --text "mountains surrounding a large lake" \
  --text "a macro photograph of an insect" \
  --text "the interior of a kitchen" \
  --text "a colorful amusement ride with motion blur" \
  --text "a green road sign with white text" \
  --text "a yellow sunflower" \
  --output "$REFERENCE_ROOT/datacomp-clip-reference.json"
```

Verify identity, counts, and relative paths:

```sh
sed -n '1,25p' "$REFERENCE_ROOT/datacomp-clip-reference.json"
rg -c '"path"' "$REFERENCE_ROOT/datacomp-clip-reference.json"
rg -c '"text"' "$REFERENCE_ROOT/datacomp-clip-reference.json"
```

Required source block:

```text
model: openclip-datacomp
architecture: ViT-B-32-256
pretrained: datacomp_s34b_b86k
```

Required counts: 10 images and 10 texts.

Each image path must resolve from `REFERENCE_ROOT`. Test all paths before parity:

```sh
cd "$REFERENCE_ROOT"
test -f ../images/01-dog-outdoors.jpg
test -f ../images/10-yellow-sunflower.jpg
```

Do not reuse a DataComp reference containing paths to a deleted `Downloads/CLIPParityFixtures` directory or the obsolete missing `_DSC7115.ARW.png` fixture.

Save its hash:

```sh
shasum -a 256 "$REFERENCE_ROOT/datacomp-clip-reference.json" \
  > "$RUN_ROOT/datacomp-reference-sha256.txt"
```

## 11. Build CLIPBench from the intended PhotoAIKit revision

Verify its dependency first:

```sh
cd "$CLIP_BENCH_ROOT"
sed -n '1,45p' Package.swift
git -C ../PhotoAIKit rev-parse HEAD
```

Then test and build:

```sh
swift test
swift build -c release --product clipbench
```

Use the freshly built executable:

```text
/Users/thomas/GitHubCLIPtests/CLIPBench/.build/release/clipbench
```

Inspect both bundles through the same runtime that will perform parity:

```sh
.build/release/clipbench inspect-model --model "$OPENAI_BUNDLE" \
  | tee "$RUN_ROOT/openai-model-inspection.txt"

.build/release/clipbench inspect-model --model "$DATACOMP_BUNDLE" \
  | tee "$RUN_ROOT/datacomp-model-inspection.txt"
```

Confirm that the printed source, architecture, pretrained tag, input geometry, tokenizer version, embedding dimensions, and model fingerprint match the recorded metadata.

## 12. Run OpenAI Core AI parity

Run the release gate and preserve its output:

```sh
cd "$CLIP_BENCH_ROOT"
set -o pipefail

.build/release/clipbench parity \
  --reference "$REFERENCE_ROOT/openai-clip-reference.json" \
  --model "$OPENAI_BUNDLE" \
  --minimum-cosine 0.998 \
  | tee "$RUN_ROOT/openai-parity.txt"
```

Expected characteristics from the corrected implementation:

- all text rows approximately `1.0000`;
- nine image rows at or above approximately `0.999`;
- minimum image cosine approximately `0.9988` for the existing JPEG-heavy fixture set; and
- command exits successfully at the `0.998` threshold.

Also run the strict diagnostic threshold:

```sh
.build/release/clipbench parity \
  --reference "$REFERENCE_ROOT/openai-clip-reference.json" \
  --model "$OPENAI_BUNDLE" \
  --minimum-cosine 0.999 \
  > "$RUN_ROOT/openai-parity-strict.txt" 2>&1
```

This strict end-to-end command may return nonzero because of the known JPEG decoder variance. Preserve the output; do not treat that specific documented result as a model failure if the `0.998` release gate passes and lossless tests remain green.

## 13. Run DataComp Core AI parity

Use its independently generated OpenCLIP reference:

```sh
cd "$CLIP_BENCH_ROOT"
set -o pipefail

.build/release/clipbench parity \
  --reference "$REFERENCE_ROOT/datacomp-clip-reference.json" \
  --model "$DATACOMP_BUNDLE" \
  --minimum-cosine 0.998 \
  | tee "$RUN_ROOT/datacomp-parity.txt"
```

Required result:

- command exits successfully;
- every text row is at least `0.999`;
- end-to-end minimum across all rows is at least `0.998`; and
- no individual maximum-absolute-error value is unexpectedly large relative to the other fixtures.

Run the strict diagnostic threshold as well:

```sh
.build/release/clipbench parity \
  --reference "$REFERENCE_ROOT/datacomp-clip-reference.json" \
  --model "$DATACOMP_BUNDLE" \
  --minimum-cosine 0.999 \
  > "$RUN_ROOT/datacomp-parity-strict.txt" 2>&1
```

Do not assume DataComp inherits OpenAI's numerical result merely because both use the same PhotoAIKit preprocessing code. It has different weights, input resolution, padding behavior, and exported functions.

## 14. Diagnose parity failures

Use the failure pattern to select the first investigation:

| Pattern | Likely first checks |
|---|---|
| Text and images fail | Wrong checkpoint, stale CLIPBench build, wrong model asset, or wrong output tensor |
| Text fails; images pass | Token IDs, padding token, EOT handling, attention mask, text output, or normalization |
| Text passes; all images fail | Resize dimension, crop origin, interpolation, color order, mean/std, orientation, image output, or normalization |
| Only JPEG images are slightly below `0.999` | Apple ImageIO versus Pillow decoding |
| One image fails badly | Missing/corrupt fixture, EXIF orientation, unsupported decoding, or stale relative path |
| Correct cosine but changed top-k on a fixture matrix | Near-tie or ranking instability; inspect exact cosine matrix |

For OpenAI, inspect `openai-clip-reference-tensors.npz` and the details JSON to isolate:

1. preprocessed pixels;
2. token IDs and masks;
3. raw model outputs;
4. normalized outputs; and
5. the cosine/ranking matrix.

For DataComp, extend the reference generator to emit equivalent intermediate tensors if a parity failure cannot be localized from embeddings alone.

Parity failure blocks RawCullFB quality evaluation. Fix the integration before judging semantic retrieval.

## 15. Build and test RawCullFB

Confirm the project has no unexpected changes and still resolves the intended PhotoAIKit revision:

```sh
cd "$RAW_CULL_FB_ROOT"
git status --short
rg -n -C 5 'PhotoAIKit|photoaikit' \
  RawCullFB.xcodeproj/project.pbxproj \
  RawCullFB.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved
```

Run its tests:

```sh
xcodebuild \
  -project RawCullFB.xcodeproj \
  -scheme RawCullFB \
  -destination 'platform=macOS,arch=arm64' \
  test
```

Build an unsigned Release product for local validation:

```sh
xcodebuild \
  -project RawCullFB.xcodeproj \
  -scheme RawCullFB \
  -configuration Release \
  -destination 'platform=macOS,arch=arm64' \
  -derivedDataPath /tmp/RawCullFB-CLIP-Evaluation \
  CODE_SIGNING_ALLOWED=NO \
  build
```

Expected product:

```text
/tmp/RawCullFB-CLIP-Evaluation/Build/Products/Release/RawCullFB.app
```

`CODE_SIGNING_ALLOWED=NO` validates compilation only. Use the project's normal signing, archive, notarization, and DMG workflow for distribution.

## 16. Freeze the semantic test catalog and queries

Both models must use:

- the exact same catalog root;
- the exact same image bytes;
- the exact same query file;
- the same result limit;
- a complete model-specific index; and
- the same RawCullFB/PhotoAIKit revisions.

Copy the canonical query file into the catalog root under the required name:

```sh
cp "$QUERY_FILE" "$CATALOG_ROOT/semantictest.txt"
wc -l "$CATALOG_ROOT/semantictest.txt"
cmp "$QUERY_FILE" "$CATALOG_ROOT/semantictest.txt"
```

Expected query count: 77 non-comment queries.

Record catalog files without including RawCullFB's hidden index or generated reports:

```sh
find "$CATALOG_ROOT" -type f \
  ! -path '*/.clipbench/*' \
  ! -name '*-semantic-test-results.txt' \
  ! -name 'semantictest.txt' \
  -print | sort > "$RUN_ROOT/catalog-files.txt"

wc -l "$RUN_ROOT/catalog-files.txt"
shasum -a 256 "$CATALOG_ROOT/semantictest.txt" \
  > "$RUN_ROOT/semantic-query-sha256.txt"
```

For strict reproducibility, compute content hashes for the complete catalog and save them with the run. This can be slow for a large photo collection.

## 17. RawCullFB test for OpenAI CLIP

Launch the validated RawCullFB build, then:

1. Open **RawCullFB > Settings > CLIP**.
2. Choose `/Users/thomas/ModelAssets/Release/Models/CLIP-OpenAI`.
3. Wait until verification reports a valid model and note its fingerprint.
4. Select `CATALOG_ROOT` as the photo-folder root.
5. Choose **Index Selected Folder** or **Update Index**.
6. Wait until indexing completes with no unexplained failures.
7. Confirm search is enabled and the index belongs to the selected model.
8. Set **Maximum results** to 50.
9. Choose **Run Model Test** in the main toolbar.
10. Wait for all 77 queries and the image-similarity evaluation to finish.

RawCullFB writes:

```text
<model-name>-semantic-test-results.txt
```

in the selected catalog root. Immediately preserve it under the run directory:

```sh
find "$CATALOG_ROOT" -maxdepth 1 -type f \
  -name '*semantic-test-results.txt' -print

cp "$CATALOG_ROOT/ViT-B-32-semantic-test-results.txt" \
  "$RUN_ROOT/openai-rawcullfb-results.txt"
```

If the generated filename differs, use the filename RawCullFB reports rather than assuming the example name.

## 18. RawCullFB test for DataComp CLIP

Repeat the workflow without changing catalog or query settings:

1. Open **RawCullFB > Settings > CLIP**.
2. Choose `/Users/thomas/ModelAssets/Release/Models/CLIP-DataComp`.
3. Wait for valid model verification and record its distinct fingerprint.
4. Keep the same `CATALOG_ROOT` selected.
5. Choose **Index Selected Folder** or **Update Index**.
6. Confirm RawCullFB creates/uses a DataComp-specific `.clipbench/clip-<model-hash>.clipindex`.
7. Wait for the complete DataComp index; never evaluate a partial or stale index.
8. Keep the result limit at 50.
9. Choose **Run Model Test**.
10. Wait for all semantic queries and image-similarity anchors to complete.

Preserve the report:

```sh
cp "$CATALOG_ROOT/datacomp_s34b_b86k-semantic-test-results.txt" \
  "$RUN_ROOT/datacomp-rawcullfb-results.txt"
```

Again, use the actual filename if RawCullFB emits a different model label.

OpenAI and DataComp indexes must remain separate. A model fingerprint, preprocessing version, or dimension mismatch must invalidate reuse. If switching models does not require its own index, stop and inspect index identity handling.

## 19. Validate RawCullFB result-file integrity

Inspect both headers:

```sh
for REPORT in \
  "$RUN_ROOT/openai-rawcullfb-results.txt" \
  "$RUN_ROOT/datacomp-rawcullfb-results.txt"
do
  echo "--- $REPORT"
  sed -n '1,18p' "$REPORT"
done
```

Require:

- correct model name;
- correct and distinct model fingerprint;
- identical catalog path;
- `status` equal to `completed`;
- `completed_queries` equal to `77`;
- `total_queries` equal to `77`;
- identical result limit, normally 50; and
- `similarity_status` equal to `completed`.

Count query and anchor sections:

```sh
for REPORT in \
  "$RUN_ROOT/openai-rawcullfb-results.txt" \
  "$RUN_ROOT/datacomp-rawcullfb-results.txt"
do
  printf '%s\tqueries=' "$REPORT"
  rg -c '^QUERY\t' "$REPORT"
  printf '%s\tanchors=' "$REPORT"
  rg -c '^ANCHOR\t' "$REPORT"
done
```

The established catalog contains 453 similarity anchors. If the catalog changes, record and explain the new anchor count; do not compare it silently with an older run.

## 20. Semantic sanity checks before labeling

Calculate or inspect at least:

- distinct top-1 images across 77 queries;
- most frequent top-1 image and its frequency;
- unique images appearing across all top-50 results;
- mean top-1 minus top-2 score margin;
- mean shared top-10 results across all query pairs;
- mean shared top-10 results within the five paraphrase groups;
- first-query time; and
- warmed mean, median, and P95 query time.

The five paraphrase groups are queries 63–77:

1. dog on a beach;
2. city street at night;
3. sharp portrait;
4. blurry photograph; and
5. beautiful landscape.

Expected healthy behavior:

- unrelated prompts do not all return the same small pool;
- no single universal image wins a large fraction of unrelated queries;
- paraphrase overlap is materially higher than unrelated-query overlap;
- object prompts return visibly plausible objects in top positions; and
- query latency stabilizes after model warm-up.

The corrected OpenAI integration previously produced 53 distinct top-1 images, a maximum hub frequency of 4/77, and substantially higher paraphrase than general overlap. Treat a return to the old collapsed pattern as an integration or index problem.

These are sanity checks, not accuracy metrics.

## 21. Create one pooled relevance-label set

For every query, pool the first five results from both models:

```text
OpenAI top five union DataComp top five
```

Deduplicate identical query/image pairs and, if practical, hide the originating model during review. Create a CSV:

```text
query_id,query,file,path,openai_rank,datacomp_rank,relevance,notes
```

Use the same graded scale for both models:

| Relevance | Definition |
|---:|---|
| 2 | Clearly and directly satisfies the query |
| 1 | Partially relevant, ambiguous, or missing an important attribute/relation |
| 0 | Irrelevant |

Inspect the actual image. Do not label from filenames, cosine scores, or which model retrieved it.

Calculate for each model:

- Precision@1;
- Precision@5;
- mean reciprocal rank (MRR);
- nDCG@5 using relevance 0/1/2; and
- metrics by query category.

Categories should include:

- objects and scenes;
- colors and attributes;
- actions and relations;
- photographic quality/style;
- composition;
- count, spatial relation, and negation; and
- paraphrases.

With only 77 queries, report raw counts as well as averages. Do not select a model from a tiny aggregate difference without reviewing category failures and uncertainty.

## 22. Evaluate image similarity separately

RawCullFB's anchor neighborhoods are useful for finding obvious failures but are not a calibrated duplicate benchmark. Build a labeled pair set containing:

- exact duplicates;
- resized/re-encoded duplicates;
- color and exposure edits;
- crops;
- adjacent burst frames;
- same subject in a different photograph;
- semantically related but visually different hard negatives; and
- unrelated negatives.

For each model, calculate:

- ROC-AUC;
- precision-recall AUC;
- false-positive rate at the chosen recall;
- false-negative rate at the chosen threshold; and
- a confusion matrix for the proposed action.

Choose separate thresholds for OpenAI and DataComp. Their cosine distributions are not interchangeable. A threshold suitable for suggestions is not automatically safe for grouping, deletion, or another destructive action.

## 23. Compare operational behavior

Use the same Mac, OS, app revision, catalog, and measurement method for both models. Record:

- model bundle size;
- cold model-load/first-query latency;
- warmed P50/P95/P99 search latency;
- image-indexing throughput;
- peak memory during indexing and searching;
- complete index size; and
- energy impact if available.

Run at least 30 unmeasured warm-up queries before measuring steady-state latency. DataComp uses 256 × 256 inputs versus OpenAI's 224 × 224 and may have a different indexing cost even though both produce 512-dimensional embeddings.

## 24. Decision table

Complete this table and save it with the run:

| Gate or metric | OpenAI ViT-B/32 | DataComp ViT-B/32-256 | Decision |
|---|---:|---:|---|
| Source identity verified | | | |
| Minimum text parity | | | |
| Minimum end-to-end image parity | | | |
| Precision@1 | | | |
| Precision@5 | | | |
| MRR | | | |
| nDCG@5 | | | |
| Weakest query category | | | |
| Largest semantic hub | | | |
| Paraphrase top-10 overlap | | | |
| Similarity PR-AUC | | | |
| Similarity FPR at selected recall | | | |
| Cold first-query latency | | | |
| Warm P95 latency | | | |
| Indexing throughput | | | |
| Peak memory | | | |
| Bundle size | | | |
| Index size | | | |

Selection rules:

- Reject any model whose source identity or numerical parity is unresolved.
- Reject any model showing semantic collapse or unacceptable labeled quality.
- Never select a model because it produces numerically higher raw similarity scores.
- Prefer DataComp only if it delivers a material labeled-quality improvement at acceptable operational cost.
- If quality is effectively tied, OpenAI is the simpler established control.
- It is acceptable to ship OpenAI and keep DataComp experimental.

## 25. Archive the complete evidence package

At minimum, `RUN_ROOT` should contain:

```text
environment.txt
fixture-sha256.txt
semantic-query-sha256.txt
catalog-files.txt
openai-metadata.json
datacomp-metadata.json
model-metadata-sha256.txt
openai-reference-sha256.txt
datacomp-reference-sha256.txt
datacomp-openclip-registry.json
openai-model-inspection.txt
datacomp-model-inspection.txt
openai-parity.txt
openai-parity-strict.txt
datacomp-parity.txt
datacomp-parity-strict.txt
openai-rawcullfb-results.txt
datacomp-rawcullfb-results.txt
relevance-labels.csv
semantic-metrics.json
similarity-pairs.csv
similarity-metrics.json
decision.md
```

Also preserve the exact source reference JSON files or their immutable hashes. The reference JSON stores paths relative to its own directory; moving only the JSON without its fixture images can break future parity runs.

## 26. Final release checklist

### Shared implementation

- [ ] PhotoAIKit focused and full tests pass.
- [ ] CLIPBench and RawCullFB use the same PhotoAIKit revision.
- [ ] RawCullFB tests and Release build pass.
- [ ] Model metadata and asset fingerprints are archived.

### OpenAI

- [ ] Hugging Face revision matches bundle `source_revision`.
- [ ] Ten-image/ten-text reference regenerated from immutable fixtures.
- [ ] Text parity is at least `0.999`.
- [ ] End-to-end fixture parity is at least `0.998`.
- [ ] RawCullFB completes 77 queries and all anchors using a fresh model-specific index.

### DataComp

- [ ] Architecture and `datacomp_s34b_b86k` identity are recorded.
- [ ] OpenCLIP registry configuration is archived.
- [ ] DataComp reference is regenerated from the same preset and fixtures.
- [ ] All reference image paths resolve.
- [ ] Text parity is at least `0.999`.
- [ ] End-to-end fixture parity is at least `0.998`.
- [ ] RawCullFB completes 77 queries and all anchors using a fresh model-specific index.

### Product quality

- [ ] Pooled top-five results are labeled consistently.
- [ ] Precision@1, Precision@5, MRR, and nDCG@5 are reported.
- [ ] Category-level failures are reviewed.
- [ ] No universal semantic hub exists.
- [ ] Paraphrases are more consistent than unrelated prompts.
- [ ] Similarity positive and hard-negative pairs are labeled.
- [ ] Model-specific similarity thresholds meet the approved false-positive ceiling.
- [ ] Latency, throughput, memory, bundle size, and index size are acceptable.
- [ ] The final OpenAI/DataComp decision is documented.

## 27. Short execution order

When repeating the evaluation later:

1. Define paths and create `RUN_ROOT`.
2. Record software revisions and model metadata.
3. Verify immutable fixture hashes.
4. Test PhotoAIKit.
5. Generate the pinned OpenAI Hugging Face reference.
6. Generate the exact DataComp OpenCLIP reference.
7. Build CLIPBench from the matching PhotoAIKit revision.
8. Run and archive both parity tests.
9. Test and compile RawCullFB.
10. Freeze the catalog and 77-query file.
11. Build a clean OpenAI index and run the RawCullFB model test.
12. Build a clean DataComp index and run the same test.
13. Validate report integrity and collapse diagnostics.
14. Label the pooled top-five results.
15. Calculate semantic and image-similarity metrics.
16. Compare operational costs.
17. Complete the decision table and release checklist.

The result is defensible only when the archived evidence links the exact source checkpoint, converted asset, preprocessing implementation, fixture bytes, catalog, query file, RawCullFB build, and human relevance labels.
