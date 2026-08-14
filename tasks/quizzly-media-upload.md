---
title: Quizzly: afbeeldingen uploaden op slides (nu alleen URL)
project: quizzly
status: doing
added: 2026-08-08
effort: M
branch: night/quizzly-media-upload
---

## Done means

In de vraag-editor kun je een afbeelding úploaden (niet alleen een URL plakken):
grootte-gecapt, mime-gesniffd op magic bytes, EXIF gestript, opgeslagen in een
Docker-volume buiten de repo, same-origin geserveerd, alleen door de quiz-eigenaar.
De drie bestaande beeld-layouts (image-above/split/full-bleed) werken ermee, de
URL-route blijft bestaan, cover-image van een quiz kan ook. Compose heeft het
volume, README de limieten. Trio groen.

## Notes

De halve feature bestaat al: `presentation.media` (URL) + verplichte alt-tekst +
drie layouts in `src/lib/theme.ts`. Alleen het uploaden ontbreekt.
