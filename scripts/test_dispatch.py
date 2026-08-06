#!/usr/bin/env python3
"""Tests for scripts/dispatch.py and scripts/brief.py.

    python3 scripts/test_dispatch.py

The point being defended: a task never silently goes to the wrong place. An
inbox task is sharpened, not built; a task without a project or a finish line
says so instead of producing a brief with a guess in it.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dispatch = _load("dispatch", ROOT / "scripts" / "dispatch.py")
brief = _load("brief", ROOT / "scripts" / "brief.py")

ROUTING = dispatch.read_routing()

PROJECT = {"slug": "versa", "repo": "olivervanderlugt/versa", "title": "Versa"}


def task(**kwargs):
    base = {"slug": "iets-doen", "status": "ready", "effort": "M", "project": "versa"}
    base.update(kwargs)
    return base


class KindFor(unittest.TestCase):
    def test_inbox_is_sharpened_never_built(self):
        self.assertEqual(dispatch.kind_for(task(status="inbox")), "sharpen")

    def test_ready_splits_on_effort(self):
        self.assertEqual(dispatch.kind_for(task(effort="S")), "build_s")
        self.assertEqual(dispatch.kind_for(task(effort="M")), "build_ml")
        self.assertEqual(dispatch.kind_for(task(effort="L")), "build_ml")

    def test_effort_is_case_insensitive(self):
        self.assertEqual(dispatch.kind_for(task(effort="s")), "build_s")

    def test_nothing_to_hand_out(self):
        for status in ("doing", "blocked", "done"):
            self.assertIsNone(dispatch.kind_for(task(status=status)), status)


class Dispatch(unittest.TestCase):
    def test_a_complete_task_dispatches_cleanly(self):
        plan = dispatch.dispatch(task(), PROJECT, ROUTING)
        self.assertEqual(plan["agent"], "versa")
        self.assertEqual(plan["repo"], "olivervanderlugt/versa")
        self.assertEqual(plan["model"], ROUTING["build_ml"]["model"])
        self.assertEqual(plan["cap"], int(ROUTING["build_ml"]["cap"]))
        self.assertEqual(plan["branch"], "night/iets-doen")
        self.assertEqual(plan["missing"], [])

    def test_no_project_has_no_agent(self):
        plan = dispatch.dispatch(task(project=""), None, ROUTING)
        self.assertIsNone(plan["agent"])
        self.assertTrue(any("no project" in m for m in plan["missing"]))

    def test_project_without_repo_has_no_agent(self):
        plan = dispatch.dispatch(task(), {"slug": "versa", "repo": ""}, ROUTING)
        self.assertIsNone(plan["agent"])
        self.assertTrue(any("no repo" in m for m in plan["missing"]))

    def test_boundaries_travel_with_every_plan(self):
        plan = dispatch.dispatch(task(), PROJECT, ROUTING)
        joined = " ".join(plan["nogo"]).lower()
        for rule in ("secrets", "costs money", "other than", "main"):
            self.assertIn(rule, joined)


class FinishLines(unittest.TestCase):
    def test_a_written_finish_line_is_returned(self):
        body = "## Done means\n\nDe knop werkt op mobiel en er is een test die dat aantoont.\n"
        self.assertEqual(len(brief.finish_lines(body)), 1)

    def test_an_unwritten_one_is_empty(self):
        body = "## Done means\n\nNog niet geschreven. Dit is alleen gevangen.\n"
        self.assertEqual(brief.finish_lines(body), [])

    def test_a_missing_section_is_empty(self):
        self.assertEqual(brief.finish_lines("## Notes\n\nGeen finish line hier.\n"), [])


class BriefFor(unittest.TestCase):
    def setUp(self):
        self.tasks = {
            "bouw-dit": (task(slug="bouw-dit"), "## Done means\n\nHet werkt en er is een test.\n"),
            "vaag": (task(slug="vaag", status="inbox"), "## Done means\n\nNog niet geschreven.\n"),
            "geen-dm": (task(slug="geen-dm"), "## Done means\n\nNog niet geschreven.\n"),
        }
        self.projects = {"versa": PROJECT}

    def test_ready_task_becomes_a_buildable_brief(self):
        out, missing = brief.brief_for("bouw-dit", self.tasks, self.projects, ROUTING)
        self.assertEqual(missing, [])
        self.assertEqual(out["agent"], "versa")
        self.assertEqual(out["branch"], "night/bouw-dit")
        self.assertTrue(out["dm"])

    def test_inbox_task_gets_a_sharpen_brief_that_forbids_building(self):
        out, _ = brief.brief_for("vaag", self.tasks, self.projects, ROUTING)
        self.assertIn("Do not build", out["goal"])
        self.assertIn("writing code for this task", out["nogo"])

    def test_ready_without_a_finish_line_is_reported_not_guessed(self):
        out, missing = brief.brief_for("geen-dm", self.tasks, self.projects, ROUTING)
        self.assertEqual(out["dm"], [])
        self.assertTrue(any("Done means" in m for m in missing))

    def test_unknown_task(self):
        out, missing = brief.brief_for("bestaat-niet", self.tasks, self.projects, ROUTING)
        self.assertIsNone(out)
        self.assertTrue(missing)


class RealQueue(unittest.TestCase):
    def test_every_open_task_in_the_repo_dispatches_or_says_why(self):
        tasks, projects = brief.load_docs()
        for slug in tasks:
            plan = dispatch.dispatch(tasks[slug][0], projects.get((tasks[slug][0].get("project") or "").strip()), ROUTING)
            if plan["kind"] is None:
                continue
            self.assertTrue(plan["agent"] or plan["missing"], slug)


if __name__ == "__main__":
    unittest.main()
