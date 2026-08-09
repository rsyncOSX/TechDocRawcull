+++
author = "Thomas Evensen"
title = "AI Model Download Service"
linkTitle = "AI Model Downloads"
date = "2026-07-31"
description = "Architecture, storage, activation, and operation of RawCull AI model downloads using self-hosted or Apple-hosted Managed Background Assets."
tags = ["ai", "models", "downloads", "siglip2", "efficient-sam", "background-assets", "self-hosting", "apple-hosting"]
categories = ["technical details"]
weight = 30
+++

# AI model download service

RawCull uses Managed Background Assets for optional AI model bundles. The app
talks only to `AssetPackManager`; the downloader extension selects whether the
packs are self-hosted or Apple-hosted.

The production build is configured for the public model-release manifest:

`https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/manifest.json`

Only catalogue entries whose release readiness is `ready` appear as
downloadable. The DataComp CLIP pack is on demand, so no model transfer starts
until the user selects **Download**. Progress, cancellation, removal, local
licence handling, and model validation remain managed by RawCull.

The app and extension share only the Managed Background Assets container
`group.no.blogspot.RawCull.model-assets`. This identifier is also recorded as
`BAAppGroupID` in the app Info.plist.

## Hosting decision

Self-hosting is the current default because RawCull's documented distribution is
a Developer ID DMG. Apple-hosted asset packs are appropriate only for an App
Store or TestFlight build. The extension already contains an Apple-hosted
`StoreDownloaderExtension` variant behind the
`RAWCULL_APPLE_HOSTED_MODEL_ASSETS` compilation condition, so the application
service and UI do not change when hosting changes.

### GitHub release origin

The proposed self-hosted origin is a dedicated repository, separate from the
RawCull application releases:

```text
https://github.com/rsyncOSX/RawCull-AI-Models
```

The first model-set release is:

| Field             | Value                                                                 |
| ----------------- | --------------------------------------------------------------------- |
| Tag               | `v1`                                                                  |
| Title             | `RawCull AI Models v1`                                                |
| Download base URL | `https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/` |

This keeps model-pack versions independent of RawCull application tags such as
`v2.2.4`. Commit only the README, notices, licence texts, provenance, checksums,
and packaging documentation to the repository. Store the large archives as
GitHub Release assets, not Git objects or Git LFS objects. Each current archive
is below GitHub's 2 GiB per-release-asset limit; GitHub documents the current
limits under
[About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas).

The `v1` release currently contains `clip-datacomp.aar` and `manifest.json`.
The app pins the manifest and archive to the `v1` download path. GitHub's
`releases/latest/download` redirect excludes prereleases and therefore cannot
be used while `v1` is classified as a prerelease.

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
  tokenizer MIT notice, and Apple's `coreai-models` BSD 3-Clause notice. Its
  published `v1` archive is the only production descriptor currently enabled.
  The archive's embedded `PROVENANCE.json` still describes the earlier runtime
  filename and hashes; refresh that record and rebuild the archive before using
  RawCull's provenance-enforcing release target.
- OpenAI CLIP includes the OpenAI CLIP MIT notice and Apple's `coreai-models`
  BSD 3-Clause notice. Release remains blocked until the MIT terms are verified
  as applying to the exact checkpoint weights and the cached immutable revision
  and source checksum are conclusively bound to the converted output.
- SigLIP 2 Base/16-256 uses Google's Apache License 2.0 checkpoint and Apple's
  `coreai-models` BSD 3-Clause conversion code. It is currently an experimental
  RawCullFB model, not a production Managed Background Assets descriptor. Before
  release, add a pack-specific notice catalogue and review redistribution,
  provenance, archive, and catalogue metadata independently.
- EfficientSAM uses the upstream Apache License 2.0 and Apple's `coreai-models`
  BSD 3-Clause conversion code. Redistribution remains blocked until the exact
  EfficientSAM source revision, checkpoint checksum, converted asset
  fingerprint, archive checksum, and complete notices are recorded.
- Meta SAM 3 now includes the complete SAM License dated November 19, 2025 and
  Apple's `coreai-models` BSD 3-Clause notice. RawCull also bundles that
  verified SAM licence text for explicit user acceptance. Release remains
  blocked until ungated redistribution is confirmed compatible with the SAM
  License and Meta's official gated checkpoint access conditions.

The notice catalogs must remain inside their corresponding archives, but their
presence is evidence and attribution, not release approval.

The production catalogue can download DataComp CLIP. The OpenAI CLIP,
EfficientSAM, and SAM 3 descriptors remain blocked. A descriptor becomes
downloadable only after its `releaseReadiness` changes to `ready`, its archive
metadata is complete, and any required verified licence has been accepted.

## Security and privacy boundary

Managed Background Assets owns transport and installation. RawCull never
constructs arbitrary destination paths from a server response. It asks the
framework for a known asset-pack ID and a catalogue-owned relative model path,
then passes that directory through the existing model-bundle validation before
using it.

The licence acceptance store records model ID/version, licence version and text
checksum, date, and RawCull version. A changed licence checksum invalidates old
acceptance automatically.

Model downloads send only the connection information necessary to serve the
asset. Photographs, embeddings, masks, prompts, and inference results are not
part of this flow.

## Signing and provisioning

The Managed Background Assets extension adds a second executable to RawCull. The
application, extension, and shared App Group use these identifiers:

| Purpose                            | Identifier                               |
| ---------------------------------- | ---------------------------------------- |
| RawCull application                | `no.blogspot.RawCull`                    |
| Model downloader extension         | `no.blogspot.RawCull.ModelDownloader`    |
| Shared Background Assets App Group | `group.no.blogspot.RawCull.model-assets` |
| Apple developer team               | `93M47F4H9T`                             |

The extension is embedded inside RawCull; it does not need a separate App Store
Connect app or store listing.

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
5. Repeat the previous two steps for `no.blogspot.RawCull.ModelDownloader`.

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
notarization and DMG workflow. Apple recommends exporting an Xcode-built Mac app
containing nested extensions from its archive.

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

The production self-hosted build must report:

```text
group.no.blogspot.RawCull.model-assets
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/manifest.json
com.apple.backgroundassets.managed
```

During development Xcode may use an Xcode-managed wildcard development profile,
even when the signed code has the explicit identifiers above. Do not use the
profile's display name as the only verification. The Developer Portal records
and the signed entitlements must both match. The final distribution export must
also pass Xcode's signing validation.

### Verify the local signing identities

App IDs and App Groups are team records in the Apple Developer account. They are
not stored in Keychain and do not need to be recreated on another Mac.

Keychain stores signing certificates together with their private keys. List the
identities available to command-line signing:

```sh
security find-identity -v -p codesigning
```

For development archives, the Mac needs a valid `Apple Development` identity.
For direct distribution, it also needs access to the appropriate
`Developer ID Application` identity. App Store distribution instead uses the
relevant Apple distribution identity or Xcode's cloud-managed signing.

A certificate visible without its private key is not a usable signing identity.
In Keychain Access, a usable identity appears under **My Certificates** and
expands to show its private key.

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
archived with permission to update provisioning. Xcode-managed development and
distribution profiles may not appear in the Profiles list on the Developer
website.

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

Development certificates belong to individual developers, and Apple permits each
Mac to have an appropriate development identity. It is usually cleaner to let
Xcode manage development identities separately on each Mac. Apple currently
limits an individual developer to two Mac development certificates, so two Macs
can normally have one each. Do not revoke a certificate still in use by the
other Mac merely to make Xcode issue another one.

Distribution identities require more care. If Xcode's cloud-managed distribution
signing is available to the account, use it. If the second Mac must use an
existing locally managed Developer ID or distribution identity, transfer the
complete certificate and private key from the first Mac:

1. On the first Mac, open **Xcode > Settings > Accounts**.
2. Select the Apple Account and team, then click **Manage Certificates**.
3. Control-click the required distribution certificate and choose **Export
   Certificate**.
4. Save it as a password-protected `.p12` file using a strong, unique password.
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

| Layer                                                | Responsibility                                                                                           |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `AIModelDownloadsView`                               | Displays catalogue details, licence review, state, progress, download, cancellation, retry, and removal. |
| `RawCullAISettingsModel`                             | Owns one download task per model and publishes main-actor UI state.                                      |
| `RawCullAIModelDownloadCoordinator`                  | Refuses blocked releases and enforces explicit licence acceptance.                                       |
| `RawCullManagedBackgroundAssetsModelDownloadService` | Uses `AssetPackManager` for both hosting modes.                                                          |
| `RawCullModelDownloader`                             | Compiles as the self-hosted or Apple-hosted downloader extension.                                        |
| `RawCullAIIntegration`                               | Validates installed bundles and creates the CLIP, EfficientSAM, or SAM 3 runtime provider.               |

A refresh first checks each catalogue descriptor's `releaseReadiness`. A blocked
model becomes unavailable before any manifest request. For an approved model,
RawCull asks whether its pack is already local. Otherwise it loads the framework
manifest and requires the exact catalogue asset-pack ID.

