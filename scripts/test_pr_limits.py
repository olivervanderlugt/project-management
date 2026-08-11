#!/usr/bin/env python3
"""Tests for scripts/pr_limits.py.

    python3 scripts/test_pr_limits.py

The point being defended: the overnight PR ceiling (decisions/0004) measures
review debt, not raw PR count — an approved PR must not block a repo, one slow
project must not block the other six, and the classification of what even
counts as a "nightrun PR" is a fixed regex, not a nightly judgment call.
"""

import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pr_limits = _load("pr_limits", ROOT / "scripts" / "pr_limits.py")

NOW = datetime(2026, 8, 11, 12, 0, tzinfo=timezone.utc)


def pr(**kwargs):
    base = {
        "repo": "olivervanderlugt/percentile",
        "number": 1,
        "branch": "night/some-task",
        "opened_at": "2026-08-10T00:00:00Z",
        "review_state": None,
    }
    base.update(kwargs)
    return base


class IsNightrunPr(unittest.TestCase):
    def test_night_slash_prefix_counts(self):
        self.assertTrue(pr_limits.is_nightrun_pr("night/percentile-f16-count-ladder"))

    def test_claude_night_dash_prefix_counts(self):
        self.assertTrue(pr_limits.is_nightrun_pr("claude/night-hangar-prioriteit-score"))

    def test_a_regular_feature_branch_does_not_count(self):
        self.assertFalse(pr_limits.is_nightrun_pr("claude/quizzly-finalization"))
        self.assertFalse(pr_limits.is_nightrun_pr("mvp/launchable"))
        self.assertFalse(pr_limits.is_nightrun_pr("main"))

    def test_a_branch_that_merely_contains_night_does_not_count(self):
        self.assertFalse(pr_limits.is_nightrun_pr("claude/knightly-refactor"))

    def test_missing_branch_is_safe(self):
        self.assertFalse(pr_limits.is_nightrun_pr(None))
        self.assertFalse(pr_limits.is_nightrun_pr(""))


class IsDebt(unittest.TestCase):
    def test_unreviewed_is_debt(self):
        self.assertTrue(pr_limits.is_debt(pr(review_state=None)))

    def test_pending_is_debt(self):
        self.assertTrue(pr_limits.is_debt(pr(review_state="PENDING")))

    def test_changes_requested_is_debt(self):
        self.assertTrue(pr_limits.is_debt(pr(review_state="CHANGES_REQUESTED")))

    def test_approved_is_not_debt(self):
        self.assertFalse(pr_limits.is_debt(pr(review_state="APPROVED")))


class Staleness(unittest.TestCase):
    def test_old_and_never_reviewed_is_stale(self):
        old = pr(opened_at="2026-07-01T00:00:00Z", review_state=None)
        self.assertTrue(pr_limits.is_stale(old, NOW))

    def test_recent_is_not_stale(self):
        recent = pr(opened_at="2026-08-10T00:00:00Z", review_state=None)
        self.assertFalse(pr_limits.is_stale(recent, NOW))

    def test_old_but_approved_is_not_stale(self):
        old_approved = pr(opened_at="2026-07-01T00:00:00Z", review_state="APPROVED")
        self.assertFalse(pr_limits.is_stale(old_approved, NOW))

    def test_old_but_changes_requested_is_not_stale(self):
        # It got a review, it just wasn't a clean one — "stale" means ignored.
        old_cr = pr(opened_at="2026-07-01T00:00:00Z", review_state="CHANGES_REQUESTED")
        self.assertFalse(pr_limits.is_stale(old_cr, NOW))

    def test_exactly_at_the_boundary_is_not_yet_stale(self):
        boundary = pr(opened_at=(NOW - timedelta(days=pr_limits.STALE_DAYS)).isoformat())
        self.assertFalse(pr_limits.is_stale(boundary, NOW))

    def test_missing_opened_at_is_never_stale(self):
        self.assertFalse(pr_limits.is_stale(pr(opened_at=None), NOW))


