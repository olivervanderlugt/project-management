# Manager en bouwers: hoe de Hangar werk over agents verdeelt

Ontwerp, 2026-08-06. Nog niet gebouwd — besluit 0003 is het voorstel, dit is de
uitwerking.

## Het idee in één alinea

Eén goedkoop, snel model is de manager. Die houdt het plan vast, kiest werk,
schrijft briefs en beoordeelt rapporten — en leest **nooit** projectcode. Dure
modellen zijn bouwers: één taak per stuk, een smalle brief, een eigen branch.
Een derde agent controleert, ziet alleen de diff en de finish line, en krijgt de
opdracht te bewijzen dat het níét af is. Alles wat deterministisch is — status
bijwerken, night-log, bord bouwen, committen — is een script en kost nul tokens.

## Waarom dit goedkoper is, en waarom niet om de reden die je denkt

Je vermoedde dat het scheelt als agents onderling in code praten in plaats van
in Nederlands. Dat klopt, maar het is klein: onderling overleg is een paar
procent van het verbruik. Waar de tokens echt heen gaan is **lezen**. Eén bouwer
die een repo verkent om te snappen waar iets staat, verbrandt meer dan honderd
berichten tussen agents.

De winst zit dus in vier dingen, in deze volgorde:

1. **De manager laat nooit ruwe bestanden binnen.** Hij ziet frontmatter,
   routeringstabel en rapporten. Nooit een diff, nooit een bestand. Zijn context
   blijft klein en dus goedkoop, en hij kan lang blijven draaien.
2. **Briefs zijn smal en zelfstandig.** De bouwer krijgt te horen wélke
   bestanden ertoe doen. Dat scheelt de dure verkenningsfase, die je anders bij
   elke sessie opnieuw betaalt.
3. **Model per soort werk.** Sorteren en samenvatten hoeft niet op het zwaarste
   model. Bouwen in vreemde code wel.
4. **Alles wat een script kan, doet een script.** De goedkoopste token is de
   token die je niet uitgeeft.

Praat toch in een vast schema in plaats van in proza — niet om de tokens, maar
omdat een schema de bouwer dwingt te zeggen óf de finish line gehaald is, per
regel, met bewijs. Dat vangt fouten. Dat is meer waard dan de besparing.

## De rollen

| Rol        | Model      | Effort | Leest                                   | Mag schrijven            |
| ---------- | ---------- | ------ | --------------------------------------- | ------------------------ |
| Manager    | Fable 5    | laag   | frontmatter van `tasks/`, `routing.yml`, rapporten | briefs, night-log-concept |
| Bouwer     | Opus       | hoog   | alleen wat in de brief staat            | code, in eigen worktree  |
| Controleur | Opus       | laag   | de diff + `## Done means`               | één oordeel, niets anders |
| Boekhouder | script     | —      | de repo                                 | frontmatter, night-log, bord |

Drie regels die de rollen echt scheiden:

- De manager raakt nooit code aan. Zodra hij dat doet, groeit zijn context en
  verliest hij zijn prijsvoordeel.
- De controleur ziet de redenering van de bouwer niet. Alleen de diff en de
  finish line. Anders neemt hij het verhaal over in plaats van het te toetsen.
- De boekhouder is geen agent. Als je merkt dat je hem instructies schrijft in
  plaats van code, is het een script geworden dat je verkeerd hebt gebouwd.

## Het protocol

Twee berichttypes, allebei compact JSON. Proza alleen in `note`, maximaal 280
tekens; al het andere is opsombaar.

**Brief — manager naar bouwer**

```json
{"t":"brief","id":"learn-live-preview","repo":"olivervanderlugt/learning-website",
 "goal":"Pages-deploy + base path, preview-URL werkend",
 "dm":["workflow deployt op push naar default","site laadt","skill tree werkt","preview: gevuld in de Hangar"],
 "files":["vite.config.ts",".github/workflows/","package.json"],
 "nogo":["curriculum","lesinhoud","secrets","betaalde hosting"],
 "m":"opus","e":"high","cap":120000,"branch":"night/learn-live-preview"}
```

**Rapport — bouwer naar manager**

```json
{"t":"report","id":"learn-live-preview","status":"done",
 "branch":"night/learn-live-preview","tests":"pass",
 "dm":[true,true,false,false],
 "evidence":["vite.config.ts:7","run 31123375991 groen","site 404: Pages-bron staat niet op Actions"],
 "spent":83000,"note":"Twee finish lines liggen buiten mijn bereik: iemand moet Pages aanzetten."}
```

