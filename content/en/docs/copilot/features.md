+++
author = "Thomas Evensen"
title = "RawCull Features and Roadmap"
linkTitle = "Features and Roadmap"
date = "2026-09-04"
lastmod = "2026-09-04"
description = "RawCull's product position, design principles, and post-3.2.0 roadmap."
tags = ["rawcull", "features", "roadmap", "product"]
categories = ["technical details"]
weight = 80
+++

# RawCull vs. Other Culling Apps, and Where RawCull Goes After 3.2.0

This document is deliberately different from the rest of the `Docs/` catalog:
docs 00–07 and `runtime.md` explain *how the code works*. This one is a
**product-positioning and roadmap** document — it compares RawCull (current
version **3.2.0**) against other well-known photo-culling tools on macOS, and
lays out a set of principles and concrete ideas for how the app should evolve
afterward. It's written for the same reader as the rest of the catalog
(Swift/SwiftUI-literate, new to this codebase), but the goal here is product
understanding, not implementation detail.

> **Disclaimer:** competitor feature descriptions below are based on public
> marketing material, documentation, and third-party reviews as of the
> research done while writing this document (early 2026), not on inspecting
> their source code — RawCull is the only app in this comparison whose
> internals this doc catalog can actually verify. Competitors update
> frequently; treat specifics (exact AI models, pricing) as approximate and
> re-verify before quoting them externally.

## What RawCull is, in one paragraph

RawCull is a **100% dedicated RAW-photo culling app** for macOS. It scans a
folder of RAW files (Sony ARW today — see
[Image Pipeline and Caching](../02-image-pipeline-and-caching/)), decodes
fast previews, lets the photographer rate/reject/flag images, optionally
groups near-duplicate "burst" shots and recommends a sharpest-on-subject
winner using on-device AI (see
[Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/)), and
copies the keepers out to a destination folder via `rsync` (see
[Export and Copy Pipeline](../04-export-copy-pipeline/)). It does not edit
photos, does not manage a permanent asset library, and does not touch the
network for anything photo-related — everything AI-driven runs locally via
Apple's CoreAI framework.

That single-purpose scope is not an accident or a limitation to be "fixed" —
it's RawCull's defining design constraint, and it's central to how this
document evaluates competitors and proposes future work.

## The competitive landscape

The table below focuses on macOS-available culling tools that photographers
commonly compare against. It's ordered roughly from "manual, no AI" to
"heavily AI-automated."

| App | Platform | AI culling | Runs locally? | Auto-applies ratings? | Pricing model | Primary audience |
|---|---|---|---|---|---|---|
| **RawCull 3.2.0** | macOS only | Yes (similarity/burst grouping, semantic search, Deep Review recommendation) | 100% on-device (Apple CoreAI) | **Never** — advisory only | (project-specific) | RAW shooters who want a fast, private, single-purpose culler |
| **Photo Mechanic** | macOS, Windows | No | N/A | No | One-time license | Sports/press/agency — pure speed and metadata, no AI at all |
| **FastRawViewer** | macOS, Windows, Linux | No | N/A | No | One-time license | Technical pixel-level RAW inspection (true histogram, focus peaking) |
| **Narrative Select** | macOS, Windows | Yes (face/expression detection, scene/angle grouping) | Mixed (has cloud-connected features) | No — AI scores, user approves every keeper | Free tier + paid plans | Portrait/wedding photographers who want AI guidance with full manual override |
| **Aftershoot** | macOS, Windows | Yes (blink/blur/focus detection, full auto-select mode, AI editing) | Mostly local processing, cloud account required | **Yes, by default** in its automated mode (user can review after) | Subscription | High-volume wedding/event shooters who want maximum automation |
| **Adobe Lightroom Classic** ("Assisted Culling") | macOS, Windows | Yes (subject/eye sharpness, eyes-open detection) | On-device processing, no upload required | Auto-sorts into Selects/Rejects bins, user reviews before committing | Subscription (Creative Cloud) | Existing Lightroom users who want AI-assisted first-pass sorting inside their normal catalog workflow |
| Capture One / ON1 Photo RAW / Photo Supreme (honorable mentions) | macOS, Windows | Limited or none (mostly manual flag/rating tools bundled into a much larger RAW-editing/DAM product) | Local | No | One-time or subscription | Photographers who want culling as one small feature of an all-in-one editor/DAM |

