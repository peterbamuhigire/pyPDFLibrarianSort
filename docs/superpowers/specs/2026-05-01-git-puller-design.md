# Git Puller — Design Spec

**Date:** 2026-05-01  
**Status:** Approved  
**File:** `git_puller.py` (project root)

---

## Overview

An interactive terminal UI tool that scans all drives on the computer for git repositories, displays their status (branch, ahead/behind, dirty), and lets the user selectively pull any or all of them. Built with [Textual](https://github.com/Textualize/textual) for a full-screen, keyboard-driven TUI experience.

Follows the same standalone-script launcher pattern as `watch_setup.py` and `sign_setup.py` in this project.

---

## Architecture

Three logical layers inside a single file:

1. **Scanner** — background thread pool that walks all drives concurrently, identifies git repos by `.git` directory presence, streams results into a thread-safe queue
2. **Status resolver** — per discovered repo, runs three fast git commands to get branch, dirty flag, and ahead/behind counts; runs in a separate short-lived thread so the scan is never blocked
3. **Textual TUI app** — three vertical panels (scan status, repo list, pull log) updated reactively as data arrives

---

## Scanner

### Drive Detection

On Windows, probes `A:\` through `Z:\` for existence at startup to build the list of available drives. All present drives are scanned.

### Thread Pool

`concurrent.futures.ThreadPoolExecutor` with 8 workers. Each worker is assigned one drive root and walks it recursively.

### Skip List

The following directory names are skipped entirely (not descended into):

- `node_modules`
- `__pycache__`
- `Windows`
- `Program Files`
- `Program Files (x86)`
- `$Recycle.Bin`
- `System Volume Information`
- `.git` subdirectories (the repo itself is registered, but its internals are not walked)

### Repo Discovery

When a `.git` folder is found inside a directory, the parent directory is a repo. It is immediately posted to the result queue (triggering a live TUI update) and the status resolver is dispatched for it.

---

## Status Resolution

Three git commands run per repo, each via `subprocess.run` with `git -C <path>`:

| Field | Command | Notes |
|---|---|---|
| Branch | `git branch --show-current` | Empty string if detached HEAD |
| Dirty | `git status --porcelain` | Non-empty output = dirty |
| Ahead/Behind | `git rev-list --left-right --count HEAD...@{u}` | Skipped if no upstream; returns `ahead\tbehind` as two tab-separated numbers |

Repos with no remote upstream are flagged `(no upstream)` and excluded from pull selection by default, but can still be manually selected.

---

## TUI Layout

```
┌─────────────────────────────────────────────────┐
│ SCAN   Scanning C:\ D:\ E:\...   Found: 14 repos│
├─────────────────────────────────────────────────┤
│ [x] C:\Users\Peter\projects\myapp   main  ↑1 ↓0 │
│ [ ] C:\wamp64\www\pyPDF...          main  ✓      │
│ [x] D:\work\api-server              dev   ↑0 ↓3  │
│ [ ] C:\Users\Peter\tools\dotfiles   main  ~ dirty│
│  ...                                             │
├─────────────────────────────────────────────────┤
│ PULL LOG                                         │
│ [myapp] Already up to date.                      │
│ [api-server] From github.com/peter/api           │
│ [api-server]   dev -> origin/dev                 │
└─────────────────────────────────────────────────┘
 Space: toggle  a: all  n: none  p: pull  q: quit
```

### Panels

**Scan panel (top):** Shows which drives are being scanned and a running count of repos found. Collapses to a one-line summary (`Scan complete — N repos found`) once all drives finish.

**Repo list panel (middle, scrollable):** One row per discovered repo. Columns:
- Checkbox `[x]` / `[ ]`
- Full path (truncated if too long, with `…`)
- Current branch name
- Ahead/behind indicator (`↑N ↓N`) or `(no upstream)` or `~ dirty`

Repos stream in as the scanner finds them. The list is scrollable with arrow keys.

**Pull log panel (bottom):** Streams `git pull` output line-by-line. Each repo's output is prefixed with `[repo-name]` in bold. Color coding:
- Green: success / already up to date
- Red: error
- Yellow: merge conflict detected

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Space` | Toggle selected repo's checkbox |
| `a` | Select all repos |
| `n` | Deselect all repos |
| `p` | Pull all selected repos |
| `q` | Quit |
| `↑` / `↓` | Navigate repo list |

---

## Pull Behavior

- Pulls run **sequentially** (not in parallel) to keep log output readable and avoid interleaved output
- **Dirty repos:** Before pulling, show an inline confirmation prompt: `This repo has uncommitted changes. Pull anyway? (y/n)`. Default: skip.
- **No upstream:** Repos without a remote upstream are skipped unless manually selected; if selected, pull is attempted and the error is shown in the log
- **Summary line:** After all pulls complete, the log panel appends: `── Done: X pulled, Y skipped, Z failed ──`

---

## Dependencies

One new dependency added to `requirements.txt`:

```
textual>=0.60.0
```

`rich` is a transitive dependency of `textual` and will be available automatically.

---

## Error Handling

- If a git command times out (>5s), the repo is shown with status `(timeout)` and excluded from pull
- If a drive is inaccessible (permission denied at root), it is silently skipped
- If `git` is not on PATH, the app exits immediately with a clear error message before launching the TUI
- Subprocess errors during pull are caught, shown in red in the log panel, and counted in the failure summary

---

## File Structure

```
pyPDFLibrarianSort/
└── git_puller.py        ← new file, single entry point
```

No new directories, no config files, no state persisted between runs.

---

## Usage

```bash
cd C:\wamp64\www\pyPDFLibrarianSort
python git_puller.py
```
