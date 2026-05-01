# Git Puller Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `git_puller.py` — a Textual TUI that scans all drives for git repos, shows branch/status, and lets the user selectively pull any or all of them.

**Architecture:** Single file `git_puller.py` split into three layers: pure utility functions (testable), a multithreaded scanner that streams results via a queue, and a Textual app with three reactive panels (scan status, repo list, pull log). Tests cover all pure logic; TUI is verified manually.

**Tech Stack:** Python 3.10+, `textual>=0.60.0` (TUI framework), `concurrent.futures` (thread pool), `subprocess` (git commands), `dataclasses` (RepoInfo model)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `git_puller.py` | Create | Entire tool — data model, scanner, status resolver, TUI app |
| `tests/test_git_puller.py` | Create | Unit tests for all pure functions |
| `requirements.txt` | Modify | Add `textual>=0.60.0` |

---

### Task 1: Add dependency and verify git guard

**Files:**
- Modify: `requirements.txt`
- Create: `git_puller.py` (stub with git check only)

- [ ] **Step 1: Add textual to requirements.txt**

Open `requirements.txt` and append:
```
textual>=0.60.0
```

- [ ] **Step 2: Install the new dependency**

```bash
pip install textual>=0.60.0
```

Expected: installs textual and its dependencies (rich, etc.) without errors.

- [ ] **Step 3: Create git_puller.py with only the git-on-PATH guard**

Create `C:\wamp64\www\pyPDFLibrarianSort\git_puller.py`:

```python
"""Interactive TUI for finding and pulling all git repositories on this machine."""

from __future__ import annotations

import shutil
import sys


def check_git() -> None:
    """Exit with a clear message if git is not on PATH."""
    if not shutil.which("git"):
        print("Error: 'git' not found on PATH. Please install git and try again.")
        sys.exit(1)


if __name__ == "__main__":
    check_git()
    print("git found — TUI not yet implemented")
```

- [ ] **Step 4: Run to verify git guard works**

```bash
python git_puller.py
```

Expected output: `git found — TUI not yet implemented`

- [ ] **Step 5: Commit**

```bash
git add requirements.txt git_puller.py
git commit -m "feat: scaffold git_puller with dependency and git-on-PATH guard"
```

---

### Task 2: Data model and pure utility functions

**Files:**
- Modify: `git_puller.py`
- Create: `tests/test_git_puller.py`

- [ ] **Step 1: Write failing tests for utility functions**

Create `C:\wamp64\www\pyPDFLibrarianSort\tests\test_git_puller.py`:

```python
"""Tests for git_puller pure utility functions."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from git_puller import RepoInfo, should_skip_dir, get_available_drives


class TestShouldSkipDir:
    def test_skips_node_modules(self):
        assert should_skip_dir("node_modules") is True

    def test_skips_pycache(self):
        assert should_skip_dir("__pycache__") is True

    def test_skips_windows(self):
        assert should_skip_dir("Windows") is True

    def test_skips_program_files(self):
        assert should_skip_dir("Program Files") is True

    def test_skips_program_files_x86(self):
        assert should_skip_dir("Program Files (x86)") is True

    def test_skips_recycle_bin(self):
        assert should_skip_dir("$Recycle.Bin") is True

    def test_skips_system_volume_info(self):
        assert should_skip_dir("System Volume Information") is True

    def test_skips_dot_git(self):
        assert should_skip_dir(".git") is True

    def test_allows_normal_dirs(self):
        assert should_skip_dir("my-project") is False

    def test_allows_src(self):
        assert should_skip_dir("src") is False


class TestGetAvailableDrives:
    def test_returns_list(self):
        drives = get_available_drives()
        assert isinstance(drives, list)

    def test_returns_strings(self):
        drives = get_available_drives()
        assert all(isinstance(d, str) for d in drives)

    def test_c_drive_present_on_windows(self):
        if sys.platform == "win32":
            drives = get_available_drives()
            assert any("C" in d.upper() for d in drives)

    def test_drive_paths_end_with_backslash(self):
        if sys.platform == "win32":
            drives = get_available_drives()
            assert all(d.endswith("\\") for d in drives)


class TestRepoInfo:
    def test_default_not_selected(self):
        repo = RepoInfo(path="C:\\myrepo")
        assert repo.selected is False

    def test_no_upstream_not_selected_by_default(self):
        repo = RepoInfo(path="C:\\myrepo", has_upstream=False)
        assert repo.selected is False

    def test_can_be_selected(self):
        repo = RepoInfo(path="C:\\myrepo")
        repo.selected = True
        assert repo.selected is True

    def test_status_badge_dirty(self):
        repo = RepoInfo(path="C:\\myrepo", dirty=True, has_upstream=True, ahead=0, behind=0)
        assert repo.status_badge == "~ dirty"

    def test_status_badge_ahead_behind(self):
        repo = RepoInfo(path="C:\\myrepo", dirty=False, has_upstream=True, ahead=2, behind=3)
        assert repo.status_badge == "↑2 ↓3"

    def test_status_badge_clean(self):
        repo = RepoInfo(path="C:\\myrepo", dirty=False, has_upstream=True, ahead=0, behind=0)
        assert repo.status_badge == "✓"

    def test_status_badge_no_upstream(self):
        repo = RepoInfo(path="C:\\myrepo", has_upstream=False)
        assert repo.status_badge == "(no upstream)"

    def test_status_badge_timeout(self):
        repo = RepoInfo(path="C:\\myrepo", timed_out=True)
        assert repo.status_badge == "(timeout)"

    def test_display_path_truncates_long_paths(self):
        long_path = "C:\\" + "a" * 60
        repo = RepoInfo(path=long_path)
        assert len(repo.display_path) <= 50
        assert repo.display_path.endswith("…")

    def test_display_path_short_path_unchanged(self):
        repo = RepoInfo(path="C:\\short\\path")
        assert repo.display_path == "C:\\short\\path"
```

