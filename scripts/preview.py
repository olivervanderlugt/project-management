#!/usr/bin/env python3
"""Run Hangar projects locally so the dashboard's "run local" buttons work.

    python3 scripts/preview.py

Serves a tiny control API on 127.0.0.1:8642. The dashboard talks to it from
the browser: it asks `/status` what is running, `POST /run/<slug>` to start a
project, `POST /stop/<slug>` to stop it. Without this helper running the
buttons say so and do nothing — the board itself stays a static page.

What starting a project means:

  * clone the project's GitHub repo into ~/.hangar-previews/<slug>
    (shallow; an existing checkout gets a fast-forward pull instead)
  * work out how to run it — `npm run dev` for a package.json project, with
    the port passed the way its framework expects, or a plain static server
    when there is just an index.html — and start it on the project's own port
  * report the local URL back so the button turns into a link

Everything is stdlib. It binds to loopback only, never deploys, never pushes,
and never touches a repo that is not named by a `repo:` line in projects/.
Logs land next to the checkouts: ~/.hangar-previews/<slug>.log.
"""

import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKDIR = Path(os.environ.get("HANGAR_PREVIEWS", Path.home() / ".hangar-previews"))

HELPER_PORT = 8642  # the one number the dashboard knows
PORT_BASE = 8650  # projects land on PORT_BASE .. PORT_BASE+199
PORT_SPAN = 200
START_TIMEOUT = 180  # seconds to wait for a dev server to answer


# --------------------------------------------------------------------- parsing


def parse_frontmatter(path):
    """Flat `key: value` frontmatter, same contract as dashboard/build.py."""
    text = path.read_text(encoding="utf-8")
    meta = {}
    if text.lstrip().startswith("---"):
        parts = text.lstrip().split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                key, _, value = line.partition(":")
                meta[key.strip().lower()] = value.strip()
    meta["slug"] = path.stem
    return meta


def runnable_projects(projects_dir=None):
    """{slug: repo} for every project that names a GitHub repo."""
    directory = projects_dir or (ROOT / "projects")
    table = {}
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        meta = parse_frontmatter(path)
        repo = meta.get("repo", "")
        if repo:
            table[meta["slug"]] = repo
    return table


def assign_ports(slugs):
    """A stable port per slug: hashed, then probed past collisions.

    Deterministic for a given set of slugs, and close to stable when the set
    changes — only a hash collision moves, and only by a step. Nothing else
    may depend on these numbers: the dashboard always reads the URL from
    /status rather than computing it.
    """
    ports = {}
    taken = set()
    for slug in sorted(slugs):
        seed = int(hashlib.sha1(slug.encode("utf-8")).hexdigest(), 16)
        for step in range(PORT_SPAN):
            port = PORT_BASE + (seed + step) % PORT_SPAN
            if port not in taken:
                ports[slug] = port
                taken.add(port)
                break
    return ports


# --------------------------------------------------------- how to run a thing


