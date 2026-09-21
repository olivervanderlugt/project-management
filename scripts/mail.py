#!/usr/bin/env python3
"""Talk to Mail on Ollie's Mac. Read, draft, junk — never send.

    python3 scripts/mail.py accounts
    python3 scripts/mail.py unread --account "VU" --since 2026-09-21T07:00:00
    python3 scripts/mail.py read 12345
    python3 scripts/mail.py draft --account "VU" --to x@y.nl --subject "Re: …" --body-file draft.txt
    python3 scripts/mail.py draft --account "VU" --reply-to 12345 --body-file draft.txt
    python3 scripts/mail.py junk 12345 [--mailbox "Junk"]

Every subcommand prints one JSON value on stdout. Mail is driven through JXA
(`osascript -l JavaScript`), which returns dates as ISO strings and lets the
script hand back JSON without AppleScript delimiter tricks. Mail is already
logged in to every account, so there is not a single password in here.

What this script cannot do, on purpose: `send` does not exist unless
HANGAR_EMAIL_SEND_OK=1 is in the environment, and that variable lives in
Ollie's own shell — never in the repo, never in a launchd plist. `junk` moves
a message to the account's junk mailbox and nothing here ever deletes; the
words `delete` and `trash` do not appear in any script this file builds.
See decisions/0007.

Message ids are Mail's own integer ids. `read`, `junk` and `--reply-to` look
in the unified inbox, which spans every account.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

SEND_OK = os.environ.get("HANGAR_EMAIL_SEND_OK") == "1"

# --- JXA templates ---------------------------------------------------------
# Each takes a JSON object P and prints one JSON value.

JXA_ACCOUNTS = """
const M = Application('Mail');
JSON.stringify(M.accounts().map(a => ({
  name: a.name(), addresses: a.emailAddresses(), enabled: a.enabled()
})));
"""

JXA_UNREAD = """
const M = Application('Mail'); const P = %(params)s;
const since = new Date(P.since); const out = [];
const msgs = M.inbox.messages.whose({readStatus: false})();
for (const m of msgs) {
  const d = m.dateReceived(); if (d < since) continue;
  const an = m.mailbox().account().name();
  if (P.account && an !== P.account) continue;
  out.push({id: m.id(), account: an, subject: m.subject(), from: m.sender(),
            date: d.toISOString()});
  if (out.length >= P.limit) break;
}
JSON.stringify(out);
"""

JXA_READ = """
const M = Application('Mail'); const P = %(params)s;
const m = M.inbox.messages.byId(P.id);
JSON.stringify({id: m.id(), account: m.mailbox().account().name(),
  subject: m.subject(), from: m.sender(),
  to: m.toRecipients().map(r => r.address()),
  date: m.dateReceived().toISOString(), headers: m.allHeaders(),
  content: m.content()});
"""

# Build an outgoing message, then either save it (draft) or send it. The
# sender line is what tells Mail which account the draft belongs to.
JXA_COMPOSE = """
const M = Application('Mail'); const P = %(params)s;
const acc = M.accounts.byName(P.account);
const from = acc.fullName() + ' <' + acc.emailAddresses()[0] + '>';
let msg;
if (P.replyTo) {
  const orig = M.inbox.messages.byId(P.replyTo);
  msg = M.reply(orig, {openingWindow: false});
  msg.content = P.body + '\\n\\n' + msg.content();
} else {
  msg = M.OutgoingMessage({subject: P.subject, content: P.body, visible: false});
  M.outgoingMessages.push(msg);
  for (const t of P.to) msg.toRecipients.push(M.Recipient({address: t}));
}
msg.sender = from;
%(action)s
JSON.stringify({%(result)s: true, account: P.account, sender: from,
  subject: msg.subject(), to: msg.toRecipients().map(r => r.address())});
"""

JXA_JUNK = """
const M = Application('Mail'); const P = %(params)s;
const m = M.inbox.messages.byId(P.id);
const acc = m.mailbox().account();
let target = null;
try { target = acc.mailboxes.byName(P.mailbox); target.name(); } catch (e) { target = null; }
if (target) { M.move(m, {to: target}); } else { m.junkMailStatus = true; }
JSON.stringify({id: P.id, account: acc.name(), moved: !!target,
  flagged: !target, mailbox: target ? P.mailbox : null});
"""


def run_jxa(script):
    """Run one JXA script through osascript and return its stdout."""
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode or 1)
    return result.stdout.strip()


def emit(text):
    """Parse the JXA output as JSON and print it neatly. Fail loudly if not."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        sys.stderr.write(f"mail.py: osascript did not return JSON:\n{text}\n")
        sys.exit(1)
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return value


def params(**kw):
    return json.dumps(kw, ensure_ascii=False)