A permitted download subscribes to `statusUpdates`, then calls
`ensureLocalAvailability(of:requireLatestVersion: true)`. After installation,
RawCull resolves the model's known logical path, enters the validating state,
and gives the URL to the appropriate model resource manager. Only a bundle that
passes PhotoAIKit validation becomes available to similarity, semantic search,
or segmentation. A completed transfer is therefore not by itself successful AI
activation. Vision feature prints remain the safe CLIP similarity fallback until
a CLIP provider is ready.

Cancellation stops RawCull's task and progress listener. The next snapshot asks
Managed Background Assets for the authoritative state. Removal uses
`AssetPackManager.remove`; RawCull never deletes a framework-returned path
directly.

## Asset-pack contents and storage

The template defines these logical packs:

| Model         | Asset-pack ID                              | Logical model directory |
| ------------- | ------------------------------------------ | ----------------------- |
| DataComp CLIP | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp`  |
| OpenAI CLIP   | `no.blogspot.RawCull.models.clip-openai`   | `Models/CLIP-OpenAI`    |
| EfficientSAM  | `no.blogspot.RawCull.models.efficient-sam` | `Models/EfficientSAM`   |
| Meta SAM 3    | `no.blogspot.RawCull.models.sam3`          | `Models/SAM3`           |

`ModelAssets/manifest.template.json` is a developer input, not the deployable
manifest. Release-time Managed Background Assets tools generate the archives and
production manifest. Each pack should include the converted model plus its
applicable licence text, immutable upstream revision, source and archive
checksums, and conversion metadata.

The checked-in `ModelAssets/Notices` directory is the canonical source for the
three existing pack-specific notice catalogs. Add and review an EfficientSAM
notice catalog before packaging that fourth model. Copy the matching catalogs
into the staging tree before packaging. The release manifests use explicit
selectors so that the runtime model and required resources are included while
`_source.aimodel`, compiled intermediates, and unrelated files are excluded.

A self-hosted HTTPS origin stores the generated archives and generated manifest.
Upload and verify immutable, versioned archives first and publish the manifest
last, so clients cannot discover an incomplete pack. Retain an archive while a
supported manifest or app can refer to it. Apple-hosted builds upload the
equivalent packs through App Store Connect; Apple owns external storage and
delivery.

On the Mac, the framework owns managed installation inside the shared
`group.no.blogspot.RawCull.model-assets` container. RawCull does not depend on
its physical path. It resolves only a catalogue-owned path such as:

```swift
AssetPackManager.shared.url(for: FilePath("Models/CLIP-OpenAI"))
```

The returned URL is authoritative and is checked before validation. Do not
hard-code its parent, move its contents, or scan the App Group container.
Manually installed models under `~/Library/Application Support/RawCull/Models/`
are separate. The Remove action affects only the managed pack.

Licence acceptance is also separate from the model and is atomically stored at
`~/Library/Application Support/RawCull/ModelLicenceAcceptances.json`. Acceptance
is bound to model version, licence version, verified licence-text SHA-256, date,
and RawCull version. Changing the checksum invalidates it.

## Activation gates

A live service requires three independent gates:

1. The catalogue descriptor must be `.ready`, with all licence, provenance,
   checksum, and redistribution evidence complete.
2. The Swift service source must be a real `.selfHosted(manifestURL:)` HTTPS URL
   or `.appleHosted`.
3. The app plist and downloader extension must select that same hosting mode.

`RawCullAIModelDownloadCoordinator.live(paths:)` and `BAManifestURL` use the
same GitHub manifest endpoint. Keep those values synchronized. An Apple-hosted
build must instead construct the service with `.appleHosted`, define
`RAWCULL_APPLE_HOSTED_MODEL_ASSETS`, set `BAUsesAppleHosting` to `YES`, and
remove `BAManifestURL`.

Do not mark a descriptor ready merely to test transport. Ready is an
application-level statement that the exact pack is approved for redistribution.

## DataComp CLIP model for release

RawCull uses the OpenCLIP `ViT-B-32-256` architecture with the
`datacomp_s34b_b86k` weights. The release input must be the following exact
file, not a fresh resolution of the OpenCLIP pretrained alias:

| Field                       | Required value                                                     |
| --------------------------- | ------------------------------------------------------------------ |
| Repository                  | `laion/CLIP-ViT-B-32-256x256-DataComp-s34B-b86K`                   |
| Revision                    | `4afec35ffe57a943d569ff7ee888061830164da8`                         |
| Source file                 | `open_clip_model.safetensors`                                      |
| Byte size                   | `605189364`                                                        |
| SHA-256                     | `92c26d60d3200ed5ed040dff31a8d19f8140648da8007216c25744c478deef27` |
| Architecture                | `ViT-B-32-256`                                                     |
| Export precision and shapes | Float16, static batch dimensions                                   |

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
PhotoAIKit revision `2cb07d604beee3549df4d361a5d48b3e9506fb87`. Create a
detached, clean checkout of that revision rather than changing a development
checkout in place:

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

`PhotoAIKit/Tools/export_clip.py` normally accepts the `datacomp_s34b_b86k`
pretrained tag. Using that tag for this conversion would allow OpenCLIP to
resolve the checkpoint again and would repeat the provenance problem. OpenCLIP
3.2.0 also accepts a local checkpoint path through the same `pretrained`
parameter. Run the tool while the verified file is the current directory and
pass its local filename explicitly:

```sh
(
  cd "$(dirname "$DATACOMP_PHOTOAIKIT_DIR")/source" || exit 1

  uv run --python 3.13 \
    --script "$DATACOMP_PHOTOAIKIT_DIR/Tools/export_clip.py" \
    --model openclip-datacomp \
    --architecture ViT-B-32-256 \
    --pretrained open_clip_model.safetensors \
    --output-dir "$DATACOMP_EXPORT_DIR" \
    --bundle-name CLIP-DataComp \
    --dtype float16
)
```

Do not add `--dynamic`; RawCull's release model uses static batch dimensions. Do
not add `--overwrite` to the evidence run. If the destination exists, keep it as
evidence and start a new attempt in a new directory.

The script's PEP 723 metadata pins the Python conversion dependencies, including
`coreai-core`, `coreai-torch`, OpenCLIP, PyTorch, torchvision, and Transformers.
Preserve the complete terminal log and record at least:

```sh
uv --version
python3 --version
sw_vers
xcodebuild -version
git -C "$DATACOMP_PHOTOAIKIT_DIR" rev-parse HEAD
git -C "$DATACOMP_PHOTOAIKIT_DIR" show HEAD:Package.swift
```

The exporter verifies tokenizer parity, creates independent `image_encoder` and
`text_encoder` Core AI functions, optimizes the runtime asset, saves the CLIP
tokenizer, and writes a fingerprint for the runtime asset into `metadata.json`.

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
`6d9109cc838977f3ca94a379eec36aecc7c807e1785cd729660ca2fc0171fb35`. If the new
export differs, stop and audit the tokenizer source and exporter behavior
instead of silently replacing the recorded checksum.

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
`CLIP-DataComp` directory at the DataComp path displayed by **RawCull >
Settings > AI**. A non-sandboxed development build normally uses:

```text
/Users/thomas/Library/Application Support/RawCull/Models/CLIP-DataComp/
```

A sandboxed build normally uses:

```text
/Users/thomas/Library/Containers/no.blogspot.RawCull/Data/Library/Application Support/RawCull/Models/CLIP-DataComp/
```

Use an empty destination. Move any previous test model to a separately named
backup directory; do not merge old and new bundle contents. Launch RawCull, open
**Settings > AI**, and choose **Check Again**. The DataComp model must become
available without a checksum or metadata error. Select DataComp, enable CLIP
similarity, and smoke-test both image similarity and text-to-image semantic
search. The first load may take longer while macOS specializes the portable Core
AI asset for that Mac.

PhotoAIKit's `ModelBundleResolver` verifies `metadata.json`, the selected asset,
the required tokenizer, and the asset fingerprint. `CoreAICLIPProvider` then
validates the runtime configuration and the normalized embedding outputs. A
successful export command alone is not sufficient release validation.

### Move the approved candidate into release staging

After validation, copy the complete generated bundle—not the manually installed
test copy—into:

```text
/Users/thomas/ModelAssets/Release/Models/CLIP-DataComp/
```

Update all release records to describe the new candidate accurately:

1. In `ModelAssets/Notices/CLIP-DataComp/PROVENANCE.json`, record the upstream
   repository, revision, source filename, `605189364` byte size, source SHA-256,
   PhotoAIKit commit, dependency versions, conversion command, tokenizer
   checksum, runtime asset filename, asset fingerprint, and `main.mlirb`
   checksum.
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

Repeat the same provenance-controlled conversion for OpenAI CLIP and SAM 3
before using the shared packaging procedure below.

## OpenAI CLIP model for release

RawCull uses the original OpenAI CLIP ViT-B/32 checkpoint exported through
Transformers. The release input must be the following exact Hugging Face
snapshot and PyTorch weight file, not an unpinned resolution of `main`:

| Field                       | Required value                                                     |
| --------------------------- | ------------------------------------------------------------------ |
| Repository                  | `openai/clip-vit-base-patch32`                                      |
| Revision                    | `3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268`                         |
| Source file                 | `pytorch_model.bin`                                                |
| Byte size                   | `605247071`                                                        |
| SHA-256                     | `a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f` |
| Architecture                | `ViT-B-32`                                                         |
| Export precision and shapes | Float16, static batch dimensions                                   |

The existing converted asset was created from a local cache at this revision,
but the exporter did not cryptographically bind that snapshot to the output.
Its provenance record therefore has `source_revision_recorded_by_exporter` set
to `null`. Create a new conversion; do not add the cached hash to the old record
and treat the old `.aimodel` as verified.

The technical procedure below does not clear redistribution. The Hugging Face
checkpoint does not currently identify an explicit weight-level licence, and
OpenAI Support did not confirm that the source repository's MIT licence covers
the hosted weights. Keep the descriptor blocked until the separate decision in
**Licence audit** and the OpenAI CLIP clearance procedure is complete.

### Create a clean OpenAI CLIP evidence workspace

Use a new evidence directory so the pinned Hugging Face cache, converter
checkout, and output remain separate from the earlier conversion:

```sh
OPENAI_CLIP_REPOSITORY='openai/clip-vit-base-patch32'
OPENAI_CLIP_REVISION='3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268'
OPENAI_CLIP_SOURCE_FILENAME='pytorch_model.bin'
OPENAI_CLIP_EXPECTED_BYTES='605247071'
OPENAI_CLIP_EXPECTED_SHA256='a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f'

