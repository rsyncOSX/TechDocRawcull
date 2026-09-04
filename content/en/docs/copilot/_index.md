+++
author = "Thomas Evensen"
title = "RawCull Architecture"
linkTitle = "Copilot Catalog"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "Architecture overview and guided documentation catalog for the RawCull macOS application."
tags = ["rawcull", "architecture", "swift", "swiftui"]
categories = ["technical details"]
weight = 70
+++

# RawCull — Architecture Overview & Documentation Index

RawCull is a macOS app for **culling RAW photos**: scanning a folder of camera
RAW files (Sony ARW today), showing fast previews, letting the photographer
rate/reject/flag images, grouping near-duplicate "burst" shots with
on-device AI, and finally exporting the keepers to a destination folder.

This document is the **entry point and index** for the whole `Docs/`
catalog. Read it first, then follow the links below — in the "Reading
order" section, and repeated here for quick reference — for deep dives into
each subsystem. All docs assume you already know Swift and SwiftUI, but
nothing about this codebase.

## Documentation catalog

| # | Document | Covers |
|---|---|---|
| 00 | [Overview](./) *(this file)* | App summary, source map, composition root, glossary |
| 01 | [Concurrency-Architecture.md](01-concurrency-architecture/) | Actors, `TaskGroup` backpressure, Sendable rules, coalescing |
| 02 | [Image-Pipeline-and-Caching.md](02-image-pipeline-and-caching/) | Scan → decode → thumbnail → cache pipeline |
| 03 | [Culling-and-Persistence.md](03-culling-and-persistence/) | Ratings model, debounced save, catalog switching |
| 04 | [Export-Copy-Pipeline.md](04-export-copy-pipeline/) | The rsync-backed export/copy step |
| 05 | [Intelligence-AI-Subsystem.md](05-intelligence-ai-subsystem/) | On-device AI: similarity, semantic search, deep review |
| — | [Intelligence Runtime](runtime/) | Deep dive: how the Intelligence runtime is built, reconfigured, and extended |
| 06 | [SwiftUI-View-Layer.md](06-swiftui-view-layer/) | Navigation, state-management idioms, the grid view |
| 07 | [Settings-and-Configuration.md](07-settings-and-configuration/) | User preferences, AI settings, memory monitor |
| — | [Features and Roadmap](features/) | RawCull vs. other culling apps, and the post-3.2.0 roadmap |
| — | [Known Issues](issues/) | Code-review findings, with severities |

