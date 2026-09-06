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

## Update 2026-08-31 — het probleem is erger dan hierboven staat

Zes nachten later (08-25 → 08-31): de stapel is niet vier maar **tien**
open stap-4-PR's (`project-management#15`-`#24`), en de kosten zijn niet
langer alleen "PR's die zich opstapelen" — vanavond is bewezen dat het
werk zelf verloren gaat, niet alleen onzichtbaar blijft:

- De nacht van 08-29 deed een grote herstelactie (een 8 nachten oude
  dagsessie-branch zonder PR teruggehaald, vier taakbestanden samengevoegd,
  `hangar-daysession-branches-onzichtbaar` geschreven) en zette dat op zijn
  eigen `claude/night-2026-08-29`-PR.
- De nacht van 08-30 vertakte — zoals elke nacht — vanaf de **stale default**
  (`861f2c3`), niet vanaf 08-29's branch. Die nacht zag dus niets van 08-29's
  herstelwerk, deed zijn eigen (kleinere) herstelactie (`pi-openclaw-gateway`
  teruggehaald), en zette dát weer op een eigen geïsoleerde PR.
- Resultaat: twee nachten die allebei "vraag 3" van
  `hangar-daysession-branches-onzichtbaar` beantwoordden, onafhankelijk van
  elkaar, allebei zonder het te weten. Precies het patroon dat 08-29 zelf al
  signaleerde bij `hsr0iy` (rule "elke nacht leest via `git show
  origin/claude/night-<datum>:tasks/...`, dat werkt maar is fragieler dan het
  hoeft") — nu bewezen dat het zichzelf herhaalt, één niveau dieper: niet
  alleen dagsessie-branches zonder PR raken zo onzichtbaar, de nachtrun se
  eigen wrapup-PR's doen het elkaar nu ook aan.

Vanavond (08-31) zijn `claude/night-2026-08-29` en `claude/night-2026-08-30`
met de hand samengevoegd op een nieuwe branch (`claude/night-2026-08-31`) om
niets kwijt te raken — maar dat is een eenmalige reparatie, geen structurele
oplossing. Zonder een keuze uit de drie opties hierboven gebeurt dit
volgende week weer, alleen dan met elf branches om samen te voegen in plaats
van twee.

**Dit verzwakt optie 3 en versterkt optie 1/2**: een lager plafond op het
*aantal* open wrapup-PR's voorkomt niet dat de *inhoud* van de meest recente
ervan onzichtbaar is voor de volgende nacht — alleen "iets landt elke nacht
op de default branch" (optie 1 of 2) doet dat. De keuze blijft aan Ollie;
dit is alleen het bewijs dat wachten de kosten laat oplopen.

## Herchecked 2026-09-06 (nachtrun, stap 3)

Gekozen als oudste nog niet recent herverifieerde inbox-taak (laatst
aangescherpt 08-31, zes nachten geleden — de vijf andere inbox-taken zijn
allemaal binnen de laatste vijf nachten gecheckt: zelfde selectieregel als
09-04 en 09-05 gebruikten).

Rechtstreeks bij GitHub opgevraagd, niet aangenomen: de stapel is nu **16**
open stap-4-PR's (`project-management#15` t/m `#30`, Night 2026-08-21 t/m
Night 2026-09-05), tegen 10 op 08-31 en 4 op 08-25. Groei is vrijwel exact
één per nacht, zoals voorspeld — geen versnelling, maar ook geen enkele
avond die er één heeft opgeruimd. Geen van de drie opties hierboven is
gekozen; niets aan de kern van het probleem is veranderd. Dit is dus geen
nieuwe vondst, maar bevestiging dat het ongewijzigd (en groter) doorloopt.

Eén relevante toevoeging sinds 08-31: `hangar-pr-plafond-kwijt` (gevonden
2026-09-05) is een **ander, wel verwant** governance-gat — dat gaat over hoe
regel 5 taak-PR-schuld telt (plat vs. review-status), dit hier gaat over de
nachtrun se eigen stap-4-PR die nooit landt. Los van elkaar oplosbaar, allebei
nog `inbox`, allebei wachtend op een keuze van Ollie. Niet samengevoegd — ze
raken verschillende regels en kunnen onafhankelijk beslist worden.

Zoals eerdere nachten ook oordeelden: dit blijft `inbox`, niet `ready` — de
drie opties bestaan al, maar welke Ollie kiest is een smaak-/procesbeslissing,
geen onderzoeksvraag. Niet zelf een van de drie opties doorgevoerd (zou regel
5 of `reference/nightrun-rules.md` raken, dat hoort niet unilateraal).
