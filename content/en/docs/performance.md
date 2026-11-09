---
title: Performance Measurement
linkTitle: Performance
description: RAW ZoomView preview measurements, historical catalog findings, benchmark semantics, and validation limits.
weight: 85
lastmod: 2026-11-08

reviewed_commit: "a68253b73cbad14a7b1030dba6b439e6bce7d3da"
reviewed_version: "3.4.5"
reviewed_build: 436
reviewed_on: "2026-11-09"
review_scope: "source delta and reference check; content updated"
---

# Performance Measurement

Treat performance claims as workload-specific evidence. A bounded task group
establishes an ownership/admission invariant; it does not by itself establish
faster browsing, lower total CPU work or a leak-free application.

## RAW ZoomView measurements — 31 October 2026

The selected build-428 policy uses direct bounded fit previews on a completed-pixel
and persistent-JPEG cache miss. Native zoom retains the established JPEG pipeline;
inspection remains native. See [source selection]({{< relref "raw-inspection.md" >}}).

The [app measurement record](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/RAW9PreviewPerformance.md)
and [raw results](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/RAW9PreviewPerformanceResults.json)
cover six filename-sorted Sony ARWs, all RAW 9 at 9984 × 6656 pixels, three passes
per mode (18 samples). Fit uses 3072 pixels; modes run in separate processes.

| Pipeline | Median image delivery | Median materialized bitmap | Process peak RSS |
| --- | ---: | ---: | ---: |
| Legacy JPEG, disk-cache miss | 4382 ms | 4644 ms | 919 MiB |
| Selected native policy, disk-cache miss | 4372 ms | 4632 ms | 919 MiB |
| Direct fit, 3072 pixels | 1418 ms | 1425 ms | 391 MiB |
| Completed fit-pixel cache hit | 0.040 ms | 7.8 ms | 499 MiB |

Uncached fit delivery was approximately 3.1× faster with 57% lower process peak
RSS in this standalone workload. These compare different display resolutions;
normal native performance stayed effectively unchanged. Cache-hit delivery is
lookup/readiness, not a painted frame. RSS includes frameworks and benchmark
bitmap materialization, not just the renderer's 256 MiB cache. OS/storage caches
were not flushed. GUI first paint, hitches, other cameras and real portrait RAWs
were not measured.

Native geometry and successive fit/native size transitions passed on all six
photos. Maximum fit mean absolute RGB error against the native JPEG was 0.779/255
(bound 3/255); native exposure checks at −1, 0 and +1 EV matched sampled reference
pixels at 0/255. This bounded cohort does not establish universal decoder quality.
Direct-native rendering was rejected (4807 ms delivery median, 1394 MiB peak RSS).

The recorded focused run passed 32 tests, including 10 new RAW preview tests.
The recorded full run executed 696 tests with three pre-existing failures:
README/project version mismatch (3.3.5 versus 3.3.6), README/parser pin mismatch
(1.3.2 versus 1.3.3), and a launch-context expectation of thumbnail while the
unchanged default is embedded JPEG. These are source-recorded results; this
documentation pass did not rerun them. Temporary full logs/images were under
`/tmp/rawcull-raw9-20261031`; the committed JSON retains samples and source hashes.

## Deferred catalog source-load tails

The [October 25 follow-up](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/DecodeLatencyFollowUp-2026-10-25.md)
records a separate matched 809-file comparison: empty-cache median 8.617 → 8.188 s,
warm median 3.973 → 3.634 s, but maximum source-load latency 343.486 → 2011.928 ms.
Its 200-pixel grid output differs from the earlier 200-point path, so memory and
resize improvements require that workload qualification. The wrapper includes
access, scheduling, parser waits, I/O and journal delivery; it does not isolate
decoder CPU time. Rare-tail causes and user impact remain unproven.

That comparison predates the RawParserKit 1.3.3 executor update. Separate package
thumbnail experiments do not replace a new RawCull catalog measurement. Preserve
the source/load-stage diagnostics and collect matched runs before attributing
an app speedup or tail fix to the new pin.

## Historical catalog findings — 25 October 2026

RawCull **3.3.5, build 426** closed the October 24–25 investigation with
qualified acceptance. The retained Phase 2 changes coalesce metadata and
thumbnail progress independently at a 100 ms cadence, publish initial and terminal
states immediately, and cancel pending publication when a catalog is replaced.
The progress ring uses a 100 ms linear transition and respects Reduce Motion;
numeric progress changes immediately. Accounting, image readiness, bounded
workers and awaited saves retain their contracts.

The current reference passed three benchmark repetitions on **809 ARWs**
(50,126,917,632 bytes), **1616 px** previews and **100 browsing steps**, optimized
Release with testability. This workload differs from the historical 1,198-file
session below. The benchmark source was `53c80dbb`; the final documentation
revision is linked in the reports below. The CPU recording's app UUID was verified,
but its source hash was not independently established.

