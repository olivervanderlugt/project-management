#!/usr/bin/env python3
"""SessionStart hook: say so if this clone is behind origin's default branch.

Wired in `.claude/settings.json` as a `command` hook on `SessionStart`, so it
costs no tool call and no model turn — same reasoning as `guard.py` and
`autosave.sh`. It speaks by printing `hookSpecificOutput.additionalContext`,
which lands in the new session's context as plain text.

This exists because of the 2026-08-14 incident (see
`tasks/hangar-stale-clone-guard.md`): a session read a week-old clone, saw
`git status` clean, and dispatched agents to build tasks that were already
built and merged. Nothing in the working tree signals staleness — you have to
ask the remote.

Fail-safe by design, matching `autosave.sh`'s rule ("anything unexpected exits
0"): no remote, no upstream, a detached HEAD, an unreachable network, or a
slow network all produce silence, never an exception and never a hang. Only
"origin's default branch has commits this HEAD doesn't" produces output.

    python3 scripts/staleness.py

also runs standalone — reads no stdin when none is piped (so it never blocks
waiting for a terminal), defaults to the current directory, and prints the
same hook JSON to stdout when the clone is behind, nothing otherwise.
"""

import json
import os
import subprocess
import sys

# Hard cap per network round-trip. Two of these run in sequence (discover the
# default branch, then fetch it), so worst case is roughly double this — kept
# well under the hook's own `timeout` in settings.json (the backstop for a
# hang this script itself failed to catch) rather than sized to match it.
NETWORK_TIMEOUT = 3


def _run(argv, cwd, timeout=None):
    try:
        return subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None


def _git(args, cwd, timeout=None):
    """Trimmed stdout of a git command, or None if it failed/timed out."""
    result = _run(["git", *args], cwd, timeout=timeout)
    if result is None or result.returncode != 0:
        return None
    return result.stdout.strip()


def _default_branch(cwd, timeout):
    """Origin's default branch name, via a symref lookup — no object transfer."""
    symref = _git(["ls-remote", "--symref", "origin", "HEAD"], cwd, timeout=timeout)
    if not symref:
        return None
    for line in symref.splitlines():
        line = line.strip()
        if line.startswith("ref:") and line.endswith("HEAD"):
            ref = line[len("ref:"):].rsplit("\t", 1)[0].strip()
            if ref.startswith("refs/heads/"):
                return ref[len("refs/heads/"):]
    return None


def check_staleness(cwd, network_timeout=NETWORK_TIMEOUT):
    """None if there's nothing to say, else a message for additionalContext."""
    if _git(["rev-parse", "--show-toplevel"], cwd) is None:
        return None  # not a git repo (or git itself is unavailable)

    head_branch = _git(["symbolic-ref", "--quiet", "--short", "HEAD"], cwd)
    if not head_branch:
        return None  # detached HEAD

    if _git(["remote", "get-url", "origin"], cwd) is None:
        return None  # no origin remote configured

    default_branch = _default_branch(cwd, network_timeout)
    if not default_branch:
        return None  # offline, timed out, or the remote gave nothing usable

    if _git(["fetch", "origin", default_branch, "--quiet"], cwd, timeout=network_timeout) is None:
        return None  # offline, timed out, or the fetch itself failed

    remote_ref = f"origin/{default_branch}"
    count_str = _git(["rev-list", "--count", f"HEAD..{remote_ref}"], cwd)
    if not count_str or not count_str.isdigit():
        return None
    behind = int(count_str)
    if behind <= 0:
        return None  # HEAD is equal to or ahead of the default branch

    log = _git(["log", "--oneline", f"HEAD..{remote_ref}"], cwd) or ""

    return (
        f"Deze kloon staat {behind} commit(s) achter op origin/{default_branch} "
        f"(lokale branch: {head_branch}). Commits die hier nog ontbreken:\n"
        f"{log}\n\n"
        "Doe een git fetch en vergelijk voordat je een taakstatus leest of werk "
        "uitdeelt — zie CLAUDE.md 'Before you trust this working tree'."
    )


def _read_event():
    """The hook's stdin JSON, or {} if there is none to read (or it's a tty)."""
    if sys.stdin.isatty():
        return {}
    try:
        data = sys.stdin.read()
    except Exception:
        return {}
    if not data.strip():
        return {}
    try:
        return json.loads(data)
    except (json.JSONDecodeError, ValueError):
        return {}


def main():
    event = _read_event()
    cwd = event.get("cwd") or os.getcwd()

    message = check_staleness(cwd)
    if message:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message,
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
