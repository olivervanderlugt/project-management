---
title: Nachtrun-PR-plafond verhoogd, maar slimmer geteld
status: accepted
date: 2026-08-11
---

## Context

Overnight rule 5 stopte de nachtrun bij drie open PR's die door eerdere
nachtruns zijn geopend — een platte telling, zonder onderscheid tussen een
PR die nog nooit iemand heeft bekeken en een PR die al goedgekeurd is en
alleen op een merge-klik wacht. Op 2026-08-11 stond de teller op precies 3
(`project-management#5`, `percentile#1`, `learning-website#3`), dus die
nacht werd er niets gebouwd — puur omdat de teller geen onderscheid maakte
tussen "Ollie moet hier nog naar kijken" en "Ollie hoeft alleen op merge te
drukken".

Ollie, 2026-08-11: verhoog het plafond zodat er minder nachten overgeslagen
worden, maar bouw het slimmer en veiliger — niet alleen een groter getal.

Wat "veiliger" hier concreet betekent: het plafond bestond om te voorkomen
dat er 's ochtends een onbeheersbare stapel review-werk ligt. Simpelweg het
getal optrekken lost het "minder nachten overgeslagen"-probleem op maar
maakt die stapel groter. De vaste vraag was dus: hoe geef je meer ruimte aan
de nachtrun zonder de stapel die Ollie moet doorlezen te vergroten.

## Decision

1. **Alleen echte review-schuld telt mee.** Een nachtrun-PR met een
   `APPROVED`-review telt niet meer mee voor het plafond — die wacht alleen
   op een merge-klik, niet op een oordeel. Dat is de kern van "slimmer":
   het plafond meet nu wat Ollie nog moet *beoordelen*, niet hoeveel PR's er
   toevallig openstaan.
2. **Plafond per repo én totaal**, niet één platte teller: max 2 openstaande
   review-schuld-PR's per repo, max 8 in totaal. Per-repo voorkomt dat één
   project de hele nacht-capaciteit opsoupeert; het totaal voorkomt dat zeven
   repo's samen alsnog een onbeheersbare stapel worden.
3. **Bij een vol plafond wordt niet meteen de hele nacht overgeslagen.** De
   nachtrun probeert de eerstvolgende `ready`-taak waarvan de repo nog onder
   zijn per-repo-plafond zit. Pas als niets meer past — elke repo met een
   `ready`-taak zit aan zijn plafond, of het totaal zit vol — gaat de nacht
   naar stap 3 (aanscherpen).
4. **Stale-signaal in plaats van eeuwige onzichtbaarheid.** Een nachtrun-PR
   die langer dan 14 dagen open staat zonder ooit een review te hebben gehad,
   telt niet mee voor het plafond (het hoger plafond mag zoiets niet
   permanent onder het tapijt vegen) maar wordt wél in het night-log genoemd.
   Dat is de andere helft van "veiliger": een hoger plafond mag nooit
   betekenen dat een genegeerde PR onzichtbaar blijft.
5. **Geteld met code, niet met avond-voor-avond interpretatie.**
   `scripts/pr_limits.py` beslist dit deterministisch uit de PR-gegevens die
   de nachtrun ophaalt (repo, branch, wanneer geopend, review-status) — geen
   losse afweging meer per nacht over wat wel/niet als "nachtrun-PR" telt
   (dat leverde eerder al twee keer discussie op: `quizzly#1` en
   `percentile#3` telden niet mee omdat de branch-naam niet paste, en dat
   stond alleen in het night-log, niet vast in code).

## Consequences

Makkelijker: minder nachten waarin er niets gebouwd wordt, zonder dat de
stapel te-reviewen werk groeit — een goedgekeurde PR blokkeert niets meer, en
één traag project blokkeert de andere zes niet. De telling is nu testbaar
(`scripts/test_pr_limits.py`) in plaats van een interpretatie die per nacht
kan verschillen.

Moeilijker/kost iets: de nachtrun moet nu voor elke repo ook de review-status
van elke open PR ophalen, niet alleen of hij open is — één extra API-aanroep
per PR. En het plafond is nu twee getallen (2 per repo, 8 totaal) in plaats
van één simpel getal — iets meer om uit te leggen, maar wel exact
gedocumenteerd in `scripts/pr_limits.py` zelf.
