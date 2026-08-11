---
title: Overnight runs merge their own PR instead of leaving it for review
status: accepted
date: 2026-08-10
---

## Context

Since the first working overnight run (2026-08-07), the routine built a task
on its own branch, opened a PR, and stopped — Ollie reviewed and merged by
hand the next morning. `CLAUDE.md`'s "Stop at three open overnight PRs" rule
existed because of that: unreviewed PRs are debt, and debt compounds if the
run keeps producing more of them than one person can read.

The check step (`hangar-checker` reading the diff against the task's
`## Done means` and trying to prove it is *not* done, or the inline
self-check when subagents aren't available) already exists as the
substantive quality gate. In practice it has been doing the actual review
work — reading the diff, re-running the tests itself, probing edge cases the
builder didn't think of — before a PR ever reaches Ollie. The morning review
had become reading something already checked, not catching what the checker
missed.

Ollie asked, in chat on 2026-08-10, for overnight runs to merge, save and
quit on their own once a task is done — a standing rule, not a one-off for
that night's PR.

## Decision

From 2026-08-10, an overnight run merges its own PR immediately once tests
are green and the checker (or the inline self-check, per `CLAUDE.md` rule 8)
has passed the diff against the task's `## Done means`. It does not wait for
Ollie to look at it first. The checker's pass is the review gate now.

A PR only stays open if GitHub itself won't merge it — a failing required
check, a real conflict, branch protection — never because a human hasn't
looked yet. The "stop at three open overnight PRs" rule stays, but it now
means three *stuck* PRs (merges GitHub refused), not three unreviewed ones.

This does not change anything else about the overnight rules: still one task
a night, still `ready` only, still never `main` directly, still tests must
pass, still never credentials/deploys/spend, still a night-log trail.

## Consequences

Makes easy: code that passes its check ships the same night instead of
sitting until Ollie has time to read it — the whole point of running
overnight in the first place. Fewer stale branches, fewer PRs Ollie feels
obligated to reread later.

Makes harder / worth watching: the checker is now the *only* gate between a
plausible-looking diff and `main`. If it is ever wrong — misses a real bug,
gets fooled by a task written too vaguely — that lands on `main` unreviewed
until Ollie happens to notice, not the next morning during a PR read. Worth
revisiting if a checker-approved merge ever turns out to have been wrong.
