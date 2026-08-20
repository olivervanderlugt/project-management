#!/usr/bin/env python3
"""Tests for scripts/staleness.py.

    python3 scripts/test_staleness.py

Everything runs against temporary local git repos — no real network. "Offline"
and "the remote is unreachable" are simulated with a bogus local remote URL,
not by hitting the internet; git fails on those just as fast as it would on a
dropped connection, which is exactly the property being tested: fail fast,
fail silent, never hang.
"""

import importlib.util
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("staleness", ROOT / "scripts" / "staleness.py")
staleness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(staleness)


def _run(argv, cwd):
    result = subprocess.run(
        argv, cwd=str(cwd), capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _git(argv, cwd):
    return _run(["git", *argv], cwd)


def _init_repo(path, branch="main"):
    path.mkdir(parents=True, exist_ok=True)
    _git(["init", "--quiet", "-b", branch], path)
    _git(["config", "user.email", "night@example.com"], path)
    _git(["config", "user.name", "Night Run"], path)
    return path


def _commit(path, name, message):
    (path / name).write_text(f"{name}\n", encoding="utf-8")
    _git(["add", name], path)
    _git(["commit", "--quiet", "-m", message], path)


class StaleClone(unittest.TestCase):
    """A clone whose HEAD is genuinely behind origin's default branch."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)

        self.origin = _init_repo(root / "origin", branch="main")
        _commit(self.origin, "a.txt", "First")

        self.clone = root / "clone"
        _git(["clone", "--quiet", str(self.origin), str(self.clone)], root)
        _git(["config", "user.email", "night@example.com"], self.clone)
        _git(["config", "user.name", "Night Run"], self.clone)

        # The clone now has everything; move origin ahead without the clone
        # ever fetching it, reproducing the 2026-08-14 incident.
        _commit(self.origin, "b.txt", "Second")
        _commit(self.origin, "c.txt", "Third")

    def test_reports_the_count_and_branch_name(self):
        message = staleness.check_staleness(str(self.clone))
        self.assertIsNotNone(message)
        self.assertIn("2 commit", message)
        self.assertIn("main", message)

    def test_up_to_date_clone_is_silent(self):
        _git(["fetch", "--quiet", "origin"], self.clone)
        _git(["merge", "--quiet", "--ff-only", "origin/main"], self.clone)
        self.assertIsNone(staleness.check_staleness(str(self.clone)))

    def test_a_clone_ahead_of_origin_is_silent(self):
        _git(["fetch", "--quiet", "origin"], self.clone)
        _git(["merge", "--quiet", "--ff-only", "origin/main"], self.clone)
        _commit(self.clone, "d.txt", "Local work not yet pushed")
        self.assertIsNone(staleness.check_staleness(str(self.clone)))


class NoRemote(unittest.TestCase):
    def test_no_origin_configured_is_silent(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = _init_repo(Path(tmp.name) / "solo")
        _commit(repo, "a.txt", "Only commit")
        self.assertIsNone(staleness.check_staleness(str(repo)))


class DetachedHead(unittest.TestCase):
    def test_detached_head_is_silent(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = _init_repo(Path(tmp.name) / "repo")
        _commit(repo, "a.txt", "First")
        _commit(repo, "b.txt", "Second")
        sha = _git(["rev-parse", "HEAD~1"], repo)
        _git(["checkout", "--quiet", sha], repo)
        self.assertIsNone(staleness.check_staleness(str(repo)))


class UpstreamTrackingIsNotRequired(unittest.TestCase):
    """A branch with no upstream still gets compared — this is deliberate.

    Every `claude/night-*` branch starts with no upstream tracking configured
    (see `git checkout -b`), and that is exactly the situation the 08-14
    incident happened in. "geen upstream/remote is ingesteld" in the task's
    Done means is read here as "no `origin` remote at all", not "this
    particular branch lacks a tracking branch" — the latter reading would
    silence the hook on precisely the branches it exists to protect.
    """

    def test_branch_without_upstream_still_reports_staleness(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)

        origin = _init_repo(root / "origin", branch="main")
        _commit(origin, "a.txt", "First")

        clone = root / "clone"
        _git(["clone", "--quiet", str(origin), str(clone)], root)
        _git(["config", "user.email", "night@example.com"], clone)
        _git(["config", "user.name", "Night Run"], clone)

        # A fresh branch with no upstream configured, same as `claude/night-*`.
        _git(["checkout", "--quiet", "-b", "claude/night-example"], clone)
        with self.assertRaises(subprocess.CalledProcessError):
            _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], clone)

        _commit(origin, "b.txt", "Second")

        message = staleness.check_staleness(str(clone))
        self.assertIsNotNone(message)
        self.assertIn("1 commit", message)
        self.assertIn("main", message)


class FetchStepFailure(unittest.TestCase):
    """The `git fetch` call itself (not just discovering the default branch)
    failing or timing out must be silent too — exercised directly, since a
    tiny network_timeout alone dies on the earlier ls-remote call first."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.origin = _init_repo(root / "origin")
        _commit(self.origin, "a.txt", "First")
        self.clone = root / "clone"
        _git(["clone", "--quiet", str(self.origin), str(self.clone)], root)
        _commit(self.origin, "b.txt", "Second")

        self.real_run = staleness._run

        def fetch_fails(argv, cwd, timeout=None):
            if len(argv) >= 2 and argv[0] == "git" and argv[1] == "fetch":
                return None
            return self.real_run(argv, cwd, timeout=timeout)

        staleness._run = fetch_fails
        self.addCleanup(setattr, staleness, "_run", self.real_run)

    def test_fetch_failure_is_silent_not_an_exception(self):
        message = staleness.check_staleness(str(self.clone))
        self.assertIsNone(message)

    def test_fetch_timeout_path_is_silent(self):
        # Same forced failure, exercised through the timeout-labelled branch
        # (network_timeout is irrelevant here — _run is fully stubbed — the
        # point is that check_staleness treats a failed fetch identically
        # regardless of which of the two calls produced it).
        message = staleness.check_staleness(str(self.clone), network_timeout=0.0001)
        self.assertIsNone(message)


class NotAGitRepo(unittest.TestCase):
    def test_a_plain_directory_is_silent(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.assertIsNone(staleness.check_staleness(tmp.name))


class UnreachableRemote(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.repo = _init_repo(root / "repo")
        _commit(self.repo, "a.txt", "First")
        _git(["remote", "add", "origin", str(root / "does-not-exist")], self.repo)

    def test_offline_or_missing_remote_is_silent_and_fast(self):
        started = time.monotonic()
        message = staleness.check_staleness(str(self.repo))
        elapsed = time.monotonic() - started
        self.assertIsNone(message)
        self.assertLess(elapsed, 5, "an unreachable remote must fail fast, not hang")

    def test_never_raises(self):
        try:
            staleness.check_staleness(str(self.repo))
        except Exception as exc:  # pragma: no cover - the assertion is the point
            self.fail(f"check_staleness raised {exc!r} instead of staying silent")

    def test_the_script_itself_exits_zero_with_no_output(self):
        started = time.monotonic()
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "staleness.py")],
            cwd=str(self.repo),
            input=f'{{"cwd": "{self.repo}"}}',
            capture_output=True,
            text=True,
            timeout=15,
        )
        elapsed = time.monotonic() - started
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")
        self.assertLess(elapsed, 10, "an unreachable remote must fail fast, not hang")


