+++
author = "Thomas Evensen"
title = "New RawCull AI models"
linkTitle = "New RawCull AI models"
date = "2026-08-10"
lastmod = "2026-09-02"
description = "Release runbook for publishing DataComp CLIP, OpenAI CLIP, EfficientSAM, and Meta SAM 3."
tags = ["ai", "models", "downloads", "clip", "efficient-sam", "sam3", "background-assets", "self-hosting", "apple-hosting"]
categories = ["technical details"]
weight = 31
+++

# Publishing new RawCull AI models

This runbook publishes four optional models:

| Model         | Asset-pack ID                              | Installed destination  |
| ------------- | ------------------------------------------ | ---------------------- |
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` |
| OpenAI CLIP   | `no.blogspot.RawCull.models.clip-openai`   | `Models/CLIP-OpenAI`   |
| EfficientSAM  | `no.blogspot.RawCull.models.efficient-sam` | `Models/EfficientSAM`  |
| Meta SAM 3    | `no.blogspot.RawCull.models.sam3`          | `Models/SAM3`          |

SigLIP2 remains deliberately excluded. EfficientSAM is planned for RawCull
3.3.0 and must be prepared as a new pack; do not mutate the published `v2`
release to add it.

The published record described by this page is the `v2` release in
[`RawCull-AI-Models`](https://github.com/rsyncOSX/RawCull-AI-Models/releases).
Tag names and GitHub release URLs are case-sensitive.

The current `v2` manifest publishes DataComp CLIP and OpenAI CLIP only. Meta SAM
3 remains blocked and must not be uploaded or added to the deployable manifest
until its redistribution review is complete. The RawCull 3.3.0 release should
add EfficientSAM under a new immutable model-release tag after its technical and
licence gates pass.

The literal `v2` hashes, sizes, URLs, and commands below are a reproducibility
record for that publication. They are not a reusable instruction to mutate the
same tag. For a new release, define these variables once and use a new immutable
tag and monotonically increasing per-pack versions:

```sh
MODEL_RELEASE_REPOSITORY='rsyncOSX/RawCull-AI-Models'
MODEL_RELEASE_TAG='vNEXT'
DATACOMP_PACK_VERSION='NEXT_INTEGER'
OPENAI_PACK_VERSION='NEXT_INTEGER'
EFFICIENTSAM_PACK_VERSION='NEXT_INTEGER'
SAM3_PACK_VERSION='NEXT_INTEGER'
RELEASE_SOURCE_ROOT='/path/to/RawCull-AI-Models/ModelAssets/Release'
RELEASE_WORK_ROOT='/path/to/private/release-work/ModelAssets/Release'
RELEASE_OUTPUT_ROOT="$RELEASE_WORK_ROOT/Output"
DOWNLOAD_BASE_URL="https://github.com/$MODEL_RELEASE_REPOSITORY/releases/download/$MODEL_RELEASE_TAG/"
```

Copy the reviewed `Models`, `Notices`, and `Packaging` directories from
`RELEASE_SOURCE_ROOT` into a clean `RELEASE_WORK_ROOT`; generate archives and
the manifest only under `RELEASE_OUTPUT_ROOT`. Never use a personal absolute
path as release identity or paste it into provenance.

## Release sources of truth

| Location | Authority |
|---|---|
| `RawCull/ModelAssets/manifest.template.json` | Stable asset-pack IDs and managed destinations checked by `ReleaseMetadataTests` |
| `RawCull/ModelAssets/Notices/<model>` | Application-side notice/provenance records and licence hashes |
| `RawCull-AI-Models/ModelAssets/Release/Models` | Reviewed runtime bundle inputs |
| `RawCull-AI-Models/ModelAssets/Release/Packaging` | Explicit `ba-package` selectors |
| Private `RELEASE_WORK_ROOT/Output` | Generated `.aar` files and generated `manifest.json`; never the canonical source tree |
| `RawCullAIModelDownloadCatalog.production` | Enabled product set, archive hashes/byte counts, release readiness, and runtime managed paths |

The packaging manifest schema uses `assetPackID`, `downloadPolicy`,
`fileSelectors`, and `platforms`. Each ready pack selects `metadata.json`,
`tokenizer`, one optimized runtime `.aimodel`, and its `Notices` directory. The
generated download manifest uses `id`, version, download size, and URL; do not
copy the packaging key name `assetPackID` into generated-manifest assertions.

## 1. Build the four canonical bundles

Follow [AI Model Download Service](../aimodeldownloads/) for the pinned source
checks, exact PhotoAIKit commands, runtime validation, and packaging layout. The
canonical release outputs are:

Before running any exporter, complete
[Prepare a clean, pinned conversion toolchain](../aimodeldownloads/#prepare-a-clean-pinned-conversion-toolchain).
Refresh host tools only before freezing the evidence workspace, then use the
reviewed exporter revision and lock unchanged for the entire run. Do not
interpret a newer package being available as permission to change a release
toolchain, and do not reuse output made by an earlier lock.

```text
CLIP-DataComp/
├── metadata.json
├── tokenizer/
└── ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel/

