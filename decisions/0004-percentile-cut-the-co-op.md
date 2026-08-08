---
title: Cut Percentile's data co-op, ship the agent-readable analytics
status: proposed
date: 2026-08-08
---

## Context

Percentile was designed as two products in one. Layer one is analytics: one line
of SDK in the page, and the coding agent reads the metrics back through MCP.
Layer two is a benchmark data network: apps opt in, their numbers are pooled
into anonymous cohort statistics, those datasets are licensed, and contributing
apps take a share of the revenue.

Layer two is what all the hard work has been for, and by August 2026 it was
clear what it actually costs.

**The benchmark needs density nobody has.** The privacy audit measured it: the
published median only becomes meaningful at roughly 1,000 contributing
workspaces in a single comparable cohort, and the full five-point ladder needs
about 10,000. Below that the output is statistically indistinguishable from
random draws — a cohort of ten apps all reporting the same value and a cohort of
ten spread across the whole range publish the same numbers. So the benchmark
cannot be charged for until it is large, and it cannot get large on revenue it
cannot charge.

**The contributors cannot fund it either.** The intended contributors are people
shipping Lovable and Bolt apps. Most of those carry very little traffic, so
thousands of them still make a thin dataset, and the revenue share flowing back
would be small enough not to motivate anyone to join.

**The legal cost is front-loaded, fixed, and large.** `docs/10-legal-review.md`
lists seven blocking fixes and nine items that need paid outside counsel: an EU
anonymisation opinion, controller/processor characterisation, data-broker
analysis in Oregon and Vermont, a CalPrivacy registration narrative, a co-op
addendum, a licence template. California registration alone is about €6,000
before any advice. Every one of those costs exists *because* data is licensed to
a third party. None of it is needed to run layer one.

**Privacy and product pull against each other.** The stronger the guarantee, the
less the published numbers say. That is a real trade-off rather than a bug, and
the audit's own recommendation is to publish one honest number instead of five
meaningless ones.

None of this is a failure of the engineering. The release gate is in good shape
and the red-team audit behind it is unusually rigorous. The problem is that
layer two is the part that only pays off at a scale a solo first-year student
cannot reach, while carrying all of the cost from day one.

## Decision

**Cut the data co-op and the benchmark licensing from the product Percentile is
trying to ship. Keep the analytics and the MCP integration, and sell that.**

Concretely:

- The product becomes: drop in one line, and your coding agent can read your
  app's own metrics. Value to a single developer on day one, with no cohort, no
  pooling and no third party.
- No data is licensed to anyone. That removes the EU anonymisation opinion, the
  data-broker registrations, the licence template and the co-op addendum — the
  entire counsel bill — from the critical path.
- **No lawyer is hired for the co-op.** The spend only makes sense immediately
  before licensing data, which is years and thousands of contributors away.
- The privacy work already done is kept, not deleted. The release gate, the
  consent ledger and the adversarial suite stay in the repo behind the co-op
  path, dormant.
- Benchmarks return only if the analytics product reaches enough customers to
  make a cohort meaningful. At that point the math is already built and the
  decision gets revisited with real numbers instead of projections.

Two fixes stay urgent regardless, because they are ordinary consent bugs in the
analytics layer and not co-op concerns: the SDK writes a persistent identifier
before consent exists, and jurisdiction is taken from the browser's timezone.
See `tasks/percentile-b3-b4-sdk-blockers.md`.

## Consequences

Easy: shipping something usable to one customer instead of ten thousand.
Charging a small monthly fee without a data licence. Skipping the counsel bill
entirely. Competing on the genuinely novel part — an agent that reads your
metrics — rather than on percentile statistics, which is the crowded end of the
market. Amplitude and Mixpanel both grew this way round: single-app analytics
first, benchmarks much later.

Hard: the revenue-share pitch goes away, and with it the story that made
Percentile distinctive to investors. The benchmark network was the ambitious
idea; what remains is a smaller, more ordinary product in a market with
well-funded incumbents, differentiated mainly by the MCP angle and by being
consent-first.

Also: per decision 0001, Percentile was the project whose revenue model would
justify building a real app for the Hangar. That justification weakens — the
smaller product can still earn, but less, and later.

Reversible: nothing is deleted, only deferred. If the analytics product finds
customers, the co-op is switched back on with the privacy engineering already
finished and paid for in effort rather than euros.
