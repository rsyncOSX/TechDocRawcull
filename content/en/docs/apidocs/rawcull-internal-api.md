+++
author = "Thomas Evensen"
title = "RawCull Internal Swift API"
date = "2026-10-22"
lastmod = "2026-10-22"
description = "Application-internal catalog, culling, preview, scoring, similarity, AI, persistence and copy method contracts."
weight = 25
mermaid = true
+++

# RawCull Internal Swift API

Use this reference alongside the
[application walkthrough]({{< relref "rawcullapidoc.md" >}}). These are internal
Swift interfaces in RawCull 3.3.5, build 425, not an independently versioned SDK.
Observable progress and completion state remain part of asynchronous contracts.
Source excerpts show the reviewed implementation; usage examples are illustrative
calls inside the application target.

## Internal method reference

### Calling conventions

Examples below run inside the app module. Names such as `viewModel`, `runtime`, `feature`, `file`, `groupFiles`, `source`, and `destinationURL` represent existing, correctly configured instances or selected values. They are context snippets, not standalone programs. Use MainActor context for UI-facing models and `await` for actor calls. Void-returning actions often communicate success or failure through observable state, so completion alone is not proof of success.

### 1. Catalog loading and sorting

Source: [RawCullViewModel+Catalog.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/RawCullViewModel+Catalog.swift), [ScanFiles.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Actors/ScanFiles.swift).

| Function | Request | Response and effects |
|---|---|---|
| `startCatalogLoad(for:)` | Optional `ARWSourceCatalog` | Returns `Void`; schedules a persistence-safe transition. A nil source clears the working set. Same active source with access is a no-op. |
| `handleSourceChange(url:) async` | Active catalog URL | Scans, sorts, hydrates compatible similarity state, restores ratings/scoring, and preloads previews. Guards against obsolete catalog results. |
| `cancelCatalogLoad()` | None | Cancels transition and active load-related tasks. Does not delete catalog files. |
| `ScanFiles.scanFiles(url:onProgress:) async -> [FileItem]` | Folder URL; optional MainActor progress callback | Scans immediate directory contents, skips hidden files and admits formats recognized by `RawFormatRegistry`; reads metadata with bounded concurrency. Focus metadata is available through `decodedFocusPoints`. |
| `ScanFiles.sortFiles(_:by:searchText:) async -> [FileItem]` | Files, `FileItemSortDescriptor`, filename query | Sorts by name, modification date or size and filters names case-insensitively. This is filename filtering, separate from semantic search. |
| `handleSortOrderChange() async` | Current sort and filter state | Updates `catalogDisplayCandidates` and `filteredFiles`; ignores superseded work. |
| `applyFilters(to:) -> [FileItem]` | Pre-sorted files | Applies rating/sharpness policies and semantic ranking or image similarity ordering. Semantic empty-index state yields no visible results. |

```swift
// App UI entry point; this schedules the lifecycle transition.
viewModel.startCatalogLoad(for: source)

// Lower-level scan for an isolated integration path.
let scanner = ScanFiles()
let files = await scanner.scanFiles(url: catalogURL) { count in
    print("Discovered \(count) RAW files")
}
let ordered = await ScanFiles.sortFiles(
    files,
    by: FileItemSortDescriptor(field: .name, direction: .ascending),
    searchText: "DSC"
)
```

The scanner is nonthrowing; directory errors produce an empty result, and its catch-path warning is currently commented out. Cancellation detected after collection also returns an empty array. An empty array does not distinguish an empty folder from an access/read problem. In the app, prefer the lifecycle entry point over directly invoking its worker.

Helper functions: `beginCatalogLoad`, `isActiveCatalogLoad`, `resetCatalogWorkingSet`, and selection reconciliation implement transition bookkeeping.

### 2. Culling decisions and persistence

Source: [RawCullViewModel+Culling.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/RawCullViewModel+Culling.swift), [CullingModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/CullingModel.swift).

