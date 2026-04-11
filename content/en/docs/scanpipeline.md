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
model, five performance bugs that were found and fixed, and the measured results
on a real catalog of 809 Sony A1 ARW files stored on an external 800 MB/s SSD.

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

EXIF metadata and Sony MakerNote focus points are extracted in a **single
combined task group pass**. Each task opens the file once and returns a pair:

```swift
let pairs: [(FileItem, DecodeFocusPoints?)] = await withTaskGroup(
    of: (FileItem, DecodeFocusPoints?).self
) { group in
    for fileURL in contents {
        guard fileURL.pathExtension.lowercased() == "arw" else { continue }
        let progress = onProgress
        let count = discoveredCount
        Task { @MainActor in progress?(count) }   // fire-and-forget UI update
        group.addTask {
            let res      = try? fileURL.resourceValues(forKeys: Set(keys))
            let exifData = self.extractExifData(from: fileURL)   // nonisolated
            let fileItem = FileItem(url: fileURL, name: res?.name ?? …,
                                    exifData: exifData)
            let focusPoint: DecodeFocusPoints? =
                SonyMakerNoteParser.focusLocation(from: fileURL).map {
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

let result      = pairs.map(\.0)
let nativePoints = pairs.compactMap(\.1)
```

For each ARW file a task is added to the group. The loop itself is non-blocking:
progress callbacks are fired to the main actor without `await`, so the loop
completes almost instantly and the task group fills up immediately.

Each task calls both `extractExifData` and `SonyMakerNoteParser.focusLocation`
**without hopping back to the actor** — both methods are `nonisolated`, so they
run directly on the global cooperative thread pool. This eliminates the separate
second file-open pass that a dedicated `extractNativeFocusPoints` function
previously required.

`extractExifData` uses Apple's ImageIO framework:

```swift
private nonisolated func extractExifData(from url: URL) -> ExifMetadata? {
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) …
```

`CGImageSourceCopyPropertiesAtIndex` reads the TIFF/EXIF header from the file.
For a Sony ARW this is the first few kilobytes — not the full ~50 MB RAW image.

**Measured throughput:** ~2–3 ms per file. 809 files concurrently ≈ **3–4 seconds**.

### 2.3 Focus point extraction and JSON fallback

Focus points are now extracted inline in the same task group as EXIF (see 2.2).
After the group completes, the results are resolved:

```swift
decodedFocusPoints = nativePoints.isEmpty
    ? decodeFocusPointsJSON(from: url)
    : nativePoints
```

If native MakerNote extraction yielded no results — for example, files captured
before the feature was available, or non-A1 bodies — `ScanFiles` falls back to
reading a `focuspoints.json` file from the catalog folder. That JSON is decoded
synchronously with a plain `JSONDecoder`; no actor-isolated types are touched:

```swift
private func decodeFocusPointsJSON(from url: URL) -> [DecodeFocusPoints]? {
    let fileURL = url.appendingPathComponent("focuspoints.json")
    guard FileManager.default.fileExists(atPath: fileURL.path) else { return nil }
    let data = try Data(contentsOf: fileURL)
    return try JSONDecoder().decode([DecodeFocusPoints].self, from: data)
}
```

#### What `SonyMakerNoteParser` does

Sony ARW is TIFF-based. Focus location lives at:

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

**Measured throughput:** ~0.3–0.4 ms per file. 809 files concurrently ≈ **< 1 second**.

---

## 3. Phase 2 — Thumbnail generation (`ScanAndCreateThumbnails`)

**File:** `RawCull/Actors/ScanAndCreateThumbnails.swift`

### 3.1 File discovery and sliding-window task group

`preloadCatalog` delegates directory scanning to a dedicated `DiscoverFiles`
actor before building the task group:

```swift
let urls = await DiscoverFiles().discoverFiles(at: catalogURL, recursive: false)
totalFilesToProcess = urls.count
await fileHandlers?.maxfilesHandler(urls.count)
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
let cgImage = try await SonyThumbnailExtractor.extractSonyThumbnail(
    from: url,
    maxDimension: CGFloat(targetSize),
    qualityCost: costPerPixel
)
```

`SonyThumbnailExtractor` hops immediately to `DispatchQueue.global()` so the
actor is not blocked during the ~180–200 ms decode:

```swift
try await withCheckedThrowingContinuation { continuation in
    DispatchQueue.global(qos: .userInitiated).async {
        let image = try Self.extractSync(from: url, …)
        continuation.resume(returning: image)
    }
}
```

Internally this calls `CGImageSourceCreateThumbnailAtIndex` which uses the
embedded JPEG preview inside the ARW where available, avoiding a full RAW
decode.

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
