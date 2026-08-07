#!/usr/bin/env python3
"""Tests for scripts/weekly_review.py.

    python3 scripts/test_weekly_review.py

Standard library unittest only, and no network: every test that needs commit
history passes its own `collect(repo, since, until)` into build_week, and every
test that writes uses a temp directory. The real planning/weekly/ is never
touched.
"""

import importlib.util
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("weekly_review", ROOT / "scripts" / "weekly_review.py")
weekly_review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(weekly_review)


PROJECT_VERSA = """---
title: Versa
status: active
repo: olivervanderlugt/versa
---

## What this is

Songteksten naast een vertaling.
"""

PROJECT_HANGAR = """---
title: The Hangar
status: active
repo: olivervanderlugt/project-management
---

## What this is

Het bord zelf.
"""

PROJECT_NO_REPO = """---
title: Los idee zonder repo
status: active
repo:
---

## What this is

Nog geen code.
"""

WEEK_FILE = """---
week: 2026-W31
focus: Iets ouds
---

## Wins

- Iets

## Slipped

-

## Next week

-
"""


def fake_root(tmp):
    """A minimal Hangar: two projects with a repo, one without, plus a template."""
    root = Path(tmp)
    (root / "projects").mkdir(parents=True, exist_ok=True)
    (root / "projects" / "versa.md").write_text(PROJECT_VERSA, encoding="utf-8")
    (root / "projects" / "hangar.md").write_text(PROJECT_HANGAR, encoding="utf-8")
    (root / "projects" / "geen-repo.md").write_text(PROJECT_NO_REPO, encoding="utf-8")
    (root / "projects" / "_template.md").write_text(PROJECT_VERSA, encoding="utf-8")
    return root


def fake_weekly(tmp, *weeks):
    """A weekly directory holding a `_template.md` plus the given week labels."""
    weekly = Path(tmp) / "weekly"
    weekly.mkdir(parents=True, exist_ok=True)
    (weekly / "_template.md").write_text(WEEK_FILE, encoding="utf-8")
    for label in weeks:
        (weekly / f"{label}.md").write_text(WEEK_FILE.replace("2026-W31", label), encoding="utf-8")
    return weekly


def collector(mapping):
    """A `collect` seam returning canned `(subjects, error)` per repo."""

    def collect(repo, since, until):
        return mapping.get(repo, ([], None))

    return collect


class WeekLabels(unittest.TestCase):
    def test_label_uses_the_iso_year(self):
        # 1 Jan 2027 is a Friday, still ISO week 53 of 2026.
        self.assertEqual(weekly_review.iso_week_label(date(2027, 1, 1)), "2026-W53")
        self.assertEqual(weekly_review.iso_week_label(date(2026, 8, 7)), "2026-W32")

    def test_parses_and_rejects(self):
        self.assertEqual(weekly_review.parse_week_label("2026-W32"), (2026, 32))
        for bad in ("2026-32", "W32", "2026-W00", "2026-W99", "", None, "notes"):
            self.assertIsNone(weekly_review.parse_week_label(bad), bad)

    def test_week_start_is_a_monday(self):
        self.assertEqual(weekly_review.week_start("2026-W32"), date(2026, 8, 3))
        self.assertEqual(weekly_review.week_start("2026-W32").weekday(), 0)


