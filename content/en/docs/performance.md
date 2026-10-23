---
title: Performance Measurement
linkTitle: Performance
description: What the October 23 real-catalog measurements establish, how preload saves are bounded, and how to design a comparable follow-up.
weight: 85
lastmod: 2026-10-23
---

# Performance Measurement

Treat performance claims as workload-specific evidence. A bounded task group
establishes an ownership/admission invariant; it does not by itself establish
faster browsing, lower total CPU work or a leak-free application.

## Recorded implementation and catalog

The October 23 remeasurement used the approved preload-save implementation
from `54058fce`, built as optimized Release with coverage disabled. The arm64
build UUID was `60782AD2-A618-385A-A5BA-3BD3A30B07A9`. These measurements predate
the current build-426 documentation baseline; do not describe them as a new
recording of every later source change.

The catalog contained 1,198 ARW files totaling 68,527,349,760 bytes, matching the
preceding day's catalog. Existing disk caches were preserved. This was not a
cold-cache benchmark. The full
[measurement report](https://github.com/rsyncOSX/RawCull/blob/677c4960d4d36d6fae1c8cbae32dd5f1b39a3c7d/Docs/Performance/2026-10-23/report.md)
and durable process samples, timing markers and analysis live in the app repository.
Raw Instruments traces were temporary files; do not assume they still exist.

## Preload owns its pending saves

[ScanAndCreateThumbnails.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCull/Actors/ScanAndCreateThumbnails.swift)
returns encoded JPEG data and its cache key from processing. Each worker:

1. Processes the image and prepares any cache-save payload.
2. Releases that file's `ThumbnailPreloadGate` waiters.
3. Checks cancellation and awaits the disk save when a payload exists.
4. Returns its task-group slot only after saving completes.

The existing limit, `min(4, max(1, activeProcessorCount / 2))`, now covers pending
preload saves and encoded payloads within each group. It is not a global limit
across independent operations. `DiskCacheManager.save` already awaits its
background atomic writer. Interactive `RequestThumbnail` saves are unchanged.
The catalog grant remains retained through the group's completion, and an
atomic write already underway is awaited rather than interrupted.

[ThumbnailPreloadSaveOwnershipTests.swift](https://github.com/rsyncOSX/RawCull/blob/2ca891be5c013dc38fe3c931a829a04083b69c2a/RawCullTests/ThumbnailPreloadSaveOwnershipTests.swift)
stalls saves to check the bound, gate ordering, completion ownership,
cancellation, unchanged preview-RAM admission and disk-backed warm reload.
A cache-preserved real catalog does not necessarily stress this write path.

## Process resource observations

Physical footprint and process disk-I/O counters were sampled approximately
once per second with `proc_pid_rusage`. MiB means bytes divided by 1,048,576.
Process I/O accounting is not physical-storage throughput.

| Observation | Browsing, source switching and reloads | Separate fresh-process load |
| --- | ---: | ---: |
| Sampling duration | 285.04 s | 81.28 s |
| Initial footprint | 531.2 MiB | 666.9 MiB |
| Peak footprint | 4,836.9 MiB | 990.2 MiB |
| Final footprint | 692.9 MiB | 989.9 MiB |
| Read delta | 14,782.4 MiB | 5,131.2 MiB |
| Write delta | 261.3 MiB | 0.0 MiB |

The longer session included adjacent-image navigation, grid scrolling, full-size
JPEG selection, 140% zoom, developed RAW selection, multiple loads, early-load
abort and recovery. Its largest footprint occurred during the full-size
source-exercise interval; that timing does not identify allocation ownership or
a leak. It later declined substantially. The separate fresh-load sample ended
near its peak and does not establish long-term stability.

Yesterday's manual workload differed in duration, actions and unrecorded cache
state. Comparing its 1,428.4 MiB peak directly with today's peaks would not be
a controlled regression or improvement measurement. Thumbnail-cache budgets
also do not cap full-size display images or framework scratch allocations.

## Timing and cancellation scope

For an explicit same-process warm reload, the app was still scanning at the
5.586-second observation; all 1,198 files and a preview were observed by 8.358
seconds after Open began. Those are automation observation bounds, including
overhead, not exact internal completion times.

Open followed immediately by Command-K returned to an empty/no-progress state
within a 1.074-second combined action sequence. A subsequent load recovered the
catalog and preview. This exercised early-load cancellation, not cancellation
specifically during thumbnail writing. Comparison multi-selection and AI review
were not verified in this measurement.

Several same-folder reopen attempts produced a zero-file state and recovered
on repeated selection. Restored picker locations also sometimes had Open
disabled until selecting the catalog from its parent directory. These remain
separate correctness observations: neither a shared cause nor a regression
from bounded saves was established.

## CPU and responsiveness limits

The primary SwiftUI trace did not finalize and could not export. Two shorter
Time Profiler traces saved recoverable CPU/hang tables, but both reported a
corrupt or incomplete logging stream. Their conclusions remain qualified.
No usable SwiftUI cause graph or animation-hitch measurement was obtained.

The 60.33-second fresh-process trace exported 12,341 symbolicated samples:

| Call path | Inclusive sampled weight |
| --- | ---: |
| Preload paths | 3,072 ms, approximately 24.9% of sampled weight |
| Preload grid downscaling | 2,803 ms, approximately 22.7%; overlaps preload |
| JPEG encoding | No matching sampled frames |
| Recorded hangs | 0 |

Do not add overlapping call-path weights or read sampled CPU weight as elapsed
load time. No sampled JPEG encoding plus zero process disk writes means this
fresh load did not meaningfully stress a preload write backlog. It does not
prove every source was a cache hit or quantify a backpressure improvement.
Zero recorded hangs in these windows is not a general absence-of-stalls claim.

The same-process fallback also recorded no hangs, but did not sample preload.
`handleSourceChange` skips preload for a URL already in `processedURLs` during
that app session. Repeated folder selection therefore does not reproduce a
fresh-process preload workload.

## Design the next comparable measurement

Use the same implementation fingerprints, source mode, preview size, catalog,
action sequence and cache preparation for both sides. Separate a cached load
from a controlled cache-miss/write workload. Record phase boundaries so source
switches and full-size development do not become catalog-load peaks. Observe
cancellation while the intended phase is active and verify recovery afterward.

Grid downscaling is a candidate for further cached-preload investigation; the
current trace does not establish that it causes foreground latency. Reproduce
the intermittent reopening issue independently before assigning its cause.
Keep photographic quality, task ownership and runtime performance as separate
validation questions.
