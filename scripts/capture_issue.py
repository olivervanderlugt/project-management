#!/usr/bin/env python3
"""Turn a GitHub issue-form submission into a task file under tasks/.

    python3 scripts/capture_issue.py

Reads three pieces of information about the issue, environment variables
first, positional argv as a fallback (useful for local testing without
setting env vars):

    ISSUE_NUMBER   the issue number, e.g. "42"                    (required)
    ISSUE_TITLE    the issue's native GitHub title                (optional,
                   used only if the form's one-liner field is somehow blank)
    ISSUE_BODY     the full rendered issue body: GitHub renders each
                   issue-form answer as "### <field label>" followed by the
                   answer, in field order                         (required)
    ISSUE_URL      the issue's html_url, used for the link in Notes
                                                                    (optional)

    argv fallback: capture_issue.py <issue_number> <issue_title> <issue_body> [issue_url]

No dependencies beyond the standard library. No model calls, no network
calls — the issue form already collected structured fields, so everything
here is deterministic text handling.

Idempotent by design: if a task file already contains the marker
"Issue: #<n>" for this issue number, the script prints that it skipped and
exits 0 without writing a second file. Re-running on the same issue (e.g. a
retried workflow step) is always safe.

Always prints, as the last line, one of:

    status=written
    path=tasks/<slug>.md

or

    status=skipped
    path=tasks/<slug-of-existing-file>.md

so the calling workflow can grep stdout without parsing anything fancier.
"""

import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"

# Must match the `label:` text in .github/ISSUE_TEMPLATE/vangen.yml exactly —
# GitHub renders each form field as "### <label>" in the issue body.
LABEL_SUMMARY = "Wat is het, in één zin?"
LABEL_NOTES = "Meer context (optioneel)"
LABEL_PROJECT = "Welk project?"
LABEL_EFFORT = "Geschatte inspanning"

NO_RESPONSE = "_No response_"
VALID_EFFORT = {"S", "M", "L"}


# --------------------------------------------------------------------- parse


def parse_form_body(body):
    """Split a rendered issue-form body into {field label: answer}.

    GitHub renders each field as a "### <label>" heading followed by the
    answer text, in the order the fields appear in the form. A field left
    empty renders its answer as the literal string "_No response_".
    """
    fields = {}
    current = None
    buf = []
    for line in (body or "").splitlines():
        if line.startswith("### "):
            if current is not None:
                fields[current] = "\n".join(buf).strip()
            current = line[4:].strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        fields[current] = "\n".join(buf).strip()
    return fields


def field(fields, label, default=""):
    value = fields.get(label, default).strip()
    return "" if value == NO_RESPONSE else value


def is_capture_form(body):
    """True if this issue body came from the Vangen form.

    The workflow used to gate on a `capture` label, which fails silently when
    the label does not exist in the repo: no label, no run, no error. The body
    is the honest signal — a form submission always renders its field labels as
    "### " headings.
    """
    fields = parse_form_body(body)
    return LABEL_SUMMARY in fields


# ---------------------------------------------------------------------- slug


def slugify(text):
    """Lowercase ascii dashes, derived from a title."""
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "task"


def unique_slug(base, tasks_dir):
    """base, or base-2 / base-3 / ... if a file already claims it."""
    candidate = base
    n = 2
    while (tasks_dir / f"{candidate}.md").exists():
        candidate = f"{base}-{n}"
        n += 1
    return candidate


# ------------------------------------------------------------------ dedupe


def issue_marker(issue_number):
    return f"Issue: #{issue_number}"


def find_existing_task_for_issue(issue_number, tasks_dir):
    """The task file that already captured this issue, if any."""
    marker = re.compile(rf"Issue:\s*#{re.escape(str(issue_number))}\b")
    if not tasks_dir.is_dir():
        return None
    for path in sorted(tasks_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if marker.search(text):
            return path
    return None


# --------------------------------------------------------------------- build


def build_task_content(title, project, effort, notes, issue_number, issue_url, added):
    notes_body = notes or "(geen extra context meegegeven bij het vangen)"
    link = f" ({issue_url})" if issue_url else ""
    return f"""---
title: {title}
project: {project}
status: inbox
added: {added}
effort: {effort}
branch:
---

## Done means

Nog niet geschreven. Dit is alleen gevangen, niet uitgedacht — de taak blijft
`inbox` totdat er een concreet doel staat waaraan je kunt zien of hij af is.

## Notes

{notes_body}

Vastgelegd via GitHub issue, niet handmatig geschreven.
{issue_marker(issue_number)}{link}
"""


def write_task(issue_number, issue_title, issue_body, issue_url="", tasks_dir=None, today=None):
    """Write the task file for one issue. Returns (path, written: bool).

    tasks_dir defaults to the module-level TASKS_DIR, looked up at call time
    (not baked in as a default argument) so tests can monkeypatch
    capture_issue.TASKS_DIR and have main() pick up the change.
    """
    if tasks_dir is None:
        tasks_dir = TASKS_DIR
    tasks_dir.mkdir(parents=True, exist_ok=True)

    existing = find_existing_task_for_issue(issue_number, tasks_dir)
    if existing is not None:
        return existing, False

    fields = parse_form_body(issue_body)
    title = field(fields, LABEL_SUMMARY) or (issue_title or "").strip() or f"Vangst issue #{issue_number}"
    project = field(fields, LABEL_PROJECT)
    if project.lower() in ("", "weet ik niet"):
        project = ""
    effort = field(fields, LABEL_EFFORT).upper()
    if effort not in VALID_EFFORT:
        effort = ""
    notes = field(fields, LABEL_NOTES)

    added = (today or date.today()).isoformat()
    slug = unique_slug(slugify(title), tasks_dir)
    path = tasks_dir / f"{slug}.md"
    content = build_task_content(title, project, effort, notes, issue_number, issue_url, added)
    path.write_text(content, encoding="utf-8")
    return path, True


# ----------------------------------------------------------------------- cli


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    issue_number = os.environ.get("ISSUE_NUMBER") or (argv[0] if len(argv) > 0 else None)
    issue_title = os.environ.get("ISSUE_TITLE") or (argv[1] if len(argv) > 1 else "")
    issue_body = os.environ.get("ISSUE_BODY") or (argv[2] if len(argv) > 2 else "")
    issue_url = os.environ.get("ISSUE_URL") or (argv[3] if len(argv) > 3 else "")

    if not issue_number:
        print("error: no ISSUE_NUMBER (env or argv[0])", file=sys.stderr)
        return 1

    if not is_capture_form(issue_body):
        print(f"skipped: issue #{issue_number} is not a Vangen form submission")
        print("status=skipped")
        print("path=")
        return 0

    path, written = write_task(issue_number, issue_title, issue_body, issue_url)
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path

    if written:
        print(f"wrote {rel}")
        print("status=written")
    else:
        print(f"skipped: issue #{issue_number} already captured at {rel}")
        print("status=skipped")
    print(f"path={rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