class Window(unittest.TestCase):
    def test_no_earlier_file_means_the_target_week_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            weekly = fake_weekly(tmp)
            since, until = weekly_review.window("2026-W32", weekly)
            self.assertEqual(since, datetime(2026, 8, 3, 0, 0, 0))
            self.assertEqual(until, datetime(2026, 8, 9, 23, 59, 59))
            self.assertEqual((until - since).days, 6)

    def test_lower_bound_is_where_the_previous_file_ended(self):
        with tempfile.TemporaryDirectory() as tmp:
            weekly = fake_weekly(tmp, "2026-W31")
            since, _ = weekly_review.window("2026-W32", weekly)
            self.assertEqual(since, datetime(2026, 8, 3, 0, 0, 0))

    def test_a_skipped_week_is_picked_up_not_lost(self):
        with tempfile.TemporaryDirectory() as tmp:
            weekly = fake_weekly(tmp, "2026-W30")
            since, until = weekly_review.window("2026-W32", weekly)
            self.assertEqual(since, datetime(2026, 7, 27, 0, 0, 0))
            self.assertEqual(until, datetime(2026, 8, 9, 23, 59, 59))

    def test_the_targets_own_file_never_moves_the_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            weekly = fake_weekly(tmp, "2026-W31", "2026-W32")
            self.assertEqual(
                weekly_review.window("2026-W32", weekly),
                (datetime(2026, 8, 3, 0, 0, 0), datetime(2026, 8, 9, 23, 59, 59)),
            )

    def test_only_the_newest_earlier_file_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            weekly = fake_weekly(tmp, "2026-W20", "2026-W30", "2026-W31")
            since, _ = weekly_review.window("2026-W32", weekly)
            self.assertEqual(since, datetime(2026, 8, 3, 0, 0, 0))

    def test_a_stray_note_is_not_a_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            weekly = fake_weekly(tmp, "2026-W30")
            (weekly / "losse-aantekening.md").write_text("hoi\n", encoding="utf-8")
            self.assertEqual(weekly_review.existing_weeks(weekly), [(2026, 30)])

    def test_a_bad_label_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                weekly_review.window("volgende week", fake_weekly(tmp))


class TrackedRepos(unittest.TestCase):
    def setUp(self):
        self.original_root = weekly_review._build.ROOT

    def tearDown(self):
        weekly_review._build.ROOT = self.original_root

    def test_only_projects_with_a_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            repos = weekly_review.tracked_repos(fake_root(tmp))
            self.assertEqual(
                repos,
                [
                    ("The Hangar", "olivervanderlugt/project-management"),
                    ("Versa", "olivervanderlugt/versa"),
                ],
            )

    def test_the_same_repo_is_read_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fake_root(tmp)
            (root / "projects" / "versa-kopie.md").write_text(PROJECT_VERSA, encoding="utf-8")
            repos = weekly_review.tracked_repos(root)
            self.assertEqual([repo for _, repo in repos].count("olivervanderlugt/versa"), 1)

    def test_the_real_hangar_projects_all_parse(self):
        repos = weekly_review.tracked_repos(ROOT)
        self.assertIn("olivervanderlugt/project-management", [repo for _, repo in repos])
        for _title, repo in repos:
            self.assertRegex(repo, r"^[^/\s]+/[^/\s]+$")


class RemoteUrls(unittest.TestCase):
    def test_reads_https_and_ssh(self):
        for url in (
            "https://github.com/olivervanderlugt/versa.git",
            "https://github.com/olivervanderlugt/versa",
            "git@github.com:olivervanderlugt/versa.git",
        ):
            self.assertEqual(weekly_review.repo_slug_from_url(url), "olivervanderlugt/versa")

    def test_nonsense_is_empty(self):
        self.assertEqual(weekly_review.repo_slug_from_url(""), "")
        self.assertEqual(weekly_review.repo_slug_from_url("nonsense"), "")

    def test_a_credential_never_survives_into_output(self):
        dirty = "fatal: could not read https://ghp_SECRETTOKEN@github.com/o/p.git"
        clean = weekly_review.scrub(dirty)
        self.assertNotIn("ghp_SECRETTOKEN", clean)
        self.assertIn("https://github.com/o/p.git", clean)


