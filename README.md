# Python Auto Mouse Mover

A small, cross-platform (Windows + macOS) script that periodically nudges the mouse to
simulate user activity — for legitimate keep-awake use such as demos, dashboards,
kiosks, and long-running jobs.

> Do **not** use this to bypass employer monitoring, time-tracking, security controls,
> or compliance policies. See [claude.md](./claude.md) for the full design and security
> requirements.

## Status

🚧 In development. See [roadmap.md](./roadmap.md) for the phased plan.
Phases 0–1 complete: the runnable MVP works. Next up: cross-platform permission
hardening, config file, and packaging.

## Usage

```bash
python auto_mouse_mover.py                          # move 1px every 60s, run until stopped
python auto_mouse_mover.py --interval 30            # every 30 seconds
python auto_mouse_mover.py --duration 120           # run for 2 hours, then exit
python auto_mouse_mover.py --interval 45 --pixels 3 # 3px every 45 seconds
python auto_mouse_mover.py --failsafe               # move mouse to top-left corner to stop
```

| Flag         | Default | Description                                          |
| ------------ | ------- | ---------------------------------------------------- |
| `--interval` | 60      | Seconds between movements                            |
| `--pixels`   | 1       | Pixels to move (right, then back)                    |
| `--duration` | 0       | Minutes to run; 0 = until stopped                    |
| `--failsafe` | off     | Enable fail-safe stop (cursor to top-left corner)    |

## Requirements

- Python 3.10+ (developed on 3.13)
- [`pyautogui`](https://pypi.org/project/pyautogui/)

## Quick Start

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
python auto_mouse_mover.py --interval 60 --pixels 1
```

Stop with `Ctrl+C`. Optional fail-safe: run with `--failsafe` and move the mouse to the
top-left corner to stop.

> **macOS:** grant Accessibility permission to your terminal / Python under
> System Settings → Privacy & Security → Accessibility.
