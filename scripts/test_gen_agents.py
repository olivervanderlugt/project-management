#!/usr/bin/env python3
"""Tests for scripts/gen_agents.py.

    python3 scripts/test_gen_agents.py

Never writes to the real .claude/agents — every test uses a temp directory.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("gen_agents", ROOT / "scripts" / "gen_agents.py")
gen_agents = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen_agents)


PROJECT_WITH_REPO = """---
title: Versa
status: active
next: iets
repo: olivervanderlugt/versa
stack: Next.js, Postgres
---

## What this is

Songteksten naast een vertaling.
"""

PROJECT_WITHOUT_REPO = """---
title: Los idee zonder repo
status: active
repo:
---

## What this is

Nog geen code.
"""


def fake_repo_root(tmp):
    """A minimal Hangar: projects/ with two files, one of which has no repo."""
    root = Path(tmp)
    (root / "projects").mkdir()
    (root / "projects" / "versa.md").write_text(PROJECT_WITH_REPO, encoding="utf-8")
    (root / "projects" / "geen-repo.md").write_text(PROJECT_WITHOUT_REPO, encoding="utf-8")
    (root / "projects" / "_template.md").write_text(PROJECT_WITH_REPO, encoding="utf-8")
    return root


class ReadRouting(unittest.TestCase):
    def test_reads_the_real_table(self):
        table = gen_agents.read_routing()
        for kind in ("capture", "sharpen", "build_s", "build_ml", "check", "manage"):
            self.assertIn(kind, table)
        self.assertEqual(table["build_ml"]["model"], "opus")
        self.assertEqual(table["check"]["effort"], "low")

    def test_ignores_comments_and_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing.yml"
            path.write_text("# comment\n\nbuild_s:\n  model: sonnet\n  cap: 80000\n", encoding="utf-8")
            table = gen_agents.read_routing(path)
            self.assertEqual(table, {"build_s": {"model": "sonnet", "cap": "80000"}})


class ProjectSelection(unittest.TestCase):
    def setUp(self):
        self.original_root = gen_agents._build.ROOT

    def tearDown(self):
        gen_agents._build.ROOT = self.original_root

    def test_only_projects_with_a_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fake_repo_root(tmp)
            slugs = [meta["slug"] for meta, _ in gen_agents.projects_with_repos(root)]
            self.assertEqual(slugs, ["versa"])


class BuilderContent(unittest.TestCase):
    def setUp(self):
        self.routing = gen_agents.read_routing()
        self.text = gen_agents.builder_agent(
            {"slug": "versa", "repo": "olivervanderlugt/versa", "title": "Versa", "stack": "Next.js"},
            self.routing,
        )

    def test_names_its_one_repo(self):
        self.assertIn("olivervanderlugt/versa", self.text)
        self.assertIn("name: versa", self.text)

    def test_carries_the_hard_boundaries(self):
        for rule in ("never force-push", "secrets", "costs money", "night/<task-slug>"):
            self.assertIn(rule, self.text)

    def test_refuses_inbox_tasks(self):
        self.assertIn("refused", self.text)
        self.assertIn("`inbox` task is never built", self.text)

    def test_model_comes_from_the_routing_table(self):
        self.assertIn(f"model: {self.routing['build_ml']['model']}", self.text)


class ManagerAndChecker(unittest.TestCase):
    def setUp(self):
        self.routing = gen_agents.read_routing()

    def test_manager_is_told_not_to_read_code(self):
        text = gen_agents.manager_agent(self.routing)
        self.assertIn("Never project code", text)
        self.assertIn("May move **down** this table".lower(), text.lower())

    def test_manager_table_lists_every_kind(self):
        text = gen_agents.manager_agent(self.routing)
        for kind in self.routing:
            self.assertIn(f"`{kind}`", text)

    def test_checker_defaults_to_no(self):
        text = gen_agents.checker_agent(self.routing)
        self.assertIn("ship: true", text.replace("`", ""))
        self.assertIn("never see the builder's reasoning", text)


class GenerateAndPrune(unittest.TestCase):
    def setUp(self):
        self.original_root = gen_agents._build.ROOT

    def tearDown(self):
        gen_agents._build.ROOT = self.original_root

    def test_writes_one_per_project_plus_two(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as out:
            root = fake_repo_root(tmp)
            agents_dir = Path(out)
            written, removed = gen_agents.generate(root, agents_dir)
            names = sorted(p.name for p in agents_dir.glob("*.md"))
            self.assertEqual(names, ["hangar-checker.md", "hangar-manager.md", "versa.md"])
            self.assertEqual(removed, [])
            self.assertEqual(len(written), 3)

    def test_second_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as out:
            root = fake_repo_root(tmp)
            agents_dir = Path(out)
            gen_agents.generate(root, agents_dir)
            written, removed = gen_agents.generate(root, agents_dir)
            self.assertEqual((written, removed), ([], []))

    def test_prunes_a_generated_agent_whose_project_is_gone(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as out:
            root = fake_repo_root(tmp)
            agents_dir = Path(out)
            gen_agents.generate(root, agents_dir)
            (root / "projects" / "versa.md").unlink()
            written, removed = gen_agents.generate(root, agents_dir)
            self.assertEqual(removed, ["versa.md"])
            self.assertFalse((agents_dir / "versa.md").exists())

    def test_leaves_hand_written_agents_alone(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as out:
            root = fake_repo_root(tmp)
            agents_dir = Path(out)
            mine = agents_dir / "mijn-eigen-agent.md"
            mine.write_text("---\nname: mijn-eigen-agent\n---\n\nMet de hand geschreven.\n", encoding="utf-8")
            gen_agents.generate(root, agents_dir)
            self.assertTrue(mine.exists())
            self.assertIn("Met de hand geschreven", mine.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
