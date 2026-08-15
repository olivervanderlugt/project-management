---
title: Quizzly media: de leesroute heeft geen authz — bewust of niet?
project: quizzly
status: inbox
added: 2026-08-14
effort: S
branch:
---

## Done means

Nog niet schrijfbaar: dit is een vraag aan Ollie, geen bug met een duidelijke
fix. Er zijn twee eerlijke uitkomsten en alleen hij kiest welke:

1. **Zo laten en het opschrijven.** De capability-URL is het ontwerp; leg vast
   dat een geüploade afbeelding zo publiek is als de link die hem draagt.
2. **Sessie-gebonden lezen** voor afbeeldingen die bij een niet-gepubliceerde
   quiz horen, en publiek zodra een spel loopt. Duurder: spelers zijn anoniem
   en hebben midden in een spel geen sessie, dus dit vraagt een spel-token.

(Voorheen stond hier ook "opruimen bij verwijderen" als derde punt. Dat is
op 2026-08-15 afgesplitst naar `quizzly-media-orphan-cleanup` — onafhankelijk
van welke van de twee bovenstaande opties wint, en had dus al een concrete
finish line. Zie die taak.)

## Notes

Gevonden op 2026-08-14 door de agent die `quizzly-media-upload` kwam bouwen,
merkte dat de nachtrun hem de nacht ervoor al gebouwd had (PR #3, gemerged), en
de finish line toen maar tegen de gemergede code aan hield in plaats van niets
te doen. Elf van de twaalf regels gehaald; deze niet.

Precies: de schrijfroute is volledig dicht — `src/app/api/media/route.ts:42`
(Origin vs `APP_ORIGIN`), `:46` `getCurrentUser`, `:70-77` `quiz.ownerId !==
user.id → 404`, `:56` rate limit per gebruiker; en `setCoverImageAction`
(`src/app/actions/quiz.ts:164-178`) draait op `requireUser` + `ownedQuiz`.

Maar `GET /api/media/[key]` heeft géén authz. Dat is een bewuste keuze met een
opgeschreven reden — spelers zijn anoniem en moeten de afbeelding midden in een
spel kunnen zien, en de URL-plak-route die dit vervangt had ook geen leesauth —
en de sleutel is 128 bits random. De taak zei alleen "alleen door de
quiz-eigenaar", en dat is dit niet, dus de agent heeft hem niet afgevinkt in
plaats van de regel naar de code toe te schrijven. Terecht.

Gevolg zoals het nu staat: wie de link heeft, ziet de afbeelding — ook nadat
die uit de vraag is gehaald. Voor een blinde groepsquiz, waar het hele punt is
dat bijdragers elkaars vragen niet zien, is dat het waard om hardop te
beslissen in plaats van het te laten staan omdat het in een commentaarblok
verantwoord is.

Rationale staat in de route-header en in `SECURITY.md` van de Quizzly-repo.

**Herchecked 2026-08-15 (nachtrun, stap 3).** De authz-keuze (1 vs 2) blijft
een smaakbesluit dat alleen Ollie kan maken — geen nieuwe informatie sinds
2026-08-14 die dat verandert. Blijft `inbox` met de vraag hierboven open.
