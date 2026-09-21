---
title: E-mail stap 4 — het enige pad naar verzenden: Ollie zegt "verstuur <id>" in de chat
project: hangar
status: inbox
added: 2026-09-21
effort: S
branch:
---

## Done means

De skill uit `email-1` krijgt één sectie "Verzenden". Alleen in een sessie met
Ollie erbij, alleen na een bericht van hem dat letterlijk een draft-id of
onderwerp noemt plus "verstuur" of "send". Claude leest de draft eerst terug
(aan wie, van welk adres, eerste regel), verstuurt dan, en schrijft één regel in
`email/log/`. Twee drafts in één bericht: twee losse bevestigingen. Een
Routine-sessie kan dit pad niet nemen: de hook uit `email-1` blokkeert zonder
`HANGAR_EMAIL_SEND_OK=1`, en die variabele zet alleen Ollie's eigen sessie.
Test in `scripts/test_guard.py`: verzendtool zonder variabele → exit 2.

## Notes

"Stuur alles maar" telt niet als toestemming per mail. Dat is een bewuste
keuze van Ollie (2026-09-21), geen voorzichtigheid van Claude.
