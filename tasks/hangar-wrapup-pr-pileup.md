---
title: Nachtrun-wrapup-PR's stapelen op — niemand merget ze
project: hangar
status: inbox
added: 2026-08-25
effort: S
branch:
---

## Done means

Nog niet schrijfbaar — dit is een procesvraag voor Ollie, geen onderzoeksvraag
die een nachtrun zelf kan beslissen. De keuze bepaalt de vorm van de fix:

1. **Laat de nachtrun zijn eigen stap-4-PR (`claude/night-<datum>`, night-log +
   dashboard-rebuild) automatisch mergen**, net als regel 3 al doet voor
   taak-PR's (adversarieel gecheckt → meteen gemerged, nooit "iemand moet dit
   eerst bekijken"). Argument voor: er is geen `## Done means` om tegen te
   checken — het is alleen een logregel + een gegenereerd bestand, laag risico,
   en regel 5's aanname ("een PR die openstaat is vastgelopen, niet in
   afwachting van review") klopt dan ook echt voor déze PR's. Nadeel: Ollie
   ziet de night-log dan pas ná de merge, niet als PR-diff vooraf.
2. **Iets moet elke nacht expliciet de vorige nacht(en) se stap-4-PR
   afhandelen** (mergen, of bewust laten staan met een reden) vóórdat het een
   nieuwe opent — zodat er nooit meer dan één open tegelijk is. Kost een
   expliciete regel in `reference/nightrun-rules.md`.
3. **Status quo, met een lager plafond**: expliciet documenteren dat stap-4-PR's
   niet meetellen in regel 5's teller (dat gebeurt al in de praktijk) maar wél
   een eigen, lagere grens krijgen — bijvoorbeeld: bij twee openstaande
   wrapup-PR's stopt de nachtrun helemaal (geen stap 2 én geen stap 3) tot
   Ollie er één gemerged heeft.

Zodra Ollie kiest, is de rest mechanisch: optie 1 is een regel in
`reference/startprompt-nightrun.md`/`nightrun-rules.md` ("merge je eigen
stap-4-PR na het pushen, tenzij GitHub het weigert"); optie 2 een expliciete
"eerst opruimen"-stap vóór stap 1; optie 3 een grenswaarde plus een teller die
apart van de taak-PR's telt.

## Notes

Waargenomen over vier opeenvolgende nachten (2026-08-21 t/m 2026-08-24): elke
nacht met "3 stuck PR's, dus niet gebouwd" opende aan het eind gewoon zijn
eigen `claude/night-<datum>`-PR (stap 4) zonder ook maar te proberen hem te
mergen, en zonder de vorige nacht(en) se PR te mergen. Resultaat vanavond
(2026-08-25): `project-management#15/#16/#17/#18` staan alle vier nog open,
elk alleen een night-log-regel + dashboard-rebuild, geen van alle vier
inhoudelijk risicovol. Praktisch gevolg, expliciet genoemd in de 08-24-log:
het onderzoek dat 08-21/22/23 deden op `versa-hosting-besluit`,
`quizzly-legal-review-west` en `hangar-in-de-browser` staat daardoor nog
steeds niet op de default branch — elke volgende nacht leest het via
`git show origin/claude/night-<datum>:tasks/...` in plaats van gewoon het
taakbestand, om niet dubbel te werken. Dat werkt, maar is fragieler dan het
hoeft te zijn: het hangt af van elke nacht die zich herinnert waar te zoeken.

Dit is bewust NIET zelf besloten of gefixt door de nacht die dit schrijft
(2026-08-25) — mergen van PR's die een andere sessie opende, buiten een
expliciete regel om, voelt als precies het soort "twijfel dan valt het
erbuiten"-geval uit de opdracht. Vandaar: opgeschreven, niet uitgevoerd.

Regel 5 (`reference/nightrun-rules.md`) zegt met zoveel woorden dat een
openstaande overnight-PR "een vastgelopen merge van een vorige nacht"
betekent — maar sluit de eigen stap-4-PR er in de praktijk stilzwijgend van
uit (vier nachten op rij tellen hem niet mee bij stap 1, en terecht: het is
geen taak-PR met een checker-oordeel). Die twee dingen — "een openstaande PR
is per definitie vastgelopen" en "de stap-4-PR telt niet mee" — spreken elkaar
een beetje tegen zonder dat de regel het uitlegt. Vandaar dat dit taakje ook
voorstelt om het gewoon met zoveel woorden op te schrijven, welke kant Ollie
ook kiest.