# --- header parsing --------------------------------------------------------

def unsubscribe_from_headers(headers):
    """Read List-Unsubscribe out of a raw header block.

    Returns {'http': [...], 'mailto': [...], 'one_click': bool}. Only the
    https URLs are ever followed by the skill, and only when one_click is
    true or the profile allows it; a mailto entry is a mail, so it becomes a
    draft (decision 0007 rule 4).
    """
    unfolded = re.sub(r"\r?\n[ \t]+", " ", headers or "")
    http, mailto = [], []
    for line in unfolded.splitlines():
        if line.lower().startswith("list-unsubscribe:"):
            for target in re.findall(r"<([^>]+)>", line):
                if target.lower().startswith("https://"):
                    http.append(target)
                elif target.lower().startswith("mailto:"):
                    mailto.append(target)
    one_click = any(
        line.lower().startswith("list-unsubscribe-post:")
        and "one-click" in line.lower()
        for line in unfolded.splitlines()
    )
    return {"http": http, "mailto": mailto, "one_click": one_click}


# --- subcommands -----------------------------------------------------------

def cmd_accounts(_args):
    emit(run_jxa(JXA_ACCOUNTS))


def cmd_unread(args):
    since = args.since or (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    script = JXA_UNREAD % {"params": params(account=args.account, since=since, limit=args.limit)}
    emit(run_jxa(script))


def cmd_read(args):
    script = JXA_READ % {"params": params(id=args.id)}
    try:
        message = json.loads(run_jxa(script))
    except json.JSONDecodeError:
        sys.exit("mail.py: osascript did not return JSON")
    message["unsubscribe"] = unsubscribe_from_headers(message.get("headers", ""))
    print(json.dumps(message, ensure_ascii=False, indent=2))


def _body(args):
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as handle:
            return handle.read()
    return args.body or ""


def _compose(args, action, result):
    if not args.reply_to and not (args.to and args.subject):
        sys.exit("mail.py: a new message needs --to and --subject; a reply needs --reply-to")
    script = JXA_COMPOSE % {
        "params": params(account=args.account, to=args.to or [], subject=args.subject or "",
                         body=_body(args), replyTo=args.reply_to),
        "action": action,
        "result": result,
    }
    emit(run_jxa(script))


def cmd_draft(args):
    _compose(args, "msg.save();", "saved")


def cmd_send(args):
    # Only reachable when HANGAR_EMAIL_SEND_OK=1: the subparser is not even
    # registered otherwise. The skill's own rule on top of this: one mail,
    # one explicit "verstuur <id>" from Ollie, read back first. See email-4.
    _compose(args, "msg.send();", "sent")


def cmd_junk(args):
    script = JXA_JUNK % {"params": params(id=args.id, mailbox=args.mailbox)}
    emit(run_jxa(script))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mail.py",
        description="Read, draft and junk mail through Mail on the Mac. Never sends.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("accounts", help="every account Mail knows, with addresses")

    unread = sub.add_parser("unread", help="unread inbox messages, newest first")
    unread.add_argument("--account", help="exact account name as Mail shows it")
    unread.add_argument("--since", help="ISO timestamp; default 24 hours ago")
    unread.add_argument("--limit", type=int, default=50)

    read = sub.add_parser("read", help="one message with headers and text")
    read.add_argument("id", type=int)

    def compose_args(p):
        p.add_argument("--account", required=True, help="exact account name as Mail shows it")
        p.add_argument("--to", action="append", help="recipient; repeatable")
        p.add_argument("--subject")
        p.add_argument("--reply-to", type=int, help="message id to reply to")
        p.add_argument("--body", help="plain text body")
        p.add_argument("--body-file", help="read the body from this file")

    draft = sub.add_parser("draft", help="save a draft in that account's Drafts mailbox")
    compose_args(draft)

    junk = sub.add_parser("junk", help="move a message to the account's junk mailbox")
    junk.add_argument("id", type=int)
    junk.add_argument("--mailbox", default="Junk", help="junk mailbox name for this account")

    if SEND_OK:
        send = sub.add_parser("send", help="send — only with HANGAR_EMAIL_SEND_OK=1 and Ollie's explicit go")
        compose_args(send)

    return parser


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "send" and not SEND_OK:
        sys.stderr.write(
            "mail.py: `send` is not available. Sending needs HANGAR_EMAIL_SEND_OK=1 in "
            "Ollie's own shell and his explicit go per mail (decisions/0007, tasks/email-4).\n"
        )
        return 2
    args = build_parser().parse_args(argv)
    {
        "accounts": cmd_accounts,
        "unread": cmd_unread,
        "read": cmd_read,
        "draft": cmd_draft,
        "junk": cmd_junk,
        "send": cmd_send,
    }[args.command](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
