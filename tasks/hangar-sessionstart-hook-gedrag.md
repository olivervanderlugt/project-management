---
title: Uitzoeken hoe SessionStart-hooks zich echt gedragen, vóór er iets omheen wordt gebouwd
project: hangar
status: ready
added: 2026-08-20
effort: S
branch:
---

## Done means

`reference/sessionstart-hooks.md` bestaat en beantwoordt de vijf vragen
hieronder, elk met het **bewijs erbij** — een commando dat gedraaid is en zijn
uitkomst, of een citaat uit de primaire documentatie met de vindplaats. Niet uit
een websearch, niet uit herinnering. Waar iets niet te verifiëren viel: dat
opschrijven als niet-geverifieerd, niet gladstrijken.

1. Landt `hookSpecificOutput.additionalContext` uit een `SessionStart`-hook echt
   in de sessiecontext? Bewijs: een wegwerp-hook die een unieke, onraadbare
   string uitstoot, en daarna een sessie waarin die string aantoonbaar
   meegelezen is.
2. Wat is de **default** timeout voor een `command`-hook, en overschrijft
   `timeout:` in `.claude/settings.json` die naar boven én naar beneden?
3. Wat gebeurt er bij exit 0 zonder output — stil, zoals `autosave.sh` aanneemt?
4. Wat gebeurt er bij een niet-nul exit uit een `SessionStart`-hook? Blokkeert
   dat de sessie (zoals exit 2 bij `PreToolUse`) of wordt het genegeerd?
5. Op welke gebeurtenissen vuurt `SessionStart` — alleen een verse start, of ook
   resume en clear? Zijn er matchers, en welke?

Sluit af met één verdictregel: **is optie 1 uit `hangar-stale-clone-guard`
(een `SessionStart`-hook) haalbaar, ja of nee.** Is het nee, dan staat erbij wat
het terugvalpad is.

**Geen productiecode.** Geen `scripts/staleness.py`, geen wijziging aan
`.claude/settings.json` die blijft staan. De wegwerp-hook mag tijdelijk in
`.claude/settings.local.json` en gaat er aan het eind weer uit — controleer dat
`git status` schoon is op dat punt.

**Wat een onbewaakte run niet kan, en dat is goed:** vraag 1 vereist een verse
sessie, en een nachtrun ís al een sessie. Kun je het niet zelf aantonen, commit
dan het wegwerp-hookblok als een codeblok in het referentiedocument, met de
exacte string erin, plus één zin: "Ollie: plak dit in `settings.local.json`,
open een sessie, vraag of hij de string ziet, haal het weer weg." Dertig
seconden werk voor hem. Dat telt als af — een eerlijk "dit deel moet jij doen"
is af, doen alsof je het gemeten hebt niet.

## Notes

Losgetrokken uit `hangar-stale-clone-guard` op 2026-08-20, omdat die taak drie
nachten (08-15, 08-17, 08-18) heeft opgegeten zonder één regel code. Zie
`tasks/nachtrun-loopt-vast-op-een-taak.md` voor wat er precies misging.

De reden dat het niet lukte is zichtbaar in de taak zelf: hij droeg `effort: S`
maar begon met "verifieer eerst empirisch hoe `SessionStart` zich gedraagt" —
onderzoek, met een script, een hook en een testsuite van vijf gevallen erachter.
Dat is geen S, en het is niet één taak.

Dit is die eerste helft, en verder niets. `hangar-stale-clone-guard` staat op
`blocked` tot dit antwoord er ligt.

Context die er al is: `.claude/settings.json` draait vandaag `PreToolUse`
(guard), `Stop` en `SessionEnd` (autosave) — allemaal `command`-hooks met een
expliciete `timeout`. `SessionStart` wordt nog nergens gebruikt, dus daar is
geen huisvoorbeeld van in deze repo.
