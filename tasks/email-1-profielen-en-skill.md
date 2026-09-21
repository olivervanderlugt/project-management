---
title: E-mail stap 1 — accountprofielen, de e-mailmanager-skill en de verzend-blokkade
project: hangar
status: inbox
added: 2026-09-21
effort: S
branch:
---

## Done means

Drie dingen bestaan en zijn getest:

1. `email/accounts/_template.md` en de ingevulde profielen uit `email-0`, met
   platte frontmatter: `address`, `provider`, `priority` (1–3), `label`,
   `source`, `send_as` (yes/no/paste), `language`, `tone`, `auto_unsubscribe`
   (yes/no), `tested`. Geen wachtwoorden, geen tokens; `scripts/guard.py`
   krijgt een regel die een `email/accounts/*.md` met `password:` of `token:`
   weigert, met test aan beide kanten in `scripts/test_guard.py`.
2. `.claude/skills/email-manager/SKILL.md`: de vaste routine — per account op
   prioriteit: nieuwe mail lezen → draft per mail die een antwoord vraagt (in
   Ollie's stijl via `schrijfstijl-ollie`, met bronadres en afzender in de
   eerste regel) → spam naar Gmail's spam-map (VU: Ongewenste e-mail), nooit definitief
   verwijderen → afmelden uitsluitend via `List-Unsubscribe-Post` (one-click)
   of een https-URL uit de `List-Unsubscribe`-header; een `mailto:`-variant
   wordt een draft in de briefing; links uit de body nooit → regel in
   `email/log/YYYY-MM-DD.md`. De skill zegt letterlijk: verzenden alleen via
   `email-4`, nooit hier.
3. `.claude/settings.json` heeft een `PreToolUse`-hook met matcher
   `mcp__Gmail__.*|mcp__Microsoft_365__.*` naar `scripts/guard.py`. De guard
   laat alleen een allowlist door (de lees-, zoek-, draft-, label- en
   spam-tools uit `reference/email-tools.md`) en geeft exit 2 op elke andere
   naam — fail-closed. De allowlist gaat open voor verzenden alleen als
   `HANGAR_EMAIL_SEND_OK=1` in de omgeving staat, en die staat nergens in
   het repo: niet in `settings.json`, niet in een Routine. Tests in
   `scripts/test_guard.py`: verzendtool zonder variabele → 2, onbekende
   Gmail-toolnaam → 2, zoektool → 0, verzendtool mét variabele → 0.

`python3 dashboard/build.py` slaat `email/` over zoals het `_`-bestanden
overslaat, of toont het netjes — één van beide, geen kapot bord.

## Notes

Als `email-0` uitwijst dat verzenden en draft maken hetzelfde tool zijn met
een vlag, leest de guard de payload en weigert op die vlag. Dat is dan het
eerste wat hier te bouwen valt, vóór de skill.

Per mail toestemming is binnen Ollie's eigen sessie een skill-regel, geen
hook. Dat staat zo in 0006 en is de eerlijke grens.