CLIP-OpenAI/
├── metadata.json
├── tokenizer/
└── clip-vit-base-patch32_float16_static.aimodel/

EfficientSAM/
├── metadata.json
└── efficient_sam_vitt_float16_static_q16.aimodel/

SAM3/
├── metadata.json
├── tokenizer/
└── sam3_float16.aimodel/
```

Use PhotoAIKit revision `6e3216027b267c27ccaf99d334807b18ea1aaec9`, or document
and review the exact later revision actually used. Release CLIP bundles must use
Float16, static batch dimensions, metadata version `0.4`, separate
`image_encoder` and `text_encoder` functions, and corrected bicubic
preprocessing. The checked-in blocked SAM 3 candidate uses metadata version
`0.2`, while the reviewed current exporter emits `0.3`. A future SAM 3 release
must be rebuilt, and its metadata version must be taken from that rebuilt
candidate rather than copied from this historical record.

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

EfficientSAM is exported separately with Apple's pinned `coreai-models`
EfficientSAM recipe. The changed release graph uses Float16, static batch
dimensions, 16 one-point queries, and no tokenizer. From the pinned clean
`coreai-models` checkout described in
[AI Model Download Service](../aimodeldownloads/), compile it with:

```sh
cd "$EFFICIENTSAM_COREAI_DIR"
uv lock --script models/efficient-sam/export.py
rg "$EFFICIENTSAM_IMPLEMENTATION_REVISION" models/efficient-sam/export.py.lock

TORCH_HOME="$EFFICIENTSAM_TORCH_HOME" \
uv run --locked --script models/efficient-sam/export.py \
  --model efficient_sam_vitt \
  --dtype float16 \
  --num-queries 16 \
  --num-pts 1 \
  --output-dir "$EFFICIENTSAM_EXPORT_DIR"
