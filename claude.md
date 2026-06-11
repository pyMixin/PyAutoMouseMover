# Python Auto Mouse Mover — Solution Design Document

## 1. Purpose

The goal is to create a small, lightweight Python-based auto mouse mover that runs on Windows and macOS. The script should periodically move the mouse slightly to simulate user activity for legitimate use cases such as keeping a workstation awake during demos, dashboards, long-running jobs, kiosk displays, or lab environments.

This tool should not be used to bypass employer monitoring, time-tracking, security controls, or compliance policies.

---

## 2. Target Platforms

| Platform      |           Support Level | Notes                                               |
| ------------- | ----------------------: | --------------------------------------------------- |
| Windows 10/11 |                    Full | Can run normally or elevated through Task Scheduler |
| macOS         |                    Full | Requires Accessibility permission                   |
| Linux         | Optional future support | Not required for this version                       |

---

## 3. Design Goals

The script should be:

* Small and simple
* Cross-platform
* Easy to start and stop
* Configurable without code changes
* Safe: no credential storage
* Minimal CPU and memory usage
* Able to run in foreground, background, or scheduled startup mode

---

## 4. Non-Goals

The tool will not:

* Capture keystrokes
* Read screen content
* Disable security controls
* Store administrator passwords
* Hide itself from users or administrators
* Attempt to bypass endpoint security tools
* Run as malware, persistence agent, or stealth process

---

## 5. Recommended Technology Stack

### Language

Python 3.10+

### Primary Library

`pyautogui`

Reason:

* Works on Windows and macOS
* Simple API
* Reliable for basic mouse movement
* Lightweight enough for this use case

Install command:

```bash
pip install pyautogui
```

Optional packaging:

```bash
pip install pyinstaller
```

---

## 6. High-Level Architecture

```text
+-----------------------------+
| auto_mouse_mover.py         |
+-----------------------------+
| Config Loader               |
| - interval_seconds          |
| - move_pixels               |
| - duration_minutes          |
| - safe_corner_stop          |
+-----------------------------+
| Platform Permission Check   |
| - Windows admin optional    |
| - macOS Accessibility check |
+-----------------------------+
| Mouse Movement Engine       |
| - Move right                |
| - Move back                 |
| - Sleep interval            |
+-----------------------------+
| Stop Controls               |
| - Ctrl+C                    |
| - Move mouse to corner      |
| - Optional duration timeout |
+-----------------------------+
```

---

## 7. Functional Requirements

### FR-1: Move Mouse Periodically

The script shall move the mouse by a small number of pixels at a configurable interval.

Default:

```text
Move every 60 seconds
Move 1 pixel right, then 1 pixel left
```

### FR-2: Configurable Runtime

The user should be able to configure:

```text
interval_seconds
move_pixels
duration_minutes
```

### FR-3: Safe Stop

The script should stop when:

* User presses `Ctrl+C`
* Runtime duration expires
* Optional fail-safe is triggered by moving mouse to top-left corner

### FR-4: Cross-Platform Support

The same script should run on:

```text
Windows
macOS
```

### FR-5: Admin Execution

The script may run with admin privileges when launched through approved OS mechanisms.

It must not store or hardcode admin credentials.

---

## 8. Security Requirements

### SR-1: No Credential Storage

The script must not contain usernames, passwords, tokens, or admin credentials.

### SR-2: No Stealth Behavior

The script must not attempt to hide from Task Manager, Activity Monitor, EDR tools, or system administrators.

### SR-3: No Input Capture

The script must not capture keyboard input, screenshots, clipboard data, or user activity.

### SR-4: User-Visible Execution

The script should log startup, movement interval, and stop messages to the console or log file.

### SR-5: Admin Rights

Admin rights should only be used when required by the organization’s endpoint policy.

Recommended approaches:

Windows:

* Use Task Scheduler
* Select “Run with highest privileges”
* Use an approved service account if required by IT policy

macOS:

* Grant Accessibility permission manually
* Use LaunchAgent for startup
* Avoid storing administrator credentials

---

## 9. macOS Permissions

On macOS, the script needs Accessibility permission.

Path:

```text
System Settings
Privacy & Security
Accessibility
Allow Terminal / Python / packaged app
```

If packaged with PyInstaller, grant permission to the packaged app.

---

## 10. Windows Admin Execution Options

### Option A: Run Manually as Administrator

Right-click Command Prompt or PowerShell:

```text
Run as Administrator
```

Then run:

```bash
python auto_mouse_mover.py
```

### Option B: Run with Task Scheduler

Recommended for controlled environments.

Settings:

```text
Trigger: At logon
Action: Start a program
Program: python.exe
Arguments: C:\Path\auto_mouse_mover.py
Run with highest privileges: Enabled
```

### Option C: Package as EXE

Package command:

```bash
pyinstaller --onefile auto_mouse_mover.py
```

Run output from:

```text
dist/auto_mouse_mover.exe
```

---

## 11. Small Effective Script