- [ ] **Step 2: Run tests — verify they all fail**

```bash
cd C:\wamp64\www\pyPDFLibrarianSort
python -m pytest tests/test_git_puller.py -v 2>&1 | head -40
```

Expected: `ImportError` or `ModuleNotFoundError` — `RepoInfo`, `should_skip_dir`, `get_available_drives` not yet defined.

- [ ] **Step 3: Implement RepoInfo, should_skip_dir, get_available_drives in git_puller.py**

Replace the full content of `git_puller.py` with:

```python
"""Interactive TUI for finding and pulling all git repositories on this machine."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass, field


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
    """Return a list of available drive root paths on Windows (e.g. ['C:\\', 'D:\\']).
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
# Git guard
# ---------------------------------------------------------------------------

def check_git() -> None:
    """Exit with a clear message if git is not on PATH."""
    if not shutil.which("git"):
        print("Error: 'git' not found on PATH. Please install git and try again.")
        sys.exit(1)


if __name__ == "__main__":
    check_git()
    print("git found — TUI not yet implemented")
```

- [ ] **Step 4: Run tests — verify they all pass**

```bash
python -m pytest tests/test_git_puller.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add git_puller.py tests/test_git_puller.py
git commit -m "feat: add RepoInfo dataclass and utility functions with tests"
```

---

### Task 3: Status resolver

**Files:**
- Modify: `git_puller.py`
- Modify: `tests/test_git_puller.py`

- [ ] **Step 1: Add tests for resolve_repo_status using a real temp git repo**

Append to `tests/test_git_puller.py`:

```python
import subprocess
import tempfile
import pathlib
from git_puller import resolve_repo_status


class TestResolveRepoStatus:
    def _make_git_repo(self, tmp_path: pathlib.Path) -> str:
        """Create a bare git repo with one commit. Returns the path string."""
        repo = str(tmp_path)
        subprocess.run(["git", "init", repo], check=True, capture_output=True)
        subprocess.run(["git", "-C", repo, "config", "user.email", "test@test.com"], check=True, capture_output=True)
        subprocess.run(["git", "-C", repo, "config", "user.name", "Test"], check=True, capture_output=True)
        (tmp_path / "README.md").write_text("hello")
        subprocess.run(["git", "-C", repo, "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", repo, "commit", "-m", "init"], check=True, capture_output=True)
        return repo

    def test_detects_branch(self, tmp_path):
        repo = self._make_git_repo(tmp_path)
        info = resolve_repo_status(repo)
        assert info.branch in ("main", "master")

    def test_clean_repo_not_dirty(self, tmp_path):
        repo = self._make_git_repo(tmp_path)
        info = resolve_repo_status(repo)
        assert info.dirty is False

    def test_modified_file_is_dirty(self, tmp_path):
        repo = self._make_git_repo(tmp_path)
        (tmp_path / "README.md").write_text("modified")
        info = resolve_repo_status(repo)
        assert info.dirty is True

    def test_no_upstream_flagged(self, tmp_path):
        repo = self._make_git_repo(tmp_path)
        info = resolve_repo_status(repo)
        assert info.has_upstream is False

    def test_path_preserved(self, tmp_path):
        repo = self._make_git_repo(tmp_path)
        info = resolve_repo_status(repo)
        assert info.path == repo
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_git_puller.py::TestResolveRepoStatus -v
```

Expected: `ImportError` — `resolve_repo_status` not yet defined.

- [ ] **Step 3: Implement resolve_repo_status in git_puller.py**

Add after the `get_available_drives` function (before the `check_git` function):

```python
# ---------------------------------------------------------------------------
# Status resolver
# ---------------------------------------------------------------------------

import subprocess


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
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/test_git_puller.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add git_puller.py tests/test_git_puller.py
git commit -m "feat: add resolve_repo_status with subprocess git commands"
```

