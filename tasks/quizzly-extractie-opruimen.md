---
title: Quizzly: extractie-restanten uit README en docs halen
project: quizzly
status: ready
added: 2026-08-06
effort: S
branch:
---

## Done means

De README van `olivervanderlugt/quizzly` beschrijft de repo zoals hij nu is:
geen noot meer over een `percentile/`-subdirectory, geen `cd <repo>/quizzly` in
de quick start. `docs/MOVING-TO-ITS-OWN-REPO.md` is weg of expliciet gemarkeerd
als afgerond — maar de drie prioriteiten uit zijn "What's next" (password
reset, nickname-filter, legal-placeholders) verhuizen eerst naar het
projectbestand of naar taken, zodat ze niet met het document verdwijnen.
`npm run typecheck && npm test && npm run build` blijft groen.

## Notes

De extractie is op 2026-08-06 gebeurd; README en docs beschrijven nog de oude
situatie waarin Quizzly in `quizzly/` naast `percentile/` in de gedeelde
`claude`-repo woonde. Die drie prioriteiten staan al samengevat in
`projects/quizzly.md` — controleer alleen dat er niets uit het document
verloren gaat dat nergens anders staat.
