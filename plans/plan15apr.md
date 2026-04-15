# RawCull — Feature Design Notes

Design discussion and proposals from a codebase review session (2026-04-15).

---

## Context

RawCull is a native macOS photo culling app for Sony ARW RAW files. The app is mature in its core scanning, thumbnailing, sharpness scoring, and rating/export pipeline. This session identified the two highest-leverage areas for new development.

---

## 1. XMP Sidecar File Writing

### The Problem

All culling decisions (ratings −1 through 5, tags) are stored in a proprietary `SavedFiles.json` in the user's Documents folder. This data is invisible to every other tool in a photographer's workflow. After culling in RawCull, the user has to re-rate everything in Lightroom, Capture One, or Darktable from scratch.

The entire point of a culling tool is to feed decisions into an editing workflow. Right now that handoff is broken.

### What to Build

Write `.xmp` sidecar files alongside the `.arw` files after a culling session. XMP is the universal language all serious RAW editors read natively.

**Mapping:**

| RawCull rating | XMP field | Value |
|---|---|---|
| 5 | `xmp:Rating` | `5` |
| 4 | `xmp:Rating` | `4` |
| 3 | `xmp:Rating` | `3` |
| 2 | `xmp:Rating` | `2` |
| −1 (reject) | `xmp:Label` | `"Reject"` |
| 0 (unrated) | — | no sidecar written, or Rating omitted |

Optionally: write the Sony AF focus point coordinates as custom XMP fields for tooling that can use them.

### Why This Is the Highest-Leverage Feature

- Infrastructure already exists: `SavedFiles.json` has ratings, `FileItem` has file paths
- It is purely additive — no existing behavior changes
- Turns RawCull from a standalone utility into the first step in a professional workflow
- Compatible with Lightroom Classic, Capture One, Darktable, RawTherapee, digiKam

### Implementation Sketch

1. Add a `WriteXMPSidecars` actor (parallel to `ExtractAndSaveJPGs`)
2. For each `FileItem` with a non-zero rating, serialize a minimal XMP packet:
   ```xml
   <?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>
   <x:xmpmeta xmlns:x='adobe:ns:meta/'>
     <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
       <rdf:Description rdf:about=''
           xmlns:xmp='http://ns.adobe.com/xap/1.0/'>
         <xmp:Rating>5</xmp:Rating>
       </rdf:Description>
     </rdf:RDF>
   </x:xmpmeta>
   <?xpacket end='w'?>
   ```
3. Write to `<filename>.xmp` adjacent to the `.arw` file (standard sidecar convention)
4. Add a "Write XMP Sidecars" button to the export section of the UI, next to the existing rsync copy controls
5. Show progress (same pattern as `ExtractAndSaveJPGs`)

### Files to Touch

- New: `Actors/WriteXMPSidecars.swift`
- `Model/ViewModels/RawCullViewModel.swift` — add trigger method
- Relevant export/copy view in `Views/` — add button

---

## 2. Burst / Similarity Grouping UI

### The Problem

`SimilarityScoringModel` already computes `VNGenerateImageFeaturePrintRequest` embeddings for all files and stores `distances: [UUID: Float]`. But the current interaction requires:

1. User manually selects an anchor file
2. User clicks "Find Similar"
3. Entire flat list re-sorts by distance from that anchor

This is useful for finding duplicates of a known image but does nothing to surface burst groups automatically. Sony burst shooters take 10–30 frames in rapid succession and have to manually scan for the sharpest one in each sequence.

### Design Proposal

#### Auto-clustering on index completion

Instead of requiring anchor selection, run a **linear sequential pass** over the file list (already sorted by filename = shot number order) immediately after indexing completes:

- Compare each file to the previous file using existing `computeDistance()`
- If distance < threshold → same burst group
- If distance ≥ threshold → new group starts

This is O(n) comparisons (not O(n²)) and works naturally because Sony files are named sequentially (`DSC_1234.ARW`, `DSC_1235.ARW`…). Burst shots are always consecutive.

Within each group, rank by existing sharpness score (descending) to identify the best frame.

#### Visual grouping in the grid

Keep the existing `LazyVGrid` flat layout but inject **section headers** between burst groups using SwiftUI `Section`. Each section header shows:

```
Burst · 8 frames · Best: DSC_1238 (87%)   [Keep Best]  [Reject All]
```

- The "best" frame (highest sharpness score in group) gets a gold crown badge instead of the standard sharpness badge
- Cells in the same group share a subtle background tint or matching colored top border
- No collapsing — headers are lightweight, always visible

#### "Keep Best" action

The primary interaction per group:

- Auto-rates the sharpest frame at `★★★` (or configurable default)
- Auto-rates all other frames in the group as `-1` (reject)
- Shows an undo toast

If sharpness scoring has not been run for the group, the button is disabled with tooltip: *"Run sharpness scoring first"*.

#### Threshold control

One slider: **"Burst sensitivity"** in `SimilarityControlsView`.

- Low → only near-identical frames grouped (tight burst)
- High → similar scenes across the session grouped
- Default: ~0.25 (VNFeaturePrint distances are typically 0.0–1.0)
- Live preview of group count as slider moves

#### Combined trigger

Replace the two-step "Index Similarity" + "Find Similar" flow with a single **"Index + Group Bursts"** button for this mode. The existing "Find Similar" anchor-based flow stays available for cross-catalog duplicate hunting.

### Data Model Changes

| Change | Where |
|---|---|
| Add `burstGroupID: Int?` to `FileItem` | `Model/ARWSourceItems/FileItem.swift` |
| Clustering logic after `indexFiles()` completes | `Model/ViewModels/SimilarityScoringModel.swift` or new `RawCullViewModel+BurstGrouping.swift` |
| `applyFilters()` produces grouped output when burst mode is active | `Model/ViewModels/RawCullViewModel.swift` |
| Section headers + "Keep Best" button | Grid view in `Views/GridView/` |
| Threshold slider | `Views/SimilarityControlsView.swift` |

### Resulting Workflow

1. Open catalog, thumbnails load
2. Click **"Index + Group Bursts"**
3. Grid redraws with burst section headers
4. Click **"Keep Best"** on each section that matters
5. Done — full shoot culled in one pass

---

## Priority Order

1. **XMP Sidecar Writing** — highest leverage, unblocks the editing workflow handoff, low complexity
2. **Burst Grouping UI** — highest UX impact for Sony burst shooters, moderate complexity
