# Night log

What the overnight run did, newest first. One short entry per night: the task,
the outcome, and anything it refused to do and why.

This exists so Ollie can see what happened while he slept without opening five
pull requests to find out.

---

## 2026-08-11

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/` beschikbaar —
de builder/checker-rolverdeling uit CLAUDE.md kan dus gebruikt worden zodra er
gebouwd wordt.

Open overnight-PR's bij start (branch-conventie `night/...` of
`claude/night-...`, zelfde telling als de vorige nacht): 3 —
`project-management#5` (`claude/night-hangar-prioriteit-score`, nog niet
gemerged in de default branch — de PR zelf bevat overigens al de volledige
afronding: taak op `done`, `hangar-priority-effort-escaping` als nieuwe
`ready`-taak, night-log-entry; er hangt dus niets in de lucht, hij wacht
alleen op merge), `percentile#1` (`night/percentile-f16-count-ladder`),
`learning-website#3` (`night/learn-csharp-chain`). (`quizzly#1` en
`percentile#3` zijn geen nachtrun-PR's — andere branch-conventie, niet
meegeteld, zelfde onderbouwing als de vorige nacht.) Dat is de grens uit
CLAUDE.md ("stop bij drie open overnight PR's") — dus vannacht wordt er
niets gebouwd. Direct naar stap 3.

**Aangescherpt: `quizzly-design-pass`** (inbox, M, "lichter en vriendelijker
app-chrome"). De oorspronkelijke Done means bundelde twee stappen die niet
hetzelfde soort werk zijn: een ontwerpvoorstel schrijven (onderzoek, geen
smaakbesluit) en dat voorstel doorvoeren (wél een smaakbesluit van Ollie).
Uitgezocht wat er staat: `src/app/globals.css` definieert het hele
app-chrome-palet in één `@theme`-blok (`--color-ink-50..950`,
`--color-brand-400..700`), en het is vandaag al consistent — geen losse
Tailwind `gray-`/`slate-`/`zinc-`/`neutral-` klassen ernaast in `src/app` of
`src/components` buiten de quiz-surface. Dat maakt "lichter en
vriendelijker" een echte richtingskeuze, geen opruimklus, en dat kan een
nachtrun niet voor hem beslissen.

Gesplitst in twee taken, zelfde patroon als `hangar-in-de-browser` stap 2
eerder:
- `quizzly-design-pass` (hernoemd naar "fase 1: ontwerpvoorstel") → `ready`,
  effort S. Done means: `docs/DESIGN.md` met 2-3 concrete richtingen (elk een
  eigen ink-/brand-ramp met hex, een berekende WCAG AA-contrastcheck, een
  voor/na voor dashboard + editor), harde randen expliciet herbevestigd
  (quiz-surface ongemoeid, 44px targets, focus-ring), één aanbeveling maar
  niets doorgevoerd. Wijzigt geen `src/`-code, dus geen testrisico.
- `quizzly-design-pass-toepassen` (nieuw) → `inbox`. Blijft liggen tot Ollie
  een richting uit `docs/DESIGN.md` kiest — pas dan is "consistent
  doorvoeren" een finish line die iemand kan afvinken.

**Bewust niet gedaan:** geen andere inbox-taak aangescherpt (`hangar-in-de-
browser` en `versa-hosting-besluit` wachten op Ollie's besluit resp. budget;
`lege-repos-beslissen` kan alleen Ollie invullen — alleen hij weet wat de
lege repo moest worden; `quizzly-legal-review-west` wacht expliciet op merge
van `quizzly#1`, dat nog open staat). Geen code gebouwd, geen tweede taak
aangeraakt, geen deploy, geen secrets, geen andere branch dan de eigen
`claude/night-2026-08-11` gebruikt, geen andere repo dan de Hangar zelf
nodig gehad.

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
