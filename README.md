# Python Auto Mouse Mover

A small, cross-platform (Windows + macOS) script that periodically nudges the mouse to
simulate user activity — for legitimate keep-awake use such as demos, dashboards,
kiosks, and long-running jobs.

> Do **not** use this to bypass employer monitoring, time-tracking, security controls,
> or compliance policies. See [claude.md](./claude.md) for the full design and security
> requirements.

## Status

🚧 In development. See [roadmap.md](./roadmap.md) for the phased plan.
Phase 0 (scaffolding) is complete; the runnable MVP arrives in Phase 1.

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
