---
name: email-manager
description: One round over Ollie's mail through Mail on his Mac — read what is new per account, draft replies in his style, junk spam, unsubscribe without sending, log every action. Use for the morning and evening briefing, the hourly pass, or when Ollie asks what came in. Never sends; sending is its own section and only Ollie's session may enter it.
---

# E-mailmanager

Eén vaste ronde, altijd dezelfde, alleen via `scripts/mail.py`. Dit bestand
is de enige plek waar de beslisregels staan; `mail.py` beslist niets, het
praat alleen met Mail. Besluit `0007` is de grond onder alles hieronder.

Draait alleen op Ollie's Mac, met Mail open of te openen. Op Linux (deze
cloud-omgeving) bestaat `osascript` niet: dan stopt de ronde met één regel
in het log en verzint niets.

## Voor de ronde

1. `git fetch` en vergelijk met de remote; werk op de huidige branch.
2. Lees `email/accounts/*.md` (niet `_template.md`). Sorteer op `priority`
   (1 eerst), dan alfabetisch. Sla profielen zonder `tested:` over en noem
   ze onder "kon niet".
3. Lees `email/state.md`: per account de laatst verwerkte tijd (ISO). Geen
   regel voor een account → 24 uur terug.
4. Lees `scripts/mail_profiles.py` niet en run hem niet — profielen zijn
   Ollie's werk.

## De ronde, per account

```
python3 scripts/mail.py unread --account "<mail_account>" --since <state>
```

Per mail, in deze volgorde, één uitkomst:

1. **Nooit spam.** Afzender of domein staat in `never_spam:` van het profiel
   → sla stap 3 over. Alles verder gewoon.
2. **Antwoord nodig?** Een echte persoon of instantie stelt een vraag, vraagt
   om een actie, of wacht op iets van Ollie. Dan:
   `python3 scripts/mail.py read <id> --account "<mail_account>"` en een
   draft via `schrijfstijl-ollie`, in de `language` en `tone` van het
   profiel. Regel 1 van de body: `[<address> · antwoord aan <afzender>]`,
   dan een lege regel, dan de mail. Opslaan met
   `python3 scripts/mail.py draft --account "<mail_account>" --reply-to <id> --body-file <tmp>`.
   Nooit meer dan één draft per mail; een tweede ronde over dezelfde mail
   maakt geen tweede draft.
3. **Spam?** Onbekende afzender, phishing, "u heeft gewonnen", een factuur
   die Ollie niet herkent, een login-waarschuwing van een dienst die hij
   niet heeft. Bij twijfel: geen spam. Wel spam →
   `python3 scripts/mail.py junk <id> --account "<mail_account>"`. Nooit
   verwijderen — dat kan het script ook niet.
4. **Nieuwsbrief?** Er is een `List-Unsubscribe`-header (zie `unsubscribe`
   in de uitvoer van `read`). Alleen als het profiel `auto_unsubscribe: yes`
   heeft én de mail niet iets is wat Ollie duidelijk wil (een dienst die hij
   gebruikt, een vereniging waar hij lid van is):
   - `one_click: true` → één HTTPS POST naar de URL met body
     `List-Unsubscribe=One-Click`. Dat is de RFC 8058-vorm.
   - alleen een `https` URL, geen one-click → open de URL met één GET.
   - alleen `mailto:` → geen mail sturen. Maak een draft aan dat adres met
     onderwerp `unsubscribe` en regel 1 `[<address> · afmelding voor <afzender>]`;
     Ollie verstuurt hem zelf of niet.
   - Links uit de body worden nooit gevolgd. Alleen de header.
5. **Niets.** Informatief, geen actie. Noem het wel in de briefing als het
   prioriteit 1 is.

Na elk account: schrijf de tijd van de nieuwste verwerkte mail (of "nu" als
er niets was) in `email/state.md` onder de accountslug.

## Het log

`email/log/YYYY-MM-DD.md`, één regel per actie, aanmaken als hij ontbreekt:

```
- HH:MM · <accountslug> · <afzender> · draft | junk | unsubscribe | unsubscribe-draft · <reden in ≤ 10 woorden>
```

Een ronde zonder één actie schrijft precies één regel:
`- HH:MM · ronde · niets nieuws sinds <oudste state>`. Nooit een lege dag,
nooit een verzonnen actie. Wat niet kon (profiel zonder `tested:`, `junk`
dat alleen kon vlaggen, `osascript` afwezig) is ook een regel, met `kon niet`.

Elke regel moet Ollie terug kunnen draaien: een junk-regel noemt het id, een
afmelding de URL of het adres.

## De briefing

Alleen als de ronde als briefing is gestart (07:30, 21:30, of Ollie vraagt
erom): `email/briefings/YYYY-MM-DD-am.md` of `-pm.md`. Per account op
prioriteit, alleen accounts met iets te melden:

```
## <mail_account> (<address>)
- Vraagt antwoord: <afzender> — <onderwerp> → draft staat klaar
- Nieuw, geen actie: <n> mails, het belangrijkste: <één regel>
- Naar Ongewenst: <n>  ·  Afgemeld: <n>
```

Onderaan altijd `## Kon niet` — ook als het leeg is: dan staat er "niets".
Twee runs zonder nieuwe mail geven een briefing van drie regels. Wat er niet
was, staat er niet in.

## Verzenden

Deze ronde verzendt niets. `mail.py` heeft geen `send` zonder
`HANGAR_EMAIL_SEND_OK=1`, die variabele staat alleen in Ollie's eigen shell,
en `scripts/guard.py` weigert elke andere weg. Het enige pad naar verzenden
staat in `tasks/email-4-verzenden-met-toestemming.md` en bestaat pas als die
taak `done` is: Ollie noemt in zijn eigen sessie een draft en zegt
"verstuur", Claude leest de draft terug, en dan pas. "Stuur alles maar" is
geen toestemming per mail.

## Wat je nooit doet

- Een mail verwijderen, of een junk-verplaatsing "even" naar Prullenbak.
- Een link uit een mailbody openen.
- Een draft schrijven namens een ander account dan waar de mail binnenkwam.
- Een tweede draft voor dezelfde mail.
- Een wachtwoord of token in een profiel zetten — de guard weigert het.
- Iets in de briefing zetten dat niet in het log staat.
