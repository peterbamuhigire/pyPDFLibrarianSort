"""Interactive TUI for finding and pulling all git repositories on this machine."""

from __future__ import annotations

import os
import queue as queue_module
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer, Input, Label, ListItem, ListView, RichLog, Static


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

class ScanPanel(Static):
    """Top panel showing scan progress."""

    scanning: reactive[bool] = reactive(True)
    drives_text: reactive[str] = reactive("")
    found_count: reactive[int] = reactive(0)

    def render(self) -> str:
        if self.scanning:
            return f"[bold]SCAN[/bold]  Scanning {self.drives_text}  Found: {self.found_count} repos"
        return f"[bold]SCAN[/bold]  Scan complete — {self.found_count} repos found"


class RepoRow(ListItem):
    """A single row in the repo list."""

    def __init__(self, repo: RepoInfo) -> None:
        super().__init__()
        self.repo = repo

    def render_row(self) -> Text:
        checkbox = "[x]" if self.repo.selected else "[ ]"
        path = self.repo.display_path.ljust(45)
        branch = (self.repo.branch or "?").ljust(12)
        badge = self.repo.status_badge

        t = Text()
        t.append(checkbox + " ", style="bold cyan" if self.repo.selected else "dim")
        t.append(path + "  ", style="white")
        t.append(branch + "  ", style="green")

        if "dirty" in badge:
            t.append(badge, style="yellow")
        elif "upstream" in badge or "timeout" in badge:
            t.append(badge, style="dim")
        elif badge == "✓":
            t.append(badge, style="green")
        else:
            t.append(badge, style="cyan")
        return t

    def compose(self) -> ComposeResult:
        yield Label(self.render_row())

    def refresh_label(self) -> None:
        self.query_one(Label).update(self.render_row())


class RepoList(ListView):
    """Scrollable list of discovered repos."""

    def add_repo(self, repo: RepoInfo) -> None:
        self.append(RepoRow(repo))

    def toggle_current(self) -> None:
        if self.highlighted_child:
            row: RepoRow = self.highlighted_child  # type: ignore
            row.repo.selected = not row.repo.selected
            row.refresh_label()

    def select_all(self) -> None:
        for child in self.children:
            row: RepoRow = child  # type: ignore
            row.repo.selected = True
            row.refresh_label()

    def deselect_all(self) -> None:
        for child in self.children:
            row: RepoRow = child  # type: ignore
            row.repo.selected = False
            row.refresh_label()

    def selected_repos(self) -> list[RepoInfo]:
        return [
            child.repo  # type: ignore
            for child in self.children
            if child.repo.selected  # type: ignore
        ]


class PullLog(RichLog):
    """Scrolling log of git pull output."""

    def log_line(self, repo_name: str, line: str, style: str = "white") -> None:
        prefix = Text(f"[{repo_name}] ", style="bold")
        prefix.append(line, style=style)
        self.write(prefix)

    def log_summary(self, pulled: int, skipped: int, failed: int) -> None:
        self.write(
            Text(
                f"── Done: {pulled} pulled, {skipped} skipped, {failed} failed ──",
                style="bold white"
            )
        )


