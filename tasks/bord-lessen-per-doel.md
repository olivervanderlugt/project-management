---
title: Bord toont de lessen, gelabeld per doel
project: hangar
status: done
added: 2026-08-06
effort: S
branch: claude/hangar-project-setup-w61m5q
---

## Done means

- `dashboard/index.html` heeft een lessen-sectie: elke les met `status: active`
  staat erop met titel, scope en doel(en), zichtbaar gelabeld per doel
  (`effectiever`, `simpeler`, `veiliger`, `goedkoper`).
- `_`-bestanden en lessen met `status: retired` verschijnen niet.
- `python3 dashboard/build.py` draait zonder fouten en blijft idempotent; de
  bestaande secties van het bord blijven zoals ze zijn.
- Alleen `dashboard/build.py` is gewijzigd (plus de gegenereerde
  `dashboard/index.html`).

## Notes

Akkoord van Ollie 2026-08-06 op het voorstel uit de lessen-doelen-taak: zodra
er lessen zijn, laat het bord per doel zien waar het systeem beter van wordt.
