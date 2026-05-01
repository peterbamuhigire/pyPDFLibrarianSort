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


import subprocess
import pathlib
from git_puller import resolve_repo_status


class TestResolveRepoStatus:
    def _make_git_repo(self, tmp_path: pathlib.Path) -> str:
        """Create a git repo with one commit. Returns the path string."""
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


import queue
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
        paths = [r.path for r in results]
        assert not any(".git" in p and p != str(repo_path) for p in paths)
