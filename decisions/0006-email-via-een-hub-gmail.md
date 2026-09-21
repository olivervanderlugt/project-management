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
   per mail, met de draft-id erbij. Geen Routine verzendt ooit. Wat de hook
   structureel garandeert is dat laatste: een `PreToolUse`-hook op alle
   `mcp__Gmail__*`- en `mcp__Microsoft_365__*`-tools laat alleen een
   allowlist door (zoeken, lezen, draft maken, label zetten, naar spam
   verplaatsen) en weigert al het andere — fail-closed, dus een nieuw of
   hernoemd verzendtool is ook dicht. De sleutel die verzenden opent staat
   alleen in Ollie's eigen shell op zijn eigen machine, nooit in
   `.claude/settings.json` en nooit in een Routine. De regel "per mail, na
   'verstuur <id>'" is binnen die ene sessie een skill-regel, geen hook; dat
   is de eerlijke grens van wat een hook kan.
4. **Spam is quarantaine, niet weg.** Claude verplaatst naar Gmail's eigen
   spam-map (in VU: de map Ongewenste e-mail), want die ruimt na 30 dagen
   zelf op; een eigen label zou nooit opgeruimd worden. Elke verplaatsing
   staat in het log, dus terughalen is één zoekopdracht. Drafts maken mag
   zonder vragen.
4b. **Afmelden mag zonder vragen, maar alleen zonder te verzenden.** Dus
   alleen via RFC 8058 one-click (`List-Unsubscribe-Post`) of een https-link
   uit de `List-Unsubscribe`-header. Een `mailto:`-afmelding ís een mail
   en gaat als draft in de briefing, met Ollie's "verstuur" als enige pad.
   Links uit de body van de mail worden nooit gevolgd — een Routine met
   connectors mag geen willekeurige URL uit ongelezen post openen.
5. **Geen credentials in de Hangar.** App-wachtwoorden voor "send mail as"
   voert Ollie zelf in bij Gmail. Het repo bevat profielen, regels, briefings
   en een log — nooit een wachtwoord of token.

## Consequences

- Wat via de hub loopt, kan Claude alleen in de hub opruimen; het bron-postvak
  van Outlook, UvA, mail.com en iCloud blijft ongemoeid, en wat de bron zelf
  al als spam wegfiltert stuurt hij niet door — dat blijft het werk van die
  provider. Afmelden werkt wél overal, want de afzender stopt.
- Doorgestuurde mail faalt vaak SPF/DKIM en belandt in de spam van de hub;
  elk hub-filter krijgt daarom "nooit naar spam" mee. Anders zet de hub zelf
  echte mail in quarantaine.
- De M365-connector dekt één account. Een tweede Outlook-familie-account
  (UvA, een tweede Outlook) gaat via doorsturen of krijgt `source: none`.
- Drafts met de juiste afzender kunnen alleen waar Gmail "send mail as" een
  SMTP-login accepteert: iCloud en mail.com met app-wachtwoord ja, Outlook en
  UvA nee. Voor die twee levert Claude de draft als tekst die Ollie plakt.
- Dit besluit past binnen 0001: geen app, geen server, markdown plus twee
  connectors en Routines.
- Twee briefings plus doorlopende verwerking is 10 tot 17 Routine-runs per dag.
  De frequentie staat in `tasks/email-3-doorlopende-verwerking.md` en is
  Ollie's knop, niet die van de run.
