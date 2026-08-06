# The Hangar

Ollie's project HQ. Everything in flight, everything parked, and every decision
that got it there — in plain markdown, in one place.

Markdown is the source of truth. `dashboard/index.html` is generated from it.

## Where it lives

| Thing            | Where                                                             |
| ---------------- | ----------------------------------------------------------------- |
| **The board**    | <https://olivervanderlugt.github.io/project-management/> — always on |
| The repo         | `github.com/olivervanderlugt/project-management`                   |
| Read it anywhere | GitHub web or app — every file renders in the browser              |
| Work on it       | claude.ai/code → open this repo → just start talking               |

The board is rebuilt and republished by GitHub Actions on every push, so it is
live in any browser with your laptop shut. Nothing runs on your machine.

One-time setup, if it 404s: repo Settings → Pages → Source: **GitHub Actions**.

Plain markdown means it opens in anything — GitHub, Obsidian, a text editor, your
phone — and it will still open in ten years.

## The five drawers

- **`planning/now.md`** — what you are on right now. One file. Always current.
- **`planning/weekly/`** — one file per week. Wins, what slipped, what's next.
- **`projects/`** — anything with a next action.
- **`ideas/`** — anything without one yet.
- **`decisions/`** — numbered records of what you chose and why, so you don't
  re-argue it in six months.
- **`reference/`** — notes and links worth keeping.

## Rebuilding the dashboard

```bash
python3 dashboard/build.py
```

No dependencies, no build tools, no install step. It reads the markdown and
writes `dashboard/index.html`. You rarely need to run this by hand — Actions does
it on every push.

## Repos

The Hangar indexes your repos, it does not contain them. Each project carries a
`repo:` field that the board turns into a link to the code.

```bash
gh repo list --json nameWithOwner,description,pushedAt --limit 200 \
  | python3 scripts/import_repos.py
```

Safe to re-run: repos already claimed by a `repo:` line are skipped. Imported
projects land as `parked` with a blank next action, so they show up flagged until
you decide what to do with them.

Easier: open the repo in Claude and say *"import my repos"* — it reads each one
before describing it, rather than guessing from the name.

## Working on it from inside itself

Open this repo at [claude.ai/code](https://claude.ai/code) and say what you want.
`CLAUDE.md` tells the session how the Hangar works — the structure, the
frontmatter contract, and the rule that the dashboard gets rebuilt after every
change. You don't re-explain any of it.

Things that already work as one-liners:

- "Add a project: <name>, next action is <x>"
- "What's on?"
- "Do the weekly review"
- "We decided to <x> because <y> — log it"
- "Publish the dashboard"
