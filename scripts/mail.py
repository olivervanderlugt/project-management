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

Message ids are Mail's own integer ids, unique per mailbox — so `read`,
`junk` and `--reply-to` take `--account` and look in that account's inbox.
Without `--account`, `read` falls back to the unified inbox and takes the
first match. `unread` prints the account with every id for exactly this
reason.

Unverified until the first run on the Mac (tasks/email-0): whether Mail
accepts the compose idiom used here (`OutgoingMessage` + `save` + `close`
saving), and the junk mailbox names. Both are the kind of thing the tests
cannot see from Linux.
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
  if (P.account && an.trim() !== P.account.trim()) continue;
  out.push({id: m.id(), account: an, subject: m.subject(), from: m.sender(),
            date: d.toISOString()});
}
out.sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
JSON.stringify(out.slice(0, P.limit));
"""

# Find one message by id. Ids are unique per mailbox, so with an account
# name the search is that account's inbox; without one, the unified inbox.
JXA_FIND = """
// Exact name first; then trimmed, because Mail lets an account name end in a
// space ("Wandarbear ") and flat frontmatter cannot keep one.
function findAccount(M, name) {
  try { const a = M.accounts.byName(name); a.name(); return a; } catch (e) {}
  const hit = M.accounts().find(a => a.name().trim() === name.trim());
  if (!hit) throw new Error('no account named ' + JSON.stringify(name));
  return hit;
}
function findMessage(M, P) {
  if (P.account) {
    const acc = findAccount(M, P.account);
    for (const mb of acc.mailboxes()) {
      const n = mb.name().toLowerCase();
      if (n !== 'inbox') continue;
      const hits = mb.messages.whose({id: P.id})();
      if (hits.length) return hits[0];
    }
    throw new Error('no message ' + P.id + ' in the inbox of ' + P.account);
  }
  return M.inbox.messages.byId(P.id);
}
"""

JXA_READ = JXA_FIND + """
const M = Application('Mail'); const P = %(params)s;
const m = findMessage(M, P);
JSON.stringify({id: m.id(), account: m.mailbox().account().name(),
  subject: m.subject(), from: m.sender(),
  to: m.toRecipients().map(r => r.address()),
  date: m.dateReceived().toISOString(), headers: m.allHeaders(),
  content: m.content()});
"""

# Build an outgoing message, then either save it (draft) or send it. For a
# new message the sender line tells Mail which account the draft belongs
# to. A reply is already bound to the account that received the original,
# so its sender is left to Mail and reported back.
JXA_COMPOSE = JXA_FIND + """
const M = Application('Mail'); const P = %(params)s;
const acc = findAccount(M, P.account);
const from = acc.fullName() + ' <' + acc.emailAddresses()[0] + '>';
let msg;
if (P.replyTo) {
  const orig = findMessage(M, P);
  msg = M.reply(orig, {openingWindow: false});
  msg.content = P.body + '\\n\\n' + msg.content();
} else {
  msg = M.OutgoingMessage({subject: P.subject, content: P.body, visible: false});
  M.outgoingMessages.push(msg);
  for (const t of P.to) msg.toRecipients.push(M.ToRecipient({address: t}));
  msg.sender = from;
}
%(action)s
JSON.stringify({%(result)s: true, account: P.account, sender: msg.sender(),
  subject: msg.subject(), to: msg.toRecipients().map(r => r.address())});
"""

# Try the junk mailbox names in order (profile first, then the usual
# suspects). If none exists, flag the message as junk in place and say so.
JXA_JUNK = JXA_FIND + """
const M = Application('Mail'); const P = %(params)s;
const m = findMessage(M, P);
const acc = m.mailbox().account();
const names = acc.mailboxes().map(mb => mb.name());
let target = null;
for (const want of P.candidates) {
  const hit = names.find(n => n.toLowerCase() === want.toLowerCase());
  if (hit) { target = acc.mailboxes.byName(hit); break; }
}
if (target) { M.move(m, {to: target}); } else { m.junkMailStatus = true; }
JSON.stringify({id: P.id, account: acc.name(), moved: !!target,
  flagged: !target, mailbox: target ? target.name() : null, tried: P.candidates});
"""

JUNK_FALLBACKS = ["Junk", "Junk Email", "Junk E-mail", "Ongewenste e-mail", "Ongewenst", "Spam"]


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


def junk_mailbox_from_profile(account):
    """The `junk_mailbox:` line of email/accounts/<slug>.md for this account, or None."""
    directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "email", "accounts")
    if not os.path.isdir(directory):
        return None
    for name in sorted(os.listdir(directory)):
        if name.startswith("_") or not name.endswith(".md"):
            continue
        with open(os.path.join(directory, name), encoding="utf-8") as handle:
            fields = {}
            for line in handle:
                if line.strip() == "---" and fields:
                    break
                key, sep, value = line.partition(":")
                if sep:
                    fields[key.strip()] = value.split("#", 1)[0].strip()
        if fields.get("mail_account", "") == (account or "").strip():
            value = fields.get("junk_mailbox", "").strip()
            return value or None
    return None


def cmd_read(args):
    script = JXA_READ % {"params": params(id=args.id, account=args.account)}
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
                         body=_body(args), replyTo=args.reply_to, id=args.reply_to),
        "action": action,
        "result": result,
    }
    emit(run_jxa(script))


def cmd_draft(args):
    # save() writes the draft; close saving 'yes' is the belt to that brace —
    # on some Mail versions only the close makes the draft appear in Drafts.
    _compose(args, "msg.save(); try { msg.close({saving: 'yes'}); } catch (e) {}", "saved")


def cmd_send(args):
    # Only reachable when HANGAR_EMAIL_SEND_OK=1: the subparser is not even
    # registered otherwise. The skill's own rule on top of this: one mail,
    # one explicit "verstuur <id>" from Ollie, read back first. See email-4.
    _compose(args, "msg.send();", "sent")


def cmd_junk(args):
    candidates = []
    for name in (args.mailbox, junk_mailbox_from_profile(args.account), *JUNK_FALLBACKS):
        if name and name not in candidates:
            candidates.append(name)
    script = JXA_JUNK % {"params": params(id=args.id, account=args.account, candidates=candidates)}
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
    read.add_argument("--account", help="exact account name; ids are only unique per mailbox")

    def compose_args(p):
        p.add_argument("--account", required=True, help="exact account name as Mail shows it")
        p.add_argument("--to", action="append", help="recipient; repeatable")
        p.add_argument("--subject")
        p.add_argument("--reply-to", type=int, help="message id to reply to")
        p.add_argument("--body", help="plain text body")
        p.add_argument("--body-file", help="read the body from this file")

    draft = sub.add_parser("draft", help="save a draft in that account's Drafts mailbox")
    compose_args(draft)

    junk = sub.add_parser("junk", help="move a message to the account's junk mailbox, never delete")
    junk.add_argument("id", type=int)
    junk.add_argument("--account", required=True, help="exact account name as Mail shows it")
    junk.add_argument("--mailbox", help="junk mailbox name; default from the profile, then the usual names")

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
