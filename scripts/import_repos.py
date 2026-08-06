#!/usr/bin/env python3
"""Create project stubs for GitHub repos that are not in the Hangar yet.

    gh repo list --json nameWithOwner,description,pushedAt --limit 200 \
        | python3 scripts/import_repos.py

    python3 scripts/import_repos.py --dry-run < repos.json

Reads a JSON array (or an object with a "repos" key) on stdin. Each entry needs
a `nameWithOwner` or `full_name`; `description` and `pushedAt`/`pushed_at` are
used when present.

Two rules it will not break:

  * A repo already claimed by a `repo:` line in projects/ is skipped, so
    re-running this is safe and renaming a project file does not duplicate it.
  * `next` is left blank and `status` is set to `parked`. Nothing here knows
    what you intend to do, so it does not pretend to — an imported project sits
    on the dashboard flagged red until you decide its next action.

Run `python3 dashboard/build.py` afterwards.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"


def existing_repos():
    """Every repo already claimed by a project file."""
    claimed = set()
    for path in PROJECTS.glob("*.md"):
        if path.name.startswith("_"):
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != "---":
            continue
        for line in lines[1:]:
            if line.strip() == "---":
                break  # end of this file's frontmatter
            if line.lower().startswith("repo:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    claimed.add(value.lower())
    return claimed


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


def title_from(name):
    words = re.split(r"[-_]+", name)
    return " ".join(words).capitalize()


def stub(full_name, description, pushed):
    repo_name = full_name.split("/")[-1]
    desc = description or (
        "Not recorded. Imported from GitHub, which knows the name and nothing else."
    )
    seen = f"\n\nLast push seen at import: {pushed}." if pushed else ""
    return f"""---
title: {title_from(repo_name)}
status: parked
next:
due:
started:
repo: {full_name}
stack:
tags:
---

## What this is

{desc}

## Where it stands

Imported from GitHub. Nothing else is known — fill this in or drop the file.{seen}

## Open questions

- What is the next concrete action? Until this is set, the project shows on the
  dashboard flagged red.
"""


def main():
    dry_run = "--dry-run" in sys.argv
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        sys.exit(f"could not read JSON on stdin: {exc}")

    repos = payload.get("repos", payload) if isinstance(payload, dict) else payload
    if not isinstance(repos, list):
        sys.exit("expected a JSON array of repos, or an object with a 'repos' key")

    claimed = existing_repos()
    created, skipped = [], []

    for entry in repos:
        if not isinstance(entry, dict):
            continue
        full_name = entry.get("nameWithOwner") or entry.get("full_name")
        if not full_name:
            continue
        if full_name.lower() in claimed:
            skipped.append(full_name)
            continue
        path = PROJECTS / f"{slugify(full_name.split('/')[-1])}.md"
        if path.exists():
            skipped.append(full_name)
            continue
        if not dry_run:
            path.write_text(
                stub(
                    full_name,
                    entry.get("description"),
                    entry.get("pushedAt") or entry.get("pushed_at"),
                ),
                encoding="utf-8",
            )
        created.append(f"{full_name} -> projects/{path.name}")
        claimed.add(full_name.lower())

    for line in created:
        print(("would create " if dry_run else "created ") + line)
    print(f"{len(created)} new, {len(skipped)} already in the Hangar")
    if created and not dry_run:
        print("now run: python3 dashboard/build.py")


if __name__ == "__main__":
    main()