```

This must create
`efficient_sam_vitt_float16_static_q16/efficient_sam_vitt_float16_static_q16.aimodel`.
The query count is compiled into the static graph; renaming the old Q64 asset is
not a conversion. Do not add `--dynamic` or package an output from the older
beta converter toolchain.

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

For EfficientSAM, verify PhotoAIKit resolves the complete bundle, compiles the
portable Core AI program, and produces correctly placed masks in RawCull. Test
the Q16 4 × 4 point grid on portraits, groups, animals, sports, landscapes,
low-light scenes, off-centre subjects, and scenes with no clear subject. Record
mask quality, subject-selection success, latency, peak `phys_footprint`, wired
memory, swap growth, and errors. Compare the first inference, later inferences,
and memory after Deep Review closes. Reject the candidate if its memory remains
close to the previous Q64 baseline or pressure becomes warning/critical on a
16 GB supported Mac.
EfficientSAM is not text-guided; do not describe its target label as a language
prompt.

For SAM 3, test text prompts, mask dimensions and placement, licence acceptance,
relaunch, and removal.

## 3. Clear release blockers

Do not mark a model `.ready` because it works locally.

### DataComp CLIP

Confirm that the new archive uses the pinned DataComp checkpoint and corrected
runtime filename. Replace the existing archive checksum and byte count whenever
the bundle or packaging changes. Update its notice and provenance records; do
not reuse values from the old custom-named runtime.

The published `v2` record is 282,966,632 bytes with SHA-256
`cf433dcd199b44635a4ff0260bd8e79177e4907a4cfcb2f72043066b8cbe4ef7`.

### OpenAI CLIP

The current engineering/release record marks OpenAI CLIP ready and publishes it
in `v2`. Its pinned source revision is
`3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268`, the recorded source-weight
SHA-256 is `a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f`,
and the archive is 282,866,068 bytes with SHA-256
`e9181157c2d4012db2e6478949488f9906696a4ed78ecaa10235d9762621136c`.

Before republishing or replacing it, re-evaluate the exact trained-weight
licence basis recorded by the responsible approver; the current Hugging Face
model page does not itself provide a weight-specific licence identifier. Record
the PhotoAIKit revision, command, tokenizer checksum, runtime fingerprint,
archive checksum, byte count, complete notices, evidence date, and approver.
Published availability and a `.ready` enum value are product state, not legal
evidence.

### EfficientSAM

EfficientSAM is the segmentation model planned for RawCull 3.3.0. Before
enabling its pack:

1. verify the pinned `yformer/EfficientSAM` implementation revision and
   `merve/EfficientSAM` checkpoint revision, byte count, and SHA-256;
2. use the pinned Apple `coreai-models` converter revision and locked Python
   dependency resolution documented in the download-service page;
3. record the conversion command, exporter and lock checksums, runtime
   fingerprint, `main.mlirb` checksum, archive checksum, and byte count;
4. include the complete Apache License 2.0, applicable Apple BSD 3-Clause
   notice, and any notices required by the locked dependencies in
   `Notices/EfficientSAM`;
5. validate the Q16 runtime through PhotoAIKit and RawCull on the supported
   macOS/Xcode toolchain; and
6. publish the pack and generated manifest under a new immutable tag before
   changing the production descriptor to `.ready`.

The stable pack identity is `no.blogspot.RawCull.models.efficient-sam`, its
managed destination is `Models/EfficientSAM`, and its runtime selector is
`efficient_sam_vitt_float16_static_q16.aimodel`. It has no tokenizer directory.

### Meta SAM 3

Before enabling the SAM 3 pack:

1. preserve the accepted gated-source revision and source SHA-256 as private
   evidence;
2. confirm that an ungated GitHub release of the converted derivative complies
   with the SAM License and Meta's gated checkpoint access conditions;
3. record the PhotoAIKit revision, command, tokenizer checksum, runtime
   fingerprint, archive checksum, and byte count in the external release
   catalogue;
4. include the complete SAM License and notices in `Notices/SAM3`;
5. keep explicit in-app licence acceptance enabled.

Technical provenance does not resolve the redistribution decision. Omit SAM 3
from the public manifest until that review is complete.

## 4. Prepare release staging

The reviewed source tree may contain all four known candidates, but a generated
release work tree and manifest must contain only the ready subset and its notice
catalogues:

```text
ModelAssets/Release/
├── Models/
│   ├── CLIP-DataComp/
│   ├── CLIP-OpenAI/
│   ├── EfficientSAM/
│   └── SAM3/
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

Each packaging manifest selects only:

- the bundle's `metadata.json`;
- its `tokenizer` directory when required (CLIP and SAM 3 only);
- its optimized runtime `.aimodel` directory;
- its matching notice directory.

The DataComp selector must be:

```text
Models/CLIP-DataComp/ViT-B-32-256-datacomp_s34b_b86k_float16_static.aimodel
```

If any checked-in packaging manifest still selects
`ViT-B-32-256-open_clip_model.safetensors_float16_static.aimodel`, it is stale
and must be corrected before packaging.

## 5. Generate and record the asset-pack archives

Check the selected Xcode tool before every release:

```sh
xcrun --find ba-package
xcrun ba-package --version
xcrun ba-package help package
```

Run one package operation per ready model from the staging root. For the current
`v2` republish, package the two CLIP models only:

```sh
cd /Users/thomas/ModelAssets/Release

xcrun ba-package package Packaging/clip-datacomp.json \
  --output-path Output/clip-datacomp.aar
xcrun ba-package package Packaging/clip-openai.json \
  --output-path Output/clip-openai.aar

shasum -a 256 Output/*.aar
stat -f '%N %z bytes' Output/*.aar
```

Run the SAM 3 operation only after its redistribution review is complete and its
status changes from blocked to ready:

```sh
xcrun ba-package package Packaging/sam3.json \
  --output-path Output/sam3.aar
```

For RawCull 3.3.0, package EfficientSAM after its technical and licence gates
pass:

```sh
xcrun ba-package package Packaging/efficient-sam.json \
  --output-path Output/efficient-sam.aar
```

The `.aar` suffix here means an Apple Archive produced for Managed Background
Assets; it is not an Android library.

Do not copy old archive checksums into the application catalogue. A changed
model, metadata file, tokenizer, notice, selector, or packaging tool can change
the archive. Record the newly generated SHA-256 and exact byte count for every
pack. Keep these archive-level values in the generated download manifest,
RawCull's production download catalogue, release documentation, and GitHub
release metadata. Do not embed an archive checksum or size in a provenance file
inside that same archive; doing so creates a self-referential checksum.

## 6. Generate the download manifest

For the historical `v2` run, the operator used this private release work tree:

```text
/Users/thomas/ModelAssets/Release
```

