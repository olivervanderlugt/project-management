#!/usr/bin/env python3
"""Build the Hangar dashboard from the markdown in this repo.

    python3 dashboard/build.py

Reads planning/, projects/, ideas/ and decisions/, and writes a self-contained
dashboard/index.html — no dependencies, no network requests, no build tools.

The output is written without <!doctype>, <html>, <head> or <body> wrappers, so
it can be opened directly in a browser *and* published as an Artifact, which
supplies that skeleton itself.
"""

import re
from datetime import date
from html import escape
from pathlib import Path

CODE_SPAN = re.compile(r"`([^`]+)`")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "index.html"
TODAY = date.today()

PROJECT_ORDER = {"active": 0, "paused": 1, "parked": 2, "shipped": 3}
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


def parse_date(value):
    try:
        return date.fromisoformat((value or "").strip())
    except ValueError:
        return None


def due_cell(value):
    """Render a due date as (text, tone, title) relative to today."""
    due = parse_date(value)
    if due is None:
        return "—", "none", "no date set"
    delta = (due - TODAY).days
    stamp = due.strftime("%d %b %Y")
    if delta < 0:
        return f"+{abs(delta)}d", "crit", f"overdue since {stamp}"
    if delta == 0:
        return "today", "crit", stamp
    if delta <= 7:
        return f"{delta}d", "warn", stamp
    return f"{delta}d", "calm", stamp


# ------------------------------------------------------------------- rendering


def rich(value):
    """Escape text, then honour markdown code spans."""
    return CODE_SPAN.sub(r"<code>\1</code>", escape(value or ""))


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
        lines.append(f"Next action: {nxt}")
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


def render_preview(meta):
    """A live preview, if the project is actually deployed somewhere.

    The iframe only loads on the GitHub Pages copy — the Artifact build runs
    under a CSP that blocks every external host, so the link below it is the
    fallback that always works.
    """
    url = (meta.get("preview") or "").strip()
    title = meta.get("title") or meta["slug"]
    if not url:
        return (
            '<p class="no-preview mono">not deployed yet &mdash; no preview to show</p>'
        )
    return f"""
          <details class="preview">
            <summary>preview {escape(title)}</summary>
            <div class="preview-body">
              <iframe src="{escape(url)}" title="Live preview of {escape(title)}"
                      loading="lazy" referrerpolicy="no-referrer"
                      sandbox="allow-scripts allow-same-origin allow-forms"></iframe>
              <a class="act" href="{escape(url)}" target="_blank" rel="noopener">
                open in a tab &#8599;</a>
            </div>
          </details>"""


def render_actions(meta, nxt):
    repo = meta.get("repo", "")
    buttons = []
    if meta.get("preview"):
        buttons.append(
            f'<a class="act" href="{escape(meta["preview"])}" target="_blank" '
            f'rel="noopener">live &#8599;</a>'
        )
    if repo:
        buttons.append(
            f'<a class="act" href="https://github.com/{escape(repo)}" '
            f'target="_blank" rel="noopener">code &#8599;</a>'
        )
    buttons.append(
        '<a class="act" href="https://claude.ai/code" target="_blank" '
        'rel="noopener">open Claude Code &#8599;</a>'
    )
    buttons.append(
        f'<button class="act" type="button" data-prompt="{escape(start_prompt(meta, nxt))}">'
        "copy start prompt</button>"
    )
    return f'<div class="strip-acts">{"".join(buttons)}</div>'


def label(text):
    return f'<span class="eyebrow">{escape(text)}</span>'


def render_now(meta, body):
    focus = meta.get("focus", "Nothing set")
    updated = parse_date(meta.get("updated", ""))
    stamp = updated.strftime("%d %b %Y") if updated else "undated"
    items = [line.strip()[2:] for line in body.splitlines() if line.strip().startswith("- ")]
    listing = (
        "<ol class='now-list'>"
        + "".join(f"<li>{rich(item)}</li>" for item in items)
        + "</ol>"
        if items
        else "<p class='empty'>No supporting actions listed.</p>"
    )
    return f"""
    <section class="now">
      <div class="now-head">
        {label("Current focus")}
        <span class="mono dim">updated {escape(stamp)}</span>
      </div>
      <p class="now-focus">{rich(focus)}</p>
      {listing}
    </section>"""


