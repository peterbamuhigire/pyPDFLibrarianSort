# Git Puller — Rescan Command Design Spec

**Date:** 2026-05-01  
**Status:** Approved  
**File:** `git_puller.py` (modify), `tests/test_git_puller.py` (delete)

---

## Overview

Two small changes to the existing `git_puller.py` tool:

1. Add an `r` keyboard shortcut that clears the repo list and restarts the full drive scan from scratch
2. Remove the `tests/` directory (the test file was scaffolding used during development)

---

## Rescan Command

### Keyboard Binding

Add `("r", "rescan", "Rescan")` to `GitPullerApp.BINDINGS`.

### action_rescan Method

Add `action_rescan(self) -> None` to `GitPullerApp`:

1. **Shut down old executor** — call `self._executor.shutdown(wait=False)` inside a daemon thread so the UI stays responsive if a prior scan is still in progress
2. **Clear repo list** — call `self.query_one(RepoList).clear()` to remove all rows
3. **Reset state** — set `self._repos = []` and `self._result_queue = queue_module.Queue()`
4. **Reset scan panel** — set `scan_panel.scanning = True` and `scan_panel.found_count = 0`
5. **Start new scan** — call `start_scan(self._result_queue)` and store the returned executor in `self._executor`
6. **Start completion watcher** — start a new daemon thread targeting `self._wait_for_scan_done`

The existing `_poll_queue` interval (started in `on_mount`) continues running and automatically drains the new queue. `PullLog` is not cleared — previous pull output remains visible.

---

## Test Cleanup

- Delete `tests/test_git_puller.py`
- Delete `tests/` directory (it will be empty)

No changes to `requirements.txt`.

---

## File Changes

| File | Action |
|---|---|
| `git_puller.py` | Add `r` binding + `action_rescan` method |
| `tests/test_git_puller.py` | Delete |
| `tests/` | Delete (empty after above) |
