#!/usr/bin/env python3
"""Tests for scripts/mail_profiles.py.

    python3 scripts/test_mail_profiles.py

Defended: addresses land in the right profile keyed on Mail's exact account
name (trailing space included), the provider guess is right for the domains
Ollie uses, filled fields are never asked again, and the body survives.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("mail_profiles", ROOT / "scripts" / "mail_profiles.py")
mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mp)


class Guessing(unittest.TestCase):
    def test_domains(self):
        for address, provider in (
            ("oliverlugt@gmail.com", "gmail"),
            ("o@icloud.com", "icloud"),
            ("o@student.vu.nl", "vu"),
            ("o@vu.nl", "vu"),
            ("o@student.uva.nl", "uva"),
            ("o@hotmail.nl", "outlook"),
            ("oliverlugt@mail.com", "mailcom"),
            ("ollie@wandarbear.nl", "other"),
            ("", "other"),
        ):
            self.assertEqual(mp.guess_provider(address), provider, address)


class Filling(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        (self.dir / "_template.md").write_text("---\naddress:\n---\n")
        (self.dir / "wandarbear.md").write_text(
            "---\naddress:\nprovider:\nmail_account: Wandarbear \njunk_mailbox: Junk\n"
            "priority: 1\nlanguage:\ntone:\nauto_unsubscribe:\nnever_spam:\ntested: 2026-09-21\n---\n"
            "\n## Wat hier binnenkomt\n\nZakelijk.\n"
        )
        self.accounts = [
            {"name": "Wandarbear ", "addresses": ["ollie@wandarbear.nl"], "enabled": True},
            {"name": "VU", "addresses": ["o.lugt@student.vu.nl"], "enabled": True},
        ]

    def test_yes_fills_defaults_and_keeps_filled_fields_and_body(self):
        mp.fill(self.accounts, self.dir, yes=True, out=lambda *_: None)
        fields, body = mp.parse((self.dir / "wandarbear.md").read_text())
        self.assertEqual(fields["address"], "ollie@wandarbear.nl")
        self.assertEqual(fields["mail_account"], "Wandarbear")  # trimmed on purpose
        self.assertEqual(fields["priority"], "1")  # was filled, not overwritten
        self.assertFalse((self.dir / "wandarbear-.md").exists())  # no second file for the same account
        self.assertEqual(fields["language"], "nl")
        self.assertEqual(fields["auto_unsubscribe"], "yes")
        self.assertIn("Zakelijk.", body)
        self.assertFalse((self.dir / "_template.md").read_text().count("wandarbear"))

    def test_new_account_gets_a_new_profile_with_provider_and_junk(self):
        mp.fill(self.accounts, self.dir, yes=True, out=lambda *_: None)
        fields, _ = mp.parse((self.dir / "vu.md").read_text())
        self.assertEqual(fields["provider"], "vu")
        self.assertEqual(fields["junk_mailbox"], "Junk Email")
        self.assertEqual(fields["address"], "o.lugt@student.vu.nl")

    def test_questions_only_for_blank_fields(self):
        asked = []

        def reader(prompt):
            asked.append(prompt)
            return "" if "provider" not in prompt else "other"

        mp.fill(self.accounts[:1], self.dir, reader=reader, out=lambda *_: None)
        self.assertFalse(any("prioriteit" in p for p in asked))  # priority was 1 already
        self.assertTrue(any("taal" in p for p in asked))
        fields, _ = mp.parse((self.dir / "wandarbear.md").read_text())
        self.assertEqual(fields["tone"], "kort en direct")

    def test_render_round_trips(self):
        fields = {k: "" for k in mp.FIELDS}
        fields.update({"mail_account": "X ", "tone": "kort, direct: ja"})
        parsed, _ = mp.parse(mp.render(fields, "\nbody\n"))
        self.assertEqual(parsed["mail_account"], "X")  # flat frontmatter cannot keep a trailing space
        self.assertEqual(parsed["tone"], "kort, direct: ja")


if __name__ == "__main__":
    unittest.main()
