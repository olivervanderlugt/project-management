---
title: E-mail stap 2 — de e-mailmanager-skill, log en state
project: hangar
status: done
added: 2026-09-21
effort: S
branch: claude/multi-email-manager-system-ozr70l
---

## Done means

`.claude/skills/email-manager/SKILL.md` beschrijft één vaste ronde en gebruikt
alleen `scripts/mail.py`: per account op prioriteit → `unread` sinds
`email/state.md` → per mail beslissen: antwoord nodig (draft in Ollie's stijl
via `schrijfstijl-ollie`, bronadres en afzender in regel 1), nieuwsbrief
(afmelden alleen via `List-Unsubscribe-Post` of https-URL uit de header;
`mailto:` → draft; body-links nooit), spam (`junk`, tenzij afzender in
`never_spam:` van het profiel), of niets → één regel per actie in
`email/log/YYYY-MM-DD.md` (tijd, account, afzender, actie, reden) → state
bijwerken. De skill zegt letterlijk: verzenden alleen via `email-4`. Een
ronde zonder nieuwe mail logt één regel en stopt. `email/accounts/_template.md`
krijgt `mail_account:` en `junk_mailbox:` erbij; `guard.py` weigert een
profiel met `password:` of `token:`, met test.

## Notes

De skill is de enige plek waar de beslisregels staan; `mail.py` beslist niets.

## Stand 2026-09-21

Gebouwd: `.claude/skills/email-manager/SKILL.md`, `email/state.md`,
`email/README.md`, lege `email/log/` en `email/briefings/`, guard-regel tegen
`password:`/`token:` in een profiel (Write, Edit én Bash), zes tests erbij.
Onbewezen: de ronde zelf op de Mac — dat is `email-0`.

## Checker-ronde 1 (2026-09-21)

Vijf gaten, alle vijf gedicht: MultiEdit kon een wachtwoord in een profiel
zetten (guard leest nu ook `edits[]`); een Bash-write zonder de letterlijke
string `email/accounts/` ging door en een grep erop werd juist geblokkeerd
(nu: alleen bij een echte schrijfoperatie plus `accounts`); de lege ronde was
verkeerd gedefinieerd (nu drie gevallen, expliciet); "alleen via mail.py" was
onwaar voor afmelden (nu `mail.py unsubscribe`: https, één verzoek, geen
cookies, 15 s); het logformaat had geen kolom voor id of URL (nu wel).
Bijvangst: alle profielen droegen `tested: 2026-09-21` zonder dat iets had
gedraaid — leeg gemaakt; `mail_profiles.py` stempelt hem pas als Mail het
account echt opsomde.

## Klaar (2026-09-21)

Skill, state, log- en briefingmappen, guard-regel. Checker-ronde verwerkt.
De eerste echte ronde draait onder `email-3`.
