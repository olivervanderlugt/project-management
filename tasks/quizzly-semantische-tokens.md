---
title: "Quizzly chrome: semantische tokenlaag, zonder één zichtbare verandering"
project: quizzly
status: ready
added: 2026-08-20
effort: M
branch:
---

## Done means

De app-chrome wijst niet langer rechtstreeks naar een tree van de `ink`-ramp,
maar naar semantische tokens die per stand kunnen omklappen. **Deze taak
verandert niets aan hoe de app eruitziet.** Dat is de hele opzet: de refactor en
de smaakwijziging worden gescheiden, zodat bij een regressie duidelijk is welke
van de twee hem veroorzaakte.

1. In het `@theme`-blok van `src/app/globals.css` staat een semantische laag —
   namen naar rol, niet naar kleur: vlak, verhoogd vlak, rand, tekst, gedempte
   tekst, invoervlak, en zo verder. Elk token krijgt zijn waarde uit de
   bestaande `ink`-ramp, met exact de tint die de plek vandaag al gebruikt.
2. Elke app-chrome-plek in `src/app` en `src/components` gebruikt die tokens.
   Tel eerst zelf hoeveel `*-ink-NNN`-utilities er staan en noem dat getal in de
   PR — `docs/DESIGN.md` telde er 166 op 2026-08-11, een telling van 2026-08-20
   gaf er 174. Het getal is gedrift; vertrouw geen van beide, tel opnieuw.
3. `.quiz-surface`, de `--q-*`-variabelen en de tien quiz-themes blijven
   **volledig ongemoeid**. Die staan los van de chrome en horen niet bij deze
   refactor. Raak je ze toch aan, dan is dat een fout, geen bijvangst.
4. 44px touch targets en de `:focus-visible`-ring blijven staan.
5. Bewijs dat er niets veranderd is aan het beeld: geen enkele berekende
   kleurwaarde op de twee schermen uit §5 van `docs/DESIGN.md` (dashboard en
   vrageneditor) verschilt van vóór de refactor. Zeg in de PR hoe je dat hebt
   vastgesteld — een screenshot-vergelijking, of de tokens per plek uitgerekend
   en naast de oude tint gelegd. "Ziet er hetzelfde uit" is geen bewijs.
6. `npm run typecheck && npm test && npm run build` groen.

## Notes

Stap 1 van twee. Ollie koos op 2026-08-20 **richting C ("Twee standen")** uit
`docs/DESIGN.md` — donker blijft het uitgangspunt, wie zijn besturingssysteem op
licht heeft krijgt automatisch een lichte chrome.

Het document beveelt B aan en zegt over C: het juiste eindpunt, de verkeerde
volgende stap, omdat de `ink`-utilities eerst naar een semantische laag moeten
en je die refactor niet wilt combineren met een smaakwijziging. Ollie koos C
alsnog — dat is zijn keuze. Wat het document daarover zegt is hier niet genegeerd
maar opgevolgd: de refactor is deze taak, de smaakwijziging is
`quizzly-design-pass-toepassen`, en die staat `blocked` tot deze af is.

De vier reparaties uit §1.3 (te lichte hulptekst, hover onder AA, invoervelden
zonder waarneembare grens, vijf brand-tinten die geen CSS opleveren) horen bij
géén van beide taken: die zitten in `quizzly-chrome-contrast-bugs`, gebouwd en
goedgekeurd, wachtend op Ollie's merge van quizzly#5. Loopt die merge vóór deze
taak, dan neem je de nieuwe waarden als uitgangspunt; loopt hij erna, dan raak je
ze niet aan.