This path is a record, not a portable prerequisite. For a new release use
`RELEASE_WORK_ROOT`. Run every `ba-package` command in chapter 6 from that
directory. Relative paths
such as `Output/clip-datacomp.aar` and `Packaging/clip-datacomp.json` are
resolved from the current directory; running the commands from
`/Users/thomas/ModelAssets` or a RawCull source checkout selects the wrong
paths.

Create a self-hosted manifest from the exact approved AAR files in
`/Users/thomas/ModelAssets/Release/Output`. The generated manifest must contain
only packs that have passed both technical and legal release gates. It may
contain any ready subset of the four packs while reviews are in progress;
RawCull must expose only the same ready set.

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

### 6.1. How to create the manifest

Create the manifest with the same Xcode installation used to package the AAR
files. First verify the working directory and inputs. These checks must list the
release packaging catalogues and the AAR files generated in chapter 5:

```sh
cd /Users/thomas/ModelAssets/Release
pwd
ls -l Packaging/*.json Output/*.aar
```

Pass only approved archives. `ba-package` matches version numbers to archive
paths by position: the first value after `--asset-pack-versions` applies to the
first AAR path, the second value to the second AAR path, and so on. Supply
exactly one version for each AAR. Version `2` is used below for the new `v2`
release; replace it with the next monotonically increasing integer for any pack
that has already used that version.

The base URL is the tag-pinned release directory, including its trailing slash:

```sh
DOWNLOAD_BASE_URL="https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/"

xcrun ba-package download-manifest create \
  Output/clip-datacomp.aar \
  --asset-pack-versions 2 \
  --macos \
  --download-base-url "$DOWNLOAD_BASE_URL" \
  --output-path Output/manifest.json
```

Generate `Output/manifest.json` with one of the commands below. Do not edit the
generated JSON to add a blocked model. If the ready set changes, regenerate the
manifest from exactly that set of AAR files.

After generation, validate the JSON, print the included IDs, and inspect every
generated pack entry before publishing:

```sh
jq empty Output/manifest.json
jq -r '.assetPacks[].id' Output/manifest.json
jq -r '.assetPacks[] | [.id, (.version | tostring), (.downloadSize | tostring), .url] | @tsv' \
  Output/manifest.json
```

The generated key is `id`, not `assetPackID`; `assetPackID` is used only in the
packaging catalogue. Verify the version, archive URL, and download size in each
entry. The Background Assets tool constructs the URL by appending the pack ID to
`DOWNLOAD_BASE_URL`. Consequently, the GitHub release asset must be named
exactly like the final URL component, for example
`no.blogspot.RawCull.models.clip-datacomp`, with no `.aar` suffix. Chapter 7
prepares those upload names. Do not hand-edit the generated JSON or URL.

### 6.2. Manifest for both CLIP models

Use this manifest after DataComp CLIP and OpenAI CLIP have both passed their
technical and legal gates, while SAM 3 remains blocked:

```sh
xcrun ba-package download-manifest create \
  Output/clip-datacomp.aar \
  Output/clip-openai.aar \
  --asset-pack-versions 2 2 \
  --macos \
  --download-base-url "$DOWNLOAD_BASE_URL" \
  --output-path Output/manifest.json
```

The result must contain exactly these asset-pack IDs:

```text
no.blogspot.RawCull.models.clip-datacomp
no.blogspot.RawCull.models.clip-openai
```

### 6.3. RawCull 3.3.0 manifest with EfficientSAM

Use this manifest for RawCull 3.3.0 after EfficientSAM and both CLIP models have
passed all release gates. SAM 3 remains omitted while its redistribution review
is blocked:

```sh
xcrun ba-package download-manifest create \
  Output/clip-datacomp.aar \
  Output/clip-openai.aar \
  Output/efficient-sam.aar \
  --asset-pack-versions \
    "$DATACOMP_PACK_VERSION" \
    "$OPENAI_PACK_VERSION" \
    "$EFFICIENTSAM_PACK_VERSION" \
  --macos \
  --download-base-url "$DOWNLOAD_BASE_URL" \
  --output-path Output/manifest.json
```

The result must contain exactly these asset-pack IDs:

```text
no.blogspot.RawCull.models.clip-datacomp
no.blogspot.RawCull.models.clip-openai
no.blogspot.RawCull.models.efficient-sam
```

### 6.4. Manifest for all four models

Use this manifest only after SAM 3 has independently passed all release gates:

