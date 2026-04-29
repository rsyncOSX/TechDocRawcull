+++
author = "Thomas Evensen"
title = "Memory Pressure"
date = "2026-04-29"
tags = ["memory", "pressure", "cache"]
categories = ["technical details"]
+++

# Memory Pressure — RawCull

> **Source files covered:**
> `Views/Settings/MemoryTab.swift` · `Model/ViewModels/MemoryViewModel.swift` · `Views/Settings/CacheSettingsTab.swift`
> `Actors/SharedMemoryCache.swift` · `Model/ViewModels/SettingsViewModel.swift`
> `Views/RawCullSidebarMainView/RawCullMainView.swift` · `Model/Handlers/CreateFileHandlers.swift`

RawCull tracks memory in two different ways:

1. **An app-side threshold** used for visualization and early warning.
2. **The macOS kernel memory-pressure signal** delivered through `DispatchSourceMemoryPressure`.

Those are related, but they are **not** the same thing. The 85% line shown in the UI is RawCull's own heuristic. The `Normal / Warning / Critical` status is the real kernel-reported pressure level.

---

## 1. How RawCull calculates memory

`MemoryViewModel` is the source for the numbers shown in **MemoryTab**.

### 1.1 Total unified memory

RawCull reads installed physical memory directly from `ProcessInfo`:

```swift
let total = ProcessInfo.processInfo.physicalMemory
```

This is the machine's total unified memory, not free memory.

### 1.2 Total used memory

RawCull does not ask macOS for a ready-made "used memory" number. It computes one from Mach VM statistics:

```swift
used = (wire_count + active_count + compressor_page_count) * pageSize
```

More precisely:

| Component | Meaning |
|---|---|
| `wire_count` | Wired pages that cannot be paged out |
| `active_count` | Pages actively in use |
| `compressor_page_count` | Pages currently compressed by the VM compressor |

The result is clamped to physical memory:

```swift
min(calculatedUsedBytes, totalPhysicalMemory)
```

So the red pressure marker in the UI is compared against a deliberately simple "used system memory" model:

```text
usedMemory = min((wired + active + compressed) * pageSize, totalMemory)
```

### 1.3 RawCull's own memory footprint

RawCull measures its own process memory with `task_info(... TASK_VM_INFO ...)` and uses:

```swift
info.phys_footprint
```

That is the app's real process footprint as reported by the kernel, and it is what **App Memory Usage** displays in `MemoryTab`.

### 1.4 Percentages shown in the UI

`MemoryViewModel` exposes three percentages:

```text
usedMemoryPercentage     = usedMemory / totalMemory
memoryPressurePercentage = memoryPressureThreshold / totalMemory
appMemoryPercentage      = appMemory / usedMemory
```

`MemoryTab` refreshes these values once per second.

---

## 2. How RawCull defines "memory pressure"

### 2.1 RawCull's heuristic threshold: 85%

`MemoryViewModel` defines a configurable threshold factor:

```swift
pressureThresholdFactor: Double = 0.85
```

The threshold is:

```text
memoryPressureThreshold = totalMemory * 0.85
```

So on a 16 GB machine, RawCull's soft warning line is roughly:

```text
16 GB * 0.85 = 13.6 GB
```

This threshold is used in two places:

1. **`MemoryTab`** draws the red vertical marker on the used-memory bar.
2. **`RawCullMainView`** checks every 5 seconds whether:

```text
usedMemory >= memoryPressureThreshold
```

If that is true **and** the kernel pressure level is still `.normal`, RawCull shows a **soft memory warning**. That is an early warning before macOS has escalated to a real pressure event.

### 2.2 Kernel-reported pressure: normal / warning / critical

The real pressure signal lives in `SharedMemoryCache`:

```swift
DispatchSource.makeMemoryPressureSource(eventMask: .all, queue: .global(qos: .utility))
```

The actor maps the kernel event to:

| RawCull enum | Meaning |
|---|---|
| `.normal` | No active kernel pressure |
| `.warning` | Memory pressure is building |
| `.critical` | System pressure is severe |

`MemoryViewModel` reads `SharedMemoryCache.shared.currentPressureLevel` directly so `MemoryTab` can show the live kernel status without creating a second pressure source.

---

## 3. How cache memory limits are set

RawCull's memory pressure behavior is tightly coupled to its two in-memory caches:

1. **Main memory cache** (full-resolution preview, `NSCache<NSURL, CachedThumbnail>`)
2. **Grid thumbnail cache** (200 px downscaled, `NSCache<NSURL, CachedThumbnail>`)