OPENAI_CLIP_EVIDENCE_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/CLIP-OpenAI/$OPENAI_CLIP_REVISION"
OPENAI_CLIP_HF_HOME="$OPENAI_CLIP_EVIDENCE_ROOT/huggingface"
OPENAI_CLIP_EXPORT_DIR="$OPENAI_CLIP_EVIDENCE_ROOT/export"
OPENAI_CLIP_PHOTOAIKIT_DIR="$OPENAI_CLIP_EVIDENCE_ROOT/PhotoAIKit"

mkdir -p "$OPENAI_CLIP_HF_HOME" "$OPENAI_CLIP_EXPORT_DIR"
```

Use the same reviewed PhotoAIKit revision as the DataComp release conversion:

```sh
OPENAI_CLIP_PHOTOAIKIT_REVISION='2cb07d604beee3549df4d361a5d48b3e9506fb87'

git clone https://github.com/rsyncOSX/PhotoAIKit.git \
  "$OPENAI_CLIP_PHOTOAIKIT_DIR"
git -C "$OPENAI_CLIP_PHOTOAIKIT_DIR" switch --detach \
  "$OPENAI_CLIP_PHOTOAIKIT_REVISION"

test "$(git -C "$OPENAI_CLIP_PHOTOAIKIT_DIR" rev-parse HEAD)" = \
  "$OPENAI_CLIP_PHOTOAIKIT_REVISION"
test -z "$(git -C "$OPENAI_CLIP_PHOTOAIKIT_DIR" status --porcelain)"
```

If RawCull resolves a later PhotoAIKit revision, review the exporter changes and
record the exact revision actually used instead of copying the value above.

### Download the pinned OpenAI CLIP snapshot

Point Hugging Face and Transformers at the evidence-specific cache, then
download only the PyTorch model and its configuration and tokenizer resources:

```sh
export HF_HOME="$OPENAI_CLIP_HF_HOME"

OPENAI_CLIP_SNAPSHOT="$(hf download "$OPENAI_CLIP_REPOSITORY" \
  config.json \
  "$OPENAI_CLIP_SOURCE_FILENAME" \
  merges.txt \
  preprocessor_config.json \
  special_tokens_map.json \
  tokenizer.json \
  tokenizer_config.json \
  vocab.json \
  README.md \
  --revision "$OPENAI_CLIP_REVISION" \
  --quiet)"

test "$(basename "$OPENAI_CLIP_SNAPSHOT")" = "$OPENAI_CLIP_REVISION"
```

The exporter currently asks Transformers for the repository ID rather than a
local snapshot path. Establish its cached `main` reference separately and
require that reference to resolve to the pinned snapshot before enabling
offline mode:

```sh
OPENAI_CLIP_MAIN_SNAPSHOT="$(hf download "$OPENAI_CLIP_REPOSITORY" \
  --revision main \
  --exclude flax_model.msgpack \
  --exclude tf_model.h5 \
  --quiet)"

test "$(basename "$OPENAI_CLIP_MAIN_SNAPSHOT")" = "$OPENAI_CLIP_REVISION"
test "$OPENAI_CLIP_MAIN_SNAPSHOT" = "$OPENAI_CLIP_SNAPSHOT"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
```

The `main` lookup is only a compatibility step for the current exporter. If it
does not resolve to the required commit, stop; do not convert a newer snapshot.
Prefer a future exporter option that accepts `OPENAI_CLIP_SNAPSHOT` directly,
then remove this compatibility lookup. Preserve the CLI output and the cache
metadata as private evidence.

### Verify the OpenAI source before conversion

Confirm the selected weight file and all resources required by the exporter:

```sh
OPENAI_CLIP_SOURCE="$OPENAI_CLIP_SNAPSHOT/$OPENAI_CLIP_SOURCE_FILENAME"

test -f "$OPENAI_CLIP_SNAPSHOT/config.json"
test -f "$OPENAI_CLIP_SOURCE"
test -f "$OPENAI_CLIP_SNAPSHOT/tokenizer.json"
test -f "$OPENAI_CLIP_SNAPSHOT/tokenizer_config.json"
test -f "$OPENAI_CLIP_SNAPSHOT/merges.txt"
test -f "$OPENAI_CLIP_SNAPSHOT/vocab.json"

shasum -a 256 "$OPENAI_CLIP_SOURCE"
stat -f '%z bytes %N' "$OPENAI_CLIP_SOURCE"
```

The checksum and byte size must be exactly:

```text
a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f
605247071 bytes
```

Make the verification fail closed:

```sh
test "$(shasum -a 256 "$OPENAI_CLIP_SOURCE" | cut -d ' ' -f 1)" = \
  "$OPENAI_CLIP_EXPECTED_SHA256"
test "$(stat -f '%z' "$OPENAI_CLIP_SOURCE")" = \
  "$OPENAI_CLIP_EXPECTED_BYTES"
```

If any check fails, stop without converting or substituting another weight
format. Investigate the source revision and download first.

### Export from the verified offline cache

Run the OpenAI preset only after the exact snapshot and cached reference checks
have succeeded. Offline mode prevents Transformers from fetching a different
revision during model or tokenizer loading:

```sh
uv run --python 3.13 \
  --script "$OPENAI_CLIP_PHOTOAIKIT_DIR/Tools/export_clip.py" \
  --model openai \
  --output-dir "$OPENAI_CLIP_EXPORT_DIR" \
  --bundle-name CLIP-OpenAI \
  --dtype float16
```

Do not add `--dynamic` or `--overwrite` to the evidence run. Preserve the
complete terminal log and record the toolchain alongside the DataComp record:

```sh
uv --version
python3 --version
sw_vers
xcodebuild -version
git -C "$OPENAI_CLIP_PHOTOAIKIT_DIR" rev-parse HEAD
git -C "$OPENAI_CLIP_PHOTOAIKIT_DIR" show HEAD:Package.swift
```

The exporter must write `source_revision` as the required commit in
`metadata.json`. A missing or different value breaks the provenance chain even
when the source file checksum was verified.

The generated bundle has this layout:

```text
CLIP-OpenAI/
├── metadata.json
├── tokenizer/
├── clip-vit-base-patch32_float16_static.aimodel/
└── clip-vit-base-patch32_float16_static_source.aimodel/
```

Keep `_source.aimodel` in private conversion evidence but exclude it from the
downloadable pack.

### Inspect, fingerprint, and validate the OpenAI bundle

Set the generated paths and validate the metadata and selected runtime asset:

```sh
OPENAI_CLIP_BUNDLE="$OPENAI_CLIP_EXPORT_DIR/CLIP-OpenAI"
OPENAI_CLIP_RUNTIME_ASSET="$OPENAI_CLIP_BUNDLE/clip-vit-base-patch32_float16_static.aimodel"

test -f "$OPENAI_CLIP_BUNDLE/metadata.json"
test -f "$OPENAI_CLIP_BUNDLE/tokenizer/tokenizer.json"
test -d "$OPENAI_CLIP_RUNTIME_ASSET"

plutil -extract source_revision raw -o - \
  "$OPENAI_CLIP_BUNDLE/metadata.json"
plutil -extract architecture raw -o - \
  "$OPENAI_CLIP_BUNDLE/metadata.json"
