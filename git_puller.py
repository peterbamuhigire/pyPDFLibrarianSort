"""Interactive TUI for finding and pulling all git repositories on this machine."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass


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
