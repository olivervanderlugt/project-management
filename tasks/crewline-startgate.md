---
title: Crewline: de poort open — Clevergig-factuur gezien, IP/contract geregeld
project: crew-management-system
status: inbox
added: 2026-08-11
effort: S
branch:
---

## Done means

§3 and §8 of the strategy brief are answered in writing, here in the Hangar:

- The actual Clevergig invoice has been seen — what the first customer pays today, per
  what unit, so there is a number to beat instead of a guess.
- IP and contract are sorted: who owns the code, what the first customer gets, what
  happens if they leave. Written down as a decision record in `decisions/`.

Until both are recorded, every other `crewline-*` task stays `inbox`. When they are,
flip this task to `done` and the rest to `ready` in the order listed in
`reference/crewline-kickoff-pack.md`.

## Notes

This is Ollie's call, not a build task — the overnight run cannot answer either question.
It sits in the queue because it is the single thing blocking eight other tasks, and a
blocker that is not written down gets forgotten.

The kickoff pack states the gate literally: "Do not start these until §3 and §8 of the
strategy brief are answered (Clevergig invoice seen, IP/contract sorted)."

Also open, and cheap to settle at the same time: the name. "Crewline" is explicitly a
placeholder — "Change it everywhere before you start." Renaming after the first commit is
work; renaming before it is a find-and-replace in one file.
