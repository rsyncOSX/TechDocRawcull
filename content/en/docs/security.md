+++
author = "Thomas Evensen"
title = "Security-Scoped URLs"
date = "2026-02-05"
tags = ["security"]
categories = ["technical details"]
+++

Security-scoped URLs are a cornerstone of macOS App Sandbox security. RawCull uses them to gain persistent, user-approved access to source and destination folders while remaining fully sandbox-compliant. This article walks through exactly how the implementation works, tracing the code from user interaction through to file operations.

---

### What Are Security-Scoped URLs?

A security-scoped URL is a special file URL that carries a cryptographic capability granted by macOS, representing explicit user consent to access a specific file or folder. Without it, a sandboxed app cannot read or write anything outside its own container.

Key properties:

- Created only from user-granted file access (file picker, drag-and-drop)
- Grants temporary access to files outside the app sandbox
- Must be explicitly activated (`startAccessingSecurityScopedResource()`) before use and deactivated (`stopAccessingSecurityScopedResource()`) after
- Can be serialized as a **bookmark** — a persistent token stored in `UserDefaults` that survives app restarts

**Core API:**

```swift
// Activate access — must be called before any file operations on the URL
let granted = url.startAccessingSecurityScopedResource()  // returns Bool

// Deactivate — must always be paired with a successful start call
url.stopAccessingSecurityScopedResource()

// Serialize to persistent bookmark data
let bookmarkData = try url.bookmarkData(
    options: .withSecurityScope,
    includingResourceValuesForKeys: nil,
    relativeTo: nil
)

// Restore from bookmark (across app launches)
var isStale = false
let restoredURL = try URL(
    resolvingBookmarkData: bookmarkData,
    options: .withSecurityScope,
    relativeTo: nil,
    bookmarkDataIsStale: &isStale
)
```

---

### Architecture in RawCull

RawCull's security-scoped URL system has three distinct layers, each with a specific responsibility.

---

#### Layer 1 — Initial User Selection (`OpencatalogView`)

`OpencatalogView` presents the macOS folder picker using SwiftUI's `.fileImporter()` modifier. When the user selects a folder, the resulting URL is a short-lived security-scoped URL. The view immediately converts it into a persistent bookmark.

**File:** `RawCull/Views/CopyFiles/OpencatalogView.swift`

```swift
.fileImporter(
    isPresented: $isImporting,
    allowedContentTypes: [.directory]
) { result in
    switch result {
    case .success(let url):
        // Activate access immediately — required to create a bookmark
        guard url.startAccessingSecurityScopedResource() else {
            Logger.process.errorMessageOnly("Failed to start accessing resource")
            return
        }

        // Store the path string for immediate UI use
        selecteditem = url.path

        // Serialize the URL to a persistent bookmark while access is active
        do {
            let bookmarkData = try url.bookmarkData(
                options: .withSecurityScope,
                includingResourceValuesForKeys: nil,
                relativeTo: nil
            )
            UserDefaults.standard.set(bookmarkData, forKey: bookmarkKey)
        } catch {
            Logger.process.warning("Could not create bookmark: \(error)")
        }

        // Release access — will be reacquired via bookmark when needed
        url.stopAccessingSecurityScopedResource()

    case .failure(let error):
        Logger.process.errorMessageOnly("File picker error: \(error)")
    }
}
```

`bookmarkKey` is either `"sourceBookmark"` or `"destBookmark"` — the two folder roles in RawCull.

**What this layer guarantees:**
- Bookmark is created while access is still active (the only valid window for bookmark creation)
- Access is released immediately after — the bookmark takes over for future launches
- The path is captured before releasing access, so the UI can display it without holding an open security scope

---

#### Layer 2 — Bookmark Restoration (`ExecuteCopyFiles`)

When the user initiates a copy operation on a subsequent launch, `ExecuteCopyFiles` resolves the stored bookmarks back into live, access-granted URLs.

**File:** `RawCull/Model/ParametersRsync/ExecuteCopyFiles.swift`

