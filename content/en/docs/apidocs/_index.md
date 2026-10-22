+++
author = "Thomas Evensen"
title = "Developer and API Documentation"
linkTitle = "API Documentation"
date = "2026-10-17"
lastmod = "2026-10-22"
description = "Developer guides and internal Swift API references for RawCull and RawBrowse."
tags = ["API"]
categories = ["technical details"]
weight = 70
+++

## Developer and API Guides

These guides follow each application's normal flow of operation and explain its
architecture, internal Swift interfaces, ownership, persistence, and error
handling. Start with the guide for the application you are working on.

| Guide | Coverage |
| ----- | -------- |
| [RawCull]({{< relref "rawcullapidoc.md" >}}) | Application startup, catalog scanning, culling, analysis, and export. |
| [RawBrowse]({{< relref "rabrowsweapidoc.md" >}}) | Folder browsing, preview, AI review, RAW 9 editing, and export. |

The API references describe application-internal Swift interfaces, rather than
HTTP endpoints or a versioned public SDK.

The RawCull guide is split into a narrative application tour and
[Internal Swift API]({{< relref "rawcull-internal-api.md" >}}) method contracts.
For current presentation and image-source policy, use
[Viewer Architecture]({{< relref "../viewer-architecture.md" >}}) and
[RAW Formats and Exposure Inspection]({{< relref "../raw-inspection.md" >}}).
