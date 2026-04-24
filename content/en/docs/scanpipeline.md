+++
author = "Thomas Evensen"
title = "Scan and Thumbnail Pipeline"
date = "2026-03-25"
tags = ["focus points", "sony", "arw", "parser","scan"]
categories = ["technical details"]
mermaid = true
+++

# RawCull — Scan and Thumbnail Pipeline

This document describes the complete execution flow from the moment a user opens
a catalog folder to the point where all thumbnails are visible in the grid.
It covers the actors involved, the data flow between them, the concurrency
model, and the measured results on a real catalog of 809 Sony A1 ARW files
stored on an external 800 MB/s SSD.

Per-vendor RAW knowledge (file extensions, embedded-thumbnail extraction,
MakerNote focus parsing, compression labels, size-class thresholds) is hidden
behind the `RawFormat` protocol. `RawFormatRegistry.format(for: URL)` returns
the matching conformer — `SonyRawFormat` for `.arw`, `NikonRawFormat` for
`.nef` — so every code path below is vendor-agnostic; only the two
`RawFormat` conformers reach into vendor-specific binary parsers.

---

## 1. Overview

Opening a catalog triggers two parallel workstreams:

```
User opens folder
       │
       ├─► ScanFiles.scanFiles()          — discovers files, reads EXIF and focus points
       │
       └─► ScanAndCreateThumbnails
               .preloadCatalog()          — generates or loads thumbnails for every file
```

Both workstreams are Swift actors. Each uses a `withTaskGroup` internally to
process files concurrently. Both report progress back to the SwiftUI layer via
`@MainActor` callbacks.

---

## 2. Phase 1 — File scan (`ScanFiles`)

**File:** `RawCull/Actors/ScanFiles.swift`

### 2.1 Directory discovery

```swift
let contents = try FileManager.default.contentsOfDirectory(
    at: url,
    includingPropertiesForKeys: [.nameKey, .fileSizeKey, .contentTypeKey,
                                  .contentModificationDateKey],
    options: [.skipsHiddenFiles]
)
```

`FileManager.contentsOfDirectory` returns all entries in one call. File-system
metadata (name, size, type, modification date) is prefetched via
`includingPropertiesForKeys` — no per-file `stat()` calls are needed later.

### 2.2 Single-pass concurrent extraction (`withTaskGroup`)

EXIF metadata and MakerNote focus points are extracted in a **single
combined task group pass**. Each task dispatches through `RawFormatRegistry`
so the same loop handles both Sony ARW and Nikon NEF files in one go:

```swift
let pairs: [(FileItem, DecodeFocusPoints?)] = await withTaskGroup(
    of: (FileItem, DecodeFocusPoints?).self
) { group in
    for fileURL in contents {
        guard let format = RawFormatRegistry.format(for: fileURL) else { continue }
        discoveredCount += 1
        let progress = onProgress
        let count = discoveredCount
        Task { @MainActor in progress?(count) }   // fire-and-forget UI update
        group.addTask {
            let res      = try? fileURL.resourceValues(forKeys: Set(keys))
            let exifData = self.extractExifData(from: fileURL, format: format)   // nonisolated
            let focusStr = format.focusLocation(from: fileURL)
            let fileItem = FileItem(
                url: fileURL,
                name: res?.name ?? fileURL.lastPathComponent,
                size: Int64(res?.fileSize ?? 0),
                dateModified: res?.contentModificationDate ?? Date(),
                exifData: exifData,
                afFocusNormalized: focusStr.flatMap { Self.parseFocusNormalized($0) },
            )
            let focusPoint: DecodeFocusPoints? = focusStr.map {
                DecodeFocusPoints(sourceFile: fileURL.lastPathComponent,
                                  focusLocation: $0)
            }
            return (fileItem, focusPoint)
        }
    }
    var collected: [(FileItem, DecodeFocusPoints?)] = []
    for await pair in group { collected.append(pair) }
    return collected
}

let result       = pairs.map(\.0)
let nativePoints = pairs.compactMap(\.1)
```

For each supported RAW file a task is added to the group. The loop itself is
non-blocking: progress callbacks are fired to the main actor without `await`,
so the loop completes almost instantly and the task group fills up immediately.

Each task calls `extractExifData(from:format:)` and `format.focusLocation(from:)`
**without hopping back to the actor** — both are `nonisolated`, so they run
directly on the global cooperative thread pool. `format.focusLocation` resolves
statically to `SonyMakerNoteParser.focusLocation` for `.arw` or
`NikonMakerNoteParser.focusLocation` for `.nef`. This eliminates the separate
second file-open pass that a dedicated `extractNativeFocusPoints` function
previously required, and keeps the dispatch loop vendor-agnostic.