| Pooled median | Historical 809-file baseline | Current reference |
| --- | ---: | ---: |
| Empty-thumbnail-cache preload | 8.206 s | 8.415 s |
| Warm-thumbnail-cache preload | 3.553 s | 3.647 s |
| JPEG encoding | 5.005 ms | 4.989 ms |
| Grid preload resize | 4.308 ms | 4.335 ms |
| Prepared disk image readiness | 0.330 ms | 0.314 ms |
| Zoom preview readiness | 3.316 ms | 3.376 ms |

These numbers are **historical context, not an accepted automated before/after
comparison**: harness fingerprints differ and the runner rejects comparison.
Three repetitions and unmatched cache/power/background conditions do not establish
significance or a general loading speedup. Source-load wrapper medians rose
13.563 → 23.296 ms and the worst rose 2.781 → 6.187 s; metadata and resource
changes also remain unresolved regression signals, without established causality.

A separate phase-aligned app capture observed preload main-thread sampled weight
falling **4.575 → 1.325 s (71%)**, while elapsed preload was **20.577 → 20.254 s**.
This supports less sampled main-thread progress work, with differing capture
configuration/provenance and no matched repetition. It does not establish a 71%
loading speedup, exact CPU savings, or smoother painted frames. Component benchmark
and app preload times measure different workloads.

Phases 3–6 deferred further encoder, grid, parser, picker and view optimizations.
They retained diagnostics and findings. A reduced warm-cache recording contained
74 hitches, worst 416.694 ms; actions and capture settings differ from earlier
recordings, so counts must not be compared as a regression rate. Full SwiftUI
acceptance, first-painted-frame smoothness, matched cancellation/catalog-switch
coverage and long-duration stability remain incomplete. Phase 7 did not rerun
Swift report tests; its Python runner/exporter suite passed 18 tests. Performance
close-out permits the normal release process, not complete release certification.

See [the final findings](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/PerformancePhase7.md),
[Phase 2 measurements](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/PerformancePhase2.md), and
[the phase plan and outcomes](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/performancefixes.md) for provenance, validation and deferred work.
The durable final trace/app/dSYM/export archive is
`/Volumes/MacMini4/TestRunPerformance/phase7-evidence-2026-10-25`;
the benchmark reference is stored separately under
`/Volumes/MacMini4/TestRunPerformance/phase7-reference-20261025-062837`.

## Run the catalog benchmark

Run from the RawCull app repository with Xcode and pinned dependencies available:

```sh
python3 -B Scripts/RunCatalogPerformance.py "/Volumes/Photos/My ARW Catalog" \
  --output /tmp/rawcull-reference --runs 3 --steps 100 --pixels 1616
```

Use a new output directory outside the repository and catalog. The source folder
is read only and nonrecursive; the benchmark requires valid ARWs. The CLI defaults
to 1600 pixels while the app source default is 1616, so pass the actual app setting.
Every repetition starts with a separate empty thumbnail disk cache, then measures
warm preload and prepared browsing with documented RAM resets. OS/parser caches
are not flushed. Results measure image readiness, not first painted pixels or AI
throughput. The benchmark build disables App Sandbox only for its command-line
catalog access; normal application settings are unchanged.

Retain `run-configuration.json`, `results.json`, `report.md`, per-run events/results,
`xcodebuild.log` and `tests.xcresult`. Add `--baseline /path/to/previous-output` only
for compatible catalog, machine/OS, Xcode, settings, version and harness identities.
Do not bypass fingerprint checks. An optional `--max-regression-percent 20` gate
requires both a median increase over 20% and over 5 ms; tails still need review.

