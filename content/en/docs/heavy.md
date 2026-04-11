+++
author = "Thomas Evensen"
title = "Synchronous Code"
date = "2026-02-19"
tags = ["heavy"]
categories = ["technical details"]
+++

# A Guide to Handling Heavy Synchronous Code in Swift Concurrency

This post explains why CPU-intensive synchronous code (such as image decoding via ImageIO) must be dispatched off the Swift Concurrency thread pool, and shows the correct patterns RawCull uses to do so.

## `DispatchQueue.global(qos:)` — QoS Levels Compared

The key difference is **priority and resource allocation** by the system.

---

### `.userInitiated`
- **Priority:** High (just below `.userInteractive`)
- **Use case:** Work the **user directly triggered** and is actively waiting for — e.g., loading a document they tapped, parsing data to display a screen
- **Expected duration:** Near-instantaneous to a few seconds
- **System behavior:** Gets **more CPU time and higher thread priority** — the system treats this as urgent
- **Energy impact:** Higher

---

### `.utility`
- **Priority:** Low-medium
- **Use case:** Long-running work the user is **aware of but not blocked by** — e.g., downloading files, importing data, periodic syncs, progress-bar tasks
- **Expected duration:** Seconds to minutes
- **System behavior:** Balanced CPU/energy trade-off; the system **throttles this more aggressively** under load or low battery
- **Energy impact:** Lower (system may apply energy efficiency optimizations)

---

### Quick Comparison

| | `.userInitiated` | `.utility` |
|---|---|---|
| **Priority** | High | Low-medium |
| **User waiting?** | Yes, directly | Aware but not blocked |
| **Duration** | < a few seconds | Seconds to minutes |
| **CPU allocation** | Aggressive | Conservative |
| **Battery impact** | Higher | Lower |
| **Thread pool** | Higher-priority threads | Lower-priority threads |

---

### Rule of thumb
```swift
// User tapped "Load" and is staring at a spinner → userInitiated
DispatchQueue.global(qos: .userInitiated).async {
    let data = loadCriticalData()
}

// Background sync / download with a progress bar → utility
DispatchQueue.global(qos: .utility).async {
    downloadLargeFile()
}
```

**If you use `.userInitiated` for everything**, you waste battery and CPU on non-urgent work. **If you use `.utility` for user-blocking tasks**, the UI will feel sluggish because the system may deprioritize the work.

## 1. The Core Problem: The Swift Cooperative Thread Pool
To understand why heavy synchronous code breaks modern Swift, you have to understand the difference between older Apple code (Grand Central Dispatch / GCD) and new Swift Concurrency.

*   **GCD (`DispatchQueue`)** uses a dynamic thread pool. If a thread gets blocked doing heavy work, GCD notices and spawns a new thread. This prevents deadlocks but causes **Thread Explosion** (which drains memory and battery).
*   **Swift Concurrency (`async`/`await`/`Task`)** uses a **fixed-size cooperative thread pool**. It strictly limits the number of background threads to exactly the number of CPU cores your device has (e.g., 6 cores = exactly 6 threads). It will *never* spawn more.

Because there are so few threads, Swift relies on **cooperation**. When an `async` function hits an `await`, it says: *"I'm pausing to wait for something. Take my thread and give it to another task!"* This allows 6 threads to juggle thousands of concurrent tasks.

### The "Choke" (Thread Pool Starvation)
If you run heavy synchronous code (code without `await`) on the Swift thread pool, it hijacks the thread and refuses to give it back. 
If you request 6 heavy image extractions at the same time, all 6 Swift threads are paralyzed. Your entire app's concurrency system freezes until an image finishes. Network requests halt, and background tasks deadlock.

---

## 2. What exactly is "Blocking Synchronous Code"?
**Synchronous code** executes top-to-bottom without ever pausing (it lacks the `await` keyword). **Blocking code** is synchronous code that takes a "long time" to finish (usually >10–50 milliseconds), thereby holding a thread hostage.

