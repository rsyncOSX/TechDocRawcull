+++
author = "Thomas Evensen"
title = "Developer and API Documentation"
linkTitle = "API Documentation"
date = "2026-10-17"
lastmod = "2026-10-31"
description = "Developer guides and internal Swift API references for RawCull."
tags = ["API"]
categories = ["technical details"]
weight = 70
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

The build-426 references include explicit burst-review commands, dedicated
semantic-state ownership, AF evidence backfill and bounded preload saves. For
measured behavior and its limits, read
[Performance Measurement]({{< relref "../performance.md" >}}).
