# email/

Alleen de template. Alles wat de e-mailmanager achterlaat — profielen met
adressen, state, log, briefings, context — staat op Ollie's Mac in
`~/.hangar-mail/` (of `HANGAR_MAIL_DIR`), want dit repo is publiek. Besluit
`0008`. De lay-out daar:

| Pad            | Houdt                                                          |
| -------------- | -------------------------------------------------------------- |
| `accounts/`    | Eén profiel per account: adres, prioriteit, toon, junk-map.    |
| `state.md`     | Laatst verwerkte tijd per account.                             |
| `log/`         | Eén bestand per dag, één regel per actie. Alles terug te draaien. |
| `briefings/`   | `YYYY-MM-DD-am.md` en `-pm.md`. Alleen wat in het log staat.  |
| `context/`     | De mailcontext per account die elke chat leest (email-5/6).    |

`scripts/mail_profiles.py` maakt de map aan en kopieert de template erheen.
