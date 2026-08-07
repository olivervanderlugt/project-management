---
title: F-8 — collapse the release gate to one value per workspace
project: percentile
status: done
added: 2026-08-07
effort: M
branch: main
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

**Done 2026-08-07**, commit `ed5bcf1` on `olivervanderlugt/percentile` main,
with the F-2 branch merged first as planned. All four points of the finish line
crossed: 199 tests green, guards named `HOLDS-12a–d` and verified to go red
against the un-collapsed gate, `HOLDS-10` kept as the control. One
interpretation call, recorded in docs/11: "weight the resulting distribution by
subjectCount" is applied *inside* the collapse (a workspace's rows weighted by
their subjectCount), not across workspaces — cross-workspace weighting would
reintroduce the very sensitivity understatement F-8 is about. F-2's
value-influence residual is inherited, not closed. Next in the audit's queue:
F-16.
