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
   eerste regel) → spam naar het label `mail/quarantaine` → afmelden via
   `List-Unsubscribe` of de link in de mail → regel in `email/log/YYYY-MM-DD.md`.
   De skill zegt letterlijk: verzenden alleen via `email-4`, nooit hier.
3. `.claude/settings.json` heeft een `PreToolUse`-hook op de verzendtools uit
   `reference/email-tools.md` die exit 2 geeft, tenzij de omgevingsvariabele
   `HANGAR_EMAIL_SEND_OK=1` staat. Test: met en zonder variabele.

`python3 dashboard/build.py` slaat `email/` over zoals het `_`-bestanden
overslaat, of toont het netjes — één van beide, geen kapot bord.

## Notes

De hook blokkeert op toolnaam. Als `email-0` uitwijst dat verzenden en draft
maken hetzelfde tool zijn met een vlag, moet de hook de payload lezen. Dat is
dan het eerste wat hier te beslissen valt.
