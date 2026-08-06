---
title: Elke les krijgt een doel: effectiever, simpeler, veiliger of goedkoper
project: hangar
status: done
added: 2026-08-06
effort: S
branch: claude/hangar-project-setup-w61m5q
---

## Done means

- `lessons/_template.md` heeft een `goal:`-veld met de vaste woordenlijst
  `effectiever | simpeler | veiliger | goedkoper` (komma-gescheiden mag,
  primaire doel eerst — zelfde vorm als `tags:`).
- Les 0001 heeft een ingevuld `goal:`.
- CLAUDE.md noemt het veld en de vier doelen in de bestaande lessons-alinea.
- `python3 scripts/gen_agents.py` en `python3 dashboard/build.py` draaien
  zonder fouten; de injectie verandert niet (het doel is metadata, de regel
  blijft wat geïnjecteerd wordt).

## Notes

Van Ollie, 2026-08-06: "Het moet in ieder geval als doel hebben effectiever te
werken, simpeler te werken, veiliger te werken en goedkoper te werken." Het
doel dwingt bij het schrijven van een les de vraag af wélk van de vier hij
dient — een les die geen van de vier dient, is geen les.
