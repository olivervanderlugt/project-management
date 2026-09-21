---
title: E-mail stap 6 — mailcontext per account in Drive, en een skill die elke chat hem laat lezen
project: hangar
status: inbox
added: 2026-09-21
effort: L
branch:
---

## Done means

Drie dingen:

1. **Samenvattingen.** De e-mailmanager-ronde krijgt een stap "context":
   voor threads uit `email-5` die `open` zijn of in de laatste 90 dagen
   geraakt, en om te beginnen alleen voor accounts met `priority: 1`,
   schrijft Claude per thread drie tot vijf regels in
   `~/.hangar-mail/context/<slug>.md`: wie, waarover, wat er van Ollie
   verwacht wordt, stand van zaken, laatste datum. Bestaande samenvattingen
   worden bijgewerkt, niet verdubbeld. Elke ronde neemt daarna één blok
   oudere threads mee (bijv. 30 per ronde), zodat de historie vanzelf
   volloopt zonder één dure run. `context.md` bovenaan: per account de open
   threads en de drie contacten die het vaakst terugkomen.
2. **Sync naar Drive.** `~/.hangar-mail/context/` staat in een map die de
   Google Drive-app op de Mac synct naar `Hangar/Mail/` (symlink of
   verplaatste map; `install.sh` uit `email-3` zet hem). Geen eigen
   upload-code.
3. **Skill `mail-context`** voor claude.ai en Cowork, apart van
   `email-manager`: bij elke vraag over mail eerst `Hangar/Mail/context.md`
   lezen via de Drive-connector (of lokaal in Cowork), dan het
   accountbestand dat bij het onderwerp hoort, dan pas antwoorden; in Cowork
   op de Mac daarnaast `mail.py` voor wat nieuwer is dan de laatste sync. De
   skill zegt hoe oud de context is en verzint niets dat er niet in staat.
   Ollie installeert hem in claude.ai zelf; de skilltekst staat in
   `.claude/skills/mail-context/SKILL.md`.

Test: één gesimuleerde ronde tegen vaste index-invoer levert een
`context.md` op waarin elke thread precies één keer voorkomt; de skilltekst
noemt geen ander pad dan Drive-connector, lokaal bestand of `mail.py`.

## Notes

Dit is Ollie's eigenlijke doel: "in elke chat meteen alles weten". Alles
hierboven leest; niets hierin verzendt, verwijdert of verandert een mail.
