+++
author = "Thomas Evensen"
title = "AI Model Download Service"
linkTitle = "AI Model Downloads"
date = "2026-07-31"
description = "Architecture, storage, activation, and operation of RawCull AI model downloads using self-hosted or Apple-hosted Managed Background Assets."
tags = ["ai", "models", "downloads", "efficient-sam", "background-assets", "self-hosting", "apple-hosting"]
categories = ["technical details"]
weight = 30
+++

# AI model download service

RawCull uses Managed Background Assets for optional AI model bundles. The app
talks only to `AssetPackManager`; the downloader extension selects whether the
packs are self-hosted or Apple-hosted.

The current build is deliberately configured for self-hosting with the
non-routable placeholder:

`https://example.invalid/rawcull/models/manifest.json`

This keeps the full user interface, progress, cancellation, removal, local
licence acceptance, and model validation path in place without making a live
network request.

The app and extension share only the Managed Background Assets container
`group.no.blogspot.RawCull.model-assets`. This identifier is also recorded as
`BAAppGroupID` in the app Info.plist.

## Hosting decision

Self-hosting is the current default because RawCull's documented distribution
is a Developer ID DMG. Apple-hosted asset packs are appropriate only for an App
Store or TestFlight build. The extension already contains an Apple-hosted
`StoreDownloaderExtension` variant behind the
`RAWCULL_APPLE_HOSTED_MODEL_ASSETS` compilation condition, so the application
service and UI do not change when hosting changes.

### Planned GitHub release origin

The proposed self-hosted origin is a dedicated repository, separate from the
RawCull application releases:

```text
https://github.com/rsyncOSX/RawCull-AI-Models
```

The first immutable model-set release is planned as:

| Field | Value |
| --- | --- |
| Tag | `v1` |
| Title | `RawCull AI Models v1` |
| Download base URL | `https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/` |

This keeps model-pack versions independent of RawCull application tags such as
`v2.2.4`. Commit only the README, notices, licence texts, provenance,
checksums, and packaging documentation to the repository. Store the large
archives as GitHub Release assets, not Git objects or Git LFS objects. Each
current archive is below GitHub's 2 GiB per-release-asset limit; GitHub
documents the current limits under
[About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas).

No model archive has been uploaded. Keep the release unpublished until all
licence and provenance gates below are resolved. If a draft release is created
for preparation, do not publish it or mark it as the RawCull application's
latest release.

For an Apple-hosted configuration:

1. Upload approved packs in App Store Connect.
2. Add `RAWCULL_APPLE_HOSTED_MODEL_ASSETS` to the downloader extension.
3. Set `BAUsesAppleHosting` to `YES`.
4. Remove `BAManifestURL` from the app target.
5. Archive and test the App Store configuration.

Do not enable both hosting configurations in one product.

## Licence audit

The canonical notice catalogs are checked into RawCull under
`ModelAssets/Notices` and mirrored into the packaging staging tree under
`/Users/thomas/ModelAssets/Release/Notices`. Each pack contains a human-readable
`NOTICE.md`, complete applicable licence texts, and a machine-readable
`PROVENANCE.json` with the known upstream revisions and checksums.

- OpenCLIP/DataComp includes the OpenCLIP/DataComp MIT notice, the OpenAI CLIP
  tokenizer MIT notice, and Apple's `coreai-models` BSD 3-Clause notice.
  Release remains blocked because the exporter did not record the exact source
  checkpoint with a source-file checksum.
- OpenAI CLIP includes the OpenAI CLIP MIT notice and Apple's `coreai-models`
  BSD 3-Clause notice. Release remains blocked until the MIT terms are verified
  as applying to the exact checkpoint weights and the cached immutable
  revision and source checksum are conclusively bound to the converted output.
- EfficientSAM uses the upstream Apache License 2.0 and Apple's
  `coreai-models` BSD 3-Clause conversion code. Redistribution remains blocked
  until the exact EfficientSAM source revision, checkpoint checksum, converted
  asset fingerprint, archive checksum, and complete notices are recorded.
- Meta SAM 3 now includes the complete SAM License dated November 19, 2025 and
  Apple's `coreai-models` BSD 3-Clause notice. RawCull also bundles that verified
  SAM licence text for explicit user acceptance. Release remains blocked until
  ungated redistribution is confirmed compatible with the SAM License and
  Meta's official gated checkpoint access conditions.

The notice catalogs must remain inside their corresponding archives, but their
presence is evidence and attribution, not release approval.

The production catalogue therefore cannot start any real model download. A
descriptor becomes downloadable only after its `releaseReadiness` changes to
`ready`, its archive metadata is complete, and any required verified licence
has been accepted.

## Security and privacy boundary

Managed Background Assets owns transport and installation. RawCull never
constructs arbitrary destination paths from a server response. It asks the
framework for a known asset-pack ID and a catalogue-owned relative model path,
then passes that directory through the existing model-bundle validation before
using it.

The licence acceptance store records model ID/version, licence version and
text checksum, date, and RawCull version. A changed licence checksum invalidates
old acceptance automatically.

Model downloads send only the connection information necessary to serve the
asset. Photographs, embeddings, masks, prompts, and inference results are not
part of this flow.

## Signing and provisioning

The Managed Background Assets extension adds a second executable to RawCull.
The application, extension, and shared App Group use these identifiers:

| Purpose | Identifier |
| --- | --- |
| RawCull application | `no.blogspot.RawCull` |
| Model downloader extension | `no.blogspot.RawCull.ModelDownloader` |
| Shared Background Assets App Group | `group.no.blogspot.RawCull.model-assets` |
| Apple developer team | `93M47F4H9T` |

The extension is embedded inside RawCull; it does not need a separate
App Store Connect app or store listing.

### Developer portal setup

In
[Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/identifiers/list):

1. Under **Identifiers**, with the filter set to **App IDs**, verify that both
   `no.blogspot.RawCull` and `no.blogspot.RawCull.ModelDownloader` exist as
   explicit App IDs.
2. Change the identifier filter from **App IDs** to **App Groups** and verify
   that `group.no.blogspot.RawCull.model-assets` exists.
3. Open `no.blogspot.RawCull`, click **Edit**, enable **App Groups**, and click
   **Configure**.
4. Select `group.no.blogspot.RawCull.model-assets`, click **Continue**,
   **Assign**, and **Done**, then save if the portal presents a Save button.
5. Repeat the previous two steps for
   `no.blogspot.RawCull.ModelDownloader`.

If the downloader App ID does not exist, create it with:

- Description: `RawCull Model Downloader`
- Type: **App**
- Bundle ID type: **Explicit**
- Bundle ID: `no.blogspot.RawCull.ModelDownloader`
- Capability: **App Groups**