| Function | Request | Response and effects |
|---|---|---|
| `updateRating(for:rating:)` | One `FileItem` or an array, integer rating | Updates saved decisions for the selected catalog and refreshes derived UI state. No selected catalog means no mutation. |
| `updateRatingAndAdvance(for:rating:in:)` | File, rating, explicit ordered list | Rates the file, marks an active comparison group reviewed, and selects the next item when present. |
| `rating(for:) -> Int?` | File | Returns explicit cached rating or nil. |
| `getRating(for:) -> Int` | File | Returns rating or zero; this collapses unrated and explicit zero for display. |
| `extractTaggedfilenames() -> [String]` | Current catalog and active scope | Returns stored names rated at least 2 within `activeCatalogFiles`. |
| `extractRatedfilenames(_:) -> [String]` | Minimum rating | Returns qualifying names from `filteredFiles`. |
| `ensureLoaded() async -> Bool` | None, on `CullingModel` | Loads the store if necessary; false indicates loading did not succeed. |
| `flushPersistence() async -> Bool` | None, on `CullingModel` | Immediately persists pending changes; true also covers an already clean store. |
| `retryCullingPersistence() async -> Bool` | None, on view model | Retries loading or saving and restores presentation after successful load recovery. |
| `archiveCullingStoreAndReset() async -> Bool` | None, on view model | Archives a damaged store before resetting; subsequent save can still fail. This is a recovery action, not normal loading. |
| `clearCurrentCatalogCullingState()` / `clearAllCullingState()` | Current catalog / all stored catalogs | Clears saved culling state at the indicated scope; expose through the app's explicit user action. |

Rating conventions: `-1` means rejected; `.keepers` filters explicit `0`; star filters use `2...5`. A nil stored rating is distinct from explicit zero, even though `getRating` displays both as zero. Do not invent a one-star convention.

```swift
viewModel.updateRating(for: file, rating: 3)
let persisted = await viewModel.cullingModel.flushPersistence()
if !persisted {
    print(viewModel.cullingModel.persistenceError ?? "Save failed")
}
```

Response example: rating a file at 3 updates in-memory decisions immediately, while persistence may still be pending. Check `hasUnsavedChanges`, `persistenceError`, and load-failure state when reporting durability.

Helper functions: `rebuildRatingCache`, `refreshCullingDerivedState`, and `scheduleSave` maintain projections and write scheduling.

### 3. Preview loading, zoom and JPEG export

Source: [RequestThumbnail.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Actors/RequestThumbnail.swift), [RawCullViewModel+Thumbnails.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/RawCullViewModel+Thumbnails.swift), [ExtractAndSaveJPGs.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Actors/ExtractAndSaveJPGs.swift).

| Function | Request | Response and effects |
|---|---|---|
| `RequestThumbnail.requestThumbnail(for:targetSize:purpose:) async -> CGImage?` | Source URL, pixel size, `ThumbnailCacheKey.Purpose` | Resolves cached/generated thumbnail; coalesces matching requests. Nil means no image was produced. |
| `selectFile(_:)` | File | Changes the focused file through the view model. |
| `closeZoomOverlay()` / `resetZoom()` | None | Closes the overlay / resets zoom state. Session models hold detailed interaction state. |
| `presentExtractJPGsSheet()` | Current selection | Prepares the export sheet. |
| `startSelectedJPGExtraction(destination:exportMode:)` | Destination `ARWSourceCatalog`, `ExtractJPGExportMode` | Starts selected-file export and publishes completion/failure presentation. |
| `ExtractAndSaveJPGs.extractAndSavejpgs() async -> JPGExportResult` | Files, destination and mode supplied at initialization | Returns successful count plus per-file failures. Empty input returns zero successes and no failures. |
| `cancelExtractJPGSTask()` | None, on exporter | Requests cancellation. Result counts can describe partial work. |
| `ScanAndExtractJPGs.extractCatalogJPGs() async -> Int` | Source URLs configured on the actor | Warms the full-size preview cache. The count is processed files, including cache hits and unsuccessful decode attempts—not successful exported files. |
| `abort()` | Current view-model tasks | Stops workflow work managed by the view model; inspect its implementation when adding a new task type. |

