#!/usr/bin/env python3
"""Build the Hangar dashboard from the markdown in this repo.

    python3 dashboard/build.py

Reads planning/, projects/, tasks/, ideas/ and decisions/, and writes a
self-contained dashboard/index.html — no dependencies, no network requests, no
build tools.

The page leads with the fleet: one card per project carrying its status, its
concrete `next`, how far its tasks have got, what an agent is working on right
now, and what is still to do. Under it sits everything that is waiting on Ollie,
and under that the slower material — focus, week, ideas, decisions, night log.

The output is written without <!doctype>, <html>, <head> or <body> wrappers, so
it can be opened directly in a browser *and* published as an Artifact, which
supplies that skeleton itself.
"""

import importlib.util
import os
import re
from datetime import date
from html import escape
from pathlib import Path

CODE_SPAN = re.compile(r"`([^`]+)`")
EMPHASIS = re.compile(r"(\*\*|__|\*|_)")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "index.html"
TODAY = date.today()

# The commit this page was built from, stamped into the output so the workflow
# can fetch the live URL and prove Pages is serving *this* build and not a
# cached older one. Empty on a local build — only CI knows its own sha, and the
# committed index.html should not churn on every run.
COMMIT = (os.environ.get("GITHUB_SHA") or "")[:7]

# The board is read-only, but capture has to work from a phone: this opens the
# issue form that scripts/capture_issue.py turns into a tasks/ file.
CAPTURE_URL = (
    "https://github.com/olivervanderlugt/project-management/issues/new?template=vangen.yml"
)
HANGAR_REPO = "https://github.com/olivervanderlugt/project-management"

# Where a repo deploys to when nobody has written a real URL into `preview:`.
# A guess, and always labelled as one.
PAGES_BASE = "https://olivervanderlugt.github.io/"

PROJECT_ORDER = {"active": 0, "paused": 1, "parked": 2, "shipped": 3}
TASK_ORDER = {"doing": 0, "blocked": 1, "ready": 2, "inbox": 3, "done": 4}
VERDICT_TONE = {
    "promising": "accent",
    "unexplored": "calm",
    "on hold": "warn",
    "dropped": "faded",
}


# --------------------------------------------------------------------- parsing


def parse_doc(path):
    """Split a markdown file into flat frontmatter and body."""
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.lstrip().startswith("---"):
        parts = text.lstrip().split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                key, _, value = line.partition(":")
                meta[key.strip().lower()] = value.strip()
            body = parts[2]
    meta["slug"] = path.stem
    return meta, body.strip()


def read_dir(name):
    """Every markdown file in a directory, templates excluded."""
    directory = ROOT / name
    if not directory.is_dir():
        return []
    docs = []
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_") or path.name.upper() == "README.MD":
            continue
        docs.append(parse_doc(path))
    return docs


def bullets(body, heading):
    """Bullet lines under a `## heading`, without their markers."""
    found, capturing = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            capturing = line[3:].strip().lower() == heading.lower()
            continue
        if capturing:
            stripped = line.strip()
            if stripped.startswith("- ") and stripped[2:].strip():
                found.append(stripped[2:].strip())
    return found


def prose(body, heading):
    """First paragraph under a `## heading`."""
    lines, capturing = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            if capturing:
                break
            capturing = line[3:].strip().lower() == heading.lower()
            continue
        if capturing:
            if line.strip():
                lines.append(line.strip())
            elif lines:
                break
    return " ".join(lines)


def first_prose(body, *headings):
    """The first of several headings that actually has a paragraph under it."""
    for heading in headings:
        text = prose(body, heading)
        if text:
            return text
    return ""


def parse_date(value):
    try:
        return date.fromisoformat((value or "").strip())
    except ValueError:
        return None


def due_cell(value):
    """Render a due date as (text, tone, title) relative to today."""
    due = parse_date(value)
    if due is None:
        return "", "none", "no date set"
    delta = (due - TODAY).days
    stamp = due.strftime("%d %b %Y")
    if delta < 0:
        return f"{abs(delta)}d over", "crit", f"overdue since {stamp}"
    if delta == 0:
        return "due today", "crit", stamp
    if delta <= 7:
        return f"due in {delta}d", "warn", stamp
    return f"due in {delta}d", "calm", stamp


def clip(text, limit=150):
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "…"


# ------------------------------------------------------------------- priority
#
# What the board should tell Ollie to do next, as one number per open task.
#
# score = status + weight + effort + age, and the point values are picked so
# that each term strictly outranks everything under it. The gap between two
# status values (300) is larger than the largest possible weight+effort+age
# (150+20+9 = 179); one step of project weight (30) is larger than the largest
# possible effort+age (29); one step of effort (10) is larger than the largest
# possible age (9). So the four factors read as a ranking in that order and the
# number is only a compact way of writing it down:
#
#   1. status   ready 600, inbox 300, blocked 0.
#      Ready first, because it is the only thing that can be picked up without
#      a decision. Blocked last, because it cannot move at all — this is what
#      keeps "do this now" from ever naming something nobody can start.
#   2. weight   the project's row in weights.yml (1..5) times 30.
#      Data, not code: the only knob Ollie turns. A task with no project:, or
#      one whose project is not in the table, gets the `neutral` row instead of
#      a crash and instead of a zero.
#   3. effort   S 20, M 10, L 0. Small first — finishing beats starting.
#   4. age      (TODAY - added) in days, capped at 90, in whole tens: 0..9.
#      Older weighs heavier, and only ever as a tiebreak, so nothing rots at
#      the bottom of the queue forever. No `added:` reads as 0 days old.
#
# The one thing that moves on its own is age, and it moves with the calendar,
# not with the clock: two builds on the same day produce the same score, the
# same order and the same file.

WEIGHTS = ROOT / "weights.yml"
NEUTRAL_KEY = "neutral"
NEUTRAL_FALLBACK = 3.0

OPEN_STATUSES = ("ready", "inbox", "blocked")
STATUS_POINTS = {"ready": 600, "inbox": 300, "blocked": 0}
EFFORT_POINTS = {"S": 20, "M": 10, "L": 0}
WEIGHT_POINTS = 30
AGE_CAP_DAYS = 90
AGE_PER_POINT = 10


def read_weights(path=None):
    """weights.yml as {slug: number}. Flat key: value, same shape as everywhere.

    A missing file, a junk line or an unparseable number is not an error worth
    failing a build over: the row is skipped and its project falls back to
    neutral, which is what an unlisted project gets anyway.
    """
    path = Path(path) if path else WEIGHTS
    table = {}
    if not path.is_file():
        return table
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        try:
            table[key.strip().lower()] = float(value.strip())
        except ValueError:
            continue
    return table


