+++
author = "Thomas Evensen"
title = "Known Issues and Findings"
linkTitle = "Known Issues"
date = "2026-09-04"
lastmod = "2026-09-15"
description = "Prioritized RawCull code-review findings, resolved items, and verification gaps."
tags = ["rawcull", "issues", "code-review", "security"]
categories = ["technical details"]
weight = 90
+++

# Known Issues and Findings

This page records findings verified against the current app source. It separates
open behavior from items fixed since the September 4 review so old remediation
advice is not mistaken for current implementation guidance.

## Open Findings

### 1. App-scope bookmark entitlements need signed-build verification — Medium

`RawCull.entitlements` currently declares the app sandbox and the Managed
Background Assets application group, but not an explicit
`com.apple.security.files.bookmarks.app-scope` or
`com.apple.security.files.user-selected.read-write` key. The active catalog is
Powerbox-selected and the copy destination is persisted as `destBookmark`.

This is a verification item, not proof of a failure. Exercise catalog and
destination access across relaunch in the actual signed distribution build. If
bookmark resolution fails under the shipping sandbox, add the required
capability and retain the existing “reopen/reselect” recovery messages.

### 2. Directory-enumeration failures are still silent — Low

`Actors/ScanFiles.swift` still catches a directory-enumeration error and returns
an empty result while its warning log remains commented out. Permission, missing
volume, and I/O failures can therefore look like an empty catalog. Restore a
diagnostic at minimum and consider a non-blocking user-facing failure state.

### 3. Last-waiter cancellation can briefly duplicate a thumbnail decode — Low

When the last waiter leaves an exact-key `RequestThumbnail` request, the actor
removes the in-flight entry and cooperatively cancels the producer. A new waiter
can start another producer before the old blocking decode observes
cancellation. Generation checks still discard stale completion safely, so this
is wasted work rather than a correctness failure.

### 4. Commented logger calls remain — Low

Commented `Logger` statements remain in scan, cache, and thumbnail paths. They
should either be removed or restored behind deliberate logging policy so they
do not look like accidentally disabled diagnostics.

## Resolved Since The Previous Review

### Quit-time persistence recovery

`AppDelegate.applicationShouldTerminate(_:)` now delegates to its testable
`beginTermination(...)` lifecycle. A failed flush presents Retry, Cancel, and the
destructive **Quit Without Saving** choice. `QuitRecoveryTests.swift` covers
successful save, retry, cancel, and discard behavior, and only one termination
task can be active.

### Copy security-scope fallback

The plain-path fallback was removed. `ExecuteCopyFiles` uses the selected
catalog URL as the source and requires `destBookmark` for the destination. It
refreshes stale destination bookmarks while access is active and returns clear
reopen/reselect messages on failure.

### Copy result integrity

Process termination now produces a typed `CopyOutcome` and retains an immutable
`CopyOperation` snapshot. Failure output is included in details; result titles
distinguish completed, incomplete, and cancelled copies/dry runs. Startup and
completion tests cover these paths.

### Export filename collisions

`SaveJPGImage` uses filesystem-enforced creation without overwriting and retries
with numeric suffixes. Concurrent exports and case-insensitive collisions no
longer overwrite an existing JPEG.

## Review Baseline

The app target still avoids force unwraps, `try!`, force casts, and blocking
semaphores in production paths. Swift 6 language mode supplies complete
concurrency checking. Continue to treat security-scope pairing, revisioned
persistence, cancellation ownership, and stale-result guards as executable
invariants backed by focused tests rather than one-time review conclusions.
