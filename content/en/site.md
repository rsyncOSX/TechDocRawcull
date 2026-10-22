---
title: Website information
linkTitle: Site info
description: Information about the website.
type: docs
params:
  body_class: td-no-left-sidebar
  hide_feedback: true
  cSpell:ignore: docsy
---

Site built with [<span class="badge bg-primary text-bg-primary fs-6">Docsy
v{{% param version %}} </span>][version]

## Build information

The site source is maintained in
[TechDocRawcull](https://github.com/rsyncOSX/TechDocRawcull).
The [documentation review record]({{< relref "docs/update.md" >}}) identifies
the application commit and package revisions used by the technical guides.
Deployment time and source-review time are separate: a site rebuild does not
mean the application implementation has been reviewed again.

[version]: <https://github.com/google/docsy/releases/v{{% param version %}}>
