# Python Auto Mouse Mover

A small, cross-platform (Windows + macOS) script that periodically nudges the mouse a
few pixels to simulate user activity — for **legitimate keep-awake use** such as demos,
dashboards, kiosks, lab environments, and long-running jobs.

> ⚠️ **Acceptable use.** Do not use this to bypass employer monitoring, time-tracking,
> security controls, or compliance policies. It does not capture input, read the screen,
> store credentials, or hide itself. See [Security](#security) and [claude.md](./claude.md).

**Status:** ✅ Complete (Phases 0–5). See [roadmap.md](./roadmap.md). Phase 6 is an
optional future backlog.

---

## Table of Contents

- [Features](#features)
- [Solution Design](#solution-design)
- [How It Works (Flow)](#how-it-works-flow)
- [Install](#install)
- [Usage](#usage)
- [Configure (config.json)](#configure-configjson)
- [Logging](#logging)
- [Platform Permissions](#platform-permissions)
- [Packaging (Standalone Binary)](#packaging-standalone-binary)
- [Deployment](#deployment)
- [Security](#security)

---

## Features

- Cross-platform: Windows 10/11 and macOS (pure `pyautogui`, no OS-specific code).
- Configurable interval, pixel distance, and run duration.
- Settings via CLI flags **or** a `config.json` file (CLI overrides the file).
- Safe stop: `Ctrl+C`, a `--duration` timeout, or the optional fail-safe corner.
- Screen-edge safe: never gets stuck nudging off the right edge.
- macOS Accessibility detection with clear, actionable guidance.
- Console logging by default; optional log file to the OS-recommended path.
- Packages to a single self-contained executable (no Python on the target).

---

## Solution Design

A single Python script, `auto_mouse_mover.py`, organized into small, testable pieces:

```text
+--------------------------------------------------------------+
| auto_mouse_mover.py                                          |
+--------------------------------------------------------------+
| Config resolution                                            |
|   CLI flags  >  config.json  >  built-in DEFAULTS            |
|   keys: interval_seconds, move_pixels,                       |
|         duration_minutes, failsafe                           |
+--------------------------------------------------------------+
| Logging (logging module)                                     |
|   console always; optional --log-file (OS path + fallback)   |
+--------------------------------------------------------------+
| Permission / platform check                                  |
|   macOS: verify a real cursor move (Accessibility)           |
|   Windows: no admin baked in; elevation left to the OS       |
+--------------------------------------------------------------+
| Movement engine                                              |
|   move right (or left near the screen edge) -> move back     |
+--------------------------------------------------------------+
| Stop controls                                                |
|   Ctrl+C  |  --duration timeout  |  fail-safe corner         |
+--------------------------------------------------------------+
```

**Settings precedence:** a value given on the command line wins; otherwise the value
from `config.json` is used; otherwise the built-in default applies.

**Repo layout:**

```text
PyMouseMover/
├── auto_mouse_mover.py      # the application
├── config.example.json      # copy to config.json to customize
├── requirements.txt         # runtime dep: pyautogui
├── requirements-dev.txt     # + pyinstaller for packaging
├── README.md
├── roadmap.md               # phased plan (all phases ✅)
├── claude.md                # full solution design document
└── dist/                    # built binary (gitignored, not committed)
```

---

## How It Works (Flow)

```text
        start
          │
          ▼
   resolve settings  ──►  CLI flags > config.json > defaults
          │
          ▼
   set up logging  ──►  console (+ optional file)
          │
          ▼
   check permission  ──►  macOS: cursor actually moves?
          │                 └─ no ─► warn + how to fix (keeps running)
          ▼
   ┌─────────────────────────────────────┐
   │  loop:                              │
   │    duration elapsed?  ── yes ──► exit "Duration complete"
   │      │ no                            │
   │      ▼                               │
   │    move mouse (edge-safe)           │
   │      │                               │
   │      ▼                               │
   │    sleep(interval)                  │
   └─────────────────────────────────────┘
          │
   Ctrl+C ─► "Stopped by user"
   fail-safe corner ─► "Fail-safe triggered"
```

---

## Install

Requires **Python 3.10+** (developed on 3.13).

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows (PowerShell/CMD)

# 2. Install the runtime dependency
pip install -r requirements.txt
```

For packaging (optional), install dev dependencies instead:

```bash
pip install -r requirements-dev.txt   # pyautogui + pyinstaller
```

---

## Usage

```bash
python auto_mouse_mover.py                          # 1px every 60s, until stopped
python auto_mouse_mover.py --interval 30            # every 30 seconds
python auto_mouse_mover.py --duration 120           # run 2 hours, then exit
python auto_mouse_mover.py --interval 45 --pixels 3 # 3px every 45 seconds
python auto_mouse_mover.py --failsafe               # mouse to top-left corner to stop
python auto_mouse_mover.py --log-file               # also log to the OS path
python auto_mouse_mover.py --config my-config.json  # load settings from a file
```

| Flag         | Default      | Description                                                       |
| ------------ | ------------ | ---------------------------------------------------------------- |
| `--interval` | 60           | Seconds between movements (must be > 0)                          |
| `--pixels`   | 1            | Pixels to move, right then back (must be > 0)                    |
| `--duration` | 0            | Minutes to run; `0` = until stopped                              |
| `--failsafe` | off          | Enable fail-safe stop (move cursor to top-left corner)           |
| `--config`   | `config.json`| Path to a JSON config file (beside the script by default)        |
| `--log-file` | off          | Log to a file; bare flag = OS path, or pass an explicit path     |

**Stop the script** by pressing `Ctrl+C` (or let `--duration` expire, or trigger the
fail-safe corner when `--failsafe` is on).

---

## Configure (config.json)

For non-developers, settings can live in a JSON file instead of flags. Copy the example:

```bash
cp config.example.json config.json
```

```json
{
  "interval_seconds": 60,
  "move_pixels": 1,
  "duration_minutes": 0,
  "failsafe": true
}
```

- The script auto-loads `config.json` from beside itself when present.
- Use `--config <path>` to point at a different file.
- **Any CLI flag overrides the file value** (precedence: CLI > config.json > defaults).
- Your real `config.json` is gitignored; only `config.example.json` is committed.

---

## Logging

By default the script logs start time, settings, and stop reason to the **console**.
Add `--log-file` to also write to a file:

| Platform | Default log path (bare `--log-file`)                |
| -------- | --------------------------------------------------- |
| Windows  | `C:\ProgramData\AutoMouseMover\auto_mouse_mover.log`|
| macOS    | `~/Library/Logs/AutoMouseMover.log`                 |

Pass an explicit path with `--log-file /path/to/file.log`. If the path is not writable,
the script warns and continues with console-only logging. **Only** start/stop/interval
and errors are logged — never user activity (see [Security](#security)).

---

## Platform Permissions

### macOS — Accessibility

macOS blocks programmatic mouse control until you grant Accessibility permission. On
startup the script detects this and prints guidance. To fix:

```text
System Settings → Privacy & Security → Accessibility
→ enable your Terminal / Python / the packaged app
```

### Windows — Admin (optional)

No admin rights are required for normal use, and **none are baked into the code**. If
your endpoint policy requires elevation, run it via an approved mechanism (see
[Deployment](#deployment)) — never by hardcoding credentials.

---

## Packaging (Standalone Binary)

Build a single self-contained executable (no Python needed on the target):

```bash
pip install -r requirements-dev.txt
pyinstaller --onefile --name auto_mouse_mover auto_mouse_mover.py
```

Output:

| Platform | Build host | Output                          |
| -------- | ---------- | ------------------------------- |
| macOS    | macOS      | `dist/auto_mouse_mover`         |
| Windows  | Windows    | `dist/auto_mouse_mover.exe`     |

> PyInstaller does not cross-compile — build the Windows `.exe` on Windows and the macOS
> binary on macOS. On macOS, grant Accessibility permission to the packaged app.
> Build artifacts (`dist/`, `build/`, `*.spec`) are gitignored and not committed.

---

## Deployment

- **Personal:** run from the terminal as shown above.
- **Windows (managed):** Task Scheduler → *At logon* → start `auto_mouse_mover.exe`
  (enable "Run with highest privileges" only if your policy requires it).
- **macOS (managed):** a LaunchAgent that runs the binary at login; grant Accessibility.
- **Enterprise:** distribute the signed/notarized binary via Intune, Jamf, or SCCM.

---

## Security

The tool is designed to be safe and transparent (full requirements in
[claude.md §8](./claude.md)):

| Requirement | Guarantee                                                                  |
| ----------- | -------------------------------------------------------------------------- |
| SR-1        | **No credential storage** — no usernames, passwords, or tokens in the code.|
| SR-2        | **No stealth** — does not hide from Task Manager / Activity Monitor / EDR. |
| SR-3        | **No input capture** — no keystrokes, screenshots, or clipboard access.    |
| SR-4        | **User-visible** — logs start, interval, and stop to console/file.         |
| SR-5        | **Admin only when required** — elevation is left to approved OS mechanisms.|
