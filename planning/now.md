---
updated: 2026-08-29
focus: Acht nachten van een verborgen dagsessie-branch teruggehaald — queue klopt weer, drie echte PR's wachten nog op jou
---

- **Grote vondst vannacht (2026-08-29): jouw besluiten van 08-20 stonden 8
  nachten onzichtbaar.** Om 15:49 UTC die dag nam je vier echte besluiten
  (`quizzly-media-read-authz` → `ready`, Versa → geparkeerd,
  `quizzly-design-pass-toepassen` → richting C gekozen,
  `hangar-stale-clone-guard` gesplitst) op een branch
  (`claude/hangar-nightrun-status-hsr0iy`) waar nooit een PR voor kwam. Elke
  nachtrun van 08-21 tot 08-28 las de default branch, zag de oude status en
  werkte daarop door — de nacht van 08-21 zocht zelfs hosting voor Versa uit
  terwijl je het project uren eerder al had geparkeerd. Vanavond ontdekt bij het
  kiezen van werk, teruggehaald met dezelfde `git checkout <branch> --
  <bestand>`-precedent als de nachtrun al gebruikt voor haar eigen weesbranches.
  Zie `tasks/hangar-daysession-branches-onzichtbaar.md` voor het volledige
  patroon en de open vraag aan jou (hoe vindt een sessie dit soort branches
  zónder te moeten gokken welke naam te controleren).
  - Bijvangst: `hangar-in-de-browser`, `hangar-wrapup-pr-pileup` en
    `quizzly-legal-review-west` (onderzoek van de nachten 08-21 t/m 08-27) waren
    óók nooit op de default beland — een aparte, kleinere versie van hetzelfde
    probleem (wél een PR-trail, maar niemand merget). Nu ook mee teruggehaald.

- **Queue na het terughalen: vier `ready` taken, oudste eerst.**
  `quizzly-media-orphan-cleanup` (08-15), `hangar-sessionstart-hook-gedrag`
  (08-20, het onderzoek dat `hangar-stale-clone-guard` blokkeert),
  `quizzly-media-read-authz` (08-14/besloten 08-20),
  `quizzly-semantische-tokens` (08-20). Vannacht niet gebouwd — zie hieronder.

- **Drie echte vastgelopen nachtrun-PR's wachten al 3+ weken op jou**, ongewijzigd
  sinds ze geopend zijn (elke nacht opnieuw gecontroleerd, nooit aangenomen):
  - `percentile#1` — echt conflict tegen `main` (`mergeable_state: dirty`).
  - `learning-website#3` — gebouwd vóór het auto-merge-besluit (0004), staat
    klaar (`mergeable_state: clean`) maar niemand heeft hem gemerged.
  - `project-management#13` (`hangar-stale-clone-guard`) — de checker hield
    `ship: false` op één punt: de taak eiste een live wegwerp-hook-test van
    `SessionStart`/`additionalContext`, en dat is (bewust) niet gedaan. Zie de
    taak zelf voor de exacte vraag.
  - Zolang deze drie op 3 blijven staan, bouwt de nachtrun niets (regel 5) en
    scherpt hij alleen `inbox`-taken aan.

- **Losse stapel: acht nachtrun-eigen stap-4-PR's staan open**
  (`project-management#15` t/m `#22`, 08-21 t/m 08-28), plus `#11` van 08-14.
  Niemand merget ze — dat is precies `hangar-wrapup-pr-pileup`, nog steeds
  `inbox`, drie opties liggen klaar, geen ervan mag een nachtrun zelf kiezen.

- **Dagsessie-PR's die al op jouw merge wachten** (niet nachtrun-eigen, dus
  tellen niet mee bij regel 5): quizzly#1 (finalisatie), quizzly#4/#5/#6
  (wachtwoord-toggle, contrast, slide-designer-onderzoek), percentile#3 (MVP
  launchable).

- **Nog steeds open:** `nightrun-limits-decisions` (vuurtijd vs. je weekly
  reset, usage-cap, inhaalrun — achtergrond in
  `reference/nightrun-usage-limits.md`); de vraag of
  `reference/startprompt-nightrun.md` letterlijk in de Routine staat — de
  live prompt van vanavond is duidelijk een (Nederlandstalige, herstructureerde)
  variant, niet deze exacte Engelse tekst; niet verder uitgezocht vanavond.
  Versa blijft geparkeerd. `ideas/` nog steeds leeg — zet er in wat er in je
  hoofd zit.
