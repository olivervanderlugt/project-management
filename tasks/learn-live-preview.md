---
title: Put Learn online so it has a live preview
project: learning-website
status: done
added: 2026-08-06
effort: S
branch:
---

## Done means

`olivervanderlugt/learning-website` builds and deploys to GitHub Pages on every
push to its default branch, the site loads and the skill tree is usable, and
`projects/learning-website.md` in the Hangar has a working `preview:` URL.

## Notes

Learn is Vite + React with no backend and no router — a static build, so Pages
serves it with nothing to pay for and no database to provision.

**Closed by the night run of 2026-08-08 — no code written, nothing to build.**
The finish line was already crossed on 2026-08-07 in another session; this task
was never checked off. Evidence, verified tonight:

- `.github/workflows/deploy.yml` exists on `main` of
  `olivervanderlugt/learning-website`.
- The latest push to `main` (54d9d78, 2026-08-07) triggered "Deploy to GitHub
  Pages" run #4, `completed` / `success`.
- `projects/learning-website.md` carries
  `preview: https://olivervanderlugt.github.io/learning-website/`.
- "Site loads and the skill tree is usable": could not be re-fetched tonight
  (the run sandbox blocks egress to github.io), but the project file records a
  browser verification on 2026-08-07 of exactly this deployed commit. If the
  site is down in the morning, reopen this task.

No branch and no PR in the project repo, because no commit was needed there.

Two things that will bite:

- Vite needs `base: '/learning-website/'` in `vite.config.ts`, otherwise every
  asset 404s on a project Pages URL.
- Pages must be switched to "GitHub Actions" as source on that repo too, which
  Ollie has to do — the same `gh api -X POST repos/OWNER/REPO/pages
  -f build_type=workflow` call that worked for the Hangar.

Do not touch the curriculum or lesson content. This task is about deployment.
