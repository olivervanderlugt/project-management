---
title: Quizzly: slide-designer — verkenning en gefaseerde roadmap
project: quizzly
status: blocked
added: 2026-08-08
effort: M
branch: night/quizzly-slide-designer
---

## Done means

`docs/SLIDE-DESIGNER.md` bestaat in de Quizzly-repo en dekt, getoetst aan de
ECHTE architectuur (niet aannames):

- **Mogelijkhedenruimte**: per-slide achtergrond/design, emoji, GIF's,
  stickers, geluiden/muziek per vraag, transitions tussen vragen, een
  soundboard voor de host tijdens het spel, en een interactieve live
  slide-preview terwijl de host bouwt.
- **Technische haalbaarheid per item**, expliciet getoetst aan wat er nu al
  staat: theming is vandaag één `Theme` (`src/lib/theme.ts`) per `Quiz`-rij,
  niet per `Question` — "per-slide design" is dus een echte schema-uitbreiding
  (`Question.payload` of een nieuw veld), geen los feature bovenop iets dat al
  bestaat. Live games draaien van `Game.quizSnapshot`
  (CLAUDE.md-invariant: nooit de live quiz-rij) — elke per-slide-wijziging
  moet door die snapshot-copy heen werken zonder het "editen tijdens een
  lopend spel raakt het spel niet"-contract te breken. `toPublicPayload()` in
  `src/lib/question-schema.ts` is de enige weg naar de speler — nieuwe
  media-velden moeten daar expliciet doorheen, anders lekt er niets (onschuldig
  maar kapot) of ontbreekt er iets.
- **Licentie- en privacyhaken**: GIPHY-gebruiksvoorwaarden (attributie,
  rate-limits, contentfilter — relevant omdat Quizzly ook door minderjarigen
  gebruikt wordt), muziekrechten voor een soundboard (geen simpele upload van
  willekeurige mp3's), en hoe dit past bij `docs/LEGAL.md` — dat document
  noemt vandaag geen enkel stuk media van derden, dus dit voegt een nieuw
  juridisch oppervlak toe, geen uitbreiding van een bestaand punt.
- **Gefaseerde roadmap** met een concrete, in één sessie bouwbare fase 1 (bijv.
  emoji + een klein vast palet aan achtergronden per vraag, zonder externe
  API's of uploads — het laagste-risico eerste stukje) en latere fases
  duidelijk gemarkeerd als afhankelijk van een keuze van Ollie (welke
  media-provider, welk maandbudget, welk risiconiveau qua licenties).
- Eindigt met **één aanbevolen fase 1**, maar past niets toe: geen
  `src/`-wijziging, geen dependency toegevoegd. Dit is onderzoek en een
  document, geen bouw van de feature zelf.

## Notes

Gevraagd door Ollie op 2026-08-08 ("later ... more design features where you
can do it yourself"). Oorspronkelijk één te grote visietaak; gesplitst in de
nacht van 2026-08-12 naar hetzelfde patroon als `quizzly-design-pass`: een
onderzoeksfase (deze taak, nu wel bouwbaar) en een toepassingsfase
(`quizzly-slide-designer-bouwen`, blijft `inbox` tot Ollie een fase kiest uit
de roadmap die deze taak oplevert).

## Waar het staat (2026-08-14)

Gebouwd en adversarieel gecheckt. **quizzly#6** staat open en wacht op Ollie's
merge. Eén bestand: `docs/SLIDE-DESIGNER.md`, 922 regels, 0 verwijderingen.
Niets in `src/`, geen dependency, geen migratie, en de wegwerp-probe is niet
meegecommit — de checker heeft dat apart geverifieerd met `gh pr view 6 --json
files` en `git diff --stat`.

Trio groen vanaf een schone kloon: typecheck zonder diagnostics, 106 tests in 8
bestanden, build compleet.

**Het interessante:** de taak stelde twee dingen als waar die niet waar bleken.
De bouwer heeft ze gemeten in plaats van overgeschreven, en de checker heeft
beide onafhankelijk bevestigd — zie de aparte taak
`quizzly-presentation-broadcast-ongefilterd`.

De checker heeft elke `file:line`-verwijzing in het document zelf afgedrukt en
vergeleken. Vijf zaten er in de eerste versie één regel naast en waren al
gecorrigeerd vóór de commit. Ook nagekeken: het document beweert nergens een
GIPHY-licentievoorwaarde die het niet heeft kunnen lezen — elke
`support.giphy.com`-URL gaf 403, en dat staat er zo in, met vijf concrete dingen
om na te vragen in plaats van een verzonnen samenvatting.

Eén kanttekening van de checker, geen fout: het document is 922 regels tegen
`docs/DESIGN.md`'s 612. Te rechtvaardigen door de scope (negen
haalbaarheidsoordelen, vijf juridische subsecties, vier fases), maar als je hem
korter wilt is dat een redactieklus, geen herbouw.
