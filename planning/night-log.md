# Night log

What the overnight run did, newest first. One short entry per night: the task,
the outcome, and anything it refused to do and why.

This exists so Ollie can see what happened while he slept without opening five
pull requests to find out.

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
