---
title: Quizzly: finaliseren voor launch — alles behalve de handmatige stappen
project: quizzly
status: done
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

**Afgerond 2026-08-07.** Alle vijf punten gebouwd en geverifieerd:
**PR #1** op `olivervanderlugt/quizzly`, vijf commits, eindigend met een
compose-fix die tijdens het testen boven kwam (Docker 29+ weigert de
ongequote `: ` in de secret-guards — `docker compose up` was stuk op
nieuwe machines). Versie 1.0.0, één additieve migratie
(`PasswordResetToken`).

Bewijs: 72 unit- + 8 integratietests groen (6× achtereen, geen flake),
trio groen, `docker compose up --build` boot met beide migraties, alle
publieke routes 200, boot-log meldt per optionele feature de status,
half-geconfigureerde SMTP weigert te booten. De socket-e2e bewijst:
host-auth (cookie + eigenaarschap), scheldnaam geweigerd, volledig spel
met scoring, geen correct-antwoord in speler-payload, resultaat in
Postgres.

Handmatig voor Ollie — volledig uitgeschreven in `docs/LAUNCH-CHECKLIST.md`
in de repo: hostingkeuze (Railway/Fly/VPS; `fly.toml` ligt klaar) +
account, SMTP-provider voor password reset (optioneel), `[BRACKETED]`-
velden in privacy/terms + SECURITY.md-contact, domein, backups + één
restore-test, en de 10-minuten-rooktest na deploy. Mergen van PR #1 doet
Ollie; daarna is deployen de enige stap tussen code en launch.

Lokale clone: `~/Claude/quizzly`. Dev-Postgres voor `npm run test:e2e`:
container `quizzly-dev-pg`, poort 5433 (draait; `docker stop` mag —
instructies staan in `vitest.e2e.config.ts`).
