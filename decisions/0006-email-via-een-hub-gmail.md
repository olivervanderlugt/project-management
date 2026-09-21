---
title:  Claude leest alle mail via één hub-Gmail; verzenden alleen op direct verzoek van Ollie
status: proposed
date:   2026-09-21
---

## Context

Ollie heeft een stuk of tien e-mailadressen bij zes providers: Gmail, Outlook,
VU, UvA, mail.com en iCloud. Gmail en VU zijn prominent. Hij wil Claude als
e-mailmanager: op de hoogte van de gesprekken, drafts voor nieuwe mails en
antwoorden, spam in quarantaine, afmelden, twee briefings per dag en doorlopend
drafts als er iets binnenkomt. Voor hemzelf moeten de accounts gescheiden
blijven; de backend voor Claude mag samengevoegd zijn.

Niet elk account laat zich koppelen. De Gmail-connector dekt één Google-account.
De Microsoft 365-connector dekt één M365-account. Er is geen connector voor
mail.com of iCloud. Wachtwoord-IMAP is bij Microsoft dicht sinds 2024, dus een
lokaal IMAP-script dekt Outlook, VU en UvA niet.

## Decision

1. **Eén hub-Gmail is Claude's leesbron.** Elk ander account stuurt door naar
   de hub (of de hub haalt het op via POP). Een Gmail-filter per bronadres
   plakt een label, zodat de scheiding voor Claude en in de briefing intact
   blijft. Ollie blijft zijn accounts gewoon los gebruiken; de hub is Claude's
   bril, niet zijn postvak.
2. **VU gaat rechtstreeks via de Microsoft 365-connector**, niet via de hub.
   VU is prominent, universiteiten blokkeren vaak doorsturen naar buiten, en
   direct betekent dat spam-quarantaine en drafts in het VU-account zelf
   landen. De M365-connector dekt één account, dus UvA gaat via de hub.
3. **Verzenden gebeurt nooit zonder Ollie's directe toestemming in de chat**,
   per mail, met de draft-id erbij. Geen Routine verzendt ooit. Dit is niet
   alleen een promptregel: een `PreToolUse`-hook blokkeert elk Gmail- of
   M365-verzendtool structureel, en de hook wordt alleen in een sessie met
   Ollie erbij expliciet omzeild — nooit door de hook uit te zetten.
4. **Spam is quarantaine, niet weg.** Claude verplaatst naar een
   quarantaine-label; Gmail's eigen spam-map ruimt na 30 dagen op. Afmelden
   mag zonder vragen. Drafts maken mag zonder vragen.
5. **Geen credentials in de Hangar.** App-wachtwoorden voor "send mail as"
   voert Ollie zelf in bij Gmail. Het repo bevat profielen, regels, briefings
   en een log — nooit een wachtwoord of token.

## Consequences

- Wat via de hub loopt, kan Claude alleen in de hub opruimen; het bron-postvak
  van Outlook, UvA, mail.com en iCloud blijft ongemoeid. Afmelden werkt wél
  overal, want de afzender stopt.
- Drafts met de juiste afzender kunnen alleen waar Gmail "send mail as" een
  SMTP-login accepteert: iCloud en mail.com met app-wachtwoord ja, Outlook en
  UvA nee. Voor die twee levert Claude de draft als tekst die Ollie plakt.
- Dit besluit past binnen 0001: geen app, geen server, markdown plus twee
  connectors en Routines.
- Twee briefings plus doorlopende verwerking is 10 tot 17 Routine-runs per dag.
  De frequentie staat in `tasks/email-3-doorlopende-verwerking.md` en is
  Ollie's knop, niet die van de run.
