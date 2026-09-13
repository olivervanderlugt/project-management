---
title: Vanuit de browser tegen de Hangar praten, met automatische routing
project: hangar
status: inbox
added: 2026-08-06
effort: L
branch:
---

## Done means

Nog niet schrijfbaar als één taak — hij is te groot en hij valt uiteen in vier
stappen die los waarde hebben. Zie hieronder. Per stap is een echte finish line
te schrijven; voor het geheel niet.

## Wat er gevraagd is

Ollie wil dit, in zijn woorden: de Hangar beschikbaar in zijn browser, die
automatisch alles wat hij zegt doorgeeft aan Claude, en die model, effort,
tokens en prioriteit grotendeels zelf bepaalt.

## Waar het nu staat

- Het bord staat al live op GitHub Pages en werkt op zijn telefoon. Lezen kan.
- Praten kan al via claude.ai/code: sessie kloont de repo, `CLAUDE.md` is de
  context. Model en effort kiest hij daar zelf.
- De nachtrun werkt de wachtrij af, één taak per nacht, oudste `ready` eerst.

Wat mist: iets opschrijven zonder een sessie te openen, en het systeem dat zelf
laat bepalen wat het waard is om aan te werken en met welk model.

## De vier stappen

**1 — Vangen vanuit de browser zonder sessie.** Een GitHub issue form op de
repo, plus een Action die Claude Code draait en van elke issue een `tasks/`
bestand maakt met `status: inbox`, een gok voor `project` en `effort`, en een
link terug naar de issue. github.com werkt op de telefoon, dus dit is "in de
browser" zonder eigen UI. Kost API-tokens, geen hosting.

**2 — Prioriteit automatisch.** Een score in `build.py`: doelgewichten uit
`reference/project-prioritering.md` maal status maal effort maal ouderdom. Het
bord toont dan één "dit nu", en de nachtrun hoeft niet meer op "oudste eerst" te
draaien. Volledig lokaal, geen kosten.

**3 — Model, effort en tokenplafond automatisch.** Een routeringstabel in de
repo: soort werk in, model plus effort plus tokenplafond uit. De nachtrun leest
hem en zet subagents op het juiste model in plaats van alles op het zwaarste.
Elke run schrijft zijn verbruik in `planning/night-log.md`, zodat er een echt
budget is in plaats van een gevoel.

**4 — Eigen UI met een invoerveld.** Pas hier is een server nodig: auth, een
API-sleutel die ergens veilig staat, iets dat sessies start, en hosting die
maandelijks geld kost. Dit breekt besluit 0001 (markdown eerst, echte app pas
als een project verdient). Als dit gebouwd wordt, hoort er eerst een nieuw
besluit te liggen dat 0001 vervangt — niet stiekem eromheen.

## Stand na de nachtrun van 2026-08-08

Aangescherpt, niet gebouwd:

- **Stap 2 is losgetrokken** als eigen taak: `tasks/hangar-prioriteit-score.md`,
  `status: ready`, effort S. Volledig lokaal, kost niets. De koppeling
  "nachtrun kiest op score" zit daar bewust NIET in — dat is een
  CLAUDE.md-regelwijziging en dus Ollie's besluit.
- **Stap 3 is grotendeels al gebeurd** sinds dit bestand geschreven werd:
  `routing.yml` bestaat en `scripts/gen_agents.py` genereert er de agents uit
  (zie besluit 0003, nog `proposed`). Wat van stap 3 overblijft: verbruik per
  nacht loggen in `planning/night-log.md`. Dat wordt pas een taak als 0003
  wordt aangenomen.
- ~~Stap 1 blijft liggen tot Ollie twee dingen beslist: (a) akkoord dat elke
  issue een API-call kost... (b) hij moet zelf de API-sleutel als repo-secret
  zetten~~ — **fout, zie de herchecking van 2026-09-13 hieronder: stap 1 was
  op het moment dat dit geschreven werd al twee dagen gebouwd en gebruikt geen
  van beide.**
- **Stap 4 blijft liggen** tot er een besluit ligt dat 0001 vervangt, zoals het
  bestand zelf al zegt.

Deze paraplu-taak blijft `inbox` tot stap 1 en 4 beslist zijn of geschrapt.

## Herchecked 2026-09-13 (nachtrun) — stap 1 stond al die tijd al gebouwd

Elke nacht sinds minstens 2026-08-23 herhaalde de log "nog geen
capture-label-issue" en liet stap 1 als open punt staan. Dat bleek onjuist
gelezen: het gaat om of er ooit een issue via het formulier is *binnengekomen*
(nog steeds nee — zie hieronder), niet of het mechanisme *bestaat*. Het bestaat
al sinds dag één:

- `.github/ISSUE_TEMPLATE/vangen.yml` en `.github/workflows/capture.yml` zijn
  gecommit op **2026-08-06**, dezelfde dag als deze taak zelf gevangen werd
  (commits `7b9e1d0`, `11e5e9a`) — dus vóór de 08-08-notitie hierboven die stap
  1 nog als "blijft liggen" beschreef.
- `scripts/capture_issue.py` (+ `scripts/test_capture_issue.py`) parsen het
  GitHub-issueformulier **deterministisch**, met een expliciete regel in het
  bestand zelf: "No dependencies beyond the standard library. No model calls,
  no network." Geen Claude-aanroep, dus geen API-sleutel, geen token-kosten
  per issue. Blokkade (a) en (b) uit de 08-08-notitie golden dus al twee dagen
  niet meer toen ze opgeschreven werden — het was gewoon niet herzien tegen de
  code.
- `git log --all --author="github-actions"` geeft nul resultaten: het
  mechanisme heeft nog nooit echt gedraaid, want Ollie heeft het
  vangformulier nog niet gebruikt. Er is dus niets kapot of onaf — het ligt
  klaar en wacht op gebruik, niet op een besluit.

**Wat dit betekent voor de taak als geheel:** van de vier stappen zijn 1, 2 en
het grootste deel van 3 al gebouwd en kosten niets. Het enige dat echt nog
openstaat is **stap 4** (eigen UI met invoerveld, server, auth, maandkosten) —
en die wacht, zoals altijd al gezegd, op een besluit dat 0001 vervangt.
Decision `0003` (het routeringsontwerp achter stap 3's restje) staat trouwens
ook nog steeds op `proposed`, ongewijzigd sinds 2026-08-06.

Blijft `inbox` — niet omdat er nog onderzoek nodig is, maar omdat stap 4 zonder
dat besluit geen `## Done means` kan krijgen. **Concrete vraag aan Ollie:** de
browser-kant van dit wens (lezen kan al, vangen zonder sessie kan al sinds
dag één, prioriteit en routing zijn al automatisch) is al waar. Wil je nog
steeds een eigen invoerveld-UI (stap 4, kost geld, vraagt een besluit dat 0001
vervangt) — of dekt "vangen via het GitHub-formulier + lezen via het bord" wat
je bedoelde, en mag deze taak dicht?

## Notes

Stap 1 tot en met 3 leveren het grootste deel van wat hij beschreef, zonder
server, zonder maandkosten en zonder 0001 te breken. Stap 4 is vooral een eigen
invoerveld in plaats van dat van GitHub.

Eén grens die overeind blijft: automatisch vangen is prima, automatisch bouwen
niet. Alles wat hij zegt gaat als `inbox` de wachtrij in; de stap naar `ready`
vraagt een echte `## Done means`. Dat is precies de rem die voorkomt dat de
nachtrun werk maakt dat 's ochtends de prullenbak in gaat.
