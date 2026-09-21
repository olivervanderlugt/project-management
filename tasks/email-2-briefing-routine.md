---
title: E-mail stap 2 — briefing om 07:30 en 21:30 met push naar de telefoon
project: hangar
status: inbox
added: 2026-09-21
effort: S
branch:
---

## Done means

Eén Routine, fresh session per run, cron 07:30 en 21:30 Amsterdam-tijd (dus
twee cron-regels in UTC, met wintertijd-omzetting genoteerd in het prompt-
bestand), met de Gmail- en M365-connector eraan en push-notificatie aan. Het
prompt staat in `reference/startprompt-email-briefing.md`, zoals de nachtrun
zijn prompt in `reference/` heeft. Elke run schrijft
`email/briefings/YYYY-MM-DD-{am,pm}.md` en commit hem: per account op
prioriteit — wat er nieuw is, wat een antwoord vraagt en welke draft klaarstaat,
wat in quarantaine ging, waar afgemeld is, en wat Claude niet kon (bron `none`,
draft om te plakken). De push bevat de eerste drie regels. Het bord toont de
laatste briefing als één tegel. Twee opeenvolgende runs zonder nieuwe mail
produceren een briefing van drie regels, niet een lege of een verzonnen.

## Notes

De Routine verzendt nooit; de hook uit `email-1` staat er sowieso op. Als de
ochtendrun `email-3` van die nacht overlapt, wint de briefing en slaat
verwerking over — de volgende uurrun haalt het in.
