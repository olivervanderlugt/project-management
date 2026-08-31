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
