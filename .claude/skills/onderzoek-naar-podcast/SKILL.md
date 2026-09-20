---
name: onderzoek-naar-podcast
description: Zet een afgerond onderzoek om in een luisterbare podcast voor Ollie's autorit, via NotebookLM. Gebruik dit zodra een groot onderzoek, deep research, nachtrun of literatuuronderzoek klaar is en hij het wil hóren in plaats van lezen. Triggers o.a. 'maak hier een podcast van', 'ik wil dit in de auto luisteren', 'zet dit onderzoek om in audio', 'podcast van deze research', 'audio overview hiervan', 'kan ik dit onderweg luisteren', 'turn this into a podcast', 'make this listenable'. Levert een bronbestand plus een plak-klare instructie voor NotebookLM, gedimensioneerd op een gekozen lengte (kort/normaal/lang). Voor het onderzoek zelf is onderzoek-sbi beter; voor een geschreven verslag conceptverslag-sbi.
---

# Onderzoek naar podcast

Een afgerond onderzoek omzetten in iets dat Ollie in de auto kan luisteren.

Deze skill maakt **geen audio**. Hij maakt de twee dingen die NotebookLM nodig
heeft om goede audio te maken, en dat is bewust: NotebookLM's Audio Overview is
gratis, heeft twee natuurlijke stemmen die geen enkele lokale TTS benadert, en
heeft geen publieke API. De laatste dertig seconden doet Ollie zelf.

## Wat je oplevert

Twee bestanden, in dezelfde map als het onderzoek (of in `~/Downloads/` als er
geen logische map is):

| Bestand                  | Wat het is                                                 |
| ------------------------ | ---------------------------------------------------------- |
| `<slug>-bron.md`         | Het onderzoek, herschreven om voorgelezen te worden.        |
| `<slug>-instructie.txt`  | De tekst die Ollie in NotebookLM's *Customize*-veld plakt.  |

Plus, in de chat, vier regels: upload dit, plak dat, druk hier, download naar
je telefoon. Niet meer.

## Stap 1 — lengte vaststellen

Drie presets. Vraag alleen als hij niets zei; kies anders zelf op basis van wat
hij noemde ("even naar college" = kort).

| Preset      | Doelduur | Secties in de bron | Woorden in de bron |
| ----------- | -------- | ------------------ | ------------------ |
| **Kort**    | ~10 min  | 3–4                | 1.200–1.800        |
| **Normaal** | ~25 min  | 7–9                | 3.000–4.500        |
| **Lang**    | ~45 min  | 12–15              | 6.000–9.000        |

**Het aantal secties is de echte knop, niet het woordenaantal.** De twee hosts
besteden ongeveer 2 tot 3 minuten per onderscheiden onderwerp, vrijwel los van
hoeveel tekst eronder ligt. Wil je korter: gooi secties weg, niet zinnen.

NotebookLM's plafond ligt rond de 30 minuten per aflevering. Vraagt Ollie om
**Lang**, zeg dan één keer dat het waarschijnlijk op ~30 min afkapt, en bied aan
de bron in twee delen te splitsen — deel 1 heenrit, deel 2 terugrit.

## Stap 2 — taal kiezen

Kies op het onderwerp, niet op de taal van de vraag:

- **Studiestof, SBI-vakken, Nederlandse casussen** → Nederlands.
- **Tech, AI, internationaal onderzoek, Engelstalige bronnen** → Engels.
- Twijfel → de taal van de meeste bronnen.

Eén ding om te weten en één keer te zeggen als het Nederlands wordt:
**NotebookLM's Shorter/Default/Longer-knop werkt alleen bij Engels.** In het
Nederlands komt de lengte dus volledig uit hoeveel secties jij in de bron zet.
Houd je dan strak aan de tabel hierboven — dat is het enige stuur dat er is.

## Stap 3 — de bron schrijven

Niet knippen en plakken uit het onderzoek. Herschrijven om gehóórd te worden,
in de auto, door iemand die niet kan terugbladeren.

Regels:

