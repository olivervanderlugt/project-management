---
title: De nachtrun blijft elke nacht dezelfde taak kiezen en haalt de bouwstap nooit
project: hangar
status: inbox
added: 2026-08-20
effort: M
branch:
---

## Wat er aan de hand is

Drie nachten (08-15, 08-17, 08-18) hebben alle drie `hangar-stale-clone-guard`
gekozen, hun startcommit gepusht, en zijn daarna gestopt vóór er één regel code
was. Twee nachten (08-19, 08-20) hebben helemaal niets achtergelaten — geen
commit op welke branch dan ook, terwijl de Routine wél gevuurd heeft
(`last_fired_at` 2026-08-20T00:05:53Z).

De weesbranches zijn er nog:

- `origin/night/hangar-stale-clone-guard` — 08-15, één commit
- `origin/claude/night-hangar-stale-clone-guard` — 08-17 + 08-18, twee commits

Beide zetten alleen `tasks/hangar-stale-clone-guard.md` op `doing` en schrijven
een night-log-blok. Geen PR, geen code.

## Waarom het zichzelf herhaalt

Regel 1 is oudste-`ready`-eerst. `hangar-stale-clone-guard` is `added:
2026-08-14`, de enige andere `ready` taak is `added: 2026-08-15`. De oudste
verandert niet door te falen — dus elke volgende nacht kiest dezelfde taak
opnieuw, komt even ver, en stopt. Er is geen mechanisme dat merkt dat een taak
al drie keer een nacht heeft opgegeten.

Daar komt bij dat de taak `effort: S` draagt maar een finish line heeft van een
nieuw script, een hook in `.claude/settings.json`, een testsuite met vijf
gevallen, én een voorwaarde vooraf ("verifieer eerst empirisch met een
wegwerp-hook hoe `SessionStart` zich gedraagt") die zelf onderzoek is. Dat is
geen S.

## Wat Ollie moet beslissen

1. Een faalteller per taak: na N nachten zonder diff gaat de taak op `blocked`
   met de reden erin, zodat de volgende nacht doorschuift. N = ?
2. Of `hangar-stale-clone-guard` opsplitsen (eerst het hook-gedrag uitzoeken als
   losse taak, dan pas bouwen) — dan lost hij zichzelf op zonder regelwijziging.
3. Wat er met de twee weesbranches moet gebeuren (niet verwijderen zonder jouw
   woord — de guard staat dat ook niet toe).

## Notes

Gevonden 2026-08-20 in een sessie die alleen de status opvroeg. Niets aan de
werkboom liet dit zien: de taak staat op de default branch gewoon op `ready`,
want de `doing`-commits zijn nooit gemerged.
