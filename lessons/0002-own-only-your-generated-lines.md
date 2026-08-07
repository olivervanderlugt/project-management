---
title: A generator owns only the lines it generated itself
scope: builders
goal: veiliger, effectiever
source: weekly-review-automatic 2026-08-07 — script wiste twee handgeschreven Wins-regels van Ollie
added: 2026-08-07
status: active
---

## Rule

When a script or agent (re)writes a file that Ollie also writes in by hand, it may only replace lines that match its own generated pattern; every other line survives verbatim. Silently overwriting hand-written content is data loss, whatever the section is called — if in doubt, keep the line and put the generated block below it.
