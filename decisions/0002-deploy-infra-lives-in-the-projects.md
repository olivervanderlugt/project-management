---
title: Deploy infrastructure lives in the project repos, not in the Hangar
status: proposed
date: 2026-08-06
---

## Context

The question was whether to wire the Hangar up to Docker, Vercel, Supabase and
Stripe so it is "ready to ship stuff when done".

The Hangar is a planning layer. It holds markdown *about* projects; it does not
hold their code, and the code lives in four other repos. Connecting a deploy
stack to it would mean the HQ carries containers, env vars, database schemas and
payment keys for software that is not in it.

There is also a cost asymmetry. Vercel and Supabase both want a project to point
at, Docker wants something to containerise, and Stripe wants a live product with
a price. Set up in advance, all four are configuration you maintain and rotate
keys for before anything ships. Set up when a project actually needs them, each
is well under an hour.

## Decision

Deploy infrastructure belongs to the individual project repos. `percentile`
gets its own Stripe and its own database when it charges someone; `learn` gets
its own Vercel project when it goes live.

The Hangar's job is to be the index: `repo` and `stack` on each project record
what a thing runs on and where its code is, so future-you knows where to look
without opening four repos to find out.

The one exception is hosting the Hangar's own dashboard, which is already done
through GitHub Pages — free, no account to wire up, no keys.

## Consequences

Easy: the Hangar keeps working with zero credentials in it, nothing to rotate,
nothing to pay for, and no blast radius if it is ever made public. Each project
picks the stack that suits it instead of inheriting one chosen months early.

Hard: no single "deploy everything" button, and no shared infrastructure between
projects. If three projects eventually want the same Supabase instance, that
gets set up then, and gets its own decision record.

Reversing this is cheap, which is the main argument for waiting: nothing here
forecloses adding any of it later.
