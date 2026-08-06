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

## Notes

Stap 1 tot en met 3 leveren het grootste deel van wat hij beschreef, zonder
server, zonder maandkosten en zonder 0001 te breken. Stap 4 is vooral een eigen
invoerveld in plaats van dat van GitHub.

Eén grens die overeind blijft: automatisch vangen is prima, automatisch bouwen
niet. Alles wat hij zegt gaat als `inbox` de wachtrij in; de stap naar `ready`
vraagt een echte `## Done means`. Dat is precies de rem die voorkomt dat de
nachtrun werk maakt dat 's ochtends de prullenbak in gaat.
