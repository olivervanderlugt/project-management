---
title: Quizzly: slide-designer — verkenning en gefaseerde roadmap
project: quizzly
status: doing
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
