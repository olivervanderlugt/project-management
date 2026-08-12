# Night log

What the overnight run did, newest first. One short entry per night: the task,
the outcome, and anything it refused to do and why.

This exists so Ollie can see what happened while he slept without opening five
pull requests to find out.

---

## 2026-08-12

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/` beschikbaar —
maar er is deze nacht niets gebouwd (zie hieronder), dus de builder/checker-
rolverdeling kwam niet in actie. Geen inline-fallback nodig.

**Stap 1 — 3 open overnight-PR's, dus niet gebouwd.**
`project-management#6` (`claude/night-2026-08-11`), `percentile#1`
(`night/percentile-f16-count-ladder`), `learning-website#3`
(`night/learn-csharp-chain`). Op de grens — direct naar stap 3, maar eerst
uitgezocht *waarom* elk vastzit, zoals regel 5 vraagt, in plaats van er verder
niets mee te doen:

- **`percentile#1`** — echt conflict. `mergeable_state: dirty`, bevestigd door
  een proefmerge in een los worktree: conflicten in `CLAUDE.md`,
  `src/core/privacy/release-gate.ts` en `test/adversarial.test.ts`. Oorzaak:
  `main` liep door na deze PR (7 aug) met PR #2 "fix/consent-and-jurisdiction"
  (9 aug, de F-3/F-4/F-12-fixes), die dezelfde bestanden raakte. CI op de
  PR-commit zelf staat groen (`test`, 2×). Niet opgelost vannacht — een
  privacy-kritische rebase hoort niet onbeheerd te gebeuren op een taak die
  niet de mijne is vanavond.
- **`project-management#6`** — ook een echt conflict, bevestigd op dezelfde
  manier: `dashboard/index.html` (gegenereerd bestand, triviaal) en
  `planning/night-log.md` (beide nachten voegen bovenaan een entry toe —
  klassiek append-only-conflict) tegen de echte default branch
  (`claude/hangar-project-setup-kvhcad`, niet `main` — dit is geen `main`-repo
  met een `main`-branch). Checks op de PR-commit: 3× groen (`build`, `deploy`,
  `verify`). Niet opgelost vannacht, om dezelfde reden: die PR is niet van
  deze sessie en de conflict-resolutie (welke night-log-tekst wint) is een
  editoriale keuze die bij de oorspronkelijke inhoud hoort.
- **`learning-website#3`** — **geen** conflict en **geen** falende check:
  `mergeable_state: clean`, 0 check-runs (deze repo heeft geen PR-CI, alleen
  een deploy-on-push-naar-main workflow). Dit is dus niet "vastzittend" in de
  zin van regel 5 — er zit hier geen GitHub-blokkade. Toch niet zelf gemerged:
  de PR is drie dagen oud, gebouwd en gecheckt door een sessie die niet deze
  sessie is, en vóór regel 3 (het besluit van 2026-08-10) bestond — ik heb de
  checker-stap niet zelf herhaald en wil geen vreemd werk ongezien in een
  live, publiek gedeployde app mergen op een onbewaakte nachtrun. Voor Ollie:
  dit is de PR die het snelst en veiligst te mergen is als hij zelf even
  kijkt — er is hier niets dat blokkeert.

Netto: de telling van "3 open PR's" klopt letterlijk, maar slechts 2 van de 3
zijn ook daadwerkelijk GitHub-geblokkeerd; de derde ligt open om een reden die
niet in regel 5 past (nooit zelf gemerged na het bouwen, van vóór het
auto-merge-besluit). Vannacht dus niets gebouwd, conform de simpele telling
uit stap 1.

**Stap 3 — `quizzly-slide-designer` aangescherpt.** Was een visietaak die zijn
eigen onderzoek al beschreef zonder een bouwbare finish line. Gesplitst,
zelfde patroon als eerder bij `hangar-in-de-browser` en `quizzly-design-pass`:

- `tasks/quizzly-slide-designer.md` → **fase 1**, nu `ready` (effort M):
  schrijf `docs/SLIDE-DESIGNER.md` in de Quizzly-repo — de volledige
  mogelijkhedenruimte (per-slide design, emoji, GIF's, geluid/muziek,
  transitions, hostsoundboard, live preview), haalbaarheid expliciet getoetst
  aan de echte architectuur (theming zit vandaag op `Quiz`, niet op
  `Question` — per-slide is dus een schema-uitbreiding; moet door
  `Game.quizSnapshot` en `toPublicPayload()` heen blijven werken), de
  licentie-/privacyhaken (GIPHY, muziekrechten — `docs/LEGAL.md` noemt vandaag
  geen media van derden), en één aanbevolen, in één sessie bouwbare fase 1.
  Geen `src/`-wijziging.
