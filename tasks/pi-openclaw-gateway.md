---
title: Pi 5 met OpenClaw als vangpoort — telefoonbericht wordt taak in tasks/
project: hangar
status: ready
added: 2026-08-07
effort: M
branch:
---

## Done means

Ollie stuurt vanaf zijn telefoon een Telegram-bericht naar zijn eigen bot, en
binnen vijf minuten staat er een nieuw bestand in `tasks/` met `status: inbox`,
een titel en de tekst van het bericht, gepusht en na de Pages-run zichtbaar op
het bord. Daarbij is te controleren dat: (1) er vanaf buiten het thuisnetwerk
niets op de Pi bereikbaar is, (2) berichten van een ander Telegram-account
genegeerd worden, (3) de drie tokens (Claude, GitHub, Telegram) alleen op de Pi
staan, en (4) er geen maandelijkse kosten bijgekomen zijn.

Let op: dit is fysiek werk bij Ollie thuis — bestellen, aansluiten,
configureren. De nachtrun kan hier niets bouwen en moet deze taak laten liggen;
dit bestand ís het plan.

## Boodschappenlijstje (prijzen gecheckt 2026-08-07)

Eerst het slechte nieuws: de Pi 5 is fors duurder geworden. Door het
LPDDR4-geheugentekort verhoogde Raspberry Pi de prijs in februari 2026 voor de
tweede keer in drie maanden (8 GB nu $125 MSRP). Alles onder ~€180 in
zoekresultaten is een verouderde cache.

| Onderdeel | Prijs | Bron |
|---|---|---|
| Raspberry Pi 5, 8 GB | ~€184–189 | Geizhals (laagste €184,49), Welectron €189 |
| Officiële 27W USB-C voeding | €12–16 | Welectron €11,90 |
| microSD 128 GB A2 (SanDisk Extreme) | €20–32 | bol.com / Amazon.nl |
| Officiële Active Cooler | ~€8 | Opencircuit €8,55 |
| Officiële Pi 5-behuizing | €14–16 | Opencircuit €15,95 |
| **Totaal los, incl. verzending** | **~€235–265** | |

Goedkopere route om eerst te checken: het SOS Solutions "Raspberry Pi 5 8GB
Starter Kit" stond op 2026-08-07 afgeprijsd van €219,95 naar **€181,78** —
minder dan een los bord elders. Als die actie nog loopt is dat de koop.

NVMe (M.2 HAT + SSD) is voor dit doel overkill: SSD-prijzen zijn ook gespiked
(500 GB ~€109) en een goede A2-kaart is ruim voldoende voor een lichte
gateway. De Active Cooler is géén luxe: zonder koeling throttlet de Pi al na
~90 seconden inferentie, wat telt zodra het terugvalmodel draait.

**Gratis alternatief, één alinea:** de oude pc/laptop met 8 GB die er nog ligt
kan dit ook — x86 is voor OpenClaw zelfs het meest gebaande pad, en het scheelt
~€200. Nadelen: meer stroomverbruik (laptop ~10–20 W tegen ~3–5 W voor de Pi,
op jaarbasis een tientje of twee verschil) en een apparaat dat al ergens voor
diende. Wie eerst wil proeven voor hij bestelt: zet OpenClaw op de laptop, en
verhuis de config later in een uurtje naar de Pi.

## Kanaal: Telegram

Telegram, omdat het als enige kanaal alleen een bot-token van BotFather nodig
heeft — geen QR-herkoppeling zoals WhatsApp, geen aparte signal-cli-daemon
zoals Signal — en in de OpenClaw-docs als gebundeld en stabielst geldt.

## Stappenplan

1. **Bestellen** (10 min). Eerst het SOS-kit checken, anders los bij
   Kiwi/Welectron/Opencircuit. *Check: orderbevestiging.*
2. **In elkaar zetten** (15 min). Active Cooler op het bord, bord in de
   behuizing. *Check: ventilator draait bij het opstarten.*
