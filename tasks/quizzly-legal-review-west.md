---
title: Quizzly: compliance-review westerse landen (EU/VK/VS/CA/AU)
project: quizzly
status: inbox
added: 2026-08-08
effort: M
branch:
---

## Done means

Nog aan te scherpen na merge van PR #1, dat al een deel dekt (GDPR-export,
age gate, retentie). Beoogd resultaat: docs/COMPLIANCE-REVIEW.md dat de echte
dataflows in de code (niet alleen de docs) toetst aan GDPR incl. kinderen, UK
GDPR, COPPA, CCPA/CPRA, PIPEDA en de Australische Privacy Act — per punt
gedekt/ontbreekt/besluit-van-Ollie-nodig, gemarkeerd must/should/could, met de
expliciete disclaimer dat dit geen juridisch advies is.

## Notes

docs/LEGAL.md bestaat al en noemt ook het patentrisico in deze productcategorie.
De legal-pagina's hebben nog [BRACKETED] placeholders — die vullen kan alleen
Ollie (echte contactgegevens).

**Herchecked 2026-08-13:** `quizzly#1` staat nog open, niet gemerged — dus de
blokkade geldt onveranderd. Blijft `inbox`. `quizzly#1` bevat naast de
GDPR-export/age-gate/retentie ook een versiebump naar 1.0.0 en deploy-config
(`fly.toml`), dus dat is sowieso geen taak die een nachtrun zelf mag mergen
(regel 6, "nooit iets deployen of aanzetten dat geld kost") — die PR wacht op
Ollie's launch-besluit, niet op onderzoek. Vraag voor Ollie: wanneer wil je
`quizzly#1` mergen, zodat deze taak daarna pas echt aan te scherpen is?
