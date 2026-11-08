+++
author = "Thomas Evensen"
title = "P0: XMP and Editor Handoff"
linkTitle = "P0: XMP and Editor Handoff"
date = "2026-11-05"
lastmod = "2026-11-05"
description = "Functional scope and implementation plan for safe XMP decision exchange and editor handoff."
tags = ["roadmap", "planning", "culling"]
categories = ["technical details"]
weight = 20

reviewed_commit = "a5f35b05c1e206ed4d6aa599522f5c8622b5308a"
reviewed_version = "3.4.0"
reviewed_build = 434
reviewed_on = "2026-11-08"
review_scope = "source delta and reference verification"
+++

# P0: XMP Import/Export and Editor Handoff

**Status:** proposed plan, not implemented capability. **Priority:** first P0.
**Outcome:** a photographer can take decisions made in RawCull into an editor,
bring changed ratings back, and understand every conflict or failed write.

This plan expands the [feature overview]({{< relref "newfeatures.md" >}}).
It proposes an explicit exchange operation before considering continuous sync.
Exact editor mappings must be qualified against named editor versions before
release; the mapping below is a product contract to validate, not a claim that
all editors already interpret metadata identically.

## 1. Functional scope

The first release imports and exports decision metadata through XMP sidecars
for selected RAW files or a whole opened catalog. The user previews changes,
chooses how conflicts are resolved, runs the operation, and receives per-file
results. Original RAW bytes remain unchanged. Existing RawCull JSON decisions
remain available and are migrated additively rather than replaced by sidecars.

| Included | Deferred |
| --- | --- |
| Read ratings; write explicitly chosen rating changes | Embedded RAW metadata modification |
| Preserve unrelated XMP, including editor adjustment data | RAW development settings exchange |
| Detect changes since import or last successful export | Background bidirectional sync and folder watching |
| Import preview, export preview, conflict resolution and retry | Launching every editor or manipulating editor databases |
| Qualified Lightroom Classic and Capture One workflows | Universal pick flags, labels or editor compatibility |
| Export beside originals; copy RAW plus applicable sidecar together | General ingest, renaming and backup management |

XMP can carry private fields without making them interoperable. Burst winners,
deferred groups, AI evidence and analysis caches remain RawCull data in this
phase. No AI recommendation becomes a rating merely because export was opened.

## 2. A complete user journey

A photographer opens a shoot containing 600 RAW files, some with existing
sidecars. They choose **Import XMP Decisions**. A preview reports unchanged files,
new ratings, conflicts, absent sidecars and unreadable files. Nothing has yet
changed in the catalog or on disk. The photographer applies uncontested changes
and resolves the remaining conflicts individually or with a documented batch
rule. They can continue reviewing files whose import failed.

After review, they choose **Export Decisions**, scoped to 48 selected files.
The preview shows the actual file list, destination sidecars, current disk value,
proposed value and any destructive clearing. A RAW with editing adjustments
keeps those adjustments. A file without a sidecar receives a new one containing
only the necessary metadata and structural declarations.

When export completes, the summary might show 45 written, two unchanged and one
blocked by an external change. The user opens the editor, follows the tested
metadata-read procedure for that editor, and verifies the ratings. Writing a
sidecar does not imply that an already-open editor catalog has refreshed it.
The failed file remains retryable and is never reported as handed off.

Later, the photographer changes a rating in the editor and writes it to disk.
RawCull's next import compares disk, local decision and the last exchanged
baseline. A local change and a different external change produce a conflict;
the application does not choose whichever timestamp happens to be newer.

## 3. Decision mapping and ownership

Before implementation, inspect the actual decision domain, including the
meaning of selection, tags, neutral, rejection and stars. Introduce an explicit
mapping adapter rather than assuming a UI selection is an editor pick flag.

