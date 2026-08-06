#!/usr/bin/env python3
"""Tests for scripts/capture_issue.py.

    python3 scripts/test_capture_issue.py

Standard library unittest only. Every test uses a temp directory as the
tasks dir passed explicitly into write_task()/find_existing_task_for_issue()
— the real tasks/ in this repo is never touched.
"""

import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Import capture_issue.py by path so this test runs regardless of cwd/sys.path.
_spec = importlib.util.spec_from_file_location("capture_issue", ROOT / "scripts" / "capture_issue.py")
capture_issue = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(capture_issue)

# Same trick for dashboard/build.py, to check the generated file round-trips
# through the dashboard's own frontmatter reader.
_build_spec = importlib.util.spec_from_file_location("dashboard_build", ROOT / "dashboard" / "build.py")
dashboard_build = importlib.util.module_from_spec(_build_spec)
_build_spec.loader.exec_module(dashboard_build)


REALISTIC_BODY = """### Wat is het, in één zin?

Percentile: exportknop doet niks op mobiel

### Meer context (optioneel)

Getest op Safari iOS. Knop reageert niet op tap, console geeft geen fout.

### Welk project?

percentile

### Geschatte inspanning

S
"""

EMPTY_OPTIONALS_BODY = """### Wat is het, in één zin?

Iets losstaands dat me opviel

### Meer context (optioneel)

_No response_

### Welk project?

weet ik niet

### Geschatte inspanning

M
"""


class ParseFormBody(unittest.TestCase):
    def test_parses_realistic_body(self):
        fields = capture_issue.parse_form_body(REALISTIC_BODY)
        self.assertEqual(
            fields[capture_issue.LABEL_SUMMARY],
            "Percentile: exportknop doet niks op mobiel",
        )
        self.assertIn("Safari iOS", fields[capture_issue.LABEL_NOTES])
        self.assertEqual(fields[capture_issue.LABEL_PROJECT], "percentile")
        self.assertEqual(fields[capture_issue.LABEL_EFFORT], "S")

    def test_no_response_becomes_empty_string(self):
        fields = capture_issue.parse_form_body(EMPTY_OPTIONALS_BODY)
        self.assertEqual(capture_issue.field(fields, capture_issue.LABEL_NOTES), "")

    def test_weet_ik_niet_is_not_a_project(self):
        fields = capture_issue.parse_form_body(EMPTY_OPTIONALS_BODY)
        self.assertEqual(fields[capture_issue.LABEL_PROJECT], "weet ik niet")


class Slugify(unittest.TestCase):
    def test_lowercases_and_dashes(self):
        self.assertEqual(
            capture_issue.slugify("Percentile: exportknop doet niks op mobiel"),
            "percentile-exportknop-doet-niks-op-mobiel",
        )

    def test_strips_accents(self):
        self.assertEqual(capture_issue.slugify("Één zin over café"), "een-zin-over-cafe")

    def test_empty_title_falls_back(self):
        self.assertEqual(capture_issue.slugify(""), "task")

    def test_deduplicates_against_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            (tasks_dir / "foo.md").write_text("x", encoding="utf-8")
            (tasks_dir / "foo-2.md").write_text("x", encoding="utf-8")
            self.assertEqual(capture_issue.unique_slug("foo", tasks_dir), "foo-3")
            self.assertEqual(capture_issue.unique_slug("bar", tasks_dir), "bar")


