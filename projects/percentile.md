---
title: Percentile
status: active
next: Merge PR #1, then fix the two consent bugs in the SDK (tasks/percentile-b3-b4-sdk-blockers.md)
due:
started:
repo: olivervanderlugt/percentile
stack: TypeScript, Node 22, SDK + API + MCP server
tags: startup, analytics, mcp
---

## What this is

Consent-first analytics for apps built by AI. One line of SDK in the page, and the coding
agent reads the metrics back through MCP — so the developer who cannot read their own app's
code can still ask their agent how the app is doing, and have it act on the answer.

The pitch: millions of people now ship apps they did not write and cannot audit, and have no
idea whether 14% activation is good or terrible.

**As of decision 0004 that pitch is being narrowed.** Percentile was designed as two
products — the analytics above, and a benchmark data network where opted-in apps are pooled
into anonymous cohort statistics, those datasets are licensed, and contributors take a
revenue share. The co-op is the half that answers "is 14% good", and it is also the half
that carries every legal cost and only works at a scale that is years away. Decision 0004
proposes cutting it and selling the analytics on its own. **That decision is `proposed`, not
accepted** — until Ollie says otherwise, the co-op code stays where it is.

## Why the co-op is being cut

Three measured reasons, all from the project's own documents:

**It needs density nobody has.** The privacy audit measured the crossover: the published
median only means anything at roughly 1,000 contributing workspaces in one comparable
cohort, and the five-point ladder needs about 10,000. Below that, a cohort of ten apps all
reporting the same number and a cohort of ten spread across the whole range publish the same
statistics. So it cannot be charged for until it is large, and it cannot get large on revenue
it cannot charge.

**The legal bill comes first and does not shrink.** `docs/10-legal-review.md` lists seven
blocking fixes and nine items needing paid outside counsel — an EU anonymisation opinion,
data-broker analysis in Oregon and Vermont, a CalPrivacy registration narrative, a licence
template. California registration alone is about €6,000 before any advice. Every one of those
costs exists because data is licensed to a third party; none is needed to run the analytics.

**Privacy and usefulness pull against each other.** The stronger the guarantee, the less the
published numbers say. The audit's own recommendation is to publish one honest number rather
than five meaningless ones.

None of this is a failure of the engineering, which is in good shape — see below.

## Where the code stands

**PR #1 is built and waiting on you** (`night/percentile-f16-count-ladder`, opened
2026-08-07). Published counts became k-threshold bands, and the refusal message stopped
leaking the exact shortfall — a one-query inversion that reached the API, MCP and rollup
wire. Tests 200/200, typecheck clean. The checker refuted the first pass, so one residual is
labelled honestly rather than claimed fixed: an attacker who can trigger refusals still
bisects the public 34% dominance cap to recover a subject count in 14–15 queries. That is a
different finding's root cause and is in the suite as an explicitly KNOWN-OPEN test.

Two Critical findings were closed before it. **Consent is now actually consulted on the
release path** (2026-08-06): it used to license data on a developer-set workspace toggle
without ever reading the consent ledger, so someone who withdrew stayed in the dataset. **The
privacy unit was fixed** (2026-08-07, `ed5bcf1`): noise was calibrated per row while privacy
is declared per workspace, so a workspace holding 600 of 1,599 rows took 600× the declared
budget and its value was readable from a single published mean.

Source is split across `src/api`, `src/core`, `src/sdk` and `src/mcp`. Tests cover privacy,
consent durability, adversarial cases, special-category data, rollup and pipeline.
`test/adversarial.test.ts` is a red-team suite where `VULN-*` tests pass *because an attack
works* — read its header before touching it.

## What to do next

**Urgent whatever happens to the co-op** — these are ordinary consent bugs in the analytics
layer, not benchmark concerns:

- `tasks/percentile-b3-b4-sdk-blockers.md` (`ready`) — the SDK writes a persistent
  `localStorage` device id in its constructor, gated on opt-*out* rather than on granted
  consent, and jurisdiction is read from the browser's timezone and trusted as given. Anyone
  can set their clock to `America/New_York` and be handled under US rules instead of EU ones.
  Found 2026-08-08 by reading the code against docs/10; the audit never reaches these files
  because it is scoped to the release gate.

**Only matters if the co-op survives:**

- `tasks/percentile-f3-f4-budget-ledger.md` (`ready`) — the query budget is keyed on
  attacker-supplied labels, so 50 of 50 releases of one population pass a budget permitting
  10, just by varying `?period=`. This is where the other attacks get their queries cheaply.
- `tasks/percentile-f11-ladder-decision.md` (`inbox`) — publish one number or five. Largely
  answered by decision 0004, but keep it until that decision is accepted.

A paste-ready prompt covering all three fixes: `reference/percentile-fix-prompt.md`.

Legal blocker score, read from the code rather than the documents: three fixed (subject-level
consent, epoch-independent withdrawal, the exponential mechanism), three open (the two SDK
bugs above, plus the public no-reidentification commitment, which is website and contract
work). One is half-done — the budget needs both a population-derived key and durability
across restarts, and has neither.

## Open questions

- Decision 0004 is `proposed`. Accepting it means no lawyer is hired, and the revenue-share
  story — the thing that made this distinctive — goes away.
- Per decision 0001, Percentile was the project whose revenue model would justify building a
  real app for the Hangar. The narrowed product can still earn, but less, and later. That
  justification weakens rather than disappears.
