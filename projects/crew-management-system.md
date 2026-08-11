---
title: Crew management system
description: Multi-tenant SaaS die Clevergig vervangt voor Nederlandse flex-crewbureaus in de evenementenbranche — plannen, inschrijven, klokken, uren, facturen.
status: parked
next: Beantwoord §3 en §8 van de strategy brief — Clevergig-factuur gezien, IP/contract geregeld. Dat is de poort voor al het andere.
due:
started:
repo: olivervanderlugt/crew-management-system
stack: Next.js App Router, TypeScript, Supabase (Postgres + Auth + RLS), Drizzle, Trigger.dev, Resend, Tailwind, Vitest, Playwright, Sentry
tags: saas, events, crew, multi-tenant
---

## What this is

Crew management voor Nederlandse flex-crewbureaus in de evenementenbranche: multi-tenant SaaS
als vervanging van Clevergig. Eerste klant heeft ~300 flexwerkers en ~5 planners, met piekbelasting
op festivalweekenden. Planners maken producties en shifts, crew schrijft zich in en klokt op de
telefoon in en uit, uren worden goedgekeurd, en daar rollen facturen en een payroll-export uit.

Gebouwd door één niet-professionele developer met Claude Code — dus expliciet: leesbare code
boven slimme code.

De Nederlandse regels zitten in het model, niet in de documentatie: alles `timestamptz` omdat
shifts over middernacht en over de zomertijd heen lopen, oproepen worden gelogd en nooit
overschreven, Arbeidstijdenwet-waarschuwingen bij het plannen, toeslagen als data omdat sinds
1 januari 2026 het loon gelijkwaardig moet zijn aan dat van de eigen werknemers van de klant,
en voor zzp'ers geen auto-toewijzing, geen verplichte klok en geen betrouwbaarheidsscore
(schijnzelfstandigheid / Wet DBA).

Bron: `reference/crewline-kickoff-pack.md`, opgeschreven 2026-08-11.

## Where it stands

Nul commits. De repo bestaat, is leeg, en blijft leeg tot de poort open is.

Wat er wél ligt: het volledige plan. De repo-`CLAUDE.md` en de vaste review-prompt staan in
`reference/crewline-kickoff-pack.md`, en de acht bouwstappen staan als `crewline-*` in `tasks/` —
allemaal `inbox`, met de finish line er al in geschreven. Zodra §3 en §8 beantwoord zijn is
promoveren naar `ready` één woord per bestand.

## Open questions

- **De poort.** §3 en §8 van de strategy brief: de echte Clevergig-factuur gezien, en IP/contract
  geregeld. Tot dat er is start er niets. Zie `tasks/crewline-startgate.md`.
- **De naam.** "Crewline" is uitdrukkelijk een werknaam — "change it everywhere before you start".
  Nu wijzigen kost een find-and-replace, na de eerste commit kost het werk.
- **Welk payroll-systeem** draait de eerste klant? Blokkeert M6; een exportformaat is niets om
  naar te gokken.
- **Welk festival, welke datum** is de go-live? Blokkeert M7 — die milestone is er volledig
  omheen geschreven.
