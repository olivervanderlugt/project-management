#!/usr/bin/env python3
"""Tests for scripts/weekly_review.py.

    python3 scripts/test_weekly_review.py

The point being defended: Wins come from real commits and nothing else, a
second run for the same week does not duplicate or invent anything, and a
human's own Focus/Slipped/Next week edits survive a re-run.
"""

import importlib.util
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


weekly_review = _load("weekly_review", ROOT / "scripts" / "weekly_review.py")


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git_repo(root, commits):
    """A tiny local git repo at `root` with one commit per message in `commits`."""
    root.mkdir(parents=True, exist_ok=True)
    run = lambda *args: subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    )
    run("init", "--quiet")
    run("config", "user.email", "test@example.com")
    run("config", "user.name", "Test")
    for i, message in enumerate(commits):
        (root / "f.txt").write_text(f"{i}\n")
        run("add", "f.txt")
        run("commit", "--quiet", "-m", message)
    return root


class IsoWeek(unittest.TestCase):
    def test_week_code_format(self):
        self.assertEqual(weekly_review.iso_week_code(date(2026, 8, 9)), "2026-W32")

    def test_monday_roundtrip(self):
        monday = weekly_review.week_code_to_monday("2026-W32")
        self.assertEqual(monday.isoweekday(), 1)
        self.assertEqual(weekly_review.iso_week_code(monday), "2026-W32")


class SinceDate(unittest.TestCase):
    def test_no_earlier_weeks_means_all_history(self):
        self.assertIsNone(weekly_review.since_date("2026-W32", {}))
        self.assertIsNone(weekly_review.since_date("2026-W32", {"2026-W32": None}))

    def test_since_is_the_monday_after_the_last_reviewed_week(self):
        since = weekly_review.since_date("2026-W34", {"2026-W32": None, "2026-W33": None})
        expected = weekly_review.week_code_to_monday("2026-W33") + weekly_review.timedelta(days=7)
        self.assertEqual(since, expected)
        self.assertEqual(since, weekly_review.week_code_to_monday("2026-W34"))

    def test_ignores_weeks_not_yet_reached(self):
        # A stray future file must not push the cutoff forward.
        since_with_future = weekly_review.since_date(
            "2026-W32", {"2026-W31": None, "2026-W40": None}
        )
        since_without_future = weekly_review.since_date("2026-W32", {"2026-W31": None})
        self.assertEqual(since_with_future, since_without_future)


class CommitsSince(unittest.TestCase):
    def test_reads_commits_from_a_local_clone(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = _git_repo(Path(tmp) / "fixture", ["first", "second"])
            with mock.patch.object(weekly_review, "local_clone", return_value=repo_path), \
                 mock.patch.object(weekly_review, "shallow_clone", return_value=None):
                commits = weekly_review.commits_since("someone/fixture", None)
        self.assertEqual(commits, ["second", "first"])

    def test_unreachable_repo_is_none_not_empty(self):
        with mock.patch.object(weekly_review, "local_clone", return_value=None), \
             mock.patch.object(weekly_review, "shallow_clone", return_value=None):
            self.assertIsNone(weekly_review.commits_since("someone/gone", None))

    def test_never_attempts_a_network_clone_when_a_local_one_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = _git_repo(Path(tmp) / "fixture", ["only commit"])
            shallow = mock.Mock(side_effect=AssertionError("should not shell out to clone"))
            with mock.patch.object(weekly_review, "local_clone", return_value=repo_path), \
                 mock.patch.object(weekly_review, "shallow_clone", shallow):
                weekly_review.commits_since("someone/fixture", None)
            shallow.assert_not_called()


class BuildWins(unittest.TestCase):
    def test_never_invents_a_win(self):
        with mock.patch.object(weekly_review, "project_repos", return_value=["a/repo"]), \
             mock.patch.object(weekly_review, "commits_since", return_value=[]):
            wins = weekly_review.build_wins(None)
        self.assertEqual(wins, ["Nothing — no commits anywhere this week"])

    def test_unreachable_repo_is_skipped_not_reported_as_empty(self):
        with mock.patch.object(weekly_review, "project_repos", return_value=["a/gone"]), \
             mock.patch.object(weekly_review, "commits_since", return_value=None):
            wins = weekly_review.build_wins(None)
        self.assertEqual(wins, ["Nothing — no repo could be reached to check"])

    def test_wins_are_prefixed_with_the_repo_slug(self):
        def fake_commits(repo, since):
            return ["did the thing"] if repo == "org/quizzly" else []

        with mock.patch.object(
            weekly_review, "project_repos", return_value=["org/quizzly", "org/versa"]
        ), mock.patch.object(weekly_review, "commits_since", side_effect=fake_commits):
            wins = weekly_review.build_wins(None)
        self.assertEqual(wins, ["quizzly: did the thing"])


class WriteWeekly(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.weekly_dir = root / "weekly"
        self._patches = [
            mock.patch.object(weekly_review, "WEEKLY_DIR", self.weekly_dir),
            mock.patch.object(weekly_review, "project_repos", return_value=[]),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self.tmp.cleanup()

    def test_writes_a_fresh_file_with_wins_and_blank_slots_for_the_rest(self):
        with mock.patch.object(weekly_review, "build_wins", return_value=["repo: a commit"]):
            out_path, wins = weekly_review.write_weekly(date(2026, 8, 9))
        self.assertEqual(out_path, self.weekly_dir / "2026-W32.md")
        text = out_path.read_text()
        self.assertIn("week: 2026-W32", text)
        self.assertIn("- repo: a commit", text)
        self.assertEqual(wins, ["repo: a commit"])

    def test_running_twice_does_not_duplicate_wins(self):
        with mock.patch.object(weekly_review, "build_wins", return_value=["repo: a commit"]):
            weekly_review.write_weekly(date(2026, 8, 9))
            out_path, _ = weekly_review.write_weekly(date(2026, 8, 9))
        text = out_path.read_text()
        self.assertEqual(text.count("a commit"), 1)

    def test_rerun_preserves_hand_written_focus_slipped_and_next_week(self):
        _write(
            self.weekly_dir / "2026-W32.md",
            "---\nweek: 2026-W32\nfocus: shipping the thing\n---\n\n"
            "## Wins\n\n- repo: old commit\n\n"
            "## Slipped\n\n- forgot the docs\n\n"
            "## Next week\n\n- write the docs\n",
        )
        with mock.patch.object(weekly_review, "build_wins", return_value=["repo: new commit"]):
            out_path, _ = weekly_review.write_weekly(date(2026, 8, 9))
        text = out_path.read_text()
        self.assertIn("focus: shipping the thing", text)
        self.assertIn("- forgot the docs", text)
        self.assertIn("- write the docs", text)
        self.assertIn("- repo: new commit", text)
        self.assertNotIn("old commit", text)

    def test_a_quiet_week_says_so_instead_of_an_empty_list(self):
        with mock.patch.object(
            weekly_review, "build_wins", return_value=["Nothing — no commits anywhere this week"]
        ):
            out_path, wins = weekly_review.write_weekly(date(2026, 8, 9))
        self.assertIn("Nothing", out_path.read_text())
        self.assertEqual(wins, ["Nothing — no commits anywhere this week"])


class ProjectRepos(unittest.TestCase):
    def test_reads_real_repo_fields_from_the_hangar(self):
        # Against the real projects/ dir — every entry must be an owner/name pair.
        repos = weekly_review.project_repos()
        self.assertTrue(repos)
        for repo in repos:
            self.assertRegex(repo, r"^[\w.-]+/[\w.-]+$")


if __name__ == "__main__":
    unittest.main()
