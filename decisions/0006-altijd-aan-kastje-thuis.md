---
title: Een altijd-aan kastje thuis als vangpoort, geen gehoste app
status: proposed
date: 2026-08-07
---

## Context

Besluit 0001 zegt: markdown eerst, een echte app pas als een project geld
oplevert. De hardste consequentie daarvan is dat er niets draait en niets
maandelijks kost — en dus ook dat Ollie niets kan vastleggen zonder een sessie
of de GitHub-app te openen.

Taak `hangar-in-de-browser` benoemde dat gat al en zette bij stap 4 ("eigen UI
met een server") de rem erop: dat zou 0001 breken en eerst een nieuw besluit
vragen. Dit is dat besluit — maar voor een kleinere stap dan stap 4. Geen eigen
UI, geen hosting, geen auth-laag: een Raspberry Pi 5 bij Ollie thuis, met
OpenClaw als gateway en Telegram als kanaal. Bericht in, taakbestand in
`tasks/` uit.

## Decision

Er komt een eigen server, maar thuis en eenmalig betaald: een Pi 5 (8 GB) die
via OpenClaw en een Telegram-bot berichten omzet in taakbestanden met
`status: inbox`, en die pusht naar deze repo. De motor is Ollie's bestaande
Claude Max-abonnement via de OpenClaw-login; er komen geen maandelijkse kosten
bij. De uitwerking staat in `tasks/pi-openclaw-gateway.md`.

Dit vervangt 0001 niet, het rekt hem bewust één stap op:

- Markdown blijft de bron van waarheid. Het kastje schrijft alleen bestanden in
  `tasks/`; het bord, de wachtrij en de nachtrun veranderen niet.
- "Niets te deployen of te betalen" wordt "niets gehost en niets maandelijks".
  Er staat nu wél een apparaat dat onderhoud vraagt. Dat is de prijs, en hij is
  eenmalig (~€200–265 hardware) plus een paar euro stroom per jaar.
- De trigger voor een echte web-app blijft omzet, precies als in 0001. Het
  kastje is vangst, geen app.
- De vangst-regel blijft staan: alles komt binnen als `inbox`, bouwen pas na
  een echte `## Done means`. Het kastje mag nooit taken op `ready` zetten of
  code aanraken.

## Consequences

Makkelijker: vastleggen vanaf de telefoon zonder sessie, ook onderweg; de
wachtrij groeit waar hij hoort te groeien in plaats van in Ollie's hoofd; €0
per maand blijft waar.

Moeilijker: er is nu een apparaat dat stuk kan, dat updates nodig heeft en dat
aan een abonnement-loginroute hangt die Anthropic in 2026 al vier keer heeft
gewijzigd. Valt die route weg, dan is de overstap een configuratieregel: een
API-sleutel met een klein model (enkele euro's per maand) of een lokaal model
op de Pi voor alleen de vangst (€0, trager). Beide staan uitgewerkt in de taak.

Dit besluit gaat pas op `accepted` als het eerste Telegram-bericht daadwerkelijk
als taakbestand in `tasks/` staat.

## Herkomst

Geschreven 2026-08-07 op een branch die nooit een PR kreeg en daardoor 24
dagen onzichtbaar bleef voor elke latere sessie. Teruggehaald 2026-08-30
(nachtrun) en hernummerd van `0004` naar `0006` — dat nummer was inmiddels
vergeven aan `0004-nightrun-auto-merge` en `0005-nachtrunregels-alleen-voor-
de-nachtrun`, allebei al `accepted` op de echte default branch. Status
ongewijzigd overgenomen (`proposed`); zie `tasks/hangar-daysession-branches-
onzichtbaar.md` voor het bredere patroon.