### The 3 Types of Blocking Code:
1.  **Heavy CPU-Bound Work:** Number crunching, image processing (`CoreGraphics`, `ImageIO`), video encoding, parsing massive JSON files. 
2.  **Synchronous I/O:** Reading massive files synchronously (e.g., `Data(contentsOf: URL)`) or older synchronous database queries. The thread is completely frozen waiting for the hard drive.
3.  **Locks and Semaphores:** Using `DispatchSemaphore.wait()` or `NSLock` intentionally pauses a thread. (Apple strictly forbids these inside Swift Concurrency).

### The Checklist to Identify Blocking Code:
Ask yourself these questions about a function:
1.  Does it lack the `async` keyword in its signature?
2.  Does it lack internal `await` calls (or `await Task.yield()`)?
3.  Does it take more than a few milliseconds to run?
4.  Is it a "Black Box" from an Apple framework (like `ImageIO`) or C/C++?

If the answer is **Yes**, it is blocking synchronous code and **does not belong in the Swift Concurrency thread pool.**

---

## 3. The Traps: Why `Task` and `Actor` Don't Fix It

It is highly intuitive to try and fix blocking code using modern Swift features. However, these common approaches are dangerous traps:

### Trap 1: Using `Task` or `Task.detached`
```swift
// ❌ TRAP: Still causes Thread Pool Starvation!
func extract() async throws -> CGImage {
    return try await Task.detached {
        return try Self.extractSync() // Blocks one of the 6 Swift threads
    }.value
}
```
`Task` and `Task.detached` do **not** create new background threads. They simply place work onto that same strict 6-thread cooperative pool. It might seem to "work" if you only test one image at a time, but at scale, it will deadlock your app.

### Trap 2: Putting it inside an `actor`
Actors process their work one-by-one to protect state. However, **Actors do not have their own dedicated threads**. They borrow threads from the cooperative pool.
If you run heavy sync code inside an Actor, you cause a **Double Whammy**:
1.  **Thread Pool Starvation:** You choked one of the 6 Swift workers.
2.  **Actor Starvation:** The Actor is locked up and cannot process any other messages until the heavy work finishes.

### Trap 3: Using `nonisolated`
Marking an Actor function as `nonisolated` just means *"this doesn't touch the Actor's private state."* It prevents Actor Starvation, but the function still physically runs on the exact same 6-thread pool, causing Thread Pool Starvation.

---

## 4. The Correct Solution: The GCD Escape Hatch

Apple's official stance is that if you have heavy, blocking synchronous code that you cannot modify, **Grand Central Dispatch (GCD) is still the correct tool for the job.**

By wrapping the work in `DispatchQueue.global().async` and `withCheckedThrowingContinuation`, you push the heavy work *out* of Swift's strict 6-thread pool and *into* GCD's flexible thread pool (which is allowed to spin up extra threads).

This leaves the precious Swift Concurrency threads completely free to continue juggling all the other `await` tasks in your app.

### Two functions in RawCull use DispatchQueue.global

extract JPGs from ARW files

