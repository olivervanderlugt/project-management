---
updated: 2026-09-03
focus: Drie vastgelopen PR's wachten al 4+ weken op jou; wrapup-stapel op 13; drie procesbeslissingen liggen klaar
---

- **hangar-in-de-browser: stap 1 ("vangen vanuit de browser zonder sessie")
  staat er al sinds 2026-08-06** — `.github/ISSUE_TEMPLATE/vangen.yml` +
  `.github/workflows/capture.yml` + `scripts/capture_issue.py`, volledig
  gratis (geen model-aanroep, geen API-sleutel — de oorspronkelijke blokkade
  gaat dus niet meer op). 27 dagen nooit met een echt issue geprobeerd.
  Probeer het Vangen-formulier zelf op GitHub (kan vanaf je telefoon) — zie
  `tasks/hangar-in-de-browser.md` voor de details en de nieuwe, kleinere vraag.

- **Drie echte vastgelopen nachtrun-PR's wachten al 4+ weken op jou**,
  ongewijzigd sinds ze geopend zijn (elke nacht opnieuw gecontroleerd via de
  API, nooit aangenomen):
  - `percentile#1` — echt conflict tegen `main` (`mergeable_state: dirty`).
  - `learning-website#3` — gebouwd vóór het auto-merge-besluit (0004), staat
    klaar (`mergeable_state: clean`) maar niemand heeft hem gemerged.
  - `project-management#13` (`hangar-stale-clone-guard`) — checker hield
    `ship: false` op één punt (live hook-verificatie niet gedaan). Zie de
    taak zelf voor de exacte vraag.
  - Zolang deze drie op 3 blijven staan, bouwt de nachtrun niets (regel 5) en
    scherpt hij alleen `inbox`-taken aan — dat is nu al twee weken de status.

- **De wrapup-PR-stapel (`hangar-wrapup-pr-pileup`) staat op 13**
  (`project-management#15`–`#27`, 14 zodra vanavond opent), plus `#11` van
  08-14. Niemand merget ze. Drie opties liggen klaar in de taak; geen ervan
  mag een nachtrun zelf kiezen — dat is expliciet jouw procesbeslissing.

- **Vijf `ready` taken staan te wachten, geblokkeerd door bovenstaande**:
  `pi-openclaw-gateway` (08-07), `quizzly-media-read-authz` (08-14),
  `quizzly-media-orphan-cleanup` (08-15), `hangar-sessionstart-hook-gedrag`
  (08-20), `quizzly-semantische-tokens` (08-20).

- **Dagsessie-PR's die al op jouw merge wachten** (tellen niet mee bij regel
  5): quizzly#1 (finalisatie), quizzly#4/#5/#6 (wachtwoord-toggle, contrast,
  slide-designer-onderzoek), percentile#3 (MVP launchable).

- **Nog steeds open:** `nightrun-limits-decisions` (vuurtijd vs. je weekly
  reset, usage-cap, inhaalrun); `hangar-daysession-branches-onzichtbaar`
  (hoe vind je een besluit dat op een branch zonder PR staat, zónder te
  gokken welke naam te controleren). Versa blijft geparkeerd. `ideas/` nog
  steeds leeg.