class Summarize(unittest.TestCase):
    def test_keeps_real_subjects_verbatim(self):
        self.assertEqual(
            weekly_review.summarize(["Add lyric sync", "Fix docker build"]),
            ["Add lyric sync", "Fix docker build"],
        )

    def test_bundles_autosave_commits_into_one_line(self):
        got = weekly_review.summarize(
            ["Autosave 2026-08-06 21:11", "Echt werk", "Autosave 2026-08-06 22:40"]
        )
        self.assertEqual(got, ["Echt werk", "2 autosave-commits"])

    def test_one_autosave_is_singular(self):
        self.assertEqual(weekly_review.summarize(["Autosave x"]), ["1 autosave-commit"])

    def test_repeated_subjects_appear_once(self):
        self.assertEqual(weekly_review.summarize(["Fix", "Fix", "Fix"]), ["Fix"])

    def test_overflow_is_counted_never_invented(self):
        got = weekly_review.summarize([f"commit {n}" for n in range(12)], limit=3)
        self.assertEqual(got, ["commit 0", "commit 1", "commit 2", "+9 meer commits"])

    def test_nothing_in_nothing_out(self):
        self.assertEqual(weekly_review.summarize([]), [])


class Sections(unittest.TestCase):
    def test_reads_raw_lines_under_a_heading(self):
        body = "## Wins\n\n- a\n\n## Slipped\n\n- b\n- c\n\n## Next week\n\nProza, geen bullet.\n"
        self.assertEqual(weekly_review.section_body(body, "Slipped"), "- b\n- c")
        self.assertEqual(weekly_review.section_body(body, "Next week"), "Proza, geen bullet.")
        self.assertEqual(weekly_review.section_body(body, "Onbekend"), "")


class OwnLinesOnly(unittest.TestCase):
    """What the script may delete from Wins: its own output, and nothing else."""

    def test_it_recognises_what_it_writes(self):
        # The round trip that matters: a recogniser that drifts from the writer
        # would start eating Ollie's bullets instead of its own.
        self.assertTrue(
            weekly_review.is_generated_win(
                weekly_review.win_line("Versa", "olivervanderlugt/versa", ["Fix"], 1)
            )
        )
        self.assertTrue(
            weekly_review.is_generated_win(
                weekly_review.win_line("The Hangar", "o/p", ["a", "b"], 23)
            )
        )

    def test_it_recognises_its_own_caveats(self):
        section = weekly_review.wins_section([], [("o/p", "geen toegang")])
        for line in section.splitlines():
            if line.strip():
                self.assertTrue(weekly_review.is_generated_win(line), line)

    def test_a_hand_written_bullet_is_not_its_own(self):
        for line in (
            "- Hangar exists: markdown structure, frontmatter contract, generated dashboard",
            "- Decided markdown-first over a real app, and wrote down why (`decisions/0001`)",
            "- **Versa** eindelijk af",
            "Gewoon een zin.",
        ):
            self.assertFalse(weekly_review.is_generated_win(line), line)

    def test_handwriting_stays_and_generated_lines_go(self):
        body = (
            "- Hangar exists: markdown structure\n"
            "- **Versa** (`o/versa`) — 1 commit: Fix\n"
            "- Decided markdown-first, and wrote down why (`decisions/0001`)\n"
            "\n"
            "_Niet gelezen deze run: `o/p` (geen toegang)._"
        )
        self.assertEqual(
            weekly_review.handwritten_wins(body),
            "- Hangar exists: markdown structure\n"
            "- Decided markdown-first, and wrote down why (`decisions/0001`)",
        )

    def test_the_templates_placeholder_is_scaffolding_not_writing(self):
        self.assertEqual(weekly_review.handwritten_wins("-"), "")
        self.assertEqual(weekly_review.handwritten_wins(""), "")

    def test_prose_and_inner_blank_lines_survive(self):
        body = "Wat een week.\n\n- een\n- twee\n\n- **X** (`o/x`) — 1 commit: y"
        self.assertEqual(
            weekly_review.handwritten_wins(body), "Wat een week.\n\n- een\n- twee"
        )

    def test_kept_writing_goes_above_the_generated_list(self):
        section = weekly_review.wins_section(
            [("Versa", "o/versa", ["Fix"], 1)], [], kept="- Mijn eigen regel"
        )
        self.assertTrue(section.startswith("- Mijn eigen regel\n\n"))
        self.assertIn("- **Versa** (`o/versa`) — 1 commit: Fix", section)


