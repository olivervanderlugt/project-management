---
title: F-11 — decide what the ladder publishes below 10k contributors
project: percentile
status: inbox
added: 2026-08-08
effort: S
branch:
---

## Done means

Not writable yet, and deliberately so: this is a product decision, not a bug.
The finish line depends on which option Ollie picks. Once he picks one, this
becomes a decision record in `decisions/` plus a `ready` build task.

## Notes

The five-point percentile ladder carries no information below roughly 10,000
contributing workspaces. This is measured, not suspected: at k=10 a cohort
spread across 0.0–0.9 and a cohort where every single app reports exactly 0.5
**publish the same ladder** — 0.164 / 0.493 / 0.834 versus 0.173 / 0.500 /
0.841, both statistically identical to the order statistics of five uniform
draws. `compare()` in `src/core/aggregate/benchmarks.ts` will read a confident
percentile rank off that and tell a developer they are in the 90th percentile of
a distribution that does not exist. That is the product's core claim failing
quietly, which is worse than failing loudly.

Mean absolute error of the published median against cohort size: 0.155 at 10
contributors, 0.145 at 100, 0.099 at 1,000, and 0.012 at 10,000. The crossover
is real and it sits an order of magnitude above where the go-to-market plan
assumes it does.

Three options, in cost order:

1. **Publish fewer statistics.** Spend the whole 0.1 budget on the median alone
   and it is usable from n ≈ 1000 today, with no other change (error 0.021 at
   n=1000 versus 0.117 now). A three-point p25/p50/p75 ladder at ε/3 sits
   between. **Free, immediate, and the auditor's recommendation.**
2. **Raise ε per query** to ~1.0 and cut releases per period from 10 to 1. Same
   total epsilon, far better utility, and it makes the "ten queries per cohort
   per period" promise honest rather than nominal.
3. **Raise the minimum cohort size to ~10,000 contributing workspaces.**
   Correct, and by far the most expensive — `docs/08-risks.md` already ranks
   cohort density as the risk that decides whether the company exists.

Options 1 and 2 are the same lever from two sides: stop spreading a small budget
over six statistics nobody acts on. The honest reading is that the marketing
claim of a five-point ladder was never affordable, and option 1 costs nothing
but the claim.

Full quantification: `docs/11-privacy-audit.md`, F-11. Guarded by `VULN-9`
(3 vuln + 2 holds, including the n=10,000 crossover), so both facts are in the
test suite rather than opinions in a document.