---

### Task 4: Drive scanner (thread pool)

**Files:**
- Modify: `git_puller.py`
- Modify: `tests/test_git_puller.py`

- [ ] **Step 1: Write failing tests for scanner**

Append to `tests/test_git_puller.py`:

```python
import queue
import time
from git_puller import scan_drive


class TestScanDrive:
    def _make_git_repo(self, tmp_path: pathlib.Path) -> str:
        repo = str(tmp_path)
        subprocess.run(["git", "init", repo], check=True, capture_output=True)
        subprocess.run(["git", "-C", repo, "config", "user.email", "t@t.com"], check=True, capture_output=True)
        subprocess.run(["git", "-C", repo, "config", "user.name", "T"], check=True, capture_output=True)
        (tmp_path / "f.txt").write_text("x")
        subprocess.run(["git", "-C", repo, "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", repo, "commit", "-m", "x"], check=True, capture_output=True)
        return repo

    def test_finds_git_repo_in_dir(self, tmp_path):
        repo_path = tmp_path / "myrepo"
        repo_path.mkdir()
        self._make_git_repo(repo_path)
        q: queue.Queue = queue.Queue()
        scan_drive(str(tmp_path), q)
        results = []
        while not q.empty():
            results.append(q.get())
        paths = [r.path for r in results]
        assert str(repo_path) in paths

    def test_skips_node_modules(self, tmp_path):
        skip_dir = tmp_path / "node_modules"
        skip_dir.mkdir()
        repo_path = skip_dir / "hidden_repo"
        repo_path.mkdir()
        self._make_git_repo(repo_path)
        q: queue.Queue = queue.Queue()
        scan_drive(str(tmp_path), q)
        results = []
        while not q.empty():
            results.append(q.get())
        paths = [r.path for r in results]
        assert str(repo_path) not in paths

    def test_does_not_descend_into_git_internals(self, tmp_path):
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        self._make_git_repo(repo_path)
        q: queue.Queue = queue.Queue()
        scan_drive(str(tmp_path), q)
        results = []
        while not q.empty():
            results.append(q.get())
        # Only the repo itself, not .git subdirectory
        paths = [r.path for r in results]
        assert not any(".git" in p and p != str(repo_path) for p in paths)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_git_puller.py::TestScanDrive -v
```

Expected: `ImportError` — `scan_drive` not defined.

- [ ] **Step 3: Implement scan_drive in git_puller.py**

Add after the `resolve_repo_status` function:

```python
# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

import queue as queue_module
from concurrent.futures import ThreadPoolExecutor


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
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/test_git_puller.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add git_puller.py tests/test_git_puller.py
git commit -m "feat: add multithreaded drive scanner"
```

---

### Task 5: Textual TUI — scan panel and app skeleton

**Files:**
- Modify: `git_puller.py`

Note: TUI components are verified by running the app manually, not with automated tests.

- [ ] **Step 1: Add the Textual app skeleton with scan panel to git_puller.py**

Add after the `start_scan` function (before `check_git`):

```python
# ---------------------------------------------------------------------------
# TUI
# ---------------------------------------------------------------------------

import queue as _queue
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
        self._result_queue: _queue.Queue = _queue.Queue()
        self._repos: list[RepoInfo] = []
        self._executor = None
        self._scan_done = False

    def compose(self) -> ComposeResult:
        drives = get_available_drives()
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
            except _queue.Empty:
                break

    def _wait_for_scan_done(self) -> None:
        if self._executor:
            self._executor.shutdown(wait=True)
        self._scan_done = True
        self.call_from_thread(self._on_scan_complete)

    def _on_scan_complete(self) -> None:
        scan_panel = self.query_one(ScanPanel)
        scan_panel.scanning = False
```

- [ ] **Step 2: Update the __main__ block to launch the app**

Replace the existing `if __name__ == "__main__":` block at the bottom with:

```python
if __name__ == "__main__":
    check_git()
    app = GitPullerApp()
    app.run()
```

- [ ] **Step 3: Run the app and verify the scan panel works**

```bash
python git_puller.py
```

Expected: full-screen TUI opens, scan panel shows `SCAN  Scanning C:\  D:\...  Found: N repos` updating in real-time, eventually shows `Scan complete — N repos found`. Press `q` to quit.

- [ ] **Step 4: Commit**

```bash
git add git_puller.py
git commit -m "feat: add Textual app skeleton with live scan panel"
```

---

### Task 6: Textual TUI — repo list panel with checkboxes

**Files:**
- Modify: `git_puller.py`

- [ ] **Step 1: Add RepoList widget to git_puller.py**

Add the following classes after `ScanPanel` and before `GitPullerApp`:

