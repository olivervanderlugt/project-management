---
title: Percentile
description: Consent-first analytics for apps built by AI — one line of SDK, metrics read back through MCP, and a benchmark network that pays contributing apps a share
status: active
next: F-16 — stop publishing a deterministic function of an attacker-movable count (docs/11)
due:
started:
repo: olivervanderlugt/percentile
stack: TypeScript, Node 22, SDK + API + MCP server
tags: startup, analytics, mcp
---

## What this is

Consent-first analytics and a benchmark data network for apps built by AI. One line of SDK
in the page; the coding agent reads the metrics back through MCP; apps that opt in earn a
share of the revenue from the anonymous benchmark datasets they help create.

The pitch it makes: millions of people now ship apps whose code they cannot read, and have
no idea whether 14% activation is good or terrible. Percentile answers that by aggregating
across the network.

## Where it stands

The privacy audit (docs/11) is the working plan; its "recommended order of work" is the
backlog. Both Critical findings from the re-audit are now closed.

**F-2 is fixed** (2026-08-06): the release path used to license data on a
developer-set workspace toggle without ever reading the consent ledger, so a subject who
withdrew was still in the licensed dataset. Observations now carry a per-subject
`coop_licensing` count, k-anonymity counts only licensed subjects, and the gate refuses
rows without any. Tests 192 → 199, all green. One residual is recorded in docs/11: a
subject who declined licensing no longer counts toward thresholds but can still influence
the value their workspace contributes.

**F-8 is fixed** (2026-08-07, commit `ed5bcf1`): noise was calibrated per *row* while
privacy is declared per *workspace*, so a workspace stuffing 600 of 1599 rows took 600×
the declared epsilon and its value was readable from a single published mean. The gate now
collapses to one subject-weighted value per workspace before any noise mechanism runs and
asserts it; the attack reproductions are converted to `HOLDS-12` guards. The F-2 branch
was merged first, so everything is on `main`.

Source is split across `src/api`, `src/core`, `src/sdk` and `src/mcp`. Tests cover
privacy, consent durability, adversarial cases, special-category data, rollup and
pipeline. `test/adversarial.test.ts` is a red-team suite where `VULN-*` tests pass
*because an attack works* — read its header before touching it.

## Next after next

The audit's order of work after F-16: F-3/F-4 (budget keyed on attacker-supplied labels),
F-11 (a product decision — the five-point percentile ladder is unaffordable below ~10k
contributors; publishing fewer statistics is free and fixes it). Nothing should be
licensed to a third party before items 1–3 are done, and docs/10's seven legal blockers
stand before any data licence regardless.

## Open questions

- This is the one project with a revenue model in it. Per decision 0001, that makes it the
  project that would justify a real app.
