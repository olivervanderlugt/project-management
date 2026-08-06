---
title: Raspberry Pi met OpenClaw als altijd-aan poort naar de Hangar
project: hangar
status: inbox
added: 2026-08-06
effort: L
branch:
---

## Done means

Nog niet schrijfbaar — eerst uitzoeken wat de Pi precies moet doen en welk
model de vang-laag draait. Dit is de concrete invulling van stap 4 uit
`hangar-in-de-browser`: eigen hardware in plaats van gehuurde hosting.

## Wat er gevraagd is

Ollie, in zijn woorden: stel ik installeer een Raspberry Pi met OpenClaw erop,
kan die dan alles — typen en hij begint? En wat is de beste en goedkoopste
optie, ook als het geen Claude is?

## Eerste beeld

- De Pi is het altijd-aan stuk dat nu ontbreekt: berichten ontvangen
  (Telegram/WhatsApp via OpenClaw), taakbestanden schrijven, pushen, de
  nachtrun draaien. Eenmalig ~€80-110, stroom een paar euro per jaar.
- Het denken blijft bij een AI-dienst via internet; een Pi is te zwak om zelf
  een bruikbaar model te draaien. Kosten dus: hardware eenmalig + verbruik per
  bericht.
- Goedkoopste zinnige indeling: vangen/gesprek op een goedkoop model (Haiku,
  of niet-Claude: Gemini Flash / DeepSeek — centen per maand), bouwen op een
  zwaar model zoals nu.
- Grenzen die blijven staan: OpenClaw niet open naar internet (sleutel staat
  thuis, houden zo), en vangen is automatisch maar bouwen pas na een echte
  `## Done means` — de Pi verandert daar niets aan.
- Breekt net als stap 4 besluit 0001 half: het is een server, alleen dan van
  jezelf. Nieuw besluit schrijven vóór er gebouwd wordt.