### Where RawCull sits

- **Vs. Photo Mechanic / FastRawViewer** — RawCull adds AI-assisted burst
  grouping and a Deep Review recommendation that these tools simply don't
  attempt. It trades some of Photo Mechanic's legendary raw ingest speed and
  metadata/captioning depth for AI-assisted grouping and recommendation
  features neither manual tool offers.
- **Vs. Narrative Select** — closest philosophical match: both treat AI as an
  *advisor*, not a decision-maker, and both let the user override every AI
  suggestion. The difference is architectural, not philosophical: RawCull's
  AI stack is 100% local (Apple CoreAI models bundled/downloaded per-device,
  see [05](../05-intelligence-ai-subsystem/)), while Narrative Select's
  feature set includes cloud-connected components. RawCull is also a
  narrower, single-purpose tool; Narrative Select bundles a broader editing
  and Lightroom-sync workflow around its culling core.
- **Vs. Aftershoot** — the sharpest philosophical contrast in this table.
  Aftershoot's default mode is designed to *auto-select and auto-reject on
  the user's behalf* at scale; RawCull's Deep Review pipeline is deliberately
  built so that segmentation/focus scoring only ever **recommends** a burst
  winner (see [Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/#deep-review) —
  the ranking is surfaced as a suggestion in the UI, no rating is written
  automatically). RawCull will never adopt Aftershoot's "commit an automatic
  cull pass" model — see the non-goals below.
- **Vs. Lightroom Classic's Assisted Culling** — Adobe's newest feature
  validates RawCull's core bet (on-device AI-assisted culling with a
  human-reviewed Selects/Rejects step is where the industry is heading), but
  it's one feature bolted onto a large, general-purpose RAW editor/DAM/cloud
  product with a subscription tied to the whole Creative Cloud suite.
  RawCull's entire surface area — UI, persistence model, export pipeline — is
  built around culling and nothing else.
- **Vs. Capture One / ON1 / Photo Supreme** — these are RAW *editors* or
  *digital asset managers* first, with basic rating/flagging tools as one
  feature among many (develop modules, layers, catalogs, cloud sync, plugin
  ecosystems). RawCull deliberately doesn't compete on any of that; it does
  one job — get from "folder of RAW files" to "folder of keepers" as fast
  and as advisedly as possible — and stops there.

### RawCull's genuine current gaps

Being honest about the comparison also means naming where RawCull is behind:

- **RAW format coverage.** Today RawCull decodes Sony ARW only (via
  `RawParserKit` — see
  [Image Pipeline and Caching](../02-image-pipeline-and-caching/)).
  Every competitor above supports far more camera makes out of the box.
- **Metadata/captioning depth.** Photo Mechanic's IPTC/caption/renaming
  toolset has no equivalent in RawCull; RawCull's persistence model
  (`03-Culling-and-Persistence.md`) is rating/status-only, not general
  metadata editing.
- **Face/expression-specific signals.** Narrative Select's and Lightroom's
  eyes-open/expression detection is more specialized than RawCull's current
  sharpness-on-subject Deep Review scoring — there's no dedicated "eyes
  closed" or "best expression" signal yet.
- **Multi-platform reach.** RawCull is macOS-only by design (it's a native
  SwiftUI app, see
  [SwiftUI View Layer](../06-swiftui-view-layer/)); several competitors
  also ship a Windows build.

None of these are reasons to broaden RawCull's mission — see below.

## RawCull's non-negotiable principles

Everything in the roadmap section that follows is filtered through three
rules that define what RawCull *is* and will keep being, even as it grows:

1. **RawCull is a 100% dedicated culling app.** Every future enhancement must
   serve the act of culling — deciding what to keep, reject, or export.
   RawCull is not going to grow into a RAW editor, a DAM, a print/proofing
   tool, or a cloud photo library. If a feature idea doesn't make culling
   faster, clearer, or more confident, it doesn't belong in RawCull, no
   matter how popular it is in adjacent tools.
