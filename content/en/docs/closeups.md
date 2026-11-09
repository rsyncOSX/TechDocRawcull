+++
title = "Close Up"
linkTitle = "Close Up"
description = "Compare detail across frames using manual regions, pinned references, recorded autofocus points and detected crops."
weight = 42
reviewed_commit = "a68253b73cbad14a7b1030dba6b439e6bce7d3da"
reviewed_version = "3.4.5"
reviewed_build = 436
reviewed_on = "2026-11-09"
review_scope = "source delta and reference check; content updated"
+++

Close Up is the inspection panel in the burst and Single Images workspace.
Use it to compare the same part of a subject across frames before choosing
a keeper. The manual cards give you control over the region and pixel source.
A strip above them shows automatic detections for the current frame.

## Compare two or more frames

1. Click a filmstrip frame to make it current. Command-click to toggle other
   frames into the comparison. Shift-click selects a displayed range, and
   Command-Shift-click adds a range to the selection. The inclusion checkboxes
   change comparison membership without activating another frame.
2. Open **Close-ups** in the workspace toolbar. With no explicit selection,
   the panel inspects the current frame.
3. Click the overview in each card to choose the region to inspect. Set the
   crop extent with **Region size**. Drag the crop or focus it and use the
   arrow keys to pan. Use **Zoom** to inspect the result more closely.
4. Click **Pin reference** on a strong frame. It stays visible while you
   change the comparison selection in that inspection session. Use
   **Replace reference** to switch baselines or **Unpin reference** to clear
   it. **Show image** activates the frame and opens the zoom overlay with
   group navigation and the current source.

Double-click a thumbnail on a burst card to open the workspace at that frame.
When comparing at most one frame, workspace navigation makes Close Up follow
the active frame. An explicit multi-frame comparison keeps its membership.

A new group starts a new inspection session. Manual regions are saved for
their source revisions, so revisiting a frame can restore its region.
**Reset region** resets that frame's chosen area. **Reset view** and
**Reset views** reset inspection pan and zoom.

## Choose a scale and pixel source

- **Fit region** fits each chosen area inside its card. Use it to compare
  framing, expression or the placement of detail.
- **Source pixels** uses the rendered source's pixel scale as the baseline.
  Check the source label and dimensions under the crop when judging fine
  detail across frames.
- **JPG** uses the preview path. The source label identifies which preview
  supplied the pixels, such as a sidecar JPG or an embedded preview.
- **RAW** uses a developed RAW render, with RAW 9 where supported and the
  system decoder otherwise. The picker displays **RAW 9** when all
  relevant frames support it. This picker controls the main stage and
  manual cards together. The automatic strip uses the embedded preview.
  If the main stage cannot show a JPG preview, **Try RAW** switches sources.

Turn on **Link pan/zoom** to move and zoom the cards together around their
independent regions. First place each region on the part you want to compare.
If a bird shifts between frames, center each region on its head before
linking the views.

## Inspect the recorded autofocus point

**Use AF point** uses the recorded autofocus location where supported.
RawCull maps the camera coordinates to the upright image and shares this
setting with the main stage. The recorded point tells you where the camera
reported focusing. Check the crop itself for sharpness. If the point is
unavailable or on a different part of the subject, select a manual region
in the overview.

## Read the automatic detection strip

**Detected faces and animal landmarks** uses the current frame's upright
embedded preview, capped at 1,600 pixels on its longest side. It refreshes
when you activate another frame and resumes after indexing. Detection and
manual comparison use separate regions.

| Tile | What you see | How to use it |
| --- | --- | --- |
| Human face | A face crop and, when available, a local preview detail value | Compare similar captures of the same face at comparable preview scales. |
| Animal head | A crop around usable head landmarks | Check head framing and visible detail. |
| Animal eye | A tighter crop around each usable eye landmark | Inspect the visible eye and use a manual RAW crop when more source detail is needed. |

RawCull uses Vision's animal body pose request for the pilot. A head crop
needs enough landmarks to establish a crop size. Eyes below the confidence
threshold are omitted, so a profile may show a single eye, and a head may
appear without eye tiles. Apple documents cat and dog support. Coverage
for birds, deer and other wildlife needs validation. Use the manual
overview for distant subjects, occlusions or missed detections.
[Apple Vision animal pose](https://developer.apple.com/videos/play/wwdc2023/10045/)

Animal tiles are for visual inspection. The human tile's detail value
measures local luminance gradients and is separate from ratings and burst
ranking. If the strip reports that detection is unavailable, use **Retry**.
A manual card with a render failure offers **Retry image**.

## Example workflow for a wildlife burst

Start with the best-looking pose and pin it. Select two nearby frames.
Use any animal tiles as a quick check, then choose each subject's eye or
head in the manual overviews. Switch to **RAW** and **Source pixels** to
judge fine detail from the developed render. Link pan and zoom after
aligning the regions. Use the workspace's rating or winner controls to
record your decision.

For implementation details, see [PhotoEvidenceKit]({{< relref "packages/photoevidencekit.md" >}}),
[PhotoAnalysisKit]({{< relref "packages/photoanalysiskit.md" >}}), and
[burst review]({{< relref "burstgroup.md" >}}).
