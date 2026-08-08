---
title: Put Learn online so it has a live preview
project: learning-website
status: done
added: 2026-08-06
effort: S
branch: main
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

Closed 2026-08-07: every finish line is met — the Pages workflow deploys on
push to `main`, https://olivervanderlugt.github.io/learning-website/ loads
(browser-verified per the repo's CLAUDE.md), and the Hangar project file
carries that `preview:` URL. Done by the 2026-08-07 merge session, recorded
here on the next manager pass.
