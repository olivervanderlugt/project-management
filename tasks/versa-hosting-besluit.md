---
title: Beslissen waar Versa draait, en hem daar neerzetten
project: versa
status: blocked
added: 2026-08-06
effort: M
branch:
---

## Done means

Nog niet schrijfbaar — daarom `blocked`, niet `inbox` (zie beneden waarom het
die status draagt).

Versa heeft Postgres en Docker nodig, dus hosting kost geld. Welk platform,
welk budget per maand en of de database managed is of niet, is een besluit van
Ollie. Zolang dat er niet ligt, is er geen finish line die iemand anders kan
afvinken.

## Notes

Uit `reference/project-prioritering.md`: Versa scoort het hoogst op CV/LinkedIn
en op tijd-tot-echte-gebruikers, en één werkende URL levert daar het meeste per
uur op. Dat maakt dit de duurste blocker in de hele Hangar.

Vragen die het besluit vormen:

- Wat mag het per maand kosten?
- Managed Postgres of zelf draaien?
- Publiek toegankelijk vanaf dag één, of eerst achter een wachtwoord?

Auteursrecht speelt hier: de repo is bewust opgezet met publiek-domein
zaaicontent en een DMCA-flow. Live gaan met de 1400+ stubs mag niet betekenen
dat er beschermde teksten meelekken — dat controleren hoort bij deze taak.

Niet 's nachts onbewaakt uitvoeren: dit raakt geld en deploys.

**Besluit van Ollie, 2026-08-20: nu niet — geparkeerd.** Versa gaat voorlopig
nergens draaien. `projects/versa.md` staat op `status: parked`, zodat het
project niet elke keer als open blokkade op het bord verschijnt.

Dat is een uitstel, geen afwijzing, en het kost iets: uit
`reference/project-prioritering.md` scoort Versa het hoogst op CV/LinkedIn en op
tijd-tot-echte-gebruikers, en één werkende URL levert daar het meeste per uur op.
Die opbrengst blijft liggen zolang dit geparkeerd staat.

Wat er nog steeds moet gebeuren zodra het weer aangaat: budget per maand,
managed Postgres of zelf draaien, publiek of eerst achter een wachtwoord, en de
auteursrechtcontrole over de 1400+ stubs vóór er iets live gaat. Die vier vragen
staan hierboven ongewijzigd.

**Dit besluit stond 8 nachten onzichtbaar** — genomen 2026-08-20 15:49 UTC op
een dagsessie-branch zonder PR (`claude/hangar-nightrun-status-hsr0iy`),
teruggehaald pas in de nacht van 08-29. Zie
`tasks/hangar-daysession-branches-onzichtbaar.md`.

## Onderzoek (2026-08-21, nachtrun — enkel research, niets uitgevoerd)

**Gedaan vóórdat de parking-beslissing hierboven bekend kon zijn** — de nacht
van 08-21 las nog de stale `inbox`-versie van dit bestand en zocht hosting uit
voor een project dat Ollie een paar uur eerder al had geparkeerd. Niet
weggegooid: het is echt werk en blijft bruikbaar zodra Versa weer aangaat, maar
het antwoordt een vraag die op dat moment al niet meer actueel was.

**Auteursrecht-check afgerond, geen risico gevonden in de repo zelf.**
`PROGRESS.md` (Phase 5) bevestigt: er staan nooit songteksten met copyright in
de repo. De 1400+ "popular-stubs" zijn metadata-only (titel + artiest,
`src/lib/db/popular-stubs.ts`); echte teksten komen pas runtime binnen via de
LRCLIB-connector, in een gitignored lokale DB (`pglite://.data/versa` of een
losse Postgres). Dat matcht CLAUDE.md's eigen regel ("Official APIs + LRCLIB
only. Genius/Spotify never provide lyrics.").

**Wél een scherpere versie van de bestaande vraag, niet een nieuwe:** zodra dit
platform live staat mét `FEATURE_LRCLIB=true`, staan er in de **productie-DB**
(niet de repo) waarschijnlijk wél teksten van nog beschermde nummers — geïmporteerd
via LRCLIB, publiekelijk leesbaar. Dat is geen repo-lek, maar wel een publiceer-besluit:
LRCLIB zelf is een legitieme, door de community aangeleverde bron zonder key, maar
"legitiem om te importeren" is niet hetzelfde als "legaal om zonder claim publiek te tonen".
De huidige `/legal`-pagina (`src/app/legal/page.tsx`) noemt alleen "user-submitted"
content in de takedown-uitleg — de LRCLIB-import-flow (`source=lrclib`, met
attributie) staat er niet expliciet in. Los van dit hosting-besluit de moeite waard om
op te merken, niet iets wat vannacht is aangepast.

**Concrete, actueel opgezochte hosting-opties (prijzen 2026, indicatief — check
zelf vóór je kiest, prijzen schuiven):**

| Optie | App-hosting | Postgres | Geschat totaal/mnd |
| --- | --- | --- | --- |
| **Railway** | usage-based, geen gratis tier meer | zelfde platform, usage-based | ~$10–15 voor een solo-app met DB en worker |
| **Render** | Starter web service $7 (512MB/0.5vCPU, always-on) | Basic managed Postgres vanaf ~$6 + opslag $0.30/GB | ~$21–28, mét een echte gratis tier als je eerst zonder always-on wilt testen |
| **Fly.io** | kleine always-on instance ~$2–5 | zelf draaien op Fly (Docker-compose past hier het best) óf externe managed DB | laagst in totaal, maar het minst "klik en klaar" |
| **Vercel (app) + Neon (DB, managed)** | Vercel hobby is gratis voor niet-commercieel, maar de site is straks publiek en heeft een custom worker (`pnpm worker`) nodig — past niet zuiver op Vercel's serverless model | Neon free tier: 100 CU-uur/mnd, 0.5GB opslag — genoeg om te proberen, te klein voor een groeiende catalogus | Gratis tot een groei-punt, dan opnieuw beslissen |

Versa heeft, naast de webapp en Postgres, ook een losstaand worker-proces nodig
(`pnpm worker` voor de job queue) — dat wil een platform dat een long-running
proces toestaat, niet puur serverless. Dat maakt Vercel als hoofd-hosting minder
voor de hand liggend dan Render/Railway/Fly, tenzij de queue-drain-inline-aanpak
(nu al de PGlite-noodgreep, zie Phase 3 in `PROGRESS.md`) bewust ook voor productie
gekozen wordt.

**De vier vragen aan Ollie, nu met een echt menu erbij — te beantwoorden zodra
Versa van `parked` af komt:**

1. Budget/maand: ergens tussen "$0, Neon/Vercel free tier, groei-plafond
   geaccepteerd" en "~$25, Render met een always-on managed DB"?
2. Managed Postgres (Render/Neon/Supabase — geen eigen back-ups/patches) of
   zelf draaien (Fly + het meegeleverde `docker-compose.yml`, meer controle,
   meer beheer)?
3. Publiek vanaf dag één, of eerst achter een wachtwoord terwijl de LRCLIB-content
   groeit?
4. Nu al gedekt door bovenstaande check, maar waard om expliciet te bevestigen:
   akkoord dat productie straks runtime-geïmporteerde, mogelijk nog-beschermde
   teksten publiek toont via de bestaande takedown-flow (net als de rest van de
   community-content), in plaats van dit te beperken tot alleen de public-domain
   seed?
