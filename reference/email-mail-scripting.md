# Mail op de Mac — wat osascript teruggaf

Invoer voor `scripts/mail.py`. Gedraaid door Ollie op 2026-09-21, letterlijk:

```
$ osascript -e 'tell application "Mail" to get name of every account'
iCloud, VU, UvA, Bas en Ollie, Personal Gmail, Wandarbear , Subliem, Ollie2005, Wandarbear Media

$ osascript -e 'tell application "Mail" to get subject of first message of inbox'
Een klein cadeautje voor jou! on Untappd!
```

Dus: Automation-toestemming staat, Mail antwoordt, en er zijn **negen**
accounts in Mail. Let op de spatie achter `Wandarbear ` — dat is de echte
accountnaam en `mail_account:` moet hem exact zo hebben. mail.com (Premium)
is nog niet gesynct en staat er dus niet bij; Ollie regelt dat zelf.

Adressen per account haalt deze regel op:

```
osascript -e 'tell application "Mail" to get {name, email addresses} of every account'
```

`scripts/mail.py` gebruikt JXA (`osascript -l JavaScript`), niet AppleScript:
datums komen dan als ISO-strings en de uitvoer is JSON zonder gepriegel met
`text item delimiters`.
