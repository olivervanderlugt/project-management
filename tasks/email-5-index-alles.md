---
title: E-mail stap 5 — mechanische index van elk bericht in elk account, zonder modelaanroep
project: hangar
status: inbox
added: 2026-09-21
effort: M
branch:
---

## Done means

`scripts/mail_index.py` bouwt en ververst `~/.hangar-mail/context/index/`
uit Mail via `mail.py`-achtige JXA, zonder Claude: per account één
`<slug>.jsonl` met per bericht id, mailbox, datum, afzender, ontvangers,
onderwerp, gelezen/ongelezen, thread-sleutel (Mail's `messageId` en
`In-Reply-To`/`References` uit de headers, anders genormaliseerd
onderwerp), en of Ollie zelf de afzender is. Daarnaast per account
`<slug>-threads.md`: één regel per thread — laatste datum, aantal, wie,
onderwerp, `open` als de laatste mail niet van Ollie is en een vraag of
verzoek bevat (heuristiek: vraagteken of werkwoord in gebiedende wijs in de
laatste 300 tekens), anders `dicht`. En `contacts.md` over alle accounts:
adres, naam, aantal threads, laatste contact, in welke accounts.

De eerste run doet alles (`--full`), daarna alleen wat nieuwer is dan de
vorige run (`state.md`). Een run zonder nieuwe mail is klaar in seconden.
Grote accounts: een voortgangsregel per 500 berichten, en de run mag
onderbroken en hervat worden zonder dubbele regels. `scripts/test_mail_index.py`
test threading, de open/dicht-heuristiek en de hervatting tegen vaste
JSON-invoer. Niets hiervan raakt het repo: alles onder `~/.hangar-mail/`.

## Notes

Dit is de "history should contain everything"-laag: mechanisch en dus
gratis. Wat Claude ervan samenvat is `email-6`. Ollie wil daarna veel
archiveren en verwijderen; archiveren (verplaatsen naar Archief) kan het
script krijgen als apart commando, verwijderen niet zonder nieuw besluit.