[Benchmark semantics](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/CatalogPerformance.md) and
[the Instruments workflow](https://github.com/rsyncOSX/RawCull/blob/dc048db4ded7b324bbf8cfe4e3f0275302f4f298/Docs/MeasurePerformance.md) explain the complete procedure.
App phase instrumentation uses subsystem `no.blogspot.RawCull`, category
`CatalogPerformance`, intervals `CatalogOpen`, `CatalogMetadataScan`,
`CatalogThumbnailPreload` and event `CatalogThumbnailPreloadComplete`.
`Scripts/ExportCatalogTrace.py` exports available tables and records missing/empty
data; `Scripts/ValidateCatalogSignposts.py` validates pairing and completion.
A successful export alone does not establish usable phase or UI evidence.
Preserve complete traces and matching binaries/dSYMs before cleaning temporary data.

## Historical October 23 evidence

The remaining sections preserve the earlier 1,198-file workload. They describe
that session and its limitations; use the October 25 findings above for current
performance status.

## Recorded implementation and catalog

The October 23 remeasurement used the approved preload-save implementation
from `54058fce`, built as optimized Release with coverage disabled. The arm64
build UUID was `60782AD2-A618-385A-A5BA-3BD3A30B07A9`. These measurements predate
the historical build-426 documentation baseline; do not describe them as a new
recording of every later source change.

The catalog contained 1,198 ARW files totaling 68,527,349,760 bytes, matching the
preceding day's catalog. Existing disk caches were preserved. This was not a
cold-cache benchmark. The full
[measurement report](https://github.com/rsyncOSX/RawCull/blob/677c4960d4d36d6fae1c8cbae32dd5f1b39a3c7d/Docs/Performance/2026-10-23/report.md)
and durable process samples, timing markers and analysis live in the app repository.
Raw Instruments traces were temporary files; do not assume they still exist.

## Preload owns its pending saves

[ScanAndCreateThumbnails.swift](https://github.com/rsyncOSX/RawCull/blob/a5f35b05c1e206ed4d6aa599522f5c8622b5308a/RawCull/Actors/ScanAndCreateThumbnails.swift)
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

[ThumbnailPreloadSaveOwnershipTests.swift](https://github.com/rsyncOSX/RawCull/blob/a5f35b05c1e206ed4d6aa599522f5c8622b5308a/RawCullTests/ThumbnailPreloadSaveOwnershipTests.swift)
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

## Comparable-measurement requirements

Use the same implementation fingerprints, source mode, preview size, catalog,
action sequence and cache preparation for both sides. Separate a cached load
from a controlled cache-miss/write workload. Record phase boundaries so source
switches and full-size development do not become catalog-load peaks. Observe
cancellation while the intended phase is active and verify recovery afterward.

The October 24 grid investigation deferred optimization; the historical
October 23 trace does not establish that downscaling causes foreground latency. Reproduce
the intermittent reopening issue independently before assigning its cause.
Keep photographic quality, task ownership and runtime performance as separate
validation questions.

## Current preview instrumentation and scripts — November 4 review

Build 429 adds a ZoomView duration badge around the awaited RAW preview loader.
It includes memory/disk-cache retrieval and excludes the later analysis wait;
it does not measure decoder-only CPU work or first paint. This instrumentation
is separate from the October 31 standalone measurements above. No new benchmark
or application test run was performed for this documentation update.

The November 1 README corrects the version/parser-pin statements implicated in
two of that recorded run's failures. This source correction does not establish a
new passing run or resolve the separately recorded launch-context expectation.

Run the standalone preview benchmark with a clean checkout of the pinned parser:

```sh
python3 Scripts/RunRAW9PreviewBenchmark.py "/path/to/ARWs" \
  --parser-source "/path/to/pinned/RawParserKit" \
  --output /tmp/rawcull-raw-preview-new
```

The runner checks the parser HEAD against the app lockfile and rejects dirty
parser `Sources`. Defaults select six files, three passes and separate processes
for baseline, native, fit, revisit and validation modes; validation uses one pass.
It writes per-mode JSONL/stderr, compiled artifacts and `summary.json`, including
renderer/benchmark source hashes. Use a fresh output directory: unlike the catalog
runner, this tool allows an existing directory and opens per-mode logs for writing.

The expanded
[scripts guide](https://github.com/rsyncOSX/RawCull/blob/a5f35b05c1e206ed4d6aa599522f5c8622b5308a/Scripts/README.md)
also covers trace export, grid/source-load analysis, model evidence runners and
`make test-scripts`. Script tests use temporary fixtures and mocked Xcode calls;
real photographs and installed models are not required. They do not run Swift
diagnostics, real-catalog/model probes or release uploads. Source-load durations
include scheduling, waits and I/O; summed overlapping durations are not CPU time.

## November 8 source review: Close-ups is a separate workload

The November 8 checkout was 3.4.0 build 434. The earlier tables remain measurements of
their recorded versions and actions. Adding Close-ups does not supply new latency,
first-paint, photographic-quality or memory-pressure measurements.

The panel's host renderer serializes its own full-size loads and returns bounded
crop/overview artifacts. The main stage and other loaders remain separate
consumers. A future comparison should record frame count, selected source,
sidecar/cache state, pinned-reference membership, crop/viewport settings, peak
process memory and cancellation behavior. Do not transfer the ZoomView fit-preview
results directly to this full-size crop pipeline.

At that review the README identified 3.3.6 and lists the older dependency snapshot, while
`project.pbxproj` identified 3.4.0 build 434 and the lockfile had 19 pins. Use project
settings and the lockfile as the current source baseline; this documentation
review does not modify the app README or establish release availability.


Build 436 adds current-frame detection on an embedded preview capped at
1,600 pixels. Human cache hits skip the Vision face request, but still need
the preview pixels for crops. Animal detection runs separately. This source
review adds no latency, memory or detection-accuracy measurements.