2. **AI enhancements are local-first and culling-relevant only.** New
   AI-assisted features may use Apple's CoreAI framework (the same stack
   documented in [05](../05-intelligence-ai-subsystem/) and
   [Intelligence Runtime](../runtime/)) — but only when the function is directly
   relevant to *deciding what to keep*. AI is not a checkbox to add for its
   own sake, and it never leaves the device: no photo, embedding, or model
   input is uploaded anywhere. If Apple ships a CoreAI capability that
   doesn't help culling decisions (e.g. generative editing), it's out of
   scope for RawCull regardless of how easy it would be to bolt on.
3. **RawCull never culls automatically. It may advise. The user decides.**
   This is the line that separates RawCull from tools like Aftershoot's
   auto-select mode. Every AI signal in RawCull — burst grouping, semantic
   search, Deep Review's recommended winner, and any future signal — is
   surfaced as a *suggestion the user can see, inspect, and override*.
   No code path may write a rating, reject, or flag without a direct user
   action. This isn't just a UX preference; it's an architectural invariant
   that should be enforced the same way `apply(configuration:)`'s guards are
   enforced in the Intelligence runtime (see
   [Intelligence Runtime](../runtime/#applyconfiguration-revision-gate-then-identity-diff)) — any PR that lets an
   AI pipeline call `CullingModel.updateRating`/`updateRatings` directly,
   without going through explicit user interaction, should be treated as a
   design regression, not a feature.

## How RawCull should evolve after 3.2.0

The ideas below are grouped by theme. All of them respect the three
principles above; none of them turn RawCull into something it isn't.

### 1. Broaden RAW format support (highest-leverage, lowest AI-relevance)

The single biggest gap versus every competitor in the table is format
coverage. `RawParserKit` decoding more camera RAW formats (Canon CR2/CR3,
Nikon NEF, Fujifilm RAF, generic DNG) would make RawCull usable by a much
larger share of photographers without touching the culling model, the
Intelligence subsystem, or the export pipeline at all — this is a pure
"widen the front door" investment, not a culling-feature investment, but it's
a prerequisite for RawCull to be a realistic choice for most shooters.

### 2. Deepen the advisory signals Deep Review can offer

Today's Deep Review recommends a burst winner using subject segmentation +
focus scoring. Candidate CoreAI-relevant extensions, all surfaced as
*additional advisory signal, never as an automatic rating*:

- **Eyes-open / blink detection** as a per-face badge on thumbnails in
  portrait/group bursts — closing the specific gap versus Narrative Select
  and Lightroom's Assisted Culling, without adopting their auto-sort step.
  Shown next to the existing sharpness recommendation, not replacing the
  user's decision.
- **Composition/subject-framing hints** (e.g. "subject partially
  out-of-frame") using the same segmentation masks Deep Review already
  computes — no new model download, just a new interpretation of existing
  CoreAI output.
- **Confidence-scored "why this one" explanations** — instead of only a
  ranked winner, show the actual signal that drove the ranking (sharper eye
  region vs. rest of frame, better subject-to-background separation), so the
  photographer can quickly sanity-check the suggestion rather than trust it
  blindly. This directly reinforces principle 3: showing *why* keeps the
  human in the loop instead of turning the recommendation into a black box.

### 3. Let the AI learn review *order*, never review *outcome*

A high-value, principle-safe idea borrowed from the industry's direction
(Lightroom's and Aftershoot's models learn from user behavior) without
crossing into auto-culling: use on-device signals to **re-order** which
photos/bursts are surfaced for review first (e.g. surface likely-reject
technical failures — badly out of focus, badly clipped — early, so a
photographer can dismiss the "easy no's" fast and spend attention on hard
calls). This changes *presentation order*, never a rating value — it's
squarely on the "advisory" side of principle 3, and it's a natural extension
of the existing `RatingFilter`/`filteredFiles` machinery documented in
[Culling and Persistence](../03-culling-and-persistence/).

### 4. Expand semantic search into a culling-time filter, not a library feature

The existing CLIP-backed semantic search (see
[Intelligence and AI Subsystem](../05-intelligence-ai-subsystem/#semantic-search))
is a natural fit for scaling up: "find all the photos where the subject is
looking at the camera," "find the photos with a clean background," etc.,
scoped strictly to *helping decide what to keep during this culling session*
— not evolving into a permanent searchable library/DAM feature that persists
independent of an active culling pass. The distinction matters: it keeps
semantic search a *culling tool*, not the seed of an asset-management
product.

### 5. Scale the pipeline for larger shoots

As format support broadens, session sizes will grow (multi-card, multi-day
event imports). The concurrency architecture
([Concurrency Architecture](../01-concurrency-architecture/)) and cache
layer ([02](../02-image-pipeline-and-caching/)) were built with backpressure
and coalescing in mind already; future work here is about *validating and
tuning* those mechanisms at 10k+ file scale (memory-mapped decode limits,
disk cache eviction policy, `TaskGroup` concurrency caps) rather than adding
new AI. This is infrastructure work that makes every other item in this list
viable at real-world event volumes.

### 6. Undo, audit, and confidence — trust infrastructure, not automation

Because RawCull's promise is "you decide, we assist," the tooling around that
promise should get stronger over time:

- A visible **undo/history** of rating changes (leaning on the existing
  debounced/revisioned persistence in
  [Culling and Persistence](../03-culling-and-persistence/)) so a
  photographer can always see and reverse what they (not the AI) did.
  Ideally, that history should also make it easy to audit that no rating was
  ever written by anything other than a direct user action — a debug/test
  hook that would let `RawCullTests` assert principle 3 mechanically, not
  just by code review.
- Clearer, persistent surfacing of **why** the AI grouped or ranked something
  a certain way (see item 2's "explanations" idea) — trust in an advisor
  comes from transparency, not just accuracy.

### 7. Model management stays user-controlled

As new CoreAI-backed capabilities are added, they should go through the same
model-management/licensing flow already documented in
[Settings and Configuration](../07-settings-and-configuration/) and
[Intelligence Runtime](../runtime/) — explicit download, explicit license acceptance,
visible storage footprint, and an explicit way to disable or remove a model.
No future AI feature should be silently bundled or silently auto-enabled;
the same configuration/consent discipline that today's segmentation and
similarity models follow should extend to every future model, keeping AI
capability itself an opt-in, inspectable part of the app rather than a black
box that "just runs."

## Explicit non-goals

To keep the roadmap honest and prevent scope creep, these are deliberately
**out of scope** for RawCull, regardless of competitive pressure:

- **No automatic rating, rejecting, or flagging of any photo, ever**, no
  matter how confident an AI signal is. This is principle 3, restated as a
  hard boundary, not a soft default that a "power user mode" could disable.
- **No RAW development/editing features** (exposure, color grading, layers,
  presets). RawCull decides *what* to keep, never *how it should look*.
- **No cloud photo storage or cloud-based AI processing.** All AI stays
  on-device via CoreAI; RawCull will not add a server-side component for
  photo analysis, even if it would unlock more powerful models.
- **No general-purpose digital asset management** (permanent searchable
  library independent of an active culling session, print/proofing/client
  gallery features, multi-user collaboration). RawCull's data model is
  scoped to "which of these files, in this catalog, do I keep" — not a
  library of everything a photographer has ever shot.
- **No expansion of the export step beyond "copy the keepers out."** The
  `rsync`-backed export pipeline ([04](../04-export-copy-pipeline/)) may grow
  more copy/rename options, but turning it into a publishing/delivery
  platform (client galleries, watermarking, web delivery) is out of scope —
  that's a job for the next tool in the photographer's chain, not RawCull.

## Where this fits in the documentation catalog

This document is a **product-level companion** to the technical docs, not a
technical deep dive itself — treat 00–07, `runtime.md`, and `issues.md` as
the source of truth for *how the code currently works*, and treat this
document as the source of truth for *why RawCull looks the way it does
compared to the rest of the market, and what problem the next feature should
solve*. When proposing a new feature, check it against the three principles
above before writing any code; when documenting it afterward, it belongs in
the relevant subsystem doc (01–07/`runtime.md`), not here.