| RawCull intent | Proposed portable rating behavior | Required qualification |
| --- | --- | --- |
| One to five stars | Exchange the corresponding integer rating | Verify read and write in each supported editor |
| Neutral/unrated | Explicitly set zero when clearing is requested | Distinguish an absent field from an intentional clear |
| Rejected | Candidate mapping to rating -1 | Verify rejection rendering and round trip per editor |
| Selected/tagged without stars | No automatic rating change | Optional future profile must show any lossy mapping |
| Burst winner or deferred review | Keep in RawCull JSON only | Must not silently create stars or pick flags |

Use the conventional XMP rating field as the candidate shared representation;
confirm its namespace and legal values from the specification during the
compatibility spike. Unsupported, malformed and out-of-range values are surfaced
as unsupported metadata, never clamped into a valid decision.

A missing sidecar or absent rating means **no external decision supplied**,
not an instruction to erase a local rating. An explicit zero is a supplied
unrated value. Exporting a clear therefore requires an intentional local change
or explicit user choice. Flags and color labels stay untouched unless a later,
versioned editor profile explicitly owns those fields.

## 4. Import, conflicts and visible states

Maintain a common baseline per source image and exchanged field. Compare local
and external values against that baseline:

| Local change | Disk change | Result |
| --- | --- | --- |
| Neither | Neither | No action |
| Only local | No | Offer export |
| No | Only external | Offer import |
| Both, same value | Both | Converged; update baseline after validation |
| Both, different values | Both | Require a conflict choice |

First contact has no common baseline. If both sides contain different explicit
values, preview them as a first-import conflict. Offer **Use RawCull**, **Use
Sidecar**, or **Skip**, with counts and sample filenames before applying a batch
choice. A conflict choice is scoped to that preview, not a permanent global
preference. Keep the original baseline for skipped or failed entries.

Track independent states such as absent, unreadable, unsupported, clean,
local-change, external-change, conflict and successfully-exchanged. Present
readable explanations. A corrupt XML packet is an error with the file path;
it must not be replaced with a minimal packet that destroys existing content.

## 5. Proposed implementation boundaries

Existing integration starts at `RawCull/Model/JSON/WriteSavedFilesJSON.swift`,
`ReadSavedFilesJSON.swift`, the `SavedFiles`/`FileRecord` decision model, and the
copy/export workflow. The current JSON writer already serializes writes through
an actor and keeps a backup; sidecar exchange needs its own per-file lifecycle.
These are inspection entry points, not a commitment to reuse JSON encoding for
XMP.

Proposed responsibilities, with names to finalize at pickup:

- A decision adapter converts existing domain decisions into explicit field
  operations: leave unchanged, set value or clear value.
- A sidecar resolver associates one RAW with an unambiguous sidecar destination.
  Define case handling, same-stem different-extension collisions and RAW/JPEG
  pairs before permitting writes. Ambiguous associations block that entry.
- An XMP document layer reads and patches owned fields while preserving unknown
  namespaces, properties and editor payloads. Namespace prefixes are not IDs.
  Reject external entity resolution and uncontrolled resource loading.
- An exchange coordinator creates immutable previews, applies resolutions,
  serializes writes to each destination and publishes per-file outcomes.
- A persisted exchange ledger stores the common decision baseline, source
  identity, sidecar identity/hash, mapping version and operation outcome.

A preview record needs source identity, source fingerprint, destination URL,
observed sidecar fingerprint, original and proposed values, mapping version and
reason. A job adds scope, operation ID, cancellation state and entry outcomes.
Use content hashes for sidecar change detection; size and timestamp alone can
miss changes. Revalidate source association if the RAW moved or was replaced.
Do not persist a broad security-scoped permission assumption as file identity.

## 6. Safe writes, recovery and copying

Read current bytes immediately before patching. If they differ from the preview,
invalidate that entry and rebuild its preview. Stage the patched packet in the
same directory, parse it again, validate changed fields and unrelated payload
preservation, then atomically replace the destination. Retain recoverable prior
bytes and record the completed outcome before advancing its common baseline.

