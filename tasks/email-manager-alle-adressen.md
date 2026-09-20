---
title: Claude als e-mailmanager voor alle (~10) adressen — lezen, drafts, spam, afmelden
project: hangar
status: inbox
added: 2026-09-20
effort: L
branch:
---

## Done means

Nog niet schrijfbaar. Eerst moet Ollie vier dingen beslissen (zie onderaan).
Daarna valt dit uiteen in losse taken met elk een eigen finish line.

## Wat er gevraagd is

Ollie, in zijn woorden: Claude als e-mailmanager voor AL zijn adressen, een stuk
of tien, sommige prominenter dan andere. Op de hoogte zijn van de gesprekken,
drafts opstellen voor nieuwe mails en antwoorden, spam bijhouden, afmelden en
verwijderen. Niet alles kan via een connector of API — wat niet kan moet Claude
"als zelfstandige handmatig" controleren. Eerst een plan, dan goedkeuring, dan
pas bouwen.

## Stand op 2026-09-20

- Gmail-connector: verbonden en aan in deze sessie. Dekt één Gmail-account.
- Google Calendar: verbonden, uit in deze chat.
- Microsoft 365 (Outlook): geïnstalleerd, niet verbonden. Relevant als er
  Outlook/VU-adressen bij zitten.
- In deze Code-sessie is van Gmail alleen `delete_draft` zichtbaar; zoeken,
  lezen en drafts maken moet in een claude.ai-chat of Cowork worden geverifieerd.

## De opties

**A — Eén hub-Gmail.** Elk adres wordt doorgestuurd naar (of via POP opgehaald
door) één Gmail. "Send mail as" per adres, zodat een draft de juiste afzender
heeft. Labels per bron-adres. De bestaande Gmail-connector ziet dan alles.
Meeste functionaliteit, geen code, geen eigen credentials in de Hangar.
Kost: ~5 min setup per adres. Grens: adressen die niet mogen doorsturen
(werk/VU) blijven buiten.

**B — Lokale IMAP-skill.** Een script naast `scripts/preview.py` dat op Ollie's
eigen machine draait met app-wachtwoorden per account in de keychain. Leest
alle accounts, schrijft drafts weg in de eigen Drafts-map, verplaatst spam,
volgt `List-Unsubscribe`. Werkt voor Gmail, iCloud, eigen domeinen. Grens:
Outlook.com/M365 laat geen wachtwoord-IMAP meer toe (OAuth verplicht).
Credentials komen nooit in dit repo — de guard blokkeert dat al.

**C — Browser-automatisering.** Playwright in Ollie's ingelogde profiel. Werkt
overal, maar traag, breekbaar bij 2FA en UI-wijzigingen. Alleen als vangnet
voor een adres dat A noch B kan.

**D — Microsoft 365-connector** voor Outlook/VU-adressen. Eén klik verbinden,
daarna zelfde rol als de Gmail-connector.

**Voorstel: A als ruggengraat, D voor Outlook, B alleen voor wat niet mag
doorsturen, C nooit tenzij het echt niet anders kan.** Bovenop de bron komt
één laag die per adres een profiel kent (prioriteit, toon, wat mag zonder
vragen) en een vaste routine: overzicht → drafts → spam → afmelden → log.

## Beslissingen die Ollie moet nemen

1. Welke providers zijn de ~10 adressen, en welke drie zijn prominent?
2. Mag alles samenkomen in één hub-Gmail, of moeten accounts gescheiden blijven?
3. Wat mag zonder vragen: spam verwijderen, afmelden, drafts aanmaken? Wat niet?
4. Ritme: op afroep, één dagelijkse briefing (Routine), of doorlopend?