```swift
let exporter = ExtractAndSaveJPGs(
    files: selectedFiles,
    destinationCatalogURL: destinationURL,
    exportMode: .embeddedJPG
)
let result = await exporter.extractAndSavejpgs()
print("Saved: \(result.succeeded)")
for failure in result.failures {
    print("\(failure.fileName): \(failure.message)")
}
```

`.embeddedJPG` exports embedded preview data. `.demosaicedRAW` renders a full-size JPEG through `SonyRawFormat`. Output names are `name.jpg` and `name_demosaic.jpg`; collisions produce numbered suffixes such as `name (1).jpg`. Existing files are protected by exclusive creation. Cancellation is cooperative and does not remove already written output; `JPGExportResult` has no separate cancellation flag.

Helper functions: `SaveJPGImage.outputURL`, JPEG encoding, timing estimates, progress callbacks, and per-file extraction routines support the public workflow. `SaveJPGImage.save` performs the actual throwing write.

### 4. Sharpness and focus analysis

Source: [RawCullViewModel+Sharpness.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/RawCullViewModel+Sharpness.swift), [SharpnessScoringModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/FocusandSharpness/SharpnessScoringModel.swift).

`calibrateAndScoreCurrentCatalog() async` calibrates and scores `sharpnessScoringTargetFiles`, re-sorts, and persists compatible scoring metadata after a non-cancelled run. Despite its name, the target may be a selection or filtered scope:

1. Explicit selected IDs take precedence.
2. A star filter narrows scoring to that rating.
3. Otherwise, scoring uses the active catalog scope, including semantic-search selection when active.

`handleSharpnessSortingChange(isEnabled:) async` applies current sorting and selects the first visible file when sharpness sorting is enabled. Read `sharpnessModel.scores`, `afPointScores` and `saliencyInfo` for results; these are measurements, not guaranteed judgments of photographic quality.

```swift
await viewModel.calibrateAndScoreCurrentCatalog()
let score: Float? = viewModel.sharpnessModel.scores[file.id]
```

`getFocusPoints() -> [FocusPoint]?` supplies selected-image focus information when available. Missing camera metadata is a supported absence; overlays must not invent focus points.

Helper functions: calibration adapters, persisted-score hydration, mask rendering and numeric scoring routines support these workflows. Preserve scoring signatures when reusing saved measurements.

### 5. Similarity indexing and semantic search

Source: [RawCullSimilarityFeature.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Intelligence/Similarity/RawCullSimilarityFeature.swift), [RawCullSemanticSearchFeature.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Intelligence/SemanticSearch/RawCullSemanticSearchFeature.swift).

| Function | Request | Response and effects |
|---|---|---|
| `hydrateCatalog(_:) async -> Bool` | `RawCullSimilarityCatalogHydrationRequest` | Loads compatible cached artifacts for a catalog identity; false covers rejected or obsolete hydration. |
| `indexCurrentCatalog(forceRefresh:) async` | Optional refresh flag, default false | Builds similarity artifacts for the current application scope. Read feature indexing progress and capability. |
| `hasCompleteIndex(for:) -> Bool` | Files | Reports coverage; does not perform indexing. |
| `search(for:) async` | Natural-language query | Ranks admitted files with compatible cached CLIP artifacts and applies result selection to the application. Blank text clears search. |
| `resultEvidence(for:)` | File ID | Optional rank and score for CLIP results. Rank is one-based; score is not a calibrated probability. |
| `setShowsAllResults(_:) async` / `adjustSelection(by:) async` | Result scope flag / count delta | Changes active semantic selection and invalidates scoped burst analysis. |
| `clear() async` / `cancel() async` | None, on semantic feature | Clears or cancels search and restores ordinary catalog presentation. |

```swift
await runtime.similarityFeature.indexCurrentCatalog()
await runtime.semanticSearchFeature.search(for: "an owl in flight")
let ids = runtime.semanticSearchFeature.orderedResultIDs
let summary = runtime.semanticSearchFeature.resultSummary
```

