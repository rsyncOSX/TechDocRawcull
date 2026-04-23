---
title: Calculations Reference
description: Comprehensive reference of all memory, cost, and other calculations in RawCull
weight: 80
---

## Overview

This document catalogs all significant calculations performed in the RawCull codebase, including memory calculations, cache cost calculations, image processing calculations, and numerical analysis. Each calculation is documented with its location, purpose, and mathematical formula.

## Memory Calculations

### System Memory Statistics

**Location:** `Model/ViewModels/MemoryViewModel.swift`

#### Used System Memory Calculation
**Function:** `getUsedSystemMemory()`
**Purpose:** Calculates the total system memory currently in use.

**Formula:**
```
Used Memory = (wired_pages + active_pages + compressed_pages) × page_size
Used Memory = min(calculated, physical_memory)
```

**Details:**
- Reads virtual memory statistics via `host_statistics64` kernel call
- `wired_count`: Memory locked in physical RAM, never paged
- `active_count`: Memory currently in use by running processes
- `compressor_page_count`: Compressed memory pages (zero-copy compression)
- `page_size`: Retrieved via `getpagesize()` (typically 4096 bytes on macOS)
- Result is clamped to not exceed physical memory

#### App Memory Calculation
**Function:** `getAppMemory()`
**Purpose:** Gets the physical memory footprint of the RawCull application.

**Formula:**
```
App Memory = task_vm_info.phys_footprint
```

**Details:**
- Uses `task_info()` kernel call with `TASK_VM_INFO` flavor
- Returns resident physical memory (excludes swapped pages)
- Automatically accounts for memory shared with other processes

#### Memory Pressure Threshold Calculation
**Function:** `calculateMemoryPressureThreshold(total:)`
**Purpose:** Determines the system memory threshold that triggers cache reduction.

**Formula:**
```
Memory Pressure Threshold = total_memory × pressure_threshold_factor
```

**Default:** `pressure_threshold_factor = 0.85` (85% of total memory)

**Details:**
- Used to warn when system approaches critical memory limits
- At 85% system memory usage, cache is reduced to 60% of its limit
- At >90% (kernel critical), cache is cleared and set to 50 MB minimum

#### Memory Percentage Calculations

**Memory Pressure Percentage:**
```
pressure_percentage = (memory_pressure_threshold / total_memory) × 100
```

**Used Memory Percentage:**
```
used_percentage = (used_memory / total_memory) × 100
```

**App Memory Percentage:**
```
app_percentage = (app_memory / used_memory) × 100
```

### Cache Configuration and Cost Calculations

**Location:** `Model/Cache/CacheConfig.swift` and `Actors/SharedMemoryCache.swift`

#### Total Cache Cost Limit
**Purpose:** Sets the maximum bytes that can be stored in the memory cache.

**Formula:**
```
Total Cost Limit (bytes) = memory_cache_size_MB × 1024 × 1024
```

**Production Default:**
```
Total Cost Limit = 500 MB = 500 × 1024 × 1024 bytes = 524,288,000 bytes
```

**Typical Capacity:**
```
Max Images = Total Cost Limit / average_image_cost
          = 500 MB / ~4.5 MB per 1024×1024 image
          ≈ 112 images (1024×1024 px @ 4 bytes/pixel × 1.1 overhead)
```

#### Grid Cache Cost Limit
**Purpose:** Dedicated in-memory cache for grid-view (small, ≤500px) thumbnails.

**Default:**
```
Grid Cache Limit = 400 MB = 400 × 1024 × 1024 bytes
```

### Thumbnail Cost Calculation

**Location:** `Model/Cache/DiscardableThumbnail.swift`

**Function:** `init(image:costPerPixel:)`

**Purpose:** Calculates the memory cost of storing a thumbnail in NSCache for accurate LRU eviction.

**Formula:**
```
Cost = Σ(pixelCost_per_representation) + overhead_buffer

Where:
  pixelCost = width_pixels × height_pixels × costPerPixel
  costPerPixel = 4 (default: RGBA 8-bit channels)
  overhead_buffer = totalCost × 1.1 (10% for NSImage metadata)
```

**Example Calculation:**
```
Image: 1024×1024 pixels, 4 bytes/pixel (RGBA)
  pixelCost = 1024 × 1024 × 4 = 4,194,304 bytes ≈ 4 MB
  overhead = 4,194,304 × 1.1 = 4,613,734 bytes ≈ 4.4 MB
  Final Cost = 4,613,734 bytes
```