def render_projects(projects):
    if not projects:
        return "<p class='empty'>The rack is empty. Add a file to <code>projects/</code>.</p>"

    def sort_key(doc):
        meta = doc[0]
        due = parse_date(meta.get("due", ""))
        return (
            PROJECT_ORDER.get(meta.get("status", "").lower(), 9),
            due or date.max,
            meta.get("title", meta["slug"]).lower(),
        )

    rows = []
    for meta, body in sorted(projects, key=sort_key):
        status = meta.get("status", "active").lower()
        title = meta.get("title") or meta["slug"]
        nxt = meta.get("next", "")
        text, tone, hint = due_cell(meta.get("due", ""))
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        tag_html = "".join(f"<span class='tag'>{escape(t)}</span>" for t in tags)
        bits = []
        if meta.get("repo"):
            slug = meta["repo"]
            bits.append(
                f'<a class="repo" href="https://github.com/{escape(slug)}">{escape(slug)}</a>'
            )
        if meta.get("stack"):
            bits.append(f'<span>{escape(meta["stack"])}</span>')
        meta_html = (
            f'<div class="strip-meta mono">{"<span class=sep>&middot;</span>".join(bits)}</div>'
            if bits
            else ""
        )
        actions_html = render_actions(meta, nxt)
        if nxt:
            next_html = f"<p class='strip-next'>{rich(nxt)}</p>"
        else:
            next_html = "<p class='strip-next missing'>No next action &mdash; decide one</p>"
        rows.append(f"""
        <article class="strip" data-status="{escape(status)}">
          <div class="strip-flag" aria-hidden="true"></div>
          <div class="strip-body">
            <div class="strip-top">
              <h3>{escape(title)}</h3>
              <span class="status mono">{escape(status)}</span>
            </div>
            {next_html}
            {meta_html}
            <div class="strip-tags">{tag_html}</div>
            {actions_html}
            {render_preview(meta)}
          </div>
          <div class="strip-due mono" data-tone="{tone}" title="{escape(hint)}">{escape(text)}</div>
        </article>""")
    return f'<div class="rack">{"".join(rows)}</div>'


def render_ideas(ideas):
    if not ideas:
        return "<p class='empty'>Nothing parked yet. Add a file to <code>ideas/</code>.</p>"
    rows = []
    for meta, body in sorted(ideas, key=lambda d: d[0].get("title", d[0]["slug"]).lower()):
        verdict = meta.get("verdict", "unexplored").lower()
        tone = VERDICT_TONE.get(verdict, "calm")
        summary = prose(body, "The idea")
        rows.append(f"""
        <li class="idea" data-tone="{tone}">
          <div class="idea-top">
            <h4>{escape(meta.get("title") or meta["slug"])}</h4>
            <span class="mono dim">{escape(meta.get("effort", "?"))}</span>
          </div>
          <span class="verdict mono">{escape(verdict)}</span>
          <p>{rich(summary) if summary else "&mdash;"}</p>
        </li>""")
    return f'<ul class="ideas">{"".join(rows)}</ul>'


def render_decisions(decisions):
    if not decisions:
        return "<p class='empty'>Nothing logged yet.</p>"
    ordered = sorted(decisions, key=lambda d: d[0]["slug"], reverse=True)
    rows = []
    for meta, body in ordered:
        number = meta["slug"].split("-", 1)[0]
        when = parse_date(meta.get("date", ""))
        stamp = when.strftime("%d %b %Y") if when else "undated"
        status = meta.get("status", "accepted").lower()
        rows.append(f"""
        <li class="decision" data-status="{escape(status)}">
          <span class="adr mono">{escape(number)}</span>
          <div>
            <h4>{escape(meta.get("title") or meta["slug"])}</h4>
            <p>{rich(prose(body, "Decision"))}</p>
            <span class="mono dim">{escape(stamp)} &middot; {escape(status)}</span>
          </div>
        </li>""")
    return f'<ul class="decisions">{"".join(rows)}</ul>'


