+++
author = "Thomas Evensen"
title = "Developer and API Documentation"
linkTitle = "API Documentation"
date = "2026-10-17"
lastmod = "2026-11-25"
description = "Developer guides and internal Swift API references for RawCull."
tags = ["API"]
categories = ["technical details"]
weight = 70

reviewed_commit = "5169ffd3487fe4ddc005d511fffa38172657d703"
reviewed_version = "3.5.0"
reviewed_build = 469
reviewed_on = "2026-11-25"
review_scope = "Checked the reading route."
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
They also describe the burst-review commands, semantic-state ownership, AF evidence
backfill and bounded preload saves. For measured behavior and its limits, read
[Performance Measurement]({{< relref "../performance.md" >}}).
