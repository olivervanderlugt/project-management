---
title: Een al door Ollie geaccepteerd, af gebouwd PR-plafond-besluit is 25 nachten kwijt geweest
project: hangar
status: inbox
added: 2026-09-05
effort: S
branch:
---

## Done means

Nog niet schrijfbaar — dit raakt regel 5, een van de weinige harde
veiligheidsregels van de nachtrun (`reference/nightrun-rules.md`). Of en hoe
dit landt is Ollie's beslissing, niet iets wat een nachtrun zelf doorvoert.
Zie "Wat Ollie moet beslissen" hieronder.

## Wat er gevonden is

Vanavond (2026-09-05, stap 3, bij het opnieuw onderzoeken van
`hangar-daysession-branches-onzichtbaar`) is de branchronde uit die taak
herhaald tegen de huidige branchlijst, niet alleen de vier eerder genoemde
branches. Dat leverde twee nieuwe, nooit eerder onderzochte niet-ancestor-
branches op. Eén ervan, `claude/charming-fermat-kdilid` (laatste commit
2026-08-11, nooit een PR), draagt één volledig af gebouwd en door Ollie
geaccepteerd besluit dat sindsdien **volledig onzichtbaar** is geweest:

- `decisions/0004-nachtrun-pr-plafond-verhoogd.md` — `status: accepted`,
  `date: 2026-08-11`. Context in het besluit zelf: op 2026-08-11 stond de
  toenmalige teller op precies 3 (`project-management#5`, `percentile#1`,
  `learning-website#3`) en werd er die nacht niets gebouwd — puur omdat regel
  5 geen onderscheid maakte tussen "Ollie moet dit nog beoordelen" en "Ollie
  hoeft alleen op merge te klikken". Ollie vroeg expliciet: "verhoog het
  plafond... maar bouw het slimmer en veiliger."
- Het besluit zelf: (1) een PR met een `APPROVED`-review telt niet meer mee
  als schuld, (2) plafond per repo (2) én totaal (8) in plaats van één platte
  teller, (3) bij een vol plafond niet meteen de hele nacht overslaan maar
  het eerste `ready`-taak proberen waarvan de repo nog ruimte heeft, (4) een
  PR die >14 dagen ongezien blijft telt niet mee voor het plafond maar wordt
  wél genoemd in het night-log — een hoger plafond mag een genegeerde PR niet
  onzichtbaar maken.
- **Volledig geïmplementeerd, niet alleen bedacht**: `scripts/pr_limits.py`
  (`decide()`, `first_open_repo()`, een pure functie op JSON-input, geen
  eigen GitHub-aanroepen) plus `scripts/test_pr_limits.py` (183 regels tests).
  Gelezen vanavond: het script is zelfstandig, raakt geen van de bestanden die
  sindsdien zijn veranderd (het dateert van vóór besluit `0005`, dat de regels
  uit `CLAUDE.md` naar `reference/nightrun-rules.md` verplaatste, maar het
  script zelf hangt daar niet van af).
- De branch bevat ook een CLAUDE.md-wijziging die de regel destijds inline
  herschreef — die is NIET meegenomen in deze taak, want CLAUDE.md's
  nachtrun-regels leven nu in `reference/nightrun-rules.md` (na besluit
  0005); die CLAUDE.md-diff van 08-11 past niet meer op de huidige structuur
  en zou opnieuw geschreven moeten worden, niet gekopieerd.

**Waarom dit meer is dan "nog een gemiste branch": het probleem dat dit
besluit oploste, is 25 nachten lang blijven bestaan.** Elke nacht van
2026-08-21 t/m vanavond (2026-09-05: zie `planning/night-log.md` en de
`Night YYYY-MM-DD`-PR's #15 t/m #29) heeft dezelfde platte "3 open PR's dus
niet bouwen"-regel toegepast — precies het gedrag dat dit besluit op
2026-08-11 al had opgelost. De drie PR's die al die nachten tellen
(`percentile#1`, `learning-website#3`, en later `project-management#13`)
zijn stuk voor stuk PR's die géén `APPROVED`-review hebben en dus onder
zowel de oude als de nieuwe telling als schuld tellen — dit specifieke
besluit had dus vanavond zelf niet tot een andere uitkomst geleid (nog
steeds 3 stuks schuld, nog steeds onder het per-repo/totaal-plafond). Maar
over 25 nachten zijn er ongetwijfeld nachten geweest waarin een taak-PR wél
een `APPROVED`-review kreeg en desondanks meetelde tegen het platte plafond
— dat is precies het scenario waarin dit besluit een nacht van "niets
gebouwd" had omgezet in "wel gebouwd". Niemand heeft dat per nacht
teruggezocht; dat zou zelf weer een aparte, grotere uitzoekklus zijn.

## Wat Ollie moet beslissen

1. **Wil je dit alsnog invoeren?** Het besluit is al `accepted` en het werk
   staat er, getest, klaar om in te haken op `reference/nightrun-rules.md`
   regel 5 (na besluit 0005's verhuizing) — maar het is 25 dagen oud. Wil je
   het zoals het daar staat, of eerst herzien in het licht van hoe de vloot
   sindsdien is gegroeid (van 1 naar 7 gekoppelde repo's; de caps 2/8 waren
   getuned voor een kleinere situatie)?
2. **Decisionnummer.** `0004` is inmiddels viervoudig vergeven op verschillende
   branches (`nightrun-auto-merge` — de echte, live versie; `altijd-aan-
   kastje-thuis` — herno naar `0006` bij een eerdere recovery;
   `percentile-cut-the-co-op` — expliciet niet aangenomen). Dit zou `0007`
   worden, niet `0004`.
3. **Wie voert het door.** Dit is precies het soort wijziging die niet
   unilateraal door een nachtrun hoort te gebeuren (het raakt een
   veiligheidsregel, niet een gewone taak) — een `ready`-taak voor een
   dagsessie, of iets dat een nachtrun pas mag bouwen ná jouw akkoord hier?

## Notes

Gevonden via dezelfde branchronde als `hangar-daysession-branches-
onzichtbaar` (`git branch -r` + `git merge-base --is-ancestor` tegen de
default, voor elke nog niet eerder verantwoorde branchnaam). Bewust
vanavond NIET zelf doorgevoerd — dit wijzigt regel 5, en "twijfel je of iets
binnen de grenzen valt, dan valt het erbuiten" gaat hier zeker op. Het
besluit, de scripts en deze analyse staan hier vast zodat de vondst zelf niet
alsnog kwijtraakt, ook als niemand `kdilid` ooit weer opent.

Zie ook `hangar-daysession-branches-onzichtbaar.md`'s "Aangescherpt
2026-09-05" — dezelfde branchronde vond nog een tweede, kleiner voorbeeld
(een complete, "done"-gemarkeerde "lessons loop"-feature op
`claude/hangar-project-setup-w61m5q`, ook nooit gemerged).
