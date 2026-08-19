---
title: Crew management system
description: Planningssysteem voor crew op events en festivals — MVP staat en is groen getest, maar heeft nog nooit tegen een echte database gedraaid.
status: active
next: Koppel het aan een echt Supabase-project en zet het op Vercel — pas dan is de MVP te bekijken
due:
started: 2026-08-19
repo: olivervanderlugt/crew-management-system
preview: https://olivervanderlugt.github.io/crew-management-system/
stack: Next.js 15, Supabase, TypeScript, Turborepo, Tailwind, PWA
tags: product, planning
---

## What this is

A self-hostable planning system for organisations that staff crew on events and
festivals. Admin side: crew records with a document archive, monthly availability
grids (B/M/X), events, a weighted matching engine, assignments, hours, costing and
a payroll CSV export. Crew side: a magic-link self-service portal with their own
availability, assignments and open shifts.

Turborepo monorepo — `packages/core` holds framework-agnostic logic, `apps/web` is
the Next.js app that actually runs, `apps/mobile` is an Expo scaffold. Backend is
Supabase: Postgres, Auth, RLS, Storage. No separate API server. UI is Dutch, docs
are English.

The repo is deliberately generic: no organisation, client or person in it.

> **The `preview` URL is a landing page, not the app.** GitHub Pages serves static
> files only; this app is server-rendered and cannot run there. A real clickable
> preview needs Vercel plus a Supabase project — that is what `next` points at.

## Where it stands

Not an empty repo — that was true on 2026-08-06 and stale by 2026-08-19, when the
whole MVP was pushed from the desktop. Eight commits, then a working session.

**2026-08-19 — first-session checklist run end to end, all green.** `pnpm install`
clean, typecheck 0 errors, 64/64 unit tests, web build 38 routes. The Playwright
smoke suite ran on a real machine for the first time: 3/3, no fixes needed. An
independent secret scan (`gitleaks` over the full history) came back clean — the
only hits were Next.js build artefacts under a gitignored `.next/`.

**A four-track analysis produced `TODO.md`** in the repo: a goal-ordered backlog
where every item cites a `file:line`. Three findings matter more than the rest.

- **Skill matching has never run.** The engine awards full skill points when the
  required-skills list is empty, and the only caller hardcodes it to empty. Ranking
  has never once considered skills.
- **Multi-day events only check day one.** The matcher reads `start_datetime` and
  never `end_datetime`, so crew marked unavailable on days 2–3 of a festival still
  rank as available.
- **Costing and payroll bill different hours.** The margin card uses raw worked
  hours; the CSV export skips unapproved rows. They do not reconcile.

None of these crash. They quietly give wrong answers, which is why they are Goal 1,
and why "it builds and the tests pass" was not the same as "it works".

**CI had a silent hang, found and fixed.** Opening the first PR exposed it live:
the e2e job ran 40+ minutes stuck on `playwright install --with-deps`, which shells
out to apt-get, with no `timeout-minutes` to stop it. It now runs in 1m31s, with a
15-minute ceiling and a concurrency group on both jobs.

**The repo shipped with no crew data at all** — the seed reads gitignored CSVs that
do not exist, so the app came up empty. There is now a `pnpm db:seed-demo` that
generates 100 fictional crew with skills and 90 days of availability, confined to a
reserved `CREW-9xxx` code range so it can never touch real records. Emails use the
`.invalid` TLD; IBANs are `NL00DEMO…` with check digits invalid by construction.

**A landing page is live**, served by GitHub Pages from `main` at `/docs`. Pages had
been enabled on the repo for a while but had never built, because there was nothing
at the configured path to serve.

**It has never run against a real database.** `.env.local` holds placeholders, which
is enough to build and typecheck and nothing else. `SETUP.md` now carries the full
Supabase walkthrough plus a cost table. It runs on free tiers, with two catches: a
free Supabase project pauses after a week idle, and the five cron schedules in
`vercel.json` need more than Vercel Hobby allows — the app is fine, the automation
just will not fire by itself.

## Open questions

- **Supabase project, then Vercel.** Nothing else about this can be judged until it
  has run once with real data. Roughly fifteen minutes, free. This is the blocker,
  not any code item.
- **Is email signup enabled in the Supabase dashboard?** It decides whether one auth
  finding — middleware treats an account with no role claim as an admin — is
  hardening or urgent. RLS still returns such an account nothing, so it is not a
  leak today.
- **Who may touch a public demo?** Read-only demo user, or a nightly re-seed. Needs
  the auth pass done first: a public demo is exactly where the finding above stops
  being theoretical.
- **Licence: decided 2026-08-19, deliberately none.** All rights reserved by
  default. Recorded here so nobody helpfully adds MIT later.
