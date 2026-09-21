---
title: E-mail stap 3 — elk uur overdag drafts, quarantaine en afmelden, met log
project: hangar
status: inbox
added: 2026-09-21
effort: M
branch:
---

## Done means

Eén Routine, fresh session per run, elk uur van 08:00 tot 22:00 Amsterdam-tijd
(frequentie is één regel in `reference/startprompt-email-verwerking.md` en
staat daar als Ollie's knop), met Gmail- en M365-connector. Per run: de skill
uit `email-1` draaien op alles dat sinds de vorige run binnenkwam (`email/state.md`
houdt de laatst verwerkte tijd per account bij). Drafts staan in het account
zelf waar dat kan (hub met send-as, VU via M365), anders als tekst in
`email/drafts/YYYY-MM-DD-<slug>.md`. Elke actie is één regel in
`email/log/YYYY-MM-DD.md`: tijd, account, afzender, actie, en bij quarantaine
of afmelden de reden. Een run zonder nieuwe mail kost aantoonbaar weinig: hij
stopt na de state-check en logt één regel. Een mail van een afzender in
`email/accounts/<slug>.md` onder `never_spam:` gaat nooit in quarantaine.

## Notes

Dit is de dure stap: 15 runs per dag. Als de eerste week uitwijst dat de meeste
uren leeg zijn, is elke twee uur de betere knop. Dat staat in het log te lezen,
dus het is een feit en geen gevoel. Verzenden: nooit, hook staat erop.
