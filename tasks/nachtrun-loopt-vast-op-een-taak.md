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

## Aangescherpt 2026-08-29 (nachtrun, stap 3)

**Vraag 2 is al beantwoord — door dezelfde sessie die dit bestand schreef, een
paar uur later.** Om 2026-08-20 15:49 UTC splitste `hangar-stale-clone-guard`
zichzelf: het onderzoek eruit als `hangar-sessionstart-hook-gedrag` (`ready`),
de bouwtaak op `blocked` tot dat antwoord er ligt. Dat besluit stond zelf 8
nachten onzichtbaar (zie `hangar-daysession-branches-onzichtbaar.md`, vanavond
teruggehaald) — precies het patroon dat vraag 1 hieronder beschrijft, alleen
dan op een besluit in plaats van op een taak die blijft falen. Vraag 2 is dus
mechanisch beantwoord, maar bewijst tegelijk dat "iemand beslist iets" niet
hetzelfde is als "de volgende nacht ziet het".

**Vraag 3, opnieuw gecontroleerd:** van de twee weesbranches is er nog maar één
écht wees. `origin/claude/night-hangar-stale-clone-guard` is niet langer een
loshangende branch — hij is de head van `project-management#13`, geopend
2026-08-20, nog open en `blocked` (zie `hangar-stale-clone-guard.md`). De
andere, `origin/night/hangar-stale-clone-guard` (08-15, één commit, alleen een
status-wissel naar `doing`), staat er 14 dagen later nog steeds zonder PR en
zonder dat iemand hem heeft opgeruimd of gebruikt. Nog steeds niet verwijderd
zonder Ollie's woord.

**Vraag 1 blijft volledig open** en is met deze nacht extra onderbouwd: niet
alleen een taak die blijft falen ontbreekt een signaal — een besluit dat wél
genomen is, ontbreekt hetzelfde signaal zodra het op een branch zonder PR
staat. Beide zijn vormen van "niemand merkt dat de toestand veranderd is
tenzij hij er toevallig naar zoekt". N is nog steeds niet gekozen.

## Herchecked 2026-09-04 (nachtrun, stap 3)

**Vraag 3, opnieuw gecontroleerd via `git ls-remote`:** `origin/night/hangar-
stale-clone-guard` (08-15, `ba1f382`) bestaat nog, ongewijzigd, nu 20 dagen
zonder PR en zonder dat iemand hem heeft opgeruimd. `origin/claude/night-
hangar-stale-clone-guard` is nog steeds gewoon de head van `project-
management#13` (`blocked`, ongewijzigd sinds 08-20) — geen wees. Geen van
beide aangeraakt.

**Een tweede, nieuwe vorm van hetzelfde patroon, deze keer niet op een taak die
faalt maar op een taak die nooit kán slagen.** `pi-openclaw-gateway` is de
oudste `ready` taak op het bord (`added: 2026-08-07`) — ouder dan
`hangar-sessionstart-hook-gedrag` (08-20), de taak die nodig is om
`hangar-stale-clone-guard` te ontgrendelen. Regel 1 zegt "oudste `ready`
eerst", maar `pi-openclaw-gateway` zegt letterlijk in zichzelf: "dit is fysiek
werk bij Ollie thuis... de nachtrun kan hier niets bouwen en moet deze taak
laten liggen." Zodra de drie-vastgelopen-PR's-grens ooit weer onder de drie
zakt, kiest regel 1 mechanisch een taak die per definitie nooit `done` kan
worden — en niets in de regels zegt of de nacht die dan moet overslaan naar de
eerstvolgende `ready` taak, of dat hij telt als "vandaag is er niets
gebouwd". Zonder een expliciete skip-regel kost dat elke keer opnieuw een hele
stap-2-poging om te ontdekken wat dit bestand al zelf meldt. Dit is dezelfde
onderliggende bug als vraag 1 (geen signaal dat "deze taak gaat het nooit
worden op de manier die regel 1 aanneemt"), alleen ligt de oorzaak nu niet bij
falen maar bij een taaksoort die de nachtrun structureel niet kan afronden.
Niet zelf opgelost — dit voegt een derde deelvraag toe aan wat Ollie al moest
beslissen:

4. Slaat "oudste `ready` eerst" een taak over die zichzelf markeert als
   niet-bouwbaar door de nachtrun (zoals `pi-openclaw-gateway`), of blijft hij
   daar elke nacht opnieuw op stuklopen zodra de PR-grens het toelaat?

(Vanavond zelf geen taak gebouwd — drie vastgelopen nachtrun-PR's, zie de
night-log van 2026-09-04. Deze taak dus sowieso niet aan de beurt, ongeacht
regel 1.)
