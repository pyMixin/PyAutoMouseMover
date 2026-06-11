"""Auto Mouse Mover.

A small, cross-platform (Windows + macOS) script that periodically nudges the
mouse a few pixels to simulate user activity for legitimate keep-awake use such
as demos, dashboards, kiosks, and long-running jobs.

Stop with Ctrl+C, an optional --duration timeout, or the optional --failsafe
(move the mouse to the top-left corner).

See claude.md for the design and roadmap.md for the phased plan.
"""

import argparse
import sys
import time
from datetime import datetime, timedelta

try:
    import pyautogui
except ImportError:
    print("Missing dependency. Install with: pip install pyautogui")
    sys.exit(1)


def move_mouse(move_pixels: int) -> None:
    """Nudge the mouse by ``move_pixels`` and return it to its start position."""
    x, y = pyautogui.position()
    pyautogui.moveTo(x + move_pixels, y, duration=0.1)
    pyautogui.moveTo(x, y, duration=0.1)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Small cross-platform auto mouse mover for Windows and macOS.",
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
        help="Enable fail-safe. Move the mouse to the top-left corner to stop.",
    )

    args = parser.parse_args(argv)

    if args.interval <= 0:
        parser.error("--interval must be a positive number of seconds")
    if args.pixels <= 0:
        parser.error("--pixels must be a positive number")
    if args.duration < 0:
        parser.error("--duration cannot be negative")

    return args


def run(args: argparse.Namespace) -> None:
    pyautogui.FAILSAFE = args.failsafe

    end_time = None
    if args.duration > 0:
        end_time = datetime.now() + timedelta(minutes=args.duration)

    duration_label = "Until stopped" if args.duration == 0 else f"{args.duration} minute(s)"
    print("Auto Mouse Mover started.")
    print(f"Interval: {args.interval} second(s)")
    print(f"Move distance: {args.pixels} pixel(s)")
    print(f"Duration: {duration_label}")
    if args.failsafe:
        print("Fail-safe enabled: move the mouse to the top-left corner to stop.")
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


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
