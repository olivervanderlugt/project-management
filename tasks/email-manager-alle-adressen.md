---
title: Claude als e-mailmanager voor alle (~10) adressen — lezen, drafts, spam, afmelden
project: hangar
status: inbox
added: 2026-09-20
effort: L
branch: claude/multi-email-manager-system-ozr70l
---

## Done means

Paraplu. Klaar als `email-0` tot en met `email-4` `done` zijn en besluit 0007
`accepted` is. Bouw begint pas na Ollie's akkoord op het plan hieronder.

## Wat er gevraagd is

Ollie, in zijn woorden: Claude als e-mailmanager voor AL zijn adressen, een stuk
of tien, sommige prominenter dan andere. Op de hoogte zijn van de gesprekken,
drafts opstellen voor nieuwe mails en antwoorden, spam bijhouden, afmelden en
verwijderen. Niet alles kan via een connector of API. Eerst een plan, dan
goedkeuring, dan pas bouwen.

## Zijn antwoorden (2026-09-21)

1. **Providers:** Gmail, Outlook, VU, UvA, mail.com, iCloud ("als het kan").
   Prominent: Gmail en VU.
2. **Scheiding:** voor hem gescheiden; de backend voor Claude mag samengevoegd.
3. **Zonder vragen:** spam in quarantaine (niet direct definitief), afmelden,
   drafts aanmaken. **Verzenden nooit** zonder zijn directe toestemming.
4. **Ritme:** briefing 's ochtends en 's avonds; daartussen doorlopend drafts
   zodra iets binnenkomt, al vóór de briefing.

## Het ontwerp (2026-09-21, herschreven)

Besluit `0007` (proposed), vervangt `0006`. Alle accounts zitten in Mail op
Ollie's Mac, mail.com via Premium. Eén script praat met Mail; alles wat het
kan is per account hetzelfde:

| Wat            | Waar                                   | Zonder vragen |
| -------------- | -------------------------------------- | ------------- |
| Lezen          | Mail, per account, sinds laatste run   | ja            |
| Draft          | Drafts-map van het account zelf        | ja            |
| Spam           | map Ongewenst van het account zelf     | ja            |
| Afmelden       | one-click / https uit de header        | ja            |
| `mailto:`-afmelding | wordt een draft                   | ja            |
| Verzenden      | alleen `email-4`, alleen Ollie's sessie | NOOIT        |

Geplande runs draaien op de Mac zelf (`launchd` + `claude -p`). Briefing
07:30 en 21:30, verwerking elk uur 08:00–22:00. Geen cloud-fallback (default:
uit; Ollie kan het aanzetten).

## Wat nog ontbreekt

De lijst met alle adressen, één per regel met provider en de accountnaam
zoals Mail hem toont. Zonder die lijst is "elk adres heeft een profiel" niet
te controleren.

## Wat "goed" is

- Elk adres heeft een profiel in `email/accounts/` en is één keer echt
  gelezen via `mail.py` op de Mac.
- Elke draft staat in de Drafts-map van het juiste account en noemt bovenaan
  bronadres en afzender.
- Alles wat Claude deed staat in `email/log/YYYY-MM-DD.md`, terug te draaien.
- Een geplande run kan niet verzenden: geen commando zonder de variabele,
  en de guard weigert `osascript` met een verzendopdracht. Test bewijst het.
- Ollie hoeft alleen nog op verzenden te drukken.

## De deeltaken

- `email-0-toegang-testen` — adreslijst → profielen; één `osascript`-regel
  op de Mac die accounts en één bericht laat zien; Automation-toestemming.
- `email-1-mail-script` — `scripts/mail.py` met tests tegen nep-`osascript`,
  guard-regel tegen verzenden.
- `email-2-skill-en-log` — de e-mailmanager-skill, log, state.
- `email-3-geplande-runs` — `launchd`-jobs, briefingbestand, bordtegel.
- `email-4-verzenden-met-toestemming` — het enige pad naar verzenden.

## Geschiedenis

- 2026-09-20: gevangen. 2026-09-21 ochtend: hub-Gmail-ontwerp (`0006`), door
  de checker op vijf punten aangescherpt. Later die dag: alle accounts in
  Mail, mail.com via Premium (doorsturen, POP en IMAP zijn daar alle drie
  betaald) — hub vervalt, `0006` superseded, `0007` proposed.

## Notes

In deze Code-sessie (Linux, cloud) is `mail.py` niet echt te draaien. Tests
mocken `osascript`; de eerste echte run is Ollie's, in `email-0`.

**mail.com (2026-09-21, later):** Premium is aangezet, maar het account synct
nog niet in Mail. Ollie regelt dit zelf; niet aan komen. Tot het synct staat
oliverlugt@mail.com als `tested:` leeg en valt het buiten elke run — het
verschijnt in de briefing onder "kon niet", niet stilzwijgend weg.
