#!/usr/bin/env python3
"""Turn a task in the queue into the brief its agent needs. No typing.

    python3 scripts/brief.py <task-slug>     the brief for one task
    python3 scripts/brief.py --list          what every open task would go to

This is the link between "Ollie wrote something down" and "an agent starts
work". Everything in the brief is derived: the repo from the project file, the
model and ceiling from routing.yml, the finish line from the task's own
`## Done means`, the boundaries from dispatch.DEFAULT_NOGO. Nothing here asks a
model to decide anything, so it costs nothing to run.

A task that cannot be dispatched says why, in the same breath: no project, no
repo, or a `## Done means` that was never written. That is the honest output —
not a brief with a guessed goal in it.
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_build = _load("dashboard_build", ROOT / "dashboard" / "build.py")
dispatch = _load("dispatch", ROOT / "scripts" / "dispatch.py")

UNWRITTEN = ("nog niet geschreven", "not writable yet", "niet schrijfbaar", "not yet")


def finish_lines(body):
    """The `## Done means` section as a list of lines, or [] if unwritten."""
    text = _build.prose(body, "Done means") or ""
    bullets = _build.bullets(body, "Done means")
    lines = bullets or [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return []
    joined = " ".join(lines).lower()
    if any(mark in joined for mark in UNWRITTEN):
        return []
    return lines


def load_docs():
    tasks = {meta["slug"]: (meta, body) for meta, body in _build.read_dir("tasks")}
    projects = {meta["slug"]: meta for meta, _ in _build.read_dir("projects")}
    return tasks, projects


def brief_for(slug, tasks, projects, routing):
    if slug not in tasks:
        return None, [f"no tasks/{slug}.md"]

    meta, body = tasks[slug]
    plan = dispatch.dispatch(meta, projects.get((meta.get("project") or "").strip()), routing)
    lines = finish_lines(body)
    missing = list(plan["missing"])

    if plan["kind"] == "sharpen":
        # Not a defect: an inbox task is supposed to have no finish line yet.
        return {
            "t": "brief",
            "id": slug,
            "repo": plan["repo"],
            "goal": f"Investigate {meta.get('title', slug)} and write a real `## Done means`. Do not build.",
            "dm": [
                "tasks/%s.md has a `## Done means` someone else could check" % slug,
                "status is `ready`, or it is still `inbox` with the open question written down",
            ],
            "files": [f"tasks/{slug}.md"],
            "nogo": plan["nogo"] + ["writing code for this task"],
            "m": plan["model"], "e": plan["effort"], "cap": plan["cap"],
            "branch": plan["branch"], "agent": plan["agent"] or "hangar-manager",
        }, missing

    if not lines:
        missing.append("`## Done means` is not written: this cannot be built")

    return {
        "t": "brief",
        "id": slug,
        "repo": plan["repo"],
        "goal": meta.get("title", slug),
        "dm": lines,
        "files": [],
        "nogo": plan["nogo"],
        "m": plan["model"], "e": plan["effort"], "cap": plan["cap"],
        "branch": plan["branch"], "agent": plan["agent"],
    }, missing


def list_queue(tasks, projects, routing):
    rows = []
    for slug in sorted(tasks):
        meta, _ = tasks[slug]
        plan = dispatch.dispatch(meta, projects.get((meta.get("project") or "").strip()), routing)
        if plan["kind"] is None:
            continue
        target = plan["agent"] or "—"
        note = f"  ({plan['missing'][0]})" if plan["missing"] else ""
        rows.append(
            f"{slug:<34} {plan['kind']:<9} {target:<22} {plan['model']:<7} {plan['cap'] or '':>7}{note}"
        )
    return rows


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    tasks, projects = load_docs()
    routing = dispatch.read_routing()

    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0

    if argv[0] == "--list":
        rows = list_queue(tasks, projects, routing)
        print(f"{'task':<34} {'kind':<9} {'agent':<22} {'model':<7} {'cap':>7}")
        print("\n".join(rows) if rows else "(queue empty)")
        return 0

    brief, missing = brief_for(argv[0], tasks, projects, routing)
    if brief is None:
        print("\n".join(f"missing: {m}" for m in missing), file=sys.stderr)
        return 1

    print(json.dumps(brief, ensure_ascii=False, indent=2))
    for m in missing:
        print(f"missing: {m}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
