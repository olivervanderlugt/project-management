---
updated: 2026-08-14
focus: Quizzly PR #4 checken en mergen; dan de vier oude PR's die al een week openstaan
---

- **Deze sessie (2026-08-14, op jouw verzoek — geen nachtrun).** Gevraagd: vier
  taken tegelijk bouwen met meerdere agents. Uitkomst: er was er nog maar één te
  bouwen. De lokale kloon liep een week achter, en de nachtrun had er in zes
  nachten drie van de vier al gebouwd én gemerged. De agents merkten dat zelf en
  hebben de gemergede code geverifieerd in plaats van hem opnieuw te bouwen.
  - **`quizzly-wachtwoord-toggle`** — echt gebouwd én adversarieel gecheckt:
    trio groen (112 tests), elke regel van de finish line vastgepind op
    coderegels. **quizzly#4 staat open en wacht op jouw merge** — een dagsessie
    mergt zijn eigen PR niet. Taak op `blocked`, want hij wacht op jou.
    Kanttekening van de checker, geen fout: de test toetst alleen de statische
    markup, dat `aria-pressed` bij een klik echt omklapt is gelezen en niet
    getest.
  - `hangar-prioriteit-score`, `weekly-review-automatic`, `quizzly-media-upload`
    — waren al `done`. Niets gebouwd, niets gepusht.
  - Bijvangst: de media-upload van vannacht is onafhankelijk nagelopen, 11 van
    de 12 regels gehaald. De uitzondering staat als taak
    `quizzly-media-read-authz` en is een vraag aan jou, geen bug.
- **Vijf PR's staan open.** quizzly#4 (vandaag, van deze sessie), quizzly#1
  (finalisatie, sinds 08-07), percentile#1 (F-16, écht conflict tegen `main`),
  percentile#3 (MVP launchable), learning-website#3 (C#-keten). De nachtrun laat
  percentile#1 en learning-website#3 al vier nachten bewust liggen: de eerste
  heeft een conflict in privacy-kritische bestanden, de tweede is gebouwd vóór
  het auto-merge-besluit. Die twee wachten echt op jou.
- **Drie account-brede nachtrun-besluiten** liggen nog bij jou (blocked taak
  `nightrun-limits-decisions`): vuurtijd versus je weekly reset, usage credits
  met een cap, en of er een inhaalrun bij moet. Achtergrond in
  `reference/nightrun-usage-limits.md`.
- **Eenmalige actie:** plak `reference/startprompt-nightrun.md` in de Routine op
  claude.ai. Zonder dat leest de nachtrun zijn regels nog steeds, maar via een
  verwijzing in `CLAUDE.md` in plaats van omdat het hem opgedragen is. Besluit
  `0005`.
- Nog steeds open van eerder: zeg wat Crew management moest worden of gooi hem
  weg; beslis waar Versa draait; de ideeën in je hoofd in `ideas/` zetten.