3. **OS flashen** (20 min). Op de laptop met Raspberry Pi Imager: Raspberry Pi
   OS **Lite 64-bit** (32-bit werkt niet met OpenClaw), en in de Imager alvast
   hostnaam, gebruiker, wifi en je SSH-sleutel instellen. *Check: `ssh
   ollie@hangar-pi.local` werkt vanaf de laptop.*
4. **Basis** (15 min). `sudo apt update && sudo apt full-upgrade`, daarna
   `unattended-upgrades` aanzetten zodat het kastje zichzelf patcht. *Check:
   `apt` meldt niets meer te doen; unattended-upgrades staat op enabled.*
5. **Node 26** (10 min). Via NodeSource. OpenClaw eist Node 26 op de Pi.
   *Check: `node -v` toont v26.x.*
6. **OpenClaw** (30 min). `npm install -g openclaw@latest`, dan `openclaw
   onboard` en de gateway als systemd-service laten installeren. Native
   installatie, geen Docker — ARM64-images zijn onbetrouwbaar gedocumenteerd
   (issue #41881), en `openclaw update` kan op ARM struikelen over native
   modules (opus/sqlite3); de Discord- en mem0-plugins uit laten. *Check:
   service draait en overleeft `sudo reboot`.*
7. **Telegram-bot** (15 min). Bij @BotFather een bot aanmaken, token in de
   OpenClaw-config, en meteen de allowlist op je eigen Telegram-user-ID.
   *Check: bericht van jouw telefoon krijgt antwoord; vanaf een tweede account
   komt er niets.*
8. **Claude Max koppelen** (15 min). Op de laptop `claude setup-token` draaien
   (geeft een token dat met `sk-ant-oat01` begint), op de Pi in OpenClaw
   plakken via `openclaw models auth paste-token --provider anthropic`. Zet het
   standaardmodel voor dit kanaal op een klein model (Haiku) — vangst heeft
   geen zwaar model nodig en dit spaart je gedeelde limiet. *Check: de bot
   antwoordt aantoonbaar via Claude.*
9. **Hangar koppelen** (45–60 min). Op GitHub een fine-grained token aanmaken
   dat alléén dit repo mag zien en alléén Contents read/write heeft. Repo
   klonen op de Pi. In de OpenClaw-workspace een capture-instructie plus een
   klein script: bericht in → `tasks/<slug>.md` uit het template, `status:
   inbox`, `added` vandaag, bericht als tekst → commit en push. Het script
   weigert elk pad buiten `tasks/` en elke status behalve `inbox` — de
   Pi-versie van de guard, afgedwongen in code en niet alleen in de prompt.
   *Check: testbericht "test vanaf de bank" → binnen 2 min staat het bestand
   op GitHub en na de Actions-run op het bord.*
10. **Dichtzetten** (20 min, vaste stappen — zie Veiligheid). *Check: vanaf 4G
    (wifi uit) is niets van de Pi bereikbaar; `sudo ufw status` toont deny
    incoming.*
11. **Altijd-aan-test** (10 min). Stekker eruit, stekker erin. *Check: binnen
    ~2 minuten antwoordt de bot weer, zonder dat je iets hebt aangeraakt.*
12. **Optioneel, terugval** (30 min + download). Ollama installeren (officiële
    ARM64-build, `curl -fsSL https://ollama.com/install.sh | sh`) en
    `qwen2.5:3b-instruct` binnenhalen. Niet aanzetten als standaard; het staat
    klaar voor de dag dat de abonnementsroute dichtgaat. *Check: provider
    tijdelijk omschakelen, testbericht wordt (traag, ~20 s) een nette taak.*

Totaal na bezorging: een middag, ruwweg 3–4 uur.

## Veiligheid (vaste stappen, geen voetnoot)

- **Niets open naar het internet.** Geen port forwarding op de router, geen
  tunnel, geen publieke webhook: OpenClaw haalt Telegram-berichten via
  uitgaande long-polling op. De Pi maakt alleen uitgaande verbindingen
  (Telegram, Anthropic, GitHub). Firewall: deny incoming, SSH alleen vanaf het
  LAN; de OpenClaw-webinterface alleen op localhost.
- **De login blijft op het kastje.** Het Claude-token, het GitHub-token en het
  Telegram-token staan alleen op de Pi (bestandsrechten 600), nooit in het
  repo, nooit in een chat. Het GitHub-token is fine-grained: dit ene repo,
  alleen Contents.
- **De Hangar-regel blijft gelden.** Alles wat via de bot binnenkomt wordt
  `status: inbox`, zonder uitzondering. De bot promoveert nooit naar `ready`,
  bouwt nooit, en raakt niets buiten `tasks/` aan — afgedwongen door het
  capture-script, niet door een verzoek in de prompt.

## Risico's

- **Anthropic sluit de abonnementsroute.** Reëel: in 2026 is dit beleid al
  vier keer gekanteld (blokkade jan → ToS-verbod feb → harde afsluiting 4 apr
  → hersteld mei/juni). Sinds 15 juni werkt het weer expliciet zoals voorheen,
  maar Anthropic heeft aangekondigd de bundeling te herzien — reken erop dat
  dit nog een keer verandert, mogelijk van de ene op de andere dag. Wat er dan
  stopt: alleen de motor; Telegram, de Pi en het capture-script merken er
  niets van. Overstap is één configuratieregel, twee smaken:
  - *API-sleutel met Haiku* ($1/MTok in, $5/MTok uit): bij ~20 berichten per
    dag ergens tussen €3–5/mnd (met prompt caching, dat op API-sleutels wél
    werkt) en ~€13/mnd (zonder). Slimste route als de bot ook antwoorden moet
    blijven geven.
  - *Lokaal model* (`qwen2.5:3b-instruct` via Ollama, stap 12): €0, ~5–6
    tokens/s, dus ~20 s per taakbestand. Prima voor pure vangst, ongeschikt
    voor echte gesprekken.
- **Gedeelde limieten.** De gateway trekt uit dezelfde pot als Claude Code en
  de nachtruns (5-uursvenster + weeklimiet), en setup-tokens krijgen géén
  prompt caching, dus elk botbericht is relatief duur. Dempen: klein model
  voor de vangst (stap 8). Loopt de pot leeg, dan zwijgt de bot tot het
  venster verspringt; berichten blijven gewoon in Telegram staan, er raakt
  niets kwijt.
- **ARM-randjes.** `openclaw update` kan breken op native modules zonder
  ARM64-build (opus, sqlite3) en sommige skills leveren geen ARM-binaries.
  Mitigatie: kanaal-plugins beperken tot Telegram, updates handmatig draaien
  op een moment dat je erbij kunt.
- **Prijsrisico hardware.** De Pi-prijs is al twee keer verhoogd en het
  geheugentekort duurt voort; wachten maakt het eerder duurder dan goedkoper.
  De oude laptop is de nul-euro-hedge.

## Notes

- Onderzoek 2026-08-07, met bronnen: officiële OpenClaw Pi-docs
  (`docs/install/raspberry-pi.md`: Pi 5 "fastest, recommended", 64-bit
  verplicht, Node 26); prijzen via Geizhals/Welectron/SOS/Opencircuit/bol;
  Max-route-tijdlijn via o.a. The Register (ToS-wijziging feb), VentureBeat
  (herstel mei), The New Stack (pauze creditsplitsing 15 juni);
  Ollama-benchmarks op Pi 5 via het openclaw-pi-oss-onderzoeksdoc
  (qwen2.5:3b ~5–6 t/s, "excellent" tool calling).
- Dit is de fysieke uitwerking van wat `hangar-in-de-browser` stap 1 wilde
  (vangen zonder sessie), via een ander kanaal: Telegram in plaats van een
  GitHub issue form. Die taak blijft staan voor stappen 2–3 (prioritering en
  routering).
- Besluit hierover: `decisions/0004-altijd-aan-kastje-thuis.md` (proposed).
  Het gaat op `accepted` zodra het eerste bericht als taak op het bord staat.