plutil -extract assets.main raw -o - \
  "$OPENAI_CLIP_BUNDLE/metadata.json"
plutil -extract asset_fingerprints.main.value raw -o - \
  "$OPENAI_CLIP_BUNDLE/metadata.json"

test "$(plutil -extract source_revision raw -o - \
  "$OPENAI_CLIP_BUNDLE/metadata.json")" = "$OPENAI_CLIP_REVISION"

python3 "$OPENAI_CLIP_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$OPENAI_CLIP_RUNTIME_ASSET"
```

The architecture must be `ViT-B-32`, `assets.main` must name the runtime asset
above, and the generated fingerprint must equal the fingerprint recorded in
`metadata.json`.

Verify the tokenizer and record fresh output hashes:

```sh
shasum -a 256 "$OPENAI_CLIP_BUNDLE/tokenizer/tokenizer.json"
python3 "$OPENAI_CLIP_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$OPENAI_CLIP_RUNTIME_ASSET"
find "$OPENAI_CLIP_RUNTIME_ASSET" -type f -name main.mlirb \
  -exec shasum -a 256 {} \;
```

The currently audited tokenizer SHA-256 is
`6d9109cc838977f3ca94a379eec36aecc7c807e1785cd729660ca2fc0171fb35`.
If it changes, audit the pinned tokenizer files and exporter before proceeding.
The new runtime hashes are conversion outputs and need not match the previous
unverified model.

Run the PhotoAIKit tests, then install a copy of the complete `CLIP-OpenAI`
directory at the OpenAI path shown by **RawCull > Settings > AI**:

```sh
swift test --package-path "$OPENAI_CLIP_PHOTOAIKIT_DIR"
```

Use an empty destination rather than merging it with an older bundle. Choose
**Check Again**, select OpenAI CLIP, enable CLIP similarity, and smoke-test both
image similarity and text-to-image semantic search. PhotoAIKit must accept the
metadata, tokenizer, asset fingerprint, runtime configuration, and normalized
embeddings before the candidate can proceed.

### Move the approved OpenAI candidate into release staging

After validation, copy the generated candidate, not the manually installed test
copy, into:

```text
/Users/thomas/ModelAssets/Release/Models/CLIP-OpenAI/
```

Complete the release evidence and packaging records:

1. Update `ModelAssets/Notices/CLIP-OpenAI/PROVENANCE.json` with the exact
   repository, revision, source filename, byte size, source SHA-256, PhotoAIKit
   commit, dependency versions, command, tokenizer checksum, runtime filename,
   asset fingerprint, and `main.mlirb` checksum.
2. Update `NOTICE.md` when the runtime filename or recorded evidence changes.
   Keep the complete applicable OpenAI CLIP and Apple conversion notices in the
   pack, without treating their presence as licence approval.
3. Ensure `Packaging/clip-openai.json` selects `metadata.json`, `tokenizer`, the
   optimized runtime `.aimodel`, and `Notices/CLIP-OpenAI`; exclude the bundle
   root and `_source.aimodel`.
4. Rebuild and inspect `clip-openai.aar`, then record its new byte size and
   SHA-256 in provenance and in the RawCull catalogue.
5. Do not reuse the historical runtime, archive, or manifest hashes. A new model
   fingerprint intentionally invalidates incompatible cached embeddings.
6. Keep the production descriptor blocked until the exact trained weights are
   cleared for the intended conversion, commercial use, and redistribution and
   every provenance, validation, notice, archive, and download check passes.

## SigLIP 2 Base/16-256 experimental model

RawCullFB can test Google's fixed-resolution SigLIP 2 Base Patch16 model through
PhotoAIKit and Core AI. This model is not currently part of RawCull's production
Managed Background Assets catalogue. Do not add it to the public manifest until
the separate licence, notice, packaging, and release-readiness work is complete.

Use the following exact source snapshot:

| Field                       | Required value                                                     |
| --------------------------- | ------------------------------------------------------------------ |
| Repository                  | `google/siglip2-base-patch16-256`                                  |
| Revision                    | `3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab`                         |
| Source file                 | `model.safetensors`                                                |
| Byte size                   | `1500985224`                                                       |
| SHA-256                     | `6125cacc01fa93bdc98a0c5101cefcd69b2ed1f8ab4f38d86f4ad5984f5dc863` |
| Architecture                | `SigLIP2-Base-Patch16-256`                                         |
| Image input                 | `1 x 3 x 256 x 256`, fixed stretch with bilinear interpolation     |
| Text input                  | `1 x 64`, Gemma/Hugging Face tokenizer JSON                        |
| Embedding dimensions        | `768`                                                              |
| Export precision and shapes | Float16, static batch dimensions                                   |
| Upstream licence            | Apache License 2.0                                                 |

Google's fixed-resolution SigLIP 2 checkpoint intentionally retains the
original `siglip` configuration type. The exporter follows the checkpoint's
declared architecture through Transformers `AutoModel`; forcing
`Siglip2Model` creates an incompatible flexible-resolution patch projection.

### Create a clean SigLIP 2 workspace

Keep the source snapshot and converted output separate. For an experimental
local build:

```sh
SIGLIP2_REPOSITORY='google/siglip2-base-patch16-256'
SIGLIP2_REVISION='3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab'
SIGLIP2_SOURCE_FILENAME='model.safetensors'
SIGLIP2_EXPECTED_BYTES='1500985224'
SIGLIP2_EXPECTED_SHA256='6125cacc01fa93bdc98a0c5101cefcd69b2ed1f8ab4f38d86f4ad5984f5dc863'

SIGLIP2_ROOT='/Users/thomas/GitHub/Models/SigLIP2-Base-Patch16-256'
SIGLIP2_SOURCE_DIR="$SIGLIP2_ROOT/source"
SIGLIP2_EXPORT_DIR="$SIGLIP2_ROOT"
SIGLIP2_PHOTOAIKIT_DIR='/Users/thomas/GitHub/RawCull/PhotoAIKit'

mkdir -p "$SIGLIP2_SOURCE_DIR"
test -f "$SIGLIP2_PHOTOAIKIT_DIR/Tools/export_siglip2.py"
```

The current exporter is in the local PhotoAIKit development checkout. Record
its exact state with the conversion evidence:

```sh
git -C "$SIGLIP2_PHOTOAIKIT_DIR" rev-parse HEAD
git -C "$SIGLIP2_PHOTOAIKIT_DIR" status --short
git -C "$SIGLIP2_PHOTOAIKIT_DIR" diff -- \
  Package.swift \
  Sources/CoreAICLIPBackend \
  Tools/export_siglip2.py
```

A production conversion must use a reviewed, committed, clean PhotoAIKit
revision. Do not describe an uncommitted development checkout as immutable
release evidence.

### Download the pinned SigLIP 2 snapshot

Download the complete public snapshot into the explicit source directory:

```sh
uvx --from huggingface-hub hf download \
  "$SIGLIP2_REPOSITORY" \
  --revision "$SIGLIP2_REVISION" \
  --local-dir "$SIGLIP2_SOURCE_DIR"
```

The snapshot contains the Safetensors weights, model configuration, image
processor configuration, tokenizer JSON, tokenizer model, tokenizer
configuration, special-token map, model card, and Hugging Face cache evidence.
The current source directory occupies approximately 1.4 GiB.

### Verify the source before conversion

Verify the immutable weight file before running the exporter:

```sh
SIGLIP2_SOURCE="$SIGLIP2_SOURCE_DIR/$SIGLIP2_SOURCE_FILENAME"

shasum -a 256 "$SIGLIP2_SOURCE"
stat -f '%z bytes %N' "$SIGLIP2_SOURCE"

test "$(shasum -a 256 "$SIGLIP2_SOURCE" | cut -d ' ' -f 1)" = \
  "$SIGLIP2_EXPECTED_SHA256"
test "$(stat -f '%z' "$SIGLIP2_SOURCE")" = \
  "$SIGLIP2_EXPECTED_BYTES"
```

The expected output is:

```text
6125cacc01fa93bdc98a0c5101cefcd69b2ed1f8ab4f38d86f4ad5984f5dc863
1500985224 bytes
```

Also verify the tokenizer inputs used by the Swift runtime:

```sh
shasum -a 256 \
  "$SIGLIP2_SOURCE_DIR/tokenizer.json" \
  "$SIGLIP2_SOURCE_DIR/tokenizer.model"
```

The tested snapshot reports:

```text
cb9140fae3ac5122c972d37adf83e1248471a38147ad76f8215c8872c6fd8322  tokenizer.json
61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2  tokenizer.model
```

Stop if a checksum or byte count differs. Do not convert a floating revision or
silently replace the recorded source format.

### Export the Core AI model

Run the PhotoAIKit exporter from the verified local snapshot:

```sh
uv run --python 3.13 \
  --script "$SIGLIP2_PHOTOAIKIT_DIR/Tools/export_siglip2.py" \
  --source-dir "$SIGLIP2_SOURCE_DIR" \
  --output-dir "$SIGLIP2_EXPORT_DIR"
