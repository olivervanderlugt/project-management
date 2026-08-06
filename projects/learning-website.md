---
title: Learn — personal learning app
status: active
next: Review en merge learning-website PR #1 (Pages-deploy) en zet Pages-bron op "GitHub Actions"
due:
started:
repo: olivervanderlugt/learning-website
preview:
stack: Vite, React, TypeScript, Tailwind v4, zustand, xyflow
tags: learning, robotics, frontend
---

## What this is

One shared knowledge graph across CS, maths, physics, engineering and robotics, built as a
playable skill tree. MVP is the full CS skill tree plus module 1 "How Computers Work" fully
playable. Long-term, every domain grows to bachelor's depth inside one graph with
cross-subject links, and robotics is the converging goal.

No backend and no router, by design. State is one versioned localStorage blob.

## Where it stands

Imported from the repo on 2026-08-06, not from memory — everything here is read off the
code.

Components exist for the skill tree, lesson player, gate sandbox, cumulative review flow,
review queue, progress and skills panels, and achievement toasts. `docs/` holds three
rounds of curriculum gap analysis plus an employability-skills coverage note. Last commit
was 2026-07-27.

## Open questions

- No next action set. This came from git, not from your head — you have to decide it.
- Three versions of the gap analysis suggests the curriculum scope kept moving. Is it
  settled now?