class Rendering(unittest.TestCase):
    def test_follows_the_template_shape(self):
        text = weekly_review.render("2026-W32", "", "- iets", "", "")
        self.assertTrue(text.startswith("---\nweek: 2026-W32\nfocus: \n---\n\n"))
        for heading in ("## Wins", "## Slipped", "## Next week"):
            self.assertIn(heading, text)
        self.assertTrue(text.endswith("\n"))

    def test_empty_sections_get_the_templates_bare_dash(self):
        text = weekly_review.render("2026-W32", "", "", "", "")
        self.assertIn("## Slipped\n\n-\n", text)
        self.assertIn("## Next week\n\n-\n", text)

    def test_the_real_template_parses_the_same_way(self):
        meta, body = weekly_review._build.parse_doc(ROOT / "planning" / "weekly" / "_template.md")
        self.assertIn("week", meta)
        self.assertIn("focus", meta)
        for heading in ("Wins", "Slipped", "Next week"):
            self.assertIn(f"## {heading}", body)

    def test_a_quiet_period_says_so_instead_of_guessing(self):
        self.assertIn("Geen commits", weekly_review.wins_section([], []))

    def test_an_unreachable_repo_is_named_not_hidden(self):
        section = weekly_review.wins_section([], [("o/p", "Repository not found")])
        self.assertIn("Niet gelezen deze run", section)
        self.assertIn("`o/p`", section)
        self.assertIn("Repository not found", section)

    def test_the_unreachable_note_is_not_a_bullet(self):
        # bullets() feeds the dashboard; a caveat must not read as a win there.
        section = weekly_review.wins_section(
            [("Versa", "o/versa", ["Fix"], 1)], [("o/p", "geen toegang")]
        )
        found = weekly_review._build.bullets(f"## Wins\n\n{section}\n", "Wins")
        self.assertEqual(len(found), 1)
        self.assertIn("Versa", found[0])

    def test_a_win_line_counts_the_real_commits(self):
        line = weekly_review.win_line("Versa", "o/versa", ["a", "b"], 7)
        self.assertIn("7 commits", line)
        self.assertIn("a; b", line)
        self.assertIn("`o/versa`", line)


