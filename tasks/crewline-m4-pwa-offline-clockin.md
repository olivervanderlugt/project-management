---
title: Crewline M4: PWA met offline in- en uitklokken
project: crew-management-system
status: inbox
added: 2026-08-11
effort: L
branch:
---

## Done means

The crew routes in `/apps/web` are an installable PWA and clock-in/clock-out works:

- Manifest, service worker, install prompt and a web push subscription flow all exist. The PR
  contains a plain-English description of exactly what a crew member on an iPhone has to do to
  get push notifications working — Ollie needs it for onboarding instructions.
- **Only** the clock-in/out screen works offline. Nothing else is cached for offline use.
  Actions queue in IndexedDB with a client-generated UUID and a local timestamp, and flush on
  next foreground.
- Sync conflicts (the server already has a clock-in for this assignment) are flagged for a
  human, never silently overwritten, and there is a planner-side conflict resolution screen.
- A test simulates an offline clock-in, comes back online, and asserts the record syncs once
  and only once even when the flush runs twice.
- Tests green.

## Notes

Blocked by `crewline-startgate` through `crewline-m3-notifications`.

Timestamps: the local timestamp from the device is data, not truth. Store both what the device
claimed and when the server received it, both `timestamptz` — the whole point of the conflict
screen is that a human decides which one counts.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md.

Turn /apps/web's crew routes into an installable PWA and build clock-in/clock-out.

Requirements:
- Manifest, service worker, install prompt, web push subscription flow. Explain to me in plain
  English what a crew member on an iPhone has to do to get push notifications working, because
  I need to write onboarding instructions for them.
- Offline: ONLY the clock-in/out screen works offline. Nothing else. Queue actions in IndexedDB
  with a client-generated UUID and local timestamp, flush on next foreground.
- Sync conflicts (server already has a clock-in for this assignment) are flagged for a human
  to resolve — never silently overwritten. Build the planner-side conflict resolution screen.
- Test: simulate offline clock-in, come back online, assert the record syncs once and only once
  even if the flush runs twice.
````