- `tasks/quizzly-slide-designer-bouwen.md` → **fase 2**, nieuw, blijft `inbox`
  tot het document bestaat én Ollie een fase kiest — dat is een smaakbesluit,
  geen onderzoeksvraag.

Grondslag gecheckt in de echte Quizzly-repo (niet aangenomen): `src/lib/theme.ts`
bevestigt theming per quiz, `prisma/schema.prisma` bevestigt `Game.quizSnapshot`,
`docs/LEGAL.md` bevat inderdaad geen enkele vermelding van media van derden.

**Bewust niet gedaan:** geen van de drie vastzittende/open PR's zelf gemerged
of geconflicteerd-opgelost (zie boven — twee zijn echte conflicten die niet
van vannacht zijn, één is mergeable maar ongezien-vreemd-werk-mergen op een
live app voelt niet als "kijk eerst waarom" maar als forceren voorbij een
grens die er niet expliciet voor vannacht stond). Geen andere inbox-taak
aangescherpt (`hangar-in-de-browser` / `versa-hosting-besluit` /
`lege-repos-beslissen` wachten nog steeds op Ollie's besluit resp. budget;
`quizzly-legal-review-west` wacht expliciet op het nog-open `quizzly#1`;
`quizzly-design-pass` is al gesplitst in het nog-open `project-management#6`
— opnieuw splitsen zou dat werk dupliceren). Geen code gebouwd, geen deploy,
geen secrets aangeraakt, geen andere repo dan de Hangar zelf en een
lees-only-verkenning van Quizzly nodig gehad.


## 2026-08-10

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/` beschikbaar —
builder/checker-rolverdeling van CLAUDE.md wordt dus echt gebruikt. Open
overnight-PR's bij start: 2 (`percentile#1` `night/percentile-f16-count-ladder`,
`learning-website#3` `night/learn-csharp-chain`) — onder de grens van 3, dus
gebouwd. (`quizzly#1` en `percentile#3` zijn geen nachtrun-PR's — andere
branch-conventie, niet meegeteld.)

**Taak: `hangar-prioriteit-score`** (oudste `ready`, `added: 2026-08-08`,
project `hangar` → repo is de Hangar zelf, geen aparte clone nodig). Gebouwd
op branch `claude/night-hangar-prioriteit-score`: `weights.yml` (nieuw, plat
`slug: gewicht`, gezaaid uit de "Aanbevolen volgorde" in
`reference/project-prioritering.md` — de ●-tabel zelf telt gelijk op tot een
tie tussen Versa/Percentile/Learn/Hangar en kon dus niet direct als gewicht
dienen), een deterministische score in `dashboard/build.py` uit vier
factoren (status, projectgewicht, effort, ouderdom) met één uitleg-
commentaarblok erbij, een "Dit nu"-regel bovenaan een nieuwe
prioriteitstabel op het bord, en `scripts/test_priority.py` (30 tests). De
`hangar-builder`-agent bouwde, de `hangar-checker`-agent deed de vijandige
review — dus de builder/checker-rolverdeling uit CLAUDE.md is écht gebruikt,
niet de inline-fallback. Checker draaide alles zelf opnieuw (build tweemaal
diffen, alle 7 testsuites, 15 kapotte-invoer-probes, CLAUDE.md-diff = 0
regels) en keurde de taak `DONE`. Taak op `done`, niet naar main gepusht —
gaat als PR.

De checker vond drie niet-blokkerende gebreken. Twee zijn bewust genoteerd en
niet aangepakt (project-gewicht buiten het gedocumenteerde bereik 1-5 kan de
status-voorrang doorbreken — geen eis uit de Done means, alleen een extra
garantie die de bouwer zelf toevoegde; een test die de echte
`dashboard/index.html` wegschrijft, onschadelijk zolang de build
deterministisch blijft). Het derde — een dubbele HTML-escape die een lege
`effort:` als de letterlijke tekst `&amp;mdash;` toont in plaats van een
gedachtestreepje — is meteen gevangen als nieuwe taak
`hangar-priority-effort-escaping` en, omdat de exacte regel en fix al bekend
waren uit de check, in dezelfde nacht direct aangescherpt naar `ready` (dit
telt niet als een tweede bouw-taak vannacht; er is geen regel code voor
geschreven).

