---
title: Quizzly
status: active
next: Pick a host (Fly/Railway/VPS), deploy it, and play one real game over phones
due:
started: 2026-07-27
repo: olivervanderlugt/quizzly
preview:
stack: Next.js 15, Socket.IO, Prisma, PostgreSQL, Docker
tags: product, realtime
---

## What this is

A live quiz platform: hosts build quizzes, players join from their phones with
a PIN, everyone plays on a shared screen. Ten question types, deep theming,
optional AI question drafting, and blind group quizzes where contributors
cannot see each other's questions until the game reaches them. Self-hosted,
one Docker container, MIT licensed.

## Where it stands

Not an empty repo — that was true on the morning of 2026-08-06 and stale by
the evening. The app was built inside the shared `claude` repo starting
2026-07-27 and extracted into its own repository on 2026-08-06, history
intact: seven commits on `main`, ending with a fresh-machine Docker fix and a
written-down verdict on three unreachable npm advisories.

CI's first run on the extracted repo died in the same GitHub incident that
killed the Hangar's Pages deploys (`Failed to resolve action download info`) —
the code was never even checked out. A rerun was kicked off the same evening
and was still sitting `queued` behind GitHub's backlog when this was written;
as an independent check, the exact trio CI runs (`npm run typecheck && npm
test && npm run build`) was run locally on a fresh `npm ci` of `main` and came
back green, 53 tests passing. The code is verified; the Actions tab just
doesn't show it yet.

Never deployed, never played with real people. That is the gap between "the
code is done" and "this is a thing", and it is what `next` points at. The
README and docs still describe the pre-extraction layout (a `percentile/`
subdirectory that no longer exists); captured as the `ready` task
`quizzly-extractie-opruimen`.

The repo's own pre-public list, in its stated priority order: password reset
flow (needs an email provider), automatic nickname filter, and the
`[BRACKETED]` placeholders in the privacy/terms pages. None of it blocks a
private game with friends. Full gap list: `SECURITY.md`, *Known limitations*.

## Open questions

- Where does it live? It needs a held-open socket connection and a Postgres,
  so serverless is out — Fly, Railway or a VPS, and each costs a little money.
  `docs/DEPLOYMENT.md` in the repo compares them.
- Switch on AI drafting? Everything works without it; one `ANTHROPIC_API_KEY`
  in the env turns it on.
- `docs/LEGAL.md` flags a real patent-litigation risk in this product category
  — read it before anything commercial, or before opening it to strangers.