Search does not decode or index missing images as a side effect. It requires compatible CLIP artifacts; a Vision similarity backend alone does not supply text search. Read `presentation`, `state`, `progress`, and `hasEmptyIndex` to explain availability. A held Combined Review lease prevents starting a semantic search.

Semantic results create a durable active catalog scope used by other workflows until cleared or reindexed. Filename and rating admission still apply before semantic ranking. This matters when an export or analysis operates on fewer files than the whole folder.

Helper functions: generation checks, application binding, identity probes, backend projections, and selection reconciliation coordinate shared state.

### 6. Burst grouping and decisions

Source: [RawCullViewModel+BurstGrouping.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/RawCullViewModel+BurstGrouping.swift), [BurstAnalysisCoordinator.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Intelligence/BurstAnalysis/BurstAnalysisCoordinator.swift).

| Function | Request | Response and effects |
|---|---|---|
| `reindexBurstAnalysis() async` | Current catalog scope | Rebuilds burst analysis through the coordinator. |
| `reGroupBursts() async` | Current state and grouping configuration | Recomputes grouping using the application's current analysis context. |
| `restoreExistingFullCatalogBurstAnalysis() async -> Bool` | Current catalog | Attempts to restore full-catalog analysis; inspect returned success. |
| `keepBestInGroup(from:)` | Group files | When admitted, rates the winner 3 and others -1, captures undo and marks a decision applied. Winner preference is manual override, recommendation, sharpest file, then first file. |
| `keepTopTwoInGroup(from:)` | Group files | When admitted, rates first 3, second 2 and remaining frames -1, with undo capture. |
| `compareBurstGroup(_:)` | Group files | Opens group comparison. |
| `undoLastBurstAction()` | None | Restores the most recently captured burst action. |
| `markBurstGroupReviewed(groupID:)` / `deferBurstGroup(groupID:)` | Group ID | Updates review-queue state. |
| `advanceToNextBurstGroup(after:) -> Bool` | Current group ID | Attempts navigation; false means no next activation was made. |

```swift
viewModel.compareBurstGroup(groupFiles)
// Invoke after the user chooses to apply the group decision.
viewModel.keepBestInGroup(from: groupFiles)
```

These actions update culling decisions; rejection is a rating, not deletion of source RAW files. Empty or ineligible groups can be no-ops. Inspect ranking confidence and cautions before presenting automatic recommendations as certain.

Helper functions: group signatures, cache snapshots, ranking assembly, undo capture and review-state serialization maintain compatibility and presentation.

### 7. AI analysis input and feature actions

Source: [RawCullViewModel+AIAnalysis.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/RawCullViewModel+AIAnalysis.swift) and feature files under `RawCull/Intelligence`.

`aiAnalysisFiles(for:) -> [FileItem]` resolves `.gridSelection` or `.taggedImages`. Grid selection uses `selectedFileIDs`, falling back to the focused ID, and admits only visible filtered files. Tagged input uses persisted ratings of at least 2 within the active scope. `preserveAIAnalysisGridSelection()` freezes the fallback batch before browsing tagged images changes focus.

| Feature and function | Input | Result and lifecycle |
|---|---|---|
| `DeepAIReviewController.start(for:) async` | Burst/group files | Uses bound application context and SAM 3 capability to evaluate subject detail. Inspect controller state for unavailable, preparing, running, cancelled, failed or completed result. |
| `applyDeepAIReviewRecommendation(_:to:)` | Result and matching group files | Checks group signature, stores winner override, rates winner 3 and marks reviewed. Does not reject other frames. |
| `RawCullQwenAnalysisFeature.analyze(_:) async` | Files and nonblank `prompt` property | Processes files not already represented in results, uses local vision-language inference, validates structured output and retries a rejected response once with feedback. Publishes `results`, `progress`, `failureMessage`, `isRunning`. |
| `RawCullObjectAnalysisFeature.analyze(_:) async` | Files and feature configuration | Uses Qwen concept discovery, SAM 3 instance segmentation and a numbered review board for assessment. Publishes per-photo results and stage/progress state. |
| `RawCullObjectAnalysisFeature.retryFailed(_:) async` | Files | Retries failed object-analysis entries. |
| `cancel()` / `cancelAndWait() async` | None, on Deep Review, Qwen or Objects controller/feature | Requests cancellation / waits for cancellation handling to drain. Use the waiting form when ordering shutdown or replacement matters. |

