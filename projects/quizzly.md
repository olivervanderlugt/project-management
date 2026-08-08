---
title: Quizzly
description: A live quiz platform: ten question types, phones as buzzers, and blind group quizzes where nobody sees each other's questions until they hit the screen.
status: active
next: Merge PR #1, then follow docs/LAUNCH-CHECKLIST.md in the repo
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

**CI is green on `main`.** The first run died in the 2026-08-06 GitHub
incident and its rerun never left GitHub's queue, but the merge push on
2026-08-07 triggered a fresh run against `04d76a7` — the full
typecheck/test/build trio passed in 66 seconds, on the code that includes all
the new features. The stuck rerun of the superseded commit refuses to cancel
(GitHub 409) and can be ignored; it belongs to a commit that no longer heads
the branch.

2026-08-07: two features Ollie asked for landed on branch
`claude/quizzly-assessment-hli9uv` (commit `9af5d78`, trio green locally,
no migration needed): **public quizzes** — a Sharing toggle in the editor, a
public `/discover` page, host-someone-else's-quiz and save-a-copy, with
public restricted to solo quizzes at every layer so the blind group-quiz
promise stays intact — and **editor autosave** for questions, theme and game
rules, with a debounce, a status line, and a fix for a latent bug where
added or reordered questions didn't show up without a reload. Review and
merge it into `main`; that's the first half of `next`.

2026-08-07, later: **merged** — `main` fast-forwarded to `04d76a7`. And the app
had its first real end-to-end play: booted from `main` against a live
Postgres, seeded, and driven through a real browser — sign-in, Discover,
autosave, sharing toggle, hosting, a nickname (`k4nker99`) blocked on join, a
player joining from a phone-sized viewport and answering a live question over
sockets. Ten screenshots delivered to Ollie as an HTML report. Not deployed
yet by choice ("not hosting today").

Same branch, commit `04d76a7`: the nickname filter the schema had promised
since day one (normalises leetspeak, blocks slurs as substrings, short terms
only as whole names, English + Dutch, 9 tests), and the extraction cleanup —
README describes the standalone repo, migration guide deleted. Task
`quizzly-extractie-opruimen` is done. Of the repo's pre-public list only
password reset (needs an email provider) and the legal-page placeholders
(need real contact details) remain, and both need input only Ollie has.

2026-08-07, continued building on the same branch (`cff0040`, trio green,
72 tests): **quiz export/import** — any solo quiz downloads as a
`.quizzly.json` file and imports back through the same validation a
hand-written question faces (the landing page had promised export since day
one; it didn't exist), plus a **search box on Discover**. Merged the same day — `main` is at
`cff0040`; CI runs on the push.

2026-08-07, evening: **finalized for launch** — task `quizzly-finalisatie`,
**PR #1**, branch `claude/quizzly-finalization`, version 1.0.0. Password reset
(optional SMTP, degrades like AI), change-password, GDPR Art. 15 export, age
gate, `DATA_RETENTION_DAYS` sweep, deliberate robots.txt, the realtime
socket-e2e suite the docs had always claimed (72 unit + 8 integration tests,
CI runs them against a Postgres service and builds the Docker image),
`fly.toml` ready, SECURITY/LEGAL doc drift fixed, and a compose bug found and
fixed (Docker 29+ choked on the unquoted secret guards). What only Ollie can
do — hosting account, SMTP credentials, legal placeholders, domain, backups —
is one ordered list in `docs/LAUNCH-CHECKLIST.md`.

Never deployed, never played with real people. Merging PR #1 and walking the
launch checklist is all that remains between the code and a live site.

## Open questions

- Where does it live? It needs a held-open socket connection and a Postgres,
  so serverless is out — Fly, Railway or a VPS, and each costs a little money.
  `docs/DEPLOYMENT.md` in the repo compares them.
- Switch on AI drafting? Everything works without it; one `ANTHROPIC_API_KEY`
  in the env turns it on.
- `docs/LEGAL.md` flags a real patent-litigation risk in this product category
  — read it before anything commercial, or before opening it to strangers.
