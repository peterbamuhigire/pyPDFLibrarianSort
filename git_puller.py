"""Interactive TUI for finding and pulling all git repositories on this machine."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import queue as queue_module
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKIP_DIRS: frozenset[str] = frozenset({
    "node_modules",
    "__pycache__",
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "$Recycle.Bin",
    "System Volume Information",
    ".git",
})


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class RepoInfo:
    path: str
    branch: str = ""
    ahead: int = 0
    behind: int = 0
    dirty: bool = False
    has_upstream: bool = True
    timed_out: bool = False
    selected: bool = False
    pull_state: str = "idle"  # idle | pulling | done | error | skipped

    @property
    def status_badge(self) -> str:
        if self.timed_out:
            return "(timeout)"
        if not self.has_upstream:
            return "(no upstream)"
        if self.dirty:
            return "~ dirty"
        if self.ahead > 0 or self.behind > 0:
            return f"↑{self.ahead} ↓{self.behind}"
        return "✓"

    @property
    def display_path(self) -> str:
        max_len = 50
        if len(self.path) <= max_len:
            return self.path
        return self.path[:max_len - 1] + "…"


# ---------------------------------------------------------------------------
# Pure utility functions
# ---------------------------------------------------------------------------

def should_skip_dir(name: str) -> bool:
    """Return True if a directory name should never be descended into."""
    return name in SKIP_DIRS


def get_available_drives() -> list[str]:
    """Return available drive root paths on Windows (e.g. ['C:\\\\', 'D:\\\\']).
    On non-Windows systems returns ['/'] as a single root."""
    if sys.platform != "win32":
        return ["/"]
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        root = f"{letter}:\\"
        if os.path.exists(root):
            drives.append(root)
    return drives


# ---------------------------------------------------------------------------
# Status resolver
# ---------------------------------------------------------------------------

def resolve_repo_status(path: str) -> RepoInfo:
    """Run three git commands to get branch, dirty flag, and ahead/behind for a repo."""
    info = RepoInfo(path=path)

    def run(args: list[str]) -> tuple[str, int]:
        try:
            result = subprocess.run(
                ["git", "-C", path] + args,
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", -1

    # Branch
    branch, rc = run(["branch", "--show-current"])
    if rc == -1:
        info.timed_out = True
        return info
    info.branch = branch or "(detached)"

    # Dirty
    dirty_out, _ = run(["status", "--porcelain"])
    info.dirty = bool(dirty_out)

    # Ahead / behind
    ab_out, ab_rc = run(["rev-list", "--left-right", "--count", "HEAD...@{u}"])
    if ab_rc != 0 or not ab_out:
        info.has_upstream = False
        info.selected = False
    else:
        parts = ab_out.split()
        if len(parts) == 2:
            try:
                info.ahead = int(parts[0])
                info.behind = int(parts[1])
                info.has_upstream = True
            except ValueError:
                info.has_upstream = False

    return info


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def scan_drive(root: str, result_queue: queue_module.Queue) -> None:
    """Walk root recursively, find git repos, post RepoInfo objects to result_queue."""
    try:
        for dirpath, dirnames, _ in os.walk(root, topdown=True):
            # Prune skip dirs in-place so os.walk won't descend into them
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

            if ".git" in os.listdir(dirpath):
                # This directory is a git repo
                info = resolve_repo_status(dirpath)
                result_queue.put(info)
                # Don't descend further into the repo's subdirs
                dirnames.clear()
    except PermissionError:
        pass  # Inaccessible drive root — skip silently


def start_scan(result_queue: queue_module.Queue) -> ThreadPoolExecutor:
    """Start scanning all available drives. Returns the executor (call shutdown to join)."""
    drives = get_available_drives()
    executor = ThreadPoolExecutor(max_workers=8)
    for drive in drives:
        executor.submit(scan_drive, drive, result_queue)
    return executor


# ---------------------------------------------------------------------------
# TUI
# ---------------------------------------------------------------------------

import threading
from textual.app import App, ComposeResult
from textual.widgets import Static, Footer
from textual.reactive import reactive


class ScanPanel(Static):
    """Top panel showing scan progress."""

    scanning: reactive[bool] = reactive(True)
    drives_text: reactive[str] = reactive("")
    found_count: reactive[int] = reactive(0)

    def render(self) -> str:
        if self.scanning:
            return f"[bold]SCAN[/bold]  Scanning {self.drives_text}  Found: {self.found_count} repos"
        return f"[bold]SCAN[/bold]  Scan complete — {self.found_count} repos found"


class GitPullerApp(App):
    """Main Textual application."""

    CSS = """
    ScanPanel {
        height: 1;
        background: $panel;
        padding: 0 1;
        color: $text;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._result_queue: queue_module.Queue = queue_module.Queue()
        self._repos: list[RepoInfo] = []
        self._executor = None
        self._scan_done = False

    def compose(self) -> ComposeResult:
        yield ScanPanel()
        yield Footer()

    def on_mount(self) -> None:
        drives = get_available_drives()
        scan_panel = self.query_one(ScanPanel)
        scan_panel.drives_text = "  ".join(drives)
        self._executor = start_scan(self._result_queue)
        self.set_interval(0.1, self._poll_queue)
        threading.Thread(target=self._wait_for_scan_done, daemon=True).start()

    def _poll_queue(self) -> None:
        drained = 0
        while not self._result_queue.empty() and drained < 20:
            try:
                repo = self._result_queue.get_nowait()
                self._repos.append(repo)
                scan_panel = self.query_one(ScanPanel)
                scan_panel.found_count = len(self._repos)
                drained += 1
            except queue_module.Empty:
                break

    def _wait_for_scan_done(self) -> None:
        if self._executor:
            self._executor.shutdown(wait=True)
        self._scan_done = True
        self.call_from_thread(self._on_scan_complete)

    def _on_scan_complete(self) -> None:
        scan_panel = self.query_one(ScanPanel)
        scan_panel.scanning = False


# ---------------------------------------------------------------------------
# Git guard
# ---------------------------------------------------------------------------

def check_git() -> None:
    """Exit with a clear message if git is not on PATH."""
    if not shutil.which("git"):
        print("Error: 'git' not found on PATH. Please install git and try again.")
        sys.exit(1)


if __name__ == "__main__":
    check_git()
    app = GitPullerApp()
    app.run()
