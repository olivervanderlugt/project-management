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

## Herchecked 2026-09-17 (nachtrun, stap 3)

Gekozen als oudste nog niet recent herverifieerde inbox-taak (laatst
aangescherpt 09-04, 13 nachten geleden — elke andere inbox-taak is binnen de
laatste acht nachten gecheckt).

Alle drie openstaande vragen opnieuw gecontroleerd, geen van drieën
veranderd:

- **Vraag 3 (weesbranch):** `origin/night/hangar-stale-clone-guard` bestaat
  nog, ongewijzigd (`ba1f382`, via `git ls-remote`), nu 33 dagen zonder PR.
  Niet aangeraakt.
- **Vraag 2 (opsplitsen):** nog steeds mechanisch gedaan (de 08-20-split
  staat op de default sinds de 08-29-recovery), maar `reference/sessionstart-
  hooks.md` — het document waarvan `hangar-stale-clone-guard`'s finish line
  zegt dat het moet bestaan vóór die taak weer `ready` wordt — bestaat nog
  steeds niet. `hangar-sessionstart-hook-gedrag` staat nog gewoon `ready`,
  ongebouwd.
- **Vraag 4 (pi-openclaw-gateway als nooit-bouwbare oudste taak):**
  `pi-openclaw-gateway` is nog steeds de oudste `ready` taak op het bord
  (`added: 2026-08-07`, ouder dan elke andere `ready` taak). De vraag blijft
  theoretisch zolang de drie-PR-grens dit blijft overslaan, maar is dat
  vanavond niet — zie de night-log-entry van vandaag.

**Groter dan deze taak, dit zelf niet oplossend:** dezelfde branchronde
vanavond (zie `hangar-pr-plafond-kwijt.md`, hieronder herverifieerd) bevestigt
dat de reden waarom regel 1 al 27 nachten op rij nooit bij `pi-openclaw-
gateway` uitkomt dezelfde is als de reden waarom deze taak zelf bestaat: een
al door Ollie geaccepteerd besluit dat het platte drie-PR-plafond had moeten
vervangen, ligt sinds 2026-08-11 onaangeraakt op een branch zonder PR. Vraag 1
hierboven ("een faalteller per taak") en dat besluit lossen een verschillend
deel van hetzelfde onderliggende gebrek op (geen signaal dat een regel niet
doet wat hij zou moeten). Geen van beide vanavond zelf doorgevoerd — allebei
raken regel 5/1, expliciet Ollie's beslissing.

## Herchecked 2026-09-25 (nachtrun, stap 3)

Gekozen als oudste nog niet recent herverifieerde inbox-taak (laatst
aangescherpt 09-17, acht nachten geleden — elke andere inbox-taak is binnen de
laatste zeven nachten gecheckt: `hangar-daysession-branches-onzichtbaar`
09-19, `quizzly-legal-review-west` 09-20, `hangar-in-de-browser` 09-21,
`hangar-pr-plafond-kwijt` 09-22, `hangar-wrapup-pr-pileup` 09-23,
`quizzly-slide-designer-bouwen` 09-24).

Alle vier openstaande vragen opnieuw gecontroleerd, geen van vieren
veranderd:

- **Vraag 1 (faalteller per taak):** nog steeds geen antwoord van Ollie.
- **Vraag 2 (opsplitsen):** de 08-20-split staat nog op de default. Maar
  `reference/sessionstart-hooks.md` — het document dat van de finish line van
  `hangar-stale-clone-guard` moet bestaan vóór die taak weer `ready` wordt —
  bestaat nog steeds niet (`ls` op de verste keten: geen bestand).
  `hangar-sessionstart-hook-gedrag` staat nog gewoon `ready`, ongebouwd.
- **Vraag 3 (weesbranch):** `origin/night/hangar-stale-clone-guard` bestaat
  nog, ongewijzigd (`ba1f382`, via `git ls-remote`), nu 41 dagen zonder PR.
  Niet aangeraakt.
- **Vraag 4 (`pi-openclaw-gateway` als nooit-bouwbare oudste taak):** nog
  steeds de oudste `ready` taak op het bord (`added: 2026-08-07`), nog steeds
  theoretisch zolang de drie-PR-grens dit blijft overslaan — en dat is
  vanavond weer het geval, zie de night-log van vandaag.

Geen nieuwe feiten sinds 09-17: dit blijft `inbox`, wachtend op Ollie's
antwoord op de vier vragen. Niet zelf doorgevoerd — allebei raken regel 1/5,
expliciet Ollie's beslissing.
