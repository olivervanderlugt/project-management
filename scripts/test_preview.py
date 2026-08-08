#!/usr/bin/env python3
"""Tests for scripts/preview.py — the offline parts.

    python3 scripts/test_preview.py

The point being defended: the helper only ever runs repos named in projects/,
each project keeps a stable port, and the run command matches the stack it
finds instead of guessing. Nothing here spawns a process or touches the
network — that half is deliberately thin enough to read.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preview = _load("preview", ROOT / "scripts" / "preview.py")


class RunnableProjects(unittest.TestCase):
    def _projects(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        directory = Path(tmp.name)
        for name, body in files.items():
            (directory / name).write_text(body, encoding="utf-8")
        return preview.runnable_projects(directory)

    def test_only_projects_with_a_repo_are_runnable(self):
        table = self._projects(
            {
                "with-repo.md": "---\nrepo: ollie/thing\n---\n",
                "without.md": "---\ntitle: No repo\nrepo:\n---\n",
            }
        )
        self.assertEqual(table, {"with-repo": "ollie/thing"})

    def test_templates_are_skipped(self):
        table = self._projects({"_template.md": "---\nrepo: owner/name\n---\n"})
        self.assertEqual(table, {})

    def test_the_real_projects_dir_parses(self):
        table = preview.runnable_projects()
        self.assertIn("timer-workout", table)
        self.assertEqual(table["timer-workout"], "olivervanderlugt/timer-workout")


class AssignPorts(unittest.TestCase):
    def test_ports_are_stable_and_in_range(self):
        slugs = ["quizzly", "versa", "timer-workout"]
        once = preview.assign_ports(slugs)
        again = preview.assign_ports(list(reversed(slugs)))
        self.assertEqual(once, again)
        for port in once.values():
            self.assertGreaterEqual(port, preview.PORT_BASE)
            self.assertLess(port, preview.PORT_BASE + preview.PORT_SPAN)

    def test_no_two_projects_share_a_port(self):
        slugs = [f"project-{i}" for i in range(150)]
        ports = preview.assign_ports(slugs)
        self.assertEqual(len(set(ports.values())), len(slugs))

    def test_adding_a_project_does_not_move_the_others(self):
        before = preview.assign_ports(["quizzly", "versa"])
        after = preview.assign_ports(["quizzly", "versa", "timer-workout"])
        for slug, port in before.items():
            # Only a direct hash collision may move a port, and none of these
            # three collide — pinned so a refactor cannot quietly reshuffle.
            self.assertEqual(after[slug], port, slug)


class PlanRun(unittest.TestCase):
    def _checkout(self, package=None, index=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        checkout = Path(tmp.name)
        if package is not None:
            (checkout / "package.json").write_text(json.dumps(package), encoding="utf-8")
        if index:
            (checkout / "index.html").write_text("<h1>hi</h1>", encoding="utf-8")
        return checkout

    def test_static_site_gets_a_static_server(self):
        argv, env, install = preview.plan_run(self._checkout(index=True), 8700)
        self.assertIn("http.server", argv)
        self.assertIn("8700", argv)
        self.assertIn("127.0.0.1", argv)
        self.assertFalse(install)

    def test_vite_gets_its_port_flag(self):
        checkout = self._checkout(
            package={"scripts": {"dev": "vite"}, "devDependencies": {"vite": "^5"}}
        )
        argv, env, install = preview.plan_run(checkout, 8700)
        self.assertEqual(argv[:3], ["npm", "run", "dev"])
        self.assertIn("--port", argv)
        self.assertIn("8700", argv)
        self.assertTrue(install)

    def test_next_gets_its_port_flag(self):
        checkout = self._checkout(
            package={"scripts": {"dev": "next dev"}, "dependencies": {"next": "15"}}
        )
        argv, env, install = preview.plan_run(checkout, 8700)
        self.assertIn("-p", argv)
        self.assertIn("8700", argv)

    def test_unknown_framework_gets_port_env(self):
        checkout = self._checkout(package={"scripts": {"dev": "node server.js"}})
        argv, env, install = preview.plan_run(checkout, 8700)
        self.assertEqual(argv, ["npm", "run", "dev"])
        self.assertEqual(env, {"PORT": "8700"})

    def test_start_script_is_the_fallback(self):
        checkout = self._checkout(package={"scripts": {"start": "node ."}})
        argv, env, install = preview.plan_run(checkout, 8700)
        self.assertEqual(argv, ["npm", "run", "start"])

    def test_package_json_beats_index_html(self):
        checkout = self._checkout(package={"scripts": {"dev": "vite"}}, index=True)
        argv, env, install = preview.plan_run(checkout, 8700)
        self.assertEqual(argv[:2], ["npm", "run"])

    def test_installed_node_modules_skip_the_install(self):
        checkout = self._checkout(package={"scripts": {"dev": "vite"}})
        (checkout / "node_modules").mkdir()
        argv, env, install = preview.plan_run(checkout, 8700)
        self.assertFalse(install)

    def test_no_recognisable_stack_means_no_plan(self):
        self.assertIsNone(preview.plan_run(self._checkout(), 8700))
        self.assertIsNone(preview.plan_run(self._checkout(package={"name": "x"}), 8700))


if __name__ == "__main__":
    unittest.main()
