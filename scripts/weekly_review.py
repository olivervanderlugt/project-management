#!/usr/bin/env python3
"""Write the weekly review from what actually happened, not from memory.

    python3 scripts/weekly_review.py [--date YYYY-MM-DD]

For every `repo:` in `projects/*.md`, looks at commits since the last weekly
file's week and writes `planning/weekly/YYYY-Www.md` with Wins filled in.
Focus, Slipped and Next week are left for Ollie — a script cannot know what
mattered, only what happened.

`--date` overrides "today", for testing; the real run always means today.

No dependencies beyond the standard library and a local (or shallow-clonable)
checkout of each repo. Never invents a win: a repo with no commits that week is
left out rather than listed as empty, and a week with nothing anywhere says so
in plain words instead of an empty bullet list.

Idempotent by design: re-running for the same week recomputes Wins from
scratch and overwrites the Wins section only. Focus/Slipped/Next week, if a
human already wrote something there, are read back out of the existing file
and carried forward untouched — the second run of the day must not eat the
first run's manual edits.
"""

import argparse
import importlib.util
import re
import subprocess
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "projects"
WEEKLY_DIR = ROOT / "planning" / "weekly"
CLONE_CACHE = ROOT / ".cache" / "weekly-repos"

# Reuse the Hangar's one frontmatter parser (dashboard/build.py) instead of
# writing a second one — same flat key:value contract, same rules for what
# counts as a template.
_spec = importlib.util.spec_from_file_location(
    "hangar_dashboard_build", ROOT / "dashboard" / "build.py"
)
_dashboard_build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dashboard_build)
parse_doc = _dashboard_build.parse_doc

HEADING = re.compile(r"^##\s+(.+?)\s*$", re.M)


def project_repos():
    """Every non-blank `repo:` in projects/*.md, in file order."""
    repos = []
    for path in sorted(PROJECTS_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        meta, _ = parse_doc(path)
        repo = (meta.get("repo") or "").strip()
        if repo:
            repos.append(repo)
    return repos


def iso_week_code(day):
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def week_code_to_monday(week_code):
    year, week = week_code.split("-W")
    return date.fromisocalendar(int(year), int(week), 1)


def existing_weekly_weeks():
    """{week_code: path} for every real (non-template) file already written."""
    weeks = {}
    if not WEEKLY_DIR.is_dir():
        return weeks
    for path in sorted(WEEKLY_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        meta, _ = parse_doc(path)
        week = (meta.get("week") or "").strip()
        if week:
            weeks[week] = path
    return weeks


def since_date(current_week_code, weeks):
    """The day after the last *reviewed* week ended, or None for all history."""
    earlier = sorted(w for w in weeks if w < current_week_code)
    if not earlier:
        return None
    return week_code_to_monday(earlier[-1]) + timedelta(days=7)


def local_clone(repo):
    """A checkout of `repo` already on disk, if one is findable without a clone."""
    slug = repo.rsplit("/", 1)[-1]
    for base in (ROOT.parent, Path.home() / ".hangar-previews", CLONE_CACHE):
        candidate = base / slug
        if (candidate / ".git").exists():
            return candidate
    return None


def shallow_clone(repo):
    """Clone (or fast-forward) `repo` into the local cache. Best-effort."""
    slug = repo.rsplit("/", 1)[-1]
    dest = CLONE_CACHE / slug
    if (dest / ".git").exists():
        result = subprocess.run(
            ["git", "fetch", "--quiet", "--depth", "100", "origin"],
            cwd=dest, capture_output=True, text=True,
        )
        return dest if result.returncode == 0 else dest
    CLONE_CACHE.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{repo}.git"
    result = subprocess.run(
        ["git", "clone", "--quiet", "--depth", "100", url, str(dest)],
        capture_output=True, text=True,
    )
    return dest if result.returncode == 0 else None


def commits_since(repo, since):
    """One-line commit messages for `repo` since `since` (None = all history).

    Returns None if the repo could not be reached at all — distinct from an
    empty list, which means "reached, nothing happened."
    """
    clone = local_clone(repo) or shallow_clone(repo)
    if clone is None:
        return None
    subprocess.run(["git", "fetch", "--quiet"], cwd=clone, capture_output=True)
    args = ["git", "log", "--no-merges", "--pretty=format:%s"]
    if since:
        args.append(f"--since={since.isoformat()}")
    result = subprocess.run(args, cwd=clone, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_wins(since):
    """Wins lines, one per commit, prefixed with the repo slug. Skips silence."""
    wins = []
    reached_any = False
    for repo in project_repos():
        commits = commits_since(repo, since)
        if commits is None:
            continue
        reached_any = True
        slug = repo.rsplit("/", 1)[-1]
        wins.extend(f"{slug}: {message}" for message in commits)
    if wins:
        return wins
    if reached_any:
        return ["Nothing — no commits anywhere this week"]
    return ["Nothing — no repo could be reached to check"]


def read_sections(path):
    """{heading: [body lines]} for an existing weekly file, or {} if none yet."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        parts = text.lstrip().split("---", 2)
        text = parts[2] if len(parts) >= 3 else ""
    sections, current = {}, None
    for line in text.splitlines():
        match = HEADING.match(line)
        if match:
            current = match.group(1).strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def section_lines(sections, heading, default):
    lines = sections.get(heading)
    if lines is None:
        return default
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines if lines else default


def render(week_code, focus, wins, slipped, next_week):
    body = [
        "---",
        f"week: {week_code}",
        f"focus: {focus}",
        "---",
        "",
        "## Wins",
        "",
        *[f"- {w}" for w in wins],
        "",
        "## Slipped",
        "",
        *slipped,
        "",
        "## Next week",
        "",
        *next_week,
        "",
    ]
    return "\n".join(body)


def write_weekly(today):
    week_code = iso_week_code(today)
    weeks = existing_weekly_weeks()
    since = since_date(week_code, weeks)
    wins = build_wins(since)

    out_path = WEEKLY_DIR / f"{week_code}.md"
    existing_meta, _ = parse_doc(out_path) if out_path.exists() else ({}, "")
    sections = read_sections(out_path)

    focus = existing_meta.get("focus", "")
    slipped = section_lines(sections, "Slipped", ["-"])
    next_week = section_lines(sections, "Next week", ["-"])

    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(week_code, focus, wins, slipped, next_week), encoding="utf-8")
    return out_path, wins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Override today's date (YYYY-MM-DD), for testing")
    args = parser.parse_args()
    today = date.fromisoformat(args.date) if args.date else date.today()

    out_path, wins = write_weekly(today)
    print(f"wrote {out_path.relative_to(ROOT)}")
    print(f"  {len(wins)} win line(s)")


if __name__ == "__main__":
    main()
