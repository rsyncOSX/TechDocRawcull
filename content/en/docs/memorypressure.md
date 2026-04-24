+++
author = "Thomas Evensen"
title = "Memory Pressure"
date = "2026-04-24"
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

1. **Main memory cache**
2. **Grid thumbnail cache**

The limits come from `SettingsViewModel` and are applied by `SharedMemoryCache.calculateConfig(from:)`.

### 3.1 Main cache limit

Default setting:

```swift
memoryCacheSizeMB = 10000
```

Applied to `NSCache` as:

```text
totalCostLimit = memoryCacheSizeMB * 1024 * 1024
```

So the default main cache cap is:

```text
10,000 MiB
```

### 3.2 Grid cache limit

Default setting:

```swift
gridCacheSizeMB = 400
```

Applied as:

```text
gridTotalCostLimit = gridCacheSizeMB * 1024 * 1024
```

So the default grid cache cap is:

```text
400 MiB
```

### 3.3 Why `countLimit` is not the primary limiter

RawCull intentionally makes item count a secondary guardrail:

| Cache | Count limit |
|---|---|
| Main cache | `10000` |
| Grid cache | `3000` |

The design intent is that **byte cost** should trigger eviction first, not the number of items.

### 3.4 Cost-per-pixel and cache cost

Settings default:

```swift
thumbnailCostPerPixel = 6
```

That value is used for **NSCache bookkeeping**, not as a claim that each image literally uses 6 bytes per pixel in RAM.

For preview-capacity estimates in `CacheSettingsTab`:

```text
costPerImage = thumbnailSizePreview * thumbnailSizePreview * thumbnailCostPerPixel
estimatedImages = cacheBytes / costPerImage
```

For "real RAM" projections, the code instead uses **4 bytes/pixel** for RGBA image data, because that better represents actual image memory:

```text
realPreviewBytes = thumbnailSizePreview * thumbnailSizePreview * 4
```

For grid thumbnails, the UI also adds a 10% safety overhead:

```text
gridBytes = (size * size * 4) * 1.1
```

That distinction is important:

- **6 bytes/pixel** -> conservative cache-cost accounting
- **4 bytes/pixel** -> approximate real image RAM

---

## 4. Limits and guardrails shown in Settings

`CacheSettingsTab` exposes several different limits.

### 4.1 Save-time validation

When settings are saved, `SettingsViewModel.validateSettings()` warns if:

1. `memoryCacheSizeMB < 500`
2. `memoryCacheSizeMB > 80%` of physical memory

This does **not** block saving. It logs that the chosen value may hurt performance or cause memory pressure.

### 4.2 Safe-limit estimator in the cache settings UI

The settings UI also uses its own "safe memory" estimate based on the same 85% threshold seen in `MemoryViewModel`:

```text
safeLimit = physicalMemory * 0.85
```

It estimates total RawCull memory as:

```text
estimatedTotalBytes =
    previewCacheBytes
  + gridCacheBytes
  + 100 MB app overhead
```

The file-count slider turns red when:

```text
estimatedTotalBytes >= (physicalMemory * 0.85) - 1 GB
```

So the estimator leaves about **1 GB of headroom** below the 85% line.

### 4.3 Projected RawCull RAM

`CacheSettingsTab` also shows a projected total app RAM figure using an empirical interpolation:

- baseline app overhead: **100 MB**
- maximum payload used by the model: **5400 MB**
- combined projected ceiling: about **5.5 GB**

That projected value is compared against:

```text
physicalMemory * 0.85
```

and shown in red if it crosses the heuristic threshold.

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

`SharedMemoryCache` owns the real response to macOS pressure events.

#### `.normal`

When pressure returns to normal:

1. `currentPressureLevel` becomes `.normal`
2. the full saved cache configuration is restored with `refreshConfig()`
3. the UI callback receives `memorypressurewarning(false)`

Effect: any pressure warning can clear, and the cache limits return to the values from Settings.

#### `.warning`

When macOS reports warning pressure:

```text
newMainCap = currentMainCap * 0.6
newGridCap = currentGridCap * 0.6
```

RawCull does **not** flush the caches immediately. It lowers both `NSCache.totalCostLimit` values in place and lets `NSCache` evict as needed under the smaller caps.

It also sends:

```swift
memorypressurewarning(true)
```

through `FileHandlers`, which sets `RawCullViewModel.memorypressurewarning = true`.

#### `.critical`

When macOS reports critical pressure:

1. `memoryCache.removeAllObjects()`
2. `memoryCache.totalCostLimit = 50 * 1024 * 1024`
3. `gridThumbnailCache.removeAllObjects()`
4. tracked grid cost/count are reset to zero
5. `memorypressurewarning(true)` is sent to the UI

So critical pressure causes an immediate cache purge and temporarily floors the main cache to **50 MB** until the system returns to normal and `refreshConfig()` restores the saved limits.

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