```swift
let files = viewModel.aiAnalysisFiles(for: .gridSelection)
runtime.qwenAnalysisFeature.prompt =
    "Evaluate composition, exposure, subject visibility, and obstructions."
await runtime.qwenAnalysisFeature.analyze(files)
let assessments = runtime.qwenAnalysisFeature.results
```

Qwen requires an available vision model and nonempty pending files. Objects requires both Qwen and SAM 3. AI analysis can be unavailable or return rejected/partial evidence; model output is advisory. Objects analysis finds instances matching requested concepts, not a guaranteed exhaustive object inventory. Feature actions respect the Combined Review resource lease where implemented.

Helper functions: response decoders, validation feedback, mask outlines, object deduplication, prompt assembly and diagnostic capture support the main analysis APIs.

### 8. Combined Review

Source: [CombinedReviewFeature.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Intelligence/CombinedReview/CombinedReviewFeature.swift), [ReviewRunContract.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Intelligence/CombinedReview/ReviewRunContract.swift), and execution/backend files in the same directory.

| Function | Request | Response and effects |
|---|---|---|
| `prepareParameters(_:) async` | `[ReviewSelectedFile]` | Prepares admission and model/source information for the selected input. |
| `canStartReview(for:) -> Bool` | Selected files | Evaluates current admission; it does not run review. |
| `analyze(_:) async` | Selected files plus `criteria`, `depth`, source preference and retention properties | Acquires the shared lease, freezes source metadata, validates models and snapshot, persists manifest, executes stages and publishes results. |
| `restoreStoredRun() async` | None | Restores latest manifest and saved history when idle. |
| `resume() async` | Existing manifest | Revalidates sources, models, pipeline and artifacts before resuming compatible pending work. |
| `cancel()` | None | Cancels worker and marks the manifest; completion handling retains finished evidence. |
| `exactInput(_:) async -> CGImage?` | Retained input key | Decodes retained image when available; nil does not imply the report is missing. |
| `currentManifest() throws -> CombinedReviewRunV1` | Current state | Returns the validated current manifest or throws. |
| `clearAllReviews() async throws` | None | Deletes stored reviews through the feature's cleanup path. |
| `clearRejectedResponses() async` / `clearRetainedInputs() async` | None | Removes optional rejected-text diagnostics / retained source inputs. |

```swift
// selectedReviewFiles is the UI-prepared [ReviewSelectedFile].
feature.criteria = "Compare subject detail and explain coverage limits."
await feature.prepareParameters(selectedReviewFiles)
if feature.canStartReview(for: selectedReviewFiles) {
    await feature.analyze(selectedReviewFiles)
}
let manifest = feature.manifest
let failure = feature.failureMessage
```

Depth uses `standard`, `deep` or `exhaustive` budgets. The run records criteria, source fingerprints, model identities, stage versions, pipeline/render versions and retention policy. Source, overview, segmentation, identity, measurement, CLIP, crop observation, reconciliation, report and comparison are explicit stage categories; work dependencies and budgets constrain execution.

Success is observable evidence and run state, not simply the absence of a thrown error: `analyze` catches failures into `failureMessage` and progress. Failed synthesis can leave observations without a synthesized conclusion. Resume rejects changed sources or incompatible models/contracts rather than silently merging different evidence. Exact-input retention consumes storage and is optional.

Helper functions: manifest construction, work IDs, evidence grounding, geometry, mask registration, source decoding and budget admission implement the review contract.

### 9. Model installation and settings

Source: [RawCullAIModelDownloadsModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Intelligence/ModelManagement/RawCullAIModelDownloadsModel.swift), [RawCullAIModelDownloadService.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Intelligence/ModelManagement/RawCullAIModelDownloadService.swift), [SettingsViewModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/SettingsViewModel.swift).

