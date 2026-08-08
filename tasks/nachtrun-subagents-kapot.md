---
title: Nachtrun kan geen subagents spawnen — bouwen zou stil zijn uitgevallen
project:
status: inbox
added: 2026-08-08
effort: S
branch:
---

## Done means

Een nachtrun die moet bouwen doet aantoonbaar één van twee dingen, zichtbaar in
het night-log: (a) hij spawnt de builder- en checker-agents via de Task-tool,
of (b) hij bouwt zelf en doet daarna een expliciete, vijandige zelf-check van
het diff tegen de `## Done means`, met de notitie dat dit inline gebeurde.
Stil overslaan van de check telt niet als af.

## Notes

Nacht van 2026-08-08: de run meldde zelf dat de project-builders en de checker
niet aanroepbaar waren. Oorzaak gevonden: de Routine (aangemaakt via de
claude.ai-UI) krijgt een vaste toolset zonder `Task` — subagents kunnen dus per
constructie niet. De run had die nacht toevallig niets te bouwen, anders was
het stil misgegaan.

Fix van 2026-08-08: regel 8 toegevoegd aan CLAUDE.md "Overnight runs" —
subagent-check aan het begin, en zonder subagents: zelf bouwen en daarna zelf
vijandig checken tegen `## Done means`; een build zonder check mag niet
gepusht. Zit op branch `claude/hangar-nightrun-push-issue-njdjly` en werkt pas
als die de default branch bereikt.

Kon niet: de Routine-prompt zelf aanpassen — UI-gemaakte routines zijn voor
agents read-only. Docs beloven juist dat subagents in cloudsessies werken en
kennen géén instelling om een tool aan een routine toe te voegen; dit lijkt
dus een platformbug. Wat Ollie kan doen: (1) deze branch mergen, (2) optioneel
de SUBAGENTS-alinea zelf in de routine-prompt plakken via de Routines-UI,
(3) de bug melden via /feedback, met verwijzing naar de docs-belofte dat
subagents in cloudsessies werken.