```

Use a new output directory for provenance-controlled conversions. The
`--overwrite` option is convenient for local iteration but must not overwrite
release evidence. The exporter pins its Python/CoreAI dependencies, exports
normalized image and text encoders, copies the tokenizer resources, and writes
`metadata.json`, `PROVENANCE.json`, and a verified runtime-asset fingerprint.

The generated bundle is:

```text
SigLIP2-Base-Patch16-256/
├── metadata.json
├── PROVENANCE.json
├── tokenizer/
│   ├── config.json
│   ├── special_tokens_map.json
│   ├── tokenizer.json
│   ├── tokenizer.model
│   └── tokenizer_config.json
└── siglip2-base-patch16-256_float16_static.aimodel/
```

The tested Core AI bundle occupies approximately 753 MiB. Its runtime asset
fingerprint is:

```text
directory-tree-sha256-v1
191995066342dc0febcddea08ab24bc4a2cdc60efc98c2a53c8380323ca57602
```

The generated `main.mlirb` is `750665474` bytes with SHA-256:

```text
aabefd212c5fae7a01b2a53dc6aa02bcc0f0887bb95fbdd998d817bf140f53e3
```

These output hashes describe the tested conversion. Recompute and record new
values whenever the exporter, dependencies, precision, or source changes.

### Inspect the SigLIP 2 bundle

Set the generated paths and compare the recorded and computed fingerprints:

```sh
SIGLIP2_BUNDLE="$SIGLIP2_EXPORT_DIR/SigLIP2-Base-Patch16-256"
SIGLIP2_RUNTIME_ASSET="$SIGLIP2_BUNDLE/siglip2-base-patch16-256_float16_static.aimodel"

test -f "$SIGLIP2_BUNDLE/metadata.json"
test -f "$SIGLIP2_BUNDLE/PROVENANCE.json"
test -f "$SIGLIP2_BUNDLE/tokenizer/tokenizer.json"
test -d "$SIGLIP2_RUNTIME_ASSET"

plutil -extract family raw -o - "$SIGLIP2_BUNDLE/metadata.json"
plutil -extract architecture raw -o - "$SIGLIP2_BUNDLE/metadata.json"
plutil -extract source_revision raw -o - "$SIGLIP2_BUNDLE/metadata.json"
plutil -extract assets.main raw -o - "$SIGLIP2_BUNDLE/metadata.json"
plutil -extract asset_fingerprints.main.value raw -o - \
  "$SIGLIP2_BUNDLE/metadata.json"

python3 "$SIGLIP2_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$SIGLIP2_RUNTIME_ASSET"
```

The family must be `siglip2`, the architecture must be
`SigLIP2-Base-Patch16-256`, the revision must equal `SIGLIP2_REVISION`, and the
computed fingerprint must equal `asset_fingerprints.main.value`.

### Validate CoreAI parity and RawCullFB search

Generate PyTorch reference embeddings from representative photographs and
English and Norwegian prompts:

```sh
SIGLIP2_REFERENCE='/private/tmp/siglip2-reference.json'

uv run --python 3.13 \
  --script "$SIGLIP2_PHOTOAIKIT_DIR/Tools/generate_clip_reference.py" \
  --model siglip2 \
  --source-dir "$SIGLIP2_SOURCE_DIR" \
  --image /path/to/reference-image-1.jpg \
  --image /path/to/reference-image-2.jpg \
  --text 'puffins portrait' \
  --text 'a portrait photo of a puffin' \
  --text 'rødnebbede lundefugler i flukt' \
  --output "$SIGLIP2_REFERENCE"
```

Run PhotoAIKit's opt-in CoreAI parity test:

```sh
SIGLIP2_COREAI_BUNDLE="$SIGLIP2_BUNDLE" \
SIGLIP2_REFERENCE="$SIGLIP2_REFERENCE" \
swift test \
  --package-path "$SIGLIP2_PHOTOAIKIT_DIR" \
  --filter SigLIP2CoreAIIntegrationTests
```

The tested conversion exceeded `0.995` cosine similarity for text embeddings.
Two end-to-end image embeddings scored `0.9949` and `0.9932` against PyTorch;
the small difference is consistent with PIL versus Core Graphics bilinear
resampling. PhotoAIKit requires greater than `0.99` for image parity.

RawCullFB's development project resolves the sibling PhotoAIKit checkout. Open
`RawCullFB.xcodeproj`, then choose the generated `SIGLIP2_BUNDLE` directory in
**RawCullFB > Settings > CLIP**. It must report
`SigLIP2-Base-Patch16-256`. Select a photo folder and run **Index Selected
Folder** before searching.

SigLIP 2 uses the `siglip2` backend together with the model fingerprint. Its
index is therefore separate from OpenAI CLIP and DataComp CLIP indexes even
though all three may use normalized embeddings. The tested RawCullFB
integration successfully loaded the bundle, indexed two photographs, persisted
the model-specific index, and completed a search for `puffins portrait`.

Before making SigLIP 2 downloadable in production, create its notice catalogue,
packaging selector, archive and manifest entries; record the committed
PhotoAIKit revision and all source, tokenizer, runtime, archive, and licence
hashes; and complete the same release-readiness review required for the other
models.

## Meta SAM 3 model for release

RawCull uses Meta's `facebook/sam3` image-segmentation checkpoint through
PhotoAIKit's Core AI SAM 3 backend. The release input must be the following
exact Hugging Face snapshot and weight file, not a fresh resolution of the
repository's `main` revision:

| Field                                | Required value                                                     |
| ------------------------------------ | ------------------------------------------------------------------ |
| Repository                           | `facebook/sam3`                                                    |
| Revision                             | `3c879f39826c281e95690f02c7821c4de09afae7`                         |
| Source file                          | `model.safetensors`                                                |
| Byte size                            | `3439938512`                                                       |
| SHA-256                              | `6d06f0a5f84e435071fe6603e61d0b4cc7b40e0d39d487cfd4d67d8cc11cc14a` |
| Export task                          | Promptable image segmentation                                      |
| Export precision and reference image | Float16, static batch, `1008 x 1008` pixels                        |

The existing converted asset was created from a local Hugging Face cache at this
revision, but the exporter did not record or cryptographically bind that
snapshot to the converted output. Its old provenance record deliberately has
`source_revision_recorded_by_exporter` set to `null`. The release model must
therefore be a new conversion. Do not copy the cached weight hash into the old
provenance record and treat the old `sam3_float16.aimodel` as verified.

The pinned source is visible in the
[SAM 3 model tree](https://huggingface.co/facebook/sam3/tree/3c879f39826c281e95690f02c7821c4de09afae7).
Unlike DataComp, this repository is gated. Download access requires a signed-in
Hugging Face account whose contact-sharing request has been accepted. That
access is conversion evidence, not permission to publish an ungated mirror. The
separate redistribution decision described under **Licence audit** remains
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

If needed, use `hf auth login` and enter the token only at its protected prompt.
Never place a Hugging Face token in this document, a shell variable, the
terminal transcript, provenance, or the downloadable pack. Keep the account and
dated access evidence private; it can contain personal information.

### Download the pinned source snapshot

Download only the Safetensors checkpoint and the configuration, processor,
tokenizer, licence, and model-card files required for the conversion record. The
exporter does not use the repository's separate `sam3.pt` file:

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
source model `facebook/sam3`, preprocessing `sam3-bounded-image-v1`,
configuration `coreai-sam3-mask-v1`, and main asset `sam3_float16.aimodel`. The
fingerprint printed by `model_fingerprint.py` must equal
`asset_fingerprints.main.value`.

Verify the exported tokenizer:

```sh
shasum -a 256 "$SAM3_BUNDLE/tokenizer/tokenizer.json"
```

The tokenizer SHA-256 for the pinned snapshot is
`6d9109cc838977f3ca94a379eec36aecc7c807e1785cd729660ca2fc0171fb35`. If it
differs, stop and audit the snapshot, dependency resolution, and exporter
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

The package tests validate the resolver, fingerprint, tokenizer layout, and SAM
3 runtime contracts, but do not execute the newly generated model against a
RawCull image. Install a copy of the complete `SAM3` directory at the SAM 3 path
displayed by **RawCull > Settings > AI**. A non-sandboxed development build
normally uses:

```text
/Users/thomas/Library/Application Support/RawCull/Models/SAM3/
```

A sandboxed build normally uses:

```text
/Users/thomas/Library/Containers/no.blogspot.RawCull/Data/Library/Application Support/RawCull/Models/SAM3/
```

Use an empty destination. Move any previous test model to a separately named
backup directory; do not merge old and new bundle contents. Launch RawCull, open
**Settings > AI**, and choose **Check Again**. The SAM 3 model and in-process
review capability must become available without a metadata, tokenizer, or
fingerprint error.

Analyze a representative catalog into burst groups, choose **Deep Review** on a
burst, select the review target, and run the review. Confirm that RawCull
creates subject masks, completes the subject-detail analysis, and presents a
recommendation without a model-load, prompt, or mask-decoding error. Inspect
several masks visually, including a scene with no clear subject. The first load
may take longer while macOS specializes the portable Core AI asset for that Mac.

PhotoAIKit's `ModelBundleResolver` verifies `metadata.json`, the selected asset,
required tokenizer, and runtime fingerprint. `CoreAISAM3Provider` then loads the
tokenizer and Core AI segmentation engine and validates the returned mask
tensors. A successful Python export alone is not sufficient release validation.

### Move the approved SAM 3 candidate into release staging

After validation, copy the complete generated bundle—not the manually installed
test copy—into:

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
   change the production descriptor to `ready` only after the independent legal
   decision confirms that RawCull may deliver the converted derivative without
   reproducing Meta's official gated checkpoint access flow. Technical
   provenance does not clear that release blocker.

The following packaging section starts only after each candidate has passed its
applicable provenance, licence, conversion, and runtime validation gates.

## EfficientSAM model for release

RawCull uses EfficientSAM ViT-Tiny through PhotoAIKit's
`CoreAIEfficientSAMBackend`. EfficientSAM is point-prompted rather than
text-prompted. For unattended Deep Review, RawCull uses a 16-query, one-point
model: the Core AI runtime places a 4 × 4 grid of foreground points and the
backend returns the highest-confidence mask.

The release candidate must be rebuilt from the exact implementation, checkpoint,
and converter revisions below. Do not use the earlier asset made with
`coreai-core 1.0.0b1` and `coreai-torch 0.4.0`. That toolchain can emit
unversioned Core AI source locations and later fail to compile with
`expected AICode versioned location` and `cannot unwrap empty odiec_module_t`.

Do not use a 64-query export on RawCull's 16-GB baseline. EfficientSAM first
emits three 1024 × 1024 candidate masks for every query, so a Q64 graph has a
large fixed GPU and host-memory peak and fails on the baseline M4 with
`kIOGPUCommandBufferCallbackErrorOutOfMemory`. The Q16 configuration below
completed segment-everything inference on that Mac and is the release target.

| Field                      | Required value                                                     |
| -------------------------- | ------------------------------------------------------------------ |
| Implementation repository  | `yformer/EfficientSAM`                                             |
| Implementation revision    | `d525f622e6f640acf5a0fc37c7ca1f243da5bde0`                         |
| Checkpoint repository      | `merve/EfficientSAM`                                               |
| Checkpoint revision        | `38bb0b55425abf62274ba4a8c51249e3d7298b70`                         |
| Source file                | `efficient_sam_vitt.pt`                                            |
| Byte size                  | `40982470`                                                         |
| SHA-256                    | `dff858b19600a46461cbb7de98f796b23a7a888d9f5e34c0b033f7d6eb9e4e6a` |
| Apple converter revision   | `c2a0274af289bf481e2d6fd292a86a5bff038f12`                         |
| Python conversion packages | `coreai-core 1.0.0b2`, `coreai-torch 0.4.1`                        |
| Export configuration       | Float16, static batch, 16 queries, one point per query             |

The source checkpoint is public, but technical access does not by itself make
the converted asset releasable. Complete the Apache 2.0 and Apple BSD 3-Clause
notice catalog and all provenance and archive checks before changing RawCull's
EfficientSAM descriptor to `ready`.

### Create a clean EfficientSAM evidence workspace

Keep the pinned checkpoint, converter, generated lock, conversion output, and
runtime validation tools together in a new evidence directory:

```sh
EFFICIENTSAM_IMPLEMENTATION_REVISION='d525f622e6f640acf5a0fc37c7ca1f243da5bde0'
EFFICIENTSAM_CHECKPOINT_REPOSITORY='merve/EfficientSAM'
EFFICIENTSAM_CHECKPOINT_REVISION='38bb0b55425abf62274ba4a8c51249e3d7298b70'
EFFICIENTSAM_SOURCE_FILENAME='efficient_sam_vitt.pt'
EFFICIENTSAM_EXPECTED_BYTES='40982470'
EFFICIENTSAM_EXPECTED_SHA256='dff858b19600a46461cbb7de98f796b23a7a888d9f5e34c0b033f7d6eb9e4e6a'
EFFICIENTSAM_COREAI_REVISION='c2a0274af289bf481e2d6fd292a86a5bff038f12'
EFFICIENTSAM_PHOTOAIKIT_REVISION='1e2eaccd00947fbadda300e4a617842479cae7b9'

