---
title: Learn — personal learning app
description: A playable skill tree over one shared knowledge graph — 133 lessons across CS, maths, physics and robotics, in the browser with no backend.
status: active
next: "Next chain, Ollie's call: C#/.NET (smallest, cleanest fit) vs OOP+Java (multi-session) vs data & BI vs db-depth — see learning-website CLAUDE.md 'Next items'"
due:
started: 2026-07-05
repo: olivervanderlugt/learning-website
preview: https://olivervanderlugt.github.io/learning-website/
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

Onboarding + guide mode shipped 2026-08-08 (Opus built, Fable gate-verified, merged to
main, deploy green): a replayable 4-step first-run tour (tappable status-card legend,
the ⏩ honesty mechanic, pick-a-start-domain that flies the map there) plus 5 contextual
💡 guide tips that fire the first time each feature becomes relevant — all off one derived
show-rule so legacy profiles with progress never see the tour, three new persisted fields,
export/import + legacy blobs verified, both themes. One real crash bug found and fixed by
the browser gate (AnimatePresence double-click step overflow).

The backend & APIs chain landed on main 2026-08-07 (Opus built, Fable gate-verified,
deploy green): web-http → web-server → web-api extending the `applied-software` domain,
tools-exam grown 10→14. That closes the whole web-and-apis skill family — employability
coverage is now 19 covered / 6 partial / 21 gap of 46. **133 playable lesson nodes across
17 domains**, each with a module exam. Gate green: build clean, map checker zero crossings
in both view tiers, content validator green on all 133 lessons (headless + in-browser),
web-http browser-played end-to-end (code screen live-run, 5/5 quiz, mastered +100 XP).

GitHub Pages deploy is LIVE and auto-runs on every push to main:
https://olivervanderlugt.github.io/learning-website/ serves the freshly-merged build.

## Open questions

- Curriculum scope (three gap-analysis docs): settled for now — the ranked Phase 1–3 depth
  backlog is done and CLAUDE.md names the open frontiers (Phase 4 leftovers, Stage 2
  rigor, Stage 3 labs, Phase-5 Tier-2 chains). Direction is chosen per session, one chain
  at a time.
- Next content call after backend & APIs: C#/.NET vs OOP+Java vs data & BI vs db-depth —
  ordering still open, Ollie's call (CLAUDE.md leans C#/.NET as smallest and cleanest).