An atomic replacement prevents partial bytes but is not a cross-application
transaction. Recheck immediately before replacement, coordinate cooperating
file access where supported, verify the resulting bytes and document the
remaining race with non-cooperating writers. Concurrent editor writes are a
release qualification case, not something timestamps can solve perfectly.

If the app stops after replacement but before recording success, recover using
the operation journal and before/after hashes. Do not blindly replay a stale
packet. Undo restores prior bytes only if the current destination still matches
the bytes this operation wrote; otherwise offer a conflict rather than
overwriting newer editor work. For newly created files, deletion on undo has
the same ownership check.

Cancellation stops scheduling new files and lets the active replacement finish
safely. The summary distinguishes completed, skipped, failed and not attempted.
Read-only media, disconnected volumes, insufficient space and revoked access
produce actionable per-file errors and preserve local decisions.

For copying selected RAWs, prepare the destination RAW and its corresponding
merged sidecar as one tracked handoff entry. A partial pair is incomplete, with
an explicit retry path; do not claim batch-wide atomicity. Check destination
collisions before copying. The destination sidecar must reflect the exported
local decision while retaining source adjustment metadata. Subsequent export
must not accidentally write to a different original/destination association.

## 7. Delivery stages and acceptance

1. **Compatibility spike.** Document decision semantics, rating namespace,
   sidecar naming and editor refresh/write procedures. Produce fixtures from
   named Lightroom Classic and Capture One versions. Resolve rejection behavior
   before offering it in a profile.
2. **Read-only preview.** Implement parsing, association, baseline comparison
   and conflict presentation without disk mutation. Demonstrate missing, malformed
   and first-contact cases using real sidecars.
3. **Controlled export.** Implement preservation, stale-preview protection,
   journaling, cancellation and recovery. Enable one qualified mapping first.
4. **Integrated handoff.** Connect selected-file and catalog scopes, persist
   imported decisions, and copy paired RAW/sidecar outputs.
5. **Release qualification.** Run the editor matrix and publish known limitations,
   including manual refresh procedures and supported versions.

Acceptance requires exact round trips for supported values, no changes to RAW
bytes, semantic preservation of unrelated XMP and editor settings, and no silent
overwrite of detected external edits. Tests must cover namespaces with alternate
prefixes, multiple descriptions, missing fields, explicit zero, malformed XML,
unknown properties, naming collisions and non-ASCII paths. Validate unrelated
metadata using independent inspection and the target editor, not only the
writer's own parser.

Exercise interrupted jobs, crash recovery between replacement and ledger write,
partial copies, retries and cancellation. Confirm that failed entries retain
their previous common baseline and never appear as successful. Measure preview
and export time for 500, 2,000 and 10,000 files on recorded storage/hardware;
set responsiveness targets from the spike rather than inventing results.

## 8. Decisions for the next revision

Record owner, decision date, rationale and evidence for: supported editor
versions; reject fallback if -1 does not round-trip; library/parser choice;
sidecar association policy; backup retention; recovery UI; ledger location and
migration; destination-copy ownership; sandbox access handling; and performance
budgets. These decisions gate implementation milestones, not basic exploration.

The [second P0]({{< relref "unified-burst-evidence.md" >}}) produces evidence and
manual choices. Only explicit photographer decisions enter this exchange path.


## 9. Modular implementation blueprint

### 9.1 Evaluation and ownership

**Recommendation:** implement XMP exchange as a UI-independent engine with a
self-contained preview/job UI. Editor handoff is a separate orchestrator that
consumes exchange outcomes. Combining all three into a view model would couple
XML preservation, decision storage, copy execution and editor behavior, making
future editor profiles or storage changes expensive.

Source inspection on 2026-11-05 confirms `SavedFiles`/`FileRecord` contain optional
ratings and generated UUIDs; decode reconstructs records. Do not assume those
UUIDs are durable exchange identities. `ExecuteCopyFiles` currently obtains its
file list through a weak RawCullViewModel reference and reports process-level
outcomes. Its rsync success cannot by itself prove each RAW/sidecar pair is
complete. Add a boundary adapter and per-entry verification before reusing it
for qualified handoff. Do not expand that class into the XMP engine.

