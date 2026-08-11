---
title: Crewline M7: hardening voor het eerste echte festival
project: crew-management-system
status: inbox
added: 2026-08-11
effort: L
branch:
---

## Done means

No new features. Six things are true before the first real event:

1. A test iterates **every** API route and asserts 401 without auth and 403-or-empty for a
   cross-tenant request — and it picks up newly added routes automatically, without anyone
   remembering to add them.
2. Load test run against staging: 300 concurrent crew opening their shift list, plus the
   50-concurrent-signup test from M2. The numbers are written down.
3. Backups verified by actually restoring the staging DB from a backup, with the runbook in
   `/docs/RUNBOOK.md`.
4. Sentry wired so a break at 02:00 on a build day reaches Ollie's phone.
5. An audit listing every place personal data is stored with its retention period, plus the
   implemented anonymisation job — 7 years for wage/hours records, 5 years for ID copies.
6. A one-page `/docs/GO-LIVE.md`: what to check that morning, what to do when X breaks, and
   how to fall back to Clevergig mid-event if it all goes wrong.

## Notes

Blocked by `crewline-startgate` through `crewline-m6-invoices-payout`.

**Open before this goes `ready`:** which festival, which date. The prompt has a literal `[DATE]`
placeholder and the whole milestone is scoped by it.

Parts of this touch things a night run must not: Sentry alerting and a staging restore involve
credentials and paid infrastructure (overnight rule 6). Realistic split when promoting — items
1 and 5 are buildable overnight, items 2, 3, 4 and 6 need Ollie at the keyboard. Consider
splitting this into two tasks at that point rather than letting the night run half-do it.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md.

We go live at a real festival in [DATE]. Harden the system. Do not add features.

1. Write a test that iterates EVERY API route and asserts: 401 without auth, and 403-or-empty
   for a cross-tenant request. This must be automatic for newly added routes.
2. Load test: 300 concurrent crew members opening their shift list, and the 50-concurrent-signup
   test from M2, run against staging. Report the numbers.
3. Verify backups: actually restore the staging DB from a backup and confirm it works. Write
   the runbook in /docs/RUNBOOK.md.
4. Wire Sentry properly — I want an alert on my phone when something breaks at 2am on a build day.
5. Audit: list every place personal data is stored, with its retention period, and implement the
   anonymisation job (7 years for wage/hours, 5 years for ID copies).
6. Give me a one-page /docs/GO-LIVE.md: what to check the morning of, what to do if X breaks,
   and how to fall back to Clevergig mid-event if it all goes wrong.
````