def plan_run(checkout, port):
    """(argv, extra_env, needs_install) for a checkout, or None if unknown.

    Pure and offline on purpose — this is the part the tests pin down.
    """
    package = checkout / "package.json"
    if package.is_file():
        try:
            manifest = json.loads(package.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            manifest = {}
        scripts = manifest.get("scripts") or {}
        script = "dev" if "dev" in scripts else ("start" if "start" in scripts else None)
        if script:
            deps = {}
            deps.update(manifest.get("dependencies") or {})
            deps.update(manifest.get("devDependencies") or {})
            needs_install = not (checkout / "node_modules").is_dir()
            if "next" in deps:
                argv = ["npm", "run", script, "--", "-p", str(port)]
            elif "vite" in deps:
                argv = ["npm", "run", script, "--", "--port", str(port), "--strictPort"]
            else:
                # The one convention nearly everything else honours.
                return (["npm", "run", script], {"PORT": str(port)}, needs_install)
            return (argv, {}, needs_install)
    if (checkout / "index.html").is_file():
        argv = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
        return (argv, {}, False)
    return None


# ---------------------------------------------------------------- the runners


class Runner:
    """One project's local process, plus everything needed to report on it."""

    def __init__(self, slug, repo, port):
        self.slug = slug
        self.repo = repo
        self.port = port
        self.proc = None
        self.state = "stopped"  # stopped | starting | running | error
        self.error = ""
        self.lock = threading.Lock()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}/"

    @property
    def checkout(self):
        return WORKDIR / self.slug

    @property
    def logfile(self):
        return WORKDIR / f"{self.slug}.log"

    def snapshot(self):
        with self.lock:
            alive = self.proc is not None and self.proc.poll() is None
            if self.state == "running" and not alive:
                self.state, self.error = "error", "the dev server exited; see the log"
            return {
                "state": self.state,
                "url": self.url if self.state == "running" else "",
                "error": self.error,
                "log": str(self.logfile),
            }

    def start(self):
        with self.lock:
            if self.state in ("starting", "running") and self.proc and self.proc.poll() is None:
                return
            self.state, self.error = "starting", ""
        threading.Thread(target=self._bring_up, daemon=True).start()

    def _bring_up(self):
        try:
            WORKDIR.mkdir(parents=True, exist_ok=True)
            with self.logfile.open("w", encoding="utf-8") as log:
                self._checkout(log)
                plan = plan_run(self.checkout, self.port)
                if plan is None:
                    raise RuntimeError(
                        "no package.json dev/start script and no index.html — "
                        "don't know how to run this"
                    )
                argv, extra_env, needs_install = plan
                if needs_install:
                    self._run(["npm", "install", "--no-audit", "--no-fund"], log)
                env = dict(os.environ, **extra_env)
                with self.lock:
                    self.proc = subprocess.Popen(
                        argv,
                        cwd=self.checkout,
                        env=env,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
            self._await_port()
            with self.lock:
                self.state = "running"
        except Exception as err:  # noqa: BLE001 — the state *is* the handler
            self.stop(quiet=True)
            with self.lock:
                self.state, self.error = "error", str(err)

    def _checkout(self, log):
        if (self.checkout / ".git").is_dir():
            # Best effort: a preview does not need to be current, and a local
            # experiment in the checkout must never be destroyed for one.
            subprocess.run(
                ["git", "-C", str(self.checkout), "pull", "--ff-only"],
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=120,
                check=False,
            )
        else:
            self._run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    f"https://github.com/{self.repo}",
                    str(self.checkout),
                ],
                log,
            )

    def _run(self, argv, log):
        result = subprocess.run(
            argv, cwd=str(WORKDIR), stdout=log, stderr=subprocess.STDOUT, check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"`{' '.join(argv)}` failed — see the log")

    def _await_port(self):
        deadline = time.monotonic() + START_TIMEOUT
        while time.monotonic() < deadline:
            with self.lock:
                if self.proc is None or self.proc.poll() is not None:
                    raise RuntimeError("the dev server exited while starting; see the log")
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return
            except OSError:
                time.sleep(0.5)
        raise RuntimeError(f"nothing answered on port {self.port} within {START_TIMEOUT}s")

    def stop(self, quiet=False):
        with self.lock:
            proc, self.proc = self.proc, None
            if not quiet:
                self.state, self.error = "stopped", ""
        if proc is not None and proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    proc.kill()


# ------------------------------------------------------------------- the API


def build_runners():
    projects = runnable_projects()
    ports = assign_ports(projects)
    return {slug: Runner(slug, repo, ports[slug]) for slug, repo in projects.items()}


class Handler(BaseHTTPRequestHandler):
    runners = {}

    def _reply(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        # The board is served from Pages, a file:// open, or an Artifact; the
        # helper is loopback-only, so a wide-open CORS header risks nothing
        # that isn't already on this machine.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802 — http.server's naming
        self._reply(200, {"ok": True})

    def do_GET(self):  # noqa: N802
        if self.path.rstrip("/") in ("", "/status"):
            self._reply(
                200,
                {
                    "helper": "hangar-preview",
                    "projects": {s: r.snapshot() for s, r in self.runners.items()},
                },
            )
        else:
            self._reply(404, {"error": "unknown path"})

    def do_POST(self):  # noqa: N802
        action, _, slug = self.path.strip("/").partition("/")
        runner = self.runners.get(slug)
        if action not in ("run", "stop") or runner is None:
            self._reply(404, {"error": f"no runnable project called {slug!r}"})
            return
        if action == "run":
            runner.start()
        else:
            runner.stop()
        self._reply(200, {"ok": True, "project": runner.snapshot()})

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")


def main():
    Handler.runners = build_runners()
    server = ThreadingHTTPServer(("127.0.0.1", HELPER_PORT), Handler)
    print(f"hangar preview helper on http://127.0.0.1:{HELPER_PORT}")
    print(f"checkouts and logs in {WORKDIR}")
    for slug, runner in sorted(Handler.runners.items()):
        print(f"  {slug:<24} -> port {runner.port}  ({runner.repo})")
    print("open the dashboard and use the 'run local' buttons. Ctrl+C stops everything.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for runner in Handler.runners.values():
            runner.stop()
    print("\nstopped.")


if __name__ == "__main__":
    main()
