+++
author = "Thomas Evensen"
title = "Export and Copy Pipeline"
linkTitle = "Export / Copy Pipeline"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "The one-way rsync-backed pipeline RawCull uses to export selected photographs."
tags = ["rawcull", "export", "rsync", "security-scoped-urls"]
categories = ["technical details"]
weight = 40
+++

# Export / Copy Pipeline (rsync)

Once files are rated, RawCull needs to get the keepers out to another
folder (a backup drive, a delivery folder, etc.). It does this by shelling
out to the system's `/usr/bin/rsync`, rather than using `FileManager` copy
APIs directly. This document explains that pipeline and, importantly, why
the code around it uses vocabulary ("synchronize", "offsite server", "SSH
parameters") that has nothing to do with what RawCull actually does.

## RawCull is not a sync tool

`RawCullViewModel`/`CullingModel`/the export UI only ever perform a
**one-way copy**: selected source files → a destination folder, on the same
Mac. There is no two-way sync, no remote host, no SSH. The rsync-flavored
naming survives because RawCull reuses configuration types and helper
packages (`RsyncArguments`, `RsyncProcessStreaming`, `ParseRsyncOutput`,
`DecodeEncodeGeneric`) from the author's earlier *RsyncOSX* project, which
did support real two-way remote sync. Recognizing this up front will save
you time — several fields exist purely because a shared type requires them,
not because RawCull uses them:

| Name you'll see | What it actually means in RawCull |
|---|---|
| `SynchronizeConfiguration.task = "synchronize"` | Hardcoded; RawCull only ever runs one "task" kind (copy). |
| `localCatalog` / `offsiteCatalog` | Local source folder / local destination folder — never remote. |
| `offsiteServer` | Always empty/`"localhost"`; unused. |
| `offsiteUsername`, `sshport`, `sshkeypathandidentityfile` | Unused SSH fields from the shared config struct. |
| `RemoteDataNumbers` / `PrepareOutputFromRsync` | Parses **local** rsync stdout; "remote" refers to rsync's own terminology for the far side of a transfer, not a network host. |
| `ParametersRsync/` folder name | Houses copy-operation config, not persistent sync profiles. |

## Configuration

`SynchronizeConfiguration` (`Model/ParametersRsync/SynchronizeConfiguration.swift`)
is a plain struct created fresh per copy operation — not a saved profile.
The fields RawCull actually uses are `localCatalog` (source),
`offsiteCatalog` (destination), and `rsyncVersion3` (`false` by default,
since macOS ships **openrsync**, a BSD rewrite, as `/usr/bin/rsync`; set it
`true` only if the user has installed real GNU rsync 3, which changes how
`RemoteDataNumbers` parses the summary output). `parameter8`–`parameter14`
are optional passthrough rsync flags defined by the shared `RsyncArguments`
package but not currently exposed in RawCull's UI — a hook for future power
users.

`Params.swift` and `ArgumentsSynchronize.swift` translate a
`SynchronizeConfiguration` plus the export options (dry-run, minimum
rating, tagged-only) into the actual argument array passed to rsync, e.g.:

```
["-avc", "--itemize-changes", "--update", "--from0",
 "--files-from=/var/tmp/copyfilelist-<uuid>.list0",
 "<source folder>/", "<destination folder>/"]
```

`--files-from` is the key flag: rather than copying an entire folder, RawCull
writes a **null-terminated list of just the rated/tagged filenames** the
user selected and tells rsync to copy only those.

## Running the copy: `ExecuteCopyFiles`

`ExecuteCopyFiles` (`Model/ParametersRsync/ExecuteCopyFiles.swift`) is a
`@MainActor @Observable` class that orchestrates one copy run:

1. **Resolve the file list** — `viewModel.extractRatedfilenames(minimumRating:)`
   (or the tagged-files equivalent) returns the filenames to copy.
2. **Write the include list** — filenames are null-separated and written to
   a temp file under `/var/tmp/copyfilelist-<UUID>.list0`; the temp file is
   deleted in `cleanup()` once the run finishes.
3. **Resolve security-scoped access** for both source and destination
   folders (they may be different security-scoped bookmarks than the
   currently active catalog), tracked as `sourceAccessedURL`/
   `destAccessedURL` and released in `cleanup()`.
4. **Build arguments and launch** — via the external `RsyncProcessStreaming`
   package's process wrapper, configured through
   `CreateStreamingHandlers.createHandlers(fileHandler:processTermination:)`
   (`Model/Handlers/CreateStreamingHandlers.swift`), which hardcodes
   `rsyncPath: "/usr/bin/rsync"`.
5. **Stream progress** — `fileHandler` is invoked with a running count as
   rsync emits itemized-change lines; `processTermination` receives the full
   output array plus exit status when the process exits.
6. **Report a typed failure** if any step fails, via the
   `CopyStartupFailure` enum (`rsyncArgumentsUnavailable`,
   `noMatchingFiles`, `sourceAccessFailed`, `processLaunchFailed`, ...), so
   the UI can show a specific alert rather than a generic error.

Any startup or teardown failure is surfaced through
`viewModel.operationFailurePresentation`, driving the alert already wired up
in `RawCullMainView`.

`isolated deinit { cleanup() }` guarantees the temp include-file and
security-scoped access are released even if `ExecuteCopyFiles` is
deallocated mid-flight (e.g. the sheet is dismissed early).

## Parsing rsync's output

rsync's own stdout is itemized-change text plus a trailing statistics
block. RawCull turns that into UI-friendly data in three steps:

- **`CreateOutputforView`** wraps each raw output line in an
  `RsyncOutputData` (adds a stable `UUID` `id` for SwiftUI `List`/`Table`).
- **`RemoteDataNumbers`** (despite the "remote" in its name — just parses
  local rsync output) drives `PrepareOutputFromRsync` (trims to the last
  ~20 lines, i.e. the summary block) and the external `ParseRsyncOutput`
  package's `getstats()` to extract numeric fields: files transferred, total
  bytes, elapsed time — populating `filestransferredInt`,
  `totaltransferredfilessizeInt`, and a formatted `stats` string for display.
- **`ItemizedOutput`** parses individual itemized-change lines (e.g.
  `>f+++++++ DSC0001.ARW`) into a change-kind + filename pair so
  `ItemizedOutputRow` can color-code new/updated/deleted entries in the
  detailed output table (`Views/OutputViews`).

## User-facing flow

1. User opens the copy sheet (`Views/CopyFiles/CopyFilesView.swift`), picks a
   minimum star rating (or "tagged files only") and a destination, and
   optionally toggles dry-run.
2. `CopyFilesView` constructs and drives `ExecuteCopyFiles`.
3. On completion, a summary ("3 files · 45.2 MB") is shown with a button to
   open the detailed itemized output table
   (`Views/OutputViews/DetailsView.swift`), backed by `RemoteDataNumbers`.
4. `Views/SavedFiles` provides a separate, persistent browser over
   previously-saved culling records (`CullingModel.savedFiles`) independent
   of any specific copy run.

## Where to look when extending this

- **Changing which rsync flags are used** → `ArgumentsSynchronize.swift`
  and `Params.swift`; don't hand-build argument arrays elsewhere.
- **Exposing the currently-unused optional parameters (8–14)** → add UI
  bindings in `Views/CopyFiles`/`Views/Settings` and thread through
  `Params.swift`; the plumbing to `RsyncArguments` already exists.
- **New failure conditions** → extend `CopyStartupFailure`, not a bare
  `Error`, so the UI keeps getting a specific, localized message.
- If you're tracing a bug and a type name mentions "remote", "offsite", or
  "SSH", first double-check whether it's a real code path or one of the
  unused legacy fields listed above.