def render_week(weeks):
    if not weeks:
        return ""
    meta, body = weeks[-1]
    items = bullets(body, "Next week") or bullets(body, "Wins")
    heading = "Next week" if bullets(body, "Next week") else "Wins"
    listing = "".join(f"<li>{rich(item)}</li>" for item in items)
    return f"""
    <section class="panel week">
      <div class="panel-head">
        {label("Last review")}
        <span class="mono dim">{escape(meta.get("week", meta["slug"]))}</span>
      </div>
      <p class="week-focus">{rich(meta.get("focus", ""))}</p>
      <span class="eyebrow inline">{escape(heading)}</span>
      <ul class="week-list">{listing}</ul>
    </section>"""


def render_counters(projects, ideas, decisions):
    active = sum(1 for m, _ in projects if m.get("status", "").lower() == "active")
    upcoming = [
        parse_date(m.get("due", ""))
        for m, _ in projects
        if parse_date(m.get("due", "")) is not None
    ]
    if upcoming:
        soonest = min(upcoming)
        delta = (soonest - TODAY).days
        next_due = f"+{abs(delta)}d" if delta < 0 else ("today" if delta == 0 else f"{delta}d")
        due_hint = soonest.strftime("%d %b")
    else:
        next_due, due_hint = "—", "nothing scheduled"
    cells = [
        ("In flight", str(active), f"{len(projects)} total"),
        ("Parked", str(len(ideas)), "ideas"),
        ("Logged", str(len(decisions)), "decisions"),
        ("Next due", next_due, due_hint),
    ]
    return "".join(
        f"""<div class="counter">
              <span class="eyebrow">{escape(name)}</span>
              <span class="counter-value mono">{escape(value)}</span>
              <span class="mono dim">{escape(hint)}</span>
            </div>"""
        for name, value, hint in cells
    )


