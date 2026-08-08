---
title: F-3/F-4 — per-workspace epsilon ledger keyed on population, not label
project: percentile
status: ready
added: 2026-08-08
effort: M
branch:
---

## Done means

`npm test` and `npm run typecheck` green, with all four of:

1. The budget key in `src/core/privacy/release-gate.ts:128` derived from the
   *population* — `sha256(sorted distinct workspaceIds) + '::' + metricId` —
   instead of `cohortKeyString(cohort) + '::' + metric.name`.
2. A **per-workspace** epsilon ledger in `differential-privacy.ts` that charges
   every contributing workspace on every release including it, capped at 1.0 per
   workspace per period.
3. `MetricSpec` resolved from a fixed registry, so renaming a metric (or
   appending whitespace to its name) cannot mint a fresh budget.
4. The three `VULN-3` tests and the two `VULN-3b` tests converted to `HOLDS-*`
   guards, verified to go red against the pre-fix gate. `HOLDS-C0` must keep
   passing.

Plus: `narrowestReleasableCohort`'s selection made binding — at most one rung
released per (workspace, metric, period) — and docs/11 F-3 and F-4 each get a
dated fixed-note.

## Notes

Two findings, one fix: the audit says the per-workspace ledger closes F-4 as a
side effect, so do them together rather than as separate branches.

Why it matters beyond its own severity: F-3 is where the *other* attacks get
their queries. Measured today, 50 of 50 releases of one identical population
sail past a budget permitting 10, just by varying the `?period=` label; 50 of 50
again by appending whitespace to the metric name. F-8's averaging attack and
F-16's adaptive binary search both need many queries and both draw them here.
Fixing this does not remove either attack — it raises their cost by an order of
magnitude. It also restores the bound F-16b's accepted concession relies on.

Full write-up including the exact fix the auditor recommends:
`docs/11-privacy-audit.md`, F-3 and F-4. This is item 4 in the audit's
recommended order of work; items 1–3 (F-2, F-8, F-16) are done, though F-16 is
still sitting in PR #1 unmerged — merge that first so this branch does not
build on a fork of the gate.

`test/adversarial.test.ts` is a red-team suite where `VULN-*` tests pass
*because an attack works*. Read its header before touching it.