**Details:**
- Sums all image representations (important for Retina displays with multiple scales)
- Falls back to logical size if no representations exist (Retina: logical size ≠ pixel count)
- 10% overhead accounts for NSImage wrapper and cache metadata
- Cost value is used as `totalCostLimit` for NSCache eviction decisions

#### Memory Pressure-Based Cache Reduction

**Location:** `Actors/SharedMemoryCache.swift`

**Function:** `handleMemoryPressureEvent()`

**Warning Level (DispatchSource.data == .warning):**
```
Reduced Cost = current_cache_limit × 0.6
```

**Critical Level (DispatchSource.data == .critical):**
```
Memory Cache: removeAllObjects() + set totalCostLimit = 50 MB
Grid Cache: removeAllObjects() + cost tracking reset to 0
```

## Image Processing & Sharpness Calculations

### Histogram Calculation

**Location:** `Views/Histogram/CalculateHistogram.swift`

**Function:** `calculateHistogram(from:)`

**Purpose:** Computes normalized luminance histogram and stores values as 0.0–1.0 for visualization.

**Formula:**
```
Luminance = 0.299 × R + 0.587 × G + 0.114 × B
histogram_bin[Int(luminance)] += 1
normalized_value = histogram_bin[i] / max(histogram)
```

**Details:**
- Iterates over every pixel in the image
- Uses standard ITU-R BT.601 luminance weights (human eye sensitivity)
- Bins range from 0–255 (8-bit luminance)
- Final output: 256 normalized values (0.0–1.0) for graph rendering
- Executed on background thread to prevent UI blocking

### Sharpness Scoring Calculations

**Location:** `Model/ViewModels/FocusMaskModel.swift`

The sharpness scoring system performs multi-step analysis to rate image focus quality. Key calculations include:

#### ISO Scaling Factor

**Function:** `isoScalingFactor(iso:)`

**Purpose:** Adapts focus detection sensitivity based on sensor noise at different ISO levels.

**Formula:**
```
ISO < 800:
  factor = 1.0 (no adaptation, clean sensor)

800 ≤ ISO < 3200:
  factor = 1.0 + (ISO - 800) / 2400 × 0.6
  Example: ISO 2000 → 1.0 + 1200/2400 × 0.6 = 1.3

ISO ≥ 3200:
  factor = min(1.6 + (ISO - 3200) / 6400 × 0.6, 2.2)
  Caps at 2.2 to avoid over-blurring at extreme ISO
```

**Details:**
- Piecewise-linear approach replaces older `sqrt(iso/400)` formula
- Flatter below ISO 800 (Sony A1-series bodies are clean at low ISO)
- Gentle rise through mid-range (1.0→1.6 from ISO 800→3200)
- Shallow tail above 3200 (robust tail mean tolerates sparse noise)

#### Effective Blur Radius Calculation

**Function:** `buildAmplifiedLaplacian(from:config:)`

**Purpose:** Determines Gaussian pre-blur radius used before Laplacian edge detection.

**Formula:**
```
imageWidth = image.extent.width
resFactor = max(1.0, min(sqrt(max(imageWidth, 512) / 512), 3.0))
isoFactor = isoScalingFactor(config.iso)
blurDamp = config.apertureHint.blurDamp

effectiveRadius = min(
  config.preBlurRadius × isoFactor × resFactor × blurDamp,
  100.0
)
```

**Example Calculation:**
```
preBlurRadius = 1.92
isoFactor = 1.3 (ISO 2000)
imageWidth = 800 pixels → resFactor = min(sqrt(800/512), 3.0) = 1.25
blurDamp = 1.0 (mid aperture)

effectiveRadius = min(1.92 × 1.3 × 1.25 × 1.0, 100.0) = 3.12 pixels
```

**Details:**
- Landscape aperture (f/8+) reduces blurDamp (≈0.7) to preserve whole-frame detail
- Wide aperture (f/5.6-) increases effective radius for narrow focus planes
- Resolution factor accounts for image size variations

#### Robust Tail Score (Sharpness Metric)

**Function:** `robustTailScore(_:)`

**Purpose:** Computes focus quality as the p90–p97 band energy relative to noise floor.

