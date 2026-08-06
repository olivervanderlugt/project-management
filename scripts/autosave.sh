#!/usr/bin/env bash
# Autosave the Hangar: rebuild the board, commit, push.
#
# Runs from the Stop and SessionEnd hooks, so work survives closing the laptop,
# a dropped connection, or walking away mid-sentence. Costs no tokens: it is a
# plain shell command, not a model call.
#
# Deliberately conservative — it must never damage the repo or interrupt a
# session:
#   * only ever runs inside the Hangar repo, verified by its actual contents
#   * never runs on a detached HEAD, and never force-pushes
#   * never touches a branch other than the one already checked out
#   * exits silently when nothing changed, so no empty commits pile up
#   * a failed push is not an error — the commit is already safe locally and
#     the next autosave will carry it up
#
# Anything unexpected exits 0. A save mechanism that blocks your session is
# worse than one that quietly retries later.

set -uo pipefail

log() { echo "autosave: $*" >&2; }

repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$repo_root" || exit 0

# Refuse to act unless this really is the Hangar. Guards against the hook
# somehow firing in another checkout.
[ -f "$repo_root/dashboard/build.py" ] || exit 0
grep -q "^# The Hangar" "$repo_root/CLAUDE.md" 2>/dev/null || exit 0

branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) || exit 0
[ -n "$branch" ] || exit 0

# Nothing staged, unstaged or untracked means nothing to do.
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
  exit 0
fi

# Rebuild so the committed board matches the markdown. If the build breaks,
# still save the markdown — losing the source is the failure that matters.
if command -v python3 >/dev/null 2>&1; then
  python3 dashboard/build.py >/dev/null 2>&1 || log "build failed, saving sources anyway"
fi

git add -A || exit 0

if git diff --cached --quiet; then
  exit 0
fi

stamp=$(date "+%Y-%m-%d %H:%M")
git -c core.hooksPath=/dev/null commit --quiet \
  -m "Autosave $stamp" \
  -m "Automatic checkpoint from the Hangar autosave hook." >/dev/null 2>&1 || exit 0

if git push --quiet origin "$branch" >/dev/null 2>&1; then
  log "saved and pushed to $branch"
else
  log "saved locally on $branch; push failed, will retry next save"
fi

exit 0