```swift
func getAccessedURL(fromBookmarkKey key: String, fallbackPath: String) -> URL? {
    // Primary path: restore from persisted bookmark
    if let bookmarkData = UserDefaults.standard.data(forKey: key) {
        do {
            var isStale = false

            let url = try URL(
                resolvingBookmarkData: bookmarkData,
                options: .withSecurityScope,
                relativeTo: nil,
                bookmarkDataIsStale: &isStale
            )

            // Activate access on the resolved URL
            guard url.startAccessingSecurityScopedResource() else {
                Logger.process.errorMessageOnly("Failed to start accessing bookmark for \(key)")
                return tryFallbackPath(fallbackPath, key: key)
            }

            // Warn if the folder was moved (bookmark is stale)
            if isStale {
                Logger.process.warning("Bookmark is stale for \(key) — user may need to reselect")
            }

            return url  // Caller is responsible for stopAccessingSecurityScopedResource()

        } catch {
            Logger.process.errorMessageOnly("Bookmark resolution failed for \(key): \(error)")
            return tryFallbackPath(fallbackPath, key: key)
        }
    }

    return tryFallbackPath(fallbackPath, key: key)
}

private func tryFallbackPath(_ fallbackPath: String, key: String) -> URL? {
    let fallbackURL = URL(fileURLWithPath: fallbackPath)
    guard fallbackURL.startAccessingSecurityScopedResource() else {
        Logger.process.errorMessageOnly("Failed to access fallback path for \(key)")
        return nil
    }
    return fallbackURL
}
```

The returned URL has `startAccessingSecurityScopedResource()` already called. The calling code in `ExecuteCopyFiles` is responsible for calling `stopAccessingSecurityScopedResource()` on each URL once the rsync operation completes.

**What this layer handles:**
- Normal case: bookmark resolves cleanly → URL returned with access active
- Stale bookmark: folder was moved → logged as warning, access still attempted
- Bookmark resolution throws: falls back to direct path access
- No bookmark stored at all: falls back to direct path access

---

#### Layer 3 — Scoped Access During File Operations (`ScanFiles`)

When scanning a directory for supported RAW files (`.arw`, `.nef`), the `ScanFiles` actor activates and deactivates security-scoped access for the duration of the scan only.

**File:** `RawCull/Actors/ScanFiles.swift`

```swift
actor ScanFiles {
    func scanFiles(
        url: URL,
        onProgress: (@MainActor @Sendable (_ count: Int) -> Void)? = nil,
    ) async -> [FileItem] {
        // Activate access for this URL
        guard url.startAccessingSecurityScopedResource() else { return [] }
        // defer guarantees deactivation even if the function throws or returns early
        defer { url.stopAccessingSecurityScopedResource() }

        let keys: [URLResourceKey] = [
            .nameKey, .fileSizeKey, .contentTypeKey, .contentModificationDateKey
        ]
        guard let contents = try? FileManager.default.contentsOfDirectory(
            at: url,
            includingPropertiesForKeys: keys,
            options: [.skipsHiddenFiles],
        ) else { return [] }

        // RawFormatRegistry.format(for:) picks SonyRawFormat / NikonRawFormat
        // based on extension; the scan loop itself stays vendor-agnostic.
        return await scanAllSupportedFormats(contents, keys: keys, onProgress: onProgress)
    }
}
```

The `defer` pattern is critical here: it guarantees that `stopAccessingSecurityScopedResource()` is called regardless of whether the function completes normally, returns early, or the Swift runtime unwinds the stack. This prevents security-scoped resources from being "leaked" (left open indefinitely).

**Actor isolation**: Because `ScanFiles` is a Swift actor, all file operations on its state are serialized by the runtime — concurrent reads of the same directory cannot race each other.

---

### Global Access Tracking in `RawCullViewModel`

The main view model maintains a comprehensive registry of all URLs for which `startAccessingSecurityScopedResource()` has been called, ensuring nothing is left open when the app quits.

**File:** `RawCull/Model/ViewModels/RawCullViewModel.swift`

