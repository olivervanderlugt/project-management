---
title: Crewline M3: notificaties naar 300 man zonder storm
project: crew-management-system
status: inbox
added: 2026-08-11
effort: M
branch:
---

## Done means

Five notification events work end to end: shift published, shift confirmed, call-time
reminder (T-24h and T-2h), shift changed, shift cancelled. And:

- Fan-out runs entirely through a Trigger.dev job with batching and rate limiting. There is
  no synchronous loop over recipients inside a request handler anywhere in the diff.
- One channel interface with adapters for web push, email (Resend) and SMS. Swapping a
  provider is a one-file change. Default is push, falling back to email. SMS fires only for
  a `priority: urgent` flag, because it costs real money.
- Every send is recorded in a `notifications` table with a status, so "they said they never
  got it" is answerable from the data.
- A test publishes a shift to 300 crew members and asserts the job completes, batches
  correctly, and creates 300 notification records without hammering the provider.
- Tests green.

## Notes

Blocked by `crewline-startgate`, `crewline-foundation`, `crewline-m1-domain-model`,
`crewline-m2-signup-concurrency`.

Background jobs run outside the request's RLS context — rule 3 in `CLAUDE.md`. This milestone
is exactly where that bites: the job must carry `tenant_id` explicitly and use scoped queries.
Run the hostile-review prompt from `reference/crewline-kickoff-pack.md` over the diff.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md.

Build the notification layer: shift published, shift confirmed, call-time reminder (T-24h and
T-2h), shift changed, shift cancelled.

Requirements:
- Everything fans out through a Trigger.dev job with batching and rate limiting. Never a
  synchronous loop inside a request handler.
- Channel abstraction: one interface, adapters for push (web push), email (Resend) and SMS.
  Swapping a provider must be a one-file change. Default to push, fall back to email.
  SMS only for a `priority: urgent` flag — it costs real money.
- Every send is recorded in a notifications table with status, so I can debug "they said they
  never got it".
- Test: publish a shift to 300 crew members and assert the job completes, batches correctly,
  and creates 300 notification records without hammering the provider.
````

Sending real SMS or email costs money — overnight rule 6. Adapters get tested against fakes;
nothing goes out to a live provider from a night run.