CSS = """
:root{
  --ground:#EEF2F1; --surface:#FFFFFF; --rack:#E5EBEA;
  --ink:#111819; --muted:#5C6A6D; --hair:#D3DBDA;
  --accent:#0E6B65; --accent-ink:#0E6B65; --accent-soft:#DBEAE7;
  --warn:#8A5A0B; --crit:#9E2B23; --good:#2C6640;
  --shadow:rgba(17,24,25,.06);
}
@media (prefers-color-scheme: dark){
  :root{
    --ground:#0C1214; --surface:#141D1F; --rack:#101819;
    --ink:#E3ECEC; --muted:#8A9A9D; --hair:#233032;
    --accent:#46B9AE; --accent-ink:#7FD3CA; --accent-soft:#16302E;
    --warn:#D9A441; --crit:#E4776C; --good:#6FBE86;
    --shadow:rgba(0,0,0,.4);
  }
}
:root[data-theme="light"]{
  --ground:#EEF2F1; --surface:#FFFFFF; --rack:#E5EBEA;
  --ink:#111819; --muted:#5C6A6D; --hair:#D3DBDA;
  --accent:#0E6B65; --accent-ink:#0E6B65; --accent-soft:#DBEAE7;
  --warn:#8A5A0B; --crit:#9E2B23; --good:#2C6640;
  --shadow:rgba(17,24,25,.06);
}
:root[data-theme="dark"]{
  --ground:#0C1214; --surface:#141D1F; --rack:#101819;
  --ink:#E3ECEC; --muted:#8A9A9D; --hair:#233032;
  --accent:#46B9AE; --accent-ink:#7FD3CA; --accent-soft:#16302E;
  --warn:#D9A441; --crit:#E4776C; --good:#6FBE86;
  --shadow:rgba(0,0,0,.4);
}

*{box-sizing:border-box;}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased;
}
.mono{
  font-family:ui-monospace,SFMono-Regular,"SF Mono","JetBrains Mono",Menlo,Consolas,monospace;
  font-variant-numeric:tabular-nums; font-size:.78rem; letter-spacing:.02em;
}
.dim{color:var(--muted);}
.board{max-width:1080px; margin:0 auto; padding:clamp(24px,5vw,56px) clamp(16px,4vw,32px) 72px;
  display:flex; flex-direction:column; gap:clamp(24px,4vw,40px);}

.eyebrow{
  font-size:.68rem; font-weight:600; text-transform:uppercase; letter-spacing:.16em;
  color:var(--muted);
}
.eyebrow.inline{display:block; margin-top:14px;}

/* masthead */
.masthead{display:flex; flex-wrap:wrap; align-items:flex-end; justify-content:space-between;
  gap:16px; padding-bottom:18px; border-bottom:2px solid var(--ink);}
.masthead h1{
  margin:2px 0 0; font-size:clamp(2rem,5vw,2.9rem); line-height:1;
  letter-spacing:-.03em; font-weight:700; text-wrap:balance;
}
.masthead h1 em{font-style:normal; color:var(--accent-ink);}
.stamp{text-align:right;}

.counters{display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:1px;
  background:var(--hair); border:1px solid var(--hair);}
.counter{background:var(--surface); padding:14px 16px; display:flex; flex-direction:column; gap:2px;}
.counter-value{font-size:1.7rem; line-height:1.1; font-weight:600; letter-spacing:-.02em;}

/* now */
.now{background:var(--surface); border:1px solid var(--hair); border-top:3px solid var(--accent);
  padding:clamp(18px,3vw,26px);}
.now-head{display:flex; justify-content:space-between; align-items:baseline; gap:12px;}
.now-focus{margin:10px 0 18px; font-size:clamp(1.35rem,3.2vw,1.9rem); line-height:1.2;
  letter-spacing:-.02em; font-weight:600; text-wrap:balance;}
.now-list{margin:0; padding:0; list-style:none; counter-reset:n;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:10px 24px;}
.now-list li{counter-increment:n; position:relative; padding-left:26px; color:var(--muted);
  border-top:1px solid var(--hair); padding-top:8px;}
.now-list li::before{
  content:counter(n,decimal-leading-zero); position:absolute; left:0; top:8px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.7rem; color:var(--accent-ink); letter-spacing:.02em;
}

/* section headings */
.section-head{display:flex; align-items:baseline; justify-content:space-between; gap:12px;
  border-bottom:1px solid var(--hair); padding-bottom:8px; margin-bottom:14px;}
.section-head h2{margin:0; font-size:1rem; font-weight:600; letter-spacing:.01em;}

/* project rack */
.rack{background:var(--rack); border:1px solid var(--hair); display:flex; flex-direction:column; gap:1px;}
.strip{display:grid; grid-template-columns:6px 1fr auto; align-items:stretch;
  background:var(--surface); transition:background .15s ease;}
.strip:hover{background:var(--accent-soft);}
.strip-flag{background:var(--muted);}
.strip[data-status="active"] .strip-flag{background:var(--accent);}
.strip[data-status="paused"] .strip-flag{background:var(--warn);}
.strip[data-status="shipped"] .strip-flag{background:var(--good);}
.strip[data-status="parked"] .strip-flag{background:var(--hair);}
.strip-body{padding:14px 18px; min-width:0;}
.strip-top{display:flex; align-items:baseline; gap:12px; flex-wrap:wrap;}
.strip-top h3{margin:0; font-size:1.05rem; font-weight:600; letter-spacing:-.01em;}
.status{text-transform:uppercase; letter-spacing:.12em; color:var(--muted); font-size:.66rem;}
.strip-next{margin:4px 0 0; color:var(--muted); font-size:.94rem;}
.strip-next.missing{color:var(--crit);}
.strip-meta{margin-top:6px; color:var(--muted); display:flex; flex-wrap:wrap; gap:6px;
  align-items:baseline;}
.strip-meta .sep{opacity:.5;}
.strip-meta .repo{color:var(--accent-ink); text-decoration:none; border-bottom:1px solid transparent;}
.strip-meta .repo:hover{border-bottom-color:currentColor;}
.strip-tags{display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;}
.strip-acts{display:flex; flex-wrap:wrap; gap:8px; margin-top:12px;}
.act{
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:.72rem;
  letter-spacing:.02em; color:var(--accent-ink); background:transparent;
  border:1px solid var(--hair); padding:4px 10px; cursor:pointer; text-decoration:none;
  transition:border-color .15s ease, background .15s ease;
}
.act:hover{border-color:var(--accent); background:var(--accent-soft);}
.act:focus-visible{outline:2px solid var(--accent); outline-offset:2px;}
.act.copied{border-color:var(--good); color:var(--good);}

.no-preview{margin:10px 0 0; color:var(--muted); opacity:.75;}
.preview{margin-top:10px;}
.preview summary{
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:.72rem;
  letter-spacing:.02em; color:var(--accent-ink); cursor:pointer; display:inline-block;
  border:1px solid var(--hair); padding:4px 10px; list-style:none;
}
.preview summary::-webkit-details-marker{display:none;}
.preview summary::before{content:"\\25B8 "; opacity:.7;}
.preview[open] summary::before{content:"\\25BE ";}
.preview summary:hover{border-color:var(--accent); background:var(--accent-soft);}
.preview summary:focus-visible{outline:2px solid var(--accent); outline-offset:2px;}
.preview-body{margin-top:10px; display:flex; flex-direction:column; gap:8px;
  align-items:flex-start;}
.preview-body iframe{
  width:100%; height:min(58vh,420px); border:1px solid var(--hair);
  background:var(--ground); border-radius:0;
}
.tag{font-size:.68rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted);
  border:1px solid var(--hair); padding:1px 7px;}
.strip-due{display:flex; align-items:center; padding:0 18px; font-size:1rem; font-weight:600;
  border-left:1px solid var(--hair); min-width:88px; justify-content:flex-end;}
.strip-due[data-tone="crit"]{color:var(--crit);}
.strip-due[data-tone="warn"]{color:var(--warn);}
.strip-due[data-tone="calm"]{color:var(--ink);}
.strip-due[data-tone="none"]{color:var(--muted); font-weight:400;}

/* lower deck */
.deck{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
  gap:clamp(20px,3vw,32px); align-items:start;}
.panel{background:var(--surface); border:1px solid var(--hair); padding:clamp(16px,2.5vw,22px);}
.panel-head{display:flex; justify-content:space-between; align-items:baseline; gap:12px;
  border-bottom:1px solid var(--hair); padding-bottom:8px;}

.ideas,.decisions{list-style:none; margin:0; padding:0; display:flex; flex-direction:column;}
.idea{padding:14px 0; border-bottom:1px solid var(--hair);}
.idea:last-child{border-bottom:0;}
.idea-top{display:flex; justify-content:space-between; align-items:baseline; gap:10px;}
.idea h4{margin:0; font-size:.98rem; font-weight:600;}
.idea p{margin:6px 0 0; color:var(--muted); font-size:.9rem;}
.verdict{text-transform:uppercase; letter-spacing:.1em; font-size:.64rem; color:var(--muted);}
.idea[data-tone="accent"] .verdict{color:var(--accent-ink);}
.idea[data-tone="warn"] .verdict{color:var(--warn);}
.idea[data-tone="faded"]{opacity:.5;}

.decision{display:grid; grid-template-columns:auto 1fr; gap:14px; padding:14px 0;
  border-bottom:1px solid var(--hair);}
.decision:last-child{border-bottom:0;}
.adr{color:var(--accent-ink); font-size:.85rem; padding-top:2px;}
.decision h4{margin:0; font-size:.98rem; font-weight:600;}
.decision p{margin:4px 0 6px; color:var(--muted); font-size:.9rem;}
.decision[data-status="superseded"]{opacity:.55;}

.week-focus{margin:12px 0 0; font-size:1.05rem; font-weight:600; letter-spacing:-.01em;}
.week-list{margin:6px 0 0; padding-left:18px; color:var(--muted); font-size:.92rem;}
.week-list li{margin-bottom:4px;}

.empty{color:var(--muted); font-size:.92rem; margin:12px 0 0;}
code{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.85em;
  background:var(--accent-soft); padding:1px 5px;}
footer{border-top:1px solid var(--hair); padding-top:14px; display:flex;
  justify-content:space-between; flex-wrap:wrap; gap:8px;}
a{color:var(--accent-ink);}
a:focus-visible{outline:2px solid var(--accent); outline-offset:2px;}
@media (prefers-reduced-motion:reduce){*{transition:none !important;}}
@media (max-width:520px){
  .strip{grid-template-columns:6px 1fr;}
  .strip-due{grid-column:2; border-left:0; border-top:1px solid var(--hair);
    justify-content:flex-start; padding:8px 18px 14px;}
}
"""


