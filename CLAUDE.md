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
description: One line, what the thing actually is. The board shows it on the card.
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

`description` is the one-line answer to "what was this again?" — the board prints
it under the project's name, above `next`. Write it from the project's own
`## What this is`, never from the repo name. If nothing is recorded, say that
rather than inventing a plausible product.

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

## Overnight runs — not your rules unless you are one

A Routine fires nightly and works the queue in `tasks/` under eleven rules: one
task per night, `ready` only, its own branch and a PR that it merges itself once
a real adversarial check has passed, tests green or no push, stop at three
*stuck* PRs, no credentials or deploys, and a trail in `planning/night-log.md`.

**Those rules are in `reference/nightrun-rules.md`, not here, and they do not
apply to you unless you were fired by the nightly Routine.** The Routine loads
them itself — `reference/startprompt-nightrun.md` is the prompt that does it.
Every one of them follows from *nobody is awake to catch a mistake*. In a
session Ollie started, that premise is false, and so is the rule.

So: if Ollie asks for four tasks at once, build four. If he asks you to build
with PRs already open, build. Do not cap yourself, do not file your trail in the
night-log, and do not tell him a rule forbids it. What you leave behind instead
is `planning/now.md` plus honest `status:` and `branch:` fields on the tasks —
that is the trail for a session with a person in it. Merging your own PR is the
night run's rule, not yours: with Ollie there, ask.

Read the file when you need the detail: you are the night run, you are changing
how it works, or you are reasoning about something it left behind — a `doing`
task with no session on it, a night branch, a night-log entry. Decision `0005`
is why it moved; `0004` is the auto-merge rule inside it.

What *does* bind you is `## Working rules` above: never invent progress, rebuild
after every content change, capture before you build, decisions are append-only.
Plus the guard, which binds everything whether or not it read anything.

## Before you trust this working tree

`git fetch` and compare against the remote before you read a status, pick a task
or plan work. The nightly Routine pushes to the default branch every night, so a
clone that sat for a week is a week of finished work you cannot see. On
2026-08-14 a session read a stale tree, believed four tasks were still `ready`,
and dispatched agents to build three that were already built and merged. The
tree looked clean the whole time — `git status` cannot tell you this.

Other sessions run against this same repo concurrently. If a task is `doing`,
someone may be on it right now.

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

## Local preview

The dashboard's **run local** buttons talk to `scripts/preview.py`, a helper
Ollie starts on his own machine:

```
python3 scripts/preview.py
```

It serves loopback-only on `127.0.0.1:8642`. A click clones the project's repo
into `~/.hangar-previews/<slug>` (or fast-forwards an existing checkout),
starts the right dev server — `npm run dev` with the port passed the way vite
or next expects, `PORT` in the env otherwise, or a plain static server for an
`index.html` project — and the button turns into a `local ↗` link. Every
project gets a stable port; logs sit next to the checkouts. Without the helper
the buttons explain themselves and do nothing. It never deploys, never pushes,
and only runs repos named by a `repo:` line in `projects/`. Tests:
`python3 scripts/test_preview.py`.

## Hosting

`.github/workflows/dashboard.yml` rebuilds the board on every push to every
branch, deploys it to GitHub Pages, and then fetches the live URL to check that
Pages is really serving that commit — the build stamps its sha into the page for
exactly that purpose. The live board is at
<https://olivervanderlugt.github.io/project-management/> and needs nothing
running locally. If it 404s, Pages has not been switched on: repo Settings →
Pages → Source: "GitHub Actions".

**If the board is stale, look at the deploy job first.** GitHub Pages runs
through the `github-pages` environment, and that environment has its own list of
branches it will accept a deploy from. A branch that is not on the list fails in
about a second without ever picking up a runner — the build is green, the deploy
is red, and the site quietly keeps serving the last good commit. Settings →
Environments → `github-pages` → Deployment branches. This cost 2026-08-08: every
`claude/**` branch except the default one had been publishing nothing all day.

Deploy infrastructure — Docker, Vercel, Supabase, Stripe — belongs to the
individual project repos, never to the Hangar. The Hangar records `stack` and
where a thing deploys so you know where to look. See decision 0002.
