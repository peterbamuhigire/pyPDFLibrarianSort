# Git Puller Rescan Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `r` keyboard shortcut that clears the repo list and restarts the full drive scan, and remove the `tests/` directory.

**Architecture:** Two isolated changes to `git_puller.py`: add `r` to BINDINGS and implement `action_rescan` which shuts down the old executor, clears the list, resets state, and starts a fresh scan. Delete `tests/` separately.

**Tech Stack:** Python, Textual (existing), threading (existing)

---

## File Map

| File | Action |
|---|---|
| `git_puller.py` | Modify — add `r` binding + `action_rescan` method |
| `tests/test_git_puller.py` | Delete |
| `tests/` | Delete (empty after above) |

---

### Task 1: Add rescan binding and action_rescan method

**Files:**
- Modify: `C:\wamp64\www\pyPDFLibrarianSort\git_puller.py:304-310` (BINDINGS) and after line 364 (new method)

- [ ] **Step 1: Add `r` to BINDINGS**

In `git_puller.py`, replace the `BINDINGS` list (lines 304–310):

```python
    BINDINGS = [
        ("space", "toggle_repo", "Toggle"),
        ("a", "select_all", "All"),
        ("n", "deselect_all", "None"),
        ("p", "pull_selected", "Pull"),
        ("r", "rescan", "Rescan"),
        ("q", "quit", "Quit"),
    ]
```

- [ ] **Step 2: Add action_rescan method**

Insert this method after `action_deselect_all` (after line 364) and before `action_pull_selected`:

```python
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
```

- [ ] **Step 3: Verify the file imports cleanly**

```bash
cd C:\wamp64\www\pyPDFLibrarianSort && python -c "import git_puller; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git -C C:\wamp64\www\pyPDFLibrarianSort add git_puller.py
git -C C:\wamp64\www\pyPDFLibrarianSort commit -m "feat: add rescan command (r key) to git_puller TUI"
```

---

### Task 2: Delete tests directory

**Files:**
- Delete: `C:\wamp64\www\pyPDFLibrarianSort\tests\test_git_puller.py`
- Delete: `C:\wamp64\www\pyPDFLibrarianSort\tests\`

- [ ] **Step 1: Remove the tests directory**

```bash
git -C C:\wamp64\www\pyPDFLibrarianSort rm -r tests/
```

- [ ] **Step 2: Verify it is gone**

```bash
ls C:\wamp64\www\pyPDFLibrarianSort\tests\ 2>&1
```

Expected: error — directory does not exist.

- [ ] **Step 3: Commit**

```bash
git -C C:\wamp64\www\pyPDFLibrarianSort commit -m "chore: remove dev test scaffolding"
```

---

### Task 3: Push to main

- [ ] **Step 1: Push**

```bash
git -C C:\wamp64\www\pyPDFLibrarianSort push origin main
```

Expected: `main -> main` success line.
