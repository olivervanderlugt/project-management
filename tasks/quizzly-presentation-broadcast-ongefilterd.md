---
title: "Quizzly: presentation gaat om het spelerfilter heen — regel vastleggen vóór iemand er een privéveld bij zet"
project: quizzly
status: done
added: 2026-08-14
effort: S
branch: claude/dreamy-knuth-n4hya3
---

## Done means

Twee architectuurfeiten die nu alleen in een roadmapdocument staan, staan waar
de volgende bouwer ze tegenkomt, met een test die het bewaakt in plaats van een
zin die het vraagt.

1. **Bij de emit zelf staat waarom `presentation` niet gefilterd wordt.** Een
   comment bij `server/realtime/engine.ts:345` (`presentation: question.presentation`)
   én bij `toPublicPayload()` in `src/lib/question-schema.ts`, dat zegt: alles in
   `presentationSchema` gaat ongefilterd naar élke speler in de room, dus een
   veld dat de speler niet hoort te zien hoort niet in dit schema — of moet
   langs een filter dat er vandaag niet is. Kort, en op beide plekken, want wie
   een veld toevoegt kijkt naar het schema, niet naar de emit.
2. **Een test die faalt als een nieuw `presentation`-veld verplicht wordt.**
   Parse een oud snapshot-object — eentje zonder het nieuwste veld — met
   `presentationSchema` en assert dat het nog steeds parseert. Dat is de test
   die `docs/SLIDE-DESIGNER.md` §6 zelf al voorschrijft voor fase 1; hij hoort
   er te staan vóórdat fase 1 gebouwd wordt, niet erna.
3. Hetzelfde in `docs/ARCHITECTURE.md` in twee zinnen, zodat het niet alleen in
   een slide-designer-roadmap staat die niemand leest als hij aan iets anders
   werkt.

Trio groen. Geen gedragswijziging: dit legt vast wat er al is, het repareert
niets.

## Wat bevestigd is (en wat niet)

Op 2026-08-14 gemeten door de bouwer van `docs/SLIDE-DESIGNER.md` en daarna
**onafhankelijk bevestigd** door een checker die de code zelf afdrukte:

- `toPublicPayload()` wordt precies één keer gebruikt in het realtime-pad, op
  `payload` (`server/realtime/engine.ts:341`). Vier regels lager gaat
  `presentation: question.presentation` (`:345`) ongefilterd in hetzelfde object,
  en `:354` stuurt dat naar de hele room. Het wiretype bevestigt het:
  `src/types/realtime.ts:42` is `presentation: Presentation` — het volle type,
  niet de gestripte `PublicPayload`-variant.
- **Vandaag lekt er niets.** Vóór de emit gaat elk snapshot langs
  `presentationSchema.parse` (`server/realtime/gameServer.ts:149`), en dat schema
  heeft precies vijf velden (`src/lib/theme.ts:441-457`): `layout`, `media`,
  `mediaAlt`, `accentOverride`, `hideTimer`. Allemaal dingen die de speler móét
  zien, en Zod stript onbekende sleutels, dus een auteur kan er ook niets in
  smokkelen. Dit is een latente valkuil, geen actief lek — en het document
  beweert dat ook nergens.
- Een **verplicht** nieuw veld op dat schema laat oude `Game.quizSnapshot`-rijen
  omvallen op regel 149; de `catch` geeft `null` terug en de speler krijgt
  "Game not found." of "That game has finished." Nuance van de checker: er zit
  een in-memory roomcache vóór die parse (`loadRoom`), dus een spel dat al
  draait blijft draaien tot het proces herstart. De pijn komt bij een deploy,
  niet op het moment van mergen.

## Notes

Dit is bijvangst van `quizzly-slide-designer` (quizzly#6). Het staat los van of
die PR gemerged wordt: de feiten gelden nu al.

Waarom het de moeite waard is en niet alleen netjes: Quizzly belooft bij een
blinde groepsquiz dat bijdragers elkaars vragen niet zien. Een pad dat om het
enige spelerfilter heen gaat is precies waar zo'n belofte stukgaat — niet
vandaag, maar op de dag dat iemand een hostnotitie, een hint of een
antwoordtoelichting aan het presentatieschema toevoegt omdat het daar logisch
lijkt te horen.

## Gebouwd en gemerged (2026-08-16, nachtrun)

**quizzly#7, gemerged** (`8bbae69`). Commentaar op beide voorgeschreven plekken
(`server/realtime/engine.ts:345` en `toPublicPayload()` in
`src/lib/question-schema.ts`), plus een derde — niet gevraagd, wel juist — bij
`presentationSchema` zelf in `src/lib/theme.ts`, met de argumentatie dat wie een
veld toevoegt naar het schema kijkt, niet naar de emit. Nieuwe test
`src/lib/theme.test.ts`: parseert een leeg object en een volledig object met
elk veld om de beurt verwijderd, allebei tegen `presentationSchema`. Twee zinnen
in `docs/ARCHITECTURE.md` §2. Trio groen (typecheck/test/build), 106→108 tests.

Eén afwijking van de taakbeschrijving, geen probleem gebleken: `docs/SLIDE-
DESIGNER.md` (waar punt 2 hierboven naar §6 verwijst) bestaat niet op `main` —
alleen op de nog niet gemergede `night/quizzly-slide-designer` (quizzly#6). De
bouwer schreef de test op basis van de taak's eigen omschrijving in plaats van
dat document, en de checker bevestigde dat de test's aanname (herparsen van
`Game.quizSnapshot`-rijen bij room-load) wel degelijk echt in de code zit
(`server/realtime/gameServer.ts:149`) — dus geen gok.

`hangar-checker` deed een eigen negatieve controle: tijdelijk een verplicht
veld (`slideSpecZZZ`) aan `presentationSchema` toegevoegd, beide nieuwe tests
faalden echt (niet alleen typecheck), bestand teruggezet. Verdict: `ship: true`,
niets onvermeld gebleven. CI op de PR groen, direct gemerged (besluit 0004).