The limits come from `SettingsViewModel` and are applied by `SharedMemoryCache.calculateConfig(from:)`, which produces a `CacheConfig` snapshot consumed by `applyConfig(_:)`.

### 3.1 Main cache limit

Settings default (loaded from `~/Library/Application Support/RawCull/settings.json`, falls back to the in-memory default if no file exists):

```swift
memoryCacheSizeMB = 4000
```

Slider range in `CacheSettingsTab`: **1000 – 8000 MB**, step 250.

Applied to `NSCache` as:

```text
totalCostLimit = memoryCacheSizeMB * 1024 * 1024
```

`SettingsViewModel.resetToDefaultsMemoryCache()` resets the value to **5000**, which differs from the on-load default of 4000.

### 3.2 Grid cache limit

Settings default:

```swift
gridCacheSizeMB = 400
```

Slider range: **400 – 2000 MB**, step 50.

Applied as:

```text
gridTotalCostLimit = gridCacheSizeMB * 1024 * 1024
```

### 3.3 Why `countLimit` is not the primary limiter

RawCull intentionally makes item count a secondary guardrail:

| Cache | Count limit | Applied in |
|---|---|---|
| Main cache | `10000` | `calculateConfig(from:)` |
| Grid cache | `3000` | `applyConfig(_:)` (hard-coded alongside `gridTotalCostLimit`) |

The design intent is that **byte cost** should trigger eviction first, not the number of items. `NSCache` applies `min(countLimit, totalCostLimit)`, so setting the count limit far above what the byte budget could ever hold makes byte cost the binding constraint.

### 3.4 Cost-per-pixel and cache cost

`costPerPixel` is **not a setting** — it lives on `SharedMemoryCache` itself as a fixed constant:

```swift
nonisolated let costPerPixel: Int = 4
```

The earlier `thumbnailCostPerPixel` setting was removed: representations in this app are always sRGB RGBA (4 bytes/pixel), so the value never needed to vary at runtime. `CachedThumbnail.init` reads this constant once when computing its NSCache cost:

```text
cost = (Σ rep.pixelsWide * rep.pixelsHigh * 4) * 1.1   // +10% wrapper overhead
```

For preview-capacity estimates in `CacheSettingsTab`:

```text
costPerImage     = thumbnailSizePreview * thumbnailSizePreview * 4
estimatedImages  = (memoryCacheSizeMB * 1024 * 1024) / costPerImage
```

For grid thumbnails, the estimator uses the **running average grid-entry cost**
when the cache has any contents (so the estimate tracks real, downscaled entry
sizes), and falls back to `(thumbnailSizeGrid * 2)² * 4 * 1.1` when the cache
is still empty.

---

## 4. Limits and guardrails shown in Settings

### 4.1 Save-time validation

When settings are saved, `SettingsViewModel.validateSettings()` checks two
conditions and logs a warning to the system log if either is true:

1. `memoryCacheSizeMB < 500`
2. `memoryCacheSizeMB > 80%` of physical memory

The check is non-blocking — the value still saves. It only records that the
chosen size may hurt performance or contribute to system memory pressure.

### 4.2 Estimator panel in the cache settings UI

`CacheSettingsTab` shows an "Estimate for RAW files" card with a separate
file-count slider (**500 – 5000**, step 100). It is **display-only** — the
slider value is not persisted and does not affect cache behaviour.

The card shows two derived counts based on the current `memoryCacheSizeMB`
and `gridCacheSizeMB` sliders:

```text
estimatedMemCacheImages  = min(numFiles,
                               memoryCacheSizeMB * 1024 * 1024 /
                               (thumbnailSizePreview² * 4))

estimatedGridCacheImages = min(numFiles,
                               gridCacheSizeMB * 1024 * 1024 /
                               avgGridEntryCost)
```

`avgGridEntryCost` is the running average of `getGridCacheCurrentCost() /
getGridCacheCount()` when the grid cache has entries; otherwise the fallback
`(thumbnailSizeGrid * 2)² * 4 * 1.1` is used.

The earlier "safe limit" / "1 GB headroom" red-warning state and the
"projected RawCull RAM" empirical-interpolation panel are no longer wired up
in the live UI (the corresponding code paths in `SettingsViewModel` and
`CacheSettingsTab` are commented out). The 85 % heuristic survives only in
`MemoryViewModel.pressureThresholdFactor` and the `RawCullMainView` poll
described in §5.1.

### 4.3 Live cache usage panel

