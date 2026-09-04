+++
author = "Thomas Evensen"
title = "Known Issues and Findings"
linkTitle = "Known Issues"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "Prioritized RawCull code-review findings and recommended remediations."
tags = ["rawcull", "issues", "code-review", "security"]
categories = ["technical details"]
weight = 90
+++

# Known Issues and Findings

This is a code-review pass over the main `RawCull` app target (excluding
`RawCullTests` and the external SPM packages). Overall the codebase is
unusually clean for its size: **no force-unwraps (`!`), no `try!`, no
force-casts (`as!`), no unguarded array `[0]` accesses, no `DispatchSemaphore`
or `Timer`/`NotificationCenter` leaks**, and every
`startAccessingSecurityScopedResource()` call has a matching
`stopAccessingSecurityScopedResource()` on all paths, including cancellation
and `deinit`. The findings below are the exceptions to that otherwise solid
baseline. Severities: **High** (real user-facing breakage or data-loss risk),
**Medium** (real bug/gap, narrow trigger conditions or degraded UX), **Low**
(code-quality / robustness / maintainability).

---

## 1. No escape hatch when a quit-time save fails — **Medium/High**

`Main/RawCullApp.swift`, `AppDelegate.applicationShouldTerminate`:

```swift
terminationTask = Task {
    let didSave = await viewModel.cullingModel.flushPersistence()
    if didSave {
        viewModel.stopActiveSecurityScopedAccess()
    }
    terminationTask = nil
    sender.reply(toApplicationShouldTerminate: didSave)
}
return .terminateLater
```

If `flushPersistence()` fails (e.g. the catalog's volume was ejected, disk is
full, or permissions changed), `didSave` is `false` and the app replies
`false` to `NSApplication` — **the app refuses to quit**. `RawCullMainView`
does show an alert in this situation (`persistenceErrorIsPresented`,
driven by `cullingModel.persistenceError`), but that alert only offers
**"Retry"** (and "Archive Damaged File" for load failures, not save
failures). There is no "Quit Without Saving" / "Force Quit" option, so a
user whose destination volume is genuinely gone has no in-app way to exit
cleanly — they must force-quit via the Dock or Activity Monitor, which is a
worse experience than a clearly-labeled data-loss confirmation.

**Suggested fix:** add a destructive "Quit Without Saving" button to the
persistence-failure alert, and have it call
`sender.reply(toApplicationShouldTerminate: true)` directly instead of
looping through `flushPersistence()` again.

## 2. Security-scope fallback path is likely dead code in the sandboxed build — **Medium**

`Model/ParametersRsync/ExecuteCopyFiles.swift`, `tryFallbackPath(_:key:)`:

```swift
private func tryFallbackPath(_ fallbackPath: String, key: String) -> URL? {
    let fallbackURL = URL(fileURLWithPath: fallbackPath)
    guard fallbackURL.startAccessingSecurityScopedResource() else { ... }
    ...
}
```

This calls `startAccessingSecurityScopedResource()` on a **plain
`file://` URL built from a string path**, not on a URL resolved from a
security-scoped bookmark or an `NSOpenPanel` selection. `RawCull.entitlements`
confirms the app runs under `com.apple.security.app-sandbox = true`. In a
sandboxed process, `startAccessingSecurityScopedResource()` only succeeds
for URLs that were actually granted through Powerbox (an open panel) or a
resolved security-scoped bookmark — calling it on an arbitrary path outside
the container will almost always return `false`. This makes the fallback
branch effectively unreachable/useless in production, while its companion
success-path log line ("Successfully accessed fallback path for ...") would
be misleading if it were ever hit. Recommend removing the fallback (relying
solely on bookmark resolution) or replacing it with a clear "please
reselect this folder" prompt routed through `NSOpenPanel`.

## 3. Entitlements may be missing a required file-access capability — **Medium (needs verification)**

`RawCull.entitlements` declares only:

```xml
<key>com.apple.security.application-groups</key> ... 
<key>com.apple.security.app-sandbox</key><true/>
```

