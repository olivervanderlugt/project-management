---
title: Claude als e-mailmanager voor alle (~10) adressen — lezen, drafts, spam, afmelden
project: hangar
status: inbox
added: 2026-09-20
effort: L
branch: claude/multi-email-manager-system-ozr70l
---

## Done means

Paraplu. Klaar als `email-0` tot en met `email-4` `done` zijn en besluit 0006
`accepted` is. Bouw begint pas na Ollie's akkoord op het plan hieronder.

## Wat er gevraagd is

Ollie, in zijn woorden: Claude als e-mailmanager voor AL zijn adressen, een stuk
of tien, sommige prominenter dan andere. Op de hoogte zijn van de gesprekken,
drafts opstellen voor nieuwe mails en antwoorden, spam bijhouden, afmelden en
verwijderen. Niet alles kan via een connector of API. Eerst een plan, dan
goedkeuring, dan pas bouwen.

## Zijn antwoorden (2026-09-21)

1. **Providers:** Gmail, Outlook, VU, UvA, mail.com, iCloud ("als het kan").
   Prominent: Gmail en VU.
2. **Scheiding:** voor hem gescheiden; de backend voor Claude mag samengevoegd.
3. **Zonder vragen:** spam in quarantaine (niet direct definitief), afmelden,
   drafts aanmaken. **Verzenden nooit** zonder zijn directe toestemming.
4. **Ritme:** briefing 's ochtends en 's avonds; daartussen doorlopend drafts
   zodra iets binnenkomt, al vóór de briefing.

## Wat nog ontbreekt

De lijst met alle ~10 adressen. De tabel hieronder is per provider; het
profiel is per adres. Zonder de lijst is "elk adres heeft een bron" niet te
controleren. Ollie levert hem bij zijn akkoord.

## Het ontwerp

Besluit `0006` (proposed). Kort, per provider:

| Account  | Bron voor Claude          | Spam opruimen | Draft met juiste afzender |
| -------- | ------------------------- | ------------- | ------------------------- |
| Gmail    | is de hub                 | ja, in bron   | ja                        |
| VU       | M365-connector, direct    | ja, in bron   | ja, in VU Drafts          |
| iCloud   | doorsturen → hub          | alleen in hub | ja (send-as, app-ww)      |
| mail.com | doorsturen/POP → hub      | alleen in hub | ja (send-as, app-ww)      |
| Outlook  | doorsturen → hub          | alleen in hub | nee: tekst om te plakken  |
| UvA      | doorsturen → hub (test)   | alleen in hub | nee: tekst om te plakken  |

Bovenop: één profiel per adres in `email/accounts/`, één skill die de vaste
routine kent (overzicht → drafts → spam → afmelden → log), twee Routines, en
een hook die verzenden structureel blokkeert.

## Wat "goed" is

- Elk adres heeft een werkende bron, of staat expliciet als "kan niet" in zijn
  profiel — nooit stil overgeslagen.
- Elke draft noemt het bronadres en de afzender waarmee hij verstuurd wordt.
- Alles wat Claude deed (quarantaine, afmelding, draft) staat in
  `email/log/YYYY-MM-DD.md`, terug te draaien.
- Geen Routine kan verzenden, ook niet via een `mailto:`-afmelding — dat is
  een hook, geen belofte. In Ollie's eigen sessie is "verstuur <id>" de regel.
- Ollie hoeft alleen nog op verzenden te drukken.

## De deeltaken

- `email-0-toegang-testen` — welke accounts kunnen doorsturen, welke Gmail-
  en M365-tools een Routine echt heeft. Bepaalt de rest. Deels Ollie's werk.
- `email-1-profielen-en-skill` — profielen, skill, verzend-blokkade, tests.
- `email-2-briefing-routine` — 07:30 en 21:30, met push naar zijn telefoon.
- `email-3-doorlopende-verwerking` — elk uur overdag: drafts, quarantaine,
  afmelden, log.
- `email-4-verzenden-met-toestemming` — het enige pad naar "verstuur".

## Check door de hangar-checker (2026-09-21)

Vijf gaten gevonden, verwerkt in 0006 en de deeltaken: afmelden via `mailto:`
is zelf verzenden (nu: alleen one-click/https, mailto wordt een draft); de
hook moet fail-closed zijn op een allowlist, niet op een lijst verzendtools;
een quarantaine-label wordt nooit opgeruimd (nu: Gmail's eigen spam-map);
tien adressen maar zes rijen (nu: lijst is voorwaarde); doorgestuurde mail
belandt in de hub-spam (nu: "nooit naar spam" op elk filter).

## Notes

Stand in deze Code-sessie: de Gmail-connector laat hier alleen `delete_draft`
zien. Zoeken, lezen, drafts maken en verzenden bestaan in claude.ai-chat en in
Routines met de connector erbij, maar de exacte toolnamen zijn hier niet te
zien. Daarom is `email-0` de eerste stap en niet de bouw.
