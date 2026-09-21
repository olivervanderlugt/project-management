#!/usr/bin/env python3
"""Talk to Mail on Ollie's Mac. Read, draft, junk — never send.

    python3 scripts/mail.py accounts
    python3 scripts/mail.py unread --account "VU" --since 2026-09-21T07:00:00
    python3 scripts/mail.py read 12345
    python3 scripts/mail.py draft --account "VU" --to x@y.nl --subject "Re: …" --body-file draft.txt
    python3 scripts/mail.py draft --account "VU" --reply-to 12345 --body-file draft.txt
    python3 scripts/mail.py junk 12345 --account "VU" [--mailbox "Junk"]
    python3 scripts/mail.py unsubscribe --url https://… [--one-click]
    python3 scripts/mail.py drafts --account "VU"

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

Data — profiles, state, log, briefings, context — lives in ~/.hangar-mail
(or HANGAR_MAIL_DIR), never in this public repo. See decision 0008.

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

# Drafts of one account: id, recipients, subject and the first line of the
# body — what Ollie needs read back to him before he says "verstuur".
JXA_DRAFTS = JXA_FIND + """
const M = Application('Mail'); const P = %(params)s;
const acc = findAccount(M, P.account); const out = [];
for (const mb of acc.mailboxes()) {
  const n = mb.name().toLowerCase();
  if (!(n.includes('draft') || n.includes('concept'))) continue;
  for (const m of mb.messages()) {
    const body = (m.content() || '').split('\\n')[0];
    out.push({id: m.id(), mailbox: mb.name(), subject: m.subject(),
              to: m.toRecipients().map(r => r.address()),
              date: m.dateSent() ? m.dateSent().toISOString() : null, first_line: body});
    if (out.length >= P.limit) break;
  }
}
JSON.stringify(out);
"""

# Send one existing draft. Mail cannot send a saved draft as such, so this
# rebuilds an outgoing message from it and sends that. The draft itself is
# left where it is — nothing here deletes — and the result says so.
JXA_SEND_DRAFT = JXA_FIND + """
const M = Application('Mail'); const P = %(params)s;
const acc = findAccount(M, P.account);
let draft = null;
for (const mb of acc.mailboxes()) {
  const n = mb.name().toLowerCase();
  if (!(n.includes('draft') || n.includes('concept'))) continue;
  const hits = mb.messages.whose({id: P.id})();
  if (hits.length) { draft = hits[0]; break; }
}
if (!draft) throw new Error('no draft ' + P.id + ' in the drafts of ' + P.account);
const from = acc.fullName() + ' <' + acc.emailAddresses()[0] + '>';
const msg = M.OutgoingMessage({subject: draft.subject(), content: draft.content(), visible: false});
M.outgoingMessages.push(msg);
for (const r of draft.toRecipients()) msg.toRecipients.push(M.ToRecipient({address: r.address()}));
for (const r of draft.ccRecipients()) msg.ccRecipients.push(M.CcRecipient({address: r.address()}));
msg.sender = from;
msg.send();
JSON.stringify({sent: true, draft_id: P.id, account: acc.name(), sender: from,
  subject: draft.subject(), to: draft.toRecipients().map(r => r.address()),
  draft_left_in_drafts: true});
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


def data_dir():
    """Where mail data lives: profiles, state, log, briefings, context.

    Outside the repo on purpose — the Hangar is public (decision 0008).
    HANGAR_MAIL_DIR overrides; default ~/.hangar-mail.
    """
    return os.environ.get("HANGAR_MAIL_DIR") or os.path.expanduser("~/.hangar-mail")


def junk_mailbox_from_profile(account):
    """The `junk_mailbox:` line of <data_dir>/accounts/<slug>.md for this account, or None."""
    directory = os.path.join(data_dir(), "accounts")
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
    if getattr(args, "draft", None) is not None:
        sys.exit("mail.py: --draft belongs to send, not draft")
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


def cmd_drafts(args):
    script = JXA_DRAFTS % {"params": params(account=args.account, limit=args.limit)}
    emit(run_jxa(script))


def cmd_send(args):
    # Only reachable when HANGAR_EMAIL_SEND_OK=1: the subparser is not even
    # registered otherwise. The skill's own rule on top of this: one mail,
    # one explicit "verstuur <id>" from Ollie, read back first. See email-4.
    if args.draft is not None:
        script = JXA_SEND_DRAFT % {"params": params(account=args.account, id=args.draft)}
        emit(run_jxa(script))
        return
    _compose(args, "msg.send();", "sent")


def unsubscribe(url, one_click, opener=None):
    """One bounded request to a List-Unsubscribe URL. Returns a dict, never raises.

    Only https, only the URL from the header (the skill enforces that part),
    one request, no cookies, no body links, 15 seconds. One-click is the
    RFC 8058 POST with the fixed body; otherwise a plain GET.
    """
    import urllib.request
    if not url.lower().startswith("https://"):
        return {"ok": False, "url": url, "error": "only https URLs from the List-Unsubscribe header"}
    data = b"List-Unsubscribe=One-Click" if one_click else None
    request = urllib.request.Request(
        url, data=data, method="POST" if one_click else "GET",
        headers={"User-Agent": "Hangar email-manager", "Content-Type": "application/x-www-form-urlencoded"},
    )
    opener = opener or urllib.request.build_opener()  # fresh: no cookies, no auth
    try:
        with opener.open(request, timeout=15) as response:
            return {"ok": 200 <= response.status < 400, "url": url,
                    "status": response.status, "method": request.method}
    except Exception as error:  # noqa: BLE001 — one line in the log, not a crash
        return {"ok": False, "url": url, "method": request.method, "error": str(error)[:200]}


def cmd_unsubscribe(args):
    result = unsubscribe(args.url, args.one_click)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


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

    drafts = sub.add_parser("drafts", help="drafts of one account, with first line — to read back before a send")
    drafts.add_argument("--account", required=True, help="exact account name as Mail shows it")
    drafts.add_argument("--limit", type=int, default=20)

    unsub = sub.add_parser("unsubscribe", help="one https request to a List-Unsubscribe URL; never a mail")
    unsub.add_argument("--url", required=True, help="the https URL from the List-Unsubscribe header")
    unsub.add_argument("--one-click", action="store_true", help="RFC 8058 POST instead of GET")

    if SEND_OK:
        send = sub.add_parser("send", help="send — only with HANGAR_EMAIL_SEND_OK=1 and Ollie's explicit go")
        compose_args(send)
        send.add_argument("--draft", type=int, help="send this existing draft (the email-4 path); other flags then ignored")

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
    result = {
        "accounts": cmd_accounts,
        "unread": cmd_unread,
        "read": cmd_read,
        "draft": cmd_draft,
        "junk": cmd_junk,
        "drafts": cmd_drafts,
        "unsubscribe": cmd_unsubscribe,
        "send": cmd_send,
    }[args.command](args)
    return result or 0


if __name__ == "__main__":
    sys.exit(main())
