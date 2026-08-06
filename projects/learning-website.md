---
title: Learn — personal learning app
status: active
next: Merge the two parked worktree branches (math-calculus-4/-5 + dev-tooling/applied-software) into main and re-run the full quality gate
due:
started: 2026-07-05
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

Re-read from the repo on 2026-08-06 evening.

~123 playable lesson nodes across 16 domains, each with a module exam. The ranked Phase 1–3
depth backlog is complete; the map checker reports zero crossings in both view tiers. PR #1
(merged 2026-08-06) added a GitHub Pages deploy workflow — first run (triggered the same
evening) built fine but failed at "Setup Pages": Pages is not enabled on the repo. One
click from Ollie fixes it: repo Settings → Pages → Source: "GitHub Actions", then re-run
the workflow. Preview stays blank until that deploy is green.

Two finished content streams from 2026-07-22 are parked on remote branches, built and
committed but never merged (the merge was interrupted mid-session):

- `worktree-agent-ac1417f092bc06180` (4591cb6) — math-calculus-4/-5 chain, math-exam 34→38
- `worktree-agent-a712044fc679120af` (1a23b90) — dev-tooling chain (bash/git), new
  `applied-software` domain + exam

The merge plan is written out in the repo's CLAUDE.md under "CURRENT STATE": merge both,
resolve curriculum.ts conflicts, then build + validator + map checker in both tiers +
browser-verify before committing. That is the next action — it unblocks two done chains
and closes the git/bash employability-skill gaps.

## Open questions

- Curriculum scope (three gap-analysis docs): settled for now — the ranked Phase 1–3 depth
  backlog is done and CLAUDE.md names the open frontiers (Phase 2/4 leftovers, Stage 2
  rigor, Stage 3 labs, Phase-5 Tier-2 chains). Direction is chosen per session, one chain
  at a time.
- After the parked merge: next content call is math-stats follow-ups vs Phase-5 Tier-2
  (OOP/Java, C#, backend) — ordering still open, Ollie's call.