```python
from textual.widgets import ListView, ListItem, Label
from textual import on
from rich.text import Text


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
```

- [ ] **Step 2: Update GitPullerApp to include RepoList**

Replace the `GitPullerApp` class with:

```python
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
    """

    BINDINGS = [
        ("space", "toggle_repo", "Toggle"),
        ("a", "select_all", "All"),
        ("n", "deselect_all", "None"),
        ("p", "pull_selected", "Pull"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._result_queue: _queue.Queue = _queue.Queue()
        self._repos: list[RepoInfo] = []
        self._executor = None
        self._scan_done = False

    def compose(self) -> ComposeResult:
        yield ScanPanel()
        yield RepoList()
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
            except _queue.Empty:
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

    def action_pull_selected(self) -> None:
        pass  # implemented in Task 7
```

- [ ] **Step 3: Run the app and verify the repo list**

```bash
python git_puller.py
```

Expected: repos appear in the scrollable middle panel as the scan runs. Arrow keys navigate. `Space` toggles checkbox. `a` selects all, `n` deselects all. `q` quits.

- [ ] **Step 4: Commit**

```bash
git add git_puller.py
git commit -m "feat: add scrollable repo list with checkbox toggling"
```

---

### Task 7: Pull log panel and pull orchestrator

**Files:**
- Modify: `git_puller.py`

- [ ] **Step 1: Add PullLog widget after RepoList class**

Add this class after `RepoList` and before `GitPullerApp`:

```python
from textual.widgets import RichLog


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
```

- [ ] **Step 2: Add pull_repos method and dirty-repo confirmation to GitPullerApp**

Add the following methods inside `GitPullerApp` (replace `action_pull_selected` stub and add helpers):

```python
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
                # Ask for confirmation — post to main thread and wait
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
        from textual.widgets import Input
        from textual.screen import ModalScreen
        from textual.app import ComposeResult as CR

        class ConfirmScreen(ModalScreen):
            def __init__(self, repo_path: str) -> None:
                super().__init__()
                self._repo_path = repo_path

            def compose(self) -> CR:
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
```

- [ ] **Step 3: Update GitPullerApp.compose to include PullLog, and update CSS**

Replace the `compose` method and `CSS` in `GitPullerApp`:

```python
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

    def compose(self) -> ComposeResult:
        yield ScanPanel()
        yield RepoList()
        yield PullLog(highlight=True, markup=True)
        yield Footer()
```

- [ ] **Step 4: Run the app and verify pull behavior**

```bash
python git_puller.py
```

Expected:
- After scan, navigate the list with arrow keys
- Press `Space` to select repos, `p` to pull
- Pull log panel (bottom) streams `[repo-name] ...` lines in color
- Dirty repos show a modal asking `y/n`
- Summary line appears when all pulls complete

- [ ] **Step 5: Commit**

```bash
git add git_puller.py
git commit -m "feat: add pull log panel and sequential pull orchestrator with dirty-repo confirmation"
```

---

### Task 8: Polish — CSS layout, keyboard hint bar, final cleanup

**Files:**
- Modify: `git_puller.py`

- [ ] **Step 1: Verify all imports are at the top of the file**

The file currently has imports scattered (added incrementally). Consolidate them at the top of `git_puller.py`. The final top-of-file import block should be:

```python
from __future__ import annotations

import os
import queue as _queue
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer, Input, Label, ListItem, ListView, RichLog, Static
```

Remove any duplicate `import` statements that were added inside functions or method bodies (the `from textual...` imports inside `_confirm_dirty_pull`), since they are now at the top level.

- [ ] **Step 2: Update _confirm_dirty_pull to remove inline imports and fix type alias**

The `_confirm_dirty_pull` method currently has `from textual...` imports inside it. Remove those lines since the classes are now imported at the top. Also rename the return type annotation on `ConfirmScreen.compose` from `-> CR:` to `-> ComposeResult:`. The method should start directly with `class ConfirmScreen(ModalScreen):` and its `compose` signature should be:

```python
def compose(self) -> ComposeResult:
```

- [ ] **Step 3: Run the full test suite one final time**

```bash
python -m pytest tests/test_git_puller.py -v
```

Expected: all tests PASS.

- [ ] **Step 4: Run the app end-to-end**

```bash
python git_puller.py
```

Verify the complete golden path:
1. App opens, scan panel shows drives being scanned
2. Repos stream into the list as found
3. Scan panel collapses to summary when complete
4. Arrow keys navigate, Space toggles, `a` selects all, `n` deselects all
5. `p` pulls selected repos, log streams output per repo with color coding
6. Dirty repo triggers `y/n` modal
7. Summary line appears after all pulls
8. `q` quits

- [ ] **Step 5: Final commit**

```bash
git add git_puller.py
git commit -m "feat: consolidate imports and finalize git_puller TUI"
```
