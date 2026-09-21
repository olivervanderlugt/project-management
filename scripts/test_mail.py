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
        self.assertIn("findMessage(M, P)", self.script())

    def test_read_with_account_searches_that_inbox(self):
        result = self.run_mail("read", "5", "--account", "Wandarbear ", out=json.dumps({"id": 5}))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"account": "Wandarbear "', self.script())
        self.assertIn("whose({id: P.id})", self.script())

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
        self.assertIn("close({saving: 'yes'})", script)
        self.assertNotIn(".send(", script)
        self.assertIn("M.ToRecipient({address: t})", script)  # not the abstract Recipient
        self.assertIn("findAccount(M, P.account)", script)
        self.assertIn('"account": "VU"', script)

    def test_reply_draft_uses_reply_and_keeps_the_original(self):
        result = self.run_mail(
            "draft", "--account", "UvA", "--reply-to", "77", "--body", "Dank",
            out=json.dumps({"saved": True}),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn("findAccount(M, P.account)", script)
        self.assertIn("M.reply(orig", script)
        self.assertIn('"replyTo": 77', script)
        self.assertIn('"id": 77', script)  # findMessage looks in UvA's inbox, not the unified one
        self.assertIn("msg.save();", script)
        # a reply keeps the account Mail bound it to; only a new message sets sender
        self.assertEqual(script.count("msg.sender = from;"), 1)
        self.assertLess(script.index("M.OutgoingMessage"), script.index("msg.sender = from;"))

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
            "junk", "9", "--account", "VU", "--mailbox", "Ongewenste e-mail",
            out=json.dumps({"id": 9, "moved": True}),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn("M.move(m, {to: target})", script)
        self.assertIn("junkMailStatus = true", script)  # the fallback, reported as flagged
        candidates = json.loads(script.split("const P = ", 1)[1].split(";", 1)[0])["candidates"]
        self.assertEqual(candidates[0], "Ongewenste e-mail")  # explicit flag wins
        self.assertIn("Junk Email", candidates)  # the usual names follow
        for forbidden in ("delete", "trash", "Trash"):
            self.assertNotIn(forbidden, script)

    def test_junk_needs_an_account(self):
        result = self.run_mail("junk", "9")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())

    def test_junk_mailbox_comes_from_the_profile_outside_the_repo(self):
        accounts = Path(self.tmp.name) / "accounts"
        accounts.mkdir()
        (accounts / "vu.md").write_text("---\nmail_account: VU\njunk_mailbox: Junk Email\n---\n")
        (accounts / "wandarbear.md").write_text("---\nmail_account: Wandarbear\njunk_mailbox: Junk\n---\n")
        os.environ["HANGAR_MAIL_DIR"] = self.tmp.name
        try:
            self.assertEqual(mail.junk_mailbox_from_profile("VU"), "Junk Email")
            self.assertEqual(mail.junk_mailbox_from_profile("Wandarbear "), "Junk")  # trailing space ok
            self.assertIsNone(mail.junk_mailbox_from_profile("No Such Account"))
        finally:
            os.environ.pop("HANGAR_MAIL_DIR", None)

    def test_profiles_are_not_read_from_the_repo(self):
        # The repo is public; the only profile in it is the template.
        repo_accounts = ROOT / "email" / "accounts"
        self.assertEqual([p.name for p in repo_accounts.glob("*.md")], ["_template.md"])
        self.assertNotIn("email", mail.data_dir().split(os.sep)[-2:])

    def test_unread_sorts_newest_first_before_the_limit(self):
        self.run_mail("unread", "--limit", "3", out="[]")
        script = self.script()
        self.assertIn("out.sort(", script)
        self.assertLess(script.index("out.sort("), script.index("slice(0, P.limit)"))

    def test_no_template_ever_deletes(self):
        for name in ("JXA_ACCOUNTS", "JXA_UNREAD", "JXA_READ", "JXA_COMPOSE", "JXA_JUNK"):
            template = getattr(mail, name).lower()
            self.assertNotIn("delete", template, name)
            self.assertNotIn("trash", template, name)


class Unsubscribing(unittest.TestCase):
    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    class FakeOpener:
        def __init__(self):
            self.requests = []

        def open(self, request, timeout=None):
            self.requests.append((request, timeout))
            return Unsubscribing.FakeResponse()

    def test_one_click_is_a_post_with_the_fixed_body(self):
        opener = self.FakeOpener()
        result = mail.unsubscribe("https://b.nl/u/1", True, opener=opener)
        request, timeout = opener.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.data, b"List-Unsubscribe=One-Click")
        self.assertEqual(timeout, 15)
        self.assertTrue(result["ok"])

    def test_plain_link_is_one_get(self):
        opener = self.FakeOpener()
        mail.unsubscribe("https://b.nl/u/1", False, opener=opener)
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(opener.requests[0][0].method, "GET")

    def test_http_and_mailto_are_refused_without_a_request(self):
        opener = self.FakeOpener()
        for url in ("http://b.nl/u", "mailto:stop@b.nl", "ftp://x"):
            result = mail.unsubscribe(url, True, opener=opener)
            self.assertFalse(result["ok"], url)
        self.assertEqual(opener.requests, [])

    def test_network_error_is_a_result_not_a_crash(self):
        class Broken:
            def open(self, *_a, **_k):
                raise OSError("no route")

        result = mail.unsubscribe("https://b.nl/u", False, opener=Broken())
        self.assertFalse(result["ok"])
        self.assertIn("no route", result["error"])


class SkillSendSection(unittest.TestCase):
    def test_the_send_section_names_no_other_path(self):
        skill = (ROOT / ".claude" / "skills" / "email-manager" / "SKILL.md").read_text(encoding="utf-8")
        section = skill.split("## Verzenden", 1)[1].split("\n## ", 1)[0]
        self.assertIn("mail.py send --draft", section)
        self.assertIn("mail.py drafts", section)
        self.assertNotIn("osascript -", section)
        self.assertNotIn(".send(", section)
        self.assertIn("HANGAR_EMAIL_SEND_OK", section)


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

    def test_drafts_lists_one_accounts_drafts_with_first_line(self):
        result = self.run_mail("drafts", "--account", "Personal Gmail", out="[]")
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn("includes('draft')", script)
        self.assertIn("includes('concept')", script)  # Dutch Mail
        self.assertIn("first_line", script)
        self.assertNotIn(".send(", script)

    def test_send_draft_rebuilds_and_sends_but_never_deletes(self):
        result = self.run_mail(
            "send", "--draft", "1007", "--account", "Personal Gmail",
            out=json.dumps({"sent": True}), send_ok=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = self.script()
        self.assertIn('"id": 1007', script)
        self.assertIn("msg.send();", script)
        self.assertIn("draft_left_in_drafts: true", script)
        self.assertIn("M.ToRecipient", script)
        for forbidden in ("delete", "trash", "Trash"):
            self.assertNotIn(forbidden, script)

    def test_send_draft_needs_the_variable_too(self):
        result = self.run_mail("send", "--draft", "1007", "--account", "Personal Gmail")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.log.exists())

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