### 9.2 Boundaries and dependency direction

| Boundary | Owns | Dependencies allowed |
| --- | --- | --- |
| `DecisionExchangeContracts` | Field values/operations, identities, previews, resolutions, results and versioned profiles | Foundation/value contracts only |
| `XMPDocument` | Safe parsing and preservation-aware patching of owned fields | Contracts and qualified XML implementation |
| `DecisionExchangeEngine` | Baseline comparison, planning, per-destination scheduling, journal/recovery and outcomes | Contracts, document layer and narrow I/O/storage interfaces |
| `DecisionExchangeUI` | Scope, preview, conflict choices, job progress, retry and summaries | Contracts and engine interface |
| `EditorHandoff` | Paired-copy manifest, verification, qualified editor instructions and optional launch | Exchange results, copy/file-access and editor adapters |
| RawCull adapters | Decision projection/commit, JSON persistence, catalog identity, permissions and existing copy integration | Application models and public feature interfaces |

Application composition injects concrete adapters. Neither engine nor document
layer imports SwiftUI, RawCullViewModel, rsync process wrappers or editor UI.
Begin in cohesive feature targets/folders; use Swift packages once their APIs
are stable. Keep concrete editor profiles out of the XML parser and keep the
ledger separate from existing saved decision JSON ownership.

### 9.3 Explicit operation contracts

| Contract | Minimum contents and behavior |
| --- | --- |
| `ExchangeScope` | Frozen explicit source list, catalog identity/revision and operation direction; selection changes after preview do not change this list |
| `SourceReference` | Durable catalog/source key, current URL, source fingerprint and association revision; permissions acquired separately |
| `DecisionSnapshot` | Source key, authoritative decision revision, rating presence/value and explicit user intent; no automatic inference from winner or AI score |
| `FieldOperation` | Leave unchanged, set supported value, or explicit clear; profile defines clear encoding and distinguishes absent from zero |
| `EditorProfile` | ID/version, supported values/fields, naming policy and qualified editor/version instructions; unsupported operations fail visibly |
| `ExchangePreview` | Immutable preview ID/revision, scope, profile version, local/ledger revisions, sidecar hash or absence token, association and proposed field changes per entry |
| `Resolution` | Preview/entry ID, expected revision and use-local/use-sidecar/skip choice; cannot apply to a regenerated preview implicitly |
| `ExchangeResult` | Operation/entry IDs, verified before/after hashes, committed decision revision, outcome/reason and recovery reference |
| `HandoffManifest` | Source and destination associations, required RAW/sidecar artifacts, expected fingerprints, per-artifact verification and pair completion |

A clear is an operation, not an ambiguous nil. Parser output separately models
missing packet, absent field, supported value, unsupported value and invalid
packet. A snapshot is an explicit decision projection, not a FileRecord or
SavedFiles object passed into a generic engine. Hashes describe observed bytes;
they are not permissions or a substitute for durable source association.

### 9.4 Injected services and lifecycle

- `DecisionRepository`: read snapshots and apply imported decisions with expected
  revisions and operation IDs. Commit through existing application persistence,
  with idempotent retry; an import is successful only after durable commit.
- `SidecarAssociating`: resolve or reject source/destination ownership and naming
  collisions without parsing or changing photographer decisions.
- `SidecarStore`: acquire scoped access, read bytes/fingerprint, stage and verify,
  and perform guarded replacement/restore. Expose external-change outcomes and
  the limits of coordination; never promise filesystem compare-and-swap across
  arbitrary editor processes.
- `ExchangeLedger`: persist baseline, pending intent and completion records,
  recover incomplete entries and migrate schema. Store recovery bytes securely
  enough for the existing access model and define retention before release.
- `CopyExecuting`: consume an explicit manifest, report artifact-level outcomes
  and support verification/retry. Existing rsync execution can implement an
  adapter but must not choose scope from live UI state during the job.
