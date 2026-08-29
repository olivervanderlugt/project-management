---
title: "Quizzly app-chrome, fase 2: richting C doorvoeren — licht als stand naast donker"
project: quizzly
status: blocked
added: 2026-08-11
effort: M
branch:
---

## Done means

Wacht op `quizzly-semantische-tokens`. Zonder die laag is dit een refactor én
een smaakwijziging in één diff, en dat is precies wat `docs/DESIGN.md` §6
afraadt: bij een regressie weet je dan niet welke van de twee hem deed.

Zodra die er ligt:

1. Eén ramp, twee standen. Donker blijft het uitgangspunt. De semantische
   tokens uit stap 1 krijgen een lichte set waarden die aanslaat op
   `prefers-color-scheme: light`.
2. De rolverdeling die `docs/DESIGN.md` §4 onder richting C uitschrijft, is
   leidend voor welk token in welke stand welke tree krijgt.
3. WCAG AA contrast geldt in **beide** standen, opnieuw gemeten en niet
   aangenomen uit fase 1 — het rekenscript staat in bijlage A van dat document.
   Elke ratio twee keer onafhankelijk uitgerekend, zoals bij
   `quizzly-chrome-contrast-bugs`.
4. `.quiz-surface`, `--q-*` en de tien quiz-themes blijven ongewijzigd. Een
   quiz ziet er in beide standen hetzelfde uit; alleen de chrome klapt om.
5. 44px touch targets en de `:focus-visible`-ring blijven staan, in beide
   standen.
6. `npm run typecheck && npm test && npm run build` groen.

## Notes

Losgetrokken van `quizzly-design-pass` op 2026-08-11.

**Richting gekozen op 2026-08-20: C, "Twee standen".** Daarmee is de blokkade
"Ollie moet kiezen" weg. Wat er nu vóór ligt is niet zijn keuze maar de volgorde
die het document zelf voorschrijft — eerst de tokenlaag, dan de stand. Daarom
`blocked` in plaats van `ready`, met precies één ding waar het op wacht.

Het argument voor C, uit het document: Ollie kiest niet tussen licht en donker,
het apparaat kiest. Voor een tool die op een beamer in een lokaal én op een
laptop 's avonds gebruikt wordt, is dat inhoudelijk het sterkste antwoord.