```swift
@Observable @MainActor
final class RawCullViewModel {
    private var securityScopedURLs: Set<URL> = []

    func trackSecurityScopedAccess(for url: URL) {
        securityScopedURLs.insert(url)
    }

    func stopSecurityScopedAccess(for url: URL) {
        guard securityScopedURLs.contains(url) else { return }
        url.stopAccessingSecurityScopedResource()
        securityScopedURLs.remove(url)
    }

    deinit {
        // Release all remaining security-scoped access on teardown
        for url in securityScopedURLs {
            url.stopAccessingSecurityScopedResource()
        }
    }
}
```

This acts as a safety net: even if a call path omits an explicit `stop`, the `deinit` cleans up everything before the app exits. Combined with `defer` in the actors, this gives double coverage against resource leaks.

---

### End-to-End Flow

```
User selects destination folder via file picker
    ↓
OpencatalogView.fileImporter result handler
    1. url.startAccessingSecurityScopedResource()
    2. selecteditem = url.path                    (UI binding)
    3. bookmarkData = try url.bookmarkData(options: .withSecurityScope)
    4. UserDefaults.set(bookmarkData, forKey: "destBookmark")
    5. url.stopAccessingSecurityScopedResource()
    ↓
    [App may be quit and relaunched here]
    ↓
User initiates copy operation
    ↓
ExecuteCopyFiles.performCopyTask()
    1. getAccessedURL(fromBookmarkKey: "sourceBookmark", ...)
       → resolves bookmark → startAccessingSecurityScopedResource() → returns URL
    2. getAccessedURL(fromBookmarkKey: "destBookmark", ...)
       → resolves bookmark → startAccessingSecurityScopedResource() → returns URL
    3. Builds rsync argument list using both paths
    4. Spawns /usr/bin/rsync via RsyncProcessStreaming
    5. After rsync completes:
       sourceURL.stopAccessingSecurityScopedResource()
       destURL.stopAccessingSecurityScopedResource()
    ↓
ScanFiles.scanFiles(url: sourceURL)
    1. url.startAccessingSecurityScopedResource()
    2. defer { url.stopAccessingSecurityScopedResource() }
    3. FileManager.contentsOfDirectory(at: url, ...)
    4. Returns [FileItem]   ← defer fires here, access released
    ↓
RawCullViewModel.deinit (on app quit)
    → stopAccessingSecurityScopedResource() for any remaining tracked URLs
```

---

### Security Model Summary

| Aspect | Implementation | Guarantee |
|--------|----------------|-----------|
| **User consent** | File picker only — no programmatic path construction | App never accesses a folder the user did not explicitly choose |
| **Persistence** | Bookmark serialized to `UserDefaults` | User does not re-select folders on every launch |
| **Minimal scope duration** | `defer` and explicit `stop` calls bound access to the operation | Security-scoped access is held only as long as needed |
| **Leak prevention** | `Set<URL>` in view model + `deinit` cleanup | No access token outlives the app session |
| **Stale bookmark detection** | `bookmarkDataIsStale` checked on every resolve | User is informed if a folder has been moved |
| **Fallback resilience** | Direct path access if bookmark resolution fails | Graceful degradation, operation still attempted |
| **Audit trail** | `OSLog` records every start, stop, failure, and stale event | Security events are observable via Console.app |

---

### Common Pitfalls (and How RawCull Avoids Them)

**1. Forgetting to call `startAccessingSecurityScopedResource()` before file operations**
→ RawCull guards every file operation with an explicit start call; failure returns `nil` or `[]` rather than crashing.

**2. Not calling `stopAccessingSecurityScopedResource()` — leaking the scope**
→ `defer` in actors and `deinit` in the view model provide two independent cleanup layers.

**3. Creating a bookmark while access is not active**
→ `OpencatalogView` always creates the bookmark inside the `startAccessing…` / `stopAccessing…` window.

**4. Ignoring the `isStale` flag**
→ RawCull logs a warning when `bookmarkDataIsStale` is `true`, making stale bookmarks visible in diagnostics.

**5. Using the resolved URL after calling `stop`**
→ The view model tracks active URLs and guards against double-stop via the `contains` check before removing from the set.
