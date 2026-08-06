---
title: Zelflerende Hangar: incidenten worden lessen, lessen landen in elke agent
project: hangar
status: done
added: 2026-08-06
effort: S
branch: claude/hangar-project-setup-w61m5q
---

## Done means

- `lessons/` bestaat met een `_template.md` (plat frontmatter, zelfde contract
  als de rest) en één echte les: `0001-*.md` over het workflow-dispatch-incident
  van 2026-08-06.
- `scripts/gen_agents.py` leest `lessons/*.md` en injecteert elke les met
  `status: active` in de gegenereerde agentbestanden, gefilterd op `scope`
  (builders, checker, manager, all, of een project-slug). Bestanden die met `_`
  beginnen worden overgeslagen.
- Na `python3 scripts/gen_agents.py` staat de tekst van les 0001 letterlijk in
  elke builder-agent in `.claude/agents/`. Handgeschreven agentbestanden blijven
  onaangeraakt.
- CLAUDE.md beschrijft de loop: incident in het night-log → les in `lessons/` →
  generator draaien. Eén alinea, geen essay.
- `python3 dashboard/build.py` en `python3 scripts/gen_agents.py` draaien
  zonder fouten en zijn idempotent: een tweede run verandert niets.

## Notes

Aanleiding: in de nachtrun van 2026-08-06 probeerde de learning-website-bouwer
`deploy.yml` af te vuren via `workflow_dispatch` — tegen regel 6. De les moet
zeggen: nooit workflows of deploys triggeren, ook niet ter verificatie; een
finish line buiten je bereik is een `false` met bewijs, geen reden om verder te
reiken.

Ollie vroeg hier expliciet om ("zelflerend, zoals dat incident, automatisch"),
vandaar direct `ready` → `doing` zonder nachtrun.
