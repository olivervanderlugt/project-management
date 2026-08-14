---
title: Een sessie moet merken dat zijn kloon achterloopt vóór hij werk uitdeelt
project: hangar
status: inbox
added: 2026-08-14
effort: S
branch:
---

## Done means

Nog niet schrijfbaar — eerst moet de vorm gekozen worden. Twee kandidaten:

1. Een `SessionStart`-hook (`command`, dus gratis) die `git fetch` doet en de
   sessie vertelt hoeveel commits hij achterloopt op de default branch. Dat is
   de goedkoopste variant en bindt elke sessie, of hij `CLAUDE.md` nu leest of
   niet — hetzelfde argument als bij de guard en de autosave.
2. `dashboard/build.py` of een klein `scripts/staleness.py` dat het verschil
   tussen lokaal en remote zichtbaar maakt en er hard over klaagt.

Optie 1 is waarschijnlijk het antwoord, maar een hook die bij elke sessiestart
het netwerk op gaat moet stil zijn als er niets aan de hand is, en mag geen
sessie ophouden als GitHub traag is. Dat is de eigenlijke ontwerpvraag.

## Notes

Aanleiding, 2026-08-14: een sessie op Ollie's verzoek las de lokale kloon, zag
vier taken op `ready` staan en stuurde vier agents op ze af. De kloon was van
2026-08-08; de nachtrun had sindsdien zes nachten doorgewerkt en drie van die
vier taken al gebouwd én gemerged (`hangar-prioriteit-score` 08-10,
`weekly-review-automatic` 08-09, `quizzly-media-upload` 08-14). Drie van de vier
agents deden dus werk dat al bestond.

Wat het gevaarlijk maakt: `git status` was de hele tijd schoon. Er is geen
enkel signaal in de werkboom dat je een week achterloopt — je moet ernaar
vragen. En de sessie kwam er alleen achter doordat een `git push` werd geweigerd,
ná drie commits, ná het uitdelen van het werk.

Deels al gemitigeerd: `CLAUDE.md` heeft nu een sectie "Before you trust this
working tree", en de nachtrun-startprompt begint met fetchen. Dat is een regel
die je moet lezen en onthouden; dit taakje gaat over de controle die vanzelf
gaat.

Kosten van het niet oplossen: dubbel werk (drie agents deze keer), en erger —
een sessie die op stale gegevens een taak van `done` terug naar `doing` zet, of
een besluitnummer opnieuw uitgeeft. Dat laatste gebeurde ook: er stonden even
twee `decisions/0004`-bestanden.
