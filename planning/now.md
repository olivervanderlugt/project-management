---
updated: 2026-09-08
focus: Drie vastgelopen PR's wachten al 4+ weken op jou; wrapup-stapel op 18; je EIGEN al geaccepteerde plafond-besluit ligt al 28 dagen ongebruikt
---

- **Je eigen besluit van 2026-08-11 om dit precieze probleem op te lossen is
  28 dagen kwijt geweest — dit is waarschijnlijk de belangrijkste regel
  hieronder.** Zie `tasks/hangar-pr-plafond-kwijt.md`. Op een branch die nooit
  een PR kreeg (`claude/charming-fermat-kdilid`) staat `decisions/0004-nachtrun-
  pr-plafond-verhoogd.md` (`status: accepted`) plus een volledig werkende,
  geteste implementatie (`scripts/pr_limits.py` + tests): een PR met een
  `APPROVED`-review telt niet meer als schuld, plafond per repo (2) én totaal
  (8) in plaats van een platte teller van 3. Jij vroeg daar zelf om, het is
  gebouwd, en het heeft de default branch nooit bereikt. Drie dingen om te
  beslissen: alsnog invoeren zoals het daar staat (of eerst herzien — de vloot
  groeide sindsdien van 1 naar 7 repo's)? Welk besluitnummer (0004 is
  inmiddels viervoudig vergeven, dit zou 0007 worden)? En wie voert het door —
  een dagsessie, of mag een nachtrun het bouwen ná jouw akkoord hier?

- **hangar-in-de-browser: stap 1 ("vangen vanuit de browser zonder sessie")
  staat er al sinds 2026-08-06, nog steeds nooit geprobeerd** —
  `.github/ISSUE_TEMPLATE/vangen.yml` + `.github/workflows/capture.yml` +
  `scripts/capture_issue.py`, volledig gratis (geen model-aanroep, geen
  API-sleutel). Opnieuw geverifieerd 09-08: de `Capture`-workflow staat nog
  `active`, nog nooit een issue met het label `capture`. Probeer het
  Vangen-formulier zelf op GitHub (kan vanaf je telefoon) — zie
  `tasks/hangar-in-de-browser.md`.

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
    scherpt hij alleen `inbox`-taken aan — dat is nu al drie weken de status.

- **De wrapup-PR-stapel (`hangar-wrapup-pr-pileup`) staat op 18**
  (`project-management#15`–`#32`), plus `#11` van 08-14. Niemand merget ze,
  groei blijft ~1 per nacht. Drie opties liggen klaar in de taak; geen ervan
  mag een nachtrun zelf kiezen — dat is expliciet jouw procesbeslissing.

- **Vijf `ready` taken staan te wachten, geblokkeerd door bovenstaande**:
  `pi-openclaw-gateway` (08-07), `quizzly-media-read-authz` (08-14),
  `quizzly-media-orphan-cleanup` (08-15), `hangar-sessionstart-hook-gedrag`
  (08-20), `quizzly-semantische-tokens` (08-20). `pi-openclaw-gateway` is de
  oudste, maar meldt zelf dat de nachtrun hem nooit kan bouwen (fysiek werk) —
  zodra de PR-grens opengaat, kiest "oudste eerst" mechanisch een taak die
  nooit `done` wordt, tenzij jij vastlegt dat zulke taken overgeslagen worden.
  Zie vraag 4 in `tasks/nachtrun-loopt-vast-op-een-taak.md`.

- **Dagsessie-PR's die al op jouw merge wachten** (tellen niet mee bij regel
  5): quizzly#1 (finalisatie), quizzly#4/#5/#6 (wachtwoord-toggle, contrast,
  slide-designer-onderzoek), percentile#3 (MVP launchable).

- **Nog steeds open:** `nightrun-limits-decisions` (vuurtijd vs. je weekly
  reset, usage-cap, inhaalrun); `hangar-daysession-branches-onzichtbaar`
  (hoe vind je een besluit dat op een branch zonder PR staat, zónder te
  gokken welke naam te controleren — precies hoe het plafond-besluit hierboven
  28 dagen kwijt was). Versa blijft geparkeerd. `ideas/` nog steeds leeg.