1. **Conclusie eerst.** De eerste sectie is het antwoord. Hij kan er zijn
   voordat de aflevering af is; wat er dan gezegd is moet het belangrijkste zijn.
2. **Geen visuele taal.** Geen tabellen, geen code, geen "zoals te zien in",
   geen opsommingen die je moet meetellen. Een tabel wordt een zin.
3. **Getallen met perspectief.** Nooit een kaal getal: altijd het totaal en het
   aandeel erbij. "Veertien van de tweeëntwintig, dus ruim zes op de tien."
4. **Namen en cijfers één keer voluit.** Afkortingen de eerste keer uitspreken.
5. **Elke sectie is een gesprek waard.** Eén kop, één vraag die hij zou stellen,
   het antwoord, en wat eraan schuurt. Een sectie zonder spanning wordt saaie
   audio — voeg het samen met een andere of laat het weg.
6. **Onzekerheid blijft staan.** Wat slecht onderbouwd was in het onderzoek is
   slecht onderbouwd in de podcast. Nooit gladstrijken omdat het beter klinkt.
7. **Bronnen niet voorlezen.** Geen DOI's, geen URL's, geen APA. Wel "een studie
   uit 2024 onder duizend deelnemers". De verwijzingen blijven in het onderzoek.

Vorm van het bestand:

```markdown
# <Onderwerp> — <preset>, <taal>

## Waar dit op uitkomt
<De conclusie, 150-250 woorden. Het antwoord, niet de aanloop.>

## <Sectie 2>
<...>
```

Geen frontmatter, geen metadata — NotebookLM leest het als bron en alles wat
erin staat kan voorgelezen worden.

## Stap 4 — de instructie schrijven

Dit is het `Customize`-veld in NotebookLM. Het is één alinea, Engels (het veld
werkt daar het best, ook bij een Nederlandse aflevering), en het benoemt:

- de doelduur in minuten;
- de taal van de aflevering;
- waar de focus ligt en wat overgeslagen mag worden;
- de luisteraar: eerstejaarsstudent, in de auto, geen voorkennis van dit
  specifieke onderzoek, wél slim;
- toon: twee mensen die het onderwerp interessant vinden, geen enthousiasme
  die er niet is.

Sjabloon:

```
Target length: about <N> minutes. Speak in <taal>.
Audience: a sharp first-year university student listening while driving —
no prior knowledge of this specific research, but quick. Lead with the
conclusion; do not save it for the end. Spend roughly equal time on each
section. Keep every number in perspective (say the total and the share, not
a bare figure). Skip methodology detail and source citations. Where the
research is uncertain, say so plainly instead of smoothing it over.
Tone: two people who genuinely find this interesting. No hype.
```

Vul `<N>` en `<taal>` in. Laat de rest staan.

## Stap 5 — de vier regels

Sluit af met precies dit, ingevuld:

```
1. notebooklm.google.com → nieuw notebook → upload <slug>-bron.md
2. Audio Overview → Customize → plak <slug>-instructie.txt
3. Format: Deep Dive. <Bij Engels: Length: Shorter / Default / Longer.>
4. Genereren duurt een paar minuten. Download als .m4a → je telefoon.
```

Bij Engels vul je de lengteknop in volgens de preset: Kort → Shorter,
Normaal → Default, Lang → Longer. Bij Nederlands laat je regel 3 de knop weg
en noem je hem niet — hij bestaat daar niet.

## Grenzen

- **Verzin geen onderzoek.** Deze skill zet om wat er is. Is een sectie dun,
  dan is de podcast op dat punt dun. Vul niets aan omdat het lekkerder loopt.
- **Gratis tier: 3 afleveringen per dag.** Genoeg voor één rit; noem het alleen
  als Ollie er meer dan drie achter elkaar wil.
- **Geen betaalde TTS, geen API-keys.** Gaat hij ooit naar volledig automatisch,
  dan is dat Kokoro of Piper — lokaal en gratis — en een apart besluit.
- Gaat het over een nachtrun: lees het echte resultaat, niet de samenvatting in
  `planning/night-log.md`. Die is voor de trail, niet voor de inhoud.
