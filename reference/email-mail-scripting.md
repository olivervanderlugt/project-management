# Mail op de Mac — wat osascript teruggaf

Invoer voor `scripts/mail.py`. Gedraaid door Ollie op 2026-09-21, letterlijk:

```
$ osascript -e 'tell application "Mail" to get name of every account'
iCloud, VU, UvA, Bas en Ollie, Personal Gmail, Wandarbear , Subliem, Ollie2005, Wandarbear Media

$ osascript -e 'tell application "Mail" to get subject of first message of inbox'
Een klein cadeautje voor jou! on Untappd!
```

Dus: Automation-toestemming staat, Mail antwoordt, en er zijn **negen**
accounts in Mail. Let op de spatie achter `Wandarbear ` — Mail staat dat toe, platte
frontmatter niet. Profielen bewaren de naam getrimd; `mail.py` zoekt eerst
exact en dan getrimd, dus beide werken. mail.com (Premium)
is nog niet gesynct en staat er dus niet bij; Ollie regelt dat zelf.

Adressen per account haalt deze regel op:

```
osascript -e 'tell application "Mail" to get {name, email addresses} of every account'
```

`scripts/mail.py` gebruikt JXA (`osascript -l JavaScript`), niet AppleScript:
datums komen dan als ISO-strings en de uitvoer is JSON zonder gepriegel met
`text item delimiters`.

## Profielen vullen — één commando op de Mac

```
cd ~ && git clone -b claude/multi-email-manager-system-ozr70l https://github.com/olivervanderlugt/project-management.git Hangar
cd ~/Hangar && python3 scripts/mail_profiles.py
```

De Hangar staat op de Mac in `~/Hangar` (aangemaakt 2026-09-21; het repo is
publiek, dus klonen vraagt geen login — pushen wel). Staat hij er al:
`cd ~/Hangar && git fetch origin && git checkout <branch> && git pull`.

Leest de adressen uit Mail, schrijft ze in `email/accounts/`, raadt de
provider uit het domein en vraagt per account alleen wat nog leeg is, met
Enter-als-default. `--yes` slaat alle vragen over. Daarna:
`git add email/accounts && git commit -m 'Vul e-mailprofielen' && git push`.

## Eerste echte run van `mail.py` (2026-09-21)

`python3 scripts/mail.py accounts` op de Mac gaf negen accounts met adres,
exact zoals Mail ze kent — het JXA-idioom voor accounts klopt dus. Twee
adressen uit Ollie's tabel bleken anders: iCloud is `oliverlugt@icloud.com`
(niet zijn Apple ID) en Subliem eindigt op `.nl`. Profielen aangepast en
alle negen `tested: 2026-09-21`. Nog onbewezen: `unread`, `draft`, `junk`.

## Tweede echte run (2026-09-21, later)

- `unread --account "Personal Gmail" --limit 3` → één ongelezen mail, id
  1007, met account, afzender en ISO-datum. De unified-inbox-filter en de
  sortering werken.
- `draft --account "Personal Gmail" --to … --subject "Hangar test"` →
  `saved: true`, afzender door Mail zelf opgelost als
  `Oliver van der Lugt (wandarbear) <oliverlugt@gmail.com>`. Het compose-
  idioom (`OutgoingMessage` + `ToRecipient` + `save` + `close saving`)
  geeft geen fout. Twee keer gedraaid, dus twee drafts "Hangar test".
- Nog te bevestigen door Ollie: staat de draft in Mail onder Drafts van
  Personal Gmail? En `read 1007 --account "Personal Gmail"` (per-account
  lookup en header-parsing).
- Nog nooit gedraaid: `junk`, `unsubscribe`.
