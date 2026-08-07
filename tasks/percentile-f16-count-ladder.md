---
title: F-16 — stop publishing a deterministic function of an attacker-movable count
project: percentile
status: doing
added: 2026-08-07
effort: S
branch: night/percentile-f16-count-ladder
---

## Done means

`npm test` and `npm run typecheck` green, with the two `VULN-6` tests (12–14
query binary-search recovers a victim's exact subject count) converted to
`HOLDS-*` guards, and released counts published either as k-threshold bands
("≥10" / "≥500", the audit's preferred option) or as `noisyCount(n, 0.5)` on a
dedicated budget line — noised first, snapped second. Docs/11 F-16 gets a dated
fixed-note.

## Notes

This is the second of the two "fixes that made things worse": count
generalisation killed naive differencing but is deterministic, so an attacker
who contributes to the cohort binary-searches a ladder boundary. Full write-up
and both fix options: `docs/11-privacy-audit.md`, F-16. Do after F-8 — the
audit's order of work is F-8 then F-16.
