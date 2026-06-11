"""Auto Mouse Mover.

A small, cross-platform (Windows + macOS) script that periodically nudges the
mouse a few pixels to simulate user activity for legitimate keep-awake use such
as demos, dashboards, kiosks, and long-running jobs.

Stop with Ctrl+C, an optional --duration timeout, or the optional --failsafe
(move the mouse to the top-left corner).

Settings come from (highest priority first): command-line flags, then an
optional config.json, then built-in defaults.

See claude.md for the design and roadmap.md for the phased plan.
"""

import argparse
import json
import logging
import os
import platform
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("Missing dependency. Install with: pip install pyautogui")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Defaults & configuration
# ---------------------------------------------------------------------------

DEFAULTS = {
    "interval_seconds": 60,
    "move_pixels": 1,
    "duration_minutes": 0,
    "failsafe": False,
}

# Config file looked up next to this script when --config is not given.
DEFAULT_CONFIG_NAME = "config.json"

log = logging.getLogger("auto_mouse_mover")


def default_log_path() -> Path:
    """Return the OS-recommended log path (used when --log-file is given bare)."""
    if platform.system() == "Windows":
        base = Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        return base / "AutoMouseMover" / "auto_mouse_mover.log"
    # macOS (and any Unix): prefer the user Library so no admin rights are needed.
    return Path.home() / "Library" / "Logs" / "AutoMouseMover.log"


def load_config(path: Path | None) -> dict:
    """Load settings from a JSON config file.

    If ``path`` is None, auto-load ``config.json`` next to the script when it
    exists. An explicitly requested path that is missing or invalid is an error.
    """
    explicit = path is not None
    if path is None:
        path = Path(__file__).resolve().parent / DEFAULT_CONFIG_NAME
        if not path.exists():
            return {}

    if not path.exists():
        raise SystemExit(f"Config file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"Could not read config file {path}: {exc}")

    if not isinstance(data, dict):
        raise SystemExit(f"Config file {path} must contain a JSON object.")

    if explicit:
        log.debug("Loaded config from %s", path)
    return data


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(log_file: Path | None) -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    log.addHandler(console)

    if log_file is not None:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(fmt)
            log.addHandler(file_handler)
            log.info("Logging to file: %s", log_file)
        except OSError as exc:
            log.warning("Could not open log file %s (%s); console logging only.",
                        log_file, exc)


# ---------------------------------------------------------------------------
# Permission / platform checks
# ---------------------------------------------------------------------------

def check_macos_accessibility() -> bool:
    """On macOS, verify the mouse can actually be moved.

    Without Accessibility permission, programmatic mouse moves are silently
    ignored. We nudge 1px and check the cursor moved, then restore it. Returns
    True if movement works (or not on macOS), False if it appears blocked.
    """
    if platform.system() != "Darwin":
        return True

    try:
        start_x, start_y = pyautogui.position()
        width, _ = pyautogui.size()
        probe_x = start_x - 2 if start_x + 2 >= width else start_x + 2
        pyautogui.moveTo(probe_x, start_y, duration=0)
        moved_x, _ = pyautogui.position()
        pyautogui.moveTo(start_x, start_y, duration=0)  # restore
    except Exception as exc:  # noqa: BLE001 - report any backend failure clearly
        log.warning("Could not verify mouse control: %s", exc)
        return False

    if moved_x == start_x:
        log.warning(
            "Mouse movement appears blocked. Grant Accessibility permission:\n"
            "  System Settings > Privacy & Security > Accessibility\n"
            "  then enable your terminal / Python / the packaged app."
        )
        return False
    return True


# ---------------------------------------------------------------------------
# Mouse movement
# ---------------------------------------------------------------------------

def move_mouse(move_pixels: int) -> None:
    """Nudge the mouse by ``move_pixels`` and return it to its start position.

    Moves left instead of right when the cursor is near the right screen edge so
    the nudge never gets clamped to a no-op.
    """
    x, y = pyautogui.position()
    width, _ = pyautogui.size()
    delta = -move_pixels if x + move_pixels >= width else move_pixels
    pyautogui.moveTo(x + delta, y, duration=0.1)
    pyautogui.moveTo(x, y, duration=0.1)


# ---------------------------------------------------------------------------
# CLI / settings resolution
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Small cross-platform auto mouse mover for Windows and macOS.",
    )
    # Defaults are None so we can tell whether a flag was explicitly provided
    # and resolve precedence (CLI > config.json > built-in defaults).
    parser.add_argument(
        "--interval", type=int, default=None,
        help="Seconds between mouse movements. Default: 60",
    )
    parser.add_argument(
        "--pixels", type=int, default=None,
        help="Number of pixels to move. Default: 1",
    )
    parser.add_argument(
        "--duration", type=int, default=None,
        help="Duration in minutes. 0 means run until stopped. Default: 0",
    )
    parser.add_argument(
        "--failsafe", action="store_true", default=None,
        help="Enable fail-safe. Move the mouse to the top-left corner to stop.",
    )
    parser.add_argument(
        "--config", type=Path, default=None,
        help="Path to a JSON config file. Defaults to config.json beside the script.",
    )
    parser.add_argument(
        "--log-file", dest="log_file", nargs="?", const="__default__", default=None,
        help="Write logs to a file. Bare flag uses the OS-recommended path; "
             "or pass an explicit path.",
    )
    return parser.parse_args(argv)