| Function | Input | Response and effects |
|---|---|---|
| `refresh() async` | None, on downloads model | Refreshes installation states and applies managed locations to the configured consumer. |
| `acceptModelLicence(for:) async` | `RawCullAIModelDownloadID` | Records acceptance through coordinator; errors become failed download state. |
| `startModelDownload(_:)` | Model ID | Starts only when the current state admits download and no conflicting task/removal exists. Returns before download completes. |
| `cancelModelDownload(_:)` | Model ID | Requests download cancellation. |
| `removeManagedModel(_:) async` | Model ID | Removes an idle managed model and refreshes capability state. |
| `SettingsViewModel.ensureLoaded() async` | None | Ensures settings loading has been attempted. |
| `saveSettings() async -> Bool` | Current settings values | Saves settings; inspect false and persistence-failure state. |
| `retryPersistence(_:) async` | Optional failed settings operation | Retries settings persistence. |
| `asyncgetsettings() async -> SavedSettings` | None | Returns settings snapshot across the model's isolation boundary. |

```swift
let settings = await SettingsViewModel.shared.asyncgetsettings()
print(settings.thumbnailSizePreview)
let didSave = await SettingsViewModel.shared.saveSettings()
```

Download state is explicit: checking, unavailable, licenceRequired, notConfigured, ready, downloading, validating, installed, removing or failed. Downloading bytes is not the same as a validated installed model. App Store and self-hosted distribution can use different delivery mechanisms; use configured services rather than hardcoded download URLs.

Helper functions: catalogue descriptors, capability validation, licence provenance, presentation mapping and configuration revisions support model management.

### 10. RAW copy and process completion

Source: [ExecuteCopyFiles.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ParametersRsync/ExecuteCopyFiles.swift).

`ExecuteCopyFiles.startCopyFiles() -> Result<Void, CopyStartupFailure>` resolves configuration and selected files, obtains source/destination access, writes an operation-specific include list and launches streaming rsync. Its instance carries `config`, `dryrun`, `rating`, `copyTaggedFiles` and the bound view model. A successful return means the process started; it does not mean copying completed.

```swift
// copyOperation is an ExecuteCopyFiles configured by the copy UI.
switch copyOperation.startCopyFiles() {
case .success:
    print("Copy process started; await completion presentation")
case .failure(let error):
    print(error.localizedDescription)
}
```

Completion is represented by `CopyDataResult`, containing output, view output, `CopyOutcome`, and the frozen `CopyOperation` settings. Outcomes are `.success`, `.failed(message:)` and `.cancelled`. `CopyOperation.dryRun` distinguishes a preview from an actual copy; a successful dry run must not be reported as files copied. `close()` stops/closes the operation through its cleanup path.

Helper functions: streaming handler setup, unique include-list generation, output parsing, bookmark resolution and cleanup support startup and completion. Preserve unique include lists so overlapping operations cannot overwrite each other's selection.

### Reading asynchronous code without losing the thread

When following an async function, track three things: the state captured before suspension, the work performed by the awaited call, and the conditions checked before publishing its result. Actor isolation serializes access to actor state, but another operation can change that state while the function is suspended.

`handleSortOrderChange()` is a compact example. It captures the sort generation, catalog identity, selected source, sort order and text. After sorting, it verifies that those inputs still describe the current request.

**Source excerpt — publication guard in [RawCullViewModel+Catalog.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/RawCullViewModel+Catalog.swift):**

```swift
let sorted = await sortFiles(files, order, text)
guard !Task.isCancelled, sortGeneration == generation,
      currentSimilarityCatalogSnapshot.identity == catalog,
      selectedSource == source, sortOrder == order, searchText == text else { return }
catalogDisplayCandidates = sorted
filteredFiles = applyFilters(to: sorted)
```

Cancellation asks work to stop; the identity and generation checks decide whether its answer still belongs to the current application state. Both are needed because an awaited dependency can complete after cancellation or after the user changes the request. The function’s deferred cleanup also checks the generation before clearing `isSorting`, so an older sort cannot hide a newer sort’s progress.

Use this pattern as a reading aid throughout catalog loading, similarity hydration and model configuration. A guard after an `await` often expresses an ownership rule, not just defensive boilerplate.