> **Naming note:** the project (and this worktree's branch) carries the name
> "rsyncosx" because it evolved from the author's earlier *RsyncOSX* rsync
> GUI. RawCull is **not** a two-way sync tool — it's a one-way RAW photo
> culling/export app that happens to reuse rsync (and several helper
> packages) from that project for its final copy step. See
> [Export and Copy Pipeline](04-export-copy-pipeline/) for the full story
> and a table of legacy names you'll bump into while reading the code.

## Where the source lives

```
RawCull/
├── Main/          RawCullApp (the @main entry point), RawCullMainView, FileItem typealias
├── Actors/         The file-scanning / thumbnail / disk-cache pipeline (all `actor`s)
├── Model/
│   ├── ViewModels/      RawCullViewModel (central state) + its feature extensions,
│   │                    CullingModel, SettingsViewModel, MemoryViewModel, GridThumbnailViewModel
│   ├── Cache/           Cache config/keys shared by the Actors layer
│   ├── Handlers/        Small callback-bundle structs passed into background workers
│   ├── ParametersRsync/ Copy/export configuration + rsync argument building
│   └── JSON/            Codable read/write helpers for on-disk persistence
├── Intelligence/    The on-device AI subsystem (similarity, semantic search,
│                    burst analysis, deep review, model management) — see its own doc
├── Views/           SwiftUI view layer, one folder per feature area
└── Extensions/      Small Foundation/Thread extensions
```

`RawCullCore` (types like `RawCullFileItem`/`FileItem`, `RawCullSourceCatalog`,
`ExifMetadata`, burst grouping/ranking algorithms) and the AI-facing
`PhotoAIContracts`/`PhotoAnalysisKit` packages, plus `RawParserKit` (RAW
decoding) and the rsync helper packages (`RsyncArguments`,
`RsyncProcessStreaming`, `ParseRsyncOutput`, `DecodeEncodeGeneric`), are all
**separate Swift packages** pulled in via SPM from the `rsyncOSX` GitHub org.
They are out of scope for this documentation — treat them as RawCull's
external boundary and consult their own repos if you need their internals.

## The composition root

The app has exactly one place where its two long-lived object graphs are
built: `RawCullApplicationState.live()` in
`RawCull/Intelligence/Composition/RawCullIntelligenceRuntime.swift`.

```swift
@MainActor
struct RawCullApplicationState {
    let intelligenceRuntime: RawCullIntelligenceRuntime
    let viewModel: RawCullViewModel

    static func live() -> RawCullApplicationState { make(integration: RawCullAIIntegration()) }
    static func make(integration:, similarityArtifactStore:, userDefaults:, ...) -> RawCullApplicationState { ... }
}
```

`RawCullApp.init()` calls `RawCullApplicationState.live()` once and stores
`viewModel` and `intelligenceRuntime` in `@State`. Everything downstream
(views, feature controllers, background workers) either receives these by
parameter or reads them via `.environment(...)`. Nothing else in the app
constructs a second `RawCullViewModel` or a second AI runtime — this matters
because several assertions in `make(...)` (`assert(viewModel.similarityFeature
=== intelligenceRuntime.similarityFeature)`, etc.) exist specifically to catch
an accidental second instance during refactors.

`RawCullApp` (`RawCull/Main/RawCullApp.swift`) declares three `Scene`s:

- **`"main-window"`** — hosts `RawCullMainView`, the whole photo-browsing UI.
- **`Settings`** — hosts `SettingsView`, bound to `intelligenceRuntime.settingsModel`.
- **`"about-window"`** — a simple about box.

An `NSApplicationDelegateAdaptor`-backed `AppDelegate` intercepts app
termination to flush pending culling-state writes
(`viewModel.cullingModel.flushPersistence()`) before actually quitting, and to
release any active security-scoped folder access.

## The central view model

`RawCullViewModel` (`Model/ViewModels/RawCullViewModel.swift`) is a
`@MainActor @Observable final class` — the single source of truth for almost
all UI-visible state: the current file list, selection, view mode (loupe /
grid / similarity grid / rated grid / comparison grid), zoom-overlay state,
rating filter, and references to the "stable feature boundaries" it doesn't
own outright: `similarityFeature`, `semanticSearchFeature`,
`deepAIReviewController`, `burstAnalysisCoordinator`, plus its own
`cullingModel` and `sharpnessModel`.

It's split across one main file and several `RawCullViewModel+*.swift`
extensions by concern (`+Culling`, `+Catalog`, `+Sharpness`, `+Similarity`,
`+Thumbnails`, `+BurstGrouping`) — a common Swift pattern for keeping a large
`@Observable` model's *storage* in one place while spreading its *behavior*
across topic-focused files.

## Reading order

1. [Concurrency Architecture](01-concurrency-architecture/) — actors,
   `TaskGroup`, cancellation, Sendable rules. Read this early; almost every
   other subsystem leans on these patterns.
2. [Image Pipeline and Caching](02-image-pipeline-and-caching/) — scan
   → decode → thumbnail → cache, from folder selection to pixels on screen.
3. [Culling and Persistence](03-culling-and-persistence/) — how
   ratings/rejects are modeled, filtered, and saved.
4. [Export and Copy Pipeline](04-export-copy-pipeline/) — how the "keeper"
   files get copied out via rsync.
5. [Intelligence and AI Subsystem](05-intelligence-ai-subsystem/) — the
   on-device ML features: burst grouping, semantic search, deep review.
   Optionally follow with [Intelligence Runtime](runtime/) for a deep dive on how
   the runtime is built, reconfigured live, and safely extended.
6. [SwiftUI View Layer](06-swiftui-view-layer/) — the view hierarchy
   and SwiftUI idioms used throughout.
7. [Settings and Configuration](07-settings-and-configuration/) — user
   preferences, AI model management/licensing, memory monitoring.
8. [Features and Roadmap](features/) — how RawCull compares to other culling apps
   (Photo Mechanic, Aftershoot, Narrative Select, Lightroom Classic, and
   others), and the principles guiding how it should evolve after 3.2.0.
   Product-level, not implementation detail — a good read once you
   understand the architecture and want the "why this app, why this shape"
   context.
9. [Known Issues](issues/) — known issues found during a code-review pass,
   with severities. Read after the above once you have the architectural
   context to evaluate them.

## Glossary

| Term | Meaning |
|---|---|
| **Catalog** / `ARWSourceCatalog` | A user-selected source folder of RAW files, plus its bookmark/metadata. Culling decisions are keyed per catalog. |
| **Culling** | The act of rating (-1 reject, 0 keeper, 2–5 stars) or flagging RAW files so a subset can be exported. |
| **Burst** | A group of near-duplicate frames (e.g. continuous shooting) detected via similarity scoring, presented together so the user picks the best one. |
| **Deep Review** | An optional, heavier AI pass over a burst group (subject segmentation + focus scoring) that recommends a winner. |
| **Loupe** | The single-photo detail view mode (as opposed to a grid of thumbnails). |
| **FileItem** | `typealias` for `RawCullCore.RawCullFileItem` — the value type representing one scanned RAW file (name, URL, metadata). |
