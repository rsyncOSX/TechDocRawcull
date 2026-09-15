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

Production currently uses model release `v3`. This runbook describes advancing
the existing DataComp CLIP and Meta SAM 3 packs to a future release such as
`v4`; it does not publish or enable that release by itself.

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

## 2. Generate The Manifest

Use `ModelAssets/manifest.template.json` only as developer-side selector input.
Change it when adding/removing a model or changing an ID, source, destination,
platform, or download policy. Let Apple's tooling generate the supported
download-manifest fields.

For a `v4` release, the final manifest should point to files such as:

```text
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v4/no.blogspot.RawCull.models.clip-datacomp
https://github.com/rsyncOSX/RawCull-AI-Models/releases/download/v4/no.blogspot.RawCull.models.sam3
```

Each entry needs the stable ID, intended pack version, final archive byte size,
on-demand policy, platform, and third-party hosted URL. Do not invent repository
provenance fields such as `archive_sha256` inside Apple's manifest schema.

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
