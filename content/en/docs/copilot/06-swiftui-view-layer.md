+++
author = "Thomas Evensen"
title = "SwiftUI View Layer"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "RawCull windows, navigation, state flow, grid composition, and view-layer conventions."
tags = ["rawcull", "swiftui", "views", "state-management"]
categories = ["technical details"]
weight = 60
+++

# SwiftUI View Layer

`RawCull/Views/` (87 files across 16 subfolders, ~15k lines) is the
presentation layer. This doc covers the navigation architecture, the
grid/inspection tools that make up most of the screen time, and the SwiftUI
state-management idioms used consistently across the whole layer, so you can
match the existing style when adding a view.

## Navigation architecture

`RawCullApp` (see [Architecture Overview](../)) hosts three `Window`
scenes; the main one wraps `RawCullMainView`
(`Main/RawCullMainView.swift`), which is the root of everything a user
actually browses photos through.

`RawCullMainView` is a single `ZStack`-based router over five mutually
exclusive **view modes** (`RawCullViewModel.mainViewMode: MainViewMode`):

```swift
switch viewModel.mainViewMode {
case .loupe:          loupeSplit
case .grid:           gridSplit
case .similarityGrid: similarityGridSplit
case .ratedGrid:      ratedGridSplit
case .comparisonGrid: comparisonGridSplit
}
```

Each `*Split` computed property is a `NavigationSplitView` (sidebar +
detail), all sharing the same `RawCullSidebarMainView` sidebar
(`Views/RawCullSidebarMainView/`) so switching modes never rebuilds catalog
navigation. Two overlays sit above this switch in the `ZStack`, shown/hidden
independently of the mode: the in-window **zoom overlay**
(`ZoomOverlayView`, `zIndex(10)`) and a bottom **progress overlay** for JPEG
extraction (`ProgressCount`, `zIndex(12)`).

Switching modes has a side effect worth knowing about:
`onChange(of: viewModel.mainViewMode)` opens/closes
`GridThumbnailViewModel` (`gridthumbnailviewmodel.open(...)`/`.close()`) —
entering a grid mode hands it the current culling model, source, and
filtered files so its thumbnail loader can start; leaving cancels
everything so background decode work doesn't run for a screen the user
can't see.

### Menu / keyboard commands via `focusedSceneValue`

