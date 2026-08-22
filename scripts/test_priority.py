#!/usr/bin/env python3
"""Tests for the priority score in dashboard/build.py.

    python3 scripts/test_priority.py

The point being defended: the board's "dit nu" line is derived, repeatable and
unopinionated about missing data. Two builds of the same tree must agree; the
project weight must come out of weights.yml and nowhere else; a task with no
project: must score neutral instead of crashing the build; and each of the four
factors must move a task in the direction the task file says it should.
"""

import importlib.util
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = _load("build", ROOT / "dashboard" / "build.py")

TODAY = date(2026, 8, 10)
WEIGHTS = {"versa": 5.0, "hangar": 2.0, "neutral": 3.0}


def task(**kwargs):
    base = {
        "slug": "iets-doen",
        "status": "ready",
        "effort": "M",
        "project": "versa",
        "added": "2026-08-01",
    }
    base.update(kwargs)
    return base


class ReadWeights(unittest.TestCase):
    """The table is data: flat key: value, and a bad line never fails a build."""

    def _weights(self, text):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "weights.yml"
        path.write_text(text, encoding="utf-8")
        return build.read_weights(path)

    def test_flat_key_value_lines_are_read(self):
        table = self._weights("# a comment\n\nversa: 5\nhangar: 2\nneutral: 3\n")
        self.assertEqual(table, {"versa": 5.0, "hangar": 2.0, "neutral": 3.0})

    def test_junk_lines_are_skipped_not_fatal(self):
        table = self._weights("versa: 5\nkapot: nope\nlos\nhangar: 2\n")
        self.assertEqual(table, {"versa": 5.0, "hangar": 2.0})

    def test_a_missing_file_is_an_empty_table(self):
        self.assertEqual(build.read_weights(ROOT / "nope" / "weights.yml"), {})

    def test_the_repo_table_parses_and_covers_every_project(self):
        table = build.read_weights()
        self.assertIn(build.NEUTRAL_KEY, table)
        for path in sorted((ROOT / "projects").glob("*.md")):
            if path.name.startswith("_"):
                continue
            self.assertIn(path.stem, table, f"{path.stem} has no weights.yml row")


class ProjectWeight(unittest.TestCase):
    def test_the_weight_comes_from_the_table(self):
        self.assertEqual(build.project_weight(task(project="versa"), WEIGHTS), 5.0)
        self.assertEqual(build.project_weight(task(project="hangar"), WEIGHTS), 2.0)

    def test_editing_the_table_changes_the_weight_without_touching_code(self):
        self.assertEqual(build.project_weight(task(project="versa"), {"versa": 1.0}), 1.0)

    def test_no_project_gets_the_neutral_weight(self):
        self.assertEqual(build.project_weight(task(project=""), WEIGHTS), 3.0)
        self.assertEqual(build.project_weight({"slug": "x"}, WEIGHTS), 3.0)

    def test_an_unlisted_project_gets_the_neutral_weight(self):
        self.assertEqual(build.project_weight(task(project="bestaat-niet"), WEIGHTS), 3.0)

    def test_a_table_without_a_neutral_row_still_answers(self):
        self.assertEqual(build.project_weight(task(project=""), {}), build.NEUTRAL_FALLBACK)


class ScoreIsSafe(unittest.TestCase):
    """Nothing missing from a task file may take the board down."""

    def test_a_task_without_a_project_scores_instead_of_crashing(self):
        self.assertEqual(
            build.priority_score(task(project=""), WEIGHTS, TODAY),
            build.priority_score(task(project="niet-in-de-tabel"), WEIGHTS, TODAY),
        )

    def test_an_empty_task_scores(self):
        self.assertIsInstance(build.priority_score({"slug": "leeg"}, WEIGHTS, TODAY), float)

    def test_a_broken_added_date_reads_as_zero_days(self):
        for value in ("", "gisteren", "2026-13-45"):
            self.assertEqual(build.task_age_days(task(added=value), TODAY), 0, value)

    def test_a_future_added_date_is_never_negative(self):
        self.assertEqual(build.task_age_days(task(added="2026-09-01"), TODAY), 0)