EFFICIENTSAM_EVIDENCE_ROOT="/Users/thomas/ModelAssets/ReleaseEvidence/EfficientSAM/$EFFICIENTSAM_CHECKPOINT_REVISION"
EFFICIENTSAM_SOURCE_DIR="$EFFICIENTSAM_EVIDENCE_ROOT/source"
EFFICIENTSAM_COREAI_DIR="$EFFICIENTSAM_EVIDENCE_ROOT/coreai-models"
EFFICIENTSAM_PHOTOAIKIT_DIR="$EFFICIENTSAM_EVIDENCE_ROOT/PhotoAIKit"
EFFICIENTSAM_EXPORT_DIR="$EFFICIENTSAM_EVIDENCE_ROOT/export"
EFFICIENTSAM_TORCH_HOME="$EFFICIENTSAM_EVIDENCE_ROOT/torch"

mkdir -p \
  "$EFFICIENTSAM_SOURCE_DIR" \
  "$EFFICIENTSAM_EXPORT_DIR" \
  "$EFFICIENTSAM_TORCH_HOME/hub/checkpoints"
```

Use detached, clean checkouts for both the Apple exporter and the PhotoAIKit
validation/fingerprint tools:

```sh
git clone https://github.com/apple/coreai-models.git \
  "$EFFICIENTSAM_COREAI_DIR"
git -C "$EFFICIENTSAM_COREAI_DIR" switch --detach \
  "$EFFICIENTSAM_COREAI_REVISION"

git clone https://github.com/rsyncOSX/PhotoAIKit.git \
  "$EFFICIENTSAM_PHOTOAIKIT_DIR"
git -C "$EFFICIENTSAM_PHOTOAIKIT_DIR" switch --detach \
  "$EFFICIENTSAM_PHOTOAIKIT_REVISION"

test "$(git -C "$EFFICIENTSAM_COREAI_DIR" rev-parse HEAD)" = \
  "$EFFICIENTSAM_COREAI_REVISION"
test "$(git -C "$EFFICIENTSAM_PHOTOAIKIT_DIR" rev-parse HEAD)" = \
  "$EFFICIENTSAM_PHOTOAIKIT_REVISION"
test -z "$(git -C "$EFFICIENTSAM_COREAI_DIR" status --porcelain)"
test -z "$(git -C "$EFFICIENTSAM_PHOTOAIKIT_DIR" status --porcelain)"
```

Revision `c2a0274...` is the first Apple converter revision that changes the
EfficientSAM recipe to `coreai-core 1.0.0b2` and `coreai-torch 0.4.1`. Do not
substitute RawCull's older Swift-package revision for this Python exporter. The
portable `.aimodel` contract is validated separately with the PhotoAIKit
revision that RawCull currently resolves.

### Download and verify the pinned checkpoint

Download the checkpoint by full Hugging Face revision instead of allowing the
exporter's floating `/main/` URL to select the source:

```sh
hf download "$EFFICIENTSAM_CHECKPOINT_REPOSITORY" \
  "$EFFICIENTSAM_SOURCE_FILENAME" \
  --revision "$EFFICIENTSAM_CHECKPOINT_REVISION" \
  --local-dir "$EFFICIENTSAM_SOURCE_DIR"

shasum -a 256 \
  "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME"
stat -f '%z bytes %N' \
  "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME"
```

The output must contain exactly:

```text
dff858b19600a46461cbb7de98f796b23a7a888d9f5e34c0b033f7d6eb9e4e6a
40982470 bytes
```

Make the checks fail closed and put the verified file in an isolated Torch
cache. The exporter checks this cache before its hard-coded floating URL, so the
conversion consumes the verified file without another download:

```sh
test "$(shasum -a 256 "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME" | cut -d ' ' -f 1)" = \
  "$EFFICIENTSAM_EXPECTED_SHA256"
test "$(stat -f '%z' "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME")" = \
  "$EFFICIENTSAM_EXPECTED_BYTES"

ditto \
  "$EFFICIENTSAM_SOURCE_DIR/$EFFICIENTSAM_SOURCE_FILENAME" \
  "$EFFICIENTSAM_TORCH_HOME/hub/checkpoints/$EFFICIENTSAM_SOURCE_FILENAME"

test "$(shasum -a 256 "$EFFICIENTSAM_TORCH_HOME/hub/checkpoints/$EFFICIENTSAM_SOURCE_FILENAME" | cut -d ' ' -f 1)" = \
  "$EFFICIENTSAM_EXPECTED_SHA256"