```sh
xcrun ba-package download-manifest create \
  Output/clip-datacomp.aar \
  Output/clip-openai.aar \
  Output/efficient-sam.aar \
  Output/sam3.aar \
  --asset-pack-versions \
    "$DATACOMP_PACK_VERSION" \
    "$OPENAI_PACK_VERSION" \
    "$EFFICIENTSAM_PACK_VERSION" \
    "$SAM3_PACK_VERSION" \
  --macos \
  --download-base-url "$DOWNLOAD_BASE_URL" \
  --output-path Output/manifest.json
```

The result must contain exactly these asset-pack IDs:

```text
no.blogspot.RawCull.models.clip-datacomp
no.blogspot.RawCull.models.clip-openai
no.blogspot.RawCull.models.efficient-sam
no.blogspot.RawCull.models.sam3
```

## Final reproducibility and licence gate

Before creating or changing any public release, one named release owner must
sign and date a single decision record that binds all of the following:

- repository commits for RawCull, its exact `Package.resolved`, PhotoAIKit,
  and the `RawCull-AI-Models` staging source;
- OS build, Xcode/Swift, `uv`, Python dependencies, `coreai-core`,
  `coreai-models`, and `ba-package` versions;
- model repository, immutable upstream revision, exact source filename, byte
  count, and SHA-256;
- conversion command and environment, generated `metadata.json`, runtime
  `main.mlirb` hash, and directory-tree model fingerprint;
- immutable evaluation fixture digest, parity reports, RawCull integration
  report, and the release decision produced from them;
- every packaged notice/licence file and checksum, evidence date, responsible
  approver, and an explicit ready/blocked/omitted conclusion for each candidate;
- packaging-selector digest, AAR filename, byte count/SHA-256, asset-pack
  version, release tag, remote asset name, and generated-manifest digest.

The gate fails if an upstream licence, model card, access gate, or distribution
term has changed since its evidence date; if the responsible owner is missing;
if a required source or fixture digest cannot be reproduced; or if the manifest
would contain a blocked/omitted pack. Do not infer permission from the ability
to download, convert, package, or upload a model. Archive the signed record
before uploading payloads, append anonymous remote verification afterward, and
publish the manifest last.

## 7. Publish the GitHub release

Chapter 7 uses two different locations:

- local files come from `/Users/thomas/ModelAssets/Release/Output`;
- the release itself is in the GitHub repository `rsyncOSX/RawCull-AI-Models`.

`gh release view` does not read a local model or packaging catalogue. Because
the command supplies `--repo rsyncOSX/RawCull-AI-Models`, it can be run from any
directory. Change to the release staging directory anyway so the later upload
paths resolve correctly:

```sh
cd /Users/thomas/ModelAssets/Release
gh auth status
gh repo view rsyncOSX/RawCull-AI-Models --json nameWithOwner,url
```

### 7.1. Create or inspect `v2`

`gh release view` only inspects an existing release; it does not create the tag
or release. To inspect `v2`, use this one-line form, which also avoids shell
errors caused by spaces after a line-continuation backslash:

```sh
gh release view v2 --repo rsyncOSX/RawCull-AI-Models --json tagName,isDraft,isPrerelease,isImmutable
```

For the existing `v2` release, the command returns:

```json
{
  "isDraft": false,
  "isImmutable": false,
  "isPrerelease": true,
  "tagName": "v2"
}
```

`isImmutable:false` means GitHub is not currently enforcing immutable-release
protection for this repository. Normally treat a release as immutable once
clients have downloaded or consumed its manifest. The narrowly scoped republish
procedure in section 7.4 is permitted only when the release is known to be
unused and the entire affected payload-and-manifest set is replaced.

If the command fails, interpret the error before changing its arguments:

- `accepts at most 1 arg(s)` usually means a copied multiline command lost a
  continuation backslash; use the one-line command above;
- `release not found` or `Could not resolve to a Release` means `v2` does not
  exist in the repository selected by `--repo`;
- an authentication error requires `gh auth login` or a valid `GH_TOKEN`;
- `error connecting to api.github.com` is a network or proxy failure, not a
  problem with `v2`, `--repo`, or `--json`.

If GitHub reports `release not found`, create the release explicitly from the
repository's `main` branch. Choose `--prerelease` only when that is the intended
publication state:

```sh
gh release create v2 --repo rsyncOSX/RawCull-AI-Models \
  --target main \
  --title "RawCull AI models v2" \
  --prerelease \
  --notes "RawCull AI model asset packs for manifest version 2."
```

Do not run `gh release create` when `gh release view v2` already succeeds. At
verification time, `tagName` must be `v2` and `isDraft` must be `false`. A
tag-pinned URL can use a published prerelease, but record that decision.

### 7.2. Prepare the exact release asset names

