---
title: E-mail stap 0 — per account testen of de bron werkt, en welke tools een Routine echt heeft
project: hangar
status: inbox
added: 2026-09-21
effort: S
branch:
---

## Done means

`email/accounts/` bevat één bestand per adres (uit `email/accounts/_template.md`)
waarin `source:` een geteste waarde heeft: `hub`, `forward`, `pop`, `m365` of
`none`, plus een `tested:` datum. Voor elke `forward`/`pop` is één testmail
aantoonbaar in de hub aangekomen met het juiste label. Voor VU is de M365-
connector verbonden en heeft Claude één VU-mail teruggelezen. Daarnaast staat
in `reference/email-tools.md` de volledige lijst Gmail- en M365-toolnamen die
een Routine met die connectors werkelijk ziet, verzameld door één eenmalige
test-Routine (`run_once_at`, connectors erbij) die niets anders doet dan zijn
tools opsommen en het bestand committen. Niet uit een chat — die ziet een
andere set. Per tool staat erbij: allowlist of niet, en of draft-maken en
verzenden hetzelfde tool zijn.

## Wat Ollie doet (± 30 min)

- Eerst: de lijst met álle adressen, één regel per adres. Elk adres hieronder
  is een eigen profiel; "Outlook" kan er drie zijn.

- iCloud: icloud.com → Mail → instellingen → doorsturen naar de hub.
- mail.com: doorsturen of POP; op een gratis account is dit mogelijk niet
  beschikbaar — dan `source: none` en eerlijk zo laten staan.
- Outlook: instellingen → doorsturen naar de hub.
- UvA: probeer doorsturen; als de tenant het blokkeert, `source: none`.
- VU: verbind de Microsoft 365-connector met het VU-account.
- Hub-Gmail: per bron een filter "to:/from: … → label `mail/<slug>`" mét
  "nooit naar spam", anders belandt doorgestuurde mail in de hub-spam.
- Send-as voor iCloud en mail.com: app-wachtwoord bij de provider, invoeren in
  Gmail → Accounts → "Mail verzenden als". Nooit in het repo.

## Wat Claude doet

De test-Routine aanmaken en afvuren voor de toollijst. Daarna in een chat met
Gmail en M365 aan: één draft aanmaken en weer verwijderen, één testmail per
label terugzoeken.

## Notes

Geen code in deze stap. Alles wat hier `none` wordt, valt terug op "tekst om te
plakken" in de briefing. Dat is de eerlijke uitkomst, geen mislukking.
