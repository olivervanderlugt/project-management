---
title: In elke Claude-chat of Cowork-sessie meteen alles over mijn mail weten
project: hangar
status: inbox
added: 2026-09-21
effort: L
branch:
---

## Done means

Nog niet schrijfbaar. Eerst twee beslissingen van Ollie (onderaan).

## Wat Ollie vroeg (2026-09-21, in zijn woorden)

"I just want to be able to chat into any claude chat or cowork session and it
immediately knows everything about my mail, history and account and context
no matter what subject, account or topic. I mainly just plug in or ask about
my mails and it analyzes and assesses everything and suggests changes, fixes
and responses."

## Wat dat verandert

Tot nu toe was het ontwerp: Claude draait rondes op de Mac en laat drafts en
een briefing achter. Dit vraagt iets anders erbij: een **contextlaag die elke
chat kan lezen**, ook een claude.ai-chat die niet bij Mail kan.

Wat een willekeurige chat kan bereiken: de Gmail-connector (één account), de
Google Drive-connector, en skills. Cowork op de Mac kan daarnaast bestanden
lokaal lezen en `mail.py` zelf draaien.

## Voorstel

1. De Mac-ronde schrijft na elke run een **mailcontext** weg: per account een
   bestand met open threads (wie, waarover, wat er van Ollie verwacht wordt,
   laatste datum), contacten die vaak terugkomen, en de laatste N dagen als
   compacte samenvatting per thread. Geen volledige mails.
2. Die map staat in **Google Drive** (`Hangar/Mail/`), zodat de
   Drive-connector hem in elke chat kan lezen — dezelfde route als de
   vakmappen die `weekschema-sbi` leest.
3. Een skill **`mail-context`** voor claude.ai en Cowork: "lees eerst
   `Hangar/Mail/context.md`, dan het accountbestand van het onderwerp, dan
   pas antwoorden." Cowork op de Mac gebruikt daarbovenop `mail.py` live.
4. De Gmail-connector blijft de live bron voor Gmail in een chat.

## Het probleem dat dit blootlegt

**Dit repo is publiek.** `email/accounts/` met negen adressen staat nu op
GitHub voor iedereen. Log en briefings zouden afzenders en onderwerpen
publiek maken. Dat kan niet. Twee uitwegen:

- **A.** Hangar privé maken. Pages werkt dan niet meer op een gratis account;
  het bord kan als Artifact gepubliceerd blijven.
- **B.** Hangar publiek laten, en álle maildata (profielen, log, briefings,
  context) buiten het repo zetten: lokaal in `~/.hangar-mail/`, gesynct naar
  Drive. Het repo houdt alleen scripts, skill en tests.

B past bij hoe `preview.py` al werkt (`~/.hangar-previews`) en bij het
Drive-voorstel hierboven.

## Beslissingen voor Ollie

1. A of B?
2. Hoe ver terug moet "history" gaan: 30 dagen, een jaar, alles?
3. Mogen de samenvattingen in Drive staan (privé, jouw account)?