The local package filenames end in `.aar`, but the generated manifest URLs do
not. Make extensionless upload copies whose basenames exactly match the `id`
values in `Output/manifest.json`:

```sh
cd /Users/thomas/ModelAssets/Release
mkdir -p Output/Upload

cp Output/clip-datacomp.aar \
  Output/Upload/no.blogspot.RawCull.models.clip-datacomp
cp Output/clip-openai.aar \
  Output/Upload/no.blogspot.RawCull.models.clip-openai
# RawCull 3.3.0, when EfficientSAM is present in Output/manifest.json:
cp Output/efficient-sam.aar \
  Output/Upload/no.blogspot.RawCull.models.efficient-sam
# Only when SAM 3 is present in Output/manifest.json:
cp Output/sam3.aar \
  Output/Upload/no.blogspot.RawCull.models.sam3
```

Before uploading, confirm that every manifest URL basename has a matching local
file and that its byte count equals `downloadSize`:

```sh
jq -r '.assetPacks[] | [.id, (.downloadSize | tostring)] | @tsv' \
  Output/manifest.json
stat -f '%N %z' Output/Upload/no.blogspot.RawCull.models.*
```

Do not upload `clip-datacomp.aar` or `clip-openai.aar` under those local names;
they would produce URLs that do not match the generated manifest.

### 7.3. Upload and verify

Upload files in this order:

1. all approved AAR payloads under their exact extensionless manifest IDs;
2. download each payload anonymously and verify its checksum and size;
3. upload `manifest.json` last;
4. download and inspect the published manifest anonymously.

For the current two-CLIP manifest, upload the extensionless assets explicitly:

```sh
gh release upload v2 \
  Output/Upload/no.blogspot.RawCull.models.clip-datacomp \
  Output/Upload/no.blogspot.RawCull.models.clip-openai \
  --repo rsyncOSX/RawCull-AI-Models
```

For RawCull 3.3.0, use its new tag and add
`Output/Upload/no.blogspot.RawCull.models.efficient-sam` to the same upload
command. Verify all three payloads anonymously before uploading that release's
generated `manifest.json`.

Do not use `--clobber` during a normal new-tag publication. Verify the remote
filenames:

```sh
gh release view v2 --repo rsyncOSX/RawCull-AI-Models \
  --json assets \
  --jq '.assets[] | [.name, (.size | tostring), .url] | @tsv'
```

Download the asset-pack URLs from the generated manifest, compare them with the
local upload copies, and only then upload the manifest:

```sh
curl --fail --location --output /tmp/no.blogspot.RawCull.models.clip-datacomp \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/no.blogspot.RawCull.models.clip-datacomp
curl --fail --location --output /tmp/no.blogspot.RawCull.models.clip-openai \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/no.blogspot.RawCull.models.clip-openai

shasum -a 256 \
  Output/Upload/no.blogspot.RawCull.models.clip-datacomp \
  /tmp/no.blogspot.RawCull.models.clip-datacomp
shasum -a 256 \
  Output/Upload/no.blogspot.RawCull.models.clip-openai \
  /tmp/no.blogspot.RawCull.models.clip-openai

gh release upload v2 Output/manifest.json \
  --repo rsyncOSX/RawCull-AI-Models
```

Each local/remote checksum pair must match. Finally, download and inspect the
published manifest anonymously:

```sh
curl --fail --location --output /tmp/rawcull-v2-manifest.json \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/manifest.json
jq empty /tmp/rawcull-v2-manifest.json
jq -r '.assetPacks[] | [.id, (.version | tostring), (.downloadSize | tostring), .url] | @tsv' \
  /tmp/rawcull-v2-manifest.json
```

If clients might already have consumed the release, never replace files under
its tag. Publish a corrective tag, for example `v2.0.1`, and update both RawCull
manifest URLs. If the release is confirmed unused, follow section 7.4 instead.

### 7.4. Historical emergency record: republishing unused `v2` assets

Use this exception only when all of the following are true:

- no user or client has downloaded or cached the model release;
- the GitHub release reports `isImmutable:false`;
- the replacement archives, manifest, RawCull catalogue, tests, notices, and
  documentation have already been updated and verified together;
- every model omitted for legal or technical reasons remains omitted. For the
  current republish, SAM 3 remains blocked and absent.

First verify the local replacement set. The manifest must contain exactly the
two ready CLIP packs, and each `downloadSize` must match its extensionless
upload file:

