# Night log

What the overnight run did, newest first. One short entry per night: the task,
the outcome, and anything it refused to do and why.

This exists so Ollie can see what happened while he slept without opening five
pull requests to find out. Only the nightly Routine writes here. A session Ollie
started himself leaves its trail in `planning/now.md` and in the task files —
day work in this file would cost it the one thing it is for. Rules and
reasoning: `reference/nightrun-rules.md`, decision `0004`.

---

## 2026-08-29

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/`-rollen
(`hangar`, `hangar-checker`, `hangar-manager`) beschikbaar.

**Kloon-check — schoon tegen de default, maar dat was niet het hele verhaal.**
`git fetch` tegen de echte default branch (`claude/hangar-project-setup-kvhcad`,
niet `main` — deze repo heeft geen `main`) liet zien dat de lokale kloon
actueel was: `861f2c3`, dezelfde commit als de laatste merge (08-20). Op dat
punt leek er niets bijzonders aan de hand. Pas bij het kiezen van werk viel
`git branch -r` op: een branch, `claude/hangar-nightrun-status-hsr0iy`, met een
recentere wijziging aan `tasks/` dan wat waar dan ook gemerged stond. Zie
hieronder — dit werd de avond.

**Stap 1 — drie vastgelopen nachtrun-PR's, opnieuw geverifieerd, dus geen
bouw.** Over alle zeven gekoppelde repo's, elk via de GitHub API opnieuw
gecontroleerd (zelfde sha, zelfde `mergeable_state`, `updated_at` ==
`created_at`, dus écht ongewijzigd sinds de vorige nachten):

- `percentile#1` — `mergeable_state: dirty`, nog steeds een echt conflict.
- `learning-website#3` — `mergeable_state: clean`, nog steeds gebouwd vóór
  besluit 0004, nog steeds niet gemerged.
- `project-management#13` (`hangar-stale-clone-guard`) — nog steeds
  `mergeable_state: dirty`, nog steeds `ship: false` op de vereiste
  live-hook-verificatie.

Drie is regel 5's plafond. Geen bouw vanavond, rechtstreeks naar stap 3 —
maar niet voordat een veel grotere ontdekking eerst is opgelost.