`status` kent er precies vier: `done`, `blocked`, `split`, `refused`. `dm` is
even lang als de lijst in de taak — geen samenvatting, per regel waar of niet
waar. Elke `false` heeft een regel in `evidence` die zegt waarom.

**Oordeel — controleur naar manager**

```json
{"t":"verdict","id":"learn-live-preview","ship":false,
 "broken":["dm[2]: skill tree niet geladen, asset-pad 404"],
 "evidence":["dist/index.html:12 verwijst naar /assets, niet /learning-website/assets"]}
```

De controleur mag `ship:true` alleen geven als hij géén enkele `broken` heeft
gevonden. Zijn opdracht is expliciet: probeer te bewijzen dat het niet af is.

## Routeringstabel

`routing.yml` in de Hangar, één plek waar model, effort en plafond vastliggen.
De manager mag hier alleen naar bedeneden van afwijken, nooit naar boven — dat
is de rem op je rekening.

| Soort werk                        | Model    | Effort | Plafond |
| --------------------------------- | -------- | ------ | ------- |
| vangen en sorteren (`inbox`)      | Haiku    | laag   | 10k     |
| `inbox` scherpen naar `ready`     | Sonnet   | midden | 60k     |
| bouwen, effort S                  | Sonnet   | midden | 80k     |
| bouwen, effort M of L             | Opus     | hoog   | 150k    |
| controleren                       | Opus     | laag   | 40k     |
| boekhouding en bord               | script   | —      | 0       |

Controleren staat bewust op een duur model met lage effort: het oordeel moet
scherp zijn, maar hij leest weinig. Dat is de goedkoopste plek waar kwaliteit
vandaan komt.

## Wat vastligt en wat de manager mag beslissen

Vast, niet onderhandelbaar: nooit een `inbox`-taak bouwen, nooit naar `main`,
één taak per branch, plafond per brief, nachtplafond over alles heen, en stoppen
bij drie open nacht-PR's.

Van de manager: welke taak, hoe hij opgeknipt wordt, welke bestanden in de brief
staan, en of een rapport goed genoeg is om door te laten.

## Faalmodi, en wat ze hier tegenhoudt

- **Twee bouwers in dezelfde bestanden.** Eén taak per branch, elke bouwer in
  zijn eigen worktree. Parallel bouwen mag alleen als de briefs elkaars `files`
  niet raken — dat is een controle die de manager doet vóór hij verstuurt.
- **De controleur stempelt af.** Hij ziet de redenering niet, moet per finish
  line waar of niet waar zeggen, en elke `false` moet bewijs hebben.
- **De manager verzint voortgang.** Het night-log citeert rapporten in plaats
  van ze samen te vatten. Geen bewijs betekent: niet gebeurd.
- **De rekening loopt weg.** Plafond per brief, plafond per nacht, en de
  boekhouder telt het echte verbruik mee in het night-log. Een gevoel is geen
  budget.
- **Half werk.** De bouwer mag `split` teruggeven: twee scherpe taken in plaats
  van code die half af is. Half af is duurder dan niets.

## De interface

"Meerdere agents in één interface" heb je al bijna: subagents rapporteren terug
in dezelfde sessie, en achtergrondwerk meldt zich als het klaar is. Wat de
Hangar toevoegt is de **gedeelde staat**: agents hoeven elkaar niet te zien, ze
hoeven alleen dezelfde wachtrij te lezen.

Concreet op het bord: elke taak met `status: doing` toont wie eraan werkt, op
welk model, hoeveel er verbrand is en sinds wanneer. Dan is het bord de
interface en hoeft er geen tweede ding gebouwd te worden dat je moet onderhouden.

## Bouwvolgorde

1. `routing.yml` plus de boekhoudscripts. Nul modelkosten, en het maakt alles
   erna meetbaar.
2. De schema's hierboven als bestand in de repo, plus de managerprompt. Vanaf
   hier is de nachtrun een manager in plaats van één agent die alles zelf doet.
3. De controleur. Dit is de stap die van "er is code gepusht" naar "er is iets
   afgemaakt" gaat.
4. Parallelle bouwers met worktrees. Pas hier zit tijdwinst — en pas hier doet
   het pijn als stap 1 tot en met 3 niet kloppen.

## Wat dit niet oplost

Meer agents maakt niets sneller als de taken elkaars bestanden raken; dan staat
er een rij te wachten en betaal je voor het wachten. En een vage taak wordt door
geen enkel model goed uitgevoerd: de `## Done means` blijft het duurste stuk
denkwerk in het hele systeem, en dat stuk is van jou.
