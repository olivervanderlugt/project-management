#!/usr/bin/env python3
"""Fill email/accounts/*.md from Mail on the Mac, then ask Ollie the rest.

    python3 scripts/mail_profiles.py            # addresses from Mail, then questions
    python3 scripts/mail_profiles.py --yes      # addresses from Mail, all defaults, no questions
    python3 scripts/mail_profiles.py --from-json accounts.json   # same, from a saved `mail.py accounts`

One profile per account Mail knows, keyed on `mail_account:` (exact name,
trailing spaces included). Existing profiles keep their body and any field
that is already filled; only blanks get asked. Every question shows its
default in brackets — Enter accepts it. Nothing here touches a password.

Provider is guessed from the address domain and only asked when the guess is
`other`. Priority, language, tone, auto-unsubscribe and never-spam are
Ollie's calls, so they are asked, with defaults that match how he works.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS = ROOT / "email" / "accounts"
MAIL = ROOT / "scripts" / "mail.py"

FIELDS = [
    "address", "provider", "mail_account", "junk_mailbox", "priority",
    "language", "tone", "auto_unsubscribe", "never_spam", "tested",
]

DOMAINS = {
    "gmail": ("gmail.com", "googlemail.com"),
    "icloud": ("icloud.com", "me.com", "mac.com"),
    "outlook": ("outlook.com", "outlook.nl", "hotmail.com", "hotmail.nl", "live.com", "live.nl", "msn.com"),
    "vu": ("vu.nl", "student.vu.nl"),
    "uva": ("uva.nl", "student.uva.nl"),
    "mailcom": ("mail.com",),
}

JUNK_BY_PROVIDER = {"vu": "Junk Email", "uva": "Junk Email", "outlook": "Junk Email"}

QUESTIONS = [
    ("priority", "prioriteit 1-3 (1 = prominent)", "2"),
    ("language", "taal nl / en / both", "nl"),
    ("tone", "toon, een paar woorden", "kort en direct"),
    ("auto_unsubscribe", "nieuwsbrieven automatisch afmelden y/n", "y"),
    ("never_spam", "afzenders die nooit spam zijn, komma-gescheiden", ""),
]


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def guess_provider(address):
    domain = address.rsplit("@", 1)[-1].lower() if "@" in address else ""
    for provider, domains in DOMAINS.items():
        if domain in domains or any(domain.endswith("." + d) for d in domains):
            return provider
    return "other"


def parse(text):
    """Flat frontmatter -> (dict, body). Same contract as build.py: no nesting."""
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not match:
        return {}, text
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.split("#", 1)[0].strip() if key.strip() != "tone" else value.strip()
    return fields, match.group(2)


def render(fields, body):
    width = max(len(k) for k in FIELDS) + 1
    lines = [f"{k}:".ljust(width + 1) + fields.get(k, "") for k in FIELDS]
    return "---\n" + "\n".join(l.rstrip() for l in lines) + "\n---\n" + body


def accounts_from_mail():
    result = subprocess.run(
        [sys.executable, str(MAIL), "accounts"], capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(f"mail.py accounts failed:\n{result.stderr}")
    return json.loads(result.stdout)


def load_profiles(directory):
    """mail_account -> (path, fields, body) for every non-template profile."""
    table = {}
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        fields, body = parse(path.read_text(encoding="utf-8"))
        table[fields.get("mail_account", path.stem).strip()] = (path, fields, body)
    return table


def ask(prompt, default, reader=input):
    shown = f" [{default}]" if default else ""
    answer = reader(f"  {prompt}{shown}: ").strip()
    return answer or default


def fill(accounts, directory, yes=False, reader=input, out=print):
    """Write one profile per Mail account. Returns the list of paths written."""
    directory.mkdir(parents=True, exist_ok=True)
    existing = load_profiles(directory)
    written = []
    today = date.today().isoformat()

    for account in accounts:
        # Mail allows a trailing space in an account name; flat frontmatter
        # cannot keep one, so profiles store the trimmed name and mail.py
        # resolves accounts by trimmed name too.
        name = account["name"].strip()
        addresses = [a for a in account.get("addresses", []) if a]
        address = addresses[0] if addresses else ""
        if name in existing:
            path, fields, body = existing[name]
        else:
            path = directory / f"{slug(name)}.md"
            fields, body = {}, "\n## Wat hier binnenkomt\n\nNog niet ingevuld.\n"
        fields["mail_account"] = name

        if address:
            fields["address"] = address
        if not fields.get("provider"):
            fields["provider"] = guess_provider(address)
        if not fields.get("junk_mailbox"):
            fields["junk_mailbox"] = JUNK_BY_PROVIDER.get(fields["provider"], "Junk")
        fields["tested"] = fields.get("tested") or today

        out(f"\n{name.strip()}  <{address or 'geen adres in Mail'}>  provider: {fields['provider']}")
        if len(addresses) > 1:
            out(f"  ook: {', '.join(addresses[1:])}")
        if fields["provider"] == "other" and not yes:
            fields["provider"] = ask("provider (gmail/icloud/outlook/vu/uva/mailcom/other)", "other", reader)
        for key, prompt, default in QUESTIONS:
            if fields.get(key):
                continue
            fields[key] = default if yes else ask(prompt, default, reader)
        if fields.get("auto_unsubscribe") in ("y", "yes", "ja"):
            fields["auto_unsubscribe"] = "yes"
        elif fields.get("auto_unsubscribe") in ("n", "no", "nee"):
            fields["auto_unsubscribe"] = "no"

        path.write_text(render(fields, body), encoding="utf-8")
        written.append(path)
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--yes", action="store_true", help="accept every default, ask nothing")
    parser.add_argument("--from-json", help="read accounts from this file instead of Mail")
    parser.add_argument("--dir", default=str(ACCOUNTS), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as handle:
            accounts = json.load(handle)
    else:
        accounts = accounts_from_mail()

    print(f"{len(accounts)} accounts in Mail. Enter = default; wat al ingevuld is wordt niet gevraagd.")
    written = fill(accounts, Path(args.dir), yes=args.yes)
    print(f"\n{len(written)} profielen geschreven in {Path(args.dir).relative_to(ROOT) if Path(args.dir).is_relative_to(ROOT) else args.dir}.")
    print("Dan: git add email/accounts && git commit -m 'Vul e-mailprofielen' && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
