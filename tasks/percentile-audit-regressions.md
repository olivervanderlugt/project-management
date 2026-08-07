---
title: Work out which two fixes made things worse in Percentile
project: percentile
status: done
added: 2026-08-06
effort: M
branch:
---

## Done means

Not writable yet — that is why this is `inbox` and not `ready`.

The last commit in the old location said finding F-1 was confirmed fixed and
that two of the fixes made things worse. Which two, and worse how, is not
recorded anywhere I can read.

**Resolved 2026-08-07.** The answer was in `docs/11-privacy-audit.md` all
along: (1) `meanSensitivity` moved from per-contributor to per-row, worsening
F-8; (2) count generalisation replaced exact counts but is deterministic and
invertible, creating F-16. One `ready` task now exists per regression:
`percentile-f8-one-value-per-workspace.md` and `percentile-f16-count-ladder.md`.

## Notes

Overnight work on this should be investigation, not code: read the red-team
audit docs in the repo, identify the two regressions, and write a `ready` task
per regression with a real finish line. Then stop.

This touches consent and privacy handling, so no unattended code changes here
until the diagnosis is on paper and Ollie has seen it.
