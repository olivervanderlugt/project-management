#!/usr/bin/env python3
"""Write the weekly review from what actually changed, not from memory.

    python3 scripts/weekly_review.py
    python3 scripts/weekly_review.py --week 2026-W31
    python3 scripts/weekly_review.py --dry-run

Reads the `repo:` field of every file in `projects/`, collects the real commit
subjects from each of those repositories for the week's window, and writes
`planning/weekly/YYYY-Www.md` in the shape of `planning/weekly/_template.md`.

The script owns exactly the lines it wrote itself, and nothing else in the file.
`focus:`, `## Slipped` and `## Next week` are Ollie's and are never touched. So
is any line he wrote under `## Wins`: a re-run replaces only the bullets it can
recognise as its own output and keeps his above them. Overwriting a person's
own sentence, even inside the section the script fills, is a bug, not a
refresh.

## The window

`--week` (default: the ISO week of today) fixes the target week. The window
ends at that week's last second. The lower bound is deliberately *not* the
week's own Monday:

  - If an **earlier** weekly file exists, the window starts where the newest of
    them ended: the Monday 00:00 following that file's week. A skipped week is
    therefore picked up by the next review instead of falling through the
    floor — that is what "since the last weekly file" has to mean if the log is
    not to lose commits.
  - If there is no earlier weekly file, the window is the seven days ending
    with the target week, i.e. the target week itself.

The target week's *own* file is ignored when looking for the lower bound. That
is what makes a second run for the same week land on the same window, and so
produce the same file rather than a second one or a doubled Wins list.

Dates are handed to `git log --since/--until` as local-time timestamps, the
same clock a commit's author date is shown in.

## Reading other repositories

Read-only, and never with a credential of its own: each remote repo is cloned
bare into a scratch directory (shallow since the window start, falling back to
a blobless clone when the server refuses a shallow request), read with
`git log`, and thrown away. The Hangar itself, if a project names it, is read
from this working copy instead of being re-cloned.

A repo that cannot be reached — private, gone, or simply outside this session's
access scope — is never fatal. It is reported on stderr and noted at the foot
of the Wins section, so the week's file says plainly which repos it could not
look at rather than quietly implying they were idle.
"""

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEKLY_DIR = ROOT / "planning" / "weekly"

# Reuse the dashboard's frontmatter reader so there is one parser, not two.
_spec = importlib.util.spec_from_file_location("dashboard_build", ROOT / "dashboard" / "build.py")
_build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_build)

WEEK_FILE = re.compile(r"^(\d{4})-W(\d{2})$")
AUTOSAVE = re.compile(r"^autosave\b", re.IGNORECASE)
CREDENTIAL_IN_URL = re.compile(r"(https?://)[^/\s@]*@")

# The three shapes this script emits under `## Wins`, and the only lines it is
# allowed to remove on a re-run. Every one of them is produced by a function
# below — GENERATED_WIN by win_line(), the other two by wins_section() — and a
# test asserts the round trip, because a recogniser that drifts from the writer
# would start eating Ollie's bullets instead of its own.
GENERATED_WIN = re.compile(r"^- \*\*.+\*\* \(`[^`]+`\) — \d+ commits?: ")
NO_ACTIVITY = "- Geen commits in deze periode in de repo's die de Hangar volgt"
UNREACHABLE_NOTE = re.compile(r"^_Niet gelezen deze run: .*_$")

# Enough commit subjects to see what a week was about; the rest is counted, not
# invented away.
MAX_SUBJECTS = 8
CLONE_TIMEOUT = 180

# `git log` says these when a repository is real but has nothing in it. That is
# "no activity", not "unreachable", and the difference matters in the output.
EMPTY_REPO_SIGNALS = (
    "does not have any commits yet",
    "bad default revision",
    "unknown revision or path not in the working tree",
    "your current branch",
)


# ---------------------------------------------------------------------- weeks


def iso_week_label(day):
    """`2026-W32` for a date, using its ISO year — not its calendar year."""
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def parse_week_label(label):
    """`(iso_year, iso_week)` for `YYYY-Www`, or None if it is not one."""
    match = WEEK_FILE.match((label or "").strip())
    if not match:
        return None
    year, week = int(match.group(1)), int(match.group(2))
    if not 1 <= week <= 53:
        return None
    try:
        date.fromisocalendar(year, week, 1)
    except ValueError:
        return None
    return year, week


