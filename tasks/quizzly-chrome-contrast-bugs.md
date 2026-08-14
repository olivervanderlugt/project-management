---
title: "Quizzly: vier a11y/CSS-bugs in de app-chrome (onafhankelijk van kleurrichting)"
project: quizzly
status: ready
added: 2026-08-13
effort: S
branch:
---

## Done means

Vier concrete, met de echte code en een herrekende WCAG-luminantieformule
bevestigde defecten in `src/`, allemaal onafhankelijk van welke richting uit
`docs/DESIGN.md` Ollie kiest — dus geen `quizzly-design-pass-toepassen`-
voorwaarde, dit mag los. Na de fix: elk gemeten contrast haalt WCAG AA
(≥4.5:1 gewone tekst, ≥3:1 grote tekst/UI-componenten), `npm run typecheck
&& npm test && npm run build` groen.

1. **`text-ink-500` (`#5d6490`) faalt AA**: 3.42:1 op de pagina-achtergrond,
   3.15:1 op een kaart — tegen de vereiste 4.5:1. 44 gebruiksplekken in 16
   bestanden, bijna allemaal `text-xs` (helptekst onder editorvelden,
   "(optioneel)"-labels, autosave-status). Fix: naar een donkerder token dat
   wel haalt (bijv. `text-ink-400`, opnieuw berekenen na de keuze).
2. **`.btn-primary:hover` zakt onder AA**: hover verlicht naar `brand-500`,
   waardoor witte knoptekst op 4.47:1 komt (net onder 4.5). Fix: donkerder
   i.p.v. lichter op hover.
3. **`.app-input` faalt WCAG 1.4.11**: achtergrond is gelijk aan de
   pagina-achtergrond, dus het veld is alleen herkenbaar aan een
   `ink-700`-rand op 1.72:1 (vereist 3:1). Fix: eigen achtergrond voor het
   veld, of een randkleur die 3:1 haalt.
4. **Vijf `brand`-tinten bestaan niet**: `brand-200/300/800/900/950` worden
   gebruikt in `src/` maar zijn nooit gedefinieerd in het `@theme`-blok van
   `src/app/globals.css`, dus Tailwind genereert er niets voor — bevestigd
   tegen de gebouwde stylesheet. Zichtbaar kapot: het dashboard's
   "group · collecting"-badge heeft geen achtergrond en geërfde tekstkleur,
   naast een "public"-badge die wel werkt (`emerald-900/300` bestaan wel).
   Fix: de ontbrekende stappen toevoegen aan de `brand`-ramp.

## Notes

Gevonden tijdens de nachtrun van 2026-08-13, als bijvangst van de
`quizzly-design-pass`-taak (het DESIGN.md-onderzoek) en onafhankelijk
bevestigd door de `hangar-checker`-agent met een eigen herimplementatie van
de WCAG-relatieve-luminantieformule (zie PR olivervanderlugt/quizzly#2,
sectie "Vier defecten die los van de richting gelden"). Rechtstreeks op
`ready` gezet omdat de vier fixes mechanisch zijn — geen smaakbesluit zoals
`quizzly-design-pass-toepassen`, puur toegankelijkheids-/CSS-bugs die met
elke gekozen richting terugkomen als ze nu niet gefixt worden. Niet vannacht
gebouwd (limiet: één taak per nacht, `quizzly-design-pass` was de taak van
vanavond).
