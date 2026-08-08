---
title: Prioriteitsscore per taak in build.py, bord toont "dit nu"
project: hangar
status: ready
added: 2026-08-08
effort: S
branch:
---

## Done means

`dashboard/build.py` berekent voor elke open taak (`inbox`/`ready`/`blocked`)
een deterministische prioriteitsscore uit vier factoren: een projectgewicht uit
een tabel die in de repo staat (nieuw blok in `routing.yml` of een eigen
`weights.yml`, gevuld met startwaarden afgeleid uit
`reference/project-prioritering.md`, door Ollie aan te passen zonder code te
raken), status (`ready` boven `inbox` boven `blocked`), effort (S boven M boven
L) en ouderdom (ouder weegt zwaarder). Het bord toont de open taken gesorteerd
op die score plus één duidelijke "dit nu"-regel bovenaan. Twee keer bouwen
geeft twee keer exact hetzelfde resultaat; taken zonder project krijgen een
neutraal gewicht in plaats van een crash. De formule staat met één
commentaarblok uitgelegd bij de code.

Nadrukkelijk NIET in deze taak: de nachtrun laten kiezen op score in plaats van
"oudste `ready` eerst". Dat is een regelwijziging in CLAUDE.md en dus een
besluit van Ollie, pas nadat hij de scores een tijdje op het bord heeft gezien.

## Notes

Dit is stap 2 uit `tasks/hangar-in-de-browser.md`, losgetrokken door de
nachtrun van 2026-08-08 omdat hij als enige van de vier stappen volledig lokaal
is, niets kost en een schrijfbare finish line heeft.

`reference/project-prioritering.md` geeft ●-scores per doel maar kiest geen
weging tussen doelen — daarom moeten de projectgewichten als data in de repo
staan waar Ollie ze kan bijstellen, niet hardcoded in de formule.

De parser in `build.py` is bewust simpel (plat `key: value`); de gewichtentabel
moet dat blijven.
