+++
author = "Thomas Evensen"
title = "New Features"
linkTitle = "New Features"
date = "2026-11-05"
lastmod = "2026-11-05"
description = "Feature opportunities and detailed P0 plans for future RawCull development."
tags = ["roadmap", "planning", "culling"]
categories = ["technical details"]
weight = 55
+++

# New Features

These documents describe proposed development after RawCull 3.3.6. They are
planning material for discussion, implementation pickup and later revision;
they do not announce released functionality or a delivery date.

Read them in this order:

1. [Features and competitive opportunities]({{< relref "newfeatures.md" >}}):
   the existing overview, competitive context and priority table.
2. [P0: XMP and editor handoff]({{< relref "xmp-editor-handoff.md" >}}):
   preserve review decisions across applications without losing metadata.
3. [P0: Unified burst evidence]({{< relref "unified-burst-evidence.md" >}}):
   compare the intended subject and understand the evidence behind a suggestion.

The overview retains its dated source baseline. The detailed plans distinguish
existing integration points from proposed contracts and behavior. Before coding,
recheck those integration points against the chosen application revision. Record
resolved decisions and validation results in the relevant plan as work proceeds.