class Determinism(unittest.TestCase):
    def test_the_same_task_scores_the_same_twice(self):
        # ready 600 + weight 5x30 + effort M 10 + age 9 days, under one point.
        for _ in range(2):
            self.assertEqual(build.priority_score(task(), WEIGHTS, TODAY), 760.0)

    def test_the_same_queue_orders_the_same_twice(self):
        queue = [
            (task(slug="a", project="hangar"), ""),
            (task(slug="b", project="versa", status="inbox"), ""),
            (task(slug="c", project="versa", effort="S"), ""),
        ]
        first = [m["slug"] for _, m, _ in build.open_tasks_by_score(queue, WEIGHTS, TODAY)]
        second = [m["slug"] for _, m, _ in build.open_tasks_by_score(queue, WEIGHTS, TODAY)]
        self.assertEqual(first, second)
        self.assertEqual(first, ["c", "a", "b"])

    def test_tied_tasks_are_ordered_by_age_then_slug(self):
        queue = [
            (task(slug="zebra", added="2026-08-05"), ""),
            (task(slug="alpha", added="2026-08-05"), ""),
            (task(slug="oud", added="2026-08-04"), ""),
        ]
        order = [m["slug"] for _, m, _ in build.open_tasks_by_score(queue, WEIGHTS, TODAY)]
        self.assertEqual(order, ["oud", "alpha", "zebra"])

    def test_two_builds_of_the_real_repo_write_the_same_file(self):
        build.build()
        first = build.OUT.read_text(encoding="utf-8")
        build.build()
        self.assertEqual(first, build.OUT.read_text(encoding="utf-8"))


class FourFactors(unittest.TestCase):
    """Each factor moves the ranking in the direction the task file names."""

    def _score(self, **kwargs):
        return build.priority_score(task(**kwargs), WEIGHTS, TODAY)

    def test_ready_outranks_inbox_outranks_blocked(self):
        self.assertGreater(self._score(status="ready"), self._score(status="inbox"))
        self.assertGreater(self._score(status="inbox"), self._score(status="blocked"))

    def test_status_outranks_every_other_factor_combined(self):
        best_inbox = self._score(status="inbox", project="versa", effort="S", added="2020-01-01")
        worst_ready = self._score(
            status="ready", project="crew-management-system", effort="L", added="2026-08-10"
        )
        self.assertGreater(worst_ready, best_inbox)

    def test_a_heavier_project_outranks_a_lighter_one(self):
        self.assertGreater(self._score(project="versa"), self._score(project="hangar"))

    def test_project_weight_outranks_effort_and_age_together(self):
        heavy_and_slow = self._score(project="versa", effort="L", added="2026-08-10")
        light_and_quick = self._score(project="hangar", effort="S", added="2020-01-01")
        self.assertGreater(heavy_and_slow, light_and_quick)

    def test_small_outranks_medium_outranks_large(self):
        self.assertGreater(self._score(effort="S"), self._score(effort="M"))
        self.assertGreater(self._score(effort="M"), self._score(effort="L"))

    def test_effort_outranks_age(self):
        small_and_new = self._score(effort="S", added="2026-08-10")
        large_and_ancient = self._score(effort="L", added="2020-01-01")
        self.assertGreater(small_and_new, large_and_ancient)

    def test_older_weighs_heavier(self):
        self.assertGreater(self._score(added="2026-06-01"), self._score(added="2026-08-09"))

    def test_age_stops_counting_at_the_cap(self):
        self.assertEqual(self._score(added="2020-01-01"), self._score(added="2026-01-01"))

    def test_an_unknown_effort_is_not_rewarded(self):
        self.assertEqual(self._score(effort="XL"), self._score(effort="L"))


class TheBoard(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            (task(slug="klein", project="hangar", effort="S"), ""),
            (task(slug="groot", project="versa", effort="L"), ""),
            (task(slug="later", project="versa", status="inbox"), ""),
            (task(slug="klaar", project="versa", status="done"), ""),
            (task(slug="loopt", project="versa", status="doing"), ""),
        ]

    def test_only_open_tasks_are_scored(self):
        slugs = [m["slug"] for _, m, _ in build.open_tasks_by_score(self.tasks, WEIGHTS, TODAY)]
        self.assertEqual(slugs, ["groot", "klein", "later"])

    def test_the_board_names_the_highest_scoring_task(self):
        html = build.render_priority(self.tasks, {}, WEIGHTS)
        self.assertIn("Dit nu", html)
        self.assertIn("groot", html)
        self.assertLess(html.index("groot"), html.index("klein"))

    def test_an_empty_queue_says_so_instead_of_naming_nothing(self):
        html = build.render_priority([(task(status="done"), "")], {}, WEIGHTS)
        self.assertNotIn("Dit nu", html)
        self.assertIn("Nothing open", html)

    def test_a_missing_effort_renders_a_plain_dash_not_the_escaped_entity(self):
        html = build.render_priority([(task(slug="leeg", effort=""), "")], {}, WEIGHTS)
        self.assertIn("&mdash;", html)
        self.assertNotIn("&amp;mdash;", html)

    def test_the_real_board_carries_the_line_and_the_table(self):
        build.build()
        html = build.OUT.read_text(encoding="utf-8")
        self.assertIn('<section id="priority">', html)
        self.assertIn("Dit nu", html)
        self.assertIn('class="queue priority"', html)


if __name__ == "__main__":
    unittest.main()
