---
title:  Claude leest en beheert alle mail via Mail op Ollie's Mac; verzenden alleen op direct verzoek
status: accepted
date:   2026-09-21
---

## Context

Ollie heeft al zijn adressen — Gmail, Outlook, VU, UvA, iCloud en mail.com
(Premium, voor IMAP) — gekoppeld in Mail op zijn Mac. Mail is scriptbaar via
`osascript`. Dat maakt de hub-Gmail uit `0006` overbodig: geen doorsturen,
geen send-as, geen tweede connector, en de accounts blijven écht gescheiden,
ook voor Claude. Gmail en VU zijn prominent.

## Decision

1. **Mail op de Mac is de enige bron.** `scripts/mail.py` praat via
   `osascript` met Mail: accounts opsommen, ongelezen mail per account sinds
   een tijdstip, één bericht lezen inclusief headers, een draft in de
   Drafts-map van dat account zetten, een bericht naar Ongewenst verplaatsen.
   Geen IMAP-code, geen wachtwoorden: Mail is al ingelogd.
2. **`mail.py` heeft geen verzendcommando** tenzij `HANGAR_EMAIL_SEND_OK=1` in
   de omgeving staat, en die staat alleen in Ollie's eigen shell, nooit in het
   repo of een geplande taak. `scripts/guard.py` weigert daarnaast elke
   `osascript`-aanroep die Mail iets laat verzenden. Twee muren, één doel:
   een geplande run kán niet verzenden. Per mail toestemming ("verstuur
   <id>") binnen Ollie's eigen sessie is een skill-regel — dat is de eerlijke
   grens van wat een hook kan.
3. **Spam is quarantaine, niet weg:** naar de map Ongewenst van het account
   zelf, nooit definitief verwijderen. Elke verplaatsing staat in het log.
4. **Afmelden zonder vragen, maar zonder te verzenden:** alleen RFC 8058
   one-click of een https-URL uit de `List-Unsubscribe`-header. Een
   `mailto:`-afmelding wordt een draft. Links uit de body worden nooit
   gevolgd.
5. **Drafts zonder vragen**, in Ollie's stijl, altijd in de Drafts-map van het
   account waar de mail binnenkwam, met bronadres en afzender bovenaan.
6. **Het draait op de Mac.** Briefing 07:30 en 21:30, verwerking elk uur van
   08:00 tot 22:00, via `launchd` met `claude -p` in dit repo. Cloud-Routines
   kunnen niet bij Mail. Slaapt de Mac, dan is een run laat, niet verloren:
   de volgende haalt in via `email/state.md`.
7. **Geen credentials in de Hangar.** Profielen, log, briefings en state
   wel; wachtwoorden nooit — de guard weigert ze.

## Consequences

- Alles werkt voor alle zes providers op dezelfde manier: lezen, drafts in de
  eigen map, spam in de eigen map. De tabel met uitzonderingen uit `0006`
  vervalt.
- Zonder Mac aan is er niets. Een Gmail-only cloud-fallback via de connector
  is mogelijk maar staat hier bewust uit; aanzetten is een nieuw besluit.
- `mail.py` is alleen op de Mac echt te testen. In het repo draaien tests
  tegen een nep-`osascript`; de eerste echte run is Ollie's smoke test in
  `email-0`.
- macOS vraagt één keer om Automation-toestemming (Terminal → Mail). Zonder
  die toestemming doet niets iets, en dat is dan de eerste regel van het log.
- Past binnen `0001`: geen app, geen server, één script plus markdown.
