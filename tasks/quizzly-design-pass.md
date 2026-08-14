---
title: "Quizzly app-chrome, fase 1: ontwerpvoorstel (DESIGN.md)"
project: quizzly
status: done
added: 2026-08-08
effort: S
branch: claude/night-quizzly-design-pass
---

## Done means

`docs/DESIGN.md` bestaat en bevat, alleen voor de app-chrome (dashboard,
editor-chrome, login/signup, settings, discover, collab, terms/privacy — nooit
`.quiz-surface`/`--q-*`, die blijven voor alle tien quiz-themes ongemoeid):

- Een korte, concrete kritiek op het huidige chrome-palet: `--color-ink-50..950`
  (donkere neutrale ramp) en `--color-brand-400..700` (indigo), gedefinieerd in
  het `@theme`-blok van `src/app/globals.css`. `body` staat op
  `background: var(--color-ink-950)` — vrijwel zwart. Chrome is vandaag al
  consistent (geen losse Tailwind `gray-`/`slate-`/`zinc-`/`neutral-` klassen
  gevonden in `src/app` of `src/components` buiten de quiz-surface), dus dit is
  een echte richtingskeuze, geen opruimklus.
- **2 tot 3 concrete alternatieve richtingen**, elk met een eigen voorgestelde
  `--color-ink-*`-ramp (10 stappen, met hex) en `--color-brand-*`-ramp (of een
  andere naam als de richting geen indigo-accent meer gebruikt), en een korte
  onderbouwing (bijv. "lichter, meer wit" vs "donker maar warmer/minder blauw"
  vs "licht-modus als optie naast donker"). Minstens één richting moet passen
  bij "lichter" (hogere achtergrondluminantie dan `ink-950`).
- Per richting: een contrastcheck (WCAG AA, dus ≥4.5:1 voor gewone tekst,
  ≥3:1 voor grote tekst/UI-componenten) voor de belangrijkste tekst/achtergrond-
  en knop/achtergrond-combinaties uit die ramp — berekend, niet aangenomen.
  Elke richting bevestigt expliciet: geen wijziging aan `.quiz-surface`,
  `.quiz-card`, `.answer-tile` of enige `--q-*`-var, 44px minimum touch target
  blijft gelden, de bestaande `:focus-visible`-ring blijft zichtbaar.
- Een voor/na-beschrijving (woorden of een tokenvergelijkingstabel volstaat —
  geen gegenereerde mockup-afbeeldingen nodig) voor minstens de twee zwaarst
  bezochte chrome-schermen: het dashboard en de vraag-editor.
- Eén aanbevolen richting aan het eind, maar **niet doorgevoerd** — dat is
  bewust fase 2 (zie `quizzly-design-pass-toepassen`, die wacht op Ollie's
  keuze uit dit document).

`npm run typecheck && npm test && npm run build` blijven ongewijzigd groen,
want deze taak wijzigt geen `src/`-code — alleen `docs/DESIGN.md`.

## Notes

Gevraagd door Ollie op 2026-08-08. Origineel één taak ("voorstel, dan
doorvoeren") — losgetrokken in twee, zelfde patroon als
`hangar-in-de-browser` stap 2: het voorstel-schrijven is onderzoek dat een
nachtrun kan doen zonder Ollie's smaak nodig te hebben (het legt opties + hun
techniche gevolgen vast, het kiest niet); het doorvoeren wél, dus dat blijft
apart en `inbox` tot hij een richting kiest.
