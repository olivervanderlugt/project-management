---
title: "Quizzly app-chrome, fase 2: gekozen ontwerp doorvoeren"
project: quizzly
status: inbox
added: 2026-08-11
effort: M
branch:
---

## Done means

Nog niet schrijfbaar. Wacht op Ollie: hij moet uit `docs/DESIGN.md` (taak
`quizzly-design-pass`, fase 1) een richting kiezen — desnoods met eigen
aanpassingen erop. Zonder die keuze is er geen finish line die iemand anders
kan afvinken; alleen "consistent doorvoeren" is geen concrete Done means.

Zodra hij gekozen heeft, is de Done means naar verwachting: de gekozen
`--color-ink-*`/`--color-brand-*`-ramp (of vervanger) staat in het
`@theme`-blok van `src/app/globals.css`, elke app-chrome plek in `src/app` en
`src/components` (buiten `.quiz-surface`/`--q-*`) gebruikt hem consistent,
`.quiz-surface`/`--q-*` en de tien quiz-themes zijn ongewijzigd, 44px touch
targets en de `:focus-visible`-ring blijven staan, WCAG AA contrast blijft
gelden (opnieuw gecheckt, niet aangenomen uit fase 1), en `npm run typecheck
&& npm test && npm run build` zijn groen.

## Notes

Losgetrokken van de oorspronkelijke `quizzly-design-pass` op 2026-08-11 —
zie de Notes daar. Blijft `inbox` tot Ollie's keuze er is; dat is geen
onderzoeksvraag die een nachtrun voor hem kan beslissen.
