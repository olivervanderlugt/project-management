---
title: Quizzly: compliance-review westerse landen (EU/VK/VS/CA/AU)
project: quizzly
status: inbox
added: 2026-08-08
effort: M
branch:
---

## Done means

Nog aan te scherpen na merge van PR #1, dat al een deel dekt (GDPR-export,
age gate, retentie). Beoogd resultaat: docs/COMPLIANCE-REVIEW.md dat de echte
dataflows in de code (niet alleen de docs) toetst aan GDPR incl. kinderen, UK
GDPR, COPPA, CCPA/CPRA, PIPEDA en de Australische Privacy Act — per punt
gedekt/ontbreekt/besluit-van-Ollie-nodig, gemarkeerd must/should/could, met de
expliciete disclaimer dat dit geen juridisch advies is.

## Notes

docs/LEGAL.md bestaat al en noemt ook het patentrisico in deze productcategorie.
De legal-pagina's hebben nog [BRACKETED] placeholders — die vullen kan alleen
Ollie (echte contactgegevens).

**Herchecked 2026-08-13:** `quizzly#1` staat nog open, niet gemerged — dus de
blokkade geldt onveranderd. Blijft `inbox`. `quizzly#1` bevat naast de
GDPR-export/age-gate/retentie ook een versiebump naar 1.0.0 en deploy-config
(`fly.toml`), dus dat is sowieso geen taak die een nachtrun zelf mag mergen
(regel 6, "nooit iets deployen of aanzetten dat geld kost") — die PR wacht op
Ollie's launch-besluit, niet op onderzoek. Vraag voor Ollie: wanneer wil je
`quizzly#1` mergen, zodat deze taak daarna pas echt aan te scherpen is?

**Herchecked 2026-08-22 (nachtrun, stap 3) — nu écht met de `quizzly#1`-diff
gelezen, niet alleen de titel.** `quizzly#1` staat nog open en ongewijzigd
sinds 08-13 (nog steeds `main`+versiebump+`fly.toml`, nog steeds Ollie's
launch-besluit, geen onderzoeksvraag). Nieuw is wat de PR concreet toevoegt —
gelezen uit `origin/claude/quizzly-finalization`, niet aangenomen uit de titel:

- **GDPR Art. 15/20 (access/portability):** `src/app/api/account/export/route.ts`
  — accountrecord + quizzes + hosted-game-historie + eigen collab-bijdragen als
  JSON, bewust zonder andermans spelersnicknames of nog-verborgen vragen van
  andere bijdragers. Plus losstaand `.quizzly.json`-quiz-export/import.
- **Retentie:** `server/retention.ts` — `DATA_RETENTION_DAYS` env-var, dagelijkse
  sweep die `Game`-rijen ouder dan N dagen verwijdert (cascadeert naar players +
  answers). Onbewaakt (env niet gezet) = geen sweep, ongewijzigd t.o.v. nu.
- **Age gate:** `src/components/AuthForm.tsx` — bij signup een checkbox "I'm at
  least 16, or the digital age of consent where I live", **zelfverklaring, niets
  opgeslagen** (geen geboortedatum-veld, dus geen extra persoonsgegeven erbij).
- **Nickname-moderatie** (niet in de oorspronkelijke Done-means genoemd, wel
  relevant voor de kinderen-sectie): `src/lib/nickname.ts`, leetspeak-folding +
  Engelse/Nederlandse blocklist, geen volledig moderatiesysteem.

Dit verandert de aard van de blokkade niet (nog steeds: pas echt te schrijven
zodra deze code op `main` staat), maar scherpt wél aan wát de review, eenmaal
gebouwd, per regime zal moeten zeggen — en legt een gat bloot dat los staat van
`quizzly#1`:

- **GDPR/UK GDPR:** met de PR gemerged grotendeels gedekt (zie boven). Wat
  ontbreekt blijft ontbreken ongeacht de merge: Art. 30-verwerkingsregister,
  DPIA, rectificatie is alleen impliciet (bewerk je eigen content).
- **COPPA (VS, <13):** de leeftijd-checkbox stopt bij 16+ zelfverklaard, dus
  ruimer dan COPPA's 13-jaargrens — maar COPPA vraagt bij "actual knowledge"
  van kinderen *geverifieerde ouderlijke toestemming*, niet zelfverklaring. Voor
  accounthouders is dat waarschijnlijk voldoende omdat er niets wordt
  geverifieerd of gevraagd dat op een kind onder de 13 wijst; voor spelers
  (geen account, alleen een nickname) is er sowieso geen "personal information"
  in COPPA-zin. **Nergens in `docs/LEGAL.md` staat COPPA met naam genoemd** —
  alleen een bronlink. Dat is een écht schrijfgat, los van de PR.
- **CCPA/CPRA (Californië):** waarschijnlijk buiten scope zolang omzet/schaal
  onder de wettelijke drempels blijft (geen "sale/sharing" van data — er wordt
  niets verkocht), maar dat is nu nergens vastgelegd of zelfs maar benoemd.
- **PIPEDA (Canada) en Australian Privacy Act:** geen van beide wordt ergens
  genoemd. Beide zijn consent-/minimalisatie-gebaseerd zoals GDPR, dus het
  ontwerp scoort er waarschijnlijk net zo goed op — maar "waarschijnlijk, nooit
  opgeschreven" is precies het gat dat deze taak moet dichten.

**Blijft `inbox`.** Niet omdat er niets te onderzoeken viel — dat klopt dus niet
meer, zie boven — maar omdat het eindresultaat (`docs/COMPLIANCE-REVIEW.md`
tegen de échte code) pas eerlijk te schrijven is zodra vaststaat welke code dat
is: nu (zonder PR#1) of straks (met). Die keuze is Ollie's merge-moment, niet
een onderzoeksvraag. Vraag voor Ollie ongewijzigd: wanneer merge je
`quizzly#1`? Zodra dat gebeurd is, kan deze taak in één stap naar `ready` — de
per-regime kaart hierboven is dan het startpunt, geen nieuw onderzoek nodig.

## Herchecked 2026-09-03 (nachtrun, stap 3)

Twaalf dagen sinds de vorige check — de langste stilstand van alle inbox-taken,
dus deze keer bewust geen aanname: `quizzly#1` rechtstreeks via de API
opgevraagd (nog steeds `open`, `updated_at` ongewijzigd sinds 2026-08-07) én
`git log --since="2026-08-22" origin/main` op de quizzly-repo gedraaid voor
`docs/LEGAL.md`, `docs/COMPLIANCE-REVIEW.md` en de repo in het geheel — nul
commits. `main` staat nog exact op de merge van PR #7 (2026-08-16); er is ook
geen dagsessie geweest die compliance-content buiten PR#1 om rechtstreeks op
`main` heeft gezet. De blokkade is dus niet alleen ongewijzigd maar ook niet op
een andere weg alsnog opgelost. Blijft `inbox`, zelfde vraag aan Ollie.
