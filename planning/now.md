---
updated: 2026-08-19
focus: Acht PR's wachten op jouw merge — vier daarvan van vandaag, alle vier gecheckt
---

- **Crew management is geen leeg repo meer (2026-08-19).** De hele MVP is vanaf de
  desktop gepusht. De eerste-sessie-checklist liep groen van begin tot eind — install,
  typecheck, 64/64 tests, build, en de Playwright-smoketest draaide voor het eerst
  écht (3/3, geen fixes nodig). `gitleaks` over de volledige historie: schoon. Een
  analyse in vier sporen leverde een `TODO.md` in het repo op, op doel gesorteerd,
  elk item met een `file:line`.
  - Drie bevindingen doen ertoe, en geen ervan crasht: **skill-matching heeft nog
    nooit gedraaid** (de enige aanroeper geeft een lege lijst mee, en dan krijgt
    iedereen de volle punten), **meerdaagse events kijken alleen naar dag één**, en
    **marge en payroll rekenen met verschillende uren**. Ze geven stilletjes een
    verkeerd antwoord — precies het soort fout dat een groene testsuite niet vangt.
  - Bijvangst: de e2e-job in CI hing 40+ minuten zonder timeout op
    `playwright install --with-deps`. Gevonden doordat de eerste PR hem live liet
    zien, gefixt, draait nu in 1m31s met een plafond van 15 minuten.
  - Er zat **geen enkel crewlid** in het repo: de seed leest CSV's die in
    `.gitignore` staan. Er is nu `pnpm db:seed-demo` — 100 verzonnen crewleden in
    een gereserveerde `CREW-9xxx`-reeks, die echte records niet kan raken.
  - Landingspagina staat live op https://olivervanderlugt.github.io/crew-management-system/
    (Pages stond al aan maar had nooit gebouwd — er stond niets op het ingestelde pad).
    **Dat is een landingspagina, geen demo:** de app is server-rendered en draait niet
    op Pages. Een echte klikbare preview is Vercel + Supabase, ~15 minuten, gratis.
  - Wat het nog nooit heeft gedaan: tegen een echte database draaien. `.env.local`
    staat vol placeholders. Dát is wat het blokkeert, geen enkel code-item.

- **Tweede ronde af (2026-08-14).** Drie taken gebouwd, twee al gecheckt en
  goedgekeurd, alle drie wachten op jouw merge:
  - **project-management#11** — `hangar-priority-effort-escaping`. Gecheckt, en de
    checker deed een negatieve controle: oude code terug, suite faalt. De test
    vangt echt iets.
  - **quizzly#5** — `quizzly-chrome-contrast-bugs`. Vier WCAG-fixes, elke ratio
    twee keer onafhankelijk herrekend. De checker keurde ronde 1 af omdat
    `.app-input::placeholder` was blijven staan; gefixt, hercheck groen.
  - **quizzly#6** — `quizzly-slide-designer`, alleen `docs/SLIDE-DESIGNER.md`
    (922 regels). Gecheckt en goedgekeurd: elke `file:line` in het document is
    door de checker afgedrukt en vergeleken, en het beweert nergens een
    GIPHY-voorwaarde die het niet heeft kunnen lezen.
  - `hangar-stale-clone-guard` is aangescherpt en staat nu op `ready`, met één
    voorbehoud dat de bouwer eerst zelf moet verifiëren (hoe `SessionStart`-hooks
    zich echt gedragen).
  - Bijvangst, inmiddels **bevestigd** en op `ready`:
    `quizzly-presentation-broadcast-ongefilterd`. `presentation` gaat echt buiten
    `toPublicPayload()` om naar elke speler. Vandaag lekt er niets — het schema
    heeft vijf velden die de speler moet zien en Zod stript de rest — maar er is
    geen filter dat de zesde tegenhoudt. Vastleggen bij de code, met een test.

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
- Nog steeds open van eerder: beslis waar Versa draait; de ideeën in je hoofd in
  `ideas/` zetten. **Crew management is beantwoord** — zie de eerste bullet.