### Use the tests as executable explanations

After following the implementation, open the corresponding tests. Their arranged state and expected outcomes make edge cases concrete. These links are a reading route through existing tests, not a claim that the suites have been run as part of editing this guide.

| Question | Test reference | What to look for |
|---|---|---|
| Can an old sort overwrite a new one? | [CatalogConcurrencyTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/CatalogConcurrencyTests.swift) | Gates deliberately release an older sort before the newer one; the older result must not publish or clear current progress. |
| Does analysis use selection or focus? | [AIAnalysisSelectionTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/AIAnalysisSelectionTests.swift) | Explicit selection is resolved in visible catalog order; focus is a fallback, and browsing tagged images preserves the captured batch. |
| Are the runtime services shared? | [RawCullIntelligenceRuntimeTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/RawCullIntelligenceRuntimeTests.swift) | Follow assembly and configuration expectations alongside the runtime’s identity assertions. |
| What happens when saving during quit fails? | [QuitRecoveryTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/QuitRecoveryTests.swift) | Read the injected flush, recovery and termination callbacks alongside `AppDelegate.beginTermination`. |
| What counts as a valid review run? | [ReviewRunContractTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/ReviewRunContractTests.swift) | Compare snapshot and work-contract validation with `ReviewRunContract.swift`. |
| Why did copying fail before starting? | [ExecuteCopyFilesStartupTests.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/ExecuteCopyFilesStartupTests.swift) | Compare setup failures with the typed startup result instead of assuming a subprocess ran. |

For example, this excerpt from the first selection test starts with three visible files and selects the third and first. The resolver returns the first and third because it walks the visible array, rather than iterating the unordered ID set.

**Source excerpt — selection behavior, with `first`, `second`, `third` and `state` prepared earlier in the test:**

```swift
state.viewModel.filteredFiles = [first, second, third]
state.viewModel.selectedFileIDs = [third.id, first.id]

#expect(
    state.viewModel.aiAnalysisFiles(for: .gridSelection).map(\.id)
        == [first.id, third.id],
)
```

For further test setup, read [TestIsolationHelpers.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/TestIsolationHelpers.swift) and [TEST_ARCHITECTURE.md](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCullTests/TEST_ARCHITECTURE.md). Injected loaders, writers, settings and temporary paths let tests exercise failures without depending on the user’s production catalogs or installed models.


## Viewer and inspection interfaces

| Owner | Entry point | Observable result / guard |
| --- | --- | --- |
| `ZoomSessionModel` | `beginRAWExposureInspection()`, `endRAWExposureInspection()` | Snapshot/restore selected source, EV and clipping; begin selects developed RAW |
| `ZoomSessionModel` | `navigate(by:from:in:using:)` | Returns false while inspecting exposure |
| `LoupeFocusPresentationModel` | `request(url:source:delay:operation:)`, `cancel()`, `reset()` | Generation-gated image/loading state; reset also clears cached identity |
| `SubjectOutlinePresentationModel` | `load(operation:)`, `reset()` | Obsolete async completion cannot replace current outline |
| `WriteSavedFilesJSON` | `diskUsage() async -> Int` | Current primary plus backup byte sizes via writer actor |
| `RawCullViewModel` | `burstGroupReviewState(groupID:)` | For ID −1, common explicit singleton state or `.none` |

Read [ZoomSessionModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/ZoomSessionModel.swift),
[LoupeFocusPresentationModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/LoupeFocusPresentationModel.swift),
[SubjectOutlinePresentationModel.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/ViewModels/SubjectOutlinePresentationModel.swift)
and [WriteSavedFilesJSON.swift](https://github.com/rsyncOSX/RawCull/blob/b46501739f6a09c0e2df352fc3ed2bf8e10a0e91/RawCull/Model/JSON/WriteSavedFilesJSON.swift).
The [viewer guide]({{< relref "../viewer-architecture.md" >}}) explains
task ownership; the [RAW guide]({{< relref "../raw-inspection.md" >}})
defines the render and display-evidence contracts.