**Aangescherpt:** naast de escaping-taak hierboven zijn de overige inbox-
taken bekeken en bewust met rust gelaten: `quizzly-design-pass` /
`quizzly-legal-review-west` / `quizzly-slide-designer` vragen elk een
voorstel dat Ollie eerst moet zien (smaak, juridisch, visie) — geen
onderzoeksvraag die een nachtrun voor hem kan beslissen. `hangar-in-de-
browser` is al grotendeels aangescherpt in eerdere nachten; de resterende
stappen 1 en 4 wachten op zijn besluiten (API-budget/secret, resp. een
besluit dat 0001 vervangt). `lege-repos-beslissen` en `versa-hosting-
besluit` zijn hetzelfde: onderzoek lost ze niet op, een keuze van Ollie wel.

**Bewust niet gedaan:** geen tweede taak gebouwd (limiet: één per nacht).
Geen deploy, geen secrets aangeraakt, geen andere branch dan de eigen
`claude/night-hangar-prioriteit-score` (taak) en `claude/night-2026-08-10`
(dit afsluitende blok) gebruikt. Geen andere repo aangeraakt dan de Hangar
zelf — deze taak had er geen nodig.


## 2026-08-09

**Subagents beschikbaar bij start** (Task-tool + `.claude/agents/` werkten
gewoon) — de builder/checker-rolverdeling uit CLAUDE.md is dus echt gebruikt,
niet de inline-fallback. Open overnight-PR's bij start: 2
(`percentile/night/percentile-f16-count-ladder`,
`learning-website/night/learn-csharp-chain`) — onder de grens van 3, dus
gebouwd.

**Taak: `weekly-review-automatic`** (oudste `ready`, `added: 2026-08-06`,
project `hangar` → repo is de Hangar zelf). Gebouwd:
`scripts/weekly_review.py` + `scripts/test_weekly_review.py` (23 tests) op
branch `claude/night-weekly-review-automatic`, PR
olivervanderlugt/project-management#3. Eerste versie ging naar de
`hangar-checker`-agent voor een vijandige review tegen de `## Done means`;
die vond vijf echte bugs (stale cache doordat een gecachte clone alleen
`git fetch` draaide zonder ooit tegen een remote-tracking ref te loggen, een
lege repo verward met een onbereikbare, onbereikbare repo's die stilzwijgend
uit de uitvoer vielen, een eerste run zonder eerdere week die de volledige
geschiedenis van elke repo in één bestand dumpte, en een handgeschreven
sectie buiten Wins/Slipped/Next week die een herhaalde run wiste). Alle vijf
gefixt, elk met een regressietest, checker's bevindingen zaten dus niet in
wat uiteindelijk gepusht is. Bewust NIET tegen het echte
`planning/weekly/2026-W32.md` gedraaid — vandaag valt nog in ISO-week 32,
hetzelfde bestand dat Ollie al met de hand schreef; een eerste echte run had
zijn Wins overschreven met automatisch afgeleide regels. Geverifieerd tegen
een synthetische toekomstige week in een losse tijdelijke map. Taak op
`done`.