class WriteTask(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tasks_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_writes_expected_frontmatter_and_sections(self):
        path, written = capture_issue.write_task(
            "42",
            "Vangen: exportknop",
            REALISTIC_BODY,
            issue_url="https://github.com/olivervanderlugt/project-management/issues/42",
            tasks_dir=self.tasks_dir,
            today=date(2026, 8, 6),
        )
        self.assertTrue(written)
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")

        self.assertIn("title: Percentile: exportknop doet niks op mobiel", text)
        self.assertIn("project: percentile", text)
        self.assertIn("status: inbox", text)
        self.assertIn("added: 2026-08-06", text)
        self.assertIn("effort: S", text)
        self.assertIn("branch:", text)
        self.assertIn("## Done means", text)
        self.assertIn("inbox", text.split("## Done means", 1)[1].split("## Notes", 1)[0])
        self.assertIn("## Notes", text)
        self.assertIn("Issue: #42", text)
        self.assertIn("https://github.com/olivervanderlugt/project-management/issues/42", text)

    def test_blank_project_when_weet_ik_niet(self):
        path, written = capture_issue.write_task(
            "7", "", EMPTY_OPTIONALS_BODY, tasks_dir=self.tasks_dir, today=date(2026, 8, 6)
        )
        self.assertTrue(written)
        text = path.read_text(encoding="utf-8")
        self.assertIn("project: \n", text)

    def test_falls_back_to_issue_title_if_summary_field_blank(self):
        body = REALISTIC_BODY.replace(
            "Percentile: exportknop doet niks op mobiel", ""
        )
        path, written = capture_issue.write_task(
            "9", "Fallback title from issue", body, tasks_dir=self.tasks_dir, today=date(2026, 8, 6)
        )
        self.assertTrue(written)
        text = path.read_text(encoding="utf-8")
        self.assertIn("title: Fallback title from issue", text)

    def test_second_run_on_same_issue_skips(self):
        path1, written1 = capture_issue.write_task(
            "42", "First", REALISTIC_BODY, tasks_dir=self.tasks_dir, today=date(2026, 8, 6)
        )
        before = set(self.tasks_dir.glob("*.md"))
        path2, written2 = capture_issue.write_task(
            "42", "First", REALISTIC_BODY, tasks_dir=self.tasks_dir, today=date(2026, 8, 6)
        )
        after = set(self.tasks_dir.glob("*.md"))

        self.assertTrue(written1)
        self.assertFalse(written2)
        self.assertEqual(path1, path2)
        self.assertEqual(before, after)  # no second file appeared

    def test_different_issues_get_different_files(self):
        path1, _ = capture_issue.write_task(
            "1", "First", REALISTIC_BODY, tasks_dir=self.tasks_dir, today=date(2026, 8, 6)
        )
        path2, _ = capture_issue.write_task(
            "2", "Second", REALISTIC_BODY, tasks_dir=self.tasks_dir, today=date(2026, 8, 6)
        )
        self.assertNotEqual(path1, path2)
        self.assertEqual(len(list(self.tasks_dir.glob("*.md"))), 2)

    def test_generated_file_parses_under_dashboard_build_reader(self):
        path, _ = capture_issue.write_task(
            "42",
            "Vangen: exportknop",
            REALISTIC_BODY,
            issue_url="https://github.com/olivervanderlugt/project-management/issues/42",
            tasks_dir=self.tasks_dir,
            today=date(2026, 8, 6),
        )
        meta, body = dashboard_build.parse_doc(path)
        self.assertEqual(meta["title"], "Percentile: exportknop doet niks op mobiel")
        self.assertEqual(meta["project"], "percentile")
        self.assertEqual(meta["status"], "inbox")
        self.assertEqual(meta["added"], "2026-08-06")
        self.assertEqual(meta["effort"], "S")
        self.assertIn("## Done means", body)
        self.assertIn("## Notes", body)


class FindExistingTaskForIssue(unittest.TestCase):
    def test_matches_exact_issue_number_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            (tasks_dir / "a.md").write_text("...\nIssue: #12\n", encoding="utf-8")
            (tasks_dir / "b.md").write_text("...\nIssue: #123\n", encoding="utf-8")

            found_12 = capture_issue.find_existing_task_for_issue("12", tasks_dir)
            found_123 = capture_issue.find_existing_task_for_issue("123", tasks_dir)
            found_none = capture_issue.find_existing_task_for_issue("99", tasks_dir)

            self.assertEqual(found_12.name, "a.md")
            self.assertEqual(found_123.name, "b.md")
            self.assertIsNone(found_none)

    def test_skips_template_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            (tasks_dir / "_template.md").write_text("Issue: #5\n", encoding="utf-8")
            self.assertIsNone(capture_issue.find_existing_task_for_issue("5", tasks_dir))


class MainCli(unittest.TestCase):
    def test_main_prints_status_and_path_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            original_tasks_dir = capture_issue.TASKS_DIR
            capture_issue.TASKS_DIR = tasks_dir
            try:
                import io
                import contextlib

                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    rc = capture_issue.main(["55", "Test title", REALISTIC_BODY, ""])
                self.assertEqual(rc, 0)
                lines = out.getvalue().splitlines()
                self.assertIn("status=written", lines)
                self.assertTrue(any(l.startswith("path=") for l in lines))

                # Run again: must skip, not error, and not write a second file.
                out2 = io.StringIO()
                with contextlib.redirect_stdout(out2):
                    rc2 = capture_issue.main(["55", "Test title", REALISTIC_BODY, ""])
                self.assertEqual(rc2, 0)
                self.assertIn("status=skipped", out2.getvalue().splitlines())
                self.assertEqual(len(list(tasks_dir.glob("*.md"))), 1)
            finally:
                capture_issue.TASKS_DIR = original_tasks_dir


if __name__ == "__main__":
    unittest.main()