def project_weight(task, weights):
    """The weights.yml row for a task's project, or the neutral one."""
    slug = (task.get("project") or "").strip().lower()
    neutral = weights.get(NEUTRAL_KEY, NEUTRAL_FALLBACK)
    if not slug:
        return neutral
    return weights.get(slug, neutral)


def task_age_days(task, today=None):
    """How long a task has been open, in days. Never negative, never a crash."""
    added = parse_date(task.get("added", ""))
    if added is None:
        return 0
    return max(0, ((today or TODAY) - added).days)


def priority_score(task, weights, today=None):
    """The four factors as one number. See the comment block above."""
    status = (task.get("status") or "inbox").strip().lower()
    effort = (task.get("effort") or "").strip().upper()
    age_points = min(task_age_days(task, today), AGE_CAP_DAYS) // AGE_PER_POINT
    return (
        STATUS_POINTS.get(status, 0)
        + project_weight(task, weights) * WEIGHT_POINTS
        + EFFORT_POINTS.get(effort, 0)
        + age_points
    )


def open_tasks_by_score(tasks, weights, today=None):
    """Open tasks, highest score first, as (score, meta, body).

    Ties break on the older task and then on the slug, so the order is settled
    by the files alone — two builds of the same tree cannot disagree.
    """
    scored = [
        (priority_score(meta, weights, today), meta, body)
        for meta, body in tasks
        if (meta.get("status") or "inbox").strip().lower() in OPEN_STATUSES
    ]
    scored.sort(key=lambda row: (-row[0], row[1].get("added", "9999-99-99"), row[1]["slug"]))
    return scored


# ------------------------------------------------------------------- rendering


def unquote(value):
    """Drop a pair of quotes wrapping a whole frontmatter value."""
    value = (value or "").strip()
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1].strip()
    return value


def rich(value):
    """Escape text, then honour markdown code spans."""
    return CODE_SPAN.sub(r"<code>\1</code>", escape(unquote(value)))


def plain(value):
    """Escaped text with markdown emphasis markers stripped."""
    return escape(EMPHASIS.sub("", unquote(value)))


def pill(text, tone="calm", title=""):
    hint = f' title="{escape(title)}"' if title else ""
    return f'<span class="pill" data-tone="{tone}"{hint}>{escape(text)}</span>'


# ---------------------------------------------------------------- the dispatch


