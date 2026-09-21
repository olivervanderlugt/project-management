---
title: E-mail stap 4 — het enige pad naar verzenden: Ollie zegt "verstuur <id>" in de chat
project: hangar
status: inbox
added: 2026-09-21
effort: S
branch:
---

## Done means

De skill uit `email-2` krijgt één sectie "Verzenden". Alleen in een sessie met
Ollie erbij, alleen na een bericht van hem dat letterlijk een draft-id of
onderwerp noemt plus "verstuur" of "send". Claude leest de draft eerst terug
(aan wie, van welk adres, eerste regel), verstuurt dan met `mail.py send <id>`,
en schrijft één regel in `email/log/`. Twee drafts in één bericht: twee losse bevestigingen. Een
geplande run kan dit pad niet nemen: `send` bestaat niet zonder
`HANGAR_EMAIL_SEND_OK=1` en de guard weigert `osascript` met een verzendopdracht, en die variabele staat alleen in Ollie's eigen shell op zijn eigen machine
(`export HANGAR_EMAIL_SEND_OK=1` vóór hij Claude Code start), nooit in het repo.
Tests staan in `email-1`; hier komt er één bij: de skill-sectie noemt geen
ander pad dan `mail.py send`.

## Notes

"Stuur alles maar" telt niet als toestemming per mail. Dat is een bewuste
keuze van Ollie (2026-09-21), geen voorzichtigheid van Claude.
