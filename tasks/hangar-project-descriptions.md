---
title: Give every project a one-line description on the board
project: hangar
status: done
added: 2026-08-08
effort: S
branch: claude/hangar-project-descriptions-2o5c0z
---

## Done means

Every file in `projects/` carries a `description:` line in its frontmatter — one
sentence saying what the thing actually is — and the dashboard shows it on the
project card, directly under the title. Ollie can look at the board and know what
Percentile is without opening anything.

## Notes

- The descriptions come from each project's existing `## What this is`, which was
  written by reading the repos. Nothing new is invented; a repo with nothing in it
  says so.
- Flat `key: value` frontmatter, one line, no wrapping — the parser in `build.py`
  stays simple.
- `scripts/import_repos.py` writes the field into new stubs as well, from the
  GitHub description, blank when GitHub has none.