def load_dispatch():
    """scripts/dispatch.py and routing.yml, or (None, {}) if either is missing.

    Imported lazily and defensively: the board is the one thing that must build
    even when the rest is mid-surgery. No dispatch module, no agent names, no
    crash.
    """
    try:
        spec = importlib.util.spec_from_file_location("dispatch", ROOT / "scripts" / "dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, module.read_routing()
    except Exception:
        return None, {}


def plan_for(task, project, dispatch, routing):
    """(agent, model) for a task — derived, never invented.

    scripts/dispatch.py owns this answer: the agent is the project slug once
    that project has a repo, the model is the routing.yml row its effort falls
    under. A task already `doing` has nothing left to hand out, so dispatch
    returns no row for it; asking the same function what that task's effort
    routes to gives the row it is running under, without a second copy of the
    rule living here.
    """
    if dispatch is None:
        return None, ""
    meta = task
    if (task.get("status") or "").strip().lower() in ("doing", "blocked"):
        meta = dict(task, status="ready")
    plan = dispatch.dispatch(meta, project, routing)
    return plan["agent"], plan["model"]


def agent_tag(agent, model):
    if not agent:
        return '<span class="agent none" title="needs a project: with a repo:">no agent</span>'
    label = escape(agent) + (f' <span class="model">{escape(model)}</span>' if model else "")
    return f'<span class="agent">{label}</span>'


# ------------------------------------------------------------------- the fleet


def preview_for(meta):
    """(url, verified) for a project's live product, or (None, False).

    A `preview:` URL was written by a person who looked at it: that one is live.
    Everything else is the GitHub Pages URL the repo would deploy to — useful,
    and labelled as a guess, because the Hangar never presents a dead deploy as
    live. Never the repo's code page; that is a separate, smaller link.
    """
    url = (meta.get("preview") or "").strip()
    if url:
        return url, True
    repo = (meta.get("repo") or "").strip()
    if not repo:
        return None, False
    return f"{PAGES_BASE}{repo.split('/')[-1]}/", False


def start_prompt(meta, nxt):
    """A scoped opening prompt, so a session does not read a whole repo to begin."""
    repo = meta.get("repo", "")
    title = meta.get("title") or meta["slug"]
    lines = [f"Work on {title}" + (f" ({repo})." if repo else ".")]
    lines.append(
        "Read CLAUDE.md, README.md and any PROGRESS.md first. Do not read the "
        "whole repo — open files only when a step needs them."
    )
    if nxt:
        lines.append(f"Next action: {unquote(nxt)}")
    else:
        lines.append(
            "There is no next action set. Work out what it should be, tell me, "
            "and write it into the Hangar."
        )
    lines.append(
        "When you finish, update this project's file in "
        "olivervanderlugt/project-management and rebuild the dashboard."
    )
    return " ".join(lines)


def render_lane(title, rows, tone):
    if not rows:
        return ""
    return f"""
          <div class="lane" data-tone="{tone}">
            <span class="lane-label">{escape(title)}</span>
            <ul class="lane-list">{"".join(rows)}</ul>
          </div>"""


def render_card(meta, body, tasks, dispatch, routing):
    status = (meta.get("status") or "active").lower()
    title = meta.get("title") or meta["slug"]
    nxt = unquote(meta.get("next", ""))
    # What the thing actually is. The card leads with `next`, which only makes
    # sense once you remember what the project was — so this sits above it.
    description = unquote(meta.get("description", ""))
    desc_html = f'<p class="card-desc">{rich(description)}</p>' if description else ""

    done = [t for t in tasks if (t[0].get("status") or "").lower() == "done"]
    doing = [t for t in tasks if (t[0].get("status") or "").lower() == "doing"]
    blocked = [t for t in tasks if (t[0].get("status") or "").lower() == "blocked"]
    todo = [t for t in tasks if (t[0].get("status") or "").lower() in ("ready", "inbox")]

    # progress
    total = len(tasks)
    if total:
        pct = round(100 * len(done) / total)
        bar = (
            f'<div class="bar" role="img" aria-label="{len(done)} of {total} tasks done">'
            f'<span style="width:{pct}%"></span></div>'
            f'<span class="mono dim">{len(done)}/{total} done</span>'
        )
    else:
        bar = (
            '<div class="bar empty" role="img" aria-label="no tasks filed"><span></span></div>'
            '<span class="mono dim">no tasks filed</span>'
        )

    due_text, due_tone, due_hint = due_cell(meta.get("due", ""))
    chips = [pill(status, status)]
    if due_text:
        chips.append(pill(due_text, due_tone, due_hint))
    if doing:
        chips.append(pill(f"{len(doing)} running", "live"))

    # running agents
    running_rows = []
    for tmeta, _ in sorted(doing, key=lambda d: d[0].get("title", d[0]["slug"]).lower()):
        agent, model = plan_for(tmeta, meta, dispatch, routing)
        branch = tmeta.get("branch", "")
        running_rows.append(
            f'<li><span class="dot live" aria-hidden="true"></span>'
            f'<span class="lane-text">{rich(tmeta.get("title") or tmeta["slug"])}</span>'
            f'{agent_tag(agent, model)}'
            + (f'<span class="mono dim branch">{escape(branch)}</span>' if branch else "")
            + "</li>"
        )

    # to do, blocked first so it cannot hide under the ready ones
    todo_rows = []
    for tmeta, tbody in sorted(
        blocked + todo,
        key=lambda d: (
            TASK_ORDER.get((d[0].get("status") or "inbox").lower(), 9),
            d[0].get("title", d[0]["slug"]).lower(),
        ),
    ):
        tstatus = (tmeta.get("status") or "inbox").lower()
        agent, model = plan_for(tmeta, meta, dispatch, routing)
        extra = agent_tag(agent, model) if tstatus == "ready" else ""
        note = "needs a verdict" if tstatus == "inbox" else ""
        if tstatus == "blocked":
            note = clip(first_prose(tbody, "Blocked", "Why", "Waiting on", "Notes"), 70) or "blocked"
        todo_rows.append(
            f'<li><span class="dot" data-status="{escape(tstatus)}" aria-hidden="true"></span>'
            f'<span class="state mono">{escape(tstatus)}</span>'
            f'<span class="lane-text">{rich(tmeta.get("title") or tmeta["slug"])}</span>'
            f'{extra}'
            + (f'<span class="mono dim">{escape(note)}</span>' if note else "")
            + "</li>"
        )

    # actions
    url, verified = preview_for(meta)
    acts = []
    if url:
        if verified:
            acts.append(
                f'<a class="act primary live" href="{escape(url)}" target="_blank" rel="noopener" '
                f'title="{escape(url)}"><span class="dot live" aria-hidden="true"></span>'
                f"Preview &#8599;</a>"
            )
        else:
            acts.append(
                f'<a class="act primary guess" href="{escape(url)}" target="_blank" rel="noopener" '
                f'title="Derived GitHub Pages URL, never opened by anyone here: {escape(url)}">'
                f"Preview &#8599;<span class=\"guess-flag\">unverified</span></a>"
            )
    if meta.get("repo"):
        acts.append(
            f'<a class="act small" href="https://github.com/{escape(meta["repo"])}" '
            f'target="_blank" rel="noopener" title="{escape(meta["repo"])}">repo</a>'
        )
        # Talks to scripts/preview.py on localhost. Without the helper the
        # button explains itself instead of doing nothing.
        acts.append(
            f'<button class="act small run-local" type="button" data-slug="{escape(meta["slug"])}">'
            "run local</button>"
            f'<a class="act small local-link" data-slug="{escape(meta["slug"])}" target="_blank" '
            'rel="noopener" hidden>local &#8599;</a>'
        )
    acts.append(
        f'<button class="act small" type="button" '
        f'data-prompt="{escape(start_prompt(meta, nxt))}">copy start prompt</button>'
    )

    if nxt:
        next_html = f'<p class="next-text">{rich(nxt)}</p>'
    elif status == "active":
        next_html = '<p class="next-text missing">No next action &mdash; decide one</p>'
    else:
        next_html = f'<p class="next-text idle">Nothing queued while {escape(status)}</p>'

    foot_bits = []
    if meta.get("stack"):
        foot_bits.append(escape(meta["stack"]))
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    tag_html = "".join(f'<span class="tag">{escape(t)}</span>' for t in tags)

    return f"""
        <article class="card" data-status="{escape(status)}">
          <div class="card-head">
            <h3>{escape(title)}</h3>
            <span class="chips">{"".join(chips)}</span>
          </div>
          {desc_html}
          <div class="next"><span class="lane-label">next</span>{next_html}</div>
          <div class="progress">{bar}</div>
          {render_lane("running now", running_rows, "live")}
          {render_lane("to do", todo_rows, "calm")}
          <div class="card-foot">
            <div class="acts">{"".join(acts)}</div>
            <div class="card-meta mono dim">{" &middot; ".join(foot_bits)}</div>
            <div class="tags">{tag_html}</div>
          </div>
        </article>"""


def render_fleet(projects, by_project, dispatch, routing):
    if not projects:
        return "<p class='empty'>The rack is empty. Add a file to <code>projects/</code>.</p>"

    def sort_key(doc):
        meta = doc[0]
        tasks = by_project.get(meta["slug"], [])
        running = sum(1 for t in tasks if (t[0].get("status") or "").lower() == "doing")
        due = parse_date(meta.get("due", ""))
        return (
            PROJECT_ORDER.get((meta.get("status") or "").lower(), 9),
            -running,
            due or date.max,
            (meta.get("title") or meta["slug"]).lower(),
        )

    cards = [
        render_card(meta, body, by_project.get(meta["slug"], []), dispatch, routing)
        for meta, body in sorted(projects, key=sort_key)
    ]
    return f'<div class="fleet">{"".join(cards)}</div>'


# --------------------------------------------------------------- waiting on me


def render_waiting(projects, tasks, by_slug):
    """Everything that cannot move without Ollie. Never hidden, even when empty."""
    rows = []

    blocked = [t for t in tasks if (t[0].get("status") or "").lower() == "blocked"]
    for meta, body in sorted(blocked, key=lambda d: d[0].get("title", d[0]["slug"]).lower()):
        why = first_prose(body, "Blocked", "Why", "Waiting on", "Notes")
        rows.append(
            (
                "blocked",
                "crit",
                meta.get("title") or meta["slug"],
                clip(why) or "No reason written in the task file.",
                meta.get("project", ""),
            )
        )

    inbox = [t for t in tasks if (t[0].get("status") or "").lower() == "inbox"]
    for meta, body in sorted(inbox, key=lambda d: d[0].get("added", "")):
        why = clip(prose(body, "Done means"))
        rows.append(
            (
                "verdict",
                "warn",
                meta.get("title") or meta["slug"],
                why or "No finish line written yet — it stays inbox until there is one.",
                meta.get("project", ""),
            )
        )

    for meta, _ in sorted(projects, key=lambda d: (d[0].get("title") or d[0]["slug"]).lower()):
        if (meta.get("status") or "").lower() == "active" and not unquote(meta.get("next", "")):
            rows.append(
                (
                    "no next",
                    "crit",
                    meta.get("title") or meta["slug"],
                    "Active project with an empty next — decide the one concrete action.",
                    meta["slug"],
                )
            )

    if not rows:
        return (
            '<p class="all-clear">Nothing is waiting on you. No blocked tasks, no inbox '
            "task without a verdict, and every active project has a next action.</p>"
        )

    items = []
    for kind, tone, title, why, where in rows:
        context = by_slug.get(where, {}).get("title", where) if where else "no project"
        items.append(f"""
          <li data-tone="{tone}">
            <span class="kind mono">{escape(kind)}</span>
            <div>
              <p class="what">{rich(title)}</p>
              <p class="why">{rich(why)}</p>
            </div>
            <span class="where mono dim">{escape(context)}</span>
          </li>""")
    return f'<ul class="waiting-list">{"".join(items)}</ul>'


# ----------------------------------------------------------------- lower stack


def render_now(meta, body):
    focus = meta.get("focus", "Nothing set")
    updated = parse_date(meta.get("updated", ""))
    stamp = updated.strftime("%d %b %Y") if updated else "undated"
    items = [line.strip()[2:] for line in body.splitlines() if line.strip().startswith("- ")]
    listing = (
        "<ul class='now-list'>" + "".join(f"<li>{rich(item)}</li>" for item in items) + "</ul>"
        if items
        else "<p class='empty'>No supporting actions listed.</p>"
    )
    return f"""
    <section class="panel focus">
      <div class="panel-head">
        <h2>Current focus</h2>
        <span class="mono dim">planning/now.md &middot; {escape(stamp)}</span>
      </div>
      <p class="focus-line">{rich(focus)}</p>
      {listing}
    </section>"""


def render_week(weeks):
    if not weeks:
        return ""
    meta, body = weeks[-1]
    nxt = bullets(body, "Next week")
    items = nxt or bullets(body, "Wins")
    heading = "Next week" if nxt else "Wins"
    listing = "".join(f"<li>{rich(item)}</li>" for item in items)
    return f"""
    <section class="panel">
      <div class="panel-head">
        <h2>Last review</h2>
        <span class="mono dim">{escape(meta.get("week", meta["slug"]))}</span>
      </div>
      <p class="lede">{rich(meta.get("focus", ""))}</p>
      <span class="lane-label">{escape(heading)}</span>
      <ul class="plain-list">{listing}</ul>
    </section>"""


def render_ideas(ideas):
    if not ideas:
        return (
            "<p class='empty'>Nothing parked yet. Add a file to <code>ideas/</code> "
            "rather than keeping it in your head.</p>"
        )
    rows = []
    for meta, body in sorted(ideas, key=lambda d: d[0].get("title", d[0]["slug"]).lower()):
        verdict = (meta.get("verdict") or "unexplored").lower()
        tone = VERDICT_TONE.get(verdict, "calm")
        summary = prose(body, "The idea")
        rows.append(f"""
        <li class="idea" data-tone="{tone}">
          <div class="row-top">
            <h4>{escape(meta.get("title") or meta["slug"])}</h4>
            <span class="mono dim">{escape(meta.get("effort", "?"))}</span>
          </div>
          <span class="verdict mono">{escape(verdict)}</span>
          <p>{rich(summary) if summary else "&mdash;"}</p>
        </li>""")
    return f'<ul class="rows">{"".join(rows)}</ul>'


def render_decisions(decisions):
    if not decisions:
        return "<p class='empty'>Nothing logged yet.</p>"
    rows = []
    for meta, body in sorted(decisions, key=lambda d: d[0]["slug"], reverse=True):
        number = meta["slug"].split("-", 1)[0]
        when = parse_date(meta.get("date", ""))
        stamp = when.strftime("%d %b %Y") if when else "undated"
        status = (meta.get("status") or "accepted").lower()
        rows.append(f"""
        <li class="decision" data-status="{escape(status)}">
          <span class="adr mono">{escape(number)}</span>
          <div>
            <h4>{escape(meta.get("title") or meta["slug"])}</h4>
            <p>{rich(prose(body, "Decision"))}</p>
            <span class="mono dim">{escape(stamp)} &middot; {escape(status)}</span>
          </div>
        </li>""")
    return f'<ul class="rows">{"".join(rows)}</ul>'


def render_nightlog():
    """The last few entries of planning/night-log.md, newest first as written."""
    path = ROOT / "planning" / "night-log.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    tail = text.split("\n---\n", 1)[-1]
    blocks = [b.strip() for b in tail.split("\n\n") if b.strip() and not b.strip().startswith("#")]
    if not blocks:
        return "<p class='empty'>No runs logged yet.</p>"
    items = "".join(f"<li>{plain(clip(b, 260))}</li>" for b in blocks[:4])
    return f'<ul class="plain-list">{items}</ul>'


def render_priority(tasks, by_slug, weights):
    """Open tasks by score, led by the one line that says which to start."""
    scored = open_tasks_by_score(tasks, weights)
    if not scored:
        return (
            '<p class="all-clear">Nothing open. No ready task, no inbox task and nothing '
            "blocked &mdash; the queue is clear.</p>"
        )

    top_score, top_meta, _ = scored[0]
    top_status = (top_meta.get("status") or "inbox").strip().lower()
    top_project = (top_meta.get("project") or "").strip()
    where = by_slug.get(top_project, {}).get("title", top_project) or "no project"
    if top_status == "ready":
        why = f"highest score in the queue &middot; {escape(where)} &middot; ready to hand out"
    elif top_status == "inbox":
        # Nothing is ready, so the top of the queue is a decision, not a build.
        why = f"nothing is ready &middot; {escape(where)} &middot; needs a finish line first"
    else:
        why = f"everything open is blocked &middot; {escape(where)} &middot; unblock this one"

    rows = []
    for score, meta, _ in scored:
        status = (meta.get("status") or "inbox").strip().lower()
        slug = (meta.get("project") or "").strip()
        age = task_age_days(meta)
        rows.append(f"""
          <tr data-status="{escape(status)}">
            <td class="mono score">{escape(f"{score:g}")}</td>
            <td><span class="state mono">{escape(status)}</span></td>
            <td class="q-title">{rich(meta.get("title") or meta["slug"])}</td>
            <td class="mono dim">{escape(slug) if slug else "&mdash;"}</td>
            <td class="mono dim" title="weights.yml">{escape(f"{project_weight(meta, weights):g}")}</td>
            <td class="mono dim">{escape(meta.get("effort", "") or "&mdash;")}</td>
            <td class="mono dim">{escape(f"{age}d")}</td>
          </tr>""")

    return f"""
      <p class="do-now">
        <span class="do-now-label mono">Dit nu</span>
        <span class="do-now-task">{rich(top_meta.get("title") or top_meta["slug"])}</span>
        <span class="mono dim">{why} &middot; score {escape(f"{top_score:g}")}</span>
      </p>
      <div class="table-scroll">
        <table class="queue priority">
          <thead><tr><th>score</th><th>status</th><th>task</th><th>project</th>
            <th>weight</th><th>effort</th><th>age</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </div>"""


def render_queue(tasks, by_slug, dispatch, routing):
    """Every task, done ones included, as the one complete list on the page."""
    if not tasks:
        return "<p class='empty'>Queue is empty. Add a file to <code>tasks/</code>.</p>"

    def sort_key(doc):
        meta = doc[0]
        return (
            TASK_ORDER.get((meta.get("status") or "inbox").lower(), 9),
            meta.get("project", ""),
            (meta.get("title") or meta["slug"]).lower(),
        )

    rows = []
    for meta, _ in sorted(tasks, key=sort_key):
        status = (meta.get("status") or "inbox").lower()
        project_slug = (meta.get("project") or "").strip()
        agent, model = plan_for(meta, by_slug.get(project_slug), dispatch, routing)
        cell = agent_tag(agent, model) if status != "done" else '<span class="dim">&mdash;</span>'
        rows.append(f"""
          <tr data-status="{escape(status)}">
            <td><span class="state mono">{escape(status)}</span></td>
            <td class="q-title">{rich(meta.get("title") or meta["slug"])}</td>
            <td class="mono dim">{escape(project_slug or "&mdash;") if project_slug else "&mdash;"}</td>
            <td class="mono dim">{escape(meta.get("effort", ""))}</td>
            <td>{cell}</td>
          </tr>""")
    return f"""
      <table class="queue">
        <thead><tr><th>status</th><th>task</th><th>project</th><th>effort</th><th>goes to</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>"""


# ------------------------------------------------------------------- the vital


def render_vitals(projects, tasks, waiting_count):
    active = sum(1 for m, _ in projects if (m.get("status") or "").lower() == "active")
    running = sum(1 for m, _ in tasks if (m.get("status") or "").lower() == "doing")
    open_todo = sum(
        1 for m, _ in tasks if (m.get("status") or "").lower() in ("ready", "inbox", "blocked")
    )
    cells = [
        ("in flight", str(active), f"of {len(projects)} projects", "", "calm"),
        ("agents running", str(running), "tasks doing", "", "live" if running else "calm"),
        ("open to-dos", str(open_todo), "in the queue", "", "calm"),
        (
            "waiting on you",
            str(waiting_count),
            "needs a call" if waiting_count else "all clear",
            "#waiting",
            "warn" if waiting_count else "good",
        ),
    ]
    out = []
    for name, value, hint, href, tone in cells:
        inner = (
            f'<span class="vital-label">{escape(name)}</span>'
            f'<span class="vital-value">{escape(value)}</span>'
            f'<span class="mono dim">{escape(hint)}</span>'
        )
        if href:
            out.append(f'<a class="vital" data-tone="{tone}" href="{href}">{inner}</a>')
        else:
            out.append(f'<div class="vital" data-tone="{tone}">{inner}</div>')
    return "".join(out)


CSS = """
:root{
  --ground:#0A0E10; --panel:#111819; --panel-2:#151E20; --raise:#192325;
  --hair:#212D2F; --hair-soft:#1A2426;
  --ink:#DEE7E7; --ink-2:#A6B6B7; --dim:#718284;
  --accent:#4FBFB2; --accent-ink:#7FD6CB; --accent-soft:#12302E;
  --live:#5FD08A; --good:#5FD08A; --warn:#E0A94A; --crit:#E8796C;
  --radius:10px;
}
*{box-sizing:border-box;}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:15.5px; line-height:1.55; -webkit-font-smoothing:antialiased;
}
h1,h2,h3,h4{margin:0; font-weight:600; letter-spacing:-.01em;}
p{margin:0;}
a{color:var(--accent-ink); text-decoration:none;}
a:hover{text-decoration:underline;}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent); outline-offset:2px;}
code{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.86em;
  background:var(--accent-soft); color:var(--accent-ink); padding:1px 5px; border-radius:4px;}
.mono{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  font-variant-numeric:tabular-nums; font-size:.74rem; letter-spacing:.02em;}
.dim{color:var(--dim);}
.empty{color:var(--dim); font-size:.92rem;}

.hangar{max-width:1180px; margin:0 auto;
  padding:clamp(22px,4vw,44px) clamp(14px,3vw,28px) 64px;
  display:flex; flex-direction:column; gap:clamp(22px,3vw,34px);}

/* masthead */
.top{display:flex; flex-wrap:wrap; align-items:flex-end; justify-content:space-between; gap:18px;}
.kicker{font-size:.64rem; text-transform:uppercase; letter-spacing:.2em; color:var(--dim);}
.top h1{font-size:clamp(1.6rem,3.4vw,2.1rem); line-height:1.1; margin-top:4px;}
.top h1 em{font-style:normal; color:var(--accent);}
.top-acts{display:flex; gap:10px; align-items:center;}

.vitals{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px;}
.vital{background:var(--panel); border:1px solid var(--hair); border-radius:var(--radius);
  padding:12px 14px; display:flex; flex-direction:column; gap:1px; color:inherit;}
a.vital:hover{border-color:var(--accent); text-decoration:none;}
.vital-label{font-size:.66rem; text-transform:uppercase; letter-spacing:.14em; color:var(--dim);}
.vital-value{font-size:1.55rem; font-weight:600; line-height:1.25;
  font-variant-numeric:tabular-nums;}
.vital[data-tone="live"] .vital-value{color:var(--live);}
.vital[data-tone="warn"] .vital-value{color:var(--warn);}
.vital[data-tone="good"] .vital-value{color:var(--good);}

/* section frame */
.sec-head{display:flex; align-items:baseline; justify-content:space-between; gap:12px;
  margin-bottom:12px;}
.sec-head h2{font-size:.78rem; text-transform:uppercase; letter-spacing:.16em; color:var(--ink-2);}

/* fleet */
.fleet{display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:12px;}
.card{background:var(--panel); border:1px solid var(--hair); border-radius:var(--radius);
  padding:16px 18px 14px; display:flex; flex-direction:column; gap:12px; position:relative;
  overflow:hidden;}
.card::before{content:""; position:absolute; inset:0 auto 0 0; width:3px; background:var(--dim);}
.card[data-status="active"]::before{background:var(--accent);}
.card[data-status="paused"]::before{background:var(--warn);}
.card[data-status="shipped"]::before{background:var(--good);}
.card[data-status="parked"]::before{background:var(--hair);}
.card[data-status="parked"],.card[data-status="shipped"]{opacity:.82;}
.card-head{display:flex; align-items:baseline; justify-content:space-between; gap:10px;
  flex-wrap:wrap;}
.card-head h3{font-size:1.06rem;}
.card-desc{font-size:.88rem; color:var(--ink-2); text-wrap:pretty; margin-top:-4px;}
.chips{display:flex; gap:6px; flex-wrap:wrap;}
.pill{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.64rem; letter-spacing:.1em;
  text-transform:uppercase; border:1px solid var(--hair); border-radius:99px; padding:2px 8px;
  color:var(--dim); white-space:nowrap;}
.pill[data-tone="active"]{color:var(--accent-ink); border-color:var(--accent-soft);}
.pill[data-tone="live"]{color:var(--live); border-color:#1E3A2B;}
.pill[data-tone="warn"]{color:var(--warn); border-color:#3A2E14;}
.pill[data-tone="crit"]{color:var(--crit); border-color:#3B211E;}
.pill[data-tone="good"]{color:var(--good);}

.lane-label{font-size:.62rem; text-transform:uppercase; letter-spacing:.16em; color:var(--dim);
  display:block;}
.next-text{font-size:.98rem; color:var(--ink); margin-top:3px; text-wrap:pretty;}
.next-text.missing{color:var(--crit);}
.next-text.idle{color:var(--dim);}

.progress{display:flex; align-items:center; gap:10px;}
.bar{flex:1; height:4px; background:var(--hair-soft); border-radius:99px; overflow:hidden;}
.bar span{display:block; height:100%; background:var(--accent); border-radius:99px;}
.bar.empty{background:repeating-linear-gradient(90deg,var(--hair-soft) 0 6px,transparent 6px 12px);}

.lane{border-top:1px solid var(--hair-soft); padding-top:9px;}
.lane-list{list-style:none; margin:5px 0 0; padding:0; display:flex; flex-direction:column; gap:5px;}
.lane-list li{display:flex; align-items:baseline; gap:8px; flex-wrap:wrap; font-size:.9rem;
  color:var(--ink-2);}
.lane-text{flex:1; min-width:min(100%,180px); color:var(--ink);}
.dot{width:6px; height:6px; border-radius:99px; background:var(--dim); flex:none;
  transform:translateY(-1px);}
.dot.live{background:var(--live); box-shadow:0 0 0 3px rgba(95,208,138,.14);
  animation:pulse 2.6s ease-in-out infinite;}
.dot[data-status="ready"]{background:var(--accent);}
.dot[data-status="inbox"]{background:var(--warn);}
.dot[data-status="blocked"]{background:var(--crit);}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.35;}}
.state{text-transform:uppercase; letter-spacing:.1em; font-size:.6rem; color:var(--dim);
  min-width:48px;}
.agent{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.68rem; color:var(--accent-ink);
  background:var(--accent-soft); border-radius:4px; padding:1px 6px; white-space:nowrap;}
.agent .model{color:var(--ink-2); opacity:.9;}
.agent.none{color:var(--warn); background:transparent; border:1px dashed #3A2E14;}
.branch{opacity:.7;}

.card-foot{margin-top:auto; padding-top:11px; border-top:1px solid var(--hair-soft);
  display:flex; flex-direction:column; gap:8px;}
.acts{display:flex; flex-wrap:wrap; gap:8px; align-items:center;}
.act{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.72rem; letter-spacing:.02em;
  border:1px solid var(--hair); border-radius:6px; padding:5px 10px; color:var(--ink-2);
  background:transparent; cursor:pointer; display:inline-flex; align-items:center; gap:6px;
  transition:border-color .15s ease,color .15s ease,background .15s ease;}
.act:hover{border-color:var(--accent); color:var(--accent-ink); text-decoration:none;}
.act.small{font-size:.68rem; padding:4px 9px; color:var(--dim);}
.act.primary{color:var(--ink); border-color:#2B3A3B; background:var(--raise); font-weight:600;}
.act.primary.live{color:var(--live); border-color:#255138;}
.act.primary.live:hover{background:#16251C;}
.act.primary.guess{border-style:dashed; border-color:#3A3323; color:var(--warn);}
.act.primary.guess:hover{background:#231D10; color:var(--warn);}
.guess-flag{font-size:.6rem; letter-spacing:.08em; text-transform:uppercase; opacity:.75;}
.act.copied{border-color:var(--good); color:var(--good);}
.act[disabled]{opacity:.55; cursor:progress;}
.act.run-local.on{border-color:var(--good); color:var(--good);}
.act.run-local.failed{border-color:var(--crit); color:var(--crit);}
.card-meta{color:var(--dim);}
.tags{display:flex; flex-wrap:wrap; gap:5px;}
.tag{font-size:.62rem; letter-spacing:.08em; text-transform:uppercase; color:var(--dim);
  border:1px solid var(--hair-soft); border-radius:99px; padding:1px 7px;}

/* waiting */
#waiting .sec-head h2{color:var(--warn);}
.waiting-list{list-style:none; margin:0; padding:0; border:1px solid var(--hair);
  border-radius:var(--radius); overflow:hidden;}
.waiting-list li{display:grid; grid-template-columns:76px 1fr auto; gap:12px; align-items:baseline;
  padding:11px 14px; background:var(--panel); border-bottom:1px solid var(--hair-soft);}
.waiting-list li:last-child{border-bottom:0;}
.kind{text-transform:uppercase; letter-spacing:.1em; font-size:.6rem; color:var(--dim);}
.waiting-list li[data-tone="crit"] .kind{color:var(--crit);}
.waiting-list li[data-tone="warn"] .kind{color:var(--warn);}
.what{font-size:.95rem;}
.why{font-size:.85rem; color:var(--dim); margin-top:2px; text-wrap:pretty;}
.where{white-space:nowrap;}
.all-clear{border:1px solid var(--hair); border-left:3px solid var(--good);
  border-radius:var(--radius); background:var(--panel); padding:13px 15px; color:var(--ink-2);
  font-size:.93rem;}

/* lower stack */
.stack{display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:12px;
  align-items:start;}
.panel{background:var(--panel); border:1px solid var(--hair); border-radius:var(--radius);
  padding:16px 18px;}
.panel-head{display:flex; align-items:baseline; justify-content:space-between; gap:12px;
  padding-bottom:9px; border-bottom:1px solid var(--hair-soft); margin-bottom:11px;}
.panel-head h2{font-size:.72rem; text-transform:uppercase; letter-spacing:.16em; color:var(--ink-2);}
.focus{border-left:3px solid var(--accent);}
.focus-line{font-size:1.18rem; font-weight:600; letter-spacing:-.01em; text-wrap:balance;}
.now-list{list-style:none; margin:12px 0 0; padding:0; display:grid;
  grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:8px 22px;}
.now-list li{color:var(--ink-2); font-size:.9rem; padding-left:14px; position:relative;
  text-wrap:pretty;}
.now-list li::before{content:""; position:absolute; left:0; top:.62em; width:5px; height:5px;
  border-radius:99px; background:var(--accent); opacity:.7;}
.lede{font-size:1rem; color:var(--ink); margin-bottom:10px;}
.plain-list{margin:6px 0 0; padding-left:16px; color:var(--ink-2); font-size:.9rem;}
.plain-list li{margin-bottom:4px; text-wrap:pretty;}

.rows{list-style:none; margin:0; padding:0;}
.rows>li{padding:11px 0; border-bottom:1px solid var(--hair-soft);}
.rows>li:last-child{border-bottom:0;}
.rows h4{font-size:.95rem;}
.rows p{font-size:.87rem; color:var(--dim); margin-top:4px; text-wrap:pretty;}
.row-top{display:flex; justify-content:space-between; gap:10px; align-items:baseline;}
.verdict{text-transform:uppercase; letter-spacing:.1em; font-size:.6rem; color:var(--dim);}
.idea[data-tone="accent"] .verdict{color:var(--accent-ink);}
.idea[data-tone="warn"] .verdict{color:var(--warn);}
.idea[data-tone="faded"]{opacity:.5;}
.decision{display:grid; grid-template-columns:auto 1fr; gap:12px;}
.adr{color:var(--accent-ink); font-size:.8rem; padding-top:3px;}
.decision[data-status="superseded"]{opacity:.55;}
.decision[data-status="proposed"] .adr{color:var(--warn);}

/* queue */
details.queue-wrap{background:var(--panel); border:1px solid var(--hair);
  border-radius:var(--radius); padding:12px 16px;}
details.queue-wrap summary{cursor:pointer; font-size:.72rem; text-transform:uppercase;
  letter-spacing:.16em; color:var(--ink-2); list-style:none;}
details.queue-wrap summary::-webkit-details-marker{display:none;}
details.queue-wrap summary::before{content:"\\25B8"; color:var(--dim); margin-right:8px;}
details.queue-wrap[open] summary::before{content:"\\25BE";}
.queue{width:100%; border-collapse:collapse; margin-top:12px; font-size:.88rem;}
.queue th{text-align:left; font-size:.6rem; text-transform:uppercase; letter-spacing:.12em;
  color:var(--dim); font-weight:500; padding:0 10px 7px 0; border-bottom:1px solid var(--hair);}
.queue td{padding:8px 10px 8px 0; border-bottom:1px solid var(--hair-soft); vertical-align:baseline;}
.queue tr[data-status="done"]{opacity:.45;}
.queue tr[data-status="doing"] .state{color:var(--live);}
.queue tr[data-status="ready"] .state{color:var(--accent-ink);}
.queue tr[data-status="inbox"] .state{color:var(--warn);}
.queue tr[data-status="blocked"] .state{color:var(--crit);}
.q-title{color:var(--ink); text-wrap:pretty;}
.table-scroll{overflow-x:auto;}

/* priority */
.do-now{display:flex; flex-wrap:wrap; align-items:baseline; gap:10px;
  background:var(--panel); border:1px solid var(--hair); border-left:3px solid var(--accent);
  border-radius:var(--radius); padding:12px 16px;}
.do-now-label{text-transform:uppercase; letter-spacing:.16em; color:var(--accent);}
.do-now-task{font-size:1.05rem; font-weight:600; color:var(--ink); text-wrap:pretty;}
.queue.priority{margin-top:10px;}
.queue.priority .score{color:var(--ink-2); font-size:.8rem;}

footer{display:flex; flex-wrap:wrap; justify-content:space-between; gap:10px;
  border-top:1px solid var(--hair); padding-top:14px;}

@media (prefers-reduced-motion:reduce){*{transition:none !important; animation:none !important;}}
@media (max-width:560px){
  .waiting-list li{grid-template-columns:1fr; gap:4px;}
  .where{text-align:left;}
}
"""

# Talks to scripts/preview.py, which serves loopback-only on a fixed port.
# Browsers exempt loopback from mixed-content blocking, so this works from the
# Pages copy too; the Artifact copy runs under a CSP that blocks every host,
# and there the catch() below turns the buttons into a pointer at the helper.
PREVIEW_JS = """
(function () {
  var HELPER = "http://127.0.0.1:8642";
  var buttons = document.querySelectorAll(".act.run-local");
  if (!buttons.length) return;
  var links = {};
  document.querySelectorAll(".act.local-link").forEach(function (a) {
    links[a.getAttribute("data-slug")] = a;
  });
  var timer = null;

  function apply(data) {
    var projects = (data && data.projects) || {};
    var anyStarting = false;
    buttons.forEach(function (btn) {
      var slug = btn.getAttribute("data-slug");
      var p = projects[slug];
      var link = links[slug];
      btn.classList.remove("on", "failed");
      btn.removeAttribute("disabled");
      btn.title = "";
      if (!p || p.state === "stopped") {
        btn.textContent = "run local";
        if (link) link.hidden = true;
      } else if (p.state === "running") {
        btn.textContent = "stop local";
        btn.classList.add("on");
        if (link) { link.href = p.url; link.hidden = false; }
      } else if (p.state === "starting") {
        anyStarting = true;
        btn.textContent = "starting\\u2026";
        btn.setAttribute("disabled", "");
        if (link) link.hidden = true;
      } else if (p.state === "error") {
        btn.textContent = "run local (failed)";
        btn.classList.add("failed");
        btn.title = (p.error || "failed") + " \\u2014 log: " + (p.log || "?");
        if (link) link.hidden = true;
      }
    });
    if (anyStarting) poll(2000);
  }

  function offline() {
    buttons.forEach(function (btn) {
      btn.textContent = "run local";
      btn.classList.remove("on", "failed");
      btn.removeAttribute("disabled");
      btn.title = "start the helper first: python3 scripts/preview.py";
    });
    Object.keys(links).forEach(function (slug) { links[slug].hidden = true; });
  }

  function refresh() {
    return fetch(HELPER + "/status")
      .then(function (r) { return r.json(); })
      .then(apply);
  }

  function poll(delay) {
    clearTimeout(timer);
    timer = setTimeout(function () { refresh().catch(offline); }, delay);
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var slug = btn.getAttribute("data-slug");
      var action = btn.classList.contains("on") ? "stop" : "run";
      btn.setAttribute("disabled", "");
      btn.textContent = action === "run" ? "starting\\u2026" : "stopping\\u2026";
      fetch(HELPER + "/" + action + "/" + encodeURIComponent(slug), { method: "POST" })
        .then(function () { return refresh(); })
        .then(function () { poll(2000); })
        .catch(function () {
          offline();
          btn.textContent = "helper offline \\u2014 python3 scripts/preview.py";
          setTimeout(function () { btn.textContent = "run local"; }, 3200);
        });
    });
  });

  refresh().catch(offline);
})();
"""

SCRIPT = """
document.querySelectorAll(".act[data-prompt]").forEach(function (button) {
  button.addEventListener("click", function () {
    var text = button.getAttribute("data-prompt");
    var was = button.textContent;
    var done = function () {
      button.textContent = "copied";
      button.classList.add("copied");
      setTimeout(function () {
        button.textContent = was;
        button.classList.remove("copied");
      }, 2000);
    };
    function fallback() {
      var field = document.createElement("textarea");
      field.value = text;
      field.setAttribute("readonly", "");
      field.style.position = "fixed";
      field.style.opacity = "0";
      document.body.appendChild(field);
      field.select();
      try { document.execCommand("copy"); done(); } catch (err) { /* nothing to do */ }
      document.body.removeChild(field);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
  });
});
"""


def build():
    now_meta, now_body = parse_doc(ROOT / "planning" / "now.md")
    weeks = sorted(read_dir("planning/weekly"), key=lambda d: d[0]["slug"])
    projects = read_dir("projects")
    ideas = read_dir("ideas")
    decisions = read_dir("decisions")
    tasks = read_dir("tasks")

    dispatch, routing = load_dispatch()
    weights = read_weights()
    by_slug = {meta["slug"]: meta for meta, _ in projects}
    by_project = {}
    for doc in tasks:
        key = (doc[0].get("project") or "").strip()
        if key in by_slug:
            by_project.setdefault(key, []).append(doc)

    waiting_html = render_waiting(projects, tasks, by_slug)
    waiting_count = waiting_html.count("<li ")

    stamp = TODAY.strftime("%d %b %Y") + (f" &middot; {COMMIT}" if COMMIT else "")
    commit_meta = f'\n<meta name="hangar-commit" content="{COMMIT}">' if COMMIT else ""

    html = f"""<meta charset="utf-8">
<title>The Hangar</title>{commit_meta}
<style>{CSS}</style>
<main class="hangar">
  <header class="top">
    <div>
      <span class="kicker">Project HQ</span>
      <h1>The <em>Hangar</em></h1>
    </div>
    <div class="top-acts">
      <a class="act small" href="{CAPTURE_URL}" target="_blank" rel="noopener">+ capture</a>
      <a class="act small" href="{HANGAR_REPO}" target="_blank" rel="noopener">hangar repo</a>
      <span class="mono dim">built {stamp}</span>
    </div>
  </header>

  <div class="vitals">{render_vitals(projects, tasks, waiting_count)}</div>

  <section id="priority">
    <div class="sec-head">
      <h2>What to start &mdash; open tasks by score</h2>
      <span class="mono dim">status &middot; weights.yml &middot; effort &middot; age</span>
    </div>
    {render_priority(tasks, by_slug, weights)}
  </section>

  <section id="fleet">
    <div class="sec-head">
      <h2>Fleet &mdash; every project, where it stands</h2>
      <span class="mono dim">projects/</span>
    </div>
    {render_fleet(projects, by_project, dispatch, routing)}
  </section>

  <section id="waiting">
    <div class="sec-head">
      <h2>Waiting on you</h2>
      <span class="mono dim">blocked &middot; needs a verdict &middot; no next action</span>
    </div>
    {waiting_html}
  </section>

  {render_now(now_meta, now_body)}

  <div class="stack">
    {render_week(weeks)}
    <section class="panel">
      <div class="panel-head">
        <h2>Parked ideas</h2>
        <span class="mono dim">{len(ideas)}</span>
      </div>
      {render_ideas(ideas)}
    </section>
    <section class="panel">
      <div class="panel-head">
        <h2>Decision log</h2>
        <span class="mono dim">{len(decisions)}</span>
      </div>
      {render_decisions(decisions)}
    </section>
    <section class="panel">
      <div class="panel-head">
        <h2>Night log</h2>
        <span class="mono dim">planning/night-log.md</span>
      </div>
      {render_nightlog()}
    </section>
  </div>

  <details class="queue-wrap">
    <summary>Full queue &mdash; {len(tasks)} task{"" if len(tasks) == 1 else "s"}, done included</summary>
    <div class="table-scroll">{render_queue(tasks, by_slug, dispatch, routing)}</div>
  </details>

  <footer>
    <span class="mono dim">Generated from markdown &middot; python3 dashboard/build.py</span>
    <span class="mono dim">github.com/olivervanderlugt/project-management</span>
  </footer>
</main>
<script>{SCRIPT}</script>
<script>{PREVIEW_JS}</script>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}")
    print(
        f"  {len(projects)} projects  {len(tasks)} tasks  {waiting_count} waiting  "
        f"{len(ideas)} ideas  {len(decisions)} decisions  {len(weeks)} weekly reviews"
    )


if __name__ == "__main__":
    build()