def build():
    now_meta, now_body = parse_doc(ROOT / "planning" / "now.md")
    weeks = sorted(read_dir("planning/weekly"), key=lambda d: d[0]["slug"])
    projects = read_dir("projects")
    ideas = read_dir("ideas")
    decisions = read_dir("decisions")

    html = f"""<title>The Hangar</title>
<style>{CSS}</style>
<main class="board">
  <header class="masthead">
    <div>
      {label("Project HQ")}
      <h1>The <em>Hangar</em></h1>
    </div>
    <div class="stamp">
      <span class="eyebrow">Board built</span><br>
      <span class="mono dim">{TODAY.strftime("%d %b %Y")}</span>
    </div>
  </header>

  <div class="counters">{render_counters(projects, ideas, decisions)}</div>

  {render_now(now_meta, now_body)}

  <section>
    <div class="section-head">
      <h2>On the apron</h2>
      <span class="mono dim">{len(projects)} project{"" if len(projects) == 1 else "s"}</span>
    </div>
    {render_projects(projects)}
  </section>

  <div class="deck">
    <section class="panel">
      <div class="panel-head">
        <h2 class="eyebrow">Parked ideas</h2>
        <span class="mono dim">{len(ideas)}</span>
      </div>
      {render_ideas(ideas)}
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2 class="eyebrow">Decision log</h2>
        <span class="mono dim">{len(decisions)}</span>
      </div>
      {render_decisions(decisions)}
    </section>
  </div>

  {render_week(weeks)}

  <footer>
    <span class="mono dim">Generated from markdown &middot; python3 dashboard/build.py</span>
    <span class="mono dim">github.com/olivervanderlugt/project-management</span>
  </footer>
</main>
<script>
document.querySelectorAll(".act[data-prompt]").forEach(function (button) {{
  button.addEventListener("click", function () {{
    var text = button.getAttribute("data-prompt");
    var done = function () {{
      var was = button.textContent;
      button.textContent = "copied - paste into Claude Code";
      button.classList.add("copied");
      setTimeout(function () {{
        button.textContent = was;
        button.classList.remove("copied");
      }}, 2200);
    }};
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(done, fallback);
    }} else {{
      fallback();
    }}
    function fallback() {{
      var field = document.createElement("textarea");
      field.value = text;
      field.setAttribute("readonly", "");
      field.style.position = "fixed";
      field.style.opacity = "0";
      document.body.appendChild(field);
      field.select();
      try {{ document.execCommand("copy"); done(); }} catch (err) {{ /* nothing to do */ }}
      document.body.removeChild(field);
    }}
  }});
}});
</script>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}")
    print(
        f"  {len(projects)} projects  {len(ideas)} ideas  "
        f"{len(decisions)} decisions  {len(weeks)} weekly reviews"
    )


if __name__ == "__main__":
    build()
