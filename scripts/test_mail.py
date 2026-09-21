#!/usr/bin/env python3
"""Tests for scripts/mail.py — against a fake osascript.

    python3 scripts/test_mail.py

There is no Mail on Linux, so a shell script named `osascript` is put first on
PATH. It writes the JXA it was handed to a file and prints whatever JSON the
test asked for. What is defended here: each subcommand builds the script it
should, `junk` never deletes, `draft` saves and never sends, and `send` does
not exist without HANGAR_EMAIL_SEND_OK=1. Whether Mail then does the right
thing is Ollie's first real run on the Mac (tasks/email-0).
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIL = ROOT / "scripts" / "mail.py"

_spec = importlib.util.spec_from_file_location("mail", MAIL)
mail = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mail)

FAKE = """#!/bin/sh
# fake osascript: record the script, print the canned answer
printf '%s' "$4" > "$FAKE_OSA_LOG"
printf '%s' "$FAKE_OSA_OUT"
"""


class WithFakeOsascript(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        bindir = Path(self.tmp.name) / "bin"
        bindir.mkdir()
        fake = bindir / "osascript"
        fake.write_text(FAKE)
        fake.chmod(0o755)
        self.log = Path(self.tmp.name) / "script.jxa"
        self.env = {
            **os.environ,
            "PATH": f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}",
            "FAKE_OSA_LOG": str(self.log),
            "FAKE_OSA_OUT": "{}",
        }
        self.env.pop("HANGAR_EMAIL_SEND_OK", None)

    def run_mail(self, *args, out="{}", send_ok=False):
        env = dict(self.env, FAKE_OSA_OUT=out)
        if send_ok:
            env["HANGAR_EMAIL_SEND_OK"] = "1"
        return subprocess.run(
            [sys.executable, str(MAIL), *args], env=env, capture_output=True, text=True
        )

    def script(self):
        return self.log.read_text() if self.log.exists() else ""


class Reading(WithFakeOsascript):
    def test_accounts_lists_names_and_addresses(self):
        out = json.dumps([{"name": "VU", "addresses": ["o@vu.nl"], "enabled": True}])
        result = self.run_mail("accounts", out=out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("emailAddresses", self.script())
        self.assertEqual(json.loads(result.stdout)[0]["name"], "VU")

    def test_unread_filters_on_account_since_and_read_status(self):
        result = self.run_mail(
            "unread", "--account", "Wandarbear ", "--since", "2026-09-21T07:00:00", out="[]"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn('"account": "Wandarbear "', script)  # trailing space survives
        self.assertIn("readStatus: false", script)
        self.assertIn("2026-09-21T07:00:00", script)

    def test_read_parses_list_unsubscribe(self):
        headers = (
            "From: a@b.nl\r\n"
            "List-Unsubscribe: <mailto:stop@b.nl>,\r\n <https://b.nl/u/1>\r\n"
            "List-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n"
        )
        out = json.dumps({"id": 5, "headers": headers, "content": "hi"})
        result = self.run_mail("read", "5", out=out)
        self.assertEqual(result.returncode, 0, result.stderr)
        got = json.loads(result.stdout)["unsubscribe"]
        self.assertEqual(got["http"], ["https://b.nl/u/1"])
        self.assertEqual(got["mailto"], ["mailto:stop@b.nl"])
        self.assertTrue(got["one_click"])
        self.assertIn('"id": 5', self.script())
        self.assertIn("byId(P.id)", self.script())

    def test_unsubscribe_parser_ignores_http_and_missing_header(self):
        got = mail.unsubscribe_from_headers("List-Unsubscribe: <http://plain.example/u>\n")
        self.assertEqual(got, {"http": [], "mailto": [], "one_click": False})
        self.assertEqual(mail.unsubscribe_from_headers("")["http"], [])


class Drafting(WithFakeOsascript):
    def test_draft_saves_in_the_account_and_never_sends(self):
        result = self.run_mail(
            "draft", "--account", "VU", "--to", "x@y.nl", "--subject", "Hoi", "--body", "Tekst",
            out=json.dumps({"saved": True}),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn("msg.save();", script)
        self.assertNotIn(".send(", script)
        self.assertIn('byName(P.account)', script)
        self.assertIn('"account": "VU"', script)

    def test_reply_draft_uses_reply_and_keeps_the_original(self):
        result = self.run_mail(
            "draft", "--account", "UvA", "--reply-to", "77", "--body", "Dank",
            out=json.dumps({"saved": True}),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn("M.reply(orig", script)
        self.assertIn('"replyTo": 77', script)
        self.assertIn("msg.save();", script)

    def test_new_draft_needs_to_and_subject(self):
        result = self.run_mail("draft", "--account", "VU", "--body", "x")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists(), "osascript must not be called")

    def test_body_file(self):
        body = Path(self.tmp.name) / "body.txt"
        body.write_text("Uit een bestand, met 'quotes' en \"dubbele\".")
        result = self.run_mail(
            "draft", "--account", "VU", "--to", "a@b.nl", "--subject", "S",
            "--body-file", str(body), out=json.dumps({"saved": True}),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Uit een bestand", self.script())


class Junking(WithFakeOsascript):
    def test_junk_moves_and_never_deletes(self):
        result = self.run_mail(
            "junk", "9", "--mailbox", "Ongewenste e-mail",
            out=json.dumps({"id": 9, "moved": True}),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn("M.move(m, {to: target})", script)
        self.assertIn("junkMailStatus = true", script)  # the fallback
        self.assertIn("Ongewenste e-mail", script)
        for forbidden in ("delete", "trash", "Trash"):
            self.assertNotIn(forbidden, script)

    def test_no_template_ever_deletes(self):
        for name in ("JXA_ACCOUNTS", "JXA_UNREAD", "JXA_READ", "JXA_COMPOSE", "JXA_JUNK"):
            template = getattr(mail, name).lower()
            self.assertNotIn("delete", template, name)
            self.assertNotIn("trash", template, name)


class Sending(WithFakeOsascript):
    def test_send_does_not_exist_without_the_variable(self):
        result = self.run_mail(
            "send", "--account", "VU", "--to", "a@b.nl", "--subject", "S", "--body", "x"
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("HANGAR_EMAIL_SEND_OK", result.stderr)
        self.assertFalse(self.log.exists(), "osascript must not be called")

    def test_help_does_not_mention_send_without_the_variable(self):
        result = self.run_mail("--help")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("send ", result.stdout.split("Never sends")[-1])

    def test_send_exists_with_the_variable(self):
        result = self.run_mail(
            "send", "--account", "VU", "--to", "a@b.nl", "--subject", "S", "--body", "x",
            out=json.dumps({"sent": True}), send_ok=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("msg.send();", self.script())
        self.assertNotIn("msg.save();", self.script())


if __name__ == "__main__":
    unittest.main(verbosity=1)
