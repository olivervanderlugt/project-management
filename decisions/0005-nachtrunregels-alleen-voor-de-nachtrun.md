---
title: Nachtrunregels staan in een eigen bestand dat de nachtrun zelf laadt
status: accepted
date: 2026-08-14
---

## Context

De elf nachtrunregels stonden in `CLAUDE.md`. Dat bestand wordt door élke sessie
gelezen die dit repo opent, en `CLAUDE.md` is per definitie staand recht — dus
paste iedere sessie ze op zichzelf toe, ook als Ollie erbij zat en er niets
onbewaakt aan was.

Op 2026-08-14 werd dat zichtbaar. Ollie vroeg om vier taken tegelijk te bouwen
met meerdere agents. De sessie deed dat, maar rechtvaardigde het alsof er twee
regels overtreden werden — "één taak per nacht" en "stoppen bij drie open PR's"
— en schreef zijn spoor in `planning/night-log.md`, een bestand dat in zijn
eigen kop zegt dat het over de nachtrun gaat. Ollie moest twee keer corrigeren:
dit is geen nachtrun, dit is mijn eigen verzoek.

Dat is geen leesfout van die ene sessie. Elke regel begint met "de nachtrun
doet X", maar staat in het bestand dat zegt: dit geldt altijd. De kosten zijn
niet cosmetisch. Een sessie die zichzelf op één taak zet terwijl Ollie er vier
vraagt, of die weigert te bouwen omdat er PR's openstaan, doet minder dan
gevraagd en verkoopt dat als zorgvuldigheid. En het night-log raakt vervuild met
dagwerk, waardoor het zijn enige functie verliest: in één blik zien wat er is
gebeurd terwijl je sliep.

De regels zelf zijn goed. Ze volgen alleen allemaal uit één feit — niemand is
wakker om een fout te vangen — en dat feit is 's ochtends niet waar.

## Decision

De elf regels verhuizen ongewijzigd naar `reference/nightrun-rules.md`, in de
tekst zoals die op 2026-08-14 in `CLAUDE.md` stond — dus mét regel 3's
auto-merge en de herschreven regel 5 uit besluit `0004`. Dat bestand opent met
wie het bindt en wie niet.

`CLAUDE.md` houdt een korte sectie over die drie dingen doet: zeggen dát er
nachtrunregels zijn, waar ze staan, en expliciet dat ze **niet** gelden voor een
sessie die Ollie zelf begonnen is. Met de instructie erbij: vraagt hij vier
taken, bouw er vier; zeg nooit dat een regel het verbiedt. Eén uitzondering
staat er met zoveel woorden bij: zijn eigen PR mergen is de nachtrun z'n regel,
niet die van een dagsessie — met Ollie erbij vraag je het.

De nachtrun krijgt de regels doordat zijn eigen prompt hem opdraagt het
regelbestand als eerste te lezen. Die prompt staat in
`reference/startprompt-nightrun.md` en moet één keer in de Routine op claude.ai
geplakt worden.

Een sessie met Ollie erbij laat een ander spoor achter: `planning/now.md` plus
eerlijke `status:` en `branch:` in de taakbestanden. Het night-log blijft van de
nachtrun.

Regel 10 krijgt er één alinea bij. Nu meerdere sessies taken op `doing` kunnen
zetten, is `doing` niet langer bewijs van een afgekapte run — de nachtrun moet
eerst `planning/now.md` en de branch bekijken voordat hij iets terugzet.

## Consequences

De nachtrun hangt nu aan zijn promptregel. Herschrijft iemand die prompt en
laat hij de "lees `reference/nightrun-rules.md`" eruit, dan volgt de run de
regels niet meer en waarschuwt niets. Daarom staat die waarschuwing in het
promptbestand zelf, en verwijst de sectie in `CLAUDE.md` er ook heen — een run
die alleen `CLAUDE.md` leest, komt er alsnog. Twee wegen naar hetzelfde
bestand, in plaats van één regel die stilzwijgend weg kan vallen.

Regels die overal gelden zijn niet meeverhuisd: niets verzinnen, dashboard
herbouwen, vangen vóór bouwen, besluiten zijn append-only, en de guard. Die
staan in `CLAUDE.md` waar ze horen.

Er is één regel bijgekomen die niets met de nachtrun te maken heeft, uit een
tweede fout van dezelfde sessie: **fetch voordat je de werkboom gelooft.** De
lokale kloon was een week oud, de nachtrun had zes nachten doorgewerkt, en de
sessie stuurde agents op drie taken af die al gebouwd en gemerged waren. `git
status` was de hele tijd schoon. Dat staat nu als eigen sectie in `CLAUDE.md`,
en als taak `hangar-stale-clone-guard` in de wachtrij, omdat een regel die je
moet onthouden zwakker is dan een controle die vanzelf gaat.

Wat dit niet oplost: er is nog steeds geen manier waarop een sessie zeker weet
of hij de nachtrun is. Dit besluit vertrouwt erop dat de Routine zijn eigen
prompt meestuurt. Blijkt dat te wankel, dan is de volgende stap een marker die
de Routine zet en de sessie kan lezen — niet nog een regel in `CLAUDE.md`.
