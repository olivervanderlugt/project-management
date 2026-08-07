---
title: Redesign the Hangar dashboard around a live all-projects status view
project: hangar
status: done
added: 2026-08-07
effort: M
branch: claude/hangar-project-setup-kvhcad
---

## Done means

`dashboard/build.py` generates a page that leads with a status view of every
project: status, progress (open vs done tasks), the concrete `next`, its open
to-dos, tasks currently `doing` (with the agent/model working them), and a
"waiting for Ollie" strip (blocked tasks, inbox tasks needing a verdict,
active projects with an empty `next`). Every project with a `repo:` gets a
Preview button that opens its live product URL (`preview:` field) when one
exists, else the derived GitHub Pages URL `https://olivervanderlugt.github.io/
<repo-name>/` — never the repo's code page. Derived, unverified links are
visually distinguished from verified live ones. Page still builds with stdlib
python3 only, `dashboard/index.html` stays generated-never-hand-edited, and
the existing weekly/ideas/decisions content remains reachable below the fold.

## Notes

Ollie, 2026-08-07: "redesign the whole hangar index page. it doesnt feel
right. start with a view and status of all projects. like progress, to-do's
and running agents, tasks or things waiting for my attention" plus the preview
button spec above. No product is truly live yet, so today every Preview button
resolves to a Pages URL.

Closed 2026-08-07: built by the Atlasboard agent (commit 09e4df8), gate-checked
by the manager — rebuild idempotent, fleet/waiting sections verified in the
generated HTML and visually in Chrome, preview buttons confirmed live-vs-guess
(curl: only the Hangar and Learn Pages URLs answer 200), zero github.com code
pages behind a Preview button. One manager fix on top: `<meta charset="utf-8">`
so em-dashes survive raw file serving (commit 3517638).
