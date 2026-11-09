+++
author = "Thomas Evensen"
title = "New Features"
linkTitle = "New Features"
date = "2026-11-05"
lastmod = "2026-11-08"
description = "Implemented Close-ups and remaining P0 plans for RawCull development."
tags = ["roadmap", "planning", "culling"]
categories = ["technical details"]
weight = 55

reviewed_commit = "a68253b73cbad14a7b1030dba6b439e6bce7d3da"
reviewed_version = "3.4.5"
reviewed_build = 436
reviewed_on = "2026-11-09"
review_scope = "source delta and reference check; content updated; dated external evidence not requalified"
+++

# New Features

These documents track implemented work and proposed development after the
RawCull 3.4.0 build 434 baseline. Manual **Close-ups is implemented in RawCull** as of
7 November 2026; the broader unified-evidence workflow and XMP handoff remain
planned. Implementation status does not establish store-release availability.

Read them in this order:

1. [Features and competitive opportunities]({{< relref "newfeatures.md" >}}):
   the existing overview, competitive context and priority table.
2. [P0: XMP and editor handoff]({{< relref "xmp-editor-handoff.md" >}}):
   preserve review decisions across applications without losing metadata.
3. [P0: Unified burst evidence]({{< relref "unified-burst-evidence.md" >}}):
   completed manual Close-ups integration and the remaining work to unify evidence.

The overview identifies the current application baseline while preserving its dated
competitor research. The detailed plans distinguish
existing integration points from proposed contracts and behavior. Before coding,
recheck those integration points against the chosen application revision. Record
resolved decisions and validation results in the relevant plan as work proceeds.

## 3.4.5 development branch status

The [Close Up guide]({{< relref "/docs/closeups.md" >}}) covers the automatic
inspection strip. Human face TestFlight validation and representative wildlife
validation remain open. People-informed ranking remains proposed.
