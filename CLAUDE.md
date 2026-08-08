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
| `tasks/`             | The queue. One file per task, `inbox` → `ready` → `done`.      |
| `routing.yml`        | Model, effort and token ceiling per kind of work.              |
| `.claude/agents/`    | Generated. One agent per project, plus manager and checker.    |
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
repo:    owner/name on GitHub, or blank
preview: Live URL, or blank. Blank is honest — never point it at a dead deploy.
stack:   What it runs on, comma separated
tags:    comma, separated
---
```

`repo` is what makes the Hangar an index into the code: the dashboard turns it
into a link. It is also the key the repo importer matches on, so never write the
same `repo` value into two project files.

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
   GitHub Actions rebuilds and republishes to Pages on push regardless, but the
   committed copy should not be stale.
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
  Artifact. Reuse the same file path so it redeploys to the same URL. The Pages
  copy needs no action; it republishes on push.

## Repos

The Hangar indexes Ollie's GitHub repos; it does not contain them.

- *"Import my repos"* → list them (`list_repos`, or `gh repo list --json
  nameWithOwner,description,pushedAt`), pipe the JSON into
  `python3 scripts/import_repos.py`, then rebuild. The importer skips repos
  already claimed by a `repo:` line, so it is safe to re-run. It writes stubs
  with `status: parked` and a blank `next` on purpose — do not fill those in
  from the repo name.
- **Read the repo before describing it.** If a repo has commits, clone it and
  write `## What this is` from its README, `CLAUDE.md` or source — never from
  the name. If it is empty, say it is empty. Two of the four repos imported on
  2026-08-06 had zero commits.
- *"Create a repo for X"* → create it on GitHub (`create_repository`), then add
  the matching `projects/<slug>.md` with its `repo:` field set, and rebuild.
  Ask before making anything public.

## Capture, then build

When Ollie shares feedback, an idea or a complaint about any project, write it
down **immediately** as a file in `tasks/` with `status: inbox`. Do this before
discussing it, and do not ask permission — capture is free and losing it is the
only real failure.

Building is a separate decision. Do not start work because something was
mentioned; work when he says so, or when a task is `ready` and the overnight run
picks it up.

Promoting `inbox` → `ready` means writing a real `## Done means`. If you cannot
state the finish line concretely, the task stays `inbox`. That line is what
keeps the overnight run from producing work that gets thrown away.

## Overnight runs

A Routine fires nightly and works the queue in `tasks/`. The rules are not
suggestions — they exist because nobody is awake to catch a mistake:

1. **One task per night.** Highest `ready` task, oldest first. Not the whole
   queue — the limit is Ollie's usage budget, not the machine.
2. **`ready` only.** An `inbox` task gets investigated and sharpened into a
   proposal. Never built.
3. **Its own branch, then a PR.** Never commit to `main`, never to a branch
   Ollie is working on. Record the branch in the task's `branch:` field.
4. **Tests must pass.** If the project has tests, run them. Red means: do not
   push code, write down what broke, set the task to `blocked`.
5. **Stop at three open overnight PRs.** Review debt compounds. At the limit,
   skip building and spend the night sharpening `inbox` tasks instead.
6. **Never touch credentials, deploys or anything that costs money.**
7. **Leave a trail.** Every night writes to `planning/night-log.md`: what it
   did, what it refused to do, and why.
8. **No subagents? Play both roles yourself.** Routine-fired sessions may lack
   the Agent/Task tool (seen on 2026-08-08) — check at the start. If delegation
   works, use the builder and checker agents as designed. If not: build first,
   then, as a separate step, adversarially check your own diff against the
   task's `## Done means` as if someone else wrote it and you must prove it is
   *not* done. Never push a build that skipped the check, and note in the
   night-log that the check ran inline.

If a task turns out to be bigger or vaguer than it looked, stop and rewrite it
as two smaller `ready` tasks. Half-finished code is worse than none.

## Agents per project

`.claude/agents/` is generated by `scripts/gen_agents.py` from `projects/*.md`
and `routing.yml`. Never edit an agent file by hand — change the project file or
the generator and run it again:

```
python3 scripts/gen_agents.py
```

Every project with a `repo:` gets its own builder agent, named after its slug.
That agent owns exactly one repository and is told so in its own prompt, which
is the whole point: access is scoped by construction rather than by remembering
to say it. A project without a `repo:` gets no agent — there is nothing to build
in. Two shared agents come with them: `hangar-manager` chooses work and writes
briefs and never reads code, and `hangar-checker` sees only the diff and the
finish line and has to prove the work is *not* done.

The generator prunes agents whose project file is gone, and leaves anything you
wrote by hand alone — it only removes files carrying its own generated marker.

`routing.yml` is the one place model, effort and token ceiling are decided. The
manager may move down that table to spend less, never up. The design behind all
of this is `reference/agent-orkestratie.md`; the decision is `decisions/0003`,
still `proposed`.

## From a captured thought to a working agent

Nothing in this path is typed twice, and none of it costs a model call:

```
python3 scripts/brief.py --list        what every open task would go to
python3 scripts/brief.py <task-slug>   the brief for one task, as JSON
```

`scripts/dispatch.py` derives it: the repo comes from the project file, the
model, effort and ceiling from `routing.yml`, the finish line from the task's
own `## Done means`, the boundaries from `DEFAULT_NOGO`. An `inbox` task gets a
*sharpen* brief that forbids writing code; a `ready` task gets a build brief. A
task with no project, no repo, or no finish line says exactly that instead of
producing a brief with a guess in it — never fill that gap yourself.

The board shows the same thing per task: which agent, which model. If it says
"no agent", the task needs a `project:` or that project needs a `repo:`.

## The guard

`scripts/guard.py` runs as a `PreToolUse` hook on every Bash, Read, Edit and
Write. It exits 2 — blocking the call — for force pushes, pushes to `main`,
branch deletion, `reset --hard`, history rewriting, anything touching secrets,
deploys and paid CLIs, and repository deletion or visibility changes.

It is a `command` hook for the same reason autosave is: zero tokens, and it
binds every agent in the repo whether or not it read its own prompt. Prompt
rules are requests; this is a wall.

Keep it narrow. It deliberately does not fire on ordinary git, tests or builds —
a guard that blocks safe work gets switched off, and a switched-off guard
protects nothing. If you add a rule, add a test to `scripts/test_guard.py` on
both sides: what it blocks and what it must keep allowing.

## Autosave

`.claude/settings.json` runs `scripts/autosave.sh` on every Stop and SessionEnd:
rebuild, commit, push. Nothing is lost when Ollie closes the laptop mid-thought.

It is a `command` hook on purpose — a shell script, so it costs zero tokens. Do
not convert it to a `prompt` or `agent` hook; that would fire a model call every
time a turn ends.

It exits silently when nothing changed, refuses to run outside this repo, never
force-pushes, and treats a failed push as a retry rather than an error. Keep
those properties if you touch it.

Autosave is a safety net, not a substitute for a real commit. Still write a
proper message at the end of a session — `Autosave <timestamp>` says nothing
about what changed.

## Hosting

`.github/workflows/dashboard.yml` rebuilds the board and deploys it to GitHub
Pages on every push to `main` or `claude/**`. The live board is at
<https://olivervanderlugt.github.io/project-management/> and needs nothing
running locally. If it 404s, Pages has not been switched on: repo Settings →
Pages → Source: "GitHub Actions".

Deploy infrastructure — Docker, Vercel, Supabase, Stripe — belongs to the
individual project repos, never to the Hangar. The Hangar records `stack` and
where a thing deploys so you know where to look. See decision 0002.