**Formula:**
```
1. Sort Laplacian output values: O(n log n) via Accelerate.vDSP.sort
2. Compute percentiles:
   p20 = value at 20th percentile (noise floor baseline)
   p90 = value at 90th percentile
   p97 = value at 97th percentile

3. If p97 ≤ p90: (no outliers)
   score = max(0, p90 - p20)

4. Otherwise: (compute band mean with density penalty)
   bandMean = Σ(max(0, value - p20)) / count
           (for values where p90 ≤ value ≤ p97)
   densityFactor = min(1.0, (edgeCount / n) / 0.06)
   score = bandMean × densityFactor
```

**Details:**
- Replaces older quickselect with Accelerate SIMD sort (avoids O(n²) on high-zero-bias images)
- p90–p97 band captures real edges without outlier noise
- Density penalty (÷0.06) penalizes blurry images with sparse edge pixels
- Robust against high ISO noise and smooth regions

#### Micro-Contrast Calculation

**Function:** `microContrast(_:)`

**Purpose:** Computes standard deviation of Laplacian values to detect fine texture detail.

**Formula:**
```
sum = Σ(value)
sum2 = Σ(value²)
n = count

mean = sum / n
variance = (sum2 / n) - mean²
microContrast = √max(0, variance)
```

**Details:**
- Near zero for smooth/blurry regions
- Higher for textured, in-focus detail
- Used to gate blur attenuation in aperture-aware scoring

#### Blur Attenuation Gate

**Function:** `computeSharpnessScalar(...)`

**Purpose:** Soft-gates (attenuates) the final score when subject region has low micro-contrast (likely blur).

**Formula:**
```
aperture_hint = config.apertureHint
lo = hint.blurGateLow (0.010 wide, 0.008 mid, 0.006 landscape)
hi = hint.blurGateHigh (0.025 wide, 0.022 mid, 0.018 landscape)

t = min(max((subjectMicro - lo) / (hi - lo), 0), 1)
blurAttenuation = 0.20 + t × 0.80
  → 0.20 when σ < lo (likely blur)
  → 1.00 when σ > hi (in focus)
```

**Details:**
- Replaces hard cliff (old: σ < 0.014 → ×0.12)
- Soft ramp prevents false positives on low-contrast subjects
- Aperture-aware: wide apertures have stricter thresholds than landscape

#### Subject Region Analysis

**Function:** `analyzeRegion(_:)` (inner function of `computeSharpnessScalar`)

**Purpose:** Calculates statistics on a specific image region (Vision saliency or AF point).

**Formula:**
```
border_width = max(1, Int(0.12 × min(region_width, region_height)))

borderFraction = borderMean / (borderMean + innerMean)
  where:
    borderMean = Σ(Laplacian) / borderPixelCount
    innerMean = Σ(Laplacian) / innerPixelCount
```

**Details:**
- Separates border pixels (silhouette rim) from inner pixels (texture)
- Border pixels are those within 12% of region edge
- High `borderFraction` indicates silhouette-dominated region

#### Silhouette Penalty

**Function:** `computeSharpnessScalar(...)`

**Purpose:** Reduces final score when subject region is dominated by silhouette rim (backlit wildlife).

**Formula:**
```
silhouetteThreshold = 0.62
if borderFraction > 0.62:
  over = min(1.0, (borderFraction - 0.62) / 0.38)
  blended_score *= (1.0 - 0.55 × over)
  → Up to 55% penalty when borderFraction ≈ 1.0
```

**Details:**
- Addresses common backlit wildlife issue (rim light mistaken for detail)
- Smooth attenuation: not a hard threshold

#### Subject-Size Bonus

**Function:** `computeSharpnessScalar(...)`

**Purpose:** Boosts score slightly when Vision saliency region is large (favorable composition).

**Formula:**
```
area = region.width × region.height (normalized 0–1)
blended_score *= (1.0 + area × config.subjectSizeFactor)

Default subjectSizeFactor = 0.1
  → Bonus of 0–10% depending on region size
```

#### Effective Subject Score Blending

**Function:** `computeSharpnessScalar(...)`

**Purpose:** Combines AF point focus score with Vision saliency score.

**Formula:**
```
if afScore AND salientScore:
  effectiveSubjectScore = afScore × 0.6 + salientScore × 0.4
elif afScore:
  effectiveSubjectScore = afScore
elif salientScore:
  effectiveSubjectScore = salientScore
else:
  effectiveSubjectScore = nil
```

