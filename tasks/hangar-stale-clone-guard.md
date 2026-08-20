---
title: Een sessie moet merken dat zijn kloon achterloopt vóór hij werk uitdeelt
project: hangar
status: blocked
added: 2026-08-14
effort: S
branch: claude/night-hangar-stale-clone-guard
---

## Done means

Een `SessionStart` command hook in `.claude/settings.json`, uitgevoerd door een
nieuw `scripts/staleness.py` (optie 1, niet optie 2 — onderbouwing hieronder),
die:

- `git fetch` doet met een harde tijdslimiet in het script zelf (bv. `timeout=5`
  op de subprocess-aanroep), plus een korte hook-`timeout` in `settings.json`
  (bv. `8`) als backstop — de default timeout voor command-hooks ligt rond de
  600s, veel te lang als grens voor iets dat op elke sessiestart het netwerk op
  gaat;
- **stil is** (geen `additionalContext`, exit 0, geen output) wanneer: de lokale
  HEAD gelijk is aan of vóór ligt op de default branch van `origin`, er geen
  upstream/remote is ingesteld, HEAD detached staat, of de `fetch` faalt of de
  tijdslimiet overschrijdt — precies de gevallen waarin `autosave.sh` ook stil
  blijft;
- **alleen spreekt** — via `hookSpecificOutput.additionalContext`, zodat het als
  tekst in de sessiecontext landt zonder een tool-aanroep te kosten — wanneer de
  lokale HEAD écht achter de default branch van `origin` ligt: hoeveel commits,
  en desnoods de bestandsnamen sinds (`git log --oneline HEAD..origin/<default>`
  is genoeg, geen diff nodig).

Threshold voor "spreek": elke commit erachter, geen ondergrens. Het incident van
08-14 ontstond na zes nachten, maar het patroon (agent bouwt iets dat al gemerged
is) kan al na één nacht optreden — er is geen veilige "kleine" achterstand.

Zit alleen in déze repo, niet in de losse projectrepos. Het incident ging over de
kloon van de Hangar zélf, waarin een sessie `tasks/*.md` las en op basis daarvan
agents uitdeelde. Een builder-agent voor een projectrepo krijgt een scoped
opdracht per dispatch (`.claude/agents/`, `scripts/dispatch.py`) en heeft dat
"lees oude status, deel zelf werk uit"-patroon niet. Doet dat patroon zich later
wél voor in een projectrepo, dan is dat een nieuwe aanleiding — niet iets om nu
al aan te nemen.

Test: `scripts/test_staleness.py`, in de stijl van `scripts/test_guard.py` en
`scripts/test_preview.py` (module laden via `importlib`, geen netwerk in de tests
zelf, werken op een tijdelijke git-repo):

- lokale HEAD == remote default → geen `additionalContext`, exit 0
- lokale HEAD N commits erachter → context vermeldt N en de branchnaam
- geen remote/upstream ingesteld → stil, exit 0
- detached HEAD → stil, exit 0
- `fetch` faalt (offline gesimuleerd) of overschrijdt de tijdslimiet → stil,
  exit 0, geen exception, en de test bewijst dat de aanroep terugkeert binnen
  tijdslimiet + marge (geen hang)

`python3 scripts/staleness.py` blijft ook los draaibaar, zoals `guard.py` en
`preview.py`, zodat hij zonder echte sessiestart te testen is.

**Eén ding zelf verifiëren vóór je bouwt:** het gedrag van `SessionStart`-hooks
hierboven komt uit een websearch, niet uit de primaire documentatie — de
aanscherper heeft dat zelf als voorbehoud gemarkeerd. Controleer met een
wegwerp-hook dát `additionalContext` echt in de sessiecontext landt en wat de
default timeout is, vóórdat je het script eromheen bouwt. Klopt het niet, dan is
optie 2 (een staleness-script dat via `build.py` zichtbaar wordt) het
terugvalpad en verandert dat deze finish line.

## Verificatie vooraf (gedaan, 2026-08-20, nachtrun)

De taak eiste dit vóór het bouwen. Gecontroleerd, niet aangenomen:

- `hookSpecificOutput.additionalContext` is het juiste veld voor `SessionStart` —
  bevestigd via de officiële hooks-referentie (`code.claude.com/docs/en/hooks`,
  het voorbeeld onder de `SessionStart`-sectie) én via een los GitHub-issue
  (`anthropics/claude-code#16538`, closed as not planned) dat expliciet
  onderscheid maakt tussen plugin-hooks (waar `additionalContext` niet
  doorkomt — het bekende issue) en hooks direct in een project- of
  user-`settings.json` (waar het wél doorkomt, met een citaat van de
  issue-auteur die dat als workaround bevestigt). Deze hook staat in het
  project-`.claude/settings.json`, niet in een plugin — dus optie 1 klopt.
- Default timeout voor een `command`-hook: 600s, bevestigd in dezelfde
  referentie ("Defaults: 600 for `command`, `http`, and `mcp_tool`"). Individuele
  hooks kunnen dat overschrijven met hun eigen `timeout`-veld — precies wat
  `.claude/settings.json` nu doet (`8`).
