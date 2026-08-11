#!/usr/bin/env python3
"""Whether the overnight routine may open another PR tonight, decided by code
instead of a nightly judgment call. See decisions/0004.

    python3 scripts/pr_limits.py < prs.json

Input on stdin: a JSON array, one object per currently OPEN pull request
across every repo the Hangar governs:

    {"repo": "owner/name", "number": 5, "branch": "claude/night-...",
     "opened_at": "2026-08-10T00:24:30Z",
     "review_state": "APPROVED" | "CHANGES_REQUESTED" | "PENDING" | null}

`review_state` is null when nobody has reviewed the PR yet. The caller (the
nightly routine, or whoever is checking) gets this by combining
list_pull_requests with each PR's review decision for every repo in scope
before calling this script — nothing here talks to GitHub.

Output on stdout: one JSON object, see `decide()`.

The four things this script decides, so nobody has to decide them again by
eye every night:

1. **What counts as a "nightrun PR" at all.** Only a PR whose head branch
   starts with `claude/night-` or `night/` — anything else (a regular
   feature branch, a manual session) is a different kind of work and is
   ignored entirely, never listed, never counted. This used to be an
   ad-hoc call made fresh each night (see night-log 2026-08-10/11 excluding
   `quizzly#1` and `percentile#3`); now it's one regex.
2. **What counts as debt.** A nightrun PR with an `APPROVED` review is not
   debt — it is only waiting on a merge click, not on a judgment. Debt is
   everything else open: unreviewed (`review_state` is null or `PENDING`)
   or sent back (`CHANGES_REQUESTED`).
3. **Whether a specific repo may receive one more PR tonight**, against a
   per-repo cap (keeps one project from eating the whole night's capacity)
   and a global cap across every repo (keeps the total stack Ollie has to
   read bounded even if every project is at its own limit).
4. **What's gone quiet.** A nightrun PR open longer than STALE_DAYS with no
   review at all is surfaced (`stale` in the output) even though it no
   longer counts against the cap — a higher ceiling must not make an
   ignored PR invisible.
"""

import json
import re
import sys
from datetime import datetime, timezone

NIGHTRUN_BRANCH = re.compile(r"^(claude/)?night[/-]")
PER_REPO_CAP = 2
GLOBAL_CAP = 8
STALE_DAYS = 14


def is_nightrun_pr(branch):
    """A PR counts as nightrun work only by its branch name, nothing else."""
    return bool(NIGHTRUN_BRANCH.match(branch or ""))


def is_debt(pr):
    """Open work that still needs Ollie's judgment, not just a merge click."""
    return (pr.get("review_state") or None) != "APPROVED"


def age_days(pr, now=None):
    opened = pr.get("opened_at")
    if not opened:
        return 0
    try:
        opened_at = datetime.fromisoformat(opened.replace("Z", "+00:00"))
    except ValueError:
        return 0
    now = now or datetime.now(timezone.utc)
    return max(0, (now - opened_at).days)


def is_stale(pr, now=None):
    """Never reviewed, and it's been sitting a while."""
    return pr.get("review_state") in (None, "PENDING") and age_days(pr, now) > STALE_DAYS


def decide(prs, target_repo=None, now=None):
    """The whole answer: may tonight's chosen task's repo get a new PR.

    `target_repo` is the repo the candidate `ready` task would build in — pass
    it to get a repo-specific verdict. Leave it out to just get the totals
    (e.g. to loop over every repo with a `ready` task and find the first one
    that still has room).
    """
    nightrun = [pr for pr in prs if is_nightrun_pr(pr.get("branch"))]
    debt = [pr for pr in nightrun if is_debt(pr)]
    stale = [pr for pr in nightrun if is_stale(pr, now)]

    by_repo = {}
    for pr in debt:
        by_repo.setdefault(pr["repo"], []).append(pr)

    global_debt = len(debt)
    result = {
        "global_debt": global_debt,
        "global_cap": GLOBAL_CAP,
        "debt_by_repo": {repo: len(items) for repo, items in by_repo.items()},
        "per_repo_cap": PER_REPO_CAP,
        "stale": [{"repo": pr["repo"], "number": pr["number"]} for pr in stale],
    }

    if target_repo is not None:
        repo_debt = len(by_repo.get(target_repo, []))
        blocked_global = global_debt >= GLOBAL_CAP
        blocked_repo = repo_debt >= PER_REPO_CAP
        result["repo"] = target_repo
        result["repo_debt"] = repo_debt
        result["may_build"] = not (blocked_global or blocked_repo)
        if blocked_global:
            result["reason"] = f"global debt {global_debt} >= cap {GLOBAL_CAP}"
        elif blocked_repo:
            result["reason"] = f"{target_repo} debt {repo_debt} >= cap {PER_REPO_CAP}"
        else:
            result["reason"] = None

    return result


def first_open_repo(prs, candidate_repos, now=None):
    """The first repo in `candidate_repos` (ordered, e.g. by task priority)
    that still has room tonight, or None if every one of them is capped."""
    for repo in candidate_repos:
        if decide(prs, target_repo=repo, now=now)["may_build"]:
            return repo
    return None


def main():
    prs = json.loads(sys.stdin.read() or "[]")
    target_repo = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(decide(prs, target_repo=target_repo), indent=2))


if __name__ == "__main__":
    main()
