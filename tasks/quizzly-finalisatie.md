---
title: Quizzly: finaliseren voor launch — alles behalve de handmatige stappen
project: quizzly
status: doing
added: 2026-08-07
effort: L
branch: claude/quizzly-finalization
---

## Done means

Alle onderstaande punten gebouwd, de trio (`npm run typecheck && npm test &&
npm run build`) groen, `docker compose up` boot en een gescript socket-spel
werkt end-to-end, branch gepusht met PR, CI groen. Plus een
`docs/LAUNCH-CHECKLIST.md` en een eindrapport met stap-voor-stap
instructies voor alles wat Ollie handmatig moet doen (hosting-account,
SMTP-provider, juridische gegevens, domein). Mergen doet Ollie.

1. Password reset + wachtwoord wijzigen (SMTP optioneel, degradeert netjes
   zoals AI; enumeration-safe; `destroyAllSessions` krijgt zijn echte caller)
2. Retentie-job (`DATA_RETENTION_DAYS`), age-gate op signup, GDPR
   Art. 15-export in settings, terms/privacy-links op signup
3. `robots.txt` bewust (publiek: `/`, `/discover`, `/privacy`, `/terms`),
   boot-warning als `REDIS_URL` gezet is maar ongebruikt
4. Realtime e2e-test over echte sockets (de test die de docs al claimen),
   integratietests voor de reset-flow; CI krijgt Postgres-service +
   Docker-build-stap
5. `fly.toml`; SECURITY.md/LEGAL.md-drift gefixt (nickname-filter en
   quiz-export bestaan inmiddels), DEPLOYMENT/.env.example/README bijgewerkt

## Notes

**Stand 2026-08-07 (gepauzeerd op Ollie's verzoek, "pause and save"):**

- Lokale clone: `~/Claude/quizzly`, branch `claude/quizzly-finalization`
  (gepusht). Eerste commit: env-oppervlak voor SMTP/EMAIL_FROM/
  DATA_RETENTION_DAYS + `emailConfigured`-vlag. Trio groen.
- Dev-Postgres: container `quizzly-dev-pg` op poort 5433 (user/pass/db
  `quizzly`), nu gestopt — `docker start quizzly-dev-pg` om te hervatten.
  Nog geen migraties gedraaid.
- Nog te bouwen, in volgorde: `PasswordResetToken`-model + migratie
  (via dev-pg op 5433), `src/lib/email.ts` (nodemailer, `server-only`),
  `src/lib/password-reset.ts` (db-gebonden, testbaar zonder `server-only`),
  acties + pagina's `/forgot-password` en `/reset-password`, wachtwoord
  wijzigen in settings, dan punten 2–5 hierboven.
- Ontwerpkeuzes al genomen: token = `generateSessionToken` +
  `hashSessionToken` (zelfde patroon als Session, alleen hash in db),
  30 min geldig, single-use, reset verwijdert alle sessies en stuurt naar
  `/login?reset=done`; e-mailverzending fire-and-forget zodat timing geen
  account-bestaan lekt; rate limit 3/uur per IP én per e-mail.
- Belangrijk gevonden feit: `main` en `claude/quizzly-assessment-hli9uv`
  wijzen beide naar `cff0040` — er stond niets meer te mergen; de
  "awaiting merge" in het projectbestand was al opgelost.
- Handmatig voor Ollie (komt in het eindrapport): hostingkeuze + account
  (Fly/Railway/VPS), SMTP-provider + credentials, `[BRACKETED]`-velden in
  privacy/terms + SECURITY.md-contact, eventueel domein en
  `ANTHROPIC_API_KEY`.