class GitPullerApp(App):
    """Main Textual application."""

    CSS = """
    ScanPanel {
        height: 1;
        background: $panel;
        padding: 0 1;
        color: $text;
    }
    RepoList {
        height: 1fr;
        border: solid $primary;
    }
    PullLog {
        height: 10;
        border: solid $accent;
    }
    #confirm-msg {
        padding: 1 2;
        background: $panel;
        border: solid $warning;
        margin: 4 8;
        height: auto;
    }
    #confirm-input {
        margin: 0 8;
    }
    """

    BINDINGS = [
        ("space", "toggle_repo", "Toggle"),
        ("a", "select_all", "All"),
        ("n", "deselect_all", "None"),
        ("p", "pull_selected", "Pull"),
        ("r", "rescan", "Rescan"),
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
        yield RepoList()
        yield PullLog(highlight=True, markup=True)
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
        repo_list = self.query_one(RepoList)
        while not self._result_queue.empty() and drained < 20:
            try:
                repo = self._result_queue.get_nowait()
                self._repos.append(repo)
                repo_list.add_repo(repo)
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

    def action_toggle_repo(self) -> None:
        self.query_one(RepoList).toggle_current()

    def action_select_all(self) -> None:
        self.query_one(RepoList).select_all()

    def action_deselect_all(self) -> None:
        self.query_one(RepoList).deselect_all()

    def action_rescan(self) -> None:
        old_executor = self._executor
        if old_executor:
            threading.Thread(
                target=old_executor.shutdown, kwargs={"wait": False}, daemon=True
            ).start()

        self.query_one(RepoList).clear()
        self._repos = []
        self._result_queue = queue_module.Queue()

        scan_panel = self.query_one(ScanPanel)
        scan_panel.scanning = True
        scan_panel.found_count = 0

        self._executor = start_scan(self._result_queue)
        threading.Thread(target=self._wait_for_scan_done, daemon=True).start()

    def action_pull_selected(self) -> None:
        repos = self.query_one(RepoList).selected_repos()
        if not repos:
            return
        pull_log = self.query_one(PullLog)
        threading.Thread(
            target=self._run_pulls, args=(repos, pull_log), daemon=True
        ).start()

    def _run_pulls(self, repos: list[RepoInfo], pull_log: PullLog) -> None:
        pulled = skipped = failed = 0

        for repo in repos:
            name = os.path.basename(repo.path)

            if repo.dirty:
                confirmed = threading.Event()
                result_holder: list[bool] = []

                def ask(r=repo, ev=confirmed, holder=result_holder) -> None:
                    self.call_from_thread(
                        self._confirm_dirty_pull, r, ev, holder
                    )

                ask()
                confirmed.wait(timeout=60)
                if not result_holder or not result_holder[0]:
                    self.call_from_thread(
                        pull_log.log_line, name,
                        "Skipped (dirty, not confirmed)", "yellow"
                    )
                    skipped += 1
                    continue

            repo.pull_state = "pulling"
            self.call_from_thread(pull_log.log_line, name, "Pulling...", "cyan")

            try:
                result = subprocess.run(
                    ["git", "-C", repo.path, "pull"],
                    capture_output=True, text=True, timeout=60
                )
                output = (result.stdout + result.stderr).strip()
                for line in output.splitlines():
                    lower = line.lower()
                    if "conflict" in lower or "error" in lower:
                        style = "yellow"
                    elif result.returncode != 0:
                        style = "red"
                    else:
                        style = "green"
                    self.call_from_thread(pull_log.log_line, name, line, style)

                if result.returncode == 0:
                    repo.pull_state = "done"
                    pulled += 1
                else:
                    repo.pull_state = "error"
                    failed += 1

            except subprocess.TimeoutExpired:
                self.call_from_thread(pull_log.log_line, name, "Timed out", "red")
                repo.pull_state = "error"
                failed += 1
            except Exception as exc:
                self.call_from_thread(pull_log.log_line, name, str(exc), "red")
                repo.pull_state = "error"
                failed += 1

        self.call_from_thread(pull_log.log_summary, pulled, skipped, failed)

    def _confirm_dirty_pull(
        self,
        repo: RepoInfo,
        event: threading.Event,
        result_holder: list[bool],
    ) -> None:

        class ConfirmScreen(ModalScreen):
            def __init__(self, repo_path: str) -> None:
                super().__init__()
                self._repo_path = repo_path

            def compose(self) -> ComposeResult:
                yield Static(
                    f"[yellow]{self._repo_path}[/yellow] has uncommitted changes.\n"
                    "Pull anyway? (y/n)",
                    id="confirm-msg"
                )
                yield Input(placeholder="y/n", id="confirm-input")

            @on(Input.Submitted, "#confirm-input")
            def on_answer(self, ev: Input.Submitted) -> None:
                self.dismiss(ev.value.strip().lower() == "y")

        def handle_result(confirmed: bool) -> None:
            result_holder.append(confirmed)
            event.set()

        self.push_screen(ConfirmScreen(repo.path), handle_result)


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