| Asset                                      | Expected v2 bytes | Expected SHA-256                                                   |
| ------------------------------------------ | ----------------: | ------------------------------------------------------------------ |
| `no.blogspot.RawCull.models.clip-datacomp` |       282,966,632 | `cf433dcd199b44635a4ff0260bd8e79177e4907a4cfcb2f72043066b8cbe4ef7` |
| `no.blogspot.RawCull.models.clip-openai`   |       282,866,068 | `e9181157c2d4012db2e6478949488f9906696a4ed78ecaa10235d9762621136c` |
| `manifest.json`                            |               783 | `d9c58b6ff6752f5ae4e3d692a6d6d5839edca733d7d60da6ed4f54eca336d8a6` |

```sh
cd /Users/thomas/ModelAssets/Release

jq -r '.assetPacks[] | [.id, (.version | tostring), (.downloadSize | tostring), .url] | @tsv' \
  Output/manifest.json
stat -f '%N %z' \
  Output/Upload/no.blogspot.RawCull.models.clip-datacomp \
  Output/Upload/no.blogspot.RawCull.models.clip-openai
shasum -a 256 \
  Output/Upload/no.blogspot.RawCull.models.clip-datacomp \
  Output/Upload/no.blogspot.RawCull.models.clip-openai \
  Output/manifest.json
```

Confirm that the manifest includes no SAM 3 entry:

```sh
test "$(jq -r '.assetPacks[].id' Output/manifest.json | sort | tr '\n' ' ')" = \
  "no.blogspot.RawCull.models.clip-datacomp no.blogspot.RawCull.models.clip-openai "
```

Inspect the current remote assets and record their names, sizes, and digests
before deleting anything:

```sh
gh release view v2 --repo rsyncOSX/RawCull-AI-Models \
  --json tagName,isDraft,isPrerelease,isImmutable,assets \
  --jq '{tagName,isDraft,isPrerelease,isImmutable,assets:[.assets[]|{name,size,digest,url}]}'
```

Delete the old `manifest.json` first. This prevents a client from discovering
the old manifest while its referenced payloads are being replaced. Then delete
the two old CLIP uploads by exact name. Do not delete or recreate the release or
tag itself:

```sh
gh release delete-asset v2 manifest.json \
  --repo rsyncOSX/RawCull-AI-Models --yes
gh release delete-asset v2 no.blogspot.RawCull.models.clip-datacomp \
  --repo rsyncOSX/RawCull-AI-Models --yes
gh release delete-asset v2 no.blogspot.RawCull.models.clip-openai \
  --repo rsyncOSX/RawCull-AI-Models --yes
```

Verify those three names are absent. If any deletion failed, stop and resolve it
before uploading replacements:

```sh
gh release view v2 --repo rsyncOSX/RawCull-AI-Models \
  --json assets --jq '.assets[].name'
```

Upload the two replacement payloads first. SAM 3 must not be included:

```sh
gh release upload v2 \
  Output/Upload/no.blogspot.RawCull.models.clip-datacomp \
  Output/Upload/no.blogspot.RawCull.models.clip-openai \
  --repo rsyncOSX/RawCull-AI-Models
```

Download both published payloads anonymously and compare their byte counts and
SHA-256 values with the exact local upload files. Upload `manifest.json` only
after both comparisons succeed:

```sh
curl --fail --location --output /tmp/no.blogspot.RawCull.models.clip-datacomp \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/no.blogspot.RawCull.models.clip-datacomp
curl --fail --location --output /tmp/no.blogspot.RawCull.models.clip-openai \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/no.blogspot.RawCull.models.clip-openai

cmp Output/Upload/no.blogspot.RawCull.models.clip-datacomp \
  /tmp/no.blogspot.RawCull.models.clip-datacomp
cmp Output/Upload/no.blogspot.RawCull.models.clip-openai \
  /tmp/no.blogspot.RawCull.models.clip-openai
shasum -a 256 \
  Output/Upload/no.blogspot.RawCull.models.clip-datacomp \
  /tmp/no.blogspot.RawCull.models.clip-datacomp \
  Output/Upload/no.blogspot.RawCull.models.clip-openai \
  /tmp/no.blogspot.RawCull.models.clip-openai

gh release upload v2 Output/manifest.json \
  --repo rsyncOSX/RawCull-AI-Models
```

Finally, download the new manifest anonymously and verify it byte-for-byte, then
cross-check every remote asset against its manifest entry and local catalogue:

```sh
curl --fail --location --output /tmp/rawcull-v2-manifest.json \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v2/manifest.json
cmp Output/manifest.json /tmp/rawcull-v2-manifest.json
jq -r '.assetPacks[] | [.id, (.version | tostring), (.downloadSize | tostring), .url] | @tsv' \
  /tmp/rawcull-v2-manifest.json
gh release view v2 --repo rsyncOSX/RawCull-AI-Models \
  --json assets \
  --jq '.assets[] | [.name, (.size | tostring), .digest, .url] | @tsv'
```