**Aangescherpt:** `nachtrun-subagents-kapot` (inbox, S) → gesloten als `done`
zonder één regel code. De branch die de notities noemden
(`claude/hangar-nightrun-push-issue-njdjly`, regel 8 "No subagents? Play both
roles yourself" in CLAUDE.md) bleek al gemerged in de default branch —
merge-commit `139192e`, 2026-08-08 11:52 UTC+2, ruim voor deze run. Deze
run is er zelf het bewijs van: subagents bleken beschikbaar, dus de
`hangar-checker` deed de echte vijandige check hierboven in plaats van een
inline zelf-check. Details in de taak zelf.

**Bewust niet gedaan:** geen tweede taak gebouwd (limiet: één per nacht).
Geen andere inbox-taken aangescherpt (`hangar-in-de-browser`,
`lege-repos-beslissen`, `versa-hosting-besluit` wachten alle drie
expliciet op een besluit van Ollie — niet iets dat onderzoek oplost;
`quizzly-design-pass`/`quizzly-legal-review-west`/`quizzly-slide-designer`
zijn nieuwer en bewust overgeslagen omdat `nachtrun-subagents-kapot` een
scherpe, met bronvermelding te bewijzen bevinding had). Geen deploy, geen
secrets aangeraakt, geen andere branch dan de eigen twee van vannacht
gebruikt.

---

## 2026-08-08

**Taak: `learn-live-preview` (oudste `ready`, gelijk oud met
`weekly-review-automatic` — zelfde commit; S gekozen boven M).** Uitkomst:
gesloten als `done` zonder één regel code. De finish line bleek op 2026-08-07
al gehaald in een andere sessie en nooit afgevinkt: `deploy.yml` staat op
`main` van `learning-website`, de laatste Pages-run op het huidige
main-commit (54d9d78) is `success`, en `projects/learning-website.md` had de
`preview:`-URL al. De site zelf kon vannacht niet opnieuw geladen worden — de
sandbox blokkeert egress naar github.io — dus "site laadt" leunt op de
Pages-run plus de browser-verificatie van 2026-08-07 die in het projectbestand
staat. Is de site 's ochtends stuk: taak heropenen.

**Aangescherpt:** `hangar-in-de-browser` (inbox, L). Stap 2 losgetrokken als
nieuwe `ready` taak `hangar-prioriteit-score` (S, volledig lokaal, gratis).
Genoteerd dat stap 3 grotendeels al bestaat (`routing.yml` + agents), en dat
stap 1 en 4 op besluiten van Ollie wachten (API-budget + secret; besluit dat
0001 vervangt). Paraplu blijft `inbox`.

**Bewust niet gedaan:** geen tweede taak gebouwd (één per nacht, ook al kostte
de eerste geen code); de nachtrun-selectieregel niet aangepast aan de nieuwe
score-taak (regelwijziging = Ollie); geen verse browser-check van de live site
(egress geblokkeerd — eerlijk genoteerd in de taak in plaats van geclaimd). De
project-builder-agents en de checker waren in deze sessie niet aanroepbaar
(geen subagent-mechanisme beschikbaar); omdat er niets gebouwd is, is er ook
geen diff die een checker had moeten afkeuren — de done-verklaring leunt op de
hierboven genoemde externe bewijzen. Open overnight-PR's bij start: 0.

---

## 2026-08-07 — daytime manager session (Ollie present)

Not an overnight run — Ollie drove this one, but it followed the same
manager/builder/checker rules, so it belongs here.

**Shipped, both as PRs for Ollie to merge (nothing auto-merged to `main`):**

- **Learn — C#/.NET chain** (PR olivervanderlugt/learning-website#3, branch
  `night/learn-csharp-chain`). Three nodes (prog-csharp → -2 → -3), skills
  csharp/dotnet/methods → covered, coverage 22/6/18. Opus built, checker
  refuted the first pass (rendering: 39 fenced code blocks would have
  collapsed to one line — a bug that also hit already-merged lessons), builder
  fixed it with a RichText fence renderer, checker shipped the fix, manager
  browser-verified the rendering in both themes end-to-end. .NET SDK 10.0.302
  installed to execute every quoted output for real.
- **Percentile — F-16** (PR olivervanderlugt/percentile#1, branch
  `night/percentile-f16-count-ladder`). Published counts → k-threshold bands;
  one-query shortfall-explanation leak closed. Checker refuted the first pass
  (the bisection attack still worked via the public dominance-cap constant, and
  a guard was a strawman); builder retracted the overclaim, closed the prose
  leak, and re-labeled the residual honestly as KNOWN-OPEN (it's F-6's root
  cause, not F-16's). Tests 200/200.

**Shipped directly to the Hangar branch (no PR — Hangar convention):**

- **Dashboard redesign** — build.py rewritten around an all-projects status
  view + "waiting on you" strip + per-project Preview buttons (live vs derived
  Pages URL, never the code page). Manager added a missing `<meta charset>`.
- **Night-run vs usage limits** — researched (findings in
  `reference/nightrun-usage-limits.md`), implemented overnight rules 8–10
  (trail-before-work, stale-`doing` sweep, downgrade on limit pressure). Three
  account-level mitigations only Ollie can decide are parked as a blocked task.

**Refused / left for Ollie:** did not enable usage credits or change the
routine schedule (costs money / needs his usage-reset time). Did not build
`weekly-review-automatic` despite it being `ready` — it writes to the same
Hangar repo the dashboard redesign was rewriting, and two writers in one tree
is the exact failure the rules forbid. Left the F-6 dominance-cap oracle open
on purpose — it's the audit's next item, not this task's.

---

## 2026-08-07 — first run produced nothing (fixed)

- The nachtrun fired at 00:04 UTC but its Routine had **no repository attached**:
  the session woke up in an empty VM with no clone of the Hangar and no push
  credentials. Nothing reached GitHub — no commits, no branch, no PR, and this
  log stayed empty. Its prompt also targeted `claude/hangar-project-setup-kvhcad`,
  which is the repo's default branch and another session's working branch.
- Ruled out: the guard and autosave hooks. All guard tests pass and every
  command a nightrun would use is allowed.
- Fix, same day: first patched via a dedicated persistent session with the repo
  attached (a live check confirmed it could push to `claude/nightrun`), then
  replaced by the real thing: Ollie recreated the Routine in the claude.ai UI
  with all seven repos attached, so every run clones them with push access —
  no runtime repo-attaching, no standing session. The temporary trigger and
  session were removed, the broken trigger deleted. Next run: tonight 00:04 UTC.
