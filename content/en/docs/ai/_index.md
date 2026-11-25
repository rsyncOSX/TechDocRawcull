+++
author = "Thomas Evensen"
title = "Artificial Intelligence"
linkTitle = "AI"
date = "2026-08-21"
lastmod = "2026-11-25"
description = "Review, burst assessments, semantic search and the boundaries between RawCull and its model providers."
tags = ["ai", "clip", "sam3", "qwen", "photoaikit"]
categories = ["technical details"]
mermaid = true
weight = 60

reviewed_commit = "5169ffd3487fe4ddc005d511fffa38172657d703"
reviewed_version = "3.5.0"
reviewed_build = 469
reviewed_on = "2026-11-25"
review_scope = "Updated the Review entry for the preselected Focus check."
+++

# Artificial intelligence in RawCull

Use **Review** to inspect selected or tagged photos. Use the burst list to assess ranked pairs across a catalog. Both workflows run inference locally. Each exposes different evidence and stores its results for a different lifetime.

| Task | Input and result | Guide |
| --- | --- | --- |
| Inspect focus, describe a photo or run all Review stages | One to eight selected or tagged images. Focus check is preselected. Review saves a run record and can retain the exact inputs behind a finding. | [Review presets and findings]({{< relref "aiinrawcull.md" >}}) |
| Compare a burst’s top candidates across the catalog | The recommended and distinct alternate from each eligible ranked group. AI Assessments displays session results. | [Burst groups]({{< relref "/docs/burstgroup.md" >}}) |
| Request an assessment from a desktop AI client | An authorized MCP source job. The consumer reads structured findings under the shared job’s consent and retention rules. | [RawCull MCP]({{< relref "/docs/mcp.md" >}}) |
| Find similar frames or search by description | Vision or CLIP image artifacts support visual similarity. Text queries require compatible CLIP embeddings. | [CLIP indexing and search]({{< relref "aiinrawcull.md" >}}#how-clip-works-in-rawcull) |

## Model and application boundaries

**SAM 3** produces candidate masks for prompted subjects. Review uses registered masks for subject-detail measurements. **DataComp CLIP** encodes images and text for comparison. **Qwen3-VL** supplies whole-photo descriptions, crop observations and report text where the preset calls for them. Qwen also supplies the structured findings for burst and MCP assessments. A stored model finding is advisory. Tagging, rating and marking a burst reviewed require an explicit action.

PhotoAIKit owns provider contracts, model validation, inference backends and reusable indexing workflows. RawCull owns the catalog, file access, model activation, run budgets, evidence presentation and culling decisions. PhotoAnalysisKit owns sharpness and Vision measurement facilities. Its Vision queue is also used by the app’s PhotoAIKit feature-print backend.

- [Full Review execution]({{< relref "full-review.md" >}}) follows the preset from SwiftUI through model URLs, prompts, inference and saved evidence.
- [AI runtime]({{< relref "airuntime.md" >}}) traces how settings changes reach a running service.
- [Model preparation]({{< relref "rawcullai.md" >}}) records the pinned build recipe for the three model packs.
- [Package snapshot]({{< relref "/docs/packages/_index.md" >}}) identifies the revisions used by the application.

The earlier AI Analysis tabs appeared in development builds. Their source-level replacement and rationale are recorded in the [AI feature decision](https://github.com/rsyncOSX/RawCull/blob/5169ffd3487fe4ddc005d511fffa38172657d703/Docs/ai-features-decision.md).
