---
title: Versa
description: Song lyrics line-by-line beside a translation — AI drafts them, the community votes and improves, LRC timestamps sync them karaoke-style. No API keys needed.
status: parked
next:    Niets. Geparkeerd op 2026-08-20 — hosting kost geld en dat besluit is uitgesteld
due:
started:
repo: olivervanderlugt/versa
stack: Next.js, Drizzle, Postgres, Docker, Playwright, pnpm
tags: product, ai, lyrics
---

## What this is

Song lyrics read line-by-line next to a translation — original left, translation
right, optional romanization between. AI drafts the translations (natural and
literal, with notes); the community improves and votes on them. Synced
karaoke-style lyrics come from LRC timestamps.

Described in its README as a hobby project engineered to be launchable: legally
clean, public-domain seed content, a DMCA takedown flow, no scraping.

## Where it stands

Imported from the repo on 2026-08-06 by reading it, not guessing.

The most built-out project in the Hangar: Next.js app with Drizzle migrations,
`docker-compose.yml`, Playwright e2e tests, and its own `CLAUDE.md` and
`PROGRESS.md`. Last commit 2026-08-06, expanding the popular-song catalog to
1400+ metadata-only stubs.

`PROGRESS.md` in the repo is the detailed status; this file is only the index
entry. Read that one before starting work.

## Open questions

- No next action set here. `PROGRESS.md` probably already implies one — worth
  copying the real next step up into `next:`.
- This one has Docker and a database, so per decision 0002 it is the project
  where deploy infrastructure actually belongs.
