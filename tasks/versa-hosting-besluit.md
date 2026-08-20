---
title: Beslissen waar Versa draait, en hem daar neerzetten
project: versa
status: blocked
added: 2026-08-06
effort: M
branch:
---

## Done means

Nog niet schrijfbaar — daarom `inbox`.

Versa heeft Postgres en Docker nodig, dus hosting kost geld. Welk platform,
welk budget per maand en of de database managed is of niet, is een besluit van
Ollie. Zolang dat er niet ligt, is er geen finish line die iemand anders kan
afvinken.

## Notes

Uit `reference/project-prioritering.md`: Versa scoort het hoogst op CV/LinkedIn
en op tijd-tot-echte-gebruikers, en één werkende URL levert daar het meeste per
uur op. Dat maakt dit de duurste blocker in de hele Hangar.

Vragen die het besluit vormen:

- Wat mag het per maand kosten?
- Managed Postgres of zelf draaien?
- Publiek toegankelijk vanaf dag één, of eerst achter een wachtwoord?

Auteursrecht speelt hier: de repo is bewust opgezet met publiek-domein
zaaicontent en een DMCA-flow. Live gaan met de 1400+ stubs mag niet betekenen
dat er beschermde teksten meelekken — dat controleren hoort bij deze taak.

Niet 's nachts onbewaakt uitvoeren: dit raakt geld en deploys.

**Besluit van Ollie, 2026-08-20: nu niet — geparkeerd.** Versa gaat voorlopig
nergens draaien. `projects/versa.md` staat op `status: parked`, zodat het
project niet elke keer als open blokkade op het bord verschijnt.

Dat is een uitstel, geen afwijzing, en het kost iets: uit
`reference/project-prioritering.md` scoort Versa het hoogst op CV/LinkedIn en op
tijd-tot-echte-gebruikers, en één werkende URL levert daar het meeste per uur op.
Die opbrengst blijft liggen zolang dit geparkeerd staat.

Wat er nog steeds moet gebeuren zodra het weer aangaat: budget per maand,
managed Postgres of zelf draaien, publiek of eerst achter een wachtwoord, en de
auteursrechtcontrole over de 1400+ stubs vóór er iets live gaat. Die vier vragen
staan hierboven ongewijzigd.
