+++
author = "Thomas Evensen"
title = "Settings and Configuration"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "RawCull preferences, AI configuration, settings persistence, and memory monitoring."
tags = ["rawcull", "settings", "configuration", "memory"]
categories = ["technical details"]
weight = 70
+++

# Settings and Configuration

RawCull's user-configurable state splits into two independently-persisted
models: general app preferences (`SettingsViewModel`) and AI-feature
preferences (`RawCullAISettingsModel`, covered in depth in
[Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/)). This
doc covers the general settings model, its persistence, and the memory
monitor shown alongside it.

## `SettingsViewModel`

`Model/ViewModels/SettingsViewModel.swift` is an `@MainActor @Observable`
class exposing a flat list of plain stored properties for every tunable in
the app — no nested config struct, so SwiftUI settings controls can bind to
each property directly (`Bindable(settingsViewModel).thumbnailSizeGrid`,
etc.). It groups into four areas via `// MARK:` comments:

| Group | Examples |
|---|---|
| **Memory cache** | `memoryCacheSizeMB`, `gridCacheSizeMB` — user-chosen ceilings on top of `CacheRecommendationPolicy`'s adaptive defaults (see [Image Pipeline and Caching](../02-image-pipeline-and-caching/)). |
| **Thumbnail size** | `thumbnailSizeGrid` (200px default), `thumbnailSizePreview` (1616px), `thumbnailSizeFullSize` (8700px), plus an optional CIRAWFilter-based sharpening pipeline (`enableThumbnailSharpening`, `thumbnailSharpenAmount`) for the zoom preview. |
| **Sharpness scoring** | Parameters feeding the sharpness-scoring algorithm used for burst ranking: border inset fraction, subject-classification toggle, salient-region weight, a `SharpnessPhotoType` preset (`.auto`, portrait, landscape, etc.), a speed/quality trade-off (`SharpnessScoringQuality`), and which image `SharpnessScoringSource` to score from (default: the embedded camera preview, cheaper than a full RAW decode). |
| **Focus mask** | Laplacian-based focus-peaking tuning: pre-blur radius, threshold, energy multiplier, erosion/dilation/feather radii — these directly parameterize the focus-mask rendering seen in the zoom overlay. |

`CacheSettingsLimits` (`memoryMinMB`/`MaxMB` = 1000–8000,
`gridMinMB`/`MaxMB` = 400–2000) bounds what the user is allowed to enter for
the two cache sliders, independent of the adaptive recommendation logic in
`CacheRecommendationPolicy`.

### Persistence

Settings are stored as JSON at
`~/Library/Application Support/RawCull/settings.json`, written through a
private nested `actor SettingsFileWriter` (atomic write, directory created
on demand if missing) — the same "small dedicated actor for atomic JSON
writes" pattern used by `WriteSavedFilesJSON` for culling data (see
[Culling and Persistence](../03-culling-and-persistence/)).

`SettingsViewModel` uses a documented two-phase initialization to satisfy
Swift's strict-concurrency initialization rules while still kicking off an
async load from `init`:

```swift
init(settingsFileURL: URL? = nil, loadOnInit: Bool = true) {
    // Phase 1: all stored properties must be set before self can be captured.
    self.settingsFileURL = settingsFileURL
    loadTask = nil
    // Phase 2: self is now fully initialized — safe to capture in the Task closure.
    if loadOnInit {
        loadTask = Task { await self.loadSettings() }
    }
}
```

Callers that need settings to be loaded before proceeding (e.g. before
computing cache sizes at launch) call `await ensureLoaded()`, which simply
awaits the stored `loadTask` — safe to call multiple times, and a no-op once
the load has already completed. `SettingsViewModel.shared` is the app's one
instance (a rare intentional singleton here, unlike `RawCullViewModel`/AI
runtime which are explicitly constructed once by the composition root and
threaded through).

## AI Settings

`RawCullAISettingsModel` (`Intelligence/ModelManagement/RawCullAISettingsModel.swift`)
is the Settings-facing surface for the Intelligence subsystem: CLIP model
choice, segmentation model choice, "use CLIP for similarity" toggle, model
download/license status, and a diagnostics scan of already-saved burst
embeddings. It deliberately does **not** expose the underlying
`PhotoAIKit`/`PhotoAnalysisKit` providers or the composition root — only
capability statuses and simple preferences, persisted to `UserDefaults`
under its own preference keys (`RawCullAI.useCLIPForSimilarity`, etc.) Full
detail is in
[Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/#model-management-and-licensing).

## Memory monitor

`MemoryViewModel` (`Model/ViewModels/MemoryViewModel.swift`) is a small
`@MainActor @Observable` class that powers the memory-usage UI in Settings.
`updateMemoryStats()` reads system/app memory via low-level `mach` calls
(`host_statistics64`, `task_info`) — deliberately moved off the main actor
with `Task.detached` since these are blocking syscalls, then republished on
the main actor:

```swift
func updateMemoryStats() async {
    let (total, used, app, threshold) = await Task.detached {
        (ProcessInfo.processInfo.physicalMemory, self.getUsedSystemMemory(),
         self.getAppMemory(), self.calculateMemoryPressureThreshold(total: total))
    }.value
    await MainActor.run {
        self.totalMemory = total; self.usedMemory = used
        self.appMemory = app; self.memoryPressureThreshold = threshold
    }
}
```

It exposes convenience percentages (`usedMemoryPercentage`,
`appMemoryPercentage`, `memoryPressurePercentage`) for progress-bar style
UI, and reads `SharedMemoryCache.shared.currentPressureLevel` directly
rather than running a second `DispatchSourceMemoryPressure` listener — a
comment on the property spells this out ("no second DispatchSource
needed"), reinforcing that `SharedMemoryCache` is the single owner of
pressure-level state (see
[Concurrency Architecture](../01-concurrency-architecture/)).

## Where to look when extending this

- **New general preference** → add a stored property to `SettingsViewModel`
  next to its logical group; it's automatically part of the JSON blob via
  `Codable` synthesis, no manual encode/decode wiring needed.
- **New cache-related preference** → also consider whether
  `CacheRecommendationPolicy`/`CacheSettingsLimits` need a matching bound.
- **New AI preference** → goes on `RawCullAISettingsModel`, not
  `SettingsViewModel`, and must flow through
  `RawCullIntelligenceRuntime.apply(configuration:)` rather than being read
  directly by a feature.
