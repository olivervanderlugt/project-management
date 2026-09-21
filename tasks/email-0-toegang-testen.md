---
title: E-mail stap 0 — adreslijst, profielen, en één echte Mail-leesactie op de Mac
project: hangar
status: doing
added: 2026-09-21
effort: S
branch: claude/multi-email-manager-system-ozr70l
---

## Done means

`email/accounts/` bevat één bestand per adres (uit `_template.md`) met
`mail_account:` exact zoals Mail het account noemt, `priority:` en een
`tested:` datum. Die datum mag er pas staan als op Ollie's Mac deze regel het
account én één onderwerp heeft teruggegeven:

```
osascript -e 'tell application "Mail" to get name of every account'
osascript -e 'tell application "Mail" to get subject of first message of inbox'
```

macOS vraagt daarbij één keer om toestemming (Terminal mag Mail besturen);
die is gegeven. `reference/email-mail-scripting.md` bevat wat de twee regels
teruggaven, letterlijk, plus de accountnamen — dat is de invoer voor `email-1`.

## Wat Ollie doet (± 10 min)

- De adreslijst: één regel per adres, met provider en prioriteit 1–3.
- De twee `osascript`-regels draaien en de uitvoer plakken.
- De Automation-vraag van macOS met "Sta toe" beantwoorden.

## Notes

Geen code. Als de tweede regel een foutmelding geeft in plaats van een
onderwerp, staat dát in het referentiebestand en begint `email-1` daar.

## Stand 2026-09-21

osascript werkt, negen accountnamen bekend, uitvoer in
`reference/email-mail-scripting.md`, negen profielstubs in `email/accounts/`.
Open: adres, provider, prioriteit, taal en toon per account — Ollie vult in.

Eerste echte `mail.py accounts` op de Mac: negen accounts, adressen bevestigd,
twee gecorrigeerd. Rest van email-0: `unread` en één draft.
