#!/usr/bin/env python3
"""Who does a task, on which model, with which ceiling.

One module so the answer is the same everywhere: the board renders it, the
brief carries it, and the manager reads it. Everything here is derived from
files that already exist — the task's status and effort, the project's repo,
and routing.yml. Nothing is asked, nothing is typed twice.

    kind_for(task)          which row of routing.yml applies
    dispatch(task, project) the whole answer as a dict
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUTING = ROOT / "routing.yml"

# The boundaries every brief carries, whatever the task says. They are repeated
# into the brief rather than assumed, because a builder reads its brief and not
# this file.
DEFAULT_NOGO = [
    "secrets, tokens, .env files",
    "deploys, publishing, anything that costs money",
    "any repository other than the one in this brief",
    "main, and any branch someone else is working on",
]


def read_routing(path=None):
    """routing.yml as {kind: {model, effort, cap, what}}. No YAML dependency."""
    path = path or ROUTING
    table, current = {}, None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" "):
            current = raw.split(":", 1)[0].strip()
            table[current] = {}
        elif current:
            key, _, value = raw.strip().partition(":")
            table[current][key.strip()] = value.strip()
    return table


def kind_for(task):
    """Which routing row a task falls under.

    An inbox task is never built — it is sharpened, which is a different job on
    a different model. That distinction is the whole reason this function
    exists rather than a lookup on effort alone.
    """
    status = (task.get("status") or "inbox").strip().lower()
    if status in ("done", "doing", "blocked"):
        return None
    if status != "ready":
        return "sharpen"
    return "build_s" if (task.get("effort") or "").strip().upper() == "S" else "build_ml"


def dispatch(task, project=None, routing=None):
    """Everything needed to hand this task to an agent, or the reason we cannot.

    Returns a dict with `agent`, `model`, `effort`, `cap`, `branch`, `repo`,
    `kind`, and `missing`: the list of things that have to be filled in by a
    person before this can go anywhere.
    """
    routing = routing or read_routing()
    kind = kind_for(task)
    row = routing.get(kind or "", {})
    slug = task.get("slug", "")
    project_slug = (task.get("project") or "").strip()

    missing = []
    if kind is None:
        missing.append(f"status {task.get('status', '?')}: nothing to hand out")
    if not project_slug:
        missing.append("no project: nobody owns this task yet")
    elif project is None:
        missing.append(f"no projects/{project_slug}.md")
    elif not project.get("repo"):
        missing.append(f"projects/{project_slug}.md has no repo:")

    return {
        "kind": kind,
        "agent": project_slug if project_slug and project and project.get("repo") else None,
        "repo": (project or {}).get("repo", ""),
        "model": row.get("model", ""),
        "effort": row.get("effort", ""),
        "cap": int(row["cap"]) if row.get("cap", "").isdigit() else None,
        "branch": f"night/{slug}" if slug else "",
        "nogo": list(DEFAULT_NOGO),
        "missing": missing,
    }
