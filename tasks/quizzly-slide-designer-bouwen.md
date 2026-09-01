---
title: Quizzly: slide-designer — fase 1 bouwen
project: quizzly
status: inbox
added: 2026-08-12
effort: M
branch:
---

## Done means

Nog niet schrijfbaar. Wacht op twee dingen: `docs/SLIDE-DESIGNER.md` bestaat
nog niet op `main` (staat alleen op de nog niet gemergede `quizzly#6`) en
Ollie's keuze welke fase-1-scope uit de roadmap daarin hij daadwerkelijk wil —
de aanbeveling in dat document is een voorstel, geen besluit dat een nachtrun
zelf mag nemen.

## Notes

Fase 2 van de oorspronkelijke `quizzly-slide-designer`-taak, losgetrokken in
de nacht van 2026-08-12 omdat "verken de mogelijkheden" en "bouw fase 1" twee
verschillende beslissingen zijn — de eerste is onderzoek dat een nachtrun kan
doen, de tweede vraagt een smaakkeuze van Ollie. Zie die taak en
`docs/SLIDE-DESIGNER.md` (zodra het bestaat) voor de volledige context.

## Aangescherpt 2026-09-01 (nachtrun, stap 3)

`docs/SLIDE-DESIGNER.md` bestaat nu wél, alleen nog niet op `main` — gelezen
rechtstreeks uit `quizzly#6` (branch `night/quizzly-slide-designer`, nog
open, ongewijzigd sinds 2026-08-14). Het document eindigt met een expliciete,
concrete aanbeveling (§7): **fase 1 = een vast palet van 8–12 per-vraag-
achtergronden (hergebruikt `backgroundSchema`) + emoji per vraag (vast
raster, geen vrije tekst) + een echte live preview in de vrageneditor**
(`QuestionFrame` + `AnswerInput` + een in de editor gebouwde
`PlayerQuestionView`, hergebruikt bewezen client-veilige code). Redenen die
het document zelf geeft: het is de enige fase die vandaag beslisbaar is (fase
3/GIF's en fase 4/audio hangen aan een provider-, budget- en
licentierisicokeuze van Ollie), de helft van de code bestaat al
(`presentation`-veld met `accentOverride` als precedent, `backgroundCss()`,
een bewezen los-renderbare `QuestionFrame`), en er komt geen nieuw
juridisch oppervlak bij (geen derde partij, geen upload, geen doorgifte —
dus niets in `docs/LEGAL.md` nodig). Het document geeft ook een concrete
acceptatielijst mee (§6, "Wat de bouwtaak moet aantonen") mocht Ollie fase 1
kiezen: beide nieuwe velden `.optional()` + een test die een oude snapshot
er ongewijzigd doorheen parst (de `Game.quizSnapshot`-val uit §1.3), een
regressietest dat een vraag zonder achtergrond exact blijft renderen zoals
vandaag, en een contrastcheck per achtergrond (4,5:1 tekst / 3:1
antwoordtegels, dezelfde methode als `docs/DESIGN.md`).

**Blijft `inbox`.** De aanbeveling is scherp en goed onderbouwd, maar het is
en blijft een voorstel — dit taakje mag zelf niet kiezen dat fase 1 het wordt,
en de dragende doc staat sowieso nog niet op `main`. Wat er nu ligt, ligt er
zodat de stap naar `ready` bij Ollie's akkoord één regel Done-means kost, geen
nieuw onderzoek: neem §6 "Fase 1" letterlijk over als scope zodra hij
`quizzly#6` merget en ja zegt tegen deze fase (of een andere kiest — de
andere opties staan in §2/§3 van het document).
