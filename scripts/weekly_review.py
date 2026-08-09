#!/usr/bin/env python3
"""Write the weekly review from what actually happened, not from memory.

    python3 scripts/weekly_review.py [--date YYYY-MM-DD]

For every `repo:` in `projects/*.md`, looks at commits since the last weekly
file's week and writes `planning/weekly/YYYY-Www.md` with Wins filled in.
Focus, Slipped and Next week are left for Ollie — a script cannot know what
mattered, only what happened.

`--date` overrides "today", for testing; the real run always means today.

No dependencies beyond the standard library and a local (or shallow-clonable)
checkout of each repo. Never invents a win: a repo with no commits in range is
left out rather than listed as empty, a week with nothing anywhere says so in
plain words instead of an empty bullet list, and a repo that could not be
reached at all is reported as unreachable rather than silently skipped —
"nothing happened" and "never checked" are different facts.

Idempotent by design: re-running for the same week recomputes Wins from
scratch and overwrites only the Wins section. Focus, Slipped, Next week, and
any other section a human already wrote (a "## Notes", say) are read back out
of the existing file and carried forward untouched — the second run of the
day must not eat the first run's manual edits.
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
    """The day after the last *reviewed* week ended.

    With no earlier week on record — the very first run — falls back to the
    Monday of the current week rather than the whole history of every repo:
    a "weekly" review that silently means "since the beginning of time" on
    day one is not weekly, and it is not a fallback anyone asked for.
    """
    earlier = sorted(w for w in weeks if w < current_week_code)
    if not earlier:
        return week_code_to_monday(current_week_code)
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


def default_ref(clone):
    """The ref that stands for `repo`'s real history: origin's default branch
    when it can be discovered, this checkout's own HEAD otherwise.

    A plain `git log` with no ref reads whatever the local checkout happens
    to have out — which, for a cached clone that only ever gets `git fetch`
    (a fetch moves remote-tracking refs, never the local branch), never
    moves past the commit it was cloned at. Reading a remote-tracking ref
    instead means a fetch is enough to see new commits, and it means a local
    sibling checkout sitting on a feature branch still reports the project's
    real branch instead of whatever a person happened to have open.

    Returns None if no ref resolves at all — a repo that has never had a
    single commit, which is "reached" but has nothing to read.
    """
    subprocess.run(
        ["git", "remote", "set-head", "origin", "--auto"],
        cwd=clone, capture_output=True,
    )
    result = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        cwd=clone, capture_output=True, text=True,
    )
    ref = result.stdout.strip() or "HEAD"
    resolves = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        cwd=clone, capture_output=True,
    ).returncode == 0
    return ref if resolves else None


def commits_since(repo, since):
    """One-line commit messages for `repo` since `since` (None = all history).

    Returns None if the repo could not be reached at all — distinct from an
    empty list, which means "reached, and either genuinely no commits since
    `since`, or no commits ever."
    """
    clone = local_clone(repo) or shallow_clone(repo)
    if clone is None:
        return None
    subprocess.run(["git", "fetch", "--quiet"], cwd=clone, capture_output=True)
    ref = default_ref(clone)
    if ref is None:
        return []
    args = ["git", "log", "--no-merges", "--pretty=format:%s", ref]
    if since:
        args.append(f"--since={since.isoformat()}")
    result = subprocess.run(args, cwd=clone, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_wins(since):
    """Wins lines, one per commit, prefixed with the repo slug.

    A repo with no commits in range is left out, per the task's own rule —
    that is silence, not news. A repo that could not be reached at all is
    NOT left out: it is reported as unreachable, because "checked, nothing
    happened" and "never checked" are different facts and the file should
    not claim the first when it only knows the second.
    """
    repos = project_repos()
    if not repos:
        return ["Nothing — no repos to check"]

    wins, unreachable = [], []
    for repo in repos:
        slug = repo.rsplit("/", 1)[-1]
        commits = commits_since(repo, since)
        if commits is None:
            unreachable.append(slug)
            continue
        wins.extend(f"{slug}: {message}" for message in commits)

    lines = wins or ["Nothing — no commits anywhere this week"]
    lines += [f"{slug}: could not be checked — repo unreachable" for slug in unreachable]
    return lines


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


def render(week_code, focus, sections):
    """`sections` is {heading: [body lines]}, in the order to render them —
    whatever order they were read back in, so a hand-added section (e.g. a
    "## Notes") keeps its place across a rerun instead of being dropped."""
    body = ["---", f"week: {week_code}", f"focus: {focus}", "---", ""]
    for heading, lines in sections.items():
        body.append(f"## {heading}")
        body.append("")
        body.extend(lines)
        body.append("")
    return "\n".join(body)


def write_weekly(today):
    week_code = iso_week_code(today)
    weeks = existing_weekly_weeks()
    since = since_date(week_code, weeks)
    wins = build_wins(since)

    out_path = WEEKLY_DIR / f"{week_code}.md"
    existing_meta, _ = parse_doc(out_path) if out_path.exists() else ({}, "")
    existing_sections = read_sections(out_path)

    focus = existing_meta.get("focus", "")
    sections = dict(existing_sections)
    sections["Wins"] = [f"- {w}" for w in wins]
    sections["Slipped"] = section_lines(existing_sections, "Slipped", ["-"])
    sections["Next week"] = section_lines(existing_sections, "Next week", ["-"])

    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(week_code, focus, sections), encoding="utf-8")
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
