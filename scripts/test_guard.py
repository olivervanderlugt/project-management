#!/usr/bin/env python3
"""Tests for scripts/guard.py.

    python3 scripts/test_guard.py

Two things matter here, and the second one as much as the first: that the guard
blocks what it must, and that it lets ordinary work through. A guard that fires
on `git status` gets switched off within a day.
"""

import importlib.util
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("guard", ROOT / "scripts" / "guard.py")
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def bash(command):
    return guard.check("Bash", {"command": command})


def read(path):
    return guard.check("Read", {"file_path": path})


class Blocks(unittest.TestCase):
    def test_force_push(self):
        for command in (
            "git push --force origin night/x",
            "git push -f",
            "git push --force-with-lease origin HEAD",
        ):
            self.assertIsNotNone(bash(command), command)

    def test_push_to_main(self):
        self.assertIsNotNone(bash("git push origin main"))
        self.assertIsNotNone(bash("git push origin HEAD:master"))

    def test_branch_deletion(self):
        self.assertIsNotNone(bash("git push origin --delete night/x"))
        self.assertIsNotNone(bash("git push origin :night/x"))

    def test_history_and_state_destruction(self):
        self.assertIsNotNone(bash("git reset --hard HEAD~3"))
        self.assertIsNotNone(bash("git filter-branch --tree-filter true HEAD"))
        self.assertIsNotNone(bash("rm -rf .git"))
        self.assertIsNotNone(bash("rm -rf ~/"))

    def test_secrets(self):
        self.assertIsNotNone(bash("cat .env"))
        self.assertIsNotNone(bash("echo TOKEN=x >> .env.local"))
        self.assertIsNotNone(read("/home/user/project/.env"))
        self.assertIsNotNone(read("/home/user/.ssh/id_rsa"))
        self.assertIsNotNone(guard.check("Write", {"file_path": "config/credentials.json"}))

    def test_money_and_deploys(self):
        for command in (
            "vercel deploy --prod",
            "fly deploy",
            "npm publish",
            "docker push ghcr.io/x/y",
            "terraform apply",
            "aws s3 sync . s3://bucket",
            "stripe products create",
        ):
            self.assertIsNotNone(bash(command), command)

    def test_repo_deletion_and_visibility(self):
        self.assertIsNotNone(bash("gh repo delete olivervanderlugt/versa"))
        self.assertIsNotNone(bash("gh repo edit --visibility public"))
        self.assertIsNotNone(bash("gh api -X DELETE repos/o/r"))


    def test_scripts_that_send_mail(self):
        self.assertIsNotNone(bash("osascript -e 'tell application \"Mail\" to send newMessage'"))
        self.assertIsNotNone(bash("osascript -l JavaScript -e 'msg.send()'"))
        # multi-statement JXA, the shape mail.py itself builds
        self.assertIsNotNone(bash(
            "osascript -l JavaScript -e \"const M = Application('Mail'); const P = {}; "
            "msg.sender = from; msg.send(); JSON.stringify({sent: true});\""
        ))
        self.assertIsNotNone(bash("cd /x && osascript -e 'tell application \"Mail\"' -e 'send theMessage'"))

    def test_setting_the_send_key_inside_a_command(self):
        for command in (
            "HANGAR_EMAIL_SEND_OK=1 python3 scripts/mail.py send --account VU --to a@b.nl",
            "export HANGAR_EMAIL_SEND_OK=1",
            "env HANGAR_EMAIL_SEND_OK=1 python3 scripts/mail.py accounts",
            "sh -c 'HANGAR_EMAIL_SEND_OK=1 python3 scripts/mail.py send'",
        ):
            self.assertIsNotNone(bash(command), command)

    def test_mail_py_send_without_the_variable(self):
        os.environ.pop("HANGAR_EMAIL_SEND_OK", None)
        self.assertIsNotNone(bash("python3 scripts/mail.py send --account VU --to a@b.nl"))
        self.assertIsNotNone(bash("cd /x && python3 scripts/mail.py send --account VU"))
        self.assertIsNotNone(bash("scripts/mail.py send --account VU"))
        self.assertIsNotNone(bash("env python3 scripts/mail.py send --account VU"))
        self.assertIsNotNone(bash("python3 -u scripts/mail.py send --account VU"))
        os.environ["HANGAR_EMAIL_SEND_OK"] = "0"
        self.assertIsNotNone(bash("python3 scripts/mail.py send --account VU --to a@b.nl"))
        os.environ.pop("HANGAR_EMAIL_SEND_OK", None)


class Allows(unittest.TestCase):
    def test_ordinary_git(self):
        for command in (
            "git status --short",
            "git add -A",
            "git commit -m 'Fix the thing'",
            "git push -u origin claude/hangar-project-setup-kvhcad",
            "git push origin night/learn-live-preview",
            "git log --oneline -10",
            "git diff --stat",
            "git checkout -b night/x",
        ):
            self.assertIsNone(bash(command), command)

    def test_the_hangars_own_commands(self):
        for command in (
            "python3 dashboard/build.py",
            "python3 scripts/gen_agents.py",
            "python3 scripts/test_guard.py",
            "pnpm test",
            "npm run build",
        ):
            self.assertIsNone(bash(command), command)

    def test_example_env_is_not_a_secret(self):
        self.assertIsNone(bash("cp .env.example .env.sample"))
        self.assertIsNone(read("/repo/.env.example"))

    def test_reading_and_drafting_mail(self):
        for command in (
            "osascript -e 'tell application \"Mail\" to get name of every account'",
            "osascript -e 'tell application \"Mail\" to get subject of first message of inbox'",
            "osascript -l JavaScript -e 'm.sender()'",  # 'sender' is not 'send'
            "python3 scripts/mail.py accounts",
            "python3 scripts/mail.py unread --account VU",
            "python3 scripts/mail.py draft --account VU --to a@b.nl --subject S --body x",
            "python3 scripts/mail.py junk 12",
            "python3 scripts/test_mail.py",
        ):
            self.assertIsNone(bash(command), command)

    def test_mentioning_send_in_a_commit_message_is_not_sending(self):
        self.assertIsNone(bash("git commit -m 'Guard blocks osascript scripts that send and mail.py send'"))
        self.assertIsNone(bash("grep -n 'mail.py send' tasks/email-4-verzenden-met-toestemming.md"))
        self.assertIsNone(bash("git commit -m 'Guard: block osascript send; mail.py send too' && git push"))
        self.assertIsNone(bash("osascript -l JavaScript /tmp/send.js"))
        self.assertIsNone(bash("osascript -l JavaScript -e 'const s = m.sender(); JSON.stringify(s)'"))

    def test_mail_py_send_with_the_variable_in_ollies_shell(self):
        os.environ["HANGAR_EMAIL_SEND_OK"] = "1"
        try:
            self.assertIsNone(bash("python3 scripts/mail.py send --account VU --to a@b.nl"))
        finally:
            os.environ.pop("HANGAR_EMAIL_SEND_OK", None)

    def test_a_branch_called_maintenance_is_not_main(self):
        self.assertIsNone(bash("git push origin maintenance-branch"))

    def test_other_tools_pass_through(self):
        self.assertIsNone(guard.check("Glob", {"pattern": "**/*.ts"}))
        self.assertIsNone(guard.check("Read", {"file_path": "projects/versa.md"}))


class Failsafe(unittest.TestCase):
    def test_unknown_shape_does_not_block(self):
        self.assertIsNone(guard.check("Bash", {}))
        self.assertIsNone(guard.check("Read", {}))


if __name__ == "__main__":
    unittest.main()
