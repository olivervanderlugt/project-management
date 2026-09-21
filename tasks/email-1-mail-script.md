---
title: E-mail stap 1 — scripts/mail.py praat met Mail via osascript, zonder verzendcommando
project: hangar
status: inbox
added: 2026-09-21
effort: M
branch:
---

## Done means

`scripts/mail.py` heeft precies deze subcommando's, elk met JSON op stdout:
`accounts`, `unread --account <naam> --since <ISO>`, `read <id>` (headers
inclusief `List-Unsubscribe` en `List-Unsubscribe-Post`, plus platte tekst),
`draft --account <naam> --to --subject --body [--reply-to <id>]` (zet een
draft in de Drafts-map van dát account, verzendt niet), `junk <id>`
(verplaatst naar Ongewenst, verwijdert nooit). Het commando `send` bestaat
alleen als `HANGAR_EMAIL_SEND_OK=1` in de omgeving staat; zonder die
variabele staat het niet in `--help` en geeft aanroepen exit 2 met uitleg.

`scripts/test_mail.py` draait op Linux tegen een nep-`osascript` op het PATH
en bewijst: elk subcommando bouwt het verwachte AppleScript, `junk` roept
nooit `delete` aan, `send` zonder variabele → 2, mét variabele → het
verwachte script. `scripts/guard.py` krijgt één regel: `osascript` waarvan
het script `send` op een Mail-bericht bevat → exit 2, met tests aan beide
kanten in `scripts/test_guard.py` (blokkeert `send newMessage`, laat
`get subject` door). `python3 dashboard/build.py` blijft werken.

## Notes

Accountnamen komen uit `reference/email-mail-scripting.md` (`email-0`). Als
Mail voor een Exchange-account (VU, UvA) de map Ongewenst anders noemt, is
`junk` per account configureerbaar via het profiel — niet hardcoded.
Nooit `delete`, nooit `empty trash`: die woorden komen in het script niet voor.
