---
title: Quizzly: wachtwoord tonen/verbergen op elk wachtwoordveld
project: quizzly
status: blocked
added: 2026-08-08
effort: S
branch: night/quizzly-wachtwoord-toggle
---

## Done means

Elk wachtwoordveld (login, signup, en de change-password/reset-velden uit PR #1
als die gemerged zijn) heeft een toegankelijke toon/verberg-knop: standaard
verborgen, `aria-pressed` en een label, met toetsenbord bedienbaar, geen
autocomplete-regressie. Trio groen.

## Notes

Gevraagd door Ollie op 2026-08-08. Zit ook in de uitbouw-startprompt
(`reference/startprompt-quizzly-uitbouw.md`) als fase 1.

## Waar het staat (2026-08-14)

Gebouwd en adversarieel gecheckt in een sessie op Ollie's verzoek, niet door de
nachtrun. **quizzly#4** staat open en wacht op zijn merge — een dagsessie mergt
zijn eigen PR niet; dat is regel 3 van de nachtrun, en die geldt hier niet.

Eén herbruikbare `PasswordInput` (`src/components/PasswordInput.tsx`), gebruikt
door `AuthForm.tsx` voor zowel login als signup. Verborgen bij start,
`aria-pressed` gebonden aan dezelfde state die het `type` stuurt, `aria-label`
wisselt mee ("Toon/Verberg wachtwoord"), echte `<button type="button">` dus
Tab + Enter/Space werken vanzelf, en `autoComplete` overleeft het wisselen
omdat alleen `type` uit state komt en de rest doorgespreid wordt.

Buiten scope, expliciet nagelopen: de change-password/reset-velden zitten in
PR #1 en die is nog niet gemerged. Het AI-API-sleutelveld in `AiKeyForm.tsx` is
geen wachtwoordveld in de zin van deze taak. Er is geen confirm-password-veld.

Trio zelf gedraaid door de checker: typecheck exit 0, 112 tests groen (9
bestanden), build compleet.

**Openstaand puntje, geen finish-line-fout:** `PasswordInput.test.tsx` toetst
alleen de statische markup. Dat `aria-pressed` echt omklapt bij een klik is
gelezen, niet getest. Wil je dat dichtgetimmerd, dan is dat een los taakje.
