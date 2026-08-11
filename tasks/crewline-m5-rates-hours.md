---
title: Crewline M5: tariefmotor, toeslagen en urenakkoord
project: crew-management-system
status: inbox
added: 2026-08-11
effort: L
branch:
---

## Done means

The rate engine and the hours approval flow work:

- The rate engine lives entirely in `/packages/domain` as pure functions: it takes
  (shift, timesheet, ratecard, surcharge rules) and returns a breakdown of pay components.
  No framework imports. No money calculation anywhere else in the codebase.
- Surcharge rules are **data, not code**. A rule is: condition (time window / weekday / hours
  threshold) → multiplier or fixed amount → applies to the client rate, the crew rate, or both.
  Rates and rules are per tenant, optionally per client, and effective-dated.
- Handled: evening, night, weekend, public holiday, overtime past a threshold, standby.
  Overnight shifts split correctly across surcharge windows and across midnight.
- Approval flow: crew submits → planner approves / rejects / adjusts. Every adjustment writes
  an `ApprovalLog` row with before, after and who. Timesheets are never hard-deleted.
- A review screen shows the calculation to a human before anything is sent onward.
- The unit tests were written first and cover at minimum: a plain day shift, an overnight shift
  crossing midnight, a shift crossing a DST boundary, a Sunday shift, a public-holiday shift,
  and a shift with 4 hours of overtime. All green.

## Notes

Blocked by `crewline-startgate` through `crewline-m4-pwa-offline-clockin`.

Why the rules are data: since 1 Jan 2026 Dutch law requires pay equivalent to the **client's own**
employees, so there is no single national table to hardcode. Any percentage that ends up in a
`.ts` file as a literal is a bug.

Run the hostile-review prompt from `reference/crewline-kickoff-pack.md` over this diff — it is
the money milestone.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md — especially the compliance section.

Build the rate engine and the hours approval flow.

The rate engine lives entirely in /packages/domain as pure functions. It takes
(shift, timesheet, ratecard, surcharge rules) and returns a breakdown of pay components.

Requirements:
- Surcharge rules are DATA, not code. A rule is: condition (time window / weekday / hours
  threshold) → multiplier or fixed amount → applies to client rate, crew rate, or both.
  Rates and rules are per tenant and optionally per client, and are effective-dated.
  This is because Dutch law since 1 Jan 2026 requires pay equivalent to the CLIENT's own
  employees, so there is no single national table.
- Handle: evening, night, weekend, public holiday, overtime past a threshold, and standby.
- Overnight shifts split correctly across surcharge windows and across midnight.
- Approval flow: crew submits → planner approves/rejects/adjusts. Every adjustment writes an
  ApprovalLog row with before/after values and who did it. Timesheets are never hard-deleted.
- The output is a calculation a human reviews before anything is sent. Build the review screen.

Write the unit tests first, covering at minimum: a plain day shift, an overnight shift crossing
midnight, a shift crossing a DST boundary, a Sunday shift, a public-holiday shift, and a shift
with 4 hours of overtime. Show me those tests before implementing.
````