**Een verborgen dagsessie-branch, 8 nachten oud, teruggehaald.**
`claude/hangar-nightrun-status-hsr0iy` bevatte één commit, 2026-08-20 15:49
UTC: vier echte besluiten van Ollie ("Vier besluiten van Ollie verwerkt: queue
van 2 naar 4 ready"). Er is **nooit een PR voor geopend** — onvindbaar via
`list_pull_requests`, onzichtbaar voor `git status` op elke latere kloon.
Geverifieerd, niet aangenomen: elke nachtrun van 08-21 tot en met 08-28 las
`tasks/quizzly-media-read-authz.md` nog als `status: inbox` met de oude
twee-opties-vraag — de nacht van 08-28 herverifieerde de route-code er zelfs
netjes tegenaan, zonder te weten dat Ollie het besluit al 8 dagen eerder had
genomen. De nacht van 08-21 zocht hosting-opties uit voor Versa, een project
dat Ollie diezelfde dag, uren eerder, al had geparkeerd. En vijf nachten
(08-15 t/m 08-20) kozen stuk voor stuk `hangar-stale-clone-guard` als oudste
`ready` taak — de taak die dezelfde 08-20-sessie zelf al had gesplitst om
precies dat te stoppen, in een besluit dat nooit de default bereikte.

Teruggehaald met `git checkout <branch> -- <bestand>` — dezelfde precedent als
eerdere nachten al gebruikten voor hun eigen weesbranches (08-16, 08-20,
08-26, 08-28): iemand anders' al voltooide, niet-controversiële besluiten
overnemen is geen beleidsbeslissing. Vier bestanden gerecovered zonder
conflict (`hangar-sessionstart-hook-gedrag.md` nieuw, `ready`;
`quizzly-semantische-tokens.md` nieuw, `ready`; `hangar-stale-clone-guard.md`
naar `blocked`; `quizzly-design-pass-toepassen.md` naar `blocked` met een
gekozen richting; `projects/versa.md` naar `parked`). Twee bestanden hadden
een echt conflict met later, onwetend onderzoek en zijn met de hand
samengevoegd: `quizzly-media-read-authz.md` (Ollie's `ready`-besluit blijft
leidend, de latere hercheck van de routecode is toegevoegd als bevestiging
dat de code sindsdien niet is gedreven) en `versa-hosting-besluit.md`
(Ollie's parkeerbesluit blijft leidend, het 08-21-onderzoek naar hosting-opties
is bewaard als naslag voor wanneer Versa weer aangaat, met een duidelijke
noot dat het gedaan is vóórdat het parkeerbesluit bekend kon zijn). Ook
meegenomen: de vier bestanden die de nacht van 08-28 al had teruggehaald uit
de nachtrun-eigen weesbranches (`hangar-in-de-browser.md`,
`hangar-wrapup-pr-pileup.md`, `quizzly-legal-review-west.md`) — die stonden
zelf ook nog niet op de default.

Nieuwe taak geschreven: `tasks/hangar-daysession-branches-onzichtbaar.md`
(`inbox`). Dit is een ánder en groter probleem dan `hangar-wrapup-pr-pileup`:
die PR's zijn tenminste vindbaar via de GitHub API; een branch zonder PR is
dat niet. Vier oudere, nooit-gemergede branches (`crewline-crew-management-
todos-opcvpy` 08-11, `percentile-project-overview-6flt0j` 08-08,
`pi-openclaw-hangar-plan-n706uo` 08-07, `github-pages-troubleshooting-wp5rcc`
08-06) zijn opgemerkt maar **niet** onderzocht vanavond — ze zijn ouder dan de
huidige default en mogelijk al achterhaald, maar dat is aangenomen, niet
geverifieerd. Staat als open vraag in de nieuwe taak.

**Stap 3 — `nachtrun-loopt-vast-op-een-taak` aangescherpt, niet alleen
herbevestigd.** Vraag 2 (moet `hangar-stale-clone-guard` opgesplitst worden?)
bleek al beantwoord door de zojuist teruggehaalde `hsr0iy`-commit zelf — een
mooie illustratie van precies het probleem: een besluit was genomen, maar
onzichtbaar voor 8 nachten. Vraag 3 (weesbranches) is opnieuw gecontroleerd:
van de twee is er nog maar één écht wees (`night/hangar-stale-clone-guard`,
08-15, nog steeds zonder PR); de andere is inmiddels de head van PR #13.
Vraag 1 (een faalteller) blijft volledig open, nu met een tweede, bredere
aanleiding.

**Niet gedaan, met opzet:** geen taak gebouwd (regel 5, drie vastgelopen
PR's); geen van de drie aangeraakt; de negen openstaande stap-4/dagsessie-PR's
op de Hangar (`#11`, `#13`, `#15`-`#22`) niet gemerged, gesloten of
samengevoegd — nog steeds `hangar-wrapup-pr-pileup`'s beslissing, niet de
mijne; de vier oudere onbekende branches niet onderzocht (zie boven); de
vraag of `reference/startprompt-nightrun.md` letterlijk in de Routine is
geplakt niet uitgezocht — de prompt die vanavond vuurde is duidelijk een
Nederlandstalige, herstructureerde variant van die tekst, wat er wel of niet
op wijst; niet verder getrokken dan de constatering in `planning/now.md`.
`planning/now.md` herschreven (niet alleen aangevuld) om de stapel oude,
inmiddels-`done` bullets niet nog een nacht mee te slepen — de informatie
staat in de taakbestanden zelf.

## 2026-08-20

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/`-rollen
(`hangar-checker`) beschikbaar — builder/checker-verdeling uit CLAUDE.md
gebruikt.

**Kloon-check.** `git fetch` + vergelijking tegen de default branch
(`claude/hangar-project-setup-kvhcad`): lokale kloon was actueel, geen
gemiste merges.

**Stap 1 — open overnight-PR's: 2, dus bouwen.** Over alle zeven gekoppelde
repo's: acht PR's open. Zes dagsessie-werk dat op Ollie's eigen merge wacht
(project-management#11, quizzly#4/#5/#6, quizzly#1, percentile#3). Twee echte
vastgelopen nachtrun-PR's, allebei opnieuw gecontroleerd, ongewijzigd:
`percentile#1` (`night/percentile-f16-count-ladder`, `mergeable_state: dirty`,
nog steeds een echt conflict) en `learning-website#3` (`night/learn-csharp-chain`,
`mergeable_state: clean`, gebouwd vóór besluit 0004). Twee, niet drie — onder
de grens van regel 5, dus doorgebouwd.

**Taakkeuze.** Twee `ready`-taken: `hangar-stale-clone-guard` (`added:
2026-08-14`) en `quizzly-media-orphan-cleanup` (`added: 2026-08-15`). Oudste
eerst, dus `hangar-stale-clone-guard`.

**Weesbranch gevonden bij het pushen, niet ervoor.** De kloon-check aan het
begin zag niets bijzonders — pas de `git push` van de eigen taakbranch werd
geweigerd (`fetch first`, geen netwerkfout). `origin/claude/night-hangar-stale-clone-guard`
bleek al twee weespogingen te dragen (`Night 2026-08-17`, `Night 2026-08-18`),
allebei alleen een statuswissel + logregel, geen code. Precies het patroon dat
deze taak zelf moet gaan signaleren — nu nog handmatig ontdekt via een
geweigerde push. Niet weggegooid en niet als tweede branch verdergegaan
(precedent uit de 08-16- en 08-18-regels hierboven): eigen drie commits
gemerged bovenop de weesbranch, het enige echte conflict (de `status`-regel in
het taakbestand) opgelost naar de eigen, verder gevorderde versie, dashboard
herbouwd, gepusht. Hun twee logregels (08-17, 08-18) zijn in die merge
meegekomen en landen op de default zodra de PR merget — hier niet dubbel
opgeschreven.

**Stap 2 — gebouwd, NIET gemerged: `hangar-stale-clone-guard` (S) →
project-management#13.** `scripts/staleness.py` (`SessionStart`-hook,
`hookSpecificOutput.additionalContext`) + `scripts/test_staleness.py` (16
tests) + de hookregel in `.claude/settings.json`. Twee `hangar-checker`-rondes:
de eerste vond vier echte gaten (fetch-timeout-tak ongetest, geen
proces-niveau bewijs voor de offline-case, een onbenoemde aanname over "geen
upstream ingesteld" die precies de nachtrun-branches zou stilleggen, en de
verplichte vooraf-verificatie stond nergens op schrift) — alle vier gefixt.
De tweede ronde hield terecht vast op één punt: de taak eiste een levende
wegwerp-hook-test van `additionalContext`, niet secundair onderzoek. Wat er
wél is gedaan — de officiële hooks-referentie rechtstreeks gelezen plus een
gesloten upstream-issue (`anthropics/claude-code#16538`) dat bevestigt dat
alleen plugin-hooks last hebben van het bekende additionalContext-gat — is
sterk documentair bewijs maar geen live proef. Een subagent hier doorloopt
geen volledige `claude`-CLI-`SessionStart`-cyclus; een écht losse sessie
zou een wegwerp-repository nodig hebben als `source_url`, wat onevenredig
voelde voor deze verificatiestap. Niet gemerged: de checker zei `ship: false`
en de regel is fixen-of-blocked, nooit forceren. Taak op `blocked`, exacte
vraag voor Ollie staat in het taakbestand. Branch gepusht, PR #13 open, bewust
niet gemerged.

**Stap 3 — inbox aangescherpt: `lege-repos-beslissen` opgelost, niet alleen
aangescherpt.** `olivervanderlugt/crew-management-system` bleek niet langer
leeg: `git log` op GitHub bevestigt commits van 2026-08-19 15:44 tot 19:10 UTC
vanaf Ollie's eigen machine — de hele MVP, plus drie tiers uit een
`VERBETERPLAN.md` opgelost. `projects/crew-management-system.md` was diezelfde
dag al herschreven met een echte `## What this is` en `next`, gecommit op de
default vóór vanavond (`7d099ee`). De finish line van deze taak was dus al
gehaald door een dagsessie, buiten de taak-flow om. Op `done` gezet.

**Niet gedaan, met opzet:** geen tweede taak opgepakt (regel 1); geen van de
twee stuck PR's aangeraakt (conflict resp. pre-auto-merge, ongewijzigd sinds
vorige keer); de oudere, nog stalere weespoging `night/hangar-stale-clone-guard`
(van 08-15) met rust gelaten — niet gebruikt, niet verwijderd; geen andere
inbox-taken herverifieerd dan de ene die onderzocht is (regel 2: één taak);
`hangar-stale-clone-guard`-PR niet gemerged ondanks groene tests — een
checker-`ship: false` op een expliciet vereiste verificatiestap forceer je
niet weg.

## 2026-08-16

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/`-rollen
(`quizzly`, `hangar-checker`) beschikbaar — builder/checker-verdeling uit
CLAUDE.md gebruikt.

**Kloon-check vóór alles.** `git fetch` + vergelijking tegen de default branch
(`claude/hangar-project-setup-kvhcad`) legde iets bloot: een branch
`claude/night-2026-08-15` bestond op de remote met één commit erbovenop de
default die nooit gemerged was, en er was nooit een PR voor geopend. Diff
gelezen: een echte, correcte stap-3-taak (`quizzly-media-read-authz` gesplitst
in de authz-vraag zelf plus een nu-`ready` `quizzly-media-orphan-cleanup`) —
geen halfbakken of kapotte staat. De nacht van 08-15 is kennelijk gestopt na
die commit, vóór stap 4 (night-log + wrap-up-PR). Niet opnieuw gedaan of
weggegooid: fast-forward gemerged op deze branch, zodat het werk niet verloren
gaat. Geen enkele `doing`-taak stond nog open (regel 10 niet van toepassing —
dit was een hele niet-afgemaakte run, geen achtergebleven taak).

**Stap 1 — open overnight-PR's.** Geteld over alle zeven aangekoppelde repo's,
niet alleen de Hangar: acht open PR's in totaal, maar de meeste zijn
dagsessie-werk dat wacht op Ollie's eigen merge (project-management#11,
quizzly#4/#5/#6, quizzly#1, percentile#3) — een dagsessie mergt zijn eigen PR
niet, dus die zijn niet "vastgelopen nachtrun-werk". Van de nachtrun zelf staan
er twee nog open, allebei al meerdere nachten bewust met rust gelaten en
vanavond opnieuw gecontroleerd, niet aangenomen:
- **`percentile#1`** (`night/percentile-f16-count-ladder`) — `mergeable_state:
  dirty`, nog steeds een echt conflict tegen `main` in privacy-kritische
  bestanden. Met rust gelaten.
- **`learning-website#3`** (`night/learn-csharp-chain`) — `mergeable_state:
  clean`, maar gebouwd vóór het auto-merge-besluit (0004) door een andere
  sessie. Met rust gelaten, zelfde oordeel als eerdere nachten.

Twee stuck, niet drie: onder de grens van regel 5, dus doorgebouwd.

**Taakkeuze.** Twee `ready`-taken delen `added: 2026-08-14`:
`quizzly-presentation-broadcast-ongefilterd` en `hangar-stale-clone-guard`.
Geen chronologisch onderscheid, dus tiebreak op het bord's eigen
prioriteitsscore (zelfde precedent als 2026-08-13): 710 tegen 680 — de
quizzly-taak wint. (`quizzly-media-orphan-cleanup`, net hersteld uit de 08-15
kloon, is `added: 2026-08-15` — jonger, dus geen kandidaat vanavond ondanks een
hogere score; regel 1 is oudste-eerst, niet hoogste-score-eerst.)

**Stap 2 — gebouwd en gemerged: `quizzly-presentation-broadcast-ongefilterd`
(S) → quizzly#7.** Builder (`quizzly`-agent) legde op branch
`claude/dreamy-knuth-n4hya3` vast waarom `presentation` ongefilterd naar elke
speler gaat: commentaar bij de emit (`server/realtime/engine.ts:345`) én bij
`toPublicPayload()` (`src/lib/question-schema.ts`), plus — eigen, gemotiveerde
keuze — een derde bij `presentationSchema` zelf in `src/lib/theme.ts`, met de
redenering dat wie een veld toevoegt naar het schema kijkt, niet naar de emit.
Nieuwe test `src/lib/theme.test.ts` bewaakt dat een toekomstig verplicht veld
breekt. Twee zinnen in `docs/ARCHITECTURE.md`. Trio groen, 106→108 tests. Eén
afwijking gemeld: `docs/SLIDE-DESIGNER.md` (waar de taak naar §6 verwijst)
bestaat niet op `main`, alleen op de nog niet gemergede quizzly#6 — de bouwer
werkte vanuit de taakomschrijving zelf in plaats van dat document.

`hangar-checker` deed een echte adversariële poging: zelf de twee comment-
plekken gelezen, zelf een negatieve controle gedraaid (tijdelijk een verplicht
veld toegevoegd, beide nieuwe tests faalden écht, teruggezet), zelf de
`Game.quizSnapshot`-herparse-aanname op `server/realtime/gameServer.ts:149`
geverifieerd in plaats van aangenomen, zelf de volledige trio gedraaid, en
bevestigd dat er geen enkele gedragswijziging in de diff zit en niets buiten de
vijf genoemde bestanden geraakt is. Verdict: `ship: true`, niets onvermeld
gebleven.

CI op quizzly#7 afgewacht tot die zelf groen was, daarna pas gemerged (`8bbae69`,
besluit 0004 — de checker's pass is het reviewmoment). Taak op `done`, branch
`claude/dreamy-knuth-n4hya3`.

**Stap 3 — inbox aangescherpt: geen van de zeven kon naar `ready`.** Alle
resterende inbox-taken opnieuw gecontroleerd, niet aangenomen dat ze nog
kloppen: `hangar-in-de-browser`, `quizzly-slide-designer-bouwen`,
`quizzly-design-pass-toepassen`, `quizzly-legal-review-west` (nog steeds
`quizzly#1` niet gemerged) en `versa-hosting-besluit` wachten alle vijf
onveranderd op een smaak- of geldbesluit van Ollie zelf — geen onderzoeksvraag
die een nachtrun voor hem kan beslissen. `quizzly-media-read-authz` is al
gesplitst (zie boven, uit de herstelde 08-15-commit) en de resterende
authz-vraag blijft om dezelfde reden `inbox`. Echt herverifieerd, niet alleen
herlezen: `lege-repos-beslissen` — `crew-management-system` heeft nog steeds
nul commits (`git log` bevestigt "does not have any commits yet" op de
aangekoppelde kloon vanavond). Geen wijziging, blijft `inbox`.

**Niet gedaan, met opzet:** geen tweede taak opgepakt ondanks resterend budget
(regel 1/3); geen van de twee stuck PR's aangeraakt (conflict resp. pre-
auto-merge, zie boven); geen enkele inbox-taak naar `ready` geforceerd zonder
een echte Done means; geen behandeling van de vijf dagsessie-PR's die op
Ollie's eigen merge wachten — dat is zijn keuze, niet de nachtrun s'.
Status → `done`, branch → `claude/dreamy-knuth-n4hya3`.

## 2026-08-14

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/`-rollen
(`quizzly`, `hangar-checker`, …) beschikbaar — builder/checker-verdeling uit
CLAUDE.md wordt gebruikt.

**Stap 1 — open overnight-PR's: 2, dus bouwen.** `night/percentile-f16-count-ladder`
(percentile#1, `mergeable_state: dirty` — echt conflict tegen `main`) en
`night/learn-csharp-chain` (learning-website#3, `mergeable_state: clean`, geen
CI in die repo, maar gebouwd/gecheckt vóór het auto-merge-besluit) staan al
sinds 2026-08-07 open. Zelfde oordeel als vorige nachten: met rust gelaten —
een conflict-rebase of het met-terugwerkende-kracht mergen van een oude,
niet-door-mij-gecheckte PR hoort niet onbeheerd te gebeuren. Twee stuck PR's,
niet drie: geen queue-herstel nodig, door naar bouwen.

Oudste `ready`-taak: drie kandidaten (`quizzly-media-upload`,
`quizzly-slide-designer`, `quizzly-wachtwoord-toggle`) delen exact dezelfde
`added: 2026-08-08` én zijn in dezelfde commit toegevoegd — geen chronologisch
onderscheid mogelijk. Tiebreak op slug-alfabet, dezelfde secundaire sleutel die
`build.py`'s eigen prioriteitssortering (regel 270) al gebruikt: **`quizzly-media-upload`**.

**Stap 2 — gebouwd: `quizzly-media-upload` (M) → gemerged als quizzly#3.**
Builder (`quizzly`-agent) bouwde de volledige feature op `night/quizzly-media-upload`:
upload i.p.v. alleen URL-plakken, grootte-cap (5 MiB, op echte bytes),
magic-byte sniffing (client-Content-Type wordt nergens vertrouwd), EXIF-strip
via een `sharp`-her-encode naar WebP, path-traversal-bestendige key-resolving,
owner-only op zowel het vraagafbeelding- als het cover-image-schrijfpad
(`Quiz.coverImage` was een dode kolom, nu echt bruikbaar), `docker-compose.yml`
kreeg het `media-uploads`-volume, README/SECURITY.md de limieten. Trio
(typecheck/test/build) groen, 106 tests (was 72).

`hangar-checker` deed een echte adversariële poging het tegendeel te bewijzen:
zelf de trio gedraaid, EXIF-strip losgetest op alle drie toegestane formaten
(niet alleen JPEG, wat de builder zelf alleen had aangetoond), beide
owner-checks nagelopen, path-traversal actief geprobeerd, en de interpretatie
van "alleen door de quiz-eigenaar" (schrijven, niet lezen — spelers zijn
anoniem en moeten de afbeelding wel kunnen zien) expliciet beargumenteerd i.p.v.
aangenomen. Verdict: finish line volledig gehaald.

Eén complicatie, geen makkelijk excuus om te wachten: de branch was gecut vóór
commit `41e8abf` op `main` landde (dezelfde compose-parse-fix, onafhankelijk
door een andere sessie gemaakt) — een echt, klein merge-conflict (alleen
commentaartekst verschilde). Zelf `origin/main` erin gemerged, het conflict met
de hand opgelost, en de volledige trio opnieuw zelf gedraaid op de gemergede
staat vóórdat er gepusht werd — groen. PR #3 geopend, CI (GitHub Actions)
afgewacht tot die zelf groen was, daarna pas gemerged. Taak op `done`, branch
`night/quizzly-media-upload`.

**Stap 3 — inbox aangescherpt: geen van de zes kon naar `ready`.** Alle zes
inbox-taken zijn opnieuw gecontroleerd (niet aangenomen dat ze nog kloppen):
`hangar-in-de-browser` en `versa-hosting-besluit` wachten expliciet op
besluiten van Ollie; `quizzly-legal-review-west` wacht nog op het mergen van
`quizzly#1` (nog open); `quizzly-slide-designer-bouwen` wacht op
`docs/SLIDE-DESIGNER.md`, dat pas ontstaat zodra de `ready`-taak
`quizzly-slide-designer` gebouwd wordt (niet vannacht, één taak per nacht);
`quizzly-design-pass-toepassen` wacht op Ollie's kleurrichting uit
`docs/DESIGN.md` — geen vervolgcommit sinds 2026-08-13 die op een keuze wijst.
`lege-repos-beslissen` opnieuw gecontroleerd: `crew-management-system` staat
nog steeds op nul commits, blokkade ongewijzigd — recheck vastgelegd in de
taak zelf. Niets kon eerlijk een concrete Done means krijgen; niets gepromoveerd.

**Nog steeds open, niet aangeraakt (zelfde oordeel als 2026-08-13):**
`night/percentile-f16-count-ladder` (echt conflict, privacy-kritische bestanden
— een rebase daar hoort niet onbeheerd op andermans taak te gebeuren) en
`night/learn-csharp-chain` (mergeable maar gebouwd vóór het auto-merge-besluit
— met rust gelaten, zoals eerdere nachten ook oordeelden).

**Niet gedaan, met opzet:** geen tweede taak opgepakt ondanks resterend budget
(regel 1/3: één taak per nacht, stoppen zodra hij af is); geen van de twee
oude stuck PR's aangeraakt (zie boven); geen enkele inbox-taak naar `ready`
geforceerd zonder een echte Done means.
Status → `doing`, branch → `night/quizzly-media-upload`.

## 2026-08-13

**Start.** Subagents-check: Task/Agent-tool en `.claude/agents/`-rollen (o.a.
`quizzly`, `hangar-checker`) beschikbaar — de builder/checker-rolverdeling
uit CLAUDE.md wordt dus echt gebruikt.

**Stap 1 — queue-herstel, geen bouwwerk uit de letterlijke telling.** Open
overnight-PR's bij start: 4 — `project-management#6`, `project-management#7`,
`percentile#1`, `learning-website#3`. Uitgezocht *waarom* elk vastzit
(regel 5) in plaats van er verder niets mee te doen:

