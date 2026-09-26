---
title: Skill die een groot onderzoeksresultaat omzet in een podcast met instelbare lengte
project: hangar
status: done
added: 2026-09-17
effort: M
branch: claude/nifty-bohr-472w7g
---

## Done means

`.claude/skills/onderzoek-naar-podcast/SKILL.md` bestaat en levert, gegeven een
afgerond onderzoek: een bronbestand voor NotebookLM, een plak-klare
`Customize`-instructie, en vier regels handwerk. Lengte via drie presets
(kort ~10 / normaal ~25 / lang ~45 min), taal gekozen op onderwerp.

Gehaald op 2026-09-17.

## Notes

Keuzes die Ollie maakte (2026-09-17):

- **Output**: script voor NotebookLM, geen eigen TTS. NotebookLM is gratis,
  heeft de beste stemmen en geen publieke API — de laatste 30 seconden doet
  hij zelf.
- **Lengte**: vaste presets, niet vrije minuten.
- **Taal**: hangt van het onderwerp af. SBI/studiestof Nederlands, tech en
  internationaal onderzoek Engels.

Wat er al bestond, gratis: NotebookLM Audio Overview — twee AI-hosts, lengte
Shorter / Default / Longer (alleen Engels), formats Deep Dive / Brief /
Critique / Debate / Lecture, 3 generaties per dag op de gratis tier. Geen
publieke API op de consumer-tier; de Gemini Notebook Enterprise API kan het
programmatisch maar is niet self-serve.

Feitencheck 2026-09-20 corrigeerde de eerste presettabel: Google garandeert
geen duur, een doorsnee aflevering landt rond de 10 min (spreiding 7-15), en
alleen het Lecture-format haalt met Longer betrouwbaar de ~30 min die het
plafond is. De eerste versie beloofde 45 min bij Lang — onhaalbaar. Presets nu
~8-10 / ~15-20 / ~25-30 min, met splitsen in twee afleveringen voor langere
ritten.

Het echte mechaniek in de skill: **het aantal secties in de bron stuurt de
duur**, niet het woordenaantal — de hosts doen ~2-3 min per onderwerp. Dat is
ook de enige lengteknop die in het Nederlands bestaat, want NotebookLM's
Shorter/Default/Longer werkt alleen bij Engels.

Openstaand: de skill staat in deze repo. Voor Cowork moet hij naar
`~/.claude/skills/` (kopie of symlink) — dat kan alleen op Ollie's eigen
machine.
