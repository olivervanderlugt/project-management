---
title: Learn — personal learning app
status: active
next: "Decide the next chain: C#/.NET (smallest) vs backend/APIs vs OOP+Java — see learning-website CLAUDE.md 'Next items'"
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

Streams A+B merged to main on 2026-08-07 (PR #2, merge commit 4731d77): the two parked
worktree branches landed as merges bfaefc6 (stream A, math-calculus-4/-5 chain, math-exam
34→38) and d19b45e (stream B, dev-tooling chain bash/git + new `applied-software` domain
and exam). 130 playable lesson nodes across 17 domains, each with a module exam. Gate
green: build clean, map checker zero crossings in both view tiers, content validator green
on all 130 lessons (headless + in-browser), math-calculus-4 browser-played end-to-end.

GitHub Pages deploy is LIVE: Pages is enabled (Source: GitHub Actions), the deploy
workflow ran green on the merge to main, and
https://olivervanderlugt.github.io/learning-website/ serves the freshly-merged build
(browser-verified — the new Applied Software Engineering domain shows on the map). Every
future push to main auto-deploys.

## Open questions

- Curriculum scope (three gap-analysis docs): settled for now — the ranked Phase 1–3 depth
  backlog is done and CLAUDE.md names the open frontiers (Phase 2/4 leftovers, Stage 2
  rigor, Stage 3 labs, Phase-5 Tier-2 chains). Direction is chosen per session, one chain
  at a time.
- After the parked merge: next content call is math-stats follow-ups vs Phase-5 Tier-2
  (OOP/Java, C#, backend) — ordering still open, Ollie's call.