Do not leave `v2` without a manifest longer than necessary. If replacement or
verification fails after deletion, keep the manifest absent until the two
payloads are complete and verified; never restore a manifest that references a
missing or mismatched archive.

## 8. Update RawCull's production catalogue

The current two-CLIP `v2` release uses:

```swift
static let includeOpenAICLIP = true
static let includeDataCompCLIP = true
static let includeSAM3 = false
```

For RawCull 3.3.0, add the EfficientSAM descriptor and inclusion switch, then
enable it only after its archive is present in the new published manifest and
all release gates are complete:

```swift
static let includeOpenAICLIP = true
static let includeDataCompCLIP = true
static let includeEfficientSAM = true
static let includeSAM3 = false
```

SAM 3 remains blocked. Change its switch only after its redistribution review
and all technical release gates are complete. The eventual four-model
configuration is:

```swift
static let includeOpenAICLIP = true
static let includeDataCompCLIP = true
static let includeEfficientSAM = true
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

The EfficientSAM descriptor must use resource name `EfficientSAM`, asset-pack ID
`no.blogspot.RawCull.models.efficient-sam`, managed path `Models/EfficientSAM`,
the verified checkpoint revision, and the actual 3.3.0 archive evidence. Its
segmentation inclusion must also add `.efficientSAM` to the enabled download-ID
and segmentation-model sets.

## 9. Point both configurations to the release

Update both locations to the same exact URL:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/<3.3.0-model-release-tag>/manifest.json
```

The literal `v2` URL remains the production value until the new EfficientSAM
release is published and anonymously verified. Replace the placeholder above
with that immutable tag; do not use a floating `latest` URL.

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
command, runtime filename, model fingerprint, and review status. Keep archive
SHA-256 and byte-count values in RawCull's production download catalogue,
release documentation, generated manifest, and release-host metadata—not in the
provenance packaged inside that archive. Update `ModelAssets/README.md` to list
the exact release URL and available packs.

Tests must verify:

- the catalogue contains exactly the enabled ready models;
- every ready model has an exact archive checksum and byte count;
- bundled licence texts match their recorded checksums;
- both manifest URL locations use the same tag;
- provenance and notice records describe the generated archives;
- excluded models do not appear in settings or the production catalogue, while
  EfficientSAM appears in both for RawCull 3.3.0.

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
5. after SAM 3 becomes ready and is published, accept its licence and verify
   segmentation;
6. relaunch and verify installation and selection persistence;
7. remove each pack independently;
8. interrupt a download and verify retry;
9. verify Vision feature-print similarity remains the safe fallback when no CLIP
   model is available.

## Release checklist

- [ ] The supported model scope remains DataComp CLIP, OpenAI CLIP, and SAM 3.
- [ ] The current manifest contains exactly the ready subset (both CLIP packs
      for v2).
- [ ] DataComp uses `datacomp_s34b_b86k`, not the custom filename preset.
- [ ] Exact upstream revisions and source checksums are recorded.
- [ ] The exact PhotoAIKit revision and conversion commands are recorded.
- [ ] Runtime fingerprints match `metadata.json`.
- [ ] CLIP parity, semantic search, and image similarity are reviewed.
- [ ] SAM 3 segmentation and licence acceptance are tested.
- [ ] OpenAI's current ready/published decision has a dated, named evidence
      record covering the exact trained weights; any newly discovered blocker
      removes it from the next manifest.
- [ ] SAM 3 remains blocked and absent, or its redistribution review is
      complete.
- [ ] Only optimized runtime assets are packaged.
- [ ] Fresh archive checksums and byte counts are in RawCull, the generated
      manifest, and release records.
- [ ] Archives are uploaded and verified before `manifest.json`.
- [ ] Both RawCull manifest URLs point to the same tag-pinned manifest.
- [ ] Inclusion flags and readiness values match the published manifest.
- [ ] Focused, full, and clean-machine tests pass.
- [ ] The final reproducibility/licence decision record is signed, dated, and
      archived before the manifest is published.

## Rollback

Before an app release, restore both manifest URLs and catalogue readiness to the
last known-good release if the new model release fails. After clients have
consumed a publication, do not mutate its tag. Publish a corrected tag, verify
it, and update both RawCull URLs together. The same-tag procedure in section 7.4
is only for a confirmed-unused release.
