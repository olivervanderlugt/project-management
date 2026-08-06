# Welk project voor welk doel

Geschreven 2026-08-06, op verzoek: welk project is het meest veelbelovend per
doel, zodat prioriteren geen gevoelskwestie is.

Dit is een oordeel, geen meting. Het is gebaseerd op wat er in de repo's staat
op 2026-08-06 — niet op verkoopcijfers, want die zijn er nergens.

## De projecten in één regel

| Project      | Wat het is                                            | Staat                            |
| ------------ | ----------------------------------------------------- | -------------------------------- |
| Versa        | Songteksten regel voor regel naast een vertaling      | Meest af. Docker, Postgres, e2e. |
| Percentile   | Consent-first analytics + benchmarknetwerk voor AI-apps | Werkend, met twee regressies open. |
| Learn        | Één skill tree over CS, wiskunde, natuurkunde, robotica | Componenten af, curriculum schoof drie keer. |
| Hangar       | Deze HQ                                                | Draait, publiceert zichzelf.     |
| Quizzly      | Onbekend                                               | Leeg. Nul commits.               |
| Crew mgmt    | Onbekend                                               | Leeg. Nul commits.               |

## Score per doel

Schaal: ●●● sterk, ●● redelijk, ● zwak. Lege repo's staan er niet in — die
scoren overal nul tot je opschrijft wat ze waren.

| Doel                              | Versa | Percentile | Learn | Hangar |
| --------------------------------- | ----- | ---------- | ----- | ------ |
| Snel kapitaal                     | ●     | ●●         | ●     | ●      |
| Winstgevend bedrijf op termijn    | ●●    | ●●●        | ●     | ●      |
| CV en LinkedIn                    | ●●●   | ●●         | ●●    | ●      |
| Leren binnen jouw interesses      | ●●    | ●●●        | ●●●   | ●●     |
| Tijd tot echte gebruikers         | ●●●   | ●          | ●●    | ●●●    |
| Studie-synergie (SBI)             | ●     | ●●●        | ●●●   | ●      |
| Hefboom op al het andere          | ●     | ●          | ●     | ●●●    |
| Overlevingskans zonder aandacht   | ●●    | ●●         | ●●    | ●●●    |
| Juridisch risico (laag = goed)    | ●●    | ●          | ●●●   | ●●●    |

## Wat dat betekent per doel

**Snel kapitaal.** Geen van deze vier. Dat is de eerlijke uitkomst en het
belangrijkste dat hier staat. Percentile is het enige project met een
verdienmodel, maar een benchmarknetwerk is per definitie waardeloos tot het
netwerk er is: de eerste klant koopt een vergelijking met niemand. Dat is
maanden, geen weken. Versa zit in een markt waar consumenten niet betalen en
rechten duur zijn. Wil je binnen een kwartaal geld, dan komt dat uit het
verkopen van je vaardigheid — AI- en automatiseringsklussen voor MKB en
studieverenigingen — en niet uit een van deze producten. Die klussen financieren
de producten; andersom werkt het niet.

**Winstgevend bedrijf op termijn.** Percentile, met afstand. Het is het enige
dat een echte wig heeft: mensen shippen apps waarvan ze de code niet lezen en
weten niet of 14% activatie goed of rampzalig is. De MCP-hoek maakt het
distribueerbaar via de coding agent zelf in plaats van via marketing. De prijs
ervoor is dat je consent en privacy foutloos moet doen, en daar liggen nu nog
twee regressies open die niemand heeft gediagnosticeerd.

**CV en LinkedIn.** Versa. Een recruiter klikt op een werkende link, niet op een
architectuurbeschrijving. Versa heeft Next.js, Drizzle, Postgres, Docker en
Playwright-e2e — precies de stack waar vacatures op filteren — en is het enige
project dat je in één zin kunt demonstreren. Percentile is inhoudelijk
indrukwekkender maar onzichtbaar: een SDK plus MCP-server laat je niet zien op
een telefoon. Zet Versa live en je hebt een portfolio; laat Versa in een repo
zitten en je hebt een verhaal.

**Leren binnen jouw interesses.** Gedeeld: Learn en Percentile, om verschillende
redenen. Learn is letterlijk gebouwd om jouw CS-, wiskunde-, natuurkunde- en
robotica-lijn in één graaf te zetten, dus daar valt studiestof en bouwen samen.
Percentile leert je het schaarsere spul: dataprivacy, adversarial testing,
protocolontwerp. Dat is het soort kennis dat maar weinig eerstejaars heeft.

**Studie-synergie (SBI).** Percentile en Learn. Percentile is een kant-en-klare
businesscase met een echt marktprobleem, een verdienmodel en een juridische
dimensie — bruikbaar in vrijwel elk SBI-vak dat om een casus vraagt. Learn is
bruikbaar als je eigen studiemateriaal. Versa en de Hangar zijn dat niet.

**Hefboom.** De Hangar. Het verdient niets en hoort niets te verdienen
(besluit 0001), maar het maakt elk ander project goedkoper om op te pakken. Wel
oppassen: gereedschap bouwen voelt productief en is de makkelijkste manier om
een avond te besteden zonder iets op te leveren. Houd het mager.

## Overige doelen die het overwegen waard zijn

- **Tijd tot echte gebruikers.** Versa. Feedback van vreemden is meer waard dan
  nog een feature.
- **Overlevingskans als je drie weken niks doet.** De Hangar, want die heeft geen
  onderhoud. Versa heeft een database en verloopt.
- **Juridische blootstelling.** Percentile raakt AVG en bijzondere
  persoonsgegevens; Versa raakt auteursrecht en heeft daarom een DMCA-flow. Dat
  is geen reden om te stoppen, wel om beide niet 's nachts onbewaakt te laten
  bouwen.
- **Optiewaarde.** Wat kost het om iets levend te houden zonder eraan te werken?
  Learn en de Hangar: niets. Versa: hosting. Percentile: hosting plus de plicht
  om beveiliging bij te houden zodra er data van derden in zit.

## Aanbevolen volgorde

1. **Versa live zetten.** Eén werkende URL levert je het meeste per uur: CV,
   LinkedIn, echte gebruikers. Vereist een hostingbesluit dat geld kost, dus dat
   is aan jou.
2. **Percentile diagnosticeren.** Eerst weten welke twee fixes het erger maakten,
   pas daarna bouwen. Dit is het lange spel en het verdient echte uren, niet
   restjes.
3. **Learn op Pages.** Kost bijna niets en verandert het van een privémap in iets
   dat je kunt laten zien. Staat al klaar als taak.
4. **Hangar mager houden.** Alleen bouwen wat de andere drie sneller maakt.
5. **Quizzly en Crew management: één alinea of weg.** Twee lege repo's zijn twee
   besluiten die je elke keer opnieuw neemt.

## Wat dit niet zegt

Niets hierin gaat over wat je leuk vindt om te doen. Als het antwoord op "waar
werk ik vrijdagavond vrijwillig aan" Learn is, dan wint Learn van elke tabel
hierboven, want een project waar je niet aan werkt scoort nul op alle doelen.
