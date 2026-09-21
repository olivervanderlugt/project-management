---
title:  Maildata staat buiten de Hangar, op de Mac en in Drive; het repo houdt alleen scripts, skill en templates
status: accepted
date:   2026-09-21
---

## Context

De Hangar is een publiek repo met GitHub Pages. Op 2026-09-21 stonden er
negen e-mailprofielen met Ollie's adressen in, en het ontwerp uit `0007`
zou log, briefings en later een mailcontext met afzenders en onderwerpen
ook in het repo zetten. Dat is publiek maken wat privé is.

Ollie's doel is bovendien breder dan rondes op de Mac: hij wil in élke
Claude-chat of Cowork-sessie meteen alles over zijn mail weten — historie,
open threads, wie wie is — over alle accounts heen. Dat vraagt een
contextlaag die ook een chat zonder toegang tot Mail kan lezen.

Twee opties: de Hangar privé maken (Pages valt dan weg op een gratis
account), of alle maildata buiten het repo houden. Ollie koos het tweede.

## Decision

1. **Niets van mail in het repo.** Profielen, state, log, briefings en
   context staan op de Mac in `~/.hangar-mail/` (`HANGAR_MAIL_DIR`
   overschrijft). Het repo houdt `email/accounts/_template.md`,
   `email/_state-template.md`, de scripts, de skill en de tests.
   `.gitignore` sluit de rest uit; de guard blijft wachtwoorden in profielen
   weigeren, waar ze ook staan.
2. **De mailcontext gaat naar Google Drive**, map `Hangar/Mail/`, gesynct
   vanaf `~/.hangar-mail/context/`. Drive is Ollie's privé-account; de
   Drive-connector maakt het leesbaar in elke claude.ai-chat, dezelfde route
   als zijn vakmappen. Cowork op de Mac leest het lokaal en heeft `mail.py`
   erbij.
3. **De context bevat geen mails.** Per account: een threadindex (wie,
   onderwerp, data, aantal, map, open of afgehandeld), een contactenlijst
   met rol, en per thread een samenvatting van enkele regels. Volledige
   tekst blijft in Mail.
4. **Historie: alles.** De index is mechanisch en dekt elk bericht in elk
   account, zonder modelaanroep. Samenvattingen door Claude beginnen bij
   prioriteit 1 en de laatste 90 dagen en groeien per ronde terug in de
   tijd; dat is de enige plek waar tokens in gaan.
5. De adressen die tot vandaag in dit branch stonden, zitten in zijn
   git-historie. Een squash-merge naar de default branch neemt ze niet mee;
   daarna gaat dit branch weg. Dat is Ollie's handeling, niet die van een
   sessie — de guard weigert branch-verwijdering en force-push.

## Consequences

- `mail_profiles.py` schrijft naar `~/.hangar-mail/accounts/` en kopieert
  de template erheen. De negen profielen die Ollie al had, verhuist hij
  met één `mv`.
- De skill leest en schrijft alleen onder `~/.hangar-mail/`.
- De eerste volledige index over alle accounts is een eenmalige lange run
  van een script, geen Claude-sessie (`email-5`). Daarna is elke ronde
  incrementeel.
- Wat een claude.ai-chat "weet" is zo vers als de laatste sync naar Drive.
  Cowork op de Mac is altijd actueel.
- Het bord toont niets van mail meer. De briefing leest Ollie in
  `~/.hangar-mail/briefings/` of in Drive.