def week_start(label):
    """The Monday of an ISO week label."""
    year, week = parse_week_label(label)
    return date.fromisocalendar(year, week, 1)


def existing_weeks(weekly_dir):
    """Every `YYYY-Www.md` in the directory as `(year, week)`, oldest first.

    Templates and anything else that is not a week label are skipped, so a
    stray note in `planning/weekly/` cannot move the window.
    """
    if not Path(weekly_dir).is_dir():
        return []
    found = []
    for path in sorted(Path(weekly_dir).glob("*.md")):
        if path.name.startswith("_"):
            continue
        key = parse_week_label(path.stem)
        if key:
            found.append(key)
    return sorted(found)


def window(target, weekly_dir):
    """`(since, until)` datetimes for a week label. See the module docstring.

    `until` is the target week's last second. `since` is midnight on the Monday
    after the newest *earlier* weekly file, or the target week's own Monday when
    there is none. The target week's own file never counts, which is what makes
    a repeat run idempotent.
    """
    target_key = parse_week_label(target)
    if target_key is None:
        raise ValueError(f"not an ISO week label: {target!r}")
    start = week_start(target)
    end = start + timedelta(days=7)

    earlier = [key for key in existing_weeks(weekly_dir) if key < target_key]
    if earlier:
        previous_start = date.fromisocalendar(*earlier[-1], 1)
        since = previous_start + timedelta(days=7)
    else:
        since = end - timedelta(days=7)

    return (
        datetime.combine(since, datetime.min.time()),
        datetime.combine(end, datetime.min.time()) - timedelta(seconds=1),
    )


# -------------------------------------------------------------------- projects


def repo_slug_from_url(url):
    """`owner/name` out of an https or ssh GitHub remote, or "" if it is neither."""
    url = (url or "").strip()
    url = re.sub(r"\.git$", "", url)
    match = re.search(r"[:/]([^/:]+)/([^/]+)$", url)
    return f"{match.group(1)}/{match.group(2)}" if match else ""


def local_repo_slug(root=None):
    """The `owner/name` of the checkout this script lives in, or "" if unknown."""
    root = Path(root or ROOT)
    done = _run(["git", "-C", str(root), "remote", "get-url", "origin"], timeout=30)
    if done is None or done.returncode != 0:
        return ""
    return repo_slug_from_url(done.stdout.strip())


def tracked_repos(root=None):
    """`[(project title, owner/name)]` for every project naming a repo.

    Deduplicated on the repo, first project file wins — two project files
    claiming the same repo is a contract violation, not a reason to read it
    twice.
    """
    if root is not None:
        _build.ROOT = Path(root)
    seen, out = set(), []
    for meta, _body in _build.read_dir("projects"):
        repo = (meta.get("repo") or "").strip()
        if not repo or "/" not in repo or repo in seen:
            continue
        seen.add(repo)
        out.append((meta.get("title") or meta["slug"], repo))
    return out


# ------------------------------------------------------------------------ git


def scrub(text):
    """Never let a credential embedded in a remote URL reach stdout or a file."""
    return CREDENTIAL_IN_URL.sub(r"\1", text or "").strip()


