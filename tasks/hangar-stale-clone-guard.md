---
title: Een sessie moet merken dat zijn kloon achterloopt vóór hij werk uitdeelt
project: hangar
status: blocked
added: 2026-08-14
effort: M
branch:
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

**Voorwaarde, en dit is waarom de taak `blocked` staat:** het gedrag van
`SessionStart`-hooks hierboven komt uit een websearch, niet uit primaire
documentatie. Dat uitzoeken is losgetrokken naar
`tasks/hangar-sessionstart-hook-gedrag.md`. Zodra `reference/sessionstart-hooks.md`
bestaat en zijn verdictregel "haalbaar" zegt, gaat deze taak naar `ready` en is
de finish line hierboven compleet. Zegt het verdict "niet haalbaar", dan
verandert deze finish line naar optie 2 (een staleness-script dat via
`build.py` zichtbaar wordt) en moet hij opnieuw geschreven worden.

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

**Op `blocked` gezet 2026-08-20, met de reden erbij.** Drie nachten (08-15,
08-17, 08-18) hebben deze taak gekozen, hun startcommit gepusht en zijn gestopt
vóór de eerste regel code — de weesbranches `night/hangar-stale-clone-guard` en
`claude/night-hangar-stale-clone-guard` staan er nog. De oorzaak zat in de taak,
niet in de nachten: een `S` die met onderzoek begon. Onderzoek eruit, effort naar
`M`, en `blocked` tot dat onderzoek er ligt — zodat de queue vannacht doorschuift
naar `quizzly-media-orphan-cleanup` in plaats van hier voor de vierde keer op
stuk te lopen. Zie `tasks/nachtrun-loopt-vast-op-een-taak.md`.
