---
title: Percentile
status: active
next: Fix F-8 — collapse the release gate to one value per workspace (docs/11, item 2 of the order of work)
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
backlog, and the two Critical findings from the re-audit were both still open on
2026-08-06.

**F-2 is now fixed** (2026-08-06): the release path used to license data on a
developer-set workspace toggle without ever reading the consent ledger, so a subject who
withdrew was still in the licensed dataset. Observations now carry a per-subject
`coop_licensing` count, k-anonymity counts only licensed subjects, and the gate refuses
rows without any. Tests 192 → 199, all green. One residual is recorded in docs/11: a
subject who declined licensing no longer counts toward thresholds but can still influence
the value their workspace contributes — closing that belongs with F-8.

The fix sits on branch `claude/percentile-assessment-mwpi8t`; `main` does not have it yet.
Merge it (the repo's own convention is to work directly on main) before building F-8 on
top.

Source is split across `src/api`, `src/core`, `src/sdk` and `src/mcp`. Tests cover
privacy, consent durability, adversarial cases, special-category data, rollup and
pipeline. `test/adversarial.test.ts` is a red-team suite where `VULN-*` tests pass
*because an attack works* — read its header before touching it.

## Next after next

The audit's order of work after F-8: F-16 (invertible count generalisation), F-3/F-4
(budget keyed on attacker-supplied labels), F-11 (a product decision — the five-point
percentile ladder is unaffordable below ~10k contributors; publishing fewer statistics is
free and fixes it). Nothing should be licensed to a third party before items 1–3 are done,
and docs/10's seven legal blockers stand before any data licence regardless.

## Open questions

- This is the one project with a revenue model in it. Per decision 0001, that makes it the
  project that would justify a real app.
