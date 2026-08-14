---
title: Quizzly: afbeeldingen uploaden op slides (nu alleen URL)
project: quizzly
status: done
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

**Nacht 2026-08-14: gebouwd, adversarieel gecheckt, gemerged.** `sharp` her-
encodeert naar WebP (≤2000px, geen `.withMetadata()` → EXIF weg, geverifieerd
voor JPEG/PNG/WebP incl. echte GPS-EXIF), magic-byte sniffing zonder de
client-Content-Type te vertrouwen, 5 MiB-cap op echte bytes, `resolveKey`
blokkeert path traversal, owner-only op beide schrijfpaden (vraagafbeelding +
cover-image, `Quiz.coverImage` was een dode kolom en is nu echt bruikbaar).
Lezen is een onauthenticated capability-URL, bewust — zelfde postuur als de
bestaande URL-plak-optie, die blijft ongewijzigd werken. `docker-compose.yml`
kreeg het `media-uploads`-volume; README/SECURITY.md de limieten. Branch was
gecut vóór `41e8abf` (dezelfde compose-parse-fix, onafhankelijk op `main`
geland) — gemerged met `main`, conflict was alleen commentaartekst, trio
opnieuw groen na de merge (106/106 tests). Checker-verdict: finish line
volledig gehaald. Gemerged als quizzly#3.
