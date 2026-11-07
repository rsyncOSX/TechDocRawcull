+++
author = "Thomas Evensen"
title = "New Features"
linkTitle = "New Features"
date = "2026-11-05"
lastmod = "2026-11-07"
description = "Implemented Close-ups and remaining P0 plans for RawCull development."
tags = ["roadmap", "planning", "culling"]
categories = ["technical details"]
weight = 55
+++

# New Features

These documents track implemented work and proposed development after the
RawCull 3.3.6 baseline. Manual **Close-ups is implemented in RawCull** as of
7 November 2026; the broader unified-evidence workflow and XMP handoff remain
planned. Implementation status does not establish store-release availability.

Read them in this order:

1. [Features and competitive opportunities]({{< relref "newfeatures.md" >}}):
   the existing overview, competitive context and priority table.
2. [P0: XMP and editor handoff]({{< relref "xmp-editor-handoff.md" >}}):
   preserve review decisions across applications without losing metadata.
3. [P0: Unified burst evidence]({{< relref "unified-burst-evidence.md" >}}):
   completed manual Close-ups integration and the remaining work to unify evidence.

The overview retains its dated source baseline. The detailed plans distinguish
existing integration points from proposed contracts and behavior. Before coding,
recheck those integration points against the chosen application revision. Record
resolved decisions and validation results in the relevant plan as work proceeds.