There is no `com.apple.security.files.bookmarks.app-scope` or
`com.apple.security.files.user-selected.read-write` entry, despite the app's
core workflow depending on persisting security-scoped bookmarks
(`UserDefaults.standard.data(forKey: "sourceBookmark")` /
`"destBookmark"`, see `RawCullViewModel.swift` and
`ExecuteCopyFiles.getAccessedURL`) to regain access to user-chosen source
and destination folders **across app relaunches**. Document-scoped bookmarks
created directly from an `NSOpenPanel` grant typically don't require an
extra entitlement, but this is worth explicitly re-verifying against a real
signed build — if bookmark resolution silently fails after an update to
sandbox rules, users would lose access to previously configured catalogs
with only a generic "could not access folder" alert and no diagnostic path
back to the root cause.

## 4. Scan failures are completely silent (no log, no UI) — **Low**

`Actors/ScanFiles.swift`, `scanFiles(url:onProgress:)`:

```swift
} catch {
    // Logger.process.warning("Scan Error: \(error)")
    return []
}
```

Any failure enumerating the catalog directory (permission denied, missing
folder, I/O error) is swallowed to an empty file list with **the log line
commented out** — there is no OSLog entry and no user-facing alert, so a
scan failure is indistinguishable from "this folder is genuinely empty."
This makes field diagnosis of access problems unnecessarily hard.
Uncomment/restore the log line at minimum; consider surfacing a
non-blocking banner for repeated scan failures the way persistence failures
already are.

## 5. Minor duplicate-decode race in thumbnail request coalescing — **Low**

`Actors/RequestThumbnail.swift`, `cancelWaiter`/`enqueue`: when the *last*
waiter for a coalesced request cancels, the in-flight entry is removed from
`inFlightRequests` and `task.cancel()` is called, but cancellation is
cooperative — if the underlying decode is mid-flight inside
`rawLoader.thumbnailCGImage` (which doesn't check `Task.isCancelled`
internally) and a **new** request for the same file arrives before the old
task notices cancellation, a second concurrent decode of the same file will
start. This wastes CPU/disk I/O but is not a correctness bug: the generation
check in `finishRequest` ensures the stale result is discarded safely and no
continuation is double-resumed. Consider making the old task's completion
check-and-reuse an already-superseding in-flight entry instead of always
starting a fresh decode.

## 6. Commented-out `Logger` calls scattered through the codebase — **Low**

`grep -rn '^\s*// Logger\.'` finds 13 debug log lines left commented out
(e.g. in `RequestThumbnail.swift`, `ScanFiles.swift`). Harmless, but they're
dead debugging leftovers that should either be deleted or restored/gated
behind a debug flag — as-is they add noise for future readers wondering if
they're intentionally disabled instrumentation or accidental omissions.

---

## What was checked and found clean

- **Force-unwraps / `try!` / `as!`**: none in the app target.
- **Security-scoped resource pairing**: every `start...` has a matching
  `stop...` on every return path, including error paths, task cancellation,
  and `isolated deinit` (`RawCullViewModel`, `ExecuteCopyFiles`, `ScanFiles`,
  `OpencatalogView`).
- **Debounced-save correctness** (`CullingModel.scheduleSave`): revision
  counters correctly prevent a stale debounced write from clobbering newer
  in-memory state; `flushPersistence`/`retryPersistence` correctly cancel any
  pending debounce and persist the *current* snapshot, not a stale captured
  one.
- **Array indexing**: every `array[0]`-style access found is either guarded
  by a preceding `!isEmpty` check or targets an Apple-guaranteed
  non-empty system directory list.
- **Swift 6 concurrency**: `SWIFT_VERSION = 6.0` is set for all targets,
  which enables complete concurrency checking at the language-mode level
  regardless of the separate (Swift 5-only) `SWIFT_STRICT_CONCURRENCY`
  build setting — the apparent inconsistency in `project.pbxproj` (only the
  test target sets `SWIFT_STRICT_CONCURRENCY = complete` explicitly) is not
  a functional gap.