class Decide(unittest.TestCase):
    def test_non_nightrun_prs_are_ignored_entirely(self):
        prs = [pr(branch="claude/quizzly-finalization"), pr(branch="mvp/launchable")]
        result = pr_limits.decide(prs, target_repo="olivervanderlugt/percentile", now=NOW)
        self.assertEqual(result["global_debt"], 0)
        self.assertTrue(result["may_build"])

    def test_approved_prs_do_not_count_as_debt(self):
        prs = [pr(review_state="APPROVED") for _ in range(5)]
        result = pr_limits.decide(prs, target_repo="olivervanderlugt/percentile", now=NOW)
        self.assertEqual(result["global_debt"], 0)
        self.assertTrue(result["may_build"])

    def test_per_repo_cap_blocks_only_that_repo(self):
        prs = [
            pr(repo="olivervanderlugt/percentile", number=1),
            pr(repo="olivervanderlugt/percentile", number=2),
        ]
        percentile = pr_limits.decide(prs, target_repo="olivervanderlugt/percentile", now=NOW)
        quizzly = pr_limits.decide(prs, target_repo="olivervanderlugt/quizzly", now=NOW)
        self.assertFalse(percentile["may_build"])
        self.assertIn("percentile", percentile["reason"])
        self.assertTrue(quizzly["may_build"])

    def test_under_the_per_repo_cap_is_fine(self):
        prs = [pr(repo="olivervanderlugt/percentile", number=1)]
        result = pr_limits.decide(prs, target_repo="olivervanderlugt/percentile", now=NOW)
        self.assertTrue(result["may_build"])

    def test_global_cap_blocks_every_repo_even_under_their_own_cap(self):
        repos = [
            "olivervanderlugt/percentile",
            "olivervanderlugt/quizzly",
            "olivervanderlugt/versa",
            "olivervanderlugt/learning-website",
        ]
        prs = [pr(repo=r, number=n) for r in repos for n in (1, 2)]  # 8 total, cap
        result = pr_limits.decide(prs, target_repo="olivervanderlugt/timer-workout", now=NOW)
        self.assertEqual(result["global_debt"], 8)
        self.assertFalse(result["may_build"])
        self.assertIn("global", result["reason"])

    def test_stale_is_reported_but_does_not_block(self):
        prs = [pr(opened_at="2026-07-01T00:00:00Z", review_state=None, number=9)]
        result = pr_limits.decide(prs, target_repo="olivervanderlugt/percentile", now=NOW)
        self.assertTrue(result["may_build"])
        self.assertEqual(result["stale"], [{"repo": "olivervanderlugt/percentile", "number": 9}])

    def test_without_a_target_repo_only_totals_come_back(self):
        result = pr_limits.decide([pr()], now=NOW)
        self.assertNotIn("may_build", result)
        self.assertEqual(result["global_debt"], 1)

    def test_is_deterministic(self):
        prs = [pr(number=n) for n in range(3)]
        first = pr_limits.decide(prs, target_repo="olivervanderlugt/percentile", now=NOW)
        second = pr_limits.decide(prs, target_repo="olivervanderlugt/percentile", now=NOW)
        self.assertEqual(first, second)


class FirstOpenRepo(unittest.TestCase):
    def test_skips_capped_repos_and_returns_the_first_with_room(self):
        prs = [
            pr(repo="olivervanderlugt/percentile", number=1),
            pr(repo="olivervanderlugt/percentile", number=2),
        ]
        candidates = ["olivervanderlugt/percentile", "olivervanderlugt/quizzly"]
        self.assertEqual(
            pr_limits.first_open_repo(prs, candidates, now=NOW), "olivervanderlugt/quizzly"
        )

    def test_none_when_everything_is_capped(self):
        prs = [pr(repo="olivervanderlugt/quizzly", number=n) for n in (1, 2)]
        self.assertIsNone(
            pr_limits.first_open_repo(prs, ["olivervanderlugt/quizzly"], now=NOW)
        )


if __name__ == "__main__":
    unittest.main()
