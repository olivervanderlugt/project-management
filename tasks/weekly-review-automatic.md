---
title: Generate the weekly review from what actually changed
project: hangar
status: done
added: 2026-08-06
effort: M
branch: claude/night-weekly-review-automatic
---

## Done means

A script reads the commit history of every repo listed in a project's `repo:`
field since the last weekly file, and writes `planning/weekly/YYYY-Www.md` with
Wins filled in from real commits. Slips and Next week stay empty for Ollie.

Running it twice for the same week does not produce two files or duplicate
lines.

## Notes

`git log --since` per repo against the shallow clones is enough; no need for
full history. Repos with no commits that week are skipped rather than listed as
empty.

Never invent a win. If a week has no commits anywhere, the file says so.

**Gebouwd 2026-08-09 (nachtrun).** `scripts/weekly_review.py` +
`scripts/test_weekly_review.py` (23 tests), PR:
olivervanderlugt/project-management, branch `claude/night-weekly-review-automatic`.
`hangar-checker` deed de vijandige review tegen dit Done means en vond vijf
echte bugs (stale cache door fetch-zonder-log-op-remote-ref, lege repo
verward met onbereikbaar, onbereikbare repo's stilzwijgend weggelaten, eerste
run zonder eerdere week dumpte alle geschiedenis, een handgeschreven sectie
buiten Wins/Slipped/Next week werd overschreven) — allemaal gefixt met een
regressietest erbij, checker's bevindingen zaten niet in de eerste push.
Bewust niet gedraaid tegen het echte lopende weekbestand
(`planning/weekly/2026-W32.md`): vandaag valt nog in ISO-week 32, hetzelfde
bestand dat Ollie al met de hand schreef, en een eerste echte run zou zijn
Wins hebben overschreven met automatisch afgeleide regels. Geverifieerd met
een synthetische week in een tijdelijke map in plaats daarvan.