Below the estimator, a second card shows real, live state:

| Field | Source |
|---|---|
| Disk cache size | `SharedMemoryCache.shared.getDiskCacheSize()` (refreshed on appear and after pruning) |
| Grid cache cost | `getGridCacheCurrentCost()` / `gridThumbnailCache.totalCostLimit` |
| Grid thumbnails | `getGridCacheCount()` (refreshed every 5 s) |

A **Prune Disk Cache** button calls `pruneDiskCache(maxAgeInDays: 0)`, which
wipes every JPEG under `~/Library/Caches/no.blogspot.RawCull/Thumbnails/`.

---

## 5. What happens when memory pressure is discovered

There are two separate response paths.

### 5.1 Soft warning: RawCull sees 85% usage before macOS escalates

In `RawCullMainView`, RawCull polls memory every 5 seconds:

```swift
let exceeded = usedMemory >= memoryPressureThreshold
```

If:

1. usage has crossed the 85% threshold, and
2. `SharedMemoryCache.shared.currentPressureLevel == .normal`

then:

```swift
viewModel.softMemoryWarning = true
```

This produces a non-kernel soft warning in the main UI.

### 5.2 Real kernel pressure: the cache actor reacts immediately

`SharedMemoryCache.handleMemoryPressureEvent()` owns the real response to
macOS pressure events. Every event also bumps a cumulative counter
(`_pressureNormals`, `_pressureWarnings`, `_pressureCriticals`) so a 5-second
diagnostics sampler that misses a `.warning → .normal` flicker can still
detect the transition by comparing counter deltas.

#### `.normal`

When pressure returns to normal:

1. `currentPressureLevel` becomes `.normal`
2. `_pressureNormals` is incremented
3. the full saved cache configuration is restored with `refreshConfig()`
   (re-reads settings, builds a fresh `CacheConfig`, applies it)
4. the UI callback receives `memorypressurewarning(false)`

Effect: any pressure warning clears, and the cache limits return to the values
configured in Settings.

#### `.warning`

When macOS reports warning pressure:

1. `currentPressureLevel` becomes `.warning`
2. `_pressureWarnings` is incremented
3. both NSCache caps are reduced **in place**:

   ```text
   memoryCache.totalCostLimit       *= 0.6
   gridThumbnailCache.totalCostLimit *= 0.6
   ```

4. `memorypressurewarning(true)` is sent through `FileHandlers`

RawCull does **not** flush either cache. `NSCache` evicts incrementally as
later inserts push the running total above the new lower cap, so the response
is gradual instead of a stall. The reduction compounds across repeated
warnings until a `.normal` event runs `refreshConfig()`.

#### `.critical`

When macOS reports critical pressure:

1. `currentPressureLevel` becomes `.critical`
2. `_pressureCriticals` is incremented
3. `memoryCache.removeAllObjects()`
4. `memoryCache.totalCostLimit = 50 * 1024 * 1024` (50 MiB floor)
5. `_memCost` and `_memCount` are reset to zero
6. `gridThumbnailCache.removeAllObjects()`
7. `_gridCost` and `_gridCount` are reset to zero
8. `_evictedRing.clear()` — wholesale flush invalidates per-URL eviction
   tracking, otherwise every subsequent disk fallback would falsely register
   as a boomerang miss
9. `memorypressurewarning(true)` is sent through `FileHandlers`

The demand counters (`_demandRequests`, `_boomerangMisses`, `_cacheCold`) are
intentionally **not** reset — Memory Diagnostics needs cumulative totals
across pressure events. Critical pressure causes an immediate cache purge
and temporarily floors the main cache to **50 MiB** until the system returns
to normal and `refreshConfig()` restores the saved limits.

---

## 6. User-visible behavior

When memory pressure is active, the user sees it in three places:

| Surface | What it shows |
|---|---|
| **MemoryTab** | Total memory, used memory, app footprint, the 85% threshold line, and the kernel pressure level |
| **CacheSettingsTab** | Cache-size estimates, projected RAM usage, and warnings when a configuration approaches the safe limit |
| **Main window overlay** | `memorypressurewarning` on kernel warning/critical, or `softMemoryWarning` when RawCull crosses 85% before the kernel does |

In short:

- **`MemoryViewModel`** calculates and formats memory usage.
- **`MemoryTab`** visualizes it.
- **`CacheSettingsTab`** explains how chosen cache sizes translate into expected memory usage.
- **`SharedMemoryCache`** is the component that actually reacts to system memory pressure.