Apple documents the current portal workflow in
[Register an App ID](https://developer.apple.com/help/account/identifiers/register-an-app-id/),
[Register an App Group](https://developer.apple.com/help/account/identifiers/register-an-app-group/),
and
[Enable App Groups](https://developer.apple.com/help/account/identifiers/enable-app-capabilities/).

### Archive with automatic provisioning

The RawCull and RawCullModelDownloader targets use automatic signing with the
same development team. Archiving from **Product > Archive** in Xcode permits
Xcode to manage the required profiles interactively.

For a command-line archive, explicitly allow Xcode to communicate with the
developer account:

```sh
cd /Users/thomas/GitHub/RawCull/RawCull

xcodebuild \
  -project RawCull.xcodeproj \
  -scheme RawCull \
  -configuration Release \
  -destination 'generic/platform=macOS' \
  -archivePath /tmp/RawCull-with-downloader.xcarchive \
  -allowProvisioningUpdates \
  archive
```

Success ends with:

```text
** ARCHIVE SUCCEEDED **
```

`-allowProvisioningUpdates` permits automatic signing to create or refresh
profiles and other required signing records. It is unnecessary when archiving
interactively from Xcode.

An archive is not the final Developer ID release. Export the distribution-
signed application from Xcode Organizer and continue through RawCull's normal
notarization and DMG workflow. Apple recommends exporting an Xcode-built Mac
app containing nested extensions from its archive.

### Verify the signed archive

Set the archive location once:

```sh
RAWCULL_ARCHIVE=/tmp/RawCull-with-downloader.xcarchive
RAWCULL_APP="$RAWCULL_ARCHIVE/Products/Applications/RawCull.app"
RAWCULL_EXTENSION="$RAWCULL_APP/Contents/Extensions/RawCullModelDownloader.appex"
```

Confirm that the extension is embedded:

```sh
test -d "$RAWCULL_EXTENSION" && echo "Downloader extension is embedded"
```

Inspect the signed application entitlements:

```sh
codesign -d --entitlements - "$RAWCULL_APP"
```

The output must contain:

```text
93M47F4H9T.no.blogspot.RawCull
group.no.blogspot.RawCull.model-assets
```

Inspect the signed extension entitlements:

```sh
codesign -d --entitlements - "$RAWCULL_EXTENSION"
```

The output must contain:

```text
93M47F4H9T.no.blogspot.RawCull.ModelDownloader
group.no.blogspot.RawCull.model-assets
```

Verify the complete nested signature:

```sh
codesign --verify --deep --strict --verbose=4 "$RAWCULL_APP"
```

Inspect the Background Assets configuration:

```sh
/usr/libexec/PlistBuddy \
  -c 'Print :BAAppGroupID' \
  "$RAWCULL_APP/Contents/Info.plist"

/usr/libexec/PlistBuddy \
  -c 'Print :BAManifestURL' \
  "$RAWCULL_APP/Contents/Info.plist"

/usr/libexec/PlistBuddy \
  -c 'Print :EXAppExtensionAttributes:EXExtensionPointIdentifier' \
  "$RAWCULL_EXTENSION/Contents/Info.plist"
```

The current placeholder build must report:

```text
group.no.blogspot.RawCull.model-assets
https://example.invalid/rawcull/models/manifest.json
com.apple.backgroundassets.managed
```

During development Xcode may use an Xcode-managed wildcard development
profile, even when the signed code has the explicit identifiers above.
Do not use the profile's display name as the only verification. The Developer
Portal records and the signed entitlements must both match. The final
distribution export must also pass Xcode's signing validation.

### Verify the local signing identities

App IDs and App Groups are team records in the Apple Developer account. They
are not stored in Keychain and do not need to be recreated on another Mac.

Keychain stores signing certificates together with their private keys. List
the identities available to command-line signing:

```sh
security find-identity -v -p codesigning
```

For development archives, the Mac needs a valid `Apple Development` identity.
For direct distribution, it also needs access to the appropriate
`Developer ID Application` identity. App Store distribution instead uses the
relevant Apple distribution identity or Xcode's cloud-managed signing.

A certificate visible without its private key is not a usable signing
identity. In Keychain Access, a usable identity appears under **My
Certificates** and expands to show its private key.

Provisioning profiles are a separate, local cache. With current Xcode versions
they are normally under:

```text
~/Library/Developer/Xcode/UserData/Provisioning Profiles/
```

Older Xcode installations may also use:

```text
~/Library/MobileDevice/Provisioning Profiles/
```

Automatic signing downloads suitable profiles when the project is built or
archived with permission to update provisioning. Xcode-managed development
and distribution profiles may not appear in the Profiles list on the
Developer website.

## Set up a second Mac

Do not recreate the RawCull App IDs or App Group. They already belong to team
`93M47F4H9T` and become visible on any Mac after signing in to the same Apple
Developer account.

On the second Mac:

1. Install the same compatible Xcode toolchain.
2. Open **Xcode > Settings > Accounts** and sign in with the Apple Account
   belonging to team `93M47F4H9T`.
3. Select the team and open **Manage Certificates**.
4. For local development, let Xcode create or download an Apple Development
   identity for that Mac if one is not already usable.
5. Clone or update the RawCull repository. Both targets already select the
   correct team and automatic signing.
6. Run the command-line archive above with a new `-archivePath`, or use
   **Product > Archive**.
7. Run all checks in **Verify the signed archive**.

Development certificates belong to individual developers, and Apple permits
each Mac to have an appropriate development identity. It is usually cleaner
to let Xcode manage development identities separately on each Mac. Apple
currently limits an individual developer to two Mac development certificates,
so two Macs can normally have one each. Do not revoke a certificate still in
use by the other Mac merely to make Xcode issue another one.

Distribution identities require more care. If Xcode's cloud-managed
distribution signing is available to the account, use it. If the second Mac
must use an existing locally managed Developer ID or distribution identity,
transfer the complete certificate and private key from the first Mac:

1. On the first Mac, open **Xcode > Settings > Accounts**.
2. Select the Apple Account and team, then click **Manage Certificates**.
3. Control-click the required distribution certificate and choose
   **Export Certificate**.
4. Save it as a password-protected `.p12` file using a strong, unique
   password.
5. Transfer the `.p12` through a secure channel. Communicate its password
   separately.
6. On the second Mac, double-click the `.p12` and enter its password. Keychain
   Access imports the certificate and private key into the login keychain.
7. Run `security find-identity -v -p codesigning` and verify that the imported
   identity is valid.

Anyone possessing the `.p12` and its password can sign software as this
developer team. Never commit `.p12`, `.cer`, private-key, or provisioning
profile files to the repository, and do not leave unencrypted copies in shared
storage.

Apple's reference for this process is
[Synchronizing code signing identities with your developer account](https://developer.apple.com/documentation/xcode/sharing-your-teams-signing-certificates).
For automatic profile refresh behavior, see
[Edit, download, or delete provisioning profiles](https://developer.apple.com/help/account/provisioning-profiles/edit-download-or-delete-profiles/).

## Runtime architecture and download flow

The implementation separates user interface, policy, transport, and runtime
validation:

| Layer | Responsibility |
| --- | --- |
| `AIModelDownloadsView` | Displays catalogue details, licence review, state, progress, download, cancellation, retry, and removal. |
| `RawCullAISettingsModel` | Owns one download task per model and publishes main-actor UI state. |
| `RawCullAIModelDownloadCoordinator` | Refuses blocked releases and enforces explicit licence acceptance. |
| `RawCullManagedBackgroundAssetsModelDownloadService` | Uses `AssetPackManager` for both hosting modes. |
| `RawCullModelDownloader` | Compiles as the self-hosted or Apple-hosted downloader extension. |
| `RawCullAIIntegration` | Validates installed bundles and creates the CLIP, EfficientSAM, or SAM 3 runtime provider. |

A refresh first checks each catalogue descriptor's `releaseReadiness`. A
blocked model becomes unavailable before any manifest request. For an approved
model, RawCull asks whether its pack is already local. Otherwise it loads the
framework manifest and requires the exact catalogue asset-pack ID.

A permitted download subscribes to `statusUpdates`, then calls
`ensureLocalAvailability(of:requireLatestVersion: true)`. After installation,
RawCull resolves the model's known logical path, enters the validating state,
and gives the URL to the appropriate model resource manager. Only a bundle that
passes PhotoAIKit validation becomes available to similarity, semantic search,
or segmentation. A completed transfer is therefore not by itself successful AI
activation. Vision feature prints remain the safe CLIP similarity fallback
until a CLIP provider is ready.

Cancellation stops RawCull's task and progress listener. The next snapshot asks
Managed Background Assets for the authoritative state. Removal uses
`AssetPackManager.remove`; RawCull never deletes a framework-returned path
directly.

## Asset-pack contents and storage

The template defines these logical packs:

| Model | Asset-pack ID | Logical model directory |
| --- | --- | --- |
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` |
| OpenAI CLIP | `no.blogspot.RawCull.models.clip-openai` | `Models/CLIP-OpenAI` |
| EfficientSAM | `no.blogspot.RawCull.models.efficient-sam` | `Models/EfficientSAM` |
| Meta SAM 3 | `no.blogspot.RawCull.models.sam3` | `Models/SAM3` |

`ModelAssets/manifest.template.json` is a developer input, not the deployable
manifest. Release-time Managed Background Assets tools generate the archives
and production manifest. Each pack should include the converted model plus its
applicable licence text, immutable upstream revision, source and archive
checksums, and conversion metadata.

The checked-in `ModelAssets/Notices` directory is the canonical source for the
three existing pack-specific notice catalogs. Add and review an EfficientSAM
notice catalog before packaging that fourth model. Copy the matching catalogs
into the staging tree before packaging. The release manifests use explicit selectors so that the
runtime model and required resources are included while `_source.aimodel`,
compiled intermediates, and unrelated files are excluded.

A self-hosted HTTPS origin stores the generated archives and generated
manifest. Upload and verify immutable, versioned archives first and publish the
manifest last, so clients cannot discover an incomplete pack. Retain an archive
while a supported manifest or app can refer to it. Apple-hosted builds upload
the equivalent packs through App Store Connect; Apple owns external storage and
delivery.

On the Mac, the framework owns managed installation inside the shared
`group.no.blogspot.RawCull.model-assets` container. RawCull does not depend on
its physical path. It resolves only a catalogue-owned path such as:

```swift
AssetPackManager.shared.url(for: FilePath("Models/CLIP-OpenAI"))
```

The returned URL is authoritative and is checked before validation. Do not
hard-code its parent, move its contents, or scan the App Group container.
Manually installed models under
`~/Library/Application Support/RawCull/Models/` are separate. The Remove
action affects only the managed pack.

Licence acceptance is also separate from the model and is atomically stored at
`~/Library/Application Support/RawCull/ModelLicenceAcceptances.json`.
Acceptance is bound to model version, licence version, verified licence-text
SHA-256, date, and RawCull version. Changing the checksum invalidates it.

## Activation gates

A live service requires three independent gates:

1. The catalogue descriptor must be `.ready`, with all licence, provenance,
   checksum, and redistribution evidence complete.
2. The Swift service source must be a real `.selfHosted(manifestURL:)` HTTPS
   URL or `.appleHosted`.
3. The app plist and downloader extension must select that same hosting mode.

The current `RawCullAIModelDownloadCoordinator.live(paths:)` passes the
in-code `.invalid` placeholder. Editing only `BAManifestURL` therefore does
not activate the current build; both values must be changed consistently.
Likewise, an Apple-hosted build must construct the service with
`.appleHosted` in addition to defining
`RAWCULL_APPLE_HOSTED_MODEL_ASSETS`, setting `BAUsesAppleHosting` to
`YES`, and removing `BAManifestURL`.

Do not mark a descriptor ready merely to test transport. Ready is an
application-level statement that the exact pack is approved for redistribution.

## DataComp CLIP model for release

RawCull uses the OpenCLIP `ViT-B-32-256` architecture with the
`datacomp_s34b_b86k` weights. The release input must be the following exact
file, not a fresh resolution of the OpenCLIP pretrained alias:

| Field | Required value |
| --- | --- |
| Repository | `laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K` |
| Revision | `4afec35ffe57a943d569ff7ee888061830164da8` |
| Source file | `open_clip_model.safetensors` |
| Byte size | `605189364` |
| SHA-256 | `92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27` |
| Architecture | `ViT-B-32-256` |
| Export precision and shapes | Float16, static batch dimensions |

The repository and revision above are already referenced by RawCull, but the
existing converted asset was not cryptographically bound to that source file.
The release model must therefore be a new conversion. Do not copy the source
hash into the old provenance record and treat the old `.aimodel` as verified.

Hugging Face documents `hf download`, `--revision`, and `--local-dir` in its
[official CLI guide](https://huggingface.co/docs/huggingface_hub/en/guides/cli).
Use a full commit hash and a new evidence directory so a cached or floating
revision cannot silently become the release input.

### Create a clean evidence workspace

The following variables keep the upstream download, converter checkout, and
generated output separate. Use a new directory if an earlier attempt already
exists; do not overwrite evidence from a previous conversion.

```sh
DATACOMP_REPOSITORY='laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K'
DATACOMP_REVISION='4afec35ffe57a943d569ff7ee888061830164da8'
DATACOMP_SOURCE_FILENAME='open_clip_model.safetensors'
DATACOMP_EXPECTED_BYTES='605189364'
DATACOMP_EXPECTED_SHA256='92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27'

DATACOMP_EVIDENCE_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/CLIP-DataComp/$DATACOMP_REVISION"
DATACOMP_SOURCE_DIR="$DATACOMP_EVIDENCE_ROOT/source"
DATACOMP_EXPORT_DIR="$DATACOMP_EVIDENCE_ROOT/export"
DATACOMP_PHOTOAIKIT_DIR="$DATACOMP_EVIDENCE_ROOT/PhotoAIKit"

mkdir -p "$DATACOMP_SOURCE_DIR" "$DATACOMP_EXPORT_DIR"
```

The converter itself is part of the evidence chain. RawCull currently resolves
PhotoAIKit revision
`2cb07d604beee3549df4d361a5d48b3e9506fb87`. Create a detached, clean checkout
of that revision rather than changing a development checkout in place:

```sh
DATACOMP_PHOTOAIKIT_REVISION='2cb07d604beee3549df4d361a5d48b3e9506fb87'

git clone https://github.com/rsyncOSX/PhotoAIKit.git \
  "$DATACOMP_PHOTOAIKIT_DIR"
git -C "$DATACOMP_PHOTOAIKIT_DIR" switch --detach \
  "$DATACOMP_PHOTOAIKIT_REVISION"

test "$(git -C "$DATACOMP_PHOTOAIKIT_DIR" rev-parse HEAD)" = \
  "$DATACOMP_PHOTOAIKIT_REVISION"
test -z "$(git -C "$DATACOMP_PHOTOAIKIT_DIR" status --porcelain)"
```

If RawCull later resolves a different PhotoAIKit revision, review the exporter
changes, replace the revision in this procedure, and record the new value. The
release record must identify the revision that was actually executed.

### Download the pinned source model

Download the weight file and the accompanying model information directly into
the evidence directory:

```sh
hf download "$DATACOMP_REPOSITORY" \
  "$DATACOMP_SOURCE_FILENAME" \
  open_clip_config.json \
  README.md \
  --revision "$DATACOMP_REVISION" \
  --local-dir "$DATACOMP_SOURCE_DIR"
```

The DataComp repository is public and does not require a token. Preserve the
download output and the `.cache/huggingface` metadata created under the local
directory as private release evidence. Also save a dated copy of the repository
API response and model page showing the revision and MIT designation.

### Verify the source before conversion

Print the downloaded file's checksum and size:

```sh
shasum -a 256 "$DATACOMP_SOURCE_DIR/$DATACOMP_SOURCE_FILENAME"
stat -f '%z bytes %N' "$DATACOMP_SOURCE_DIR/$DATACOMP_SOURCE_FILENAME"
```

The output must contain exactly:

```text
92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27
605189364 bytes
```

Make the verification fail closed before continuing:

```sh
test "$(shasum -a 256 "$DATACOMP_SOURCE_DIR/$DATACOMP_SOURCE_FILENAME" | cut -d ' ' -f 1)" = \
  "$DATACOMP_EXPECTED_SHA256"
test "$(stat -f '%z' "$DATACOMP_SOURCE_DIR/$DATACOMP_SOURCE_FILENAME")" = \
  "$DATACOMP_EXPECTED_BYTES"
```

If either command fails, stop. Do not convert, rename, repair, or substitute the
file. Investigate the download and upstream revision first.

### Export from the verified local Safetensors file

`PhotoAIKit/Tools/export_clip.py` normally accepts the
`datacomp_s34b_b86k` pretrained tag. Using that tag for this conversion would
allow OpenCLIP to resolve the checkpoint again and would repeat the provenance
problem. OpenCLIP 3.2.0 also accepts a local checkpoint path through the same
`pretrained` parameter. Run the tool while the verified file is the current
directory and pass its local filename explicitly:

```sh
cd "$DATACOMP_SOURCE_DIR"

uv run --script "$DATACOMP_PHOTOAIKIT_DIR/Tools/export_clip.py" \
  --model openclip-datacomp \
  --architecture ViT-B-32-256 \
  --pretrained open_clip_model.safetensors \
  --output-dir "$DATACOMP_EXPORT_DIR" \
  --bundle-name CLIP-DataComp \
  --dtype float16
```

Do not add `--dynamic`; RawCull's release model uses static batch dimensions.
Do not add `--overwrite` to the evidence run. If the destination exists, keep
it as evidence and start a new attempt in a new directory.

The script's PEP 723 metadata pins the Python conversion dependencies,
including `coreai-core`, `coreai-torch`, OpenCLIP, PyTorch, torchvision, and
Transformers. Preserve the complete terminal log and record at least:

```sh
uv --version
python3 --version
sw_vers
xcodebuild -version
git -C "$DATACOMP_PHOTOAIKIT_DIR" rev-parse HEAD
git -C "$DATACOMP_PHOTOAIKIT_DIR" show HEAD:Package.swift
```

The exporter verifies tokenizer parity, creates independent `image_encoder`
and `text_encoder` Core AI functions, optimizes the runtime asset, saves the
CLIP tokenizer, and writes a fingerprint for the runtime asset into
`metadata.json`.

Because the verified local filename is supplied through `--pretrained`, the
current exporter produces this runtime directory:

```text
CLIP-DataComp/
├── metadata.json
├── tokenizer/
├── ViT-B-32-256-open_clip_model.safetensors_float16_static.aimodel/
└── ViT-B-32-256-open_clip_model.safetensors_float16_static_source.aimodel/
```

The `_source.aimodel` directory is a conversion intermediate. Preserve it in
private evidence, but do not include it in the downloadable asset pack. Do not
rename the runtime directory without also regenerating `metadata.json` and its
asset reference. RawCull resolves the runtime filename from `assets.main`; it
does not require the previous alias-derived filename.

### Inspect and fingerprint the generated bundle

Set the generated paths and confirm the required files exist:

```sh
DATACOMP_BUNDLE="$DATACOMP_EXPORT_DIR/CLIP-DataComp"
DATACOMP_RUNTIME_ASSET="$DATACOMP_BUNDLE/ViT-B-32-256-open_clip_model.safetensors_float16_static.aimodel"

test -f "$DATACOMP_BUNDLE/metadata.json"
test -f "$DATACOMP_BUNDLE/tokenizer/tokenizer.json"
test -d "$DATACOMP_RUNTIME_ASSET"

plutil -extract architecture raw -o - "$DATACOMP_BUNDLE/metadata.json"
plutil -extract assets.main raw -o - "$DATACOMP_BUNDLE/metadata.json"
plutil -extract asset_fingerprints.main.value raw -o - \
  "$DATACOMP_BUNDLE/metadata.json"

python3 "$DATACOMP_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$DATACOMP_RUNTIME_ASSET"
```

The architecture must be `ViT-B-32-256`, `assets.main` must name the runtime
asset above, and the fingerprint printed by `model_fingerprint.py` must equal
`asset_fingerprints.main.value` in `metadata.json`.

Verify the tokenizer produced by the exporter:

```sh
shasum -a 256 "$DATACOMP_BUNDLE/tokenizer/tokenizer.json"
```

The currently audited tokenizer SHA-256 is
`6d9109cc838977f3ca94a379eec36aecc7c807e1785cd729660ca2fc0171fb35`.
If the new export differs, stop and audit the tokenizer source and exporter
behavior instead of silently replacing the recorded checksum.

Record a fresh directory fingerprint and locate and hash the runtime
`main.mlirb` file. These are new conversion outputs and are not expected to
match the hashes of the previous unverified conversion:

```sh
python3 "$DATACOMP_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$DATACOMP_RUNTIME_ASSET"
find "$DATACOMP_RUNTIME_ASSET" -type f -name main.mlirb \
  -exec shasum -a 256 {} \;
```

### Validate the bundle with PhotoAIKit and RawCull

First run the tests for the exact PhotoAIKit checkout used by the exporter:

```sh
swift test --package-path "$DATACOMP_PHOTOAIKIT_DIR"
```

These tests verify the package contracts but do not replace validation of the
generated bundle. For an end-to-end check, install a copy of the complete
`CLIP-DataComp` directory at the DataComp path displayed by
**RawCull > Settings > AI**. A non-sandboxed development build normally uses:

```text
/Users/thomas/Library/Application Support/RawCull/Models/CLIP-DataComp/
```

A sandboxed build normally uses:

```text
/Users/thomas/Library/Containers/no.blogspot.RawCull/Data/Library/Application Support/RawCull/Models/CLIP-DataComp/
```

Use an empty destination. Move any previous test model to a separately named
backup directory; do not merge old and new bundle contents. Launch RawCull,
open **Settings > AI**, and choose **Check Again**. The DataComp model must
become available without a checksum or metadata error. Select DataComp, enable
CLIP similarity, and smoke-test both image similarity and text-to-image
semantic search. The first load may take longer while macOS specializes the
portable Core AI asset for that Mac.

PhotoAIKit's `ModelBundleResolver` verifies `metadata.json`, the selected asset,
the required tokenizer, and the asset fingerprint. `CoreAICLIPProvider` then
validates the runtime configuration and the normalized embedding outputs. A
successful export command alone is not sufficient release validation.

### Move the approved candidate into release staging

After validation, copy the complete generated bundle—not the manually
installed test copy—into:

```text
/Users/thomas/ModelAssets/Release/Models/CLIP-DataComp/
```

Update all release records to describe the new candidate accurately:

1. In `ModelAssets/Notices/CLIP-DataComp/PROVENANCE.json`, record the upstream
   repository, revision, source filename, `605189364` byte size, source
   SHA-256, PhotoAIKit commit, dependency versions, conversion command,
   tokenizer checksum, runtime asset filename, asset fingerprint, and
   `main.mlirb` checksum.
2. Update `NOTICE.md` if it names the old runtime asset. Keep the complete MIT,
   tokenizer, and Apple conversion notices with the pack.
3. Change `Packaging/clip-datacomp.json` to select `metadata.json`, `tokenizer`,
   the new runtime `.aimodel`, and `Notices/CLIP-DataComp`. Do not select the
   bundle root or `_source.aimodel`.
4. Rebuild and inspect `clip-datacomp.aar`, then record its new byte size and
   SHA-256 in the provenance record and RawCull catalogue.
5. Do not reuse the previous runtime, AAR, or manifest hashes. Changing the
   model fingerprint also deliberately invalidates incompatible cached CLIP
   embeddings.
6. Change the production descriptor to `ready` only after the separate licence
   decision is recorded and every provenance, validation, notice, archive, and
   download check has passed.

Repeat the same provenance-controlled conversion for SAM 3 before using the
shared packaging procedure below.

## Meta SAM 3 model for release

RawCull uses Meta's `facebook/sam3` image-segmentation checkpoint through
PhotoAIKit's Core AI SAM 3 backend. The release input must be the following
exact Hugging Face snapshot and weight file, not a fresh resolution of the
repository's `main` revision:

| Field | Required value |
| --- | --- |
| Repository | `facebook/sam3` |
| Revision | `3c879f39826c281e95690f02c7821c4de09afae7` |
| Source file | `model.safetensors` |
| Byte size | `3439938512` |
| SHA-256 | `6d06f0a5f84e435071fe6603e61d0b4cc7b40e0d39d487cfd4d67d8cc11cc14a` |
| Export task | Promptable image segmentation |
| Export precision and reference image | Float16, static batch, `1008 x 1008` pixels |

The existing converted asset was created from a local Hugging Face cache at
this revision, but the exporter did not record or cryptographically bind that
snapshot to the converted output. Its old provenance record deliberately has
`source_revision_recorded_by_exporter` set to `null`. The release model must
therefore be a new conversion. Do not copy the cached weight hash into the old
provenance record and treat the old `sam3_float16.aimodel` as verified.

The pinned source is visible in the
[SAM 3 model tree](https://huggingface.co/facebook/sam3/tree/3c879f39826c281e95690f02c7821c4de09afae7).
Unlike DataComp, this repository is gated. Download access requires a signed-in
Hugging Face account whose contact-sharing request has been accepted. That
access is conversion evidence, not permission to publish an ungated mirror.
The separate redistribution decision described under **Licence audit** remains
mandatory even after the technical procedure below succeeds.

### Create a clean SAM 3 evidence workspace

Use a new evidence directory so that the gated source snapshot, converter
checkout, dependency record, and generated output stay separate from the old
unverified conversion:

```sh
SAM3_REPOSITORY='facebook/sam3'
SAM3_REVISION='3c879f39826c281e95690f02c7821c4de09afae7'
SAM3_SOURCE_FILENAME='model.safetensors'
SAM3_EXPECTED_BYTES='3439938512'
SAM3_EXPECTED_SHA256='6d06f0a5f84e435071fe6603e61d0b4cc7b40e0d39d487cfd4d67d8cc11cc14a'
SAM3_LICENSE_SHA256='b08db9d32c687054e99cbd41eb1dad19c76936dfb9e2b58e186a01204d8be9ab'

SAM3_EVIDENCE_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/SAM3/$SAM3_REVISION"
SAM3_SOURCE_ROOT="$SAM3_EVIDENCE_ROOT/source"
SAM3_SOURCE_DIR="$SAM3_SOURCE_ROOT/facebook/sam3"
SAM3_EXPORT_DIR="$SAM3_EVIDENCE_ROOT/export"
SAM3_PHOTOAIKIT_DIR="$SAM3_EVIDENCE_ROOT/PhotoAIKit"

mkdir -p "$SAM3_SOURCE_DIR" "$SAM3_EXPORT_DIR"
```

The nested `source/facebook/sam3` path is intentional. The pinned PhotoAIKit
exporter accepts only the model name `facebook/sam3`. When the export runs from
`$SAM3_SOURCE_ROOT`, Transformers interprets that name as this local directory
instead of contacting the remote repository.

Use the same detached, clean PhotoAIKit revision as RawCull:

```sh
SAM3_PHOTOAIKIT_REVISION='2cb07d604beee3549df4d361a5d48b3e9506fb87'

git clone https://github.com/rsyncOSX/PhotoAIKit.git \
  "$SAM3_PHOTOAIKIT_DIR"
git -C "$SAM3_PHOTOAIKIT_DIR" switch --detach \
  "$SAM3_PHOTOAIKIT_REVISION"

test "$(git -C "$SAM3_PHOTOAIKIT_DIR" rev-parse HEAD)" = \
  "$SAM3_PHOTOAIKIT_REVISION"
test -z "$(git -C "$SAM3_PHOTOAIKIT_DIR" status --porcelain)"
```

If RawCull later resolves a different PhotoAIKit revision, audit changes to
`Tools/export_sam3.py`, update this procedure, and record the revision that was
actually executed.

### Confirm gated access without exposing credentials

Open the official [SAM 3 model page](https://huggingface.co/facebook/sam3),
review the access conditions and the
[pinned SAM License](https://huggingface.co/facebook/sam3/blob/3c879f39826c281e95690f02c7821c4de09afae7/LICENSE),
and complete the repository's access flow. Then confirm that the CLI is logged
in:

```sh
hf auth whoami
```

If needed, use `hf auth login` and enter the token only at its protected
prompt. Never place a Hugging Face token in this document, a shell variable,
the terminal transcript, provenance, or the downloadable pack. Keep the
account and dated access evidence private; it can contain personal information.

### Download the pinned source snapshot

Download only the Safetensors checkpoint and the configuration, processor,
tokenizer, licence, and model-card files required for the conversion record.
The exporter does not use the repository's separate `sam3.pt` file:

```sh
hf download "$SAM3_REPOSITORY" \
  "$SAM3_SOURCE_FILENAME" \
  config.json \
  processor_config.json \
  tokenizer.json \
  tokenizer_config.json \
  special_tokens_map.json \
  merges.txt \
  vocab.json \
  LICENSE \
  README.md \
  --revision "$SAM3_REVISION" \
  --local-dir "$SAM3_SOURCE_DIR"
```

Preserve the command output and the local directory's `.cache/huggingface`
metadata as private release evidence. Also preserve a dated copy of the gated
model page and access conditions. The downloadable model archive must contain
the verified SAM License from RawCull's notice catalog, not Hugging Face cache
metadata or access credentials.

### Verify the SAM 3 source before conversion

Print the checkpoint checksum and size:

```sh
shasum -a 256 "$SAM3_SOURCE_DIR/$SAM3_SOURCE_FILENAME"
stat -f '%z bytes %N' "$SAM3_SOURCE_DIR/$SAM3_SOURCE_FILENAME"
```

The output must contain exactly:

```text
6d06f0a5f84e435071fe6603e61d0b4cc7b40e0d39d487cfd4d67d8cc11cc14a
3439938512 bytes
```

Make the checkpoint and licence verification fail closed:

```sh
test "$(shasum -a 256 "$SAM3_SOURCE_DIR/$SAM3_SOURCE_FILENAME" | cut -d ' ' -f 1)" = \
  "$SAM3_EXPECTED_SHA256"
test "$(stat -f '%z' "$SAM3_SOURCE_DIR/$SAM3_SOURCE_FILENAME")" = \
  "$SAM3_EXPECTED_BYTES"
test "$(shasum -a 256 "$SAM3_SOURCE_DIR/LICENSE" | cut -d ' ' -f 1)" = \
  "$SAM3_LICENSE_SHA256"
```

The pinned `LICENSE` must match the complete
`ModelAssets/Notices/SAM3/SAM3-SAM-License-2025-11-19.txt` bundled with RawCull.
Create a checksum manifest for every explicitly downloaded file:

```sh
(
  cd "$SAM3_SOURCE_DIR"
  shasum -a 256 \
    model.safetensors \
    config.json \
    processor_config.json \
    tokenizer.json \
    tokenizer_config.json \
    special_tokens_map.json \
    merges.txt \
    vocab.json \
    LICENSE \
    README.md
) | tee "$SAM3_EVIDENCE_ROOT/source-sha256.txt"
```

If any required file is missing or either fixed checksum differs, stop. Do not
convert a substitute file or retrieve `main` without the full revision.

### Export only from the verified local snapshot

`PhotoAIKit/Tools/export_sam3.py` calls Transformers three times: for the model,
the processor/reference inputs, and the saved tokenizer. All three must resolve
the same local snapshot. Change to the source root so the literal
`facebook/sam3` argument names the verified local directory, then force the
Hugging Face and Transformers clients offline:

```sh
cd "$SAM3_SOURCE_ROOT"

HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
uv run --script "$SAM3_PHOTOAIKIT_DIR/Tools/export_sam3.py" \
  --model facebook/sam3 \
  --output-dir "$SAM3_EXPORT_DIR" \
  --bundle-name SAM3 \
  --dtype float16
```

Do not run this command from another current directory. Without the local
`facebook/sam3` path, the same argument denotes the remote repository alias.
Offline mode makes such a mistake fail instead of silently resolving a newer
checkpoint.

Do not add `--overwrite` to an evidence run. A complete SAM 3 conversion is
resource intensive; if it fails after creating output, retain the attempt and
start again in a new evidence directory.

The exporter's PEP 723 metadata fixes `coreai-core` and `coreai-torch` and
constrains the compatible Transformers and tokenizer versions. Record the
complete dependency resolution in addition to the terminal log:

```sh
uv export \
  --script "$SAM3_PHOTOAIKIT_DIR/Tools/export_sam3.py" \
  --format requirements.txt \
  --no-hashes \
  --output-file "$SAM3_EVIDENCE_ROOT/python-requirements.txt"

uv --version
python3 --version
sw_vers
xcodebuild -version
git -C "$SAM3_PHOTOAIKIT_DIR" rev-parse HEAD
git -C "$SAM3_PHOTOAIKIT_DIR" show HEAD:Package.swift
```

The exporter loads `Sam3Model` at Float16, uses a static one-image reference
input at `1008 x 1008`, exports the five SAM 3 outputs, converts and optimizes
the Core AI program, saves the tokenizer, and fingerprints the runtime asset in
`metadata.json`.

The expected generated directory is:

```text
SAM3/
├── metadata.json
├── tokenizer/
├── sam3_float16.aimodel/
└── sam3_float16_source.aimodel/
```

The `_source.aimodel` directory is a conversion intermediate. Preserve it in
private evidence, but do not include it in the downloadable asset pack. Do not
rename the runtime directory without regenerating `metadata.json` and its
fingerprint.

### Inspect and fingerprint the generated SAM 3 bundle

Set the generated paths and confirm the required files exist:

```sh
SAM3_BUNDLE="$SAM3_EXPORT_DIR/SAM3"
SAM3_RUNTIME_ASSET="$SAM3_BUNDLE/sam3_float16.aimodel"

test -f "$SAM3_BUNDLE/metadata.json"
test -f "$SAM3_BUNDLE/tokenizer/tokenizer.json"
test -f "$SAM3_BUNDLE/tokenizer/tokenizer_config.json"
test -d "$SAM3_RUNTIME_ASSET"

plutil -extract metadata_version raw -o - "$SAM3_BUNDLE/metadata.json"
plutil -extract kind raw -o - "$SAM3_BUNDLE/metadata.json"
plutil -extract family raw -o - "$SAM3_BUNDLE/metadata.json"
plutil -extract source_model raw -o - "$SAM3_BUNDLE/metadata.json"
plutil -extract preprocessing_version raw -o - "$SAM3_BUNDLE/metadata.json"
plutil -extract configuration_version raw -o - "$SAM3_BUNDLE/metadata.json"
plutil -extract assets.main raw -o - "$SAM3_BUNDLE/metadata.json"
plutil -extract asset_fingerprints.main.value raw -o - \
  "$SAM3_BUNDLE/metadata.json"

python3 "$SAM3_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$SAM3_RUNTIME_ASSET"
```

The fields must report metadata version `0.3`, kind `segmenter`, family `sam3`,
source model `facebook/sam3`, preprocessing
`sam3-bounded-image-v1`, configuration `coreai-sam3-mask-v1`, and main asset
`sam3_float16.aimodel`. The fingerprint printed by
`model_fingerprint.py` must equal `asset_fingerprints.main.value`.

Verify the exported tokenizer:

```sh
shasum -a 256 "$SAM3_BUNDLE/tokenizer/tokenizer.json"
```

The tokenizer SHA-256 for the pinned snapshot is
`6d9109cc838977f3ca94a379eec36aecc7c807e1785cd729660ca2fc0171fb35`.
If it differs, stop and audit the snapshot, dependency resolution, and exporter
behavior.

Record the new runtime fingerprint and `main.mlirb` checksum:

```sh
python3 "$SAM3_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$SAM3_RUNTIME_ASSET"
find "$SAM3_RUNTIME_ASSET" -type f -name main.mlirb \
  -exec shasum -a 256 {} \;
```

These are fresh conversion outputs and are not required to equal the old
unverified runtime fingerprint or the old `main.mlirb` SHA-256
`43a9b88e40d193f5a6608a7fee536a78f4ba4ec5d95f1eb24db03031630f0a31`.

### Validate SAM 3 with PhotoAIKit and RawCull

Run the tests from the exact PhotoAIKit checkout used by the exporter:

```sh
swift test --package-path "$SAM3_PHOTOAIKIT_DIR"
```

The package tests validate the resolver, fingerprint, tokenizer layout, and
SAM 3 runtime contracts, but do not execute the newly generated model against a
RawCull image. Install a copy of the complete `SAM3` directory at the SAM 3
path displayed by **RawCull > Settings > AI**. A non-sandboxed development
build normally uses:

```text
/Users/thomas/Library/Application Support/RawCull/Models/SAM3/
```

A sandboxed build normally uses:

```text
/Users/thomas/Library/Containers/no.blogspot.RawCull/Data/Library/Application Support/RawCull/Models/SAM3/
```

Use an empty destination. Move any previous test model to a separately named
backup directory; do not merge old and new bundle contents. Launch RawCull,
open **Settings > AI**, and choose **Check Again**. The SAM 3 model and
in-process review capability must become available without a metadata,
tokenizer, or fingerprint error.

Analyze a representative catalog into burst groups, choose **Deep Review** on
a burst, select the review target, and run the review. Confirm that RawCull
creates subject masks, completes the subject-detail analysis, and presents a
recommendation without a model-load, prompt, or mask-decoding error. Inspect
several masks visually, including a scene with no clear subject. The first load
may take longer while macOS specializes the portable Core AI asset for that
Mac.

PhotoAIKit's `ModelBundleResolver` verifies `metadata.json`, the selected
asset, required tokenizer, and runtime fingerprint. `CoreAISAM3Provider` then
loads the tokenizer and Core AI segmentation engine and validates the returned
mask tensors. A successful Python export alone is not sufficient release
validation.

### Move the approved SAM 3 candidate into release staging

After validation, copy the complete generated bundle—not the manually
installed test copy—into:

```text
/Users/thomas/ModelAssets/Release/Models/SAM3/
```

Update the release records for the new candidate:

1. In `ModelAssets/Notices/SAM3/PROVENANCE.json`, record the upstream
   repository, revision, source filename, `3439938512` byte size, source
   SHA-256, licence SHA-256, PhotoAIKit commit, resolved dependency versions,
   conversion command, tokenizer checksum, runtime asset filename, asset
   fingerprint, and `main.mlirb` checksum. Remove the old statement that the
   exporter output is not bound to a source revision only after this evidence
   has been reviewed.
2. Keep `NOTICE.md`, the complete SAM License, and Apple's conversion notice
   with the pack. Update `NOTICE.md` only if the runtime asset name changes.
3. Keep `Packaging/sam3.json` restricted to `metadata.json`, `tokenizer`, the
   new runtime `sam3_float16.aimodel`, and `Notices/SAM3`. Do not select the
   bundle root or `_source.aimodel`.
4. Rebuild and inspect `sam3.aar`, then record its new byte size and SHA-256 in
   the provenance record and RawCull catalogue.
5. Do not reuse the previous runtime, fingerprint, `main.mlirb`, AAR, or
   manifest hashes. The new runtime fingerprint deliberately distinguishes
   cached masks created with a different model artifact.
6. Record the immutable upstream revision in RawCull's SAM 3 descriptor, but
   change the production descriptor to `ready` only after the independent
   legal decision confirms that RawCull may deliver the converted derivative
   without reproducing Meta's official gated checkpoint access flow. Technical
   provenance does not clear that release blocker.

The following packaging section starts only after each candidate has passed
its applicable provenance, licence, conversion, and runtime validation gates.

## EfficientSAM model for local use

RawCull supports Apple's Core AI conversion of EfficientSAM ViT-Tiny through
PhotoAIKit's `CoreAIEfficientSAMBackend`. EfficientSAM is point-prompted rather
than text-prompted. RawCull sends an empty point query: a one-query export uses
the image center, while a perfect-square multi-query export makes the Core AI
runtime place a regular grid of foreground points and PhotoAIKit returns the
highest-confidence mask.

For unattended Deep Review, create the 64-query, one-point variant. This gives
an 8 × 8 segment-everything grid and is more suitable than the exporter's
single-center-point default when the subject is off center.

The procedure below creates a local model bundle only. It does not approve the
bundle for redistribution or turn on RawCull's disabled production download.

### Download the matching Core AI converter

PhotoAIKit currently pins Apple's `coreai-models` revision shown below. Use the
same revision so the exporter and Swift runtime agree:

```sh
EFFICIENTSAM_COREAI_REVISION='bffc38fe48f50e4e962ac9772b64a5b55a605286'
EFFICIENTSAM_WORK_ROOT='/Users/thomas/ModelAssets/LocalBuild/EfficientSAM'
EFFICIENTSAM_COREAI_DIR="$EFFICIENTSAM_WORK_ROOT/coreai-models"
EFFICIENTSAM_EXPORT_DIR="$EFFICIENTSAM_WORK_ROOT/export"

mkdir -p "$EFFICIENTSAM_WORK_ROOT" "$EFFICIENTSAM_EXPORT_DIR"
git clone https://github.com/apple/coreai-models.git \
  "$EFFICIENTSAM_COREAI_DIR"
git -C "$EFFICIENTSAM_COREAI_DIR" switch --detach \
  "$EFFICIENTSAM_COREAI_REVISION"

test "$(git -C "$EFFICIENTSAM_COREAI_DIR" rev-parse HEAD)" = \
  "$EFFICIENTSAM_COREAI_REVISION"
test -z "$(git -C "$EFFICIENTSAM_COREAI_DIR" status --porcelain)"
```

The official exporter obtains the ViT-Tiny EfficientSAM implementation from
`yformer/EfficientSAM` and downloads
`efficient_sam_vitt.pt` from the `merve/EfficientSAM` Hugging Face repository.
No separate manual checkpoint download is required for a local build. Preserve
the terminal log and the downloaded checkpoint checksum if the result may
later become a distributable model.

### Create the RawCull EfficientSAM bundle

Install `uv` if necessary, then run the exporter from the pinned checkout:

```sh
brew install uv

cd "$EFFICIENTSAM_COREAI_DIR"
uv run models/efficient-sam/export.py \
  --model efficient_sam_vitt \
  --dtype float16 \
  --num-queries 64 \
  --num-pts 1 \
  --output-dir "$EFFICIENTSAM_EXPORT_DIR"
```

Do not add `--dynamic` to this Float16 export. Apple's runtime does not support
the dynamic attention reshape in Float16. Do not add `--overwrite` to an
evidence build; use a clean output directory instead.

The expected generated bundle is:

```text
efficient_sam_vitt_float16_static_q64/
├── metadata.json
└── efficient_sam_vitt_float16_static_q64.aimodel/
```

EfficientSAM is point-only, so it does not need the `tokenizer` directory that
CLIP and SAM 3 bundles require. Confirm that `metadata.json` selects the model
asset and that both paths exist:

```sh
EFFICIENTSAM_BUNDLE="$EFFICIENTSAM_EXPORT_DIR/efficient_sam_vitt_float16_static_q64"
EFFICIENTSAM_ASSET="$EFFICIENTSAM_BUNDLE/efficient_sam_vitt_float16_static_q64.aimodel"

test -f "$EFFICIENTSAM_BUNDLE/metadata.json"
test -d "$EFFICIENTSAM_ASSET"
test "$(plutil -extract kind raw -o - "$EFFICIENTSAM_BUNDLE/metadata.json")" = \
  'segmenter'
test "$(plutil -extract assets.main raw -o - "$EFFICIENTSAM_BUNDLE/metadata.json")" = \
  'efficient_sam_vitt_float16_static_q64.aimodel'

shasum -a 256 \
  "$EFFICIENTSAM_COREAI_DIR/.build/efficient_sam_weights.pt"
```

The checkpoint checksum printed by the last command is provenance evidence.
Record it together with the `coreai-models` revision and the exact export
command if the bundle will be retained.

### Install and select EfficientSAM in RawCull

RawCull expects the complete generated bundle contents in a directory named
`EfficientSAM`. For a non-sandboxed development build, install it with:

```sh
EFFICIENTSAM_INSTALL_DIR='/Users/thomas/Library/Application Support/RawCull/Models/EfficientSAM'

test ! -e "$EFFICIENTSAM_INSTALL_DIR"
mkdir -p "$(dirname "$EFFICIENTSAM_INSTALL_DIR")"
ditto "$EFFICIENTSAM_BUNDLE" "$EFFICIENTSAM_INSTALL_DIR"
```

A sandboxed build normally uses:

```text
/Users/thomas/Library/Containers/no.blogspot.RawCull/Data/Library/Application Support/RawCull/Models/EfficientSAM/
```

Do not merge the bundle into a previous model directory. In RawCull, open
**Settings > AI**, choose **Check Again**, and verify that **EfficientSAM
model** is available. Select **EfficientSAM** under **Deep Review segmentation
model**. The in-process readiness row must then show EfficientSAM as available.

EfficientSAM does not interpret the Deep Review target names such as person,
bird, or face. Those values remain in PhotoAIKit's common diagnostics and cache
keys, but the EfficientSAM provider uses the same grid-driven mask acquisition
for each target. Select SAM 3 when text-guided target semantics are required.

For a future downloadable pack, stage the approved bundle as
`Models/EfficientSAM`, add complete EfficientSAM Apache 2.0 and Apple BSD
3-Clause notices, record the checkpoint and converted-asset fingerprints, and
package it with asset-pack ID
`no.blogspot.RawCull.models.efficient-sam`. Keep the production catalogue entry
blocked until those release records and archive checks are complete.

## Preparing the downloadable resources

### Use an asset-pack archive, not a ZIP

Do not ZIP model directories manually. Xcode supplies `ba-package`, which
creates a Managed Background Assets archive with the required `.aar`
extension. The AAR is an opaque framework artifact, not a ZIP that RawCull
opens. Managed Background Assets downloads, verifies, installs, and exposes its
selected files.

Check the release tool before preparing packs:

```sh
xcrun --find ba-package
xcrun ba-package --version
xcrun ba-package help package
```

The lean archives below were created with `ba-package 2.0-beta` from the
currently selected Xcode beta. Recheck its version and help after every Xcode
change because its manifest schema, validation, and command interface are
tool-version specific.

### Recommended staging tree

```text
ModelAssets/Release/
├── Models/
│   ├── CLIP-DataComp/
│   │   ├── metadata.json
│   │   └── … .aimodel or .aimodelc plus declared resources …
│   ├── CLIP-OpenAI/
│   │   ├── metadata.json
│   │   └── … .aimodel or .aimodelc plus declared resources …
│   ├── EfficientSAM/
│   │   ├── metadata.json
│   │   └── … .aimodel or .aimodelc plus declared resources …
│   └── SAM3/
│       ├── metadata.json
│       └── … .aimodel or .aimodelc plus declared resources …
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

Validate each model directory with the same PhotoAIKit rules used at runtime.
Keep its complete redistribution notice, immutable upstream revision,
conversion recipe and tool versions, source checksums, and final checksums.
Packaging does not make an unverified checkpoint safe to redistribute.

### Create one packaging manifest per pack

One invocation creates one pack. Use explicit selectors rather than selecting
the complete model directory. For example, `Packaging/clip-openai.json` is:

```json
{
  "assetPackID": "no.blogspot.RawCull.models.clip-openai",
  "downloadPolicy": {
    "onDemand": {}
  },
  "fileSelectors": [
    { "file": "Models/CLIP-OpenAI/metadata.json" },
    { "directory": "Models/CLIP-OpenAI/tokenizer" },
    {
      "directory": "Models/CLIP-OpenAI/clip-vit-base-patch32_float16_static.aimodel"
    },
    { "directory": "Notices/CLIP-OpenAI" }
  ],
  "platforms": [ "macOS" ]
}
```

The four manifests select these runtime models and notice catalogs:

| Manifest | Runtime model directory | Notice catalog |
| --- | --- | --- |
| `clip-datacomp.json` | `Models/CLIP-DataComp/ViT-B-32-256-open_clip_model.safetensors_float16_static.aimodel` | `Notices/CLIP-DataComp` |
| `clip-openai.json` | `Models/CLIP-OpenAI/clip-vit-base-patch32_float16_static.aimodel` | `Notices/CLIP-OpenAI` |
| `efficient-sam.json` | `Models/EfficientSAM/efficient_sam_vitt_float16_static_q64.aimodel` | `Notices/EfficientSAM` |
| `sam3.json` | `Models/SAM3/sam3_float16.aimodel` | `Notices/SAM3` |

Each manifest also selects its model's `metadata.json` file. The CLIP and SAM
3 manifests additionally select their `tokenizer` directory; EfficientSAM has
no tokenizer. Do not replace these selectors with the broader model root. The
broad selector also packages `_source.aimodel`, `.aimodelc`, or other
conversion outputs that are not required at runtime.

Selector paths are relative. The tool resolves them against its current working
directory, includes directory contents recursively, and preserves their
logical paths. Run it from the release staging root.

The checked-in `ModelAssets/manifest.template.json` is only a four-pack
design skeleton. It is **not directly accepted by `ba-package`**. The tool
expects one top-level `assetPackID` per packaging manifest and a relative path
for every selector. Generate a fresh starting point with
`xcrun ba-package template` after a toolchain update, then reapply and review
the explicit selectors.

### Generate and record the AAR files

```sh
cd /Users/thomas/ModelAssets/Release

xcrun ba-package package Packaging/clip-datacomp.json \
  --output-path /Users/thomas/ModelsAAR/Output-lean/clip-datacomp.aar
xcrun ba-package package Packaging/clip-openai.json \
  --output-path /Users/thomas/ModelsAAR/Output-lean/clip-openai.aar
xcrun ba-package package Packaging/efficient-sam.json \
  --output-path /Users/thomas/ModelsAAR/Output-lean/efficient-sam.aar
xcrun ba-package package Packaging/sam3.json \
  --output-path /Users/thomas/ModelsAAR/Output-lean/sam3.aar

shasum -a 256 /Users/thomas/ModelsAAR/Output-lean/*.aar
stat -f '%N %z bytes' /Users/thomas/ModelsAAR/Output-lean/*.aar
```

The historical, unpublished lean build from August 2, 2026 produced the values
below. The DataComp archive predates the pinned-source re-export procedure and
must be rebuilt; do not use its listed size or checksum for the release pack.

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
| `clip-datacomp.aar` | 282,967,203 | `ab109bd64f61629d33a20c55364f0e40f98cbd070547d02a86d018de5ec4a8e6` |
| `clip-openai.aar` | 282,829,540 | `24e403f2f58cdea5765fb105d10fd37a57d4e53f5830e9b7248053e0229712dc` |
| `efficient-sam.aar` | Not generated | Not generated |
| `sam3.aar` | 1,542,689,135 | `f207db7d83fdb90baff6f32e894935f9267e3ebdc276358011d41bd36d5cd4df` |

Compared with the broad-directory archives, the two CLIP packs are about half
the previous size and SAM 3 is about one third. This is consistent with the
source and intermediate model representations being excluded.

The output path must end in `.aar`. Treat a published archive as immutable.
Keep the manifests, checksums, provenance, conversion logs, and exact
Xcode/`ba-package` version as release evidence. Copy archive SHA-256 and byte
sizes into the release record and matching catalogue metadata before changing
a descriptor to `.ready`.

### Create the self-hosted download manifest

The packaging manifests describe archive contents. The **download manifest** is
a different generated JSON file served to Macs. It lists versions, sizes,
policies, and download URLs.

```sh
xcrun ba-package download-manifest create \
  /Users/thomas/ModelsAAR/Output-lean/clip-datacomp.aar \
  /Users/thomas/ModelsAAR/Output-lean/clip-openai.aar \
  /Users/thomas/ModelsAAR/Output-lean/efficient-sam.aar \
  /Users/thomas/ModelsAAR/Output-lean/sam3.aar \
  --asset-pack-versions 1 1 1 1 \
  --macos \
  --download-base-url \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/ \
  --output-path /Users/thomas/ModelsAAR/Output-lean/manifest.json
```

The base URL is not an individual archive URL. The tool appends each
asset-pack ID, not the local AAR filename. Inspect the generated JSON and make
the GitHub Release asset names match its URLs exactly. The planned URLs are:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/no.blogspot.RawCull.models.clip-datacomp
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/no.blogspot.RawCull.models.clip-openai
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/no.blogspot.RawCull.models.efficient-sam
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/no.blogspot.RawCull.models.sam3
```

The local inputs retain their `.aar` extension, but the release copies must be
named with the exact asset-pack IDs above because those are the URL path
components generated by `ba-package`. The proposed manifest URL, if the
manifest is uploaded as another release asset, is:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/manifest.json
```

Ensure every generated pack URL returns the archive rather than an HTML login
or error page. GitHub's release-download endpoint may redirect to asset
storage, so HTTP verification must follow redirects and confirm the final byte
count and checksum.

At the time of this documentation update, the selected Xcode beta's
`ba-package 2.0-beta` successfully created the archives but
`download-manifest create` rejected the valid `.aar` inputs with the message
`path extension isn't "aar"`. Do not rename the local archives to work around
that contradictory diagnostic. Regenerate and inspect the manifest with a
stable or corrected Xcode toolchain before creating the GitHub release.

Upload packs first, verify every generated URL, and publish
`manifest.json` last. Both `BAManifestURL` and RawCull's self-hosted source
must identify the manifest, not an AAR. For later releases use
`ba-package download-manifest update` or create a deliberately versioned new
manifest; RawCull requests the latest pack version.

For Apple hosting, generate the same AAR files but not the self-hosted download
manifest. Upload the packs and versions in App Store Connect, then use the
Apple-hosted app and extension configuration described above.

## What happens when the user selects Download

1. `startModelDownload` accepts only a ready or retryable failed row and
   prevents two tasks for the same model.
2. The row immediately changes to `downloading(progress: 0)` and shows Cancel.
3. The coordinator resolves the stable model descriptor and rechecks release
   readiness so UI state cannot bypass distribution policy.
4. If explicit acceptance is required, it loads
   `ModelLicenceAcceptances.json` and requires a record matching the current
   model, licence version, and licence-text checksum.
5. The service rejects an unconfigured source before requesting a manifest.
6. `AssetPackManager.shared.manifest` obtains the hosting-mode manifest. A
   self-hosted build uses `BAManifestURL`; an Apple-hosted build uses the
   store downloader extension and Apple's asset metadata.
7. RawCull looks up the exact asset-pack ID. It never guesses a URL or accepts
   a similarly named pack.
8. RawCull listens to asynchronous `statusUpdates`. Progress is delivered to
   the main actor and clamped to zero through one.
9. `ensureLocalAvailability(of:requireLatestVersion: true)` asks Managed
   Background Assets to download and install the latest selected AAR in managed
   storage.
10. RawCull reports 100 percent, resolves the catalogue's logical model path,
    and verifies that it is a directory. Incorrect archive organization becomes
    `downloadedModelNotFound`.
11. The row changes to `validating`; the URL becomes a candidate for the
    matching CLIP, EfficientSAM, or SAM 3 resource manager.
12. PhotoAIKit validates `metadata.json`, the chosen `.aimodel` or
    `.aimodelc`, declared resources, and the runtime contract. Only then does
    RawCull construct a provider and refresh feature capabilities.
13. The next snapshot reports the pack installed. The feature is active only
    when validation and provider creation also succeeded.

Cancel stops RawCull's task and status listener. RawCull does not assume the
framework removed partial data; it requests a new authoritative snapshot.
Failures become `failed(message:)`, and Retry repeats the guarded sequence.
Remove asks the framework to remove the asset-pack ID, clears its managed
candidate URL, and refreshes capabilities without deleting manually installed
models.
