+++
author = "Thomas Evensen"
title = "AI Model Download Service"
linkTitle = "AI Model Downloads"
date = "2026-07-31"
description = "Architecture, storage, activation, and operation of RawCull AI model downloads using self-hosted or Apple-hosted Managed Background Assets."
tags = ["ai", "models", "downloads", "background-assets", "self-hosting", "apple-hosting"]
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

For an Apple-hosted configuration:

1. Upload approved packs in App Store Connect.
2. Add `RAWCULL_APPLE_HOSTED_MODEL_ASSETS` to the downloader extension.
3. Set `BAUsesAppleHosting` to `YES`.
4. Remove `BAManifestURL` from the app target.
5. Archive and test the App Store configuration.

Do not enable both hosting configurations in one product.

## Licence audit

The audit source was `~/Downloads/ailicences.md` and its
`THIRD-PARTY-NOTICES` directory.

- OpenCLIP/DataComp: a complete MIT notice is bundled, but release remains
  blocked until the exact source-checkpoint revision and source-file checksums
  are cryptographically recorded with the converted archive.
- OpenAI CLIP: the bundled MIT notice covers the source/tokenizer. Release
  remains blocked until the exact weights licence, immutable revision, and
  source checksums are verified.
- Meta SAM 3: the Downloads catalogue describes a gated, non-MIT licence, but
  no complete licence document was present. Release remains blocked until that
  text is packaged and ungated redistribution is confirmed compatible with
  Meta's licence and official access conditions.

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
| `RawCullAIIntegration` | Validates installed bundles and creates the CLIP or SAM 3 runtime provider. |

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
| Meta SAM 3 | `no.blogspot.RawCull.models.sam3` | `Models/SAM3` |

`ModelAssets/manifest.template.json` is a developer input, not the deployable
manifest. Release-time Managed Background Assets tools generate the archives
and production manifest. Each pack should include the converted model plus its
applicable licence text, immutable upstream revision, source and archive
checksums, and conversion metadata.

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

These examples use `ba-package 1.2`. Recheck its help after changing Xcode
because its manifest schema and command interface are tool-version specific.

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
│   └── SAM3/
│       ├── metadata.json
│       └── … .aimodel or .aimodelc plus declared resources …
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

Validate each model directory with the same PhotoAIKit rules used at runtime.
Keep its complete redistribution notice, immutable upstream revision,
conversion recipe and tool versions, source checksums, and final checksums.
Packaging does not make an unverified checkpoint safe to redistribute.

### Create one packaging manifest per pack

With `ba-package 1.2`, one invocation creates one pack. For example,
`Packaging/clip-openai.json` is:

```json
{
  "assetPackID": "no.blogspot.RawCull.models.clip-openai",
  "downloadPolicy": {
    "onDemand": {}
  },
  "fileSelectors": [
    { "directory": "Models/CLIP-OpenAI" },
    { "directory": "Notices/CLIP-OpenAI" }
  ],
  "platforms": [ "macOS" ]
}
```

Create equivalent manifests for these pairs:

| Manifest | Asset-pack ID | Model directory |
| --- | --- | --- |
| `clip-datacomp.json` | `no.blogspot.RawCull.models.clip-datacomp` | `Models/CLIP-DataComp` |
| `clip-openai.json` | `no.blogspot.RawCull.models.clip-openai` | `Models/CLIP-OpenAI` |
| `sam3.json` | `no.blogspot.RawCull.models.sam3` | `Models/SAM3` |

Selector paths are relative. The tool resolves them against its current working
directory, includes directory contents recursively, and preserves their
logical paths. Run it from the release staging root.

The checked-in `ModelAssets/manifest.template.json` is only a three-pack
design skeleton. It is **not directly accepted by `ba-package 1.2`**. That
version expects one top-level `assetPackID` per packaging manifest and a
relative string for each directory selector. Generate a fresh starting point
with `xcrun ba-package template` before a release.

### Generate and record the AAR files

```sh
cd /path/to/ModelAssets/Release

xcrun ba-package package Packaging/clip-datacomp.json \
  --output-path Output/clip-datacomp.aar
xcrun ba-package package Packaging/clip-openai.json \
  --output-path Output/clip-openai.aar
xcrun ba-package package Packaging/sam3.json \
  --output-path Output/sam3.aar

shasum -a 256 Output/*.aar
stat -f '%N %z bytes' Output/*.aar
```

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
  Output/clip-datacomp.aar \
  Output/clip-openai.aar \
  Output/sam3.aar \
  --asset-pack-versions 1 1 1 \
  --macos \
  --download-base-url https://downloads.example.com/rawcull/models/packs/ \
  --output-path Output/manifest.json
```

The base URL is not an individual archive URL. The tool appends each
asset-pack ID. Inspect the generated JSON and upload each AAR to the exact URL
it records. With this example, OpenAI CLIP normally resolves to:

```text
https://downloads.example.com/rawcull/models/packs/no.blogspot.RawCull.models.clip-openai
```

The remote key need not show `.aar` when the generated URL omits it; the local
input to `ba-package` still requires that extension. Ensure every URL returns
the archive, not an HTML login, redirect, or error page.

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
    matching CLIP or SAM 3 resource manager.
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
