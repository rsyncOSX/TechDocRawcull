+++
author = "Thomas Evensen"
title = "Developer and API Documentation"
linkTitle = "API Documentation"
date = "2026-10-17"
lastmod = "2026-11-23"
description = "Developer guides and internal Swift API references for RawCull."
tags = ["API"]
categories = ["technical details"]
weight = 70

reviewed_commit = "0513a30e4567b4b5e3093e10791d49c86ecfe7e6"
reviewed_version = "3.4.9"
reviewed_build = 466
reviewed_on = "2026-11-23"
review_scope = "Updated the developer reading route for Review, batch assessment and release checks."
+++

## Developer and API Guides

These guides follow RawCull's normal flow of operation and explain its
architecture, internal Swift interfaces, ownership, persistence and error
handling.

| Guide | Coverage |
| ----- | -------- |
| [RawCull]({{< relref "rawcullapidoc.md" >}}) | Application startup, catalog scanning, culling, analysis, and export. |

The API references describe application-internal Swift interfaces, rather than
HTTP endpoints or a versioned public SDK.

The RawCull guide is split into a narrative application tour and
[Internal Swift API]({{< relref "rawcull-internal-api.md" >}}) method contracts.
For current presentation and image-source policy, use
[Viewer Architecture]({{< relref "../viewer-architecture.md" >}}) and
[RAW Formats and Exposure Inspection]({{< relref "../raw-inspection.md" >}}).

The current guides also cover Review admission, explicit decision actions, ranked-pair assessment and the App Store release checks.
The historical build-426 references include explicit burst-review commands, dedicated
semantic-state ownership, AF evidence backfill and bounded preload saves. For
measured behavior and its limits, read
[Performance Measurement]({{< relref "../performance.md" >}}).
