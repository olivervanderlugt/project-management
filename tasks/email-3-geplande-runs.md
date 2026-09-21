---
title: E-mail stap 3 — briefing 07:30 en 21:30 plus uurronde 08–22 via launchd op de Mac
project: hangar
status: inbox
added: 2026-09-21
effort: M
branch:
---

## Done means

`scripts/email-schedule/` bevat twee `launchd`-plists en een `install.sh` die
ze in `~/Library/LaunchAgents` zet en laadt: `nl.hangar.email.briefing`
(07:30 en 21:30) en `nl.hangar.email.pass` (elk uur 08:00–22:00), beide
`claude -p` met de skill in dit repo, met een token-plafond uit `routing.yml`
(nieuw blok `email_pass` en `email_briefing`). De briefing schrijft
`~/.hangar-mail/briefings/YYYY-MM-DD-{am,pm}.md`: per account op prioriteit wat nieuw
is, wat een antwoord vraagt en welke draft klaarstaat, wat naar Ongewenst
ging, waar afgemeld is, en wat niet kon. Niets ervan komt in het repo (besluit
0008); `install.sh` zet daarnaast `~/.hangar-mail/context/` in de map die de
Google Drive-app synct, zodat briefing en context op de telefoon leesbaar
zijn via Drive. Een macOS-notificatie met de eerste drie regels. Twee runs zonder
nieuwe mail geven een briefing van drie regels, niet een lege of verzonnen.
Een `uninstall.sh` haalt beide weer weg. De uurfrequentie is één regel in de
plist en staat in de README als Ollie's knop.

## Notes

`launchd` wekt een slapende Mac niet; `pmset repeat wakeorpoweron` voor
07:25 staat als optionele regel in de README, niet in `install.sh`. Als de
Mac dicht is, haalt de volgende run in via `~/.hangar-mail/state.md`. Verzenden kan
deze run niet: geen variabele, en de guard.

## Stand 2026-09-21

Claude Code 2.1.252 staat op de Mac (`claude --version`), dus `launchd` +
`claude -p` is de weg. Wacht op `email-5` niet: de rondes kunnen eerder
starten, de context-stap komt er later bij.
