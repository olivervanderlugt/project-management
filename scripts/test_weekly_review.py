#!/usr/bin/env python3
"""Tests for scripts/weekly_review.py.

    python3 scripts/test_weekly_review.py

The point being defended: Wins come from real commits and nothing else, a
second run for the same week does not duplicate or invent anything, a repo
that could not be reached is reported as such rather than silently dropped,
and a human's own Focus/Slipped/Next week/other-section edits survive a
re-run.
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


def _run(*args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    )


def _git_repo(root, commits):
    """A tiny local git repo at `root` with one commit per message in `commits`."""
    root.mkdir(parents=True, exist_ok=True)
    _run("init", "--quiet", cwd=root)
    _run("config", "user.email", "test@example.com", cwd=root)
    _run("config", "user.name", "Test", cwd=root)
    for i, message in enumerate(commits):
        (root / "f.txt").write_text(f"{i}\n")
        _run("add", "f.txt", cwd=root)
        _run("commit", "--quiet", "-m", message, cwd=root)
    return root


def _bare_repo(root):
    root.mkdir(parents=True, exist_ok=True)
    _run("init", "--quiet", "--bare", cwd=root)
    return root


def _clone(remote, dest):
    subprocess.run(
        ["git", "clone", "--quiet", str(remote), str(dest)], capture_output=True
    )
    return dest


def _commit(repo, message):
    (repo / f"{message.replace(' ', '_')}.txt").write_text("x\n")
    _run("add", ".", cwd=repo)
    _run("commit", "--quiet", "-m", message, cwd=repo)


class IsoWeek(unittest.TestCase):
    def test_week_code_format(self):
        self.assertEqual(weekly_review.iso_week_code(date(2026, 8, 9)), "2026-W32")

    def test_monday_roundtrip(self):
        monday = weekly_review.week_code_to_monday("2026-W32")
        self.assertEqual(monday.isoweekday(), 1)
        self.assertEqual(weekly_review.iso_week_code(monday), "2026-W32")


class SinceDate(unittest.TestCase):
    def test_no_earlier_weeks_falls_back_to_this_week_not_all_history(self):
        # The very first run ever must not dump a repo's entire history into
        # one file — it should behave like every other run: "since Monday."
        self.assertEqual(
            weekly_review.since_date("2026-W32", {}),
            weekly_review.week_code_to_monday("2026-W32"),
        )
        self.assertEqual(
            weekly_review.since_date("2026-W32", {"2026-W32": None}),
            weekly_review.week_code_to_monday("2026-W32"),
        )

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

    def test_since_actually_filters(self):
        # Proves --since is wired through, without depending on exact commit
        # timestamps: a cutoff a year out must exclude everything.
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = _git_repo(Path(tmp) / "fixture", ["old", "older"])
            far_future = date.today() + weekly_review.timedelta(days=365)
            with mock.patch.object(weekly_review, "local_clone", return_value=repo_path), \
                 mock.patch.object(weekly_review, "shallow_clone", return_value=None):
                commits = weekly_review.commits_since("someone/fixture", far_future)
        self.assertEqual(commits, [])

    def test_empty_repo_is_reached_but_has_no_commits(self):
        # A repo cloned successfully but with zero commits ever (the actual
        # shape of olivervanderlugt/crew-management-system) must be "reached,
        # empty" (an empty list), never confused with "could not be reached."
        with tempfile.TemporaryDirectory() as tmp:
            remote = _bare_repo(Path(tmp) / "remote")
            clone = _clone(remote, Path(tmp) / "clone")
            with mock.patch.object(weekly_review, "local_clone", return_value=clone), \
                 mock.patch.object(weekly_review, "shallow_clone", return_value=None):
                commits = weekly_review.commits_since("someone/empty", None)
        self.assertEqual(commits, [])

    def test_second_call_sees_a_commit_pushed_after_the_first(self):
        # This is the stale-cache bug: a cached clone that only ever runs
        # `git fetch` must still see new commits on a later call, because
        # fetch moves remote-tracking refs even though it never touches the
        # local checked-out branch.
        with tempfile.TemporaryDirectory() as tmp:
            remote = _git_repo(Path(tmp) / "remote", ["week one commit"])
            clone = _clone(remote, Path(tmp) / "clone")
            with mock.patch.object(weekly_review, "local_clone", return_value=clone), \
                 mock.patch.object(weekly_review, "shallow_clone", return_value=None):
                first = weekly_review.commits_since("someone/fixture", None)
                _commit(remote, "week two commit")
                second = weekly_review.commits_since("someone/fixture", None)
        self.assertEqual(first, ["week one commit"])
        self.assertIn("week two commit", second)
        self.assertIn("week one commit", second)

    def test_reads_the_remote_default_branch_not_whatever_is_checked_out(self):
        # A local sibling checkout can be sitting on a feature branch (this
        # very repo usually is). The project's real history is the remote's
        # default branch, not whichever branch a person left checked out.
        with tempfile.TemporaryDirectory() as tmp:
            remote = _git_repo(Path(tmp) / "remote", ["on main"])
            clone = _clone(remote, Path(tmp) / "clone")
            _run("checkout", "--quiet", "-b", "someones-feature-branch", cwd=clone)
            _commit(clone, "local-only work in progress")
            with mock.patch.object(weekly_review, "local_clone", return_value=clone), \
                 mock.patch.object(weekly_review, "shallow_clone", return_value=None):
                commits = weekly_review.commits_since("someone/fixture", None)
        self.assertEqual(commits, ["on main"])
        self.assertNotIn("local-only work in progress", commits)


class BuildWins(unittest.TestCase):
    def test_never_invents_a_win(self):
        with mock.patch.object(weekly_review, "project_repos", return_value=["a/repo"]), \
             mock.patch.object(weekly_review, "commits_since", return_value=[]):
            wins = weekly_review.build_wins(None)
        self.assertEqual(wins, ["Nothing — no commits anywhere this week"])

    def test_unreachable_repo_is_reported_not_silently_dropped(self):
        with mock.patch.object(weekly_review, "project_repos", return_value=["a/gone"]), \
             mock.patch.object(weekly_review, "commits_since", return_value=None):
            wins = weekly_review.build_wins(None)
        self.assertEqual(len(wins), 2)
        self.assertIn("Nothing — no commits anywhere this week", wins)
        self.assertIn("gone: could not be checked — repo unreachable", wins)

    def test_wins_are_prefixed_with_the_repo_slug(self):
        def fake_commits(repo, since):
            return ["did the thing"] if repo == "org/quizzly" else []

        with mock.patch.object(
            weekly_review, "project_repos", return_value=["org/quizzly", "org/versa"]
        ), mock.patch.object(weekly_review, "commits_since", side_effect=fake_commits):
            wins = weekly_review.build_wins(None)
        self.assertEqual(wins, ["quizzly: did the thing"])

    def test_reachable_and_unreachable_repos_both_show_up(self):
        def fake_commits(repo, since):
            return None if repo == "org/gone" else ["shipped it"]

        with mock.patch.object(
            weekly_review, "project_repos", return_value=["org/quizzly", "org/gone"]
        ), mock.patch.object(weekly_review, "commits_since", side_effect=fake_commits):
            wins = weekly_review.build_wins(None)
        self.assertIn("quizzly: shipped it", wins)
        self.assertIn("gone: could not be checked — repo unreachable", wins)
        self.assertNotIn("Nothing", " ".join(wins))


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

    def test_rerun_preserves_a_hand_added_section(self):
        _write(
            self.weekly_dir / "2026-W32.md",
            "---\nweek: 2026-W32\nfocus: \n---\n\n"
            "## Wins\n\n- repo: old commit\n\n"
            "## Slipped\n\n-\n\n"
            "## Next week\n\n-\n\n"
            "## Notes\n\n- Ollie's own aside that isn't Wins/Slipped/Next week\n",
        )
        with mock.patch.object(weekly_review, "build_wins", return_value=["repo: new commit"]):
            out_path, _ = weekly_review.write_weekly(date(2026, 8, 9))
        text = out_path.read_text()
        self.assertIn("## Notes", text)
        self.assertIn("Ollie's own aside that isn't Wins/Slipped/Next week", text)

    def test_a_quiet_week_says_so_instead_of_an_empty_list(self):
        with mock.patch.object(
            weekly_review, "build_wins", return_value=["Nothing — no commits anywhere this week"]
        ):
            out_path, wins = weekly_review.write_weekly(date(2026, 8, 9))
        self.assertIn("Nothing", out_path.read_text())
        self.assertEqual(wins, ["Nothing — no commits anywhere this week"])

    def test_first_run_ever_scopes_to_this_week_not_all_history(self):
        # No planning/weekly/*.md at all yet — write_weekly must still ask
        # build_wins for a bounded `since`, not None.
        captured = {}

        def fake_build_wins(since):
            captured["since"] = since
            return ["repo: a commit"]

        with mock.patch.object(weekly_review, "build_wins", side_effect=fake_build_wins):
            weekly_review.write_weekly(date(2026, 8, 9))
        self.assertEqual(captured["since"], weekly_review.week_code_to_monday("2026-W32"))


class ProjectRepos(unittest.TestCase):
    def test_reads_real_repo_fields_from_the_hangar(self):
        # Against the real projects/ dir — every entry must be an owner/name pair.
        repos = weekly_review.project_repos()
        self.assertTrue(repos)
        for repo in repos:
            self.assertRegex(repo, r"^[\w.-]+/[\w.-]+$")


if __name__ == "__main__":
    unittest.main()
