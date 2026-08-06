#!/usr/bin/env python3
"""PreToolUse guard: refuse the handful of things that cannot be undone.

Wired in .claude/settings.json as a `command` hook, so it costs zero tokens —
the same reasoning as scripts/autosave.sh. A prompt rule is a request; this is
a wall, and it holds for every agent in the repo including the ones generated
into .claude/agents/.

Reads the hook payload on stdin, exits 0 to allow and 2 to block. Exit 2 sends
the message on stderr back to the model, which then knows why and can pick
another route.

What it refuses, and why each one is here:

    force pushes, deletes, resets      history you cannot get back
    pushes to main/master              the branch nobody agreed to touch
    secrets                            reading one is enough to leak it
    deploys and paid CLIs              spends money with no human awake
    repo deletion and visibility flips public is a one-way door

Deliberately NOT here: ordinary git, tests, builds, file edits. A guard that
fires on safe work gets switched off, and a guard that is off protects nothing.
"""

import json
import re
import sys

# (regex over the command, reason shown to the model)
BASH_RULES = [
    (r"\bgit\s+push\b[^|;&]*(--force\b|--force-with-lease\b|\s-f\b)",
     "force push: rewrites history someone else may already have"),
    (r"\bgit\s+push\b[^|;&]*\b(main|master)\b",
     "push to main: work goes to its own branch and a PR"),
    (r"\bgit\s+push\b[^|;&]*(--delete\b|--mirror\b|\s:\S)",
     "deleting or mirroring a remote branch"),
    (r"\bgit\s+reset\b[^|;&]*--hard",
     "git reset --hard: throws away work that was never committed"),
    (r"\bgit\s+filter-(branch|repo)\b",
     "rewriting history"),
    (r"\bgh\s+repo\s+delete\b|\bgh\s+api\b[^|;&]*-X\s*DELETE",
     "deleting a repository or resource over the API"),
    (r"\bgh\s+repo\s+edit\b[^|;&]*--visibility",
     "changing repository visibility: public is a one-way door"),
    (r"\b(vercel|netlify|fly|flyctl|railway|heroku|supabase|wrangler)\b[^|;&]*\b(deploy|up|launch|publish|create)\b",
     "deploying: costs money and nobody is awake to watch it"),
    (r"\bnpm\s+publish\b|\bdocker\s+push\b|\bterraform\s+(apply|destroy)\b",
     "publishing or applying infrastructure"),
    (r"\b(aws|gcloud|az|stripe)\s+\w",
     "cloud or billing CLI: assume it costs money"),
    (r"\brm\b[^|;&]*-[a-zA-Z]*r[a-zA-Z]*\s+(/|~|\$HOME)(\s|/|$)",
     "recursive delete outside the project"),
    (r"\brm\b[^|;&]*\s\.git(\s|/|$)",
     "deleting the .git directory"),
]

# Secrets: matched against both commands and file paths.
SECRET = re.compile(
    r"(\.env\b(?!\.example|\.sample|\.template)"
    r"|\bid_rsa\b|\bid_ed25519\b|\.pem\b|\.p12\b|\.key\b"
    r"|\.git-credentials\b|\bcredentials\.json\b|\.npmrc\b"
    r"|\bsecrets?\.(json|ya?ml|toml|env)\b)",
    re.IGNORECASE,
)

FILE_TOOLS = {"Read", "Edit", "MultiEdit", "Write", "NotebookEdit"}


def check(tool, payload):
    """The reason to block, or None to allow."""
    if tool == "Bash":
        command = " ".join((payload.get("command") or "").split())
        if SECRET.search(command):
            return "secrets: not read, not written, not printed"
        for pattern, reason in BASH_RULES:
            if re.search(pattern, command, re.IGNORECASE):
                return reason
        return None

    if tool in FILE_TOOLS:
        path = payload.get("file_path") or payload.get("notebook_path") or ""
        if SECRET.search(path):
            return "secrets: not read, not written, not printed"
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # A guard that crashes must not become a guard that blocks everything.
        return 0

    reason = check(event.get("tool_name", ""), event.get("tool_input") or {})
    if reason is None:
        return 0

    print(
        f"Blocked by scripts/guard.py — {reason}. "
        "This is a hard boundary in the Hangar, not a preference: "
        "find another route or write down what you cannot do.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
