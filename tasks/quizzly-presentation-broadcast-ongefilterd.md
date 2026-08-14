---
title: "Quizzly: gaat Question.presentation ongefilterd naar de speler?"
project: quizzly
status: inbox
added: 2026-08-14
effort: S
branch:
---

## Done means

Nog niet schrijfbaar: eerst moet de bewering bevestigd zijn, en daarna is het
antwoord waarschijnlijk "opschrijven", niet "repareren".

## Wat er beweerd wordt

De agent die op 2026-08-14 `docs/SLIDE-DESIGNER.md` schreef (quizzly#6) zegt
twee dingen te hebben gevonden die inggaan tegen wat de taakomschrijving zelf
als waar aannam. Beide zijn gemeten met een wegwerp-probe (`npx tsx`), niet
beredeneerd — maar op het moment van dit schrijven nog niet door een tweede
agent geverifieerd, want die checker viel om op een API-fout. **Behandel dit als
een bewering, niet als een feit, tot dat rond is.**

1. **`toPublicPayload()` is niet de enige weg naar de speler.**
   `src/lib/question-schema.ts` filtert wat een speler van een vraag ziet, maar
   `presentation` zou daar helemaal niet doorheen gaan — het wordt ongefilterd
   meegestuurd. Als dat klopt, is de vraag: staat er ooit iets in `presentation`
   dat een speler niet hoort te zien? Vandaag zijn dat `layout`, `media`,
   `mediaAlt`, `accentOverride` en `hideTimer` — allemaal onschuldig, en de
   speler moet ze grotendeels zien ook. Dus waarschijnlijk geen lek vandaag,
   maar wel een latente valkuil: wie er morgen een veld bij zet dat wél privé is
   (een hostnotitie, een hint, een antwoordtoelichting), lekt het zonder dat
   iets hem tegenhoudt.
2. **Een verplicht nieuw veld op het presentation-schema sloopt elk lopend
   spel.** Live games draaien van `Game.quizSnapshot`; oude snapshots missen het
   nieuwe veld en zouden niet meer parsen. Een nieuw veld moet dus optioneel
   zijn, met een test die bewijst dat een oude snapshot nog parseert.

## Waarom dit een eigen taak is

De slide-designer-taak leverde een document op; dit zijn twee
architectuurfeiten die dat document gebruikt en die groter zijn dan dat
document. Punt 1 hoort in `docs/ARCHITECTURE.md` of als commentaar bij
`toPublicPayload()` te staan, zodat de volgende die een veld toevoegt het ziet.
Punt 2 hoort een test te zijn, niet een zin in een roadmap.

En het raakt een belofte die Quizzly expliciet maakt: bij een blinde groepsquiz
mogen bijdragers elkaars vragen niet zien. Een pad dat om het filter heen gaat
is precies waar zo'n belofte stukgaat.

## Eerst dit

Bevestig of ontken punt 1 tegen de echte code (`toPublicPayload()`, de
socket-broadcast in de gameserver, `Game.quizSnapshot`). Klopt het niet, dan kan
deze taak weg — en dan moet `docs/SLIDE-DESIGNER.md` gecorrigeerd worden, want
dan staat er een onjuist architectuurfeit in.
