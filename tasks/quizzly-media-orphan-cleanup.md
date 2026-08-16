---
title: "Quizzly media: opruimen wat geen vraag/quiz meer aanwijst"
project: quizzly
status: ready
added: 2026-08-15
effort: M
branch:
---

## Done means

Een los te draaien opschoon-commando (geen deploy, geen cron nodig om deze
taak af te ronden — dat document je alleen) dat een geüpload
bestand in `MEDIA_UPLOAD_DIR` verwijdert zodra geen enkele `Quiz.coverImage`
of `Question.presentation.media` er meer naar verwijst.

1. **`scripts/gc-media.ts`** (of `src/scripts/...`, wat bij de bestaande
   project-conventie past — er is nog geen `scripts/` map in de repo, kijk
   hoe `db:seed`/`db:studio` als npm-commando's zijn aangehaakt in
   `package.json` en doe hetzelfde patroon):
   - Query alle `Quiz.coverImage`- en `Question.presentation.media`-waarden
     via Prisma (het tweede is een JSON-kolom — `presentation` — dus het veld
     `media` moet uit die JSON gehaald worden, niet uit een losse kolom).
   - Filter met `isUploadedMediaPath()` (`src/lib/media/ref.ts:69-71`) —
     alleen zelf-gehoste referenties tellen mee; een extern geplakte URL wijst
     nooit naar `MEDIA_UPLOAD_DIR` en moet genegeerd worden.
   - Haal per gevonden referentie de sleutel eruit (strip `MEDIA_URL_PREFIX`,
     `src/lib/media/ref.ts:13`) — dat is de verzameling "in gebruik".
   - Loop alle bestanden onder `mediaRoot()` (`src/lib/media/storage.ts:26`,
     twee-teken-fanout-mappen, zie de fanout-comment op regel 39-41) en
     vergelijk tegen de in-gebruik-verzameling.
   - **Dry-run is het default gedrag**: print welke bestanden verwijderd zouden
     worden (pad + hoeveel), verwijder niets. Pas bij een expliciete
     `--delete`-vlag echt verwijderen.
   - **Veiligheidsgrens**: weiger te verwijderen (ook met `--delete`) als dat
     meer dan 50% van de bestaande bestanden zou wegvegen in één run — dat is
     vrijwel zeker een kapotte query, geen echte opruiming — tenzij een
     tweede, expliciete `--force`-vlag is meegegeven. Print in dat geval
     hoeveel het er zijn en waarom hij weigert.
   - Geen wijziging aan de schrijfpaden zelf (`setCoverImageAction`,
     de question-save action rond `src/app/actions/quiz.ts:425-437`) — dit is
     bewust een losse, periodieke opschoonstap, geen delete-on-write. Delete-
     on-write is een makkelijke manier om een bestand te slopen dat toevallig
     nog ergens anders naar verwijst (een auteur kan in theorie dezelfde
     upload-URL in twee vragen plakken), dus dat hoort hier niet bij.
2. **Test** (`src/lib/media/gc.test.ts` of naast het script, in de stijl van
   `src/lib/media/storage.test.ts` — tijdelijke map via `mkdtemp`, geen echte
   DB-connectie nodig als de query-laag mockbaar is; anders: een pglite
   testdatabase zoals de rest van de suite al gebruikt):
   - een bestand dat door geen enkele quiz/vraag wordt aangewezen → verwijderd
     bij `--delete`, blijft staan bij dry-run.
   - een bestand dat wél door `Quiz.coverImage` wordt aangewezen → blijft
     staan.
   - een bestand dat wél door een `Question.presentation.media` wordt
     aangewezen → blijft staan.
   - een externe (hotlinked) URL in `presentation.media` → genegeerd, telt
     niet mee als "in gebruik" en veroorzaakt geen bestandstoegang buiten
     `mediaRoot()`.
   - de 50%-veiligheidsgrens: een situatie waarin bijna alles "ongebruikt"
     lijkt → geweigerd zonder `--force`, wél uitgevoerd mét.
3. **Documentatie**: één alinea in `docs/DEPLOYMENT.md` (zelfhostende
   operators lezen dat) die het commando noemt en aanraadt het periodiek te
   draaien (bijv. maandelijks, via de cron van hun keuze) — geen cron zelf
   instellen, dat is deploy-gebied en niet iets een taak in deze repo doet.
4. `npm run typecheck && npm test && npm run build` groen.

## Notes

Afgesplitst op 2026-08-15 (nachtrun, stap 3) van `quizzly-media-read-authz`.
Dat taak's punt 3 ("Opruimen bij verwijderen") is onafhankelijk van de
authz-vraag (punten 1/2 daar) — "ongeacht 1 of 2", zoals de taak zelf al
zei — en had dus al een concrete finish line kunnen krijgen. De authz-vraag
zelf (moet de leesroute session-gebonden worden?) blijft een smaakbesluit
voor Ollie en staat verder in `quizzly-media-read-authz`.

Geverifieerd tegen de echte code op `origin/main` (niet aangenomen):
`readMedia`/`storeMedia`/`mediaRoot`/`resolveKey` in
`src/lib/media/storage.ts` — er bestaat vandaag geen `deleteMedia` of enige
opschoonroute. `Quiz.coverImage` is een losse `String?`-kolom
(`prisma/schema.prisma:91`); `Question.presentation` is een JSON-kolom
(`prisma/schema.prisma:153`) waar `media` een van de velden in is
(`src/lib/theme.ts:441-457`, `presentationSchema`). Beide accepteren via
`mediaReferenceSchema` (`src/lib/media/ref.ts:93-99`) óf een uploadpad óf een
externe URL — vandaar de `isUploadedMediaPath`-filter, anders probeert de GC
een externe hostname als lokale sleutel te lezen.

Niet onderzocht (voor de bouwer): of quiz/vraag-verwijdering zelf al cascadeert
in de DB (het schema heeft `onDelete: Cascade` op de relaties,
`prisma/schema.prisma:87`) — dat ruimt de DB-rij op, niet het bestand op disk,
dus die weesbestanden vallen ook onder deze GC, geen aparte hook nodig op de
delete-actions.