The scan also parses the normalised AF-point `CGPoint` (origin top-left, range
0–1) inline via `parseFocusNormalized`, caching it on `FileItem.afFocusNormalized`
for the sharpness pipeline to consume without re-reading the file.

`extractExifData(from:format:)` uses Apple's ImageIO framework:

```swift
private nonisolated func extractExifData(from url: URL, format: any RawFormat.Type) -> ExifMetadata? {
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) …
```

`CGImageSourceCopyPropertiesAtIndex` reads the TIFF/EXIF header from the file.
For a Sony ARW or Nikon NEF this is the first few kilobytes — not the full
RAW image. The resolved `format` is passed through so the per-vendor
`rawFileTypeString(compressionCode:)` and `sizeClassThresholds(camera:)`
helpers render body-appropriate labels (e.g. compression code `6` means
"Compressed" on Sony but Nikon uses `34713` for `NEF Compressed`).

**Measured throughput:** ~2–3 ms per file. 809 files concurrently ≈ **3–4 seconds**.

### 2.3 Focus point extraction and JSON fallback

Focus points are extracted inline in the same task group as EXIF (see 2.2).
After the group completes, the results are resolved:

```swift
decodedFocusPoints = nativePoints.isEmpty
    ? await decodeFocusPointsJSON(from: url)
    : nativePoints
```

If native MakerNote extraction yielded no results — for example, files captured
before the feature was available, older Nikon DSLRs whose `AFInfo2` layout is
not yet parsed, or Sony bodies other than the supported list — `ScanFiles`
falls back to reading a `focuspoints.json` sidecar file from the catalog
folder. The fallback file read runs on a detached utility-priority task to
avoid blocking the scan actor:

```swift
private func decodeFocusPointsJSON(from url: URL) async -> [DecodeFocusPoints]? {
    let fileURL = url.appendingPathComponent("focuspoints.json")
    guard FileManager.default.fileExists(atPath: fileURL.path) else { return nil }
    let data = try await Task.detached(priority: .utility) {
        try Data(contentsOf: fileURL)
    }.value
    return try JSONDecoder().decode([DecodeFocusPoints].self, from: data)
}
```

#### What the MakerNote parsers do

Both Sony ARW and Nikon NEF are TIFF-based. `SonyMakerNoteParser` and
`NikonMakerNoteParser` are caseless enums with a shared `focusLocation(from:)`
output shape — `"width height x y"` in full-sensor pixel space, origin top-left
— so the downstream `parseFocusNormalized` helper accepts both identically.

Sony ARW focus location lives at:

```
TIFF IFD0  →  ExifIFD (tag 0x8769)  →  MakerNote (tag 0x927C)
    →  Sony MakerNote IFD  →  FocusLocation (tag 0x2027)
```

Tag `0x2027` is `int16u[4]` = `[sensorWidth, sensorHeight, focusX, focusY]`
in full sensor pixel coordinates. The parser navigates the TIFF IFD chain in
binary using only the bytes it needs.

**Key implementation detail:** the parser reads only the first 4 MB of the file:

```swift
guard let fh = try? FileHandle(forReadingFrom: url) else { return nil }
defer { try? fh.close() }
guard let data = try? fh.read(upToCount: 4 * 1024 * 1024) …
```

Sony ARW MakerNote metadata sits well within the first 1–2 MB of the file.
Reading 4 MB is a conservative safe limit. The full RAW image data follows
later in the file and is never touched.

`NikonMakerNoteParser` follows the same idea but targets the Nikon Type-3
MakerNote layout (`"Nikon\0"` signature + inner TIFF header + `AFInfo2` tag
`0x00B7`), and uses AFInfoVersion `0300`+ offsets for AFImageWidth/Height and
AFAreaX/Y — the layout used by Z9, Z8, Z7, and Z6 class bodies.

**Measured throughput:** ~0.3–0.4 ms per file. 809 files concurrently ≈ **< 1 second**.

---

## 3. Phase 2 — Thumbnail generation (`ScanAndCreateThumbnails`)

**File:** `RawCull/Actors/ScanAndCreateThumbnails.swift`

### 3.1 File discovery and sliding-window task group

`preloadCatalog` delegates directory scanning to a dedicated `DiscoverFiles`
struct before building the task group. `DiscoverFiles.discoverFiles(at:recursive:)`
is `nonisolated` and runs its directory walk inside a detached utility-priority
task, filtering by the union of all registered extensions:

```swift
let urls = await DiscoverFiles().discoverFiles(at: catalogURL, recursive: false)
totalFilesToProcess = urls.count
await fileHandlers?.maxfilesHandler(urls.count)

// Inside DiscoverFiles:
let supported: Set<String> = RawFormatRegistry.allExtensions   // {"arw", "nef"}
```

