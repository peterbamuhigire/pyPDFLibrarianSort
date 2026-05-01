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
