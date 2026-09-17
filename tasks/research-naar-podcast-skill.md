---
title: Skill die een groot onderzoeksresultaat omzet in een podcast met instelbare lengte
project: hangar
status: inbox
added: 2026-09-17
effort: M
branch:
---

## Done means

Nog niet scherp genoeg om `ready` te zijn. De finish line hangt aan twee
keuzes die Ollie nog moet maken (zie Notes): welke stem/TTS-route, en of de
skill audio oplevert of alleen een script.

## Notes

Ollie's vraag (2026-09-17): als Cowork 's nachts een groot onderzoek heeft
gedraaid, wil hij dat de volgende ochtend als podcast in de auto kunnen
luisteren. Zelf de lengte kunnen kiezen.

Wat er al bestaat, gratis:

- **NotebookLM Audio Overview** — gratis, twee AI-hosts, lengte Shorter /
  Default / Longer (alleen Engels), formats Deep Dive / Brief / Critique /
  Debate, max ~30 min, 3 generaties per dag op de gratis tier. Handmatig:
  bestand uploaden, knop drukken, downloaden. Geen publieke API op de
  consumer-tier; de Gemini Notebook Enterprise API kan het wel programmatisch
  maar is niet self-serve.
- Lokale TTS (Kokoro, Piper) of macOS `say`: gratis, wel zelf een
  twee-stemmen-script en audio-pipeline bouwen.

De skill zou dus of (a) een dunne laag zijn: onderzoek → podcastscript in
NotebookLM-vorm → handmatig door NotebookLM halen, of (b) end-to-end:
script + TTS + mp3 in een map die zijn telefoon synct.

Aandachtspunten: de guard blokkeert credentials, dus een betaalde TTS-key
hoort niet in deze repo. Lengte sturen doe je via woordenaantal in het
script (~150 woorden per minuut gesproken).
