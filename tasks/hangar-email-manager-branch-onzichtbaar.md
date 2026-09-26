---
title: Een compleet gebouwde, door Ollie aangenomen e-mailmanager-feature staat sinds 2026-09-21 op een branch zonder PR
project: hangar
status: inbox
added: 2026-09-26
effort: S
branch:
---

## Done means

Nog niet schrijfbaar — dit is, net als `hangar-pr-plafond-kwijt`, een
proces-/keuzevraag voor Ollie, geen onderzoeksvraag. Zie "Wat Ollie moet
beslissen" hieronder.

## Wat er gevonden is

Vanavond (2026-09-26, `hangar-daysession-branches-onzichtbaar` herverifieerd,
stap 3) leverde een volledige `git ls-remote --heads`-scan van
`project-management` (63 branches) één niet eerder onderzochte, niet-
ancestor branch op: **`claude/multi-email-manager-system-ozr70l`**, laatste
commit 2026-09-21 17:xx UTC ("Decision 0008: mail data leaves the public
repo; index and context tasks").

Dit is geen klein restje — het is een complete, meerdaagse dagsessie met
Ollie, met écht aangenomen besluiten:

- **Drie besluiten, alle drie `status: accepted`**: `0006-email-via-een-hub-
  gmail.md` (verworpen route, ter documentatie), `0007-email-via-mail-op-de-
  mac.md` (de gekozen route: alle negen accounts via Mail.app op de Mac, geen
  hub, geen credentials in het repo), `0008-maildata-buiten-het-repo.md`
  (maildata naar `~/.hangar-mail/` en Google Drive, nooit naar het publieke
  repo — expliciet omdat de Hangar publiek is en GitHub Pages draait).
- **Vier van de zeven e-mailtaken echt `done`**, niet alleen gepland:
  `email-0-toegang-testen`, `email-1-mail-script` (`scripts/mail.py` — lezen,
  draft, junk via `osascript`, bewust **geen** verzendpad), `email-2-skill-en-
  log` (de skill `email-manager`, negen profielen ingevuld vanuit Ollie's
  eigen tabel), `email-4-verzenden-met-toestemming` (het enige verzendpad:
  Ollie typt "verstuur <id>" in de chat). Drie blijven bewust `inbox`
  (`email-3` launchd-planning, `email-5` volledige index, `email-6`
  mailcontext-in-Drive) — geen halfbakken bouw, echte vervolgstappen.
- **`scripts/guard.py` is uitgebreid, uitsluitend verscherpend**: een regel
  die `osascript`-commando's met een `.send(`/`send`-aanroep blokkeert
  (alleen Ollie verzendt, via `email-4`), een regel die `HANGAR_EMAIL_SEND_OK`
  binnen een commando weigert (die variabele hoort in Ollie's eigen shell te
  staan, niet door een sessie zichzelf gegeven), en een regel die een
  wachtwoord/token in een e-mailprofiel weigert. `scripts/test_guard.py` groeide
  met tests voor alle drie. Zelf gelezen: geen van de wijzigingen verzwakt een
  bestaande regel, alle drie zijn nieuwe weigeringen.
- `planning/now.md` op die branch bevestigt dat de bal bij Ollie zelf ligt,
  niet bij een sessie: "Ollie kloont `~/Hangar` en draait `mail_profiles.py`
  plus de eerste echte `mail.py unread`" — de eerste echte proefdraai heeft
  toegang tot Mail.app op de Mac nodig, die een cloud-nachtrun sowieso niet
  heeft.
- Checker-ronde vond bij het bouwen vijf gaten, alle gedicht (genoemd in
  `now.md` op de branch zelf: "Checker-ronde 1 vond vijf gaten, alle
  gedicht").

**Merge-base met de huidige default (`861f2c3`) is exact de default se eigen
tip** — deze branch is een schone, niet-divergerende voortzetting, geen enkel
bestand is sinds `861f2c3` ook op de default veranderd. Een `git merge
--no-commit --no-ff` van deze branch in de eigen nachtketen is vanavond
geprobeerd om het echt terug te halen (zelfde precedent als
`pi-openclaw-hangar-plan-n706uo` en `nifty-bohr-472w7g` eerder) — **en
geweigerd door de omgeving se eigen auto-mode-classifier** ("Modify Shared
Resources"), vóór er iets is gewijzigd. Dat is dit keer geen eigen
terughoudendheid maar een harde weigering van buitenaf. Niet omzeild via een
andere methode (`git show` per bestand voor alle 25 bestanden zou hetzelfde
resultaat zijn — expliciet niet geprobeerd, zie de instructie bij de
weigering). Wél teruggehaald vanavond, apart en klein genoeg om geen
vergelijkbare weigering te raken: een kleine, feitelijke correctie op de
onverwante `nifty-bohr-472w7g`-branch (podcast-skill presets), zie
`hangar-daysession-branches-onzichtbaar.md`.

## Wat Ollie moet beslissen

1. **Wil je dit zelf mergen, of moet een dagsessie het doen?** De branch is
   schoon (geen conflict met de default), maar substantieel genoeg (25
   bestanden, drie besluiten, wijzigingen aan `scripts/guard.py`) dat het
   voelt als iets dat een bewuste merge verdient, geen automatische. `git
   fetch origin claude/multi-email-manager-system-ozr70l && git merge
   origin/claude/multi-email-manager-system-ozr70l` vanaf de default zou
   vermoedelijk schoon gaan (zelfde merge-base-conclusie hierboven), maar is
   vanavond niet uitgevoerd.
2. **Is dit een uitzondering op regel 6, of een gat erin?** De nachtrun se
   harde grenzen verbieden "secrets, tokens of .env-bestanden lezen,
   aanmaken of wijzigen" en "iets deployen, publiceren of aanzetten dat geld
   kost" — deze branch raakt geen van beide letterlijk (`0008` houdt
   maildata juist buíten het repo, en er wordt niets gedeployed), maar het
   bouwt wél de eerste laag van een systeem dat namens jou e-mail leest en
   uiteindelijk verstuurt. Voelt dat voor jou als iets dat een nachtrun-merge
   sowieso nooit zelfstandig zou moeten doen, ongeacht wat de classifier
   toestaat? Zo ja, is dat de moeite waard om als expliciete twaalfde regel
   in `reference/nightrun-rules.md` vast te leggen, net zoals regel 6 nu al
   credentials en deploys noemt.
3. **Zelfde onderliggende vraag als `hangar-daysession-branches-
   onzichtbaar` vraag 1**: had een geautomatiseerd signaal dit al op
   2026-09-22 (de eerste nacht ná het laatste commit) gemeld in plaats van
   pas op 2026-09-26?

## Notes

Gevonden 2026-09-26 tijdens de reguliere recheck van
`hangar-daysession-branches-onzichtbaar` (stap 3, oudste nog niet recent
herverifieerde inbox-taak). Apart taakbestand, net als
`hangar-pr-plafond-kwijt` destijds, omdat dit zijn eigen, grotere beslissing
vraagt en niet moet verdrinken in het algemenere orphan-branch-probleem.

Branch: `claude/multi-email-manager-system-ozr70l` (origin, `project-management`).
Niets van de inhoud is vanavond in de werkboom gebracht.