class TimeoutIsEnforced(unittest.TestCase):
    """A network_timeout of ~0 must force the timeout path, not a hang."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.origin = _init_repo(root / "origin")
        _commit(self.origin, "a.txt", "First")
        self.clone = root / "clone"
        _git(["clone", "--quiet", str(self.origin), str(self.clone)], root)
        _commit(self.origin, "b.txt", "Second")

    def test_a_near_zero_timeout_returns_none_quickly(self):
        started = time.monotonic()
        message = staleness.check_staleness(str(self.clone), network_timeout=0.0001)
        elapsed = time.monotonic() - started
        self.assertIsNone(message)
        self.assertLess(elapsed, 5, "a timed-out network call must not hang")


class MainEntryPoint(unittest.TestCase):
    """The standalone/CLI path: no stdin required, correct hook JSON shape."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.origin = _init_repo(root / "origin")
        _commit(self.origin, "a.txt", "First")
        self.clone = root / "clone"
        _git(["clone", "--quiet", str(self.origin), str(self.clone)], root)
        _commit(self.origin, "b.txt", "Second")

    def _run_script(self, cwd, stdin_text=""):
        return subprocess.run(
            ["python3", str(ROOT / "scripts" / "staleness.py")],
            cwd=str(cwd),
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_silent_run_prints_nothing_and_exits_zero(self):
        _git(["fetch", "--quiet", "origin"], self.clone)
        _git(["merge", "--quiet", "--ff-only", "origin/main"], self.clone)
        result = self._run_script(self.clone, stdin_text="{}")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

    def test_stale_run_prints_the_documented_hook_shape(self):
        result = self._run_script(self.clone, stdin_text=f'{{"cwd": "{self.clone}"}}')
        self.assertEqual(result.returncode, 0)
        payload = __import__("json").loads(result.stdout)
        self.assertEqual(
            payload["hookSpecificOutput"]["hookEventName"], "SessionStart"
        )
        self.assertIn("1 commit", payload["hookSpecificOutput"]["additionalContext"])

    def test_empty_stdin_does_not_hang(self):
        result = self._run_script(self.clone, stdin_text="")
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
