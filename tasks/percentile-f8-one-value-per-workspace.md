---
title: F-8 — collapse the release gate to one value per workspace
project: percentile
status: ready
added: 2026-08-07
effort: M
branch:
---

## Done means

`npm test` and `npm run typecheck` green, with: (1) the gate's step 4 operating
on exactly one value per workspace (subject-weighted mean, asserted), (2) the
four `VULN-4` tests converted to `HOLDS-*` guards proving the 98%
single-release mean classifier now scores ~chance, (3) docs/11's F-8 section
carrying a dated fixed-note, and (4) CLAUDE.md pointing at F-16 as next.

## Notes

Why: privacy is declared per *workspace* but noise is calibrated per *row* — a
workspace holding 600 of 1599 rows gets 600× the declared epsilon. Full write-up:
`docs/11-privacy-audit.md`, F-8. Prerequisite: merge branch
`claude/percentile-assessment-mwpi8t` into main first (carries the F-2 fix).

Steps:

1. `git checkout main`
2. `git merge claude/percentile-assessment-mwpi8t`
3. Open `src/core/privacy/release-gate.ts`
4. Find `const values = eligible.map(...)` (gate step 4)
5. Above it, group `eligible` rows by `workspaceId`
6. Replace each group with one number: subject-weighted mean of its values
7. Make `values` = that list (one entry per workspace)
8. Add one assertion: after the collapse, rows === distinct workspaces
9. `npm test`
10. The four `VULN-4` tests now fail → rename to `HOLDS-*`, flip assertions
    (attack must *not* work); keep `HOLDS-10` as the control
11. `npm test` again — all green
12. `npm run typecheck`
13. Mark F-8 fixed in `docs/11-privacy-audit.md` (dated note, like F-2's)
14. Change CLAUDE.md's "next thing to build" to F-16
15. Commit + push
16. In project-management: set percentile.md `next:` to F-16
17. `python3 dashboard/build.py`
18. Commit + push this repo

Steps 5–7 are the entire fix; the rest is ceremony. Privacy-critical code —
per the parent task's rule, not for an unattended overnight run unless Ollie
has approved this plan (he has seen it, 2026-08-07 session).