```

If the size or checksum differs, stop. Do not export a replacement checkpoint, a
cached file with unknown origin, or the current `main` revision.

### Lock the Python source resolution

Apple's PEP 723 script pins the Core AI packages but names the EfficientSAM Git
dependency without a revision. Generate and inspect a script lock before the
conversion so the implementation cannot float between evidence runs:

```sh
cd "$EFFICIENTSAM_COREAI_DIR"

uv lock --script models/efficient-sam/export.py
uv export \
  --script models/efficient-sam/export.py \
  --format requirements.txt \
  --no-hashes \
  --output-file "$EFFICIENTSAM_EVIDENCE_ROOT/python-requirements.txt"

rg 'd525f622e6f640acf5a0fc37c7ca1f243da5bde0' \
  models/efficient-sam/export.py.lock
rg 'coreai-core==1.0.0b2|coreai-torch==0.4.1' \
  "$EFFICIENTSAM_EVIDENCE_ROOT/python-requirements.txt"
git diff --exit-code -- models/efficient-sam/export.py
```

Both revision and package-version checks must succeed. Preserve
`export.py.lock`, `python-requirements.txt`, and their SHA-256 checksums with
the private evidence. The lock file is generated evidence; it is not an upstream
source modification.

### Export only from the verified checkpoint

Run the locked exporter with the isolated Torch cache. The cache file has the
same basename as the exporter's URL, so `load_state_dict_from_url` loads the
verified local checkpoint:

```sh
cd "$EFFICIENTSAM_COREAI_DIR"

TORCH_HOME="$EFFICIENTSAM_TORCH_HOME" \
uv run --locked --script models/efficient-sam/export.py \
  --model efficient_sam_vitt \
  --dtype float16 \
  --num-queries 16 \
  --num-pts 1 \
  --output-dir "$EFFICIENTSAM_EXPORT_DIR"
```

Do not add `--dynamic`; the Core AI runtime does not support EfficientSAM's
dynamic attention reshape at Float16. Do not add `--overwrite` to an evidence
run. If the destination exists, retain it and create a new evidence directory.

Record the toolchain and exact checkouts with the terminal log:

```sh
uv --version
python3 --version
sw_vers
xcodebuild -version
git -C "$EFFICIENTSAM_COREAI_DIR" rev-parse HEAD
git -C "$EFFICIENTSAM_PHOTOAIKIT_DIR" rev-parse HEAD
shasum -a 256 \
  "$EFFICIENTSAM_COREAI_DIR/models/efficient-sam/export.py" \
  "$EFFICIENTSAM_COREAI_DIR/models/efficient-sam/export.py.lock" \
  "$EFFICIENTSAM_EVIDENCE_ROOT/python-requirements.txt"
```

The exporter reserializes the verified state dictionary as
`.build/efficient_sam_weights.pt`. Record its checksum as a conversion
intermediate, but do not confuse it with the source checkpoint checksum: a Torch
reserialization can have different bytes.

The expected generated directory is:

```text
efficient_sam_vitt_float16_static_q16/
├── metadata.json
└── efficient_sam_vitt_float16_static_q16.aimodel/
```

EfficientSAM is point-only and therefore has no tokenizer directory.

### Inspect and fingerprint the EfficientSAM bundle

Set the generated paths and verify the metadata and runtime asset:

```sh
EFFICIENTSAM_BUNDLE="$EFFICIENTSAM_EXPORT_DIR/efficient_sam_vitt_float16_static_q16"
EFFICIENTSAM_RUNTIME_ASSET="$EFFICIENTSAM_BUNDLE/efficient_sam_vitt_float16_static_q16.aimodel"

test -f "$EFFICIENTSAM_BUNDLE/metadata.json"
test -d "$EFFICIENTSAM_RUNTIME_ASSET"
test "$(plutil -extract metadata_version raw -o - "$EFFICIENTSAM_BUNDLE/metadata.json")" = \
  '0.2'
test "$(plutil -extract kind raw -o - "$EFFICIENTSAM_BUNDLE/metadata.json")" = \
  'segmenter'
test "$(plutil -extract assets.main raw -o - "$EFFICIENTSAM_BUNDLE/metadata.json")" = \
  'efficient_sam_vitt_float16_static_q16.aimodel'

python3 "$EFFICIENTSAM_PHOTOAIKIT_DIR/Tools/model_fingerprint.py" \
  "$EFFICIENTSAM_RUNTIME_ASSET"
find "$EFFICIENTSAM_RUNTIME_ASSET" -type f -name main.mlirb \
  -exec shasum -a 256 {} \;
shasum -a 256 \
  "$EFFICIENTSAM_COREAI_DIR/.build/efficient_sam_weights.pt"
```

Record the runtime fingerprint, `main.mlirb` checksum, and reserialized-weight
checksum. These values belong to the new conversion and must not be copied from
the asset produced by the older, incompatible converter.

### Validate EfficientSAM with PhotoAIKit and RawCull

Run the tests from the exact PhotoAIKit checkout used for validation:

```sh
swift test --package-path "$EFFICIENTSAM_PHOTOAIKIT_DIR"
```

Install a copy of the complete generated bundle at the EfficientSAM path shown
by **RawCull > Settings > AI**. A non-sandboxed build normally uses:

```text
/Users/thomas/Library/Application Support/RawCull/Models/EfficientSAM/
```

A sandboxed build normally uses:

```text
/Users/thomas/Library/Containers/no.blogspot.RawCull/Data/Library/Application Support/RawCull/Models/EfficientSAM/
```

Use an empty destination. Move any earlier test model to a separately named
backup; do not merge bundle contents. Launch RawCull, choose **Check Again**,
and verify that **EfficientSAM model** is available. Select **EfficientSAM** as
the Deep Review segmentation model and run Deep Review on representative burst
groups. Confirm that the model compiles, produces masks, completes subject
detail analysis, and does not report a versioned-location or mask-decoding
error. Inspect several masks visually, including an off-center subject and a
scene with no clear subject.

EfficientSAM does not interpret target names such as person, bird, or face.
Those values remain in the common diagnostics and cache keys, while this backend
uses the same 4 × 4 point grid for every target. Use SAM 3 when text-guided
target semantics are required.

A successful Python export is not sufficient validation. PhotoAIKit must resolve
the bundle and asset, and RawCull must compile and execute the portable Core AI
program on the supported macOS/Xcode toolchain.

### Move the approved EfficientSAM candidate into release staging

After validation, copy the complete generated bundle—not the manually installed
test copy—into:

```text
/Users/thomas/ModelAssets/Release/Models/EfficientSAM/
```

Then complete the release records:

1. Create or update `ModelAssets/Notices/EfficientSAM/PROVENANCE.json` with the
   implementation repository and revision, checkpoint repository and revision,
   source filename, byte size and SHA-256, Apple converter commit, exporter and
   lock checksums, resolved dependency versions, conversion command,
   reserialized-weight checksum, runtime filename and fingerprint, and
   `main.mlirb` checksum.
2. Include the complete EfficientSAM Apache License 2.0 and Apple's applicable
   `coreai-models` BSD 3-Clause notice. Record and review any additional notices
   reported by the locked dependency set.
3. Add or update `Packaging/efficient-sam.json` so it selects only
   `metadata.json`, the runtime `.aimodel`, and `Notices/EfficientSAM`. Do not
   select a failed older asset, compiler intermediates, cache files, or private
   evidence.
4. Build and inspect `efficient-sam.aar`, then record its byte size and SHA-256
   in the provenance record and RawCull catalogue.
5. Use asset-pack ID `no.blogspot.RawCull.models.efficient-sam` and logical
   destination `Models/EfficientSAM`.
6. Keep the production catalogue entry blocked until the licence, provenance,
   runtime, notice, archive, and download checks have all passed. Do not treat
   successful conversion as redistribution approval.

## Preparing the downloadable resources

### Use an asset-pack archive, not a ZIP

Do not ZIP model directories manually. Xcode supplies `ba-package`, which
creates a Managed Background Assets archive with the required `.aar` extension.
The AAR is an opaque framework artifact, not a ZIP that RawCull opens. Managed
Background Assets downloads, verifies, installs, and exposes its selected files.

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
Keep its complete redistribution notice, immutable upstream revision, conversion
recipe and tool versions, source checksums, and final checksums. Packaging does
not make an unverified checkpoint safe to redistribute.

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
  "platforms": ["macOS"]
}
```

The four manifests select these runtime models and notice catalogs:

| Manifest             | Runtime model directory                                                                | Notice catalog          |
| -------------------- | -------------------------------------------------------------------------------------- | ----------------------- |
| `clip-datacomp.json` | `Models/CLIP-DataComp/ViT-B-32-256-open_clip_model.safetensors_float16_static.aimodel` | `Notices/CLIP-DataComp` |
| `clip-openai.json`   | `Models/CLIP-OpenAI/clip-vit-base-patch32_float16_static.aimodel`                      | `Notices/CLIP-OpenAI`   |
| `efficient-sam.json` | `Models/EfficientSAM/efficient_sam_vitt_float16_static_q16.aimodel`                    | `Notices/EfficientSAM`  |
| `sam3.json`          | `Models/SAM3/sam3_float16.aimodel`                                                     | `Notices/SAM3`          |

