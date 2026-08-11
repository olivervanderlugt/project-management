---
title: Crewline M1: kernmodel — Project, Job, Shift, ShiftAssignment, crew-profielen
project: crew-management-system
status: inbox
added: 2026-08-11
effort: M
branch:
---

## Done means

The core scheduling domain exists: Client, Project, Job (phase build/show/strike), Role,
Shift, CrewProfile, Skill, Certificate, Document, Availability, ShiftAssignment — every
table with a non-null `tenant_id` and an RLS policy in the same PR. On top of that:

- `Shift.call_time`, `start_at` and `end_at` are all `timestamptz`. An overnight shift
  (22:00 → 04:00) is representable and survives both the March and October DST transitions,
  proven by unit tests using the real 2027 changeover dates as fixtures.
- `ShiftAssignment.status` implements the exact lifecycle from `CLAUDE.md`
  (`invited → applied → confirmed → clocked_in → clocked_out → approved`, terminals
  `declined`, `no_show`, `replaced`). The state machine lives in `/packages/domain`, illegal
  transitions are rejected with a clear error, and **every** transition — legal and illegal —
  has a test.
- `Certificate` has an `expiry_date`, and a Trigger.dev job flags certificates expiring
  within 30 days.
- A Shift can reference a crew_chief ShiftAssignment (self-referencing), at most one per shift,
  enforced by the database.
- The schema was written out as a table/column list in the PR description before the code.
- Tests green.

## Notes

Blocked by `crewline-startgate` and `crewline-foundation`.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md and /docs/DECISIONS.md.

Implement the core scheduling domain: Client, Project, Job (phase: build/show/strike),
Role, Shift, CrewProfile, Skill, Certificate, Document, Availability, ShiftAssignment.

Requirements:
- Shift.call_time, start_at and end_at are all timestamptz. An overnight shift (22:00 → 04:00)
  must be representable and must survive the March and October DST transitions. Write unit
  tests using the real 2027 DST changeover dates as fixtures.
- ShiftAssignment.status is the exact lifecycle in CLAUDE.md. Illegal transitions must be
  rejected at the domain layer with a clear error — put this state machine in /packages/domain
  and test every transition, legal and illegal.
- Certificate has an expiry_date. Add a Trigger.dev job that flags certificates expiring in
  the next 30 days.
- A Shift can reference a crew_chief ShiftAssignment (self-referencing). One chief per shift, max.

Before writing code: show me the schema as a list of tables and columns and wait for my OK.
````

"Wait for my OK" is an interactive instruction. Overnight: put the schema list at the top of
the PR description as the first commit, then build against it.
