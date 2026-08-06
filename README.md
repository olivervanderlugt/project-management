# The Hangar

Ollie's project HQ. Everything in flight, everything parked, and every decision
that got it there — in plain markdown, in one place.

Markdown is the source of truth. `dashboard/index.html` is generated from it.

## Where it lives

| Thing            | Where                                                  |
| ---------------- | ------------------------------------------------------ |
| The repo         | `github.com/olivervanderlugt/project-management`        |
| Read it anywhere | GitHub web or app — every file renders in the browser   |
| Work on it       | claude.ai/code → open this repo → just start talking    |
| The dashboard    | `dashboard/index.html`, publishable as a shareable link |

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
writes `dashboard/index.html`. Open that file directly, or ask Claude to publish
it as a link you can keep on your phone.

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