def resolve_settings(args: argparse.Namespace, config: dict) -> dict:
    """Merge CLI args over config-file values over built-in defaults."""
    def pick(cli_value, config_key):
        if cli_value is not None:
            return cli_value
        if config_key in config:
            return config[config_key]
        return DEFAULTS[config_key]

    settings = {
        "interval": pick(args.interval, "interval_seconds"),
        "pixels": pick(args.pixels, "move_pixels"),
        "duration": pick(args.duration, "duration_minutes"),
        "failsafe": bool(pick(args.failsafe, "failsafe")),
    }

    if not isinstance(settings["interval"], int) or settings["interval"] <= 0:
        raise SystemExit("interval must be a positive integer number of seconds")
    if not isinstance(settings["pixels"], int) or settings["pixels"] <= 0:
        raise SystemExit("pixels must be a positive integer")
    if not isinstance(settings["duration"], int) or settings["duration"] < 0:
        raise SystemExit("duration cannot be negative")

    return settings


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run(settings: dict) -> None:
    pyautogui.FAILSAFE = settings["failsafe"]

    end_time = None
    if settings["duration"] > 0:
        end_time = datetime.now() + timedelta(minutes=settings["duration"])

    duration_label = ("Until stopped" if settings["duration"] == 0
                      else f"{settings['duration']} minute(s)")
    log.info("Auto Mouse Mover started.")
    log.info("Interval: %s second(s)", settings["interval"])
    log.info("Move distance: %s pixel(s)", settings["pixels"])
    log.info("Duration: %s", duration_label)
    if settings["failsafe"]:
        log.info("Fail-safe enabled: move the mouse to the top-left corner to stop.")
    log.info("Press Ctrl+C to stop.")

    check_macos_accessibility()

    try:
        while True:
            if end_time and datetime.now() >= end_time:
                log.info("Duration complete. Exiting.")
                break
            move_mouse(settings["pixels"])
            time.sleep(settings["interval"])
    except KeyboardInterrupt:
        log.info("Stopped by user.")
    except pyautogui.FailSafeException:
        log.info("Fail-safe triggered. Exiting.")


def main() -> None:
    args = parse_args()

    log_file = None
    if args.log_file is not None:
        log_file = default_log_path() if args.log_file == "__default__" else Path(args.log_file)
    setup_logging(log_file)

    config = load_config(args.config)
    settings = resolve_settings(args, config)
    run(settings)


if __name__ == "__main__":
    main()
