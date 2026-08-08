---
title: B3/B4 — the two legal blockers the privacy audit never looked at
project: percentile
status: ready
added: 2026-08-08
effort: M
branch:
---

## Done means

`npm test` and `npm run typecheck` green, with both blockers closed and a
regression test per blocker:

**B3 — nothing persisted or transmitted before consent is `granted`.**
`src/sdk/browser.ts:95-108` writes a persistent device id to `localStorage` in
the constructor, gated only on `optedOut()`. That is an opt-*out* check (GPC/DNT);
B3 requires opt-*in*. Queue events in memory only, mint no persistent identifier
and send nothing until a `granted` state exists. Test: a fresh SDK instance with
no consent state writes zero `localStorage` keys and issues zero requests.

**B4 — jurisdiction resolved server-side.** `detectJurisdiction()`
(`src/sdk/browser.ts:43-54`) reads the browser's timezone, and
`src/core/ingest.ts:64` takes `raw.context?.jurisdiction` at face value. An EU
subject who sets their clock to `America/New_York` gets the US posture. Resolve
from IP server-side; where the client hint and the server determination differ,
apply the stricter of the two. Test: an event carrying `jurisdiction: 'US'` from
an EU-resolved address is handled as EU.

Then update `docs/10-legal-review.md` with a dated note against B3 and B4, and
correct the blocker count wherever it is quoted.

## Notes

**Why this task exists.** The privacy audit in `docs/11` is titled "adversarial
review of the release gate", and that is exactly what it reviews. Its
recommended order of work — F-2, F-8, F-16, F-3/F-4, F-11, F-6 — never reaches
the SDK or the ingest path. So working the audit's list to completion does not
clear the licence blockers, and it is easy to believe otherwise because the two
documents overlap in the middle and diverge at the edges.

Blocker status read from the code on 2026-08-08, not from the documents:

| # | What it wants | State |
|---|---|---|
| B1 | Gate on the subject's `coop_licensing`, not workspace enrolment | fixed (F-2, 6 Aug) — value-influence residual open |
| B2 | Epoch-independent withdrawal | fixed — `deriveConsentAnchor` keys consent on a stable anchor |
| B3 | Nothing written or sent before `granted` | **open** — this task |
| B4 | Server-side jurisdiction | **open** — this task |
| B5 | Exponential mechanism, or drop the ladder | fixed |
| B6 | Persist ε budget; key per cohort per period; reject caller `period` | **partly** — keying is F-3/F-4, durability is F-15, both open |
| B7 | CCPA public no-reidentification commitment + licence terms | open — not code, needs counsel |

So B6 is not closed by the F-3/F-4 task alone: that task fixes the *key*, and
B6 also demands the budget survive a process restart. Pair it with F-15 or B6
stays open with a green test suite, which is the worst of both.

Full text: `docs/10-legal-review.md`, "Recommended changes". Note that document's
own caveat — its author could not open a single primary source, so quoted
statutory language needs re-verification before anyone relies on it.