Each manifest also selects its model's `metadata.json` file. The CLIP and SAM 3
manifests additionally select their `tokenizer` directory; EfficientSAM has no
tokenizer. Do not replace these selectors with the broader model root. The broad
selector also packages `_source.aimodel`, `.aimodelc`, or other conversion
outputs that are not required at runtime.

Selector paths are relative. The tool resolves them against its current working
directory, includes directory contents recursively, and preserves their logical
paths. Run it from the release staging root.

The checked-in `ModelAssets/manifest.template.json` is only a four-pack design
skeleton. It is **not directly accepted by `ba-package`**. The tool expects one
top-level `assetPackID` per packaging manifest and a relative path for every
selector. Generate a fresh starting point with `xcrun ba-package template` after
a toolchain update, then reapply and review the explicit selectors.

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

The current published DataComp archive and the historical unpublished packs
have these values:

| Archive             |         Bytes | SHA-256                                                            |
| ------------------- | ------------: | ------------------------------------------------------------------ |
| `clip-datacomp.aar` |   282,967,394 | `fae9cab286e0e3605d27de01865122f177d515984b152610005cc793012bd3aa` |
| `clip-openai.aar`   |   282,829,540 | `24e403f2f58cdea5765fb105d10fd37a57d4e53f5830e9b7248053e0229712dc` |
| `efficient-sam.aar` | Not generated | Not generated                                                      |
| `sam3.aar`          | 1,542,689,135 | `f207db7d83fdb90baff6f32e894935f9267e3ebdc276358011d41bd36d5cd4df` |

Compared with the broad-directory archives, the two CLIP packs are about half
the previous size and SAM 3 is about one third. This is consistent with the
source and intermediate model representations being excluded.

The output path must end in `.aar`. Treat a published archive as immutable. Keep
the manifests, checksums, provenance, conversion logs, and exact
Xcode/`ba-package` version as release evidence. Copy archive SHA-256 and byte
sizes into the release record and matching catalogue metadata before changing a
descriptor to `.ready`.

### Create the self-hosted download manifest

The packaging manifests describe archive contents. The **download manifest** is
a different generated JSON file served to Macs. It lists versions, sizes,
policies, and download URLs.

```sh
MODEL_RELEASE_TAG='v1'
MODEL_RELEASE_ROOT='/Users/thomas/ModelsAAR/Output-lean'
MODEL_DOWNLOAD_BASE="https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/$MODEL_RELEASE_TAG/"

xcrun ba-package download-manifest create \
  "$MODEL_RELEASE_ROOT/clip-datacomp.aar" \
  --asset-pack-versions 1 \
  --macos \
  --download-base-url "$MODEL_DOWNLOAD_BASE" \
  --output-path "$MODEL_RELEASE_ROOT/manifest.generated.json"
```

The base URL is not an individual archive URL. The tool appends each asset-pack
ID, not the local AAR filename. The release asset is named
`clip-datacomp.aar`, so replace the generated pack URL with that exact GitHub
Release URL while preserving every other generated field:

```sh
DATACOMP_ARCHIVE_URL="$MODEL_DOWNLOAD_BASE"'clip-datacomp.aar'

jq --arg archiveURL "$DATACOMP_ARCHIVE_URL" '
  (.assetPacks[] |
    select(.id == "no.blogspot.RawCull.models.clip-datacomp") |
    .url) = $archiveURL
' "$MODEL_RELEASE_ROOT/manifest.generated.json" \
  > "$MODEL_RELEASE_ROOT/manifest.json"
```

Do not use `https://github.com` by itself as `--download-base-url`; that creates
the invalid URL `https://github.com/no.blogspot.RawCull.models.clip-datacomp`.
Alternatively, keep the generated URL unchanged and upload a release copy named
exactly `no.blogspot.RawCull.models.clip-datacomp`. Patching the URL is clearer
when the release asset keeps its `.aar` extension.

Validate the finished manifest before publishing it:

```sh
jq -e '
  .assetPacks | length == 1 and
  .[0].id == "no.blogspot.RawCull.models.clip-datacomp" and
  .[0].version == 1 and
  .[0].downloadSize == 282967394 and
  .[0].url == "https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/clip-datacomp.aar"
' "$MODEL_RELEASE_ROOT/manifest.json"

shasum -a 256 \
  "$MODEL_RELEASE_ROOT/clip-datacomp.aar" \
  "$MODEL_RELEASE_ROOT/manifest.json"
```

The archive SHA-256 must be
`fae9cab286e0e3605d27de01865122f177d515984b152610005cc793012bd3aa`.
The manifest checksum changes whenever its JSON formatting or fields change and
is recorded as release evidence rather than in RawCull's model catalogue.

### Publish the archive and manifest

Install and authenticate GitHub CLI once if necessary:

```sh
brew install gh
gh auth login
```

Create the release if it does not exist, then upload the archive first:

```sh
gh release view "$MODEL_RELEASE_TAG" \
  --repo rsyncOSX/RawCull-AI-Models >/dev/null 2>&1 || \
gh release create "$MODEL_RELEASE_TAG" \
  --repo rsyncOSX/RawCull-AI-Models \
  --title "RawCull AI Models $MODEL_RELEASE_TAG"

gh release upload "$MODEL_RELEASE_TAG" \
  "$MODEL_RELEASE_ROOT/clip-datacomp.aar" \
  --repo rsyncOSX/RawCull-AI-Models \
  --clobber
```

Upload the validated manifest last so clients never discover a missing archive:

```sh
gh release upload "$MODEL_RELEASE_TAG" \
  "$MODEL_RELEASE_ROOT/manifest.json" \
  --repo rsyncOSX/RawCull-AI-Models \
  --clobber
```

Verify both public downloads, following GitHub's redirects:

```sh
curl --fail --location --output /tmp/rawcull-manifest.json \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/manifest.json

jq -e '.assetPacks[0].url | endswith("/v1/clip-datacomp.aar")' \
  /tmp/rawcull-manifest.json

curl --fail --location --output /tmp/clip-datacomp.aar \
  https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v1/clip-datacomp.aar

test "$(shasum -a 256 /tmp/clip-datacomp.aar | cut -d ' ' -f 1)" = \
  'fae9cab286e0e3605d27de01865122f177d515984b152610005cc793012bd3aa'
```

Keep `.aar` files out of Git history. For subsequent model versions, publish a
new release tag, increase the manifest's asset-pack version, pin its archive URL
to the new tag, and replace the latest release's `manifest.json`. RawCull asks
Managed Background Assets for the latest declared pack version.

Both `BAManifestURL` and RawCull's self-hosted service source identify the
manifest, not the AAR. For Apple hosting, generate the same AAR but omit the
self-hosted download manifest and upload the pack through App Store Connect.

## What happens when the user selects Download

1. `startModelDownload` accepts only a ready or retryable failed row and
   prevents two tasks for the same model.
2. The row immediately changes to `downloading(progress: 0)` and shows Cancel.
3. The coordinator resolves the stable model descriptor and rechecks release
   readiness so UI state cannot bypass distribution policy.
4. If explicit acceptance is required, it loads `ModelLicenceAcceptances.json`
   and requires a record matching the current model, licence version, and
   licence-text checksum.
5. The service rejects an unconfigured source before requesting a manifest.
6. `AssetPackManager.shared.manifest` obtains the hosting-mode manifest. A
   self-hosted build uses `BAManifestURL`; an Apple-hosted build uses the store
   downloader extension and Apple's asset metadata.
7. RawCull looks up the exact asset-pack ID. It never guesses a URL or accepts a
   similarly named pack.
8. RawCull listens to asynchronous `statusUpdates`. Progress is delivered to the
   main actor and clamped to zero through one.
9. `ensureLocalAvailability(of:requireLatestVersion: true)` asks Managed
   Background Assets to download and install the latest selected AAR in managed
   storage.
10. RawCull reports 100 percent, resolves the catalogue's logical model path,
    and verifies that it is a directory. Incorrect archive organization becomes
    `downloadedModelNotFound`.
11. The row changes to `validating`; the URL becomes a candidate for the
    matching CLIP, EfficientSAM, or SAM 3 resource manager.
12. PhotoAIKit validates `metadata.json`, the chosen `.aimodel` or `.aimodelc`,
    declared resources, and the runtime contract. Only then does RawCull
    construct a provider and refresh feature capabilities.
13. The next snapshot reports the pack installed. The feature is active only
    when validation and provider creation also succeeded.

Cancel stops RawCull's task and status listener. RawCull does not assume the
framework removed partial data; it requests a new authoritative snapshot.
Failures become `failed(message:)`, and Retry repeats the guarded sequence.
Remove asks the framework to remove the asset-pack ID, clears its managed
candidate URL, and refreshes capabilities without deleting manually installed
models.
