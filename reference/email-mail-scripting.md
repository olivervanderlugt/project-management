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
