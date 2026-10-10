+++
author = "Thomas Evensen"
title = "Synchronizing Cache Storage and Accounting"
date = "2026-10-10"
lastmod = "2026-10-10"
weight = 21
tags = ["cache", "concurrency", "evictions", "swift"]
categories = ["technical details"]
+++

# Synchronizing Cache Storage and Accounting

RawCull keeps preview and grid thumbnails in memory so that scrolling and
selection do not repeatedly decode the same RAW files. Settings also reports
how many thumbnails are cached and their estimated byte cost. Those numbers
must follow insertions, replacements, clears, and automatic eviction.

This document explains Thomas Evensen's change,
[“Synchronize cache storage and accounting with owned eviction delegates”](https://github.com/rsyncOSX/RawCull/commit/a96442f0c7305bf9aa194e513d98b6e028663504).
The commit changes five files: 194 insertions and 101 deletions. The implementation
is a worked example of keeping a thread-safe container and its external
bookkeeping consistent. See the [Memory Cache overview]({{< relref "cache.md" >}})
for the surrounding thumbnail pipeline.

## The Problem: Safe Operations Can Still Form an Unsafe Sequence

`NSCache` supports concurrent access, but does not expose its current item count
or total stored cost. RawCull therefore maintains its own accounting.

Previously, `SharedMemoryCache` held bare `NSCache` instances and separate
lock-protected count and cost counters. Replacing a thumbnail involved looking
up the previous object, subtracting its cost and count, inserting the new object,
and adding the new cost and count. Each individual counter access was protected;
the whole sequence was not.

Two writers replacing the same key could both observe the same previous value
and both adjust the counters. A clear could also interleave with insertion so
that storage and counters ended up describing different states. Clamping a
counter to zero did not restore the missing relationship between these operations.

There was a second ownership problem. The old shared `CacheDelegate` identified
caches by comparing them against `SharedMemoryCache.shared`. A separately
constructed cache owner, such as a test fixture, could not use that delegate to
update its own accounting. Test fixtures consequently disabled eviction tracking.

## One Wrapper Owns Storage, Metadata, and Callbacks

The new
[`TrackedThumbnailCache.swift`](https://github.com/rsyncOSX/RawCull/blob/a96442f0c7305bf9aa194e513d98b6e028663504/RawCull/Model/Cache/TrackedThumbnailCache.swift)
combines these responsibilities:

```swift
private let lock = NSRecursiveLock()
private let storage = NSCache<NSString, Entry>()
private var entries: [String: (id: UUID, cost: Int)] = [:]
private var storedCost = 0
```

Every storage lookup, insertion, clear, limit access, accounting read, and
accounting change uses the same lock. The wrapper sets `storage.delegate = self`,
so an eviction updates the wrapper that owns the evicted entry. No singleton
lookup or cache-identity comparison is needed.

`Entry` contains a unique UUID, the string key, the thumbnail, and its insertion
cost. The metadata dictionary stores only the UUID and cost, without retaining
the thumbnail. If metadata retained thumbnails, eviction could remove them from
`NSCache` while the bookkeeping still kept their image memory alive.

The accounting rule is simple: `currentCount` is `entries.count`, and
`currentCost` is the sum of the registered costs. The stored cost is normalized
with `max(0, cost)`. It is the caller-supplied cache cost, not a measurement of
the process's actual resident memory.

## Replacement and Immediate Eviction

Insertion runs as one locked operation:

```swift
let entry = Entry(key: key as String, thumbnail: thumbnail, cost: max(0, cost))
if let previous = entries[entry.key] {
    storedCost -= previous.cost
}
entries[entry.key] = (entry.id, entry.cost)
storedCost += entry.cost
storage.setObject(entry, forKey: key, cost: entry.cost)
```

The new metadata is registered **before** calling `NSCache.setObject`. An
insertion can trigger an eviction callback immediately; that callback must be
able to find and remove the new entry's accounting.

Replacement also needs to distinguish two entries that use the same key. The
delegate checks the entry UUID before subtracting anything:

```swift
guard entries[entry.key]?.id == entry.id else { return }
entries.removeValue(forKey: entry.key)
storedCost -= entry.cost
```

For example, suppose key `photo` holds entry A with cost 400, then receives
entry B with cost 1600. Replacement subtracts 400 and registers B's 1600. If a
callback arrives for A, its UUID no longer matches the metadata and the callback
is ignored. A callback for B removes B and subtracts 1600. Matching only the key
would allow A's callback to corrupt B's accounting.

## Why the Lock Is Recursive

`NSCache` can call its delegate during insertion or a limit change, while the
wrapper already holds the lock. The callback enters the same locked helper.
`NSRecursiveLock` allows that reentry on the calling thread; a nonrecursive lock
would deadlock in that case. A callback on another thread is serialized by the
same lock.

All wrapper operations are synchronous. No lock is held across `await`.
`@unchecked Sendable` expresses the wrapper's manually maintained concurrency
contract: its mutable state is private and lock-protected. It does not itself
make mutable data safe. Cached thumbnails must continue to follow RawCull's
invariant that an image is fully constructed before caching and treated as
immutable afterwards.

## Clearing, Limits, and Lifetime

`removeAllObjects()` first clears metadata and sets `storedCost` to zero, then
clears `NSCache`, all under the lock. Any resulting callback finds no matching
metadata and does nothing. A concurrent insertion happens before or after that
operation, so it cannot leave an empty cache with an insertion's counter update.

`totalCostLimit` and `countLimit` also go through the wrapper. Evictions caused
by limit changes use the same accounting callback. These are cache policy limits;
the implementation does not assume a particular eviction order or assert an
exact number of survivors after changing a limit.

The wrapper detaches `storage.delegate` in `deinit`. This prevents cache teardown
from calling back into the wrapper after its metadata or lock has been destroyed.

Each accounting property is read under the lock, but separate calls to
`currentCount`, `currentCost`, and `object(forKey:)` are separate observations.
They are not a combined snapshot while other tasks are mutating the cache.

## Integration with SharedMemoryCache

[`SharedMemoryCache.swift`](https://github.com/rsyncOSX/RawCull/blob/a96442f0c7305bf9aa194e513d98b6e028663504/RawCull/Actors/SharedMemoryCache.swift)
remains an actor for configuration and memory-pressure handling. Its two
synchronous cache endpoints become:

```swift
nonisolated let memoryCache = TrackedThumbnailCache()
nonisolated let gridThumbnailCache = TrackedThumbnailCache()
```

Thumbnail reads and writes still work without an actor hop. The preview and grid
wrappers independently own their storage and accounting. The actor's public
count/cost methods forward to the corresponding wrapper; the four separate
counters and the old `CacheDelegate.swift` are removed.

Critical memory pressure calls `removeAllObjects()` and
`removeAllGridObjects()`, using the same synchronized clear path as other callers.
The test helper no longer needs `tracksEvictions: false`: isolated owners now
track their own evictions exactly like the production owner.

## Tests That Protect the Contract

[`CacheAccountingConcurrencyTests.swift`](https://github.com/rsyncOSX/RawCull/blob/a96442f0c7305bf9aa194e513d98b6e028663504/RawCullTests/CacheAccountingConcurrencyTests.swift)
contains three Swift Testing tests, each parameterized for preview and grid:

| Test | Workload | Checked result |
| --- | --- | --- |
| Concurrent replacements | 16 tasks each replace one key 200 times, alternating thumbnail sizes | One live entry; recorded cost matches the surviving thumbnail |
| Concurrent clear and insert | 12 tasks each perform 200 clears or insertions | Count and cost match final storage; a subsequent clear and insert reset correctly |
| Owned eviction accounting | Insert 50 keys with count limit 2, then set cost limit 1 | Count and cost match the entries actually found in that isolated cache |

The task-group tests wait for all workers to finish before comparing storage
with accounting. The eviction test measures actual survivors instead of relying
on `NSCache`'s eviction order. These are regression tests for the identified
races and ownership issue, rather than proof of every possible interleaving.

The reusable principle is to synchronize the container operation and its
bookkeeping as one operation, give callbacks an owning instance, and use an
entry identity when callbacks can refer to a replaced value.