def _run(cmd, timeout=CLONE_TIMEOUT, cwd=None):
    """Run a git command with prompts disabled. None if git itself is missing."""
    env = {"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "", "GCM_INTERACTIVE": "never"}
    merged = dict(os.environ, **env)
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=merged
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", "timed out")
    except FileNotFoundError:
        return None


def _last_error_line(done):
    lines = [line for line in scrub(done.stderr).splitlines() if line.strip()]
    return lines[-1][:200] if lines else f"git exited {done.returncode}"


def clone_bare(repo, dest, since, timeout=CLONE_TIMEOUT):
    """Clone `repo` read-only into `dest`. None on success, an error string otherwise.

    Shallow-since first because it is the cheapest thing that answers the
    question. Some servers refuse a shallow request that selects no commits, and
    a repo that was simply quiet all week must not be reported as unreachable —
    so a blobless full-history clone is the fallback before giving up.
    """
    url = f"https://github.com/{repo}.git"
    attempts = (
        ["--shallow-since", since.strftime("%Y-%m-%d")],
        ["--filter=blob:none"],
    )
    error = "no clone attempted"
    for extra in attempts:
        if Path(dest).exists():
            shutil.rmtree(dest, ignore_errors=True)
        done = _run(
            ["git", "clone", "--bare", "--quiet", "--no-tags", *extra, url, str(dest)],
            timeout=timeout,
        )
        if done is None:
            return "git is not installed"
        if done.returncode == 0:
            return None
        error = _last_error_line(done)
    shutil.rmtree(dest, ignore_errors=True)
    return error


def git_subjects(repo_path, since, until, timeout=CLONE_TIMEOUT):
    """`(subjects, error)` — commit subjects in the window, newest first.

    An empty repository is `([], None)`: nothing happened there, which is a
    fact, not a failure.
    """
    done = _run(
        [
            "git",
            "-C",
            str(repo_path),
            "log",
            "--no-merges",
            f"--since={since.isoformat(sep=' ')}",
            f"--until={until.isoformat(sep=' ')}",
            "--format=%s",
        ],
        timeout=timeout,
    )
    if done is None:
        return [], "git is not installed"
    if done.returncode != 0:
        stderr = scrub(done.stderr).lower()
        if any(signal in stderr for signal in EMPTY_REPO_SIGNALS):
            return [], None
        return [], _last_error_line(done)
    return [line.strip() for line in done.stdout.splitlines() if line.strip()], None


def collect_from_git(repo, since, until, scratch, local_slug="", timeout=CLONE_TIMEOUT):
    """`(subjects, error)` for one repo. The Hangar is read from this checkout."""
    if local_slug and repo == local_slug:
        return git_subjects(ROOT, since, until, timeout)
    dest = Path(scratch) / repo.replace("/", "__")
    error = clone_bare(repo, dest, since, timeout)
    if error:
        return [], error
    return git_subjects(dest, since, until, timeout)


# -------------------------------------------------------------------- summary


def summarize(subjects, limit=MAX_SUBJECTS):
    """Commit subjects, deduplicated and autosave-bundled. Nothing invented.

    Autosave commits are the hook doing its job, not a win, so a run of them
    collapses to one honest line with its count. Everything else keeps its own
    subject exactly as it was written; when there are more than `limit` of them
    the overflow is *counted*, never summarised into a sentence nobody wrote.
    """
    autosaves = sum(1 for s in subjects if AUTOSAVE.match(s))
    real, seen = [], set()
    for subject in subjects:
        if AUTOSAVE.match(subject) or subject in seen:
            continue
        seen.add(subject)
        real.append(subject)

    shown = real[:limit]
    if len(real) > limit:
        shown.append(f"+{len(real) - limit} meer commits")
    if autosaves:
        shown.append(f"{autosaves} autosave-commit{'s' if autosaves != 1 else ''}")
    return shown


def win_line(title, repo, subjects, total):
    """One Wins bullet for one repo."""
    count = f"{total} commit{'s' if total != 1 else ''}"
    return f"- **{title}** (`{repo}`) — {count}: {'; '.join(subjects)}"


# --------------------------------------------------------------------- render


def section_body(body, heading):
    """The raw lines under a `## heading`, up to the next one.

    Raw, not parsed into bullets: whatever Ollie wrote under Slipped or Next
    week comes back byte for byte, prose and sub-bullets included, because a
    re-run has no business reformatting his half of the file.
    """
    out, capturing = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            if capturing:
                break
            capturing = line[3:].strip().lower() == heading.lower()
            continue
        if capturing:
            out.append(line)
    return "\n".join(out).strip("\n")


def is_generated_win(line):
    """True if this Wins line is one this script wrote and may therefore replace."""
    line = line.strip()
    return (
        line == NO_ACTIVITY
        or bool(GENERATED_WIN.match(line))
        or bool(UNREACHABLE_NOTE.match(line))
    )


def handwritten_wins(wins_body):
    """Everything under `## Wins` that this script did not write, trimmed at the ends.

    The script's own bullets come out; the template's bare `-` placeholder comes
    out because it is scaffolding, not a sentence; everything else — Ollie's
    bullets, his prose, the blank lines between them — stays exactly as it is.
    Only leading and trailing blank lines are dropped, so the result can be
    joined to a freshly generated block with a predictable single blank line
    between them. That predictability is what keeps a second run byte-identical.
    """
    lines = [
        line
        for line in (wins_body or "").splitlines()
        if not is_generated_win(line) and line.strip() != "-"
    ]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def read_existing(path):
    """`(focus, kept_wins, slipped, next_week)` from a week file, or empty defaults."""
    path = Path(path)
    if not path.exists():
        return "", "", "", ""
    meta, body = _build.parse_doc(path)
    return (
        meta.get("focus", ""),
        handwritten_wins(section_body(body, "Wins")),
        section_body(body, "Slipped"),
        section_body(body, "Next week"),
    )


def render(week, focus, wins, slipped, next_week):
    """The whole file, in the shape of planning/weekly/_template.md."""
    return (
        f"---\nweek: {week}\nfocus: {focus}\n---\n\n"
        f"## Wins\n\n{wins or '-'}\n\n"
        f"## Slipped\n\n{slipped or '-'}\n\n"
        f"## Next week\n\n{next_week or '-'}\n"
    )


def wins_section(entries, unreachable, kept=""):
    """The Wins body: anything Ollie wrote, then this run's bullets beneath it.

    A repo with no commits is left out entirely rather than listed as empty —
    a week's wins should read as wins. A repo that could not be read is the
    opposite: it gets said out loud, because silence there would look exactly
    like idleness.

    `kept` is his own writing, as returned by handwritten_wins(). It goes first
    and is never reformatted; the generated block is only ever appended below.
    """
    lines = [win_line(title, repo, subjects, total) for title, repo, subjects, total in entries]
    if not lines:
        lines = [NO_ACTIVITY]
    if unreachable:
        listed = ", ".join(f"`{repo}` ({reason})" for repo, reason in unreachable)
        lines.append("")
        lines.append(f"_Niet gelezen deze run: {listed}._")
    generated = "\n".join(lines)
    return f"{kept}\n\n{generated}" if kept else generated


# ----------------------------------------------------------------------- build


def build_week(week=None, weekly_dir=None, collect=None, root=None, today=None):
    """Write one weekly file. Returns `(path, text, report)`.

    `collect(repo, since, until)` is the seam the tests use: it returns
    `(subjects, error)` for one repo, so nothing here needs a network.
    """
    weekly_dir = Path(weekly_dir or WEEKLY_DIR)
    week = week or iso_week_label(today or date.today())
    if parse_week_label(week) is None:
        raise ValueError(f"not an ISO week label: {week!r}")

    since, until = window(week, weekly_dir)
    repos = tracked_repos(root)

    entries, unreachable = [], []
    for title, repo in repos:
        subjects, error = collect(repo, since, until)
        if error:
            unreachable.append((repo, error))
            continue
        if not subjects:
            continue
        entries.append((title, repo, summarize(subjects), len(subjects)))

    path = weekly_dir / f"{week}.md"
    focus, kept, slipped, next_week = read_existing(path)
    text = render(week, focus, wins_section(entries, unreachable, kept), slipped, next_week)

    report = {
        "week": week,
        "since": since,
        "until": until,
        "repos": len(repos),
        "moved": len(entries),
        "unreachable": unreachable,
        "existed": path.exists(),
        "kept": len([line for line in kept.splitlines() if line.strip()]),
    }
    return path, text, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--week", help="ISO week label, e.g. 2026-W32. Default: this week.")
    parser.add_argument("--dry-run", action="store_true", help="Print the file, write nothing.")
    parser.add_argument("--timeout", type=int, default=CLONE_TIMEOUT, help="Per-git-call seconds.")
    args = parser.parse_args(argv)

    local = local_repo_slug()
    with tempfile.TemporaryDirectory(prefix="weekly-review-") as scratch:

        def collect(repo, since, until):
            return collect_from_git(repo, since, until, scratch, local, args.timeout)

        try:
            path, text, report = build_week(week=args.week, collect=collect)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    for repo, reason in report["unreachable"]:
        print(f"warning: could not read {repo}: {reason}", file=sys.stderr)

    window_text = f"{report['since']:%Y-%m-%d %H:%M} .. {report['until']:%Y-%m-%d %H:%M}"
    if args.dry_run:
        print(f"--- {path.relative_to(ROOT)} (dry run, {window_text}) ---")
        print(text, end="")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    changed = not path.exists() or path.read_text(encoding="utf-8") != text
    if changed:
        path.write_text(text, encoding="utf-8")
    print(f"{'wrote' if changed else 'unchanged'} {path.relative_to(ROOT)}  ({window_text})")
    print(
        f"  {report['moved']}/{report['repos']} repos with commits  "
        f"{len(report['unreachable'])} unreachable  "
        f"{'updated an existing file' if report['existed'] else 'new file'}"
    )
    print(
        f"  kept {report['kept']} hand-written line(s) in Wins; "
        "Slipped and Next week left for Ollie"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
