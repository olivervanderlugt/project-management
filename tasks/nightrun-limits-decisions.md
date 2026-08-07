---
title: Night run vs usage limits — three account-level decisions
project: hangar
status: blocked
added: 2026-08-07
effort: S
branch:
---

## Done means

Ollie has decided, and whoever executes has done, three things (any explicit
"no" also counts as done): (1) the routine's firing time is set relative to
his weekly reset moment (visible only to him at claude.ai/settings/usage) and
outside his own evening usage window; (2) usage credits with a monthly cap
are enabled or explicitly declined — agents may never enable them, it costs
money; (3) a catch-up firing a few hours after the main one is added or
explicitly declined (it spends more of the daily routine-run cap).

## Notes

Blocked on: Ollie. Background and the reasoning for each option:
`reference/nightrun-usage-limits.md`. The in-repo half of this work (overnight
rules 8–10: trail-before-work, stale-`doing` recovery, downgrade on limit
pressure) already landed 2026-08-07 via `tasks/hangar-nightrun-token-limits.md`.