- `EditorHandoffProviding`: return qualified instructions/capabilities and,
  optionally, launch the explicitly chosen installed application. Launch success
  is separate from metadata ingestion, which RawCull cannot assume happened.

The engine serializes work by resolved destination, including overlapping jobs;
a single job actor is insufficient if two jobs can target the same sidecar.
Parsing/hashing/copying run away from the presentation actor. UI subscribes to
operation-ID-scoped progress; closing the view follows an explicit job-lifetime
policy rather than silently abandoning a write. Cancellation finishes the active
safe replacement and marks remaining entries not attempted.

Revalidate both disk fingerprints and local decision revisions at apply time.
A rating changed during preview must not be overwritten by a stale import, and
an export must not silently change to the newest local value without a revised
preview. After sidecar replacement, baseline advancement records the exact
exported value/revision; a newer local change remains pending export.

Journal imports as well as exports. A crash between durable local import and
ledger commit is reconciled by operation ID and expected before/after decision
revisions; do not replay against a newer local edit. No cross-store atomicity is
assumed between saved decision JSON, the ledger and external sidecar bytes.
Uncertain recovery remains a visible unresolved entry. Skips and failures never
advance a baseline.

### 9.5 Delivery sequence with module gates

1. **Domain/profile spike.** Trace getRating, tagging, neutral/clear semantics and
   persistence; define source identity and the first qualified profile. Capture
   real editor fixtures and refresh procedures. Gate: explicit mapping examples
   and unsupported cases approved as product behavior, not parser assumptions.
2. **Pure contracts and planning.** Implement field semantics, three-way merge,
   association policy and immutable preview using fake repositories/stores.
   Gate: no app or UI dependency; absent versus zero, first contact and stale
   local decisions all have deterministic outcomes.
3. **Read-only integration.** Add RawCull decision/access adapters and a reusable
   preview model/view for selected and catalog scopes. Gate: fixture host and
   real catalog produce previews with no disk or decision mutations.
4. **Durable import.** Add revision-checked decision commands and recovery across
   local persistence/ledger boundaries. Gate: failed persistence and interrupted
   imports cannot appear successful or erase subsequent local decisions.
5. **Controlled export.** Qualify preservation-aware patching, guarded writes,
   shared destination scheduling, backup and journal recovery. Gate: independent
   inspection and editor round trips pass; unrelated adjustments survive.
6. **Handoff integration.** Implement manifest-driven paired copy, per-artifact
   verification and retry of incomplete pairs; then add instructions/optional
   launch through editor profiles. Gate: an exchange-only host works without
   rsync or an installed editor, and partial pairs never count as handed off.
7. **Package and release qualification.** Enforce target dependency rules, add
   profile/ledger migrations and run section 7's failure/performance matrix.
   Gate: replacing the parser, copy backend or UI does not change merge policy
   or the application decision model. Publish the qualified editor versions.

Do not expand v1 into continuous sync or editor catalog automation. Future label
fields require explicit ownership and baseline policy; new editor profiles add
capabilities through the same contracts rather than branches in RawCull views.

## 10. Shared modularity policy for both P0 features

Unified evidence and XMP exchange meet only through authoritative photographer
decisions in the application domain. They must not import each other's UI,
workers, caches or ledger. An evidence result cannot directly trigger sidecar
writing. A manual rating flows through the existing decision command boundary;
exchange later reads the committed projection on explicit request.

For both implementations, maintain a short module README containing ownership,
public inputs/outputs, lifecycle, error states, schema/policy versions and a
minimal fixture-host example. Add a dependency check or target-level build gate
against app-view-model imports. Use narrow protocols at real replaceable service
boundaries, not a protocol for every class. Keep domain values immutable across
worker boundaries and prevent service locators or hidden singletons from
bypassing injected dependencies.

Before declaring a module complete, demonstrate three changes independently:
replace a worker/provider, replace persistence through an adapter, and change the
view layout. Each should leave unrelated modules untouched. This is the practical
maintainability acceptance criterion for future RawCull enhancements.
