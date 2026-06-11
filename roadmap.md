# Roadmap — Python Auto Mouse Mover

A phased plan to turn the [design document](./claude.md) into a working, standalone,
cross-platform (Windows + macOS) script. Each phase is independently shippable and
builds on the previous one. Check items off as they land.

> **Scope reminder:** legitimate keep-awake use only (demos, dashboards, kiosks,
> long-running jobs). No stealth, no input capture, no credential handling — per the
> Security Requirements (SR-1…SR-5) in the design doc.

---

## Environment Note (resolve before Phase 1)

- Current `.venv` runs **Python 3.9.6**; the design doc requires **3.10+**.
- `pyautogui` is **not yet installed**.

**Action:** either recreate the venv on Python 3.10+, or relax the floor to 3.9 if the
code avoids 3.10-only syntax. Decide this first — it affects every later phase.

---

## Phase 0 — Project Scaffolding
**Goal:** a clean repo skeleton matching §21 of the design doc.

- [ ] `git init` (repo is not currently version-controlled).
- [ ] Create folder structure: `auto_mouse_mover.py`, `requirements.txt`, `README.md`.
- [ ] `requirements.txt` → `pyautogui`.
- [ ] Add `.gitignore` (`.venv/`, `dist/`, `build/`, `__pycache__/`, `*.spec`).
- [ ] Recreate / verify the virtual environment (see Environment Note) and
      `pip install -r requirements.txt`.

**Exit criteria:** `python -c "import pyautogui"` succeeds inside the venv.

---

## Phase 1 — MVP Core Script
**Goal:** the §11 "Small Effective Script" running end-to-end. This is the standalone
deliverable in its simplest form.

- [ ] Implement `move_mouse(move_pixels)` — nudge right, return to origin.
- [ ] Implement `argparse` CLI: `--interval`, `--pixels`, `--duration`, `--failsafe`.
- [ ] Graceful `import pyautogui` guard with a helpful install message.
- [ ] Main loop: move → sleep → honor duration timeout.
- [ ] Stop controls: `Ctrl+C` (KeyboardInterrupt) and `FailSafeException`.
- [ ] Startup banner: interval, pixel distance, duration, stop hint.

**Exit criteria (maps to FR-1…FR-4):**
- Runs forever with defaults; stops cleanly on `Ctrl+C`.
- `--duration N` exits after N minutes.
- `--failsafe` stops when the mouse hits the top-left corner.
- Same script runs on both Windows and macOS.

---

## Phase 2 — Permissions & Cross-Platform Hardening
**Goal:** make the script behave predictably on each OS (§9, §10, FR-5).

- [ ] macOS: detect missing Accessibility permission and print clear guidance
      (System Settings → Privacy & Security → Accessibility) instead of failing opaquely.
- [ ] Windows: confirm behavior under normal and elevated (Task Scheduler) execution;
      no admin requirement baked into the code.
- [ ] Verify `pyautogui` screen-bounds handling so a 1px move never errors at screen edges.
- [ ] Manual test matrix: Windows 10/11 + macOS, foreground run.

**Exit criteria:** documented, friendly behavior when permissions are missing on each platform.

---

## Phase 3 — Configuration & Logging
**Goal:** configurable without code changes + audit-friendly output (§15, §16, SR-4).

- [ ] Optional `config.json` loader (`interval_seconds`, `move_pixels`,
      `duration_minutes`, `failsafe`); CLI flags override file values.
- [ ] Replace bare `print` with the `logging` module (console by default).
- [ ] Optional `--log-file` writing to the recommended OS path
      (Win: `C:\ProgramData\AutoMouseMover\`, macOS: `/Library/Logs/`).
- [ ] Log start time, stop time, interval, and errors only — **never** user activity (SR-3).

**Exit criteria:** behavior fully driven by `config.json`; log file shows start/stop/interval.

---

## Phase 4 — Packaging (Standalone Binaries)
**Goal:** distributable executables, no Python required on the target (§13, §14).

- [ ] Add `pyinstaller` to a dev/build requirements set.
- [ ] Windows: `pyinstaller --onefile auto_mouse_mover.py` → `dist/auto_mouse_mover.exe`.
- [ ] macOS: `pyinstaller --onefile auto_mouse_mover.py` → `dist/auto_mouse_mover`;
      verify Accessibility permission applies to the packaged app.
- [ ] Smoke-test each binary on a clean machine/VM without a Python install.

**Exit criteria:** a single standalone executable per platform that runs the full MVP.

---

## Phase 5 — Documentation & Acceptance
**Goal:** ship-ready repo (§22, §18).

- [ ] `README.md`: quick start, all CLI flags, stop methods, per-OS permission setup.
- [ ] Acceptable-use note (legitimate keep-awake only) per §18 risk mitigations.
- [ ] Deployment notes: Task Scheduler (Windows) and LaunchAgent (macOS) examples.
- [ ] Final review against Security Requirements SR-1…SR-5.

**Exit criteria:** a new user can install/run from the README with no extra help.

---

## Phase 6 — Future Enhancements (Backlog, optional)
Not required for the standalone deliverable; pull in as needed (§20).

- [ ] System tray icon.
- [ ] Pause/resume hotkey.
- [ ] Signed Windows executable / notarized macOS app.
- [ ] Centralized / policy-based runtime limits for enterprise (Intune, Jamf, SCCM).

---

## Milestone Summary

| Phase | Outcome                          | Standalone? |
| ----- | -------------------------------- | ----------- |
| 0     | Repo scaffold + working venv     | —           |
| 1     | MVP script runs (FR-1…FR-4)      | ✅ (needs Python) |
| 2     | Cross-platform permission polish | ✅          |
| 3     | Config file + logging            | ✅          |
| 4     | PyInstaller binaries             | ✅✅ (no Python needed) |
| 5     | Docs + acceptance                | ✅ ship     |
| 6     | Enhancements backlog             | optional    |

**Definition of "standalone, done":** Phases 1–5 complete — a single executable per
platform (Phase 4) plus README, configurable via flags/`config.json`, with safe stop
controls and audit logging, meeting all functional and security requirements.
