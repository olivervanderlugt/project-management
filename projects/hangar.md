---
title: The Hangar
status: active
next: Set a next action on Learn and Percentile
due:
started: 2026-08-06
repo: olivervanderlugt/project-management
preview: https://olivervanderlugt.github.io/project-management/
stack: Markdown, Python 3, GitHub Pages
tags: tooling, personal
---

## What this is

A personal HQ for everything I'm working on: projects in flight, ideas parked,
decisions logged, and a weekly rhythm on top. Markdown in a git repo, with a
generated dashboard for the at-a-glance view.

The point is that it's the same place every time, and that Claude can work on it
without me re-explaining the structure.

## Where it stands

Structure, templates and the dashboard build are done. The four existing GitHub
repos were imported on 2026-08-06; two of them turned out to be empty. The board
publishes itself to GitHub Pages on every push, so it is up with the laptop shut.

Two active projects are sitting there with no next action, which is the point of
the red flag and the thing to fix first.

## Still to build

Asked for, not yet built. Kept here rather than in a chat, so it survives.

- **Working across projects from one place.** The board links out and hands you a
  scoped start prompt; it does not yet let you drive several projects from one
  view.
- **Memory across chats.** `CLAUDE.md` carries the Hangar's own rules, but there
  is no per-project briefing that a fresh session reads instead of re-deriving
  context from the code.
- **Token and context budget.** Start prompts cut the expensive first pass. No
  measurement, no budget per project.
- **Overnight work.** Nothing scheduled. Needs a decision on what may run
  unattended before it gets built — see the open question below.
- **A preview per project.** The field and the embed exist; only the Hangar has a
  live URL. Learn could go on GitHub Pages for free; Versa needs real hosting.
- **`main` branch.** Everything still sits on `claude/hangar-project-setup-kvhcad`.

## Open questions

- What may run unattended overnight? Preparing and reporting inside the Hangar is
  safe. Writing code in the project repos is not, without a review step.
- Does the weekly review actually happen, or does this go stale like every other
  system? Answer in three weeks, not now.
- Do ideas need more structure than a verdict and an effort estimate?
