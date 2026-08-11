---
title: Crewline M2: zelf inschrijven op shifts, race-vast op headcount
project: crew-management-system
status: inbox
added: 2026-08-11
effort: M
branch:
---

## Done means

A crew member sees open shifts matching their skills and availability, applies, and a planner
confirms — or the shift auto-confirms if configured for it. The part that decides whether this
is done:

- Headcount is enforced at the **database** level, by a constraint or a row lock. Not an
  app-level "count, then insert".
- A test fires 50 concurrent signup requests at a shift with 3 open slots and asserts exactly
  3 succeed and 47 get a clean "shift full" response. That test passes **before** any UI exists.
- zzp constraints hold: signing up is a genuine opt-in action, nothing is auto-assigned, no
  reliability or ranking score is shown anywhere, and a confirmed assignment has a
  "nominate a substitute" action.
- Tests green.

## Notes

Blocked by `crewline-startgate`, `crewline-foundation`, `crewline-m1-domain-model`.

This is the concurrency-critical milestone. If the 50-vs-3 test does not pass, the task is not
done regardless of how good the UI looks — say so and set the task `blocked` rather than
shipping a race.

The zzp rules are legal constraints (schijnzelfstandigheid / Wet DBA), not product preferences.
Do not "improve" them away.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md.

Build the crew-facing signup flow: a crew member sees open shifts matching their skills and
availability, applies, and a planner confirms (or auto-confirm if the shift is configured for it).

The critical requirement: a Shift has a headcount. If 50 crew tap "apply" for the last slot at
the same moment, exactly the right number must succeed. Enforce this with a database-level
constraint or row lock — NOT an app-level "count then insert". 

Write a test that fires 50 concurrent signup requests at a shift with 3 open slots and asserts
exactly 3 succeed and 47 get a clean "shift full" response. I want to see that test pass before
you build any UI.

For zzp crew members: signing up must be a genuine opt-in action. Never auto-assign. Never show
a reliability score. Include a "nominate a substitute" action on a confirmed assignment.
````
