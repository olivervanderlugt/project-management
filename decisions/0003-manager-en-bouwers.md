---
title: Werk verdelen over een goedkope manager en dure bouwers
status: proposed
date: 2026-08-06
---

## Context

De nachtrun is nu één agent die alles zelf doet: kiezen, lezen, bouwen,
controleren en opschrijven. Dat werkt, maar het is de duurste vorm. Alles
gebeurt op het zwaarste model, ook het sorteren en het bijwerken van
frontmatter, en de context groeit de hele nacht door omdat dezelfde agent code
leest én het plan vasthoudt.

Ollie werkt in zijn eigen projecten al anders: een Fable 5-agent als manager die
Opus-agents aanstuurt, controleert en bijstuurt tot het doel gehaald is. De
vraag is of de Hangar dat overneemt.

Het alternatief is laten zoals het is. Dat is minder om te onderhouden, en één
agent die alles ziet maakt geen coördinatiefouten. Het kost alleen meer, en het
schaalt niet naar meerdere taken per nacht.

## Decision

Splitsen in vier rollen: een manager op een goedkoop, snel model die het plan
vasthoudt en nooit projectcode leest; bouwers op een zwaar model met een smalle
brief en een eigen branch; een controleur die alleen de diff en de finish line
ziet en moet proberen te bewijzen dat het niet af is; en boekhouding als script,
zonder model.

Model, effort en tokenplafond per soort werk liggen vast in `routing.yml`. De
manager mag daarvan naar beneden afwijken, nooit naar boven.

Agents wisselen vaste JSON-berichten uit — brief, rapport, oordeel — in plaats
van proza. Niet vanwege de tokens, maar omdat een schema afdwingt dat er per
finish line waar of niet waar wordt gezegd, met bewijs.

De uitwerking staat in `reference/agent-orkestratie.md`.

## Consequences

Makkelijker: meer werk per nacht voor minder geld, een echt tokenbudget in
plaats van een gevoel, en een controlestap die het verschil ziet tussen "er is
gepusht" en "het is af". Rollen zijn los te vervangen — een beter model voor
bouwers verandert één regel in de tabel.

Moeilijker: er zijn nu vier dingen die stuk kunnen in plaats van één, en
coördinatiefouten zijn nieuw. Twee bouwers in dezelfde bestanden is de
gevaarlijkste; daarom eist dit worktrees en briefs die elkaars bestanden niet
raken. Debuggen wordt lastiger omdat er niet één transcript meer is.

Dit is een voorstel, geen genomen besluit. Het gaat pas op `accepted` als stap 1
van de bouwvolgorde draait — de routeringstabel en de boekhoudscripts — want tot
die tijd is er niets meetbaar en is de rest gokwerk.