```python
import argparse
import time
import sys
from datetime import datetime, timedelta

try:
    import pyautogui
except ImportError:
    print("Missing dependency. Install with: pip install pyautogui")
    sys.exit(1)


def move_mouse(move_pixels: int) -> None:
    """
    Moves mouse slightly and returns it to original position.
    """
    x, y = pyautogui.position()
    pyautogui.moveTo(x + move_pixels, y, duration=0.1)
    pyautogui.moveTo(x, y, duration=0.1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Small cross-platform auto mouse mover for Windows and macOS."
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Seconds between mouse movements. Default: 60",
    )

    parser.add_argument(
        "--pixels",
        type=int,
        default=1,
        help="Number of pixels to move. Default: 1",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Duration in minutes. 0 means run until stopped. Default: 0",
    )

    parser.add_argument(
        "--failsafe",
        action="store_true",
        help="Enable PyAutoGUI fail-safe. Move mouse to top-left corner to stop.",
    )

    args = parser.parse_args()

    pyautogui.FAILSAFE = args.failsafe

    end_time = None
    if args.duration > 0:
        end_time = datetime.now() + timedelta(minutes=args.duration)

    print("Auto Mouse Mover started.")
    print(f"Interval: {args.interval} seconds")
    print(f"Move distance: {args.pixels} pixel(s)")
    print(f"Duration: {'Until stopped' if args.duration == 0 else str(args.duration) + ' minutes'}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            if end_time and datetime.now() >= end_time:
                print("Duration complete. Exiting.")
                break

            move_mouse(args.pixels)
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except pyautogui.FailSafeException:
        print("\nFail-safe triggered. Exiting.")


if __name__ == "__main__":
    main()
```

---

## 12. Example Commands

Run forever with default settings:

```bash
python auto_mouse_mover.py
```

Move every 30 seconds:

```bash
python auto_mouse_mover.py --interval 30
```

Run for 2 hours:

```bash
python auto_mouse_mover.py --duration 120
```

Move 3 pixels every 45 seconds:

```bash
python auto_mouse_mover.py --interval 45 --pixels 3
```

Enable fail-safe stop:

```bash
python auto_mouse_mover.py --failsafe
```

---

## 13. Packaging for Windows

Install PyInstaller:

```bash
pip install pyinstaller
```

Create EXE:

```bash
pyinstaller --onefile auto_mouse_mover.py
```

Output:

```text
dist/auto_mouse_mover.exe
```

Recommended folder:

```text
C:\Tools\AutoMouseMover\
```

---

## 14. Packaging for macOS

Install PyInstaller:

```bash
pip install pyinstaller
```

Create executable:

```bash
pyinstaller --onefile auto_mouse_mover.py
```

Run from:

```text
dist/auto_mouse_mover
```

Grant Accessibility permission to Terminal, Python, or the packaged app.

---

## 15. Optional Config File Enhancement

For a slightly more enterprise-friendly version, add a `config.json` file.

Example:

```json
{
  "interval_seconds": 60,
  "move_pixels": 1,
  "duration_minutes": 0,
  "failsafe": true
}
```

This keeps the script small while allowing non-developers to adjust behavior.

---

## 16. Logging Recommendation

Basic console logging is enough for the small version.

For managed environments, write to:

Windows:

```text
C:\ProgramData\AutoMouseMover\auto_mouse_mover.log
```

macOS:

```text
/Library/Logs/AutoMouseMover.log
```

Log only:

```text
Start time
Stop time
Interval setting
Errors
```

Do not log user activity.

---

## 17. Deployment Model

### Personal Use

```text
Run manually from terminal
```

### Departmental / Admin Use

```text
Windows Task Scheduler
macOS LaunchAgent
Packaged executable
Approved software distribution tool
```

### Enterprise Use

```text
Intune
Jamf
SCCM
Group Policy
Approved endpoint management platform
```

---

## 18. Risk Considerations

| Risk                       | Mitigation                               |
| -------------------------- | ---------------------------------------- |
| Misuse to fake activity    | Publish acceptable use policy            |
| Endpoint security alert    | Code sign packaged executable            |
| macOS permission failure   | Document Accessibility setup             |
| User forgets it is running | Console output and optional duration     |
| Script runs forever        | Use `--duration` for controlled sessions |
| Admin credential misuse    | Never store credentials in script        |

---

## 19. Recommended MVP

The MVP should include:

```text
auto_mouse_mover.py
README.md
requirements.txt
```

`requirements.txt`:

```text
pyautogui
```

MVP features:

```text
Cross-platform mouse movement
Configurable interval
Configurable pixel distance
Optional duration
Ctrl+C stop
Optional fail-safe stop
```

---

## 20. Future Enhancements

Possible future improvements:

```text
System tray icon
Pause/resume hotkey
Config file support
Signed Windows executable
macOS notarized app
Centralized logging
Policy-based runtime limit
```

---

## 21. Recommended Final Folder Structure

```text
auto-mouse-mover/
│
├── auto_mouse_mover.py
├── requirements.txt
├── README.md
└── dist/
```

---

## 22. README Quick Start

```bash
pip install -r requirements.txt
python auto_mouse_mover.py --interval 60 --pixels 1
```

Stop:

```text
Press Ctrl+C
```

Optional safe stop:

```bash
python auto_mouse_mover.py --failsafe
```

Move the mouse to the top-left corner to stop.

---

## 23. Final Recommendation

Use a single Python script with `pyautogui`. Do not build admin credential handling into the code. Let Windows Task Scheduler, macOS Accessibility permissions, Jamf, Intune, or approved endpoint tools handle elevated execution. This keeps the solution small, effective, and safer for enterprise use.
