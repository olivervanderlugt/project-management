---
title: Make the nightly routine survive Claude usage limits
project: hangar
status: done
added: 2026-08-07
effort: M
branch: claude/hangar-project-setup-kvhcad
---

## Done means

A researched, written-down answer to what actually happens when the nightly
Routine (a) hits the 5-hour or weekly usage limit mid-run, or (b) fires while
the account is already at a limit — with sources, not guesses. Then the best
feasible mitigations implemented in the Hangar: at minimum the routine's
instructions handle both cases explicitly (leave a night-log trail, set the
task back to a safe status, never leave a task stuck on `doing`), and anything
schedule- or budget-shaped that the research supports (e.g. firing time chosen
relative to limit resets, cheaper fallback work when near a limit). What can't
be fixed from inside the Hangar is recorded as a known limit in reference/.

## Notes

Ollie, 2026-08-07: "research what happens when the night time routine runs
into the token limit (any limit, like 5 hours or weekly) or is already on the
limit when started. Then find possible fixes ... and implement the best
one(s)." Research first (claude-code-guide agent), implementation after the
dashboard redesign lands to avoid two writers in this repo.

Closed 2026-08-07. Research delivered and written up (tagged docs/3rd-party/
inferred) in `reference/nightrun-usage-limits.md`. Implemented in-repo:
overnight rules 8–10 in CLAUDE.md — trail-before-work + commit-per-step,
stale-`doing` sweep at run start, downgrade-and-exit on limit errors. The
three account-level mitigations (firing time vs weekly reset, usage credits
with a cap, catch-up firing) only Ollie can decide — split off as
`tasks/nightrun-limits-decisions.md` (blocked).
