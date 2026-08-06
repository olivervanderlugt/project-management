# The Hangar

Ollie's personal project HQ. Markdown is the source of truth. The dashboard is
generated from it and is never edited by hand.

Ollie is Oliver van der Lugt. Write to him in whatever language he used — Dutch
or English. Keep it direct; no filler.

## Layout

| Path                 | Holds                                                        |
| -------------------- | ------------------------------------------------------------ |
| `planning/now.md`    | The single current focus. One file, always current.           |
| `planning/weekly/`   | One file per ISO week: `YYYY-Www.md`. Wins, slips, next week. |
| `projects/`          | One file per project. Anything with a next action.            |
| `ideas/`             | One file per idea. Not started, not committed to.             |
| `decisions/`         | Numbered decision records: `NNNN-slug.md`. Append-only.       |
| `reference/`         | Notes and links worth keeping.                                |
| `dashboard/build.py` | Generates `dashboard/index.html` from everything above.       |

Each directory has a `_template.md`. Copy it rather than inventing a new shape.
Files starting with `_` are templates and are skipped by the build.

## Frontmatter contract

Frontmatter is deliberately flat `key: value` — no nested YAML, no lists. The
parser in `build.py` is simple on purpose, so keep it that way.

**`projects/*.md`**

```
---
title:   Human name of the project
status:  active | paused | shipped | parked
next:    One concrete next action. Never empty on an active project.
due:     YYYY-MM-DD, or blank if nothing is actually due
started: YYYY-MM-DD
tags:    comma, separated
---
```

**`ideas/*.md`**

```
---
title:   Human name
verdict: unexplored | promising | on hold | dropped
sparked: YYYY-MM-DD
effort:  S | M | L
---
```

**`decisions/NNNN-slug.md`**

```
---
title:  What was decided
status: proposed | accepted | superseded
date:   YYYY-MM-DD
---
```

Body sections: `## Context`, `## Decision`, `## Consequences`.

## Working rules

1. **Every active project has a `next`.** A concrete action, not a theme. If a
   project has no next action, that is the finding — say so.
2. **Rebuild after every content change.** Run `python3 dashboard/build.py`
   whenever anything under `planning/`, `projects/`, `ideas/`, `decisions/` or
   `reference/` changes. Commit the regenerated `dashboard/index.html` with it.
3. **Never invent status, dates or progress.** Leave a field blank and ask.
4. **Decisions are append-only.** To reverse one, add a new record and set the
   old one to `superseded`. Do not rewrite history.
5. **Moving an idea to a project** means: create `projects/<slug>.md`, set
   `started`, and set the idea's `verdict` to `promising` with a pointer — do
   not delete the idea file.
6. **Commit and push** at the end of a working session. Short imperative
   messages. Do not open a pull request unless Ollie asks for one.

## Common requests

- *"Add a project X"* → copy the template, fill what you can infer, ask only for
  what you genuinely cannot, rebuild, commit.
- *"What's on?"* → read `planning/now.md` plus active projects, answer in prose.
  Lead with anything overdue.
- *"Weekly review"* → create this week's file from `planning/weekly/_template.md`,
  fill it from what changed in the repo since the last one (`git log` is fair
  game), update `planning/now.md`, rebuild, commit.
- *"Publish the dashboard"* → build, then publish `dashboard/index.html` as an
  Artifact. Reuse the same file path so it redeploys to the same URL.