The task group then processes the discovered URLs with a sliding window:

```swift
let maxConcurrent = ProcessInfo.processInfo.activeProcessorCount * 2

for (index, url) in urls.enumerated() {
    if index >= maxConcurrent {
        await group.next()        // keep at most maxConcurrent in flight
    }
    group.addTask {
        await self.processSingleFile(url, targetSize: targetSize, …)
    }
}
```

On a Mac Mini M2 (10 reported cores), `maxConcurrent` = 20. The sliding window
ensures at most 20 files are being processed simultaneously, preventing memory
pressure from loading too many large images at once.

### 3.2 Per-file processing (`processSingleFile`)

Each task follows a three-tier lookup:

```
A. RAM cache (NSCache)   →  microseconds, no I/O
B. Disk cache (JPEG)     →  ~1–5 ms, reads ~494 KB from internal SSD
C. RAW extraction        →  ~180–200 ms, decodes full ARW via ImageIO
```

#### A. RAM cache

`SharedMemoryCache` is a global actor wrapping `NSCache`. A cache hit is a
synchronous dictionary lookup — effectively free.

#### B. Disk cache

Thumbnails are stored as JPEG files at
`~/Library/Caches/no.blogspot.RawCull/Thumbnails/`. The filename is an MD5
hash of the source file's absolute path. Each cached thumbnail is ~494 KB
(512 px longest edge, JPEG quality 0.7).

`DiskCacheManager.load(for:)` spawns a `Task.detached` for the file read,
releasing the actor during I/O.

After a first full scan, the disk cache is ~400 MB for 809 files.

#### C. RAW extraction

```swift
guard let format = RawFormatRegistry.format(for: url) else { return }
let cgImage = try await format.extractThumbnail(
    from: url,
    maxDimension: CGFloat(targetSize),
    qualityCost: costPerPixel,
)
```

`format.extractThumbnail` resolves to `SonyThumbnailExtractor.extractSonyThumbnail`
for `.arw` and `NikonThumbnailExtractor.extractNikonThumbnail` for `.nef`. Both
extractors hop immediately to `DispatchQueue.global()` so the actor is not
blocked during the ~180–200 ms decode:

```swift
try await withCheckedThrowingContinuation { continuation in
    DispatchQueue.global(qos: .userInitiated).async {
        let image = try Self.extractSync(from: url, …)
        continuation.resume(returning: image)
    }
}
```

Internally each extractor calls `CGImageSourceCreateThumbnailAtIndex` which
uses the embedded JPEG preview inside the RAW where available, avoiding a
full RAW decode. For ARW 6.0 (RA16) files the Sony path falls back to
reading the embedded JPEG directly via `SonyMakerNoteParser.embeddedJPEGLocations`;
the Nikon path defers to ImageIO with `kCGImageSourceCreateThumbnailFromImageIfAbsent`
so the embedded preview is used when present.

After extraction the thumbnail is:
1. Stored in the RAM cache (`NSCache`) immediately.
2. Encoded to JPEG data and written to the disk cache via a background
   `Task.detached` — this write does not block the thumbnail pipeline.

### 3.3 Progress notification and ETA (fire-and-forget)

After each file completes, the UI is notified without blocking the pipeline:

```swift
private func notifyFileHandler(_ count: Int) {
    let handler = fileHandlers?.fileHandler
    Task { @MainActor in handler?(count) }
}
```

The `Task { @MainActor in }` delivers the update to SwiftUI without blocking
the current task. Thumbnail generation does not wait for the UI to finish
rendering before moving on to the next file.

The ETA is updated in the same fire-and-forget pattern. Rather than measuring
each task's own wall-clock duration, the algorithm tracks the **inter-arrival
time** — the elapsed time between consecutive completions — and averages the
last 10 samples:

```swift
private func updateEstimatedTime(for _: Date, itemsProcessed: Int) {
    let now = Date()
    if let lastTime = lastItemTime {
        processingTimes.append(now.timeIntervalSince(lastTime))
    }
    lastItemTime = now

    if itemsProcessed >= Self.minimumSamplesBeforeEstimation {
        let recentTimes = processingTimes.suffix(min(10, processingTimes.count))
        let avgTimePerItem = recentTimes.reduce(0, +) / Double(recentTimes.count)
        let estimatedSeconds = Int(avgTimePerItem * Double(totalFilesToProcess - itemsProcessed))
        let handler = fileHandlers?.estimatedTimeHandler
        Task { @MainActor in handler?(estimatedSeconds) }
    }
}
```

Estimation begins only after `minimumSamplesBeforeEstimation` (10) items have
completed, avoiding noisy early estimates when the first few tasks may be
subject to cold-start I/O latency.
