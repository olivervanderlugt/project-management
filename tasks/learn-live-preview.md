---
title: Put Learn online so it has a live preview
project: learning-website
status: blocked
added: 2026-08-06
effort: S
branch: night/learn-live-preview
---

## Done means

`olivervanderlugt/learning-website` builds and deploys to GitHub Pages on every
push to its default branch, the site loads and the skill tree is usable, and
`projects/learning-website.md` in the Hangar has a working `preview:` URL.

## Notes

Learn is Vite + React with no backend and no router — a static build, so Pages
serves it with nothing to pay for and no database to provision.

Two things that will bite:

- Vite needs `base: '/learning-website/'` in `vite.config.ts`, otherwise every
  asset 404s on a project Pages URL.
- Pages must be switched to "GitHub Actions" as source on that repo too, which
  Ollie has to do — the same `gh api -X POST repos/OWNER/REPO/pages
  -f build_type=workflow` call that worked for the Hangar.

Do not touch the curriculum or lesson content. This task is about deployment.

## Status 2026-08-06 (nachtrun)

Gebouwd op `night/learn-live-preview`, PR #1 open naar main: Pages-workflow plus
`base: '/learning-website/'`. Lokale build en headless-check groen (skill tree
rendert, 140 nodes, klikbaar). Checker: `ship:false` — niets staat live tot:

1. ~~Ollie PR #1 merget~~ — gemerged door Ollie, 2026-08-06 18:25.
2. Pages op de repo op bron "GitHub Actions" staat. Dit is het enige dat nog
   openstaat: Ollie's handmatige run (31126219285) bouwde groen maar faalde op
   `configure-pages` met "Get Pages site failed: Not Found". Fix: Settings →
   Pages → Source: "GitHub Actions" (of `gh api -X POST
   repos/olivervanderlugt/learning-website/pages -f build_type=workflow`),
   daarna de workflow re-runnen. De manager kon dit niet zelf: de API-call is
   in deze sessie geblokkeerd.

Daarna `preview:` in `projects/learning-website.md` invullen en deze taak `done`.