**Details:**
- AF point is camera ground truth (60% weight)
- Vision saliency is perceptual fallback (40% weight)
- Prevents AF points on secondary subjects from mis-ranking

#### Final Score Composition

**Function:** `computeSharpnessScalar(...)`

**Purpose:** Blends full-frame focus metric with subject-region focus metric.

**Formula:**
```
if fullScore AND effectiveSubjectScore:
  base = fullScore × (1 - salientWeight) + effectiveSubjectScore × salientWeight
  (apply silhouette penalty if applicable)
  (apply subject-size bonus if Vision saliency)

elif fullScore only:
  base = fullScore × (1 - salientWeight)³
  (cube penalizes "no detectable subject")

elif effectiveSubjectScore only:
  base = effectiveSubjectScore

finalScore = base × blurAttenuation
```

**Details:**
- `salientWeight` defaults to 0.75 (subject region dominates for wildlife)
- Landscape aperture reduces `salientWeight` (whole-frame detail matters more)
- "No subject" scored with cubic penalty (strong discouragement for wildlife app)

### Sharpness Calibration from Burst

**Location:** `Model/ViewModels/SharpnessScoringModel.swift`

**Function:** `calibrateFromBurst(_:)`

**Purpose:** Computes per-ISO percentile statistics (p50, p90, p95, p99) across a burst for threshold/gain auto-tuning.

**Details:**
- Processes burst with 5–8 concurrent tasks
- Computes 4 percentile points for statistical distribution
- Results used to auto-scale threshold and energyMultiplier per ISO

### Sharpness Score Normalization

**Function:** `recomputeMaxScore()` in `SharpnessScoringModel`

**Purpose:** Updates normalization denominator for badge display (O(1) per view cell).

**Formula:**
```
if scores.count < 2:
  maxScore = scores.values.first ?? 1.0

elif scores.count < 10:
  maxScore = max(sorted_scores.last, 1e-6)

else:
  k = Int(Float(count - 1) × 0.90)  (90th percentile)
  maxScore = max(sorted_scores[k], 1e-6)
```

**Details:**
- Avoids outliers: normalizes to p90 instead of maximum
- Ensures badges span 0–100% across typical range

## Similarity Scoring Calculations

**Location:** `Model/ViewModels/SimilarityScoringModel.swift`

### Vision Feature-Print Distance

**Function:** `rankSimilar(to:using:saliencyInfo:)`

**Purpose:** Computes visual similarity between images using Vision framework embeddings.

**Details:**
- Uses `VNGenerateImageFeaturePrintRequest` (revision 2)
- Distance computed via `VNFeaturePrintObservation.computeDistance()`
- Applied on background thread pool to prevent main-thread blocking

### Subject Mismatch Penalty

**Formula:**
```
mismatchPenalty = 0.10 (constant kSubjectMismatchPenalty)

if anchorLabel ≠ comparisonLabel:
  distance += 0.10
```

**Details:**
- Penalizes cross-subject comparisons slightly (10% of typical distance range)
- Keeps visual embedding as dominant signal
- Encourages grouping by both appearance and subject type

### Burst Distance Clustering

**Function:** `groupBursts(files:)`

**Purpose:** Groups consecutive frames into bursts using sequential distance threshold.

**Formula:**
```
for each adjacent pair (i-1, i):
  distance = VNFeaturePrintObservation.computeDistance(i-1, i)
  startNewGroup = distance ≥ burstSensitivity

Default burstSensitivity = 0.25
```

**Details:**
- O(n) sequential pass (preserves shot order)
- Typical burst threshold: 0.25 (camera captures every ~0.1–0.2 sec in burst mode)
- Can be adjusted by user slider (0.05–0.95)

## Processing Progress & Estimation Calculations

### Sharpness Scoring Progress

**Location:** `Model/ViewModels/SharpnessScoringModel.swift`

**Function:** `scoreFiles(_:)`

**Purpose:** Estimates remaining time based on completion rate.

**Formula:**
```
elapsed = Date().timeIntervalSince(startTime)
rate = completedCount / elapsed (files per second)
scoringEstimatedSeconds = max(0, (totalFiles - completedCount) / rate)
```

**Details:**
- Updated after each file completion
- 6 concurrent scoring tasks for parallelism

### Similarity Indexing Progress

**Function:** `indexFiles(_:thumbnailMaxPixelSize:)` in `SimilarityScoringModel`