```swift
static func extractEmbeddedPreview(
        from arwURL: URL,
        fullSize: Bool = false
    ) async -> CGImage? {
        let maxThumbnailSize: CGFloat = fullSize ? 8640 : 4320

        return await withCheckedContinuation { (continuation: CheckedContinuation<CGImage?, Never>) in
            // Dispatch to GCD to prevent Thread Pool Starvation
            DispatchQueue.global(qos: .utility).async {

                guard let imageSource = CGImageSourceCreateWithURL(arwURL as CFURL, nil) else {
                    Logger.process.warning("PreviewExtractor: Failed to create image source")
                    continuation.resume(returning: nil)
                    return
                }

                let imageCount = CGImageSourceGetCount(imageSource)
                var targetIndex: Int = -1
                var targetWidth = 0

                // 1. Find the LARGEST JPEG available
                for index in 0 ..< imageCount {
                    guard let properties = CGImageSourceCopyPropertiesAtIndex(
                        imageSource,
                        index,
                        nil
                    ) as? [CFString: Any]
                    else {
                        Logger.process.debugMessageOnly("enum: extractEmbeddedPreview(): Index \(index) - Failed to get properties")
                        continue
                    }

                    let hasJFIF = (properties[kCGImagePropertyJFIFDictionary] as? [CFString: Any]) != nil
                    let tiffDict = properties[kCGImagePropertyTIFFDictionary] as? [CFString: Any]
                    let compression = tiffDict?[kCGImagePropertyTIFFCompression] as? Int
                    let isJPEG = hasJFIF || (compression == 6)

                    if let width = getWidth(from: properties) {
                        if isJPEG, width > targetWidth {
                            targetWidth = width
                            targetIndex = index
                        }
                    }
                }

                guard targetIndex != -1 else {
                    Logger.process.warning("PreviewExtractor: No JPEG found in file")
                    continuation.resume(returning: nil)
                    return
                }

                let requiresDownsampling = CGFloat(targetWidth) > maxThumbnailSize
                let result: CGImage?

                // 2. Decode & Downsample using ImageIO directly
                if requiresDownsampling {
                    Logger.process.info("PreviewExtractor: Native downsampling to \(maxThumbnailSize)px")

                    // THESE ARE THE MAGIC OPTIONS that replace your resizeImage() function
                    let options: [CFString: Any] = [
                        kCGImageSourceCreateThumbnailFromImageAlways: true,
                        kCGImageSourceCreateThumbnailWithTransform: true,
                        kCGImageSourceThumbnailMaxPixelSize: Int(maxThumbnailSize)
                    ]

                    result = CGImageSourceCreateThumbnailAtIndex(imageSource, targetIndex, options as CFDictionary)
                } else {
                    Logger.process.info("PreviewExtractor: Using original preview size (\(targetWidth)px)")

                    // Your original standard decoding options
                    let decodeOptions: [CFString: Any] = [
                        kCGImageSourceShouldCache: true,
                        kCGImageSourceShouldCacheImmediately: true
                    ]

                    result = CGImageSourceCreateImageAtIndex(imageSource, targetIndex, decodeOptions as CFDictionary)
                }

                continuation.resume(returning: result)
            }
        }
    }
```

extract thumbnails

```swift
import AppKit
import Foundation

enum SonyThumbnailExtractor {
    /// Extract thumbnail using generic ImageIO framework.
    /// - Parameters:
    ///   - url: The URL of the RAW image file.
    ///   - maxDimension: Maximum pixel size for the longest edge of the thumbnail.
    ///   - qualityCost: Interpolation cost.
    /// - Returns: A `CGImage` thumbnail.
    static func extractSonyThumbnail(
        from url: URL,
        maxDimension: CGFloat,
        qualityCost: Int = 4
    ) async throws -> CGImage {
        // We MUST explicitly hop off the current thread.
        // Since we are an enum and static, we have no isolation of our own.
        // If we don't do this, we run on the caller's thread (the Actor), causing serialization.

        try await withCheckedThrowingContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                do {
                    let image = try Self.extractSync(
                        from: url,
                        maxDimension: maxDimension,
                        qualityCost: qualityCost
                    )
                    continuation.resume(returning: image)
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }
```

---

## 5. The "Modern Swift" Alternative (If you own the code)
If `extractSync` was your own custom Swift code (and not an opaque framework like `ImageIO`), the truly "Modern Swift" way to fix it is to rewrite the synchronous loop to be cooperative. 

You do this by sprinkling `await Task.yield()` inside heavy loops to voluntarily give the thread back:

```swift
func extractSyncCodeMadeAsync() async -> CGImage {
    for pixelRow in image {
        process(pixelRow)
        
        // Every few rows, pause and let another part of the app use the thread!
        if pixelRow.index % 10 == 0 {
            await Task.yield() 
        }
    }
}
```
If you can do this, you don't need `DispatchQueue`! But if you are using black-box code that you can't add `await` to, the **GCD Escape Hatch** is the correct, Apple-approved architecture.

---

## Summary

Heavy synchronous code — especially CPU-bound ImageIO work — must never run directly on Swift's cooperative thread pool. The GCD escape hatch (`DispatchQueue.global` + `withCheckedContinuation`) moves that work onto GCD's flexible thread pool, leaving Swift Concurrency threads free. RawCull uses this pattern for both thumbnail extraction (`userInitiated` priority) and JPEG preview extraction (`utility` priority).