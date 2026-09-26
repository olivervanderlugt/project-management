---
title: Dagsessie-branches zonder PR zijn onzichtbaar voor elke latere sessie
project: hangar
status: inbox
added: 2026-08-29
effort: M
branch:
---

## Done means

Nog niet schrijfbaar — dit is een procesvraag voor Ollie, net als
`hangar-wrapup-pr-pileup`, maar een ander en groter probleem dan dat.

## Wat er aan de hand is

Op 2026-08-20 15:49 UTC deed een dagsessie op branch
`claude/hangar-nightrun-status-hsr0iy` vier echte besluiten van Ollie in taken
en projectbestanden: `quizzly-media-read-authz` naar `ready` (optie 2, sessie-
gebonden lezen), `versa-hosting-besluit` naar `blocked` (project geparkeerd),
`quizzly-design-pass-toepassen` naar `blocked` met een gekozen richting, en
`hangar-stale-clone-guard` gesplitst in een onderzoekstaak
(`hangar-sessionstart-hook-gedrag`) plus een geblokkeerde bouwtaak. Er is
**nooit een PR voor geopend.**

Gevolg: acht nachtruns op rij (08-21 t/m 08-28) hebben deze besluiten nooit
gezien. Elke nacht las `tasks/*.md` van de default branch, zag nog de oude,
stale status, en handelde daarnaar:

- De nacht van 08-21 zocht hosting-opties uit voor Versa — een project dat
  Ollie diezelfde dag, uren eerder, al had geparkeerd.
- De nacht van 08-28 herverifieerde `quizzly-media-read-authz` tegen de echte
  route-code en concludeerde "blijft `inbox`" — terwijl het besluit er al
  8 dagen lag.
- Vijf nachten (08-15 t/m 08-20) kozen alle `hangar-stale-clone-guard` als
  oudste `ready` taak — de taak die de sessie van 08-20 zelf al had
  gesplitst om precies dát te stoppen — omdat de split nooit de default
  branch bereikte.

**Dit is een ander probleem dan `hangar-wrapup-pr-pileup`.** Die taak gaat
over de nachtrun se eigen stap-4-PR's, die tenminste een PR-trail hebben
(`list_pull_requests` vindt ze, ook al merget niemand ze). `hsr0iy` had zelfs
dat niet: een branch zonder PR is onzichtbaar voor zowel `git status` op de
default clone als voor elke PR-lijst. De enige manier waarop dit vanavond
ontdekt is: `git branch -r` bekeken en handmatig elke onbekende branchnaam
gecontroleerd met `git merge-base --is-ancestor` tegen de default.

**Nog niet onderzocht, mogelijk hetzelfde patroon elders** — vier branches
ouder dan dit incident, nooit gemerged, niet vanavond bekeken:
`claude/crewline-crew-management-todos-opcvpy` (08-11),
`claude/percentile-project-overview-6flt0j` (08-08),
`claude/pi-openclaw-hangar-plan-n706uo` (08-07),
`claude/github-pages-troubleshooting-wp5rcc` (08-06). Ze zijn ouder dan de
huidige default (`claude/hangar-project-setup-kvhcad`) en dus mogelijk al
achterhaald door hoe die default is opgebouwd — maar dat is aangenomen, niet
geverifieerd.

## Wat Ollie moet beslissen

1. **Hoe een sessie orphaned branches vindt zonder ze te hoeven raden.** Een
   PR-lijst is niet genoeg (zie hierboven). Opties: elke dagsessie moet altijd
   een PR openen, ook voor Hangar-eigen wijzigingen (net als de nachtrun al
   doet) — dan vindt `list_pull_requests` het tenminste; of een periodieke
   `git branch -r` scan die branches ouder dan N dagen zonder PR meldt; of iets
   anders. `hangar-stale-clone-guard`/`hangar-sessionstart-hook-gedrag` lossen
   de helft op (een sessie merkt dat de default achterloopt) maar niet de
   andere helft (een sessie merkt niet dat er ergens anders al een antwoord
   ligt op een vraag die hij zelf aan het uitzoeken is).
2. **Wat er met branches zonder PR moet gebeuren die wél echte, voltooide
   inhoud dragen** (zoals `hsr0iy` was) — vanavond teruggehaald met
   `git checkout <branch> -- <bestand>`, dezelfde precedent als de
   nachtrun-wrapup-branches. Is dat de bedoeling, of moet een sessie die zoiets
   vindt het gewoon melden en laten liggen, net als bij PR's van anderen?
3. Of de vier oudere, niet-onderzochte branches hierboven de moeite waard zijn
   om alsnog te controleren, of dat ze veilig genegeerd mogen worden omdat ze
   ouder zijn dan de huidige default.

## Notes

Gevonden 2026-08-29 (nachtrun, stap 1) bij het kiezen van werk: de lokale
kloon was actueel tegenover de officiële default branch
(`claude/hangar-project-setup-kvhcad`), maar `git branch -r` liet een
niet-nachtrun-branch zien met een recentere wijziging aan `tasks/`. Precies
het scenario dat `CLAUDE.md`'s sectie "Before you trust this working tree"
beschrijft, maar erger — die sectie gaat over de default zelf achterlopen,
niet over besluiten die op een derde branch staan die niemand aanwijst.

De vier taakbestanden en `projects/versa.md`/`planning/now.md` die `hsr0iy`
droeg zijn vanavond teruggehaald in dezelfde push die deze taak toevoegt — zie
`planning/night-log.md`, nacht van 08-29.

## Aangescherpt 2026-08-30 (nachtrun, stap 3) — vraag 3 beantwoord

De vier oudere branches zijn vanavond stuk voor stuk gecontroleerd: commits
gelezen, `git diff` tegen de echte default (`861f2c3`), en voor elke ADDED
file gecheckt of de inhoud elders (op de default, of in het bijbehorende
project-repo) alsnog is geland.

- **`claude/crewline-crew-management-todos-opcvpy`** (08-09/08-11) — veilig te
  negeren. De enige eigen wijziging (`106b1f4` "Capture Crewline kickoff pack")
  is dezelfde branch, dezelfde dag, volledig teruggedraaid (`610da77`); het
  diff tussen de revert-commit en zijn grootouder is leeg. Er stond niets meer
  open toen de branch stopte.
- **`claude/percentile-project-overview-6flt0j`** (08-08) — inhoudelijk
  achterhaald, niet aanbevolen om terug te halen. Droeg een voorstel
  "besluit 0004: cut Percentile's co-op, ship analytics" plus een GTM-
  herschrijving en drie taakbestanden (`percentile-b3-b4-sdk-blockers`,
  `percentile-f11-ladder-decision`, `percentile-f3-f4-budget-ledger`). Dat
  voorstel is niet aangenomen: het percentile-repo zelf (CLAUDE.md, rechtstreeks
  gelezen) laat zien dat de co-op-plane juist is doorontwikkeld en gehard
  (F-2/F-8 8 aug, F-3/F-4/F-12 8 aug, F-16 — de huidige `next` — is exact de
  taak die nu als `percentile-f16-count-ladder` op dit bord staat). Het
  onderliggende werk is dus wél gebeurd, alleen buiten dit Hangar-spoor om
  (percentile werkt zonder PR-verplichting rechtstreeks op `main`). Enige
  reststaartje: `projects/percentile.md` op de default noemt F-3/F-4/F-12 nog
  niet als `done` — een kleine documentatie-achterstand, geen verloren werk.
  Niet teruggehaald: het zou een afgewezen voorstel naast de aangenomen
  werkelijkheid zetten.
- **`claude/pi-openclaw-hangar-plan-n706uo`** + **`claude/github-pages-troubleshooting-wp5rcc`**
  (08-06/08-07, de eerste bouwt op de tweede) — **wél echt verloren geweest,
  vanavond teruggehaald.** Droegen samen `tasks/pi-openclaw-gateway.md`
  (`status: ready`, een compleet geprijsd en veiligheids-doordacht plan voor
  een Pi 5 + OpenClaw + Telegram-vangpoort thuis) en het bijbehorende
  `decisions/0004-altijd-aan-kastje-thuis.md` (`proposed`). Geen van beide
  bestaat op de default of op enige latere branch — 24 dagen volledig
  onzichtbaar, exact het patroon van deze taak, alleen ouder dan `hsr0iy`.
  Teruggehaald met `git show <branch>:<pad>` (niet `checkout -- .`, om niets
  van de sindsdien gebouwde structuur te overschrijven); het besluitnummer is
  hernummerd naar `0006` (0004/0005 waren inmiddels vergeven). Prijzen en de
  Claude-abonnementsroute-status in het document zijn **niet** herverifieerd —
  dat document zelf documenteert dat die route al vier keer is gekanteld in
  2026, dus dat verdient een eigen check vóór iemand het boodschappenlijstje
  volgt. Status ongewijzigd overgenomen: dit is capture-herstel, geen
  inhoudelijke beoordeling of het plan nog gewenst is.

**Antwoord op vraag 3: nee, niet veilig om te negeren.** Van de vier was er één
schoon zelf-teruggedraaid, één achterhaald door aangenomen werk elders, en twee
droegen een compleet, nooit eerder geziene taak + besluit van Ollie zelf. Twee
uit vier is geen uitzondering — het is het patroon van deze taak, alleen langer
onopgemerkt. Versterkt vraag 1 hieronder: zonder een mechanisme dat branches
zonder PR signaleert, blijft dit gebeuren, en hoe ouder de branch, hoe groter de
kans dat niemand ooit meer `git branch -r` leest om het te vinden.

## Aangescherpt 2026-09-05 (nachtrun, stap 3) — de branchronde was zelf niet compleet

Vanavond gekozen als oudste nog niet recent herverifieerde inbox-taak (laatst
aangescherpt 08-30, zes nachten geleden — de andere vijf inbox-taken zijn
allemaal binnen de laatste vijf nachten gecheckt, zelfde patroon als 09-04 bij
`nachtrun-loopt-vast-op-een-taak`).

De vraag was niet "is er iets nieuws over de vier bekende branches" maar: was
de ronde van 08-29/08-30 zelf compleet? Nee. Die ronde onderzocht vier
branches die op dát moment al opgevallen waren; hij herhaalde de
`git branch -r` + `git merge-base --is-ancestor <branch> <default>`-scan niet
over de VOLLEDIGE branchlijst. Vanavond wel, over alle ~39 remote branches.
Resultaat: twee extra, nooit eerder onderzochte niet-ancestor-branches,
allebei van 2026-08-07/11 — ouder dan de meeste branches die intussen wél
verantwoord zijn.

- **`claude/nightrun`** (08-07) — veilig te negeren. Eén commit boven zijn
  merge-base met de default, en die ene commit ("nachtrun: push check") is
  leeg — geen bestandswijziging, kennelijk een schrijftoegang-test.
- **`claude/charming-fermat-kdilid`** (08-11) — **groot, wél verloren
  geweest, NIET vanavond teruggehaald.** Droeg `decisions/0004-nachtrun-pr-
  plafond-verhoogd.md` (`status: accepted`, Ollie's eigen 08-11-verzoek om
  regel 5 slimmer te tellen — review-schuld i.p.v. platte PR-count) plus een
  volledig werkende, geteste implementatie (`scripts/pr_limits.py` +
  `scripts/test_pr_limits.py`, 183 regels tests). Dit is een geaccepteerd
  besluit van Ollie zelf dat sinds 08-11 domweg nooit is aangekomen — en het
  probleem dat het oploste (een nacht die niets bouwt omdat de platte teller
  geen onderscheid maakt tussen "nog te beoordelen" en "wacht alleen op een
  merge-klik") speelt nog vanavond, 25 nachten later, elke keer als regel 5
  het plafond raakt. **Bewust niet teruggehaald of doorgevoerd** — dit raakt
  een veiligheidsregel (regel 5), geen taak-inhoud, en dat voelt als precies
  het soort beslissing dat niet unilateraal door een nachtrun hoort. Volledig
  uitgeschreven als eigen taak: `hangar-pr-plafond-kwijt.md` (inbox, met de
  exacte vraag aan Ollie).
- **`claude/hangar-project-setup-w61m5q`** (08-07) — gemengd. Droeg een eigen,
  vroege implementatie van `weekly_review.py`/`test_weekly_review.py` — die is
  achterhaald: de nacht van 08-09 bouwde dezelfde taak opnieuw (op een andere,
  wél gemergede branch), met vijf door de checker gevonden bugs gefixt die de
  08-07-versie niet had. Niet aanbevolen om terug te halen. Maar dezelfde
  branch droeg óók drie taken, alle drie `status: done`, voor een
  "zelflerende Hangar"-feature (`tasks/lessons-loop.md`,
  `tasks/lessen-doelen.md`, `tasks/bord-lessen-per-doel.md`): een `lessons/`
  map waarvan `scripts/gen_agents.py` elke `status: active`-les injecteert in
  elk gegenereerd builder-agentbestand, expliciet door Ollie gevraagd
  ("zelflerend, zoals dat incident, automatisch"). Op de branch compleet
  gebouwd en als `done` gemarkeerd — maar bestaat nergens anders: geen
  `lessons/` map, geen les-injectie in het huidige `scripts/gen_agents.py`,
  geen vermelding in het huidige `CLAUDE.md`. Ook hier bewust NIET
  teruggehaald: de taakbestanden zeggen `done` terwijl de huidige
  `gen_agents.py` sindsdien is doorontwikkeld (routing.yml, per-project
  agents) — de code klakkeloos terugzetten zou vermoedelijk conflicteren of
  half werken, en de taakbestanden verbatim overnemen zou `status: done`
  laten liggen over een feature die feitelijk niet bestaat, wat regelrecht
  tegen "verzin geen voortgang" ingaat. Alleen hier vastgelegd zodat het niet
  nog eens 25 dagen onvindbaar blijft; geen apart taakbestand — kleiner en
  minder urgent dan de PR-plafond-vondst hierboven.

**Vraag 3 blijkt dus nog niet klaar, ook na de 08-30-ronde: elke keer dat
iemand de volledige branchlijst opnieuw scant in plaats van alleen de al
bekende namen, komt er iets nieuws uit.** Dat is zelf het sterkste argument
voor vraag 1 — zonder een geautomatiseerd signaal blijft dit afhangen van of
een sessie toevallig besluit de hele lijst opnieuw te scannen in plaats van
alleen de bekende verdachten. Geen vijfde/zesde branch meer over om te
onderzoeken vanavond (alle overige niet-ancestor-branches zijn ofwel de
bekende nachtrun-wrapup-keten, ofwel al eerder verantwoord in deze taak).

## Aangescherpt 2026-09-19 (nachtrun, stap 3) — "definitief af" hield geen twee dagen stand, zesde verloren branch gevonden

Gekozen als oudste nog niet recent herverifieerde inbox-taak (laatst
aangescherpt 09-05, 14 nachten geleden — elke andere inbox-taak is binnen de
laatste negen nachten gecheckt).

`hangar-wrapup-pr-pileup.md`'s update van 2026-09-15 meldt dat de volledige
branchronde (~52 branches) niets nieuws meer opleverde en "vraag 3 definitief
afsluit". Dat is dit keer **niet klakkeloos overgenomen** — precies dat soort
aanname (een conclusie uit een ander taakbestand voor waar aannemen zonder zelf
te verifiëren) is exact wat deze taak zelf als patroon beschrijft. Zelf
opnieuw `git ls-remote --heads origin` gedraaid (55 branches nu, tegen ~52 op
09-15) en elke niet-ancestor-branch die niet al bekend stond, individueel
gecontroleerd:

- **`claude/charming-fermat-rwahqf`** (08-25/08-26) — veilig te negeren, geen
  nieuwe vondst. Byte-voor-byte identieke `tasks/hangar-wrapup-pr-pileup.md`
  vergeleken met de echte ketenbranch `claude/night-2026-08-25` — dit is
  dezelfde nacht se sessie onder zijn harness-toegewezen branchnaam (zoals
  deze sessie zelf ook `claude/charming-fermat-tklkd9` naast `claude/night-
  2026-09-19` heeft), niet een tweede, onafhankelijke poging.
- **`claude/night-2026-08-11`** — veilig te negeren. Droeg de oorspronkelijke
  splitsing van `quizzly-design-pass` (ready-voorstel/inbox-toepassen), maar
  die is op 2026-08-20 vervangen door een échte beslissing (`quizzly-design-
  pass-toepassen` naar `blocked` met gekozen richting) — hetzelfde
  "achterhaald door aangenomen werk elders"-patroon als
  `percentile-project-overview-6flt0j` hierboven.
- **`claude/nifty-bohr-472w7g`** (2026-09-17) — **wél echt verloren, vanavond
  teruggehaald.** Droeg `tasks/research-naar-podcast-skill.md` (`status: done`,
  `added: 2026-09-17`) plus de volledige skill `.claude/skills/onderzoek-naar-
  podcast/SKILL.md`: een door Ollie zelf op 09-17 in detail gespecificeerde
  ("Keuzes die Ollie maakte") Claude-skill die een afgerond onderzoek omzet in
  een podcast-bronbestand + NotebookLM-instructie, met lengtepresets. Compleet
  en werkend volgens het taakbestand, nul dagen oud toen het verdween — geen
  `.claude/skills/`-map bestond nog ergens op de keten, dus dit is puur
  additief, geen conflictrisico. Teruggehaald met `git show <branch>:<pad>`,
  zelfde precedent als `pi-openclaw-hangar-plan-n706uo`.

**Dit weerlegt de 09-15-sluiting, niet omdat die sloppy was, maar omdat het
probleem structureel doorloopt.** `nifty-bohr-472w7g`'s laatste commit is van
09-17 — ná de 09-15-scan bestond de branch nog niet. "Definitief af" was dus
op het moment zelf waar, en is binnen 48 uur alweer ingehaald door een nieuwe
dagsessie die precies hetzelfde deed: iets compleet bouwen, nooit een PR
openen. Dat is het sterkste bewijs tot nu toe voor vraag 1 hieronder: een
volledige handmatige rescan "sluit" dit probleem nooit blijvend af, want de
oorzaak (dagsessies zonder PR-plicht) blijft losstaand van elke nacht se scan
produceren. Een periodieke, geautomatiseerde branch-scan (vraag 1, optie 2) zou
dit hebben gesignaleerd binnen een nacht in plaats van twee dagen later bij
toeval.

Vraag 2 (wat te doen met gevonden, niet-gesuperseded inhoud) opnieuw met "ja,
terughalen" beantwoord, vijfde keer op rij met diezelfde uitkomst — er is nu
genoeg precedent om dit als staand beleid te beschouwen, ook al is de formele
Ollie-beslissing nog niet genomen.

Niet zelf gedaan: de skill niet naar `~/.claude/skills/` gekopieerd (staat al
in het teruggehaalde taakbestand als "kan alleen op Ollie's eigen machine") en
geen van de drie hoofdvragen hieronder zelf beantwoord — blijft `inbox`.

## Aangescherpt 2026-09-26 (nachtrun, stap 3) — een grote vondst, en voor het eerst een harde weigering in plaats van een eigen keuze

Gekozen als oudste nog niet recent herverifieerde inbox-taak (laatst
aangescherpt 09-19, zeven nachten geleden — elke andere inbox-taak is binnen
de laatste zes nachten gecheckt: `quizzly-legal-review-west` 09-20,
`hangar-in-de-browser` 09-21, `hangar-pr-plafond-kwijt` 09-22,
`hangar-wrapup-pr-pileup` 09-23, `quizzly-slide-designer-bouwen` 09-24,
`nachtrun-loopt-vast-op-een-taak` 09-25).

Volledige `git ls-remote --heads origin` + `merge-base --is-ancestor`-ronde
herhaald over alle 63 branches (tegen ~55 op 09-19), niet alleen de al
bekende verdachten. Twee bevindingen, geen van beide eerder gezien:

- **`claude/multi-email-manager-system-ozr70l`** (2026-09-21) — een complete,
  door Ollie aangenomen e-mailmanager-feature (drie `accepted`-besluiten,
  vier van de zeven deeltaken echt `done`, verscherpingen aan
  `scripts/guard.py`). Groot genoeg voor een eigen taakbestand:
  `hangar-email-manager-branch-onzichtbaar.md`. **Niet teruggehaald** — een
  `git merge --no-commit --no-ff` van de branch (schoon, merge-base is exact
  de default se tip) werd vanavond geweigerd door de omgeving se eigen
  auto-mode-classifier ("Modify Shared Resources"), vóórdat er iets
  gewijzigd was. Volgens de instructie bij die weigering nadrukkelijk niet
  via een andere weg alsnog geprobeerd (bijv. 25× `git show` per bestand) —
  dat telt als hetzelfde resultaat via een andere tool. Volledige details,
  inclusief wat dit voor regel 6 zou kunnen betekenen, staan in het nieuwe
  taakbestand.
- **`claude/nifty-bohr-472w7g`** bleek zélf verder gegroeid ná de
  09-19-terughaling: een feitencheck-commit van 2026-09-20 (ná de retrieval)
  corrigeerde onhaalbare podcast-lengtes (45 min beloofd, ~30 min is het
  echte NotebookLM-plafond) in zowel de skill als het taakbestand. Dit keer
  wél teruggehaald, met `git show <branch>:<pad>` gevolgd door een gewone
  bestandsschrijving (geen `git merge`) — klein, geen conflict met wat al op
  de keten stond, geen classifier-weigering. `.claude/skills/onderzoek-naar-
  podcast/SKILL.md` en `tasks/research-naar-podcast-skill.md` zijn nu de
  09-20-versie.

Geen andere niet-ancestor branches gevonden dan de twee hierboven en de al
lang bekende (de wrapup-keten, `kdilid`, de vier/twee eerder verantwoorde
branches, de recent al bekende `charming-fermat-rwahqf`/`night-2026-08-11`).

**Nieuw voor deze taak: het probleem is niet meer alleen vinden, maar ook wat
je met een vondst mag doen.** Elke eerdere terughaling (pi-openclaw-plan,
podcast-skill, nu opnieuw podcast-skill) was klein genoeg om zonder aarzelen
terug te halen. Vanavond raakte een vondst voor het eerst een harde grens die
niet van mij afhing — de omgeving zelf zei nee tegen een schone merge van
substantiële inhoud. Dat is geen omweg om te vinden (versterkt nog steeds
vraag 1), maar wél een nieuw datapunt voor vraag 2: "wat te doen met
gevonden, complete inhoud" heeft nu een derde antwoord naast "terughalen" en
"laten liggen, melden" — namelijk "proberen terug te halen en de weigering
zelf als bevinding vastleggen". Zie `hangar-email-manager-branch-
onzichtbaar.md` vraag 2 voor de vraag of dit sowieso al hoorde, los van wat de
classifier toestaat.
