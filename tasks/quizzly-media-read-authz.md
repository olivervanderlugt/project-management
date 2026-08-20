---
title: "Quizzly media: de leesroute krijgt authz — sessiegebonden tot een spel loopt"
project: quizzly
status: ready
added: 2026-08-14
effort: M
branch:
---

## Done means

`GET /api/media/[key]` (`src/app/api/media/[key]/route.ts`) serveert een
afbeelding die bij een **niet-gepubliceerde** quiz hoort alleen aan iemand die er
recht op heeft, en blijft publiek zodra er een spel mee loopt.

1. **Eigenaar mag altijd.** Een ingelogde gebruiker die de quiz bezit waar de
   sleutel bij hoort, krijgt de bytes. Zelfde route als de schrijfkant:
   `getCurrentUser` / `requireUser` + `ownedQuiz` (`src/app/actions/quiz.ts:164-178`).
2. **Speler in een lopend spel mag.** Een anonieme speler in een actief spel met
   die quiz krijgt de bytes.
3. **Verder niemand.** Een sleutel die bij een quiz hoort zonder lopend spel en
   zonder ingelogde eigenaar levert **404**, niet 403 — dezelfde vorm die de
   schrijfroute al kiest (`route.ts:70-77`), zodat het bestaan van een sleutel
   niet lekt.
4. **Een sleutel die nergens meer bij hoort levert 404.** Vandaag krijg je hem
   nog gewoon te zien, ook nadat de afbeelding uit de vraag is gehaald — dat is
   de klacht die deze taak opent.
5. De redenering in de route-header en in `SECURITY.md` wordt herschreven naar
   wat er dan wél geldt. Laat de oude alinea niet staan: die verantwoordt
   precies het gedrag dat je weghaalt.
6. Tests dekken alle vier de gevallen hierboven, plus een negatieve controle:
   draai de authz-check er tijdelijk uit en bewijs dat de nieuwe tests écht
   falen. Zet hem terug.
7. `npm run typecheck && npm test && npm run build` groen.

**Twee dingen die je moet weten vóór je begint, allebei zelf nagekeken op
2026-08-20 — verifieer ze opnieuw, ze kunnen gedrift zijn:**

- **Er is al een spelertoken.** `addPlayer()` geeft
  `{ ok: true, playerId, token }` terug met `randomBytes(24).toString("base64url")`
  (`server/realtime/engine.ts:174-220`), en `resumePlayer(playerId, token)`
  valideert hem (`:224`). Je hoeft er dus geen te verzinnen.
- **Maar hij staat alleen in het geheugen van het realtime-proces.** Het zit in
  de `this.players`-Map, niet in de database — het Prisma-model `Player` heeft
  geen tokenkolom. De Next-routehandler draait in een ánder proces en kan die
  Map niet lezen. Dát is het echte werk in deze taak, en het is de reden dat hij
  `M` is en niet `S`.

Twee vormen die allebei werken; kies er één en verantwoord de keuze in de PR:
een kortlevend HMAC-getekend leestoken over `SESSION_SECRET` (`src/lib/env.ts:31`,
beide processen lezen dezelfde env, dus er is geen gedeelde staat nodig), of het
spelertoken alsnog persisteren. De eerste is goedkoper en lekt niets naar de
database; de tweede is simpeler te volgen. Blijkt onderweg dat geen van beide
past, splits dan en leg uit waarom in plaats van door te bouwen.

Om van een sleutel naar zijn quiz te komen heb je dezelfde query als
`quizzly-media-orphan-cleanup`: `Quiz.coverImage` plus `Question.presentation.media`
(JSON-kolom), gefilterd met `isUploadedMediaPath()` (`src/lib/media/ref.ts:69-71`)
en ontdaan van `MEDIA_URL_PREFIX` (`ref.ts:13`). Loopt die taak eerst, hergebruik
dan wat daar staat in plaats van het twee keer te schrijven.

Let op de caching-header: `public, max-age=31536000, immutable` mag niet blijven
staan op een antwoord dat per kijker verschilt.

## Notes

Gevonden op 2026-08-14 door de agent die `quizzly-media-upload` kwam bouwen en
merkte dat de nachtrun hem de nacht ervoor al gebouwd had (PR #3, gemerged).
Elf van de twaalf regels gehaald; deze niet.

De schrijfroute is volledig dicht — `src/app/api/media/route.ts:42` (Origin vs
`APP_ORIGIN`), `:46` `getCurrentUser`, `:56` rate limit per gebruiker, `:70-77`
`quiz.ownerId !== user.id → 404`. Alleen de leesroute niet, en dat was een
bewuste keuze met een opgeschreven reden: spelers zijn anoniem en moeten de
afbeelding midden in een spel kunnen zien, en de URL-plak-route die dit vervangt
had ook geen leesauth. De sleutel is 128 bits random.

**Besluit van Ollie, 2026-08-20: optie 2.** Niet zo laten. Voor een blinde
groepsquiz — waar het hele punt is dat bijdragers elkaars vragen niet zien — is
"wie de link heeft ziet hem, ook nadat hij verwijderd is" niet goed genoeg. De
capability-URL blijft wel het mechanisme zodra een spel loopt; hij wordt alleen
niet langer het enige.

Op 2026-08-15 is "opruimen bij verwijderen" hier afgesplitst naar
`quizzly-media-orphan-cleanup`, dat onafhankelijk van dit besluit al `ready`
stond. Die taak blijft los; hij verwijdert bestanden, deze bewaakt ze.