class BuildWeek(unittest.TestCase):
    def setUp(self):
        self.original_root = weekly_review._build.ROOT

    def tearDown(self):
        weekly_review._build.ROOT = self.original_root

    def build(self, tmp, mapping, week="2026-W32", weeks=(), weekly=None):
        root = fake_root(tmp)
        weekly = weekly if weekly is not None else fake_weekly(tmp, *weeks)
        return weekly_review.build_week(
            week=week, weekly_dir=weekly, collect=collector(mapping), root=root
        )

    def test_wins_come_from_real_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, text, report = self.build(
                tmp,
                {
                    "olivervanderlugt/versa": (["Add lyric sync", "Fix docker build"], None),
                    "olivervanderlugt/project-management": (["Bouw het bord"], None),
                },
            )
            self.assertEqual(path.name, "2026-W32.md")
            self.assertIn("Add lyric sync", text)
            self.assertIn("Bouw het bord", text)
            self.assertEqual(report["moved"], 2)
            self.assertEqual(report["repos"], 2)

    def test_slips_and_next_week_stay_empty_for_ollie(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, text, _ = self.build(tmp, {"olivervanderlugt/versa": (["Iets"], None)})
            self.assertIn("## Slipped\n\n-\n", text)
            self.assertIn("## Next week\n\n-\n", text)
            self.assertIn("focus: \n", text)

    def test_a_silent_repo_is_left_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, text, report = self.build(
                tmp,
                {
                    "olivervanderlugt/versa": (["Iets"], None),
                    "olivervanderlugt/project-management": ([], None),
                },
            )
            self.assertNotIn("project-management", text)
            self.assertEqual(report["moved"], 1)

    def test_an_unreachable_repo_is_noted_and_never_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, text, report = self.build(
                tmp,
                {
                    "olivervanderlugt/versa": ([], "Repository not found"),
                    "olivervanderlugt/project-management": (["Iets"], None),
                },
            )
            self.assertIn("Niet gelezen deze run", text)
            self.assertIn("olivervanderlugt/versa", text)
            self.assertEqual(report["unreachable"], [("olivervanderlugt/versa", "Repository not found")])
            self.assertIn("Iets", text)

    def test_every_repo_unreachable_still_writes_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, text, report = self.build(
                tmp,
                {
                    "olivervanderlugt/versa": ([], "geen toegang"),
                    "olivervanderlugt/project-management": ([], "geen toegang"),
                },
            )
            self.assertIn("Geen commits", text)
            self.assertEqual(len(report["unreachable"]), 2)

    def test_the_window_reaches_the_collector(self):
        seen = []

        def collect(repo, since, until):
            seen.append((repo, since, until))
            return [], None

        with tempfile.TemporaryDirectory() as tmp:
            root = fake_root(tmp)
            weekly_review.build_week(
                week="2026-W32", weekly_dir=fake_weekly(tmp, "2026-W31"), collect=collect, root=root
            )
            self.assertEqual({s for _, s, _ in seen}, {datetime(2026, 8, 3, 0, 0, 0)})
            self.assertEqual({u for _, _, u in seen}, {datetime(2026, 8, 9, 23, 59, 59)})

    def test_defaults_to_the_week_of_the_given_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fake_root(tmp)
            path, _, _ = weekly_review.build_week(
                weekly_dir=fake_weekly(tmp),
                collect=collector({}),
                root=root,
                today=date(2026, 8, 7),
            )
            self.assertEqual(path.name, "2026-W32.md")

    def test_a_bad_week_label_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                self.build(tmp, {}, week="volgende week")


class Idempotent(unittest.TestCase):
    """Twice for the same week: one file, one copy of every line."""

    def setUp(self):
        self.original_root = weekly_review._build.ROOT

    def tearDown(self):
        weekly_review._build.ROOT = self.original_root

    def run_twice(self, tmp, mapping, weeks=("2026-W31",)):
        root = fake_root(tmp)
        weekly = fake_weekly(tmp, *weeks)
        results = []
        for _ in range(2):
            path, text, report = weekly_review.build_week(
                week="2026-W32", weekly_dir=weekly, collect=collector(mapping), root=root
            )
            path.write_text(text, encoding="utf-8")
            results.append((path, text, report))
        return weekly, results

    def test_one_file_and_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            mapping = {"olivervanderlugt/versa": (["Add lyric sync"], None)}
            weekly, results = self.run_twice(tmp, mapping)
            written = sorted(p.name for p in weekly.glob("*.md") if not p.name.startswith("_"))
            self.assertEqual(written, ["2026-W31.md", "2026-W32.md"])
            self.assertEqual(results[0][1], results[1][1])

    def test_no_duplicate_win_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            mapping = {"olivervanderlugt/versa": (["Add lyric sync"], None)}
            _, results = self.run_twice(tmp, mapping)
            text = results[1][1]
            self.assertEqual(text.count("Add lyric sync"), 1)
            self.assertEqual(text.count("## Wins"), 1)

    def test_the_second_run_sees_an_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, results = self.run_twice(tmp, {"olivervanderlugt/versa": (["Iets"], None)})
            self.assertFalse(results[0][2]["existed"])
            self.assertTrue(results[1][2]["existed"])

    def test_ollies_own_writing_survives_a_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fake_root(tmp)
            weekly = fake_weekly(tmp, "2026-W31")
            path = weekly / "2026-W32.md"
            path.write_text(
                "---\nweek: 2026-W32\nfocus: Percentile afmaken\n---\n\n"
                "## Wins\n\n- met de hand geschreven win\n\n"
                "## Slipped\n\n- Versa bleef liggen\n- en de tandarts ook\n\n"
                "## Next week\n\nEerst de audit, dan pas features.\n",
                encoding="utf-8",
            )
            _, text, report = weekly_review.build_week(
                week="2026-W32",
                weekly_dir=weekly,
                collect=collector({"olivervanderlugt/versa": (["Nieuwe commit"], None)}),
                root=root,
            )
            self.assertIn("focus: Percentile afmaken", text)
            self.assertIn("- Versa bleef liggen\n- en de tandarts ook", text)
            self.assertIn("Eerst de audit, dan pas features.", text)
            self.assertIn("Nieuwe commit", text)
            # His Wins line is not collateral damage — it stays, above the list.
            self.assertIn("- met de hand geschreven win", text)
            self.assertEqual(report["kept"], 1)
            self.assertLess(
                text.index("met de hand geschreven win"), text.index("Nieuwe commit")
            )

    def test_a_hand_written_win_survives_two_reruns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fake_root(tmp)
            weekly = fake_weekly(tmp, "2026-W31")
            path = weekly / "2026-W32.md"
            path.write_text(
                "---\nweek: 2026-W32\nfocus: \n---\n\n"
                "## Wins\n\n- Hangar exists: markdown structure\n"
                "- Decided markdown-first (`decisions/0001`)\n\n"
                "## Slipped\n\n-\n\n## Next week\n\n-\n",
                encoding="utf-8",
            )
            texts = []
            for _ in range(3):
                _, text, _ = weekly_review.build_week(
                    week="2026-W32",
                    weekly_dir=weekly,
                    collect=collector({"olivervanderlugt/versa": (["Nieuwe commit"], None)}),
                    root=root,
                )
                path.write_text(text, encoding="utf-8")
                texts.append(text)
            self.assertEqual(texts[0], texts[1])
            self.assertEqual(texts[1], texts[2])
            # Kept once, not multiplied and not lost.
            self.assertEqual(texts[2].count("- Hangar exists: markdown structure"), 1)
            self.assertEqual(texts[2].count("- Decided markdown-first (`decisions/0001`)"), 1)
            self.assertEqual(texts[2].count("Nieuwe commit"), 1)

    def test_stale_generated_lines_do_not_pile_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fake_root(tmp)
            weekly = fake_weekly(tmp, "2026-W31")
            path = weekly / "2026-W32.md"
            path.write_text(
                "---\nweek: 2026-W32\nfocus: \n---\n\n"
                "## Wins\n\n- **Versa** (`olivervanderlugt/versa`) — 9 commits: oud; ouder\n\n"
                "## Slipped\n\n-\n\n## Next week\n\n-\n",
                encoding="utf-8",
            )
            _, text, report = weekly_review.build_week(
                week="2026-W32",
                weekly_dir=weekly,
                collect=collector({"olivervanderlugt/versa": (["Nieuw"], None)}),
                root=root,
            )
            self.assertNotIn("9 commits", text)
            self.assertIn("1 commit: Nieuw", text)
            self.assertEqual(report["kept"], 0)


class Degradation(unittest.TestCase):
    """The git seam itself, without reaching the network."""

    def test_an_unreachable_remote_is_an_error_string_not_an_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            error = weekly_review.clone_bare(
                "olivervanderlugt/definitely-not-a-real-repo-xyz",
                Path(tmp) / "dest",
                datetime(2026, 8, 3),
                timeout=60,
            )
            self.assertIsInstance(error, str)
            self.assertTrue(error)

    def test_a_path_that_is_not_a_repo_is_an_error_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            subjects, error = weekly_review.git_subjects(
                tmp, datetime(2026, 8, 3), datetime(2026, 8, 9), timeout=30
            )
            self.assertEqual(subjects, [])
            self.assertIsInstance(error, str)

    def test_reading_this_checkout_works(self):
        # A window wide enough to hold this repo's whole life, but inside the
        # range git's date parser actually accepts — it silently matches nothing
        # for a year like 2100.
        subjects, error = weekly_review.git_subjects(
            ROOT, datetime(2000, 1, 1), datetime.now(), timeout=60
        )
        self.assertIsNone(error)
        self.assertTrue(subjects, "this repo has commits")

    def test_an_empty_window_is_no_activity_not_an_error(self):
        subjects, error = weekly_review.git_subjects(
            ROOT, datetime(2001, 1, 1), datetime(2001, 1, 7), timeout=60
        )
        self.assertEqual(subjects, [])
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
