---
title: Nachtrun kan geen subagents spawnen — bouwen zou stil zijn uitgevallen
project:
status: done
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

**Gesloten 2026-08-09 (nachtrun, tijdens de aanscherp-stap).** De genoemde
branch `claude/hangar-nightrun-push-issue-njdjly` staat al in de default
branch — merge-commit `139192e` op `claude/hangar-project-setup-kvhcad`,
2026-08-08 11:52 UTC+2, ruim voor deze run. Regel 8 staat dus al in het
`CLAUDE.md` dat elke nachtrun leest. Deze taak is verder geen los te bouwen
stuk werk meer: de Done means beschrijft een gedrag dat nu bij elke run
opnieuw wordt afgedwongen door de instructies zelf, niet iets dat je één keer
"af" maakt met een commit. Deze run is er zelf het bewijs van: subagents
bleken beschikbaar, dus stap b (inline zelf-check) verviel en de echte
`hangar-checker` deed de vijandige check op de `weekly-review-automatic`-diff
(zie `planning/night-log.md`). Het pad zonder subagents (regel 8b) is
geschreven en stond al eerder deze week zelf model voor de fix, maar is
vannacht niet opnieuw getriggerd omdat de tool wél beschikbaar was — dat is
geen gat, alleen niet elke nacht hetzelfde pad bewandelen.

Blijft open, maar is geen taak meer: de onderliggende platformbug (Routines
via de UI krijgen geen `Task`-tool) is niet door een nachtrun te fixen. Als
die zich weer voordoet, vangt regel 8 het op — dat is precies waarvoor hij er
is.
