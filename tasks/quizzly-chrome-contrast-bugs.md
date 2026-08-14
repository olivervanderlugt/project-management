---
title: "Quizzly: vier a11y/CSS-bugs in de app-chrome (onafhankelijk van kleurrichting)"
project: quizzly
status: blocked
added: 2026-08-13
effort: S
branch: night/quizzly-chrome-contrast-bugs
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

## Waar het staat (2026-08-14)

Gebouwd, afgekeurd, gerepareerd en opnieuw gecheckt. **quizzly#5** staat open en
wacht op Ollie's merge.

Alle vier de defecten gefixt, elke ratio door bouwer én checker onafhankelijk
herrekend met de echte WCAG-luminantieformule:

1. `text-ink-500` → `text-ink-400` op 47 plekken in 18 bestanden — 5.82:1 op de
   paginakleur, 5.37:1 op een kaart (was 3.42:1 / 3.15:1).
2. `.btn-primary:hover` van `brand-500` naar `brand-700` — wit op 7.90:1 (was
   4.47:1). Donkerder op hover, niet lichter.
3. `.app-input`-rand van `ink-700` naar `ink-500` — 3.42:1 (was 1.72:1), haalt de
   3:1 van WCAG 1.4.11. De veldachtergrond blijft gelijk aan de pagina; de finish
   line liet beide routes toe en een eigen achtergrond is een smaakbesluit dat bij
   `quizzly-design-pass-toepassen` hoort.
4. `brand-200/300/800/900/950` toegevoegd aan het `@theme`-blok. Geverifieerd in
   de gebouwde stylesheet, niet alleen in de bron.

**Wat de checker ving:** de eerste ronde had `.app-input::placeholder` laten
staan op `ink-500` — binnen exact het regelblok dat gewijzigd werd. Elke
class-gebaseerde `text-ink-500` was gemigreerd, deze CSS-regel niet, dus defect 1
overleefde op elke placeholder in de editor, login, settings en collab. Gefixt,
hercheck groen.

**Voor jou:** `brand-200` bestaat in geen van de drie richtingen in
`docs/DESIGN.md`, terwijl `src/` het wel gebruikt — een gat in het ontwerpdoc,
geen botsing. De andere vier tinten zijn in alle drie de richtingen identiek, dus
deze fix loopt geen enkele richting voor de voeten.