**Formula:** Same as sharpness scoring estimation

**Details:**
- 4 concurrent embedding tasks (lighter than sharpness computation)

## Data Synchronization Calculations

**Location:** `Model/ParametersRsync/RemoteDataNumbers.swift`

**Purpose:** Parses rsync output to extract file counts, sizes, and transfer rates.

**Parsed Values:**
```
filestransferred: count (int)
totaltransferredfilessize: bytes (int)
numberoffiles: count (int)
totalfilesize: bytes (int)
totaldirectories: count (int)
newfiles: count (int)
deletefiles: count (int)
maxpushpull: Double (percentage of data to transfer)
```

**Details:**
- Reduces rsync output to last 20 lines for performance
- Extracts structured data for confirmation dialog display
- Supports both rsync v3 and openrsync output formats

## Aperture-Based Thresholds

**Location:** `Model/ViewModels/SharpnessScoringModel.swift`

**Function:** `ApertureFilter.matches(_:)`

**Purpose:** Filters images by aperture range for subject-specific analysis.

**Thresholds:**
```
Wide aperture: f ≤ 5.6 (narrow focus plane)
Landscape aperture: f ≥ 8.0 (deep depth of field)
All: no filter
```

## Summary of Key Constants

| Constant | Value | Location | Purpose |
|----------|-------|----------|---------|
| Memory Pressure Factor | 0.85 | MemoryViewModel | Threshold to trigger cache reduction |
| Default Cost Per Pixel | 4 bytes/px | CacheConfig, DiscardableThumbnail | RGBA 8-bit channels |
| Cache Overhead Buffer | 1.10× | DiscardableThumbnail | 10% for NSImage metadata |
| Production Cache Limit | 500 MB | CacheConfig | Primary memory constraint |
| Grid Cache Limit | 400 MB | CacheConfig | Small grid thumbnails (≤500px) |
| Memory Pressure Warning Reduction | 0.60× | SharedMemoryCache | Reduce cache to 60% on warning |
| Memory Pressure Critical Limit | 50 MB | SharedMemoryCache | Minimum cache size on critical |
| Default Sharpness Saliency Weight | 0.75 | FocusDetectorConfig | Favor subject region (75%) over full-frame (25%) |
| Sharpness Subject Size Factor | 0.10 | FocusDetectorConfig | 0–10% bonus based on region area |
| Sharpness Border Inset Fraction | 0.04 | FocusDetectorConfig | Exclude 4% border to avoid blur artifacts |
| AF Region Radius | 0.12 | FocusDetectorConfig | 12% of image dimension |
| Subject Mismatch Penalty | 0.10 | SimilarityScoringModel | Small penalty for cross-subject matches |
| Default Burst Sensitivity | 0.25 | SimilarityScoringModel | Distance threshold for burst grouping |
| Histogram Bins | 256 | CalculateHistogram | 0–255 luminance levels |
| Luminance Red Weight | 0.299 | CalculateHistogram | ITU-R BT.601 |
| Luminance Green Weight | 0.587 | CalculateHistogram | ITU-R BT.601 |
| Luminance Blue Weight | 0.114 | CalculateHistogram | ITU-R BT.601 |
| Silhouette Threshold | 0.62 | FocusMaskModel | Trigger silhouette penalty |
| Silhouette Penalty Max | 0.55 | FocusMaskModel | Up to 55% score reduction |
| Max Concurrent Sharpness Tasks | 6 | SharpnessScoringModel | Parallel scoring limit |
| Max Concurrent Similarity Index Tasks | 4 | SimilarityScoringModel | Parallel indexing limit |
| Max Concurrent Similarity Embedding Tasks | 4 | SimilarityScoringModel | Parallel embedding limit |
| Percentile for Score Normalization | 0.90 | SharpnessScoringModel | Use p90 instead of max for badges |
| Robust Tail Density Threshold | 0.06 | FocusMaskModel | Expected fraction of edge pixels |
| AF Focus Region Minimum Samples | 64 pixels | FocusMaskModel | Minimum pixels for valid AF score |
| Salient Region Minimum Samples | 256 pixels | FocusMaskModel | Minimum pixels for valid saliency score |
| Minimum Salient Object Union Area | 0.03 | FocusMaskModel | Exclude very small detected regions |
| Minimum Classification Confidence | 0.06 (subjects) / 0.15 (environment) | FocusMaskModel | Filter weak classifications |