Global menu commands (Extract JPGs, Abort Task, Add Catalog, Copy Tagged
Files, Show Saved Files — defined in `Views/Tools/MenuCommands.swift` and
wired in `RawCullApp`'s `.commands { ... }`) don't reach through the view
hierarchy as parameters. Instead, `RawCullMainView` publishes bindings via
`.focusedSceneValue(\.extractJPGs, $viewModel.focusExtractJPGs)` and mirrors
menu-triggered boolean flips back into concrete actions with
`onChange(of: viewModel.focusExtractJPGs) { ... }`. This decouples the menu
bar (scene-level) from wherever in the view tree the acting view model
happens to be — a menu command can trigger main-view behavior without
threading a callback through several intermediate views.

## State management idioms

The codebase favors **explicit dependency injection over global singletons**
for its `@Observable` models:

- **`@Bindable var viewModel: RawCullViewModel`** — the dominant pattern
  (28+ occurrences) for any view that needs to both read and write central
  app state. Passed explicitly down the tree as a parameter, not read from
  `@Environment`, so different windows/hierarchies can (in principle) bind
  different instances and tests can substitute a fixture view model.
- **`@Environment(...)`** — used for the few models that are genuinely
  global-for-the-window-scene: `GridThumbnailViewModel` (injected once at
  `RawCullApp`'s root) and `RawCullViewModel` itself is *also* placed in the
  environment for convenience, but most views still take it as an explicit
  `@Bindable` parameter for clarity/testability.
- **`@State` (local)** — transient, view-local interaction state: hover,
  animation flags, collapsed/expanded sets, in-flight `Task` handles. Used
  120+ times; this is the majority of state in the view layer by count.
- **Dictionary-keyed per-item `@State`** — e.g.
  `ComparisonGridView`'s `imageStates: [FileItem.ID: ComparisonImageState]`.
  Needed because SwiftUI recycles cells in scrolling containers, so a plain
  `@State` declared *inside* a `ForEach` row is not reliable storage across
  scroll — keying by stable ID and hoisting the dictionary to the parent
  preserves per-item state (zoom/pan position, etc.) across scroll.

## The main grid: `CullingGridView`

`Views/CullingGrid/CullingGridView.swift` is the canonical implementation
other grid modes are built from (rated grid, similarity grid, comparison
grid all reuse or mirror its structure). Notable patterns:

### Render cache to avoid O(n²) recompute

Every hover, selection change, or animation frame would otherwise force
SwiftUI to recompute the full filtered/sorted/grouped file list. The view
instead computes an equatable cache key from just the inputs that actually
affect layout...

```swift
private var gridCacheKey: CullingGridRenderCacheKey {
    CullingGridRenderCacheKey(
        burstGroups: reviewFilteredBurstGroups, files: files,
        ratingFilter: ratingFilter, reviewQueueFilter: viewModel.burstReviewQueueFilter,
        scoresCount: viewModel.sharpnessModel.scores.count,
        scoreRevision: viewModel.sharpnessModel.scoreRevision,
        maxScore: viewModel.sharpnessModel.maxScore,
        burstAnalysisResults: viewModel.burstAnalysisResults,
    )
}
```

...and only rebuilds the derived `visibleBurstGroups` cache
(`.onChange(of: gridCacheKey, initial: true)`) when that key actually
changes. This is a manual, explicit alternative to relying on SwiftUI's
automatic dependency tracking, chosen because it gives fine-grained control
over *when* an expensive O(n) filter/sort/group pass reruns.

### Burst group collapse/expand

Burst groups can be shown "clean" (top-3 frames only) or fully expanded, and
the view tracks two independent `Set<Int>` of group IDs
(`expandedBurstGroupIDs`, `collapsedBurstGroupIDs`) so toggling a group's
visibility behaves correctly whichever display mode is active, without
losing the user's per-group choices when they switch modes.

### Selection: a stateless coordinator

Multi-select (click, ⌘-click, badge-based batch select) is implemented by a
**stateless** helper, `CullingGridSelectionCoordinator`, rather than logic
embedded in the view:

```swift
private func handleToggleSelection(for file: FileItem) {
    let next = CullingGridSelectionCoordinator.toggleSelection(
        fileID: file.id, state: selectionState, visibleIDs: visibleSelectionIDs,
        modifier: CullingGridSelectionModifier(flags: NSEvent.modifierFlags),
    )
    applySelectionState(next)
}
```

The view reads current selection into a value-type `CullingGridSelectionState`,
passes it plus modifier-key flags into a pure function, and writes the
returned new state back onto `viewModel`. This makes selection logic
independently testable without a live view hierarchy — the same shape used
for badge-based batch rating (`CullingGridSelectionCoordinator.matchingIDs`/
`.badgeSelectionItems`, which cross-reference burst rank, saliency label, and
sharpness score to find "all files like this one").

### Deep Review presentation

Burst group headers show a "Deep Review" button whose label/state is driven
directly from `deepAIReviewController.isRunning(groupID:)` and
`.isActionUnavailable`; tapping it presents `DeepAIReviewSheetView` as a
`.sheet(item:)`, and its `onApply` callback routes the accepted
recommendation back through
`viewModel.applyDeepAIReviewRecommendation(_:to:)` — the view never talks to
the AI backend directly, only through the controller (see
[Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/)).

## Photo inspection tools

- **`Views/ZoomViews`** — the in-window zoom overlay (`ZoomOverlayView`)
  replacing what used to be separate OS windows; supports pinch/keyboard
  zoom, pan, and a source toggle (thumbnail vs. full decode).
- **`Views/FocusPeek`, `Views/FocusPoints`** — focus-peaking rendering and an
  overlay of autofocus points parsed from EXIF/maker-notes data
  (`FocusPointsModel`/`FocusPoint`, surfaced by `RawCullViewModel.getFocusPoints()`).
- **`Views/Histogram`** — `HistogramView` downsamples the source `CGImage` to
  a bounded 512px-max dimension before computing histogram buckets
  (`context.interpolationQuality = .none` to preserve representative pixel
  values), turning an O(width·height) computation into a bounded O(512²)
  one regardless of the source RAW's native resolution.
- **Subject-mask regeneration in `ZoomOverlayView`** debounces expensive
  recomputation behind `Task.sleep` + cancellation, exactly like the async
  debouncing pattern below.

### A recurring async debounce pattern

Several views need to react to fast-changing input (scroll position, focus
config changes) without recomputing on every intermediate value:

```swift
.onChange(of: focusConfig) { _, _ in
    maskTask?.cancel()
    maskTask = Task {
        try? await Task.sleep(for: .milliseconds(400))
        guard !Task.isCancelled else { return }
        await regenerateMask()
    }
}
```

`ComparisonGridView`'s scroll-position debounce (120ms) and
`CullingModel.scheduleSave()`'s 350ms save debounce
(see [Culling and Persistence](../03-culling-and-persistence/)) follow
the identical shape: cancel the previous `Task`, sleep, check
`Task.isCancelled`, then act.

## Reusable components

- **`Views/ThumbnailComponents`** — the actual image tile view, rating
  controls, keyboard navigation modifiers, and hover/selection overlays
  shared by every grid mode.
- **`Views/Modifiers`** — custom `ViewModifier`s/button styles used across
  the app for consistent look and behavior.
- **`Views/FileViews`** — small file-metadata display components.
- **`Views/Progress`** — the shared progress-bar/overlay components used for
  scanning, thumbnail generation, and JPEG extraction.

## Settings, Saved Files, Tools

- **`Views/Settings`** (11 files) maps directly onto `SettingsViewModel`
  (cache sizes, thumbnail sizes, scoring parameters) and
  `RawCullAISettingsModel` (AI model selection/downloads) — see
  [Settings and Configuration](../07-settings-and-configuration/).
- **`Views/SavedFiles`** is a standalone browser over
  `CullingModel.savedFiles` (per-catalog rating history), independent of the
  currently-open catalog.
- **`Views/Tools`** holds the About window and `MenuCommands`.

## Accessibility

Grid tiles, focus-point controls, and other interactive elements set
explicit accessibility label/value/hint (e.g. `ImageItemView`,
`FocusPointControllerView`) rather than relying on SwiftUI's default
inference — follow this pattern for any new interactive photo-browsing
control.

## Where to look when extending this

- **New grid variant** → start from `CullingGridView`'s structure
  (render-cache key, selection coordinator, burst header) rather than
  writing bespoke filtering/selection logic.
- **New expensive per-frame computation** (a new overlay, a new visual
  analysis) → downsample defensively (see the histogram pattern) and gate
  behind the debounce-task pattern if it's triggered by fast-changing input.
- **New global action** (menu item, keyboard shortcut) → route it through
  `focusedSceneValue`, following the existing `extractJPGs`/`aborttask`
  bindings, rather than passing a new callback down through the view tree.
