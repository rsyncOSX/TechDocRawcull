+++
author = "Thomas Evensen"
title = "Saved Files"
date = "2026-04-09"
weight = 1
tags = ["saved files"]
categories = ["technical details"]
mermaid = true
+++

# SavedFiles Architecture

This document describes how `SavedFiles` are created, read, and updated across the RawCull codebase, and where the source of truth lives.

---

## Data Model

```
SavedFiles
├── id: UUID
├── catalog: URL?          — directory path scanned (per-catalog grouping key)
├── dateStart: String?     — timestamp of when cataloging started
└── filerecords: [FileRecord]?
         ├── id: UUID
         ├── fileName: String?    — ARW file name
         ├── dateTagged: String?  — when the file was tagged
         ├── dateCopied: String?  — when the file was copied (unused)
         └── rating: Int?         — 1-5 star, -1 rejected, 0 keeper
```

**Disk location:** `~/Documents/savedfiles.json`

---

## Source of Truth

`CullingModel.savedFiles: [SavedFiles]` is the single in-memory source of truth.
It is an `@Observable @MainActor` property — all reads and mutations happen on the main thread.

`RawCullViewModel` maintains two derived caches rebuilt after every mutation:
- `ratingCache: [String: Int]` — O(1) rating lookups by filename
- `taggedNamesCache: Set<String>` — O(1) tagged-file membership checks

---

## Lifecycle Diagram

```mermaid
flowchart TD
    subgraph Disk["Disk  ~/Documents/savedfiles.json"]
        JSON[(savedfiles.json)]
    end

    subgraph Persistence["Persistence Layer  Model/JSON/"]
        R["ReadSavedFilesJSON\n@MainActor\nreadjsonfilesavedfiles()"]
        W["WriteSavedFilesJSON\nactor\ninit(_ savedfiles:) async"]
    end

    subgraph StateHub["Source of Truth  Model/ViewModels/"]
        CM["CullingModel\n@Observable @MainActor\n\nsavedFiles: [SavedFiles]"]
        RC["RawCullViewModel\n\nratingCache: [String:Int]\ntaggedNamesCache: Set&lt;String&gt;"]
    end

    subgraph Mutations["Mutation Sites"]
        T["CullingModel\ntoggleSelectionSavedFiles()"]
        RT["RawCullViewModel+Culling\nupdateRating()"]
        AS["RawCullViewModel+Culling\napplySharpnessThreshold()"]
        RS1["CullingModel\nresetSavedFiles()"]
        RS2["RawCullMainView  alert confirm"]
        RS3["SavedFilesView  reset confirm"]
    end

    subgraph Load["Catalog Load  RawCullViewModel+Catalog.swift:46"]
        LD["cullingModel.loadSavedFiles()"]
    end

    subgraph ReadSites["Read / Display Sites"]
        TI["TaggedPhotoItemView\nrating color + tagged bg"]
        TG["TaggedPhotoHorisontalGridView\ntagged files ≥ rating 2"]
        TR["FileTableRowView\nmarked toggle"]
        TB["SharedMainToolbarContent\nenable grid window"]
        SF["SavedFilesView\ndisplay all catalogs"]
    end

    %% Load path
    LD -->|reads| R
    R -->|reads| JSON
    R -->|populates| CM

    %% Rebuild caches after load
    CM -->|rebuildRatingCache| RC

    %% Mutation paths — all write back to disk
    T -->|mutates| CM
    RT -->|mutates| CM
    AS -->|mutates| CM
    RS1 -->|mutates| CM
    RS2 -->|calls resetSavedFiles| RS1
    RS3 -->|calls resetSavedFiles| RS1

    CM -->|"await WriteSavedFilesJSON()"| W
    W -->|atomic write| JSON

    %% Cache rebuild on every mutation
    RT -->|rebuildRatingCache| RC
    AS -->|rebuildRatingCache| RC

    %% Read paths
    CM -->|savedFiles| TG
    CM -->|savedFiles| SF
    RC -->|ratingCache / taggedNamesCache| TI
    RC -->|taggedNamesCache| TR
    RC -->|taggedNamesCache| TB
```

---

## Write Operations

Every write passes the full `cullingModel.savedFiles` array to `WriteSavedFilesJSON` (actor, atomic write).

| Trigger | Location | What changes |
|---------|----------|--------------|
| User tags / untags a file | `CullingModel.toggleSelectionSavedFiles()` | Adds or removes a `FileRecord` |
| User rates a file (1-5 / reject) | `RawCullViewModel+Culling.updateRating()` | Updates `FileRecord.rating` |
| User applies sharpness threshold | `RawCullViewModel+Culling.applySharpnessThreshold()` | Bulk-updates ratings below threshold |
| User resets current catalog | `CullingModel.resetSavedFiles()` | Clears `filerecords` for the catalog |
| User confirms reset alert (main view) | `RawCullMainView` (alert) | Calls `resetSavedFiles()` |
| User confirms reset (SavedFilesView) | `SavedFilesView` | Calls `resetSavedFiles()` |

---

## Read Operations

All in-memory reads hit `CullingModel.savedFiles` or the derived caches — no disk I/O after initial load.

| Purpose | Location |
|---------|----------|
| Build rating / tagged caches | `RawCullViewModel.rebuildRatingCache()` |
| Is file tagged? | `CullingModel.isTagged()` |
| Count tagged files | `CullingModel.countSelectedFiles()` |
| Rating color in thumbnail | `TaggedPhotoItemView` |
| Tagged-file grid display | `TaggedPhotoHorisontalGridView` |
| Marked toggle in file table | `FileTableRowView.marktoggle()` |
| Enable grid window button | `SharedMainToolbarContent` |
| Management UI | `SavedFilesView` |

---

## Key Design Notes

- **Per-catalog grouping:** `SavedFiles` is keyed by `catalog: URL`. Each scanned directory gets its own entry; `filerecords` holds only the files for that catalog.
- **Atomic writes:** `WriteSavedFilesJSON` uses the `.atomic` write option to prevent JSON corruption on crash.
- **Cache invalidation:** `ratingCache` and `taggedNamesCache` are always rebuilt immediately after any mutation — there is no deferred or lazy invalidation.
- **Single load point:** `loadSavedFiles()` is called exactly once per catalog selection, in `RawCullViewModel+Catalog.swift:46`, after the file scan completes.

 