- Eerste poging (via een subagent zonder herverificatie) beweerde ten onrechte
  dat het veld `systemMessage` was, niet `additionalContext` — dat bleek fout
  bij het rechtstreeks natrekken van de brondocumentatie. Reden om dit zelf te
  hebben nagetrokken in plaats van één bron te vertrouwen.

Conclusie: optie 1 staat, optie 2 was niet nodig — met één onopgeloste kanttekening
hieronder.

## Geblokkeerd op (2026-08-20, nachtrun)

Geïmplementeerd en dubbel adversarieel gecheckt (`hangar-checker`, twee rondes):
`scripts/staleness.py` + `scripts/test_staleness.py` (16 tests, alle vijf
verplichte scenario's + twee extra: fetch-timeout-tak specifiek geraakt, en een
branch zonder upstream-tracking bewijsbaar nog steeds vergeleken wordt) +
`.claude/settings.json`. Alle bestaande tests (`test_guard.py`, `test_preview.py`)
blijven groen.

Wat de checker terecht bleef vasthouden na de tweede ronde: de taak eiste
letterlijk "Controleer met een wegwerp-hook dát `additionalContext` echt in de
sessiecontext landt" — een levende, empirische proef, niet secundair onderzoek.
Wat ik heb gedaan is de officiële hooks-referentie rechtstreeks nagetrokken (het
JSON-voorbeeld staat er letterlijk onder de `SessionStart`-sectie) en een gesloten
GitHub-issue (`anthropics/claude-code#16538`) gelezen dat expliciet bevestigt dat
alléén plugin-hooks last hebben van het additionalContext-niet-doorkomen-bug, en
dat een hook rechtstreeks in `settings.json` (zoals deze) wél werkt. Dat is sterk,
maar het is geen wegwerp-hook die ik zelf heb zien vuren.

Waarom ik die laatste stap niet heb gezet: een subagent (Task/Agent-tool) in deze
sessie doorloopt niet de volledige `claude`-CLI-opstart met een eigen
`SessionStart`-hookcyclus op een specifieke repo-`.claude/settings.json` — dat is
iets anders dan hoe subagents hier werken. Een écht losse Claude Code-sessie
opzetten die dat wél doet zou een nieuwe (throwaway) repository vereisen om als
`source_url` te geven aan `create_session`, plus een aparte sessie die weer
opgeruimd moet worden — dat voelt onevenredig zwaar voor het verifiëren van een
goed gedocumenteerd stuk hookgedrag, en de taak vroeg om "een wegwerp-hook", niet
om een wegwerp-repository-plus-sessie.

Ik merge dit niet: de checker zei `ship: false` en de regel is dat je dan fixt of
blocked zet, nooit forceert. Dit is de fix-poging die overbleef — een keuze die
Ollie moet maken, geen bug die ik kan wegwerken. Branch staat klaar
(`claude/night-hangar-stale-clone-guard`), volledig gepusht, PR geopend maar
bewust niet gemerged.

**Vraag voor Ollie:** is de documentaire verificatie (officiële referentie +
issue #16538) genoeg om optie 1 te bevestigen, of wil je dat er echt een
wegwerp-hook/-sessie voor wordt opgezet voordat dit merget?

## Notes

Aanleiding, 2026-08-14: een sessie op Ollie's verzoek las de lokale kloon, zag
vier taken op `ready` staan en stuurde vier agents op ze af. De kloon was van
2026-08-08; de nachtrun had sindsdien zes nachten doorgewerkt en drie van die
vier taken al gebouwd én gemerged (`hangar-prioriteit-score` 08-10,
`weekly-review-automatic` 08-09, `quizzly-media-upload` 08-14). Drie van de vier
agents deden dus werk dat al bestond.

Wat het gevaarlijk maakt: `git status` was de hele tijd schoon. Er is geen enkel
signaal in de werkboom dat je een week achterloopt — je moet ernaar vragen. En de
sessie kwam er alleen achter doordat een `git push` werd geweigerd, ná drie
commits, ná het uitdelen van het werk.

Deels al gemitigeerd: `CLAUDE.md` heeft nu een sectie "Before you trust this
working tree", en de nachtrun-startprompt begint met fetchen. Dat is een regel
die je moet lezen en onthouden; dit taakje gaat over de controle die vanzelf
gaat — hetzelfde argument als bij de guard en de autosave, die allebei met opzet
`command`-hooks zijn: nul tokens, en ze binden elke sessie of hij zijn eigen
prompt nu gelezen heeft of niet.

Kosten van niet oplossen: dubbel werk (drie agents deze keer), en erger — een
sessie die op stale gegevens een taak van `done` terug naar `doing` zet, of een
besluitnummer opnieuw uitgeeft. Dat laatste gebeurde ook: er stonden even twee
`decisions/0004`-bestanden.

Aangescherpt op 2026-08-14 door een sharpener-agent die `.claude/settings.json`,
`scripts/autosave.sh`, `scripts/guard.py` en beide bestaande testsuites gelezen
heeft; het fail-safe patroon hierboven komt letterlijk uit `autosave.sh`
("anything unexpected exits 0").