- **`project-management#7`** — `mergeable_state: clean`, drie checks groen
  (`build`, `deploy`, `verify`), wijzigde alleen `tasks/`, `night-log.md` en
  het gegenereerde dashboard. Volgens besluit 0004 had dit vanzelf moeten
  mergen en is dat gewoon niet gebeurd. Direct gemerged — geen codewijziging,
  geen risico.
- **`project-management#6`** — was oorspronkelijk in dezelfde situatie, maar
  raakte pas écht in conflict doordat `#7` intussen op dezelfde stale basis
  was geland (beide voegen bovenaan iets toe aan `night-log.md` en raken het
  gegenereerde dashboard). De inhoud zelf (het splitsen van
  `quizzly-design-pass` in een onderzoeksfase en een bouwfase) stond niet ter
  discussie, dus met de hand overgezet naar een nieuwe branch bovenop de
  actuele default, alle 7 Hangar-testsuites nogmaals groen gedraaid, gemerged
  als `project-management#8`, en `#6` gesloten met een verwijzing ernaar.
- **`percentile#1`** — echt conflict tegen `main` in privacy-kritische
  bestanden (`release-gate.ts`, `adversarial.test.ts`). Met rust gelaten —
  een rebase daar hoort niet onbeheerd op andermans taak te gebeuren.
- **`learning-website#3`** — `mergeable_state: clean`, maar gebouwd en
  gecheckt door een andere sessie van vóór het auto-merge-besluit. Met rust
  gelaten, zoals eerdere nachten ook oordeelden.

Na dit herstel staan nog 2 PR's écht vast (niet 4) — onder de grens van
regel 5. Dus toch doorgebouwd vanavond in plaats van meteen naar stap 3.

**Taakkeuze:** de vier `ready`-taken die op 2026-08-08 zijn aangemaakt stonden
gelijk op `added`. Het bord's eigen prioriteitsscore (`dashboard/build.py`,
score → added → slug als sorteersleutel) wijst `quizzly-design-pass`
("fase 1: ontwerpvoorstel") aan als hoogste (score 710, gelijk met
`quizzly-wachtwoord-toggle`, gewonnen op slug-alfabet).

