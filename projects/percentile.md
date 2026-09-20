---
title: Percentile
description: Consent-first analytics for apps built by AI — one line of SDK, metrics read back through MCP, and 30% of the benchmark-data revenue back to the apps that contribute.
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

**F-3 and F-4 are fixed** (2026-08-08): the ε budget used to be keyed on attacker-supplied
metadata and the coarsening ladder multiplied ε over nested populations. Both close with a
per-workspace epsilon ledger keyed on the contributing population plus a registry metric id.
**F-12 is fixed in code** (2026-08-08): jurisdiction is now resolved server-side from the
request IP and takes the stricter of hint and determination — still needs a real geo lookup
wired in before it's complete. Residuals `VULN-3r` and `VULN-11r` are recorded in the test
suite. (Corrected here 2026-08-30 — this file still said F-16 was the only work after F-2/F-8;
the repo's own `docs/11-privacy-audit.md` and `CLAUDE.md` show F-3/F-4/F-12 landed the same
day as F-16 was scoped. Verified directly against `docs/11-privacy-audit.md` lines 15–21 and
137–143 on `origin/main`, not just the task's own claim.)

Source is split across `src/api`, `src/core`, `src/sdk` and `src/mcp`. Tests cover
privacy, consent durability, adversarial cases, special-category data, rollup and
pipeline. `test/adversarial.test.ts` is a red-team suite where `VULN-*` tests pass
*because an attack works* — read its header before touching it.

## Next after next

F-16 (`next`, above) is built and adversarially checked but stuck: its PR
(`percentile#1`, branch `night/percentile-f16-count-ladder`) has had a real merge
conflict since 2026-08-07 — nine consecutive nightly re-checks (through 2026-08-29)
found it unchanged. It needs a manual rebase before anything else in this backlog can
build on top of it. After that: F-11 (a product decision — the five-point percentile
ladder is unaffordable below ~10k contributors; publishing fewer statistics is free and
fixes it) and F-12's geo-lookup wiring. Nothing should be licensed to a third party
before these are done, and docs/10's seven legal blockers stand before any data licence
regardless.

## Open questions

- This is the one project with a revenue model in it. Per decision 0001, that makes it the
  project that would justify a real app.