**Stap 2 — `quizzly-design-pass` gebouwd.** De `quizzly`-builder-agent schreef
`docs/DESIGN.md` (612 regels) op branch `claude/night-quizzly-design-pass` in
de Quizzly-repo: drie richtingen (A "Daglicht" licht, B "Haard" donker/warm,
C "Twee standen" licht+donker), elk met een volledige 11-staps
`--color-ink-*`-ramp en `--color-brand-*`-ramp, WCAG-contrast per paar
zelf berekend (niet aangenomen), expliciete herbevestiging per richting dat
`.quiz-surface`/`--q-*`/44px-targets/focus-ring ongemoeid blijven, een
voor/na voor dashboard en editor, en één aanbeveling (richting B) die niet is
doorgevoerd. Geen `src/`-wijziging; trio (`typecheck`/`test`/`build`) groen.
PR olivervanderlugt/quizzly#2.

De `hangar-checker`-agent deed de vijandige review: eigen herimplementatie
van de WCAG-luminantieformule op alle 47 gepubliceerde ratio's (allemaal
correct op één cosmetische afronding in de kritiek-tekst na, die geen enkele
tabel beïnvloedt), eigen `git diff --stat` tegen de PR (alleen `docs/DESIGN.md`,
612 toevoegingen, nul `src/`), en zelf `npm run typecheck && npm test && npm
run build` gedraaid op de PR-commit. Verdict: **DONE**. PR gemerged
(besluit 0004 — de checker's pass is het reviewmoment, niet Ollie 's ochtends).
Taak op `done`.

**Bijvangst, meteen gevangen als taak (regel "Capture, then build"):** het
DESIGN.md-onderzoek en de checker's herrekening vonden vier echte, van de
gekozen richting onafhankelijke a11y/CSS-bugs in de bestaande chrome
(`text-ink-500` faalt AA op 44 plekken, `.btn-primary:hover` zakt net onder
AA, `.app-input` heeft geen 3:1-randcontrast, vijf `brand`-tinten worden
gebruikt maar bestaan niet in `@theme`). Nieuwe taak
`quizzly-chrome-contrast-bugs`, direct op `ready` gezet (geen smaakbesluit
nodig — mechanische fixes, gelden ongeacht welke richting uit DESIGN.md wint)
maar niet vannacht gebouwd (limiet: één bouwtaak per nacht).

**Stap 3 — inbox aangescherpt.** `quizzly-legal-review-west` herchecked:
`quizzly#1` (de finalization/launch-PR) staat nog open, dus de blokkade geldt
onveranderd. Die PR bevat naast compliance-features ook een versiebump naar
1.0.0 en `fly.toml` — sowieso niet iets dat een nachtrun zelf mag mergen
(regel 6). Blijft `inbox`, met de expliciete vraag aan Ollie genoteerd in de
taak (wanneer wil je `quizzly#1` mergen?). De overige inbox-taken
(`hangar-in-de-browser`, `versa-hosting-besluit`, `lege-repos-beslissen`,
`quizzly-design-pass-toepassen`, `quizzly-slide-designer-bouwen`) wachten
allemaal op een besluit van Ollie zelf (geld, smaak, of "wat moest deze lege
repo worden") en zijn bewust niet opnieuw aangescherpt — kort geverifieerd
dat er niets veranderd is (bijv. `crew-management-system` heeft nog steeds
nul commits).

**Bewust niet gedaan:** geen tweede bouwtaak (limiet: één per nacht — de
queue-herstelcommits van stap 1 zijn geen "bouw", er is geen `src/`-code
in aangeraakt). `percentile#1` en `learning-website#3` niet aangeraakt (zie
stap 1). Geen deploy, geen secrets, geen `quizzly#1` gemerged (dat is Ollie's
launch-besluit). Andere branches dan de eigen `claude/charming-fermat-kb8te9`
(Hangar) en `claude/night-quizzly-design-pass` (Quizzly) niet gebruikt.


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

**Herstel-noot (toegevoegd 2026-08-13):** deze entry stond alleen in de
niet-gemergede PR `project-management#6` en ontbrak dus in de echte
geschiedenis. Hersteld door de nachtrun van 2026-08-13 bij het oplossen van
`#6`'s merge-conflict met `#7` — zie de 2026-08-13 entry hieronder voor de
volledige toedracht.


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
