# Roadmap — Python Auto Mouse Mover

A phased plan to turn the [design document](./claude.md) into a working, standalone,
cross-platform (Windows + macOS) script. Each phase is independently shippable and
builds on the previous one. Check items off as they land.

> **Scope reminder:** legitimate keep-awake use only (demos, dashboards, kiosks,
> long-running jobs). No stealth, no input capture, no credential handling — per the
> Security Requirements (SR-1…SR-5) in the design doc.

---

## Environment Note (resolved ✅)

- ~~Current `.venv` runs **Python 3.9.6**; the design doc requires **3.10+**.~~
  Venv recreated on **Python 3.13.9**.
- ~~`pyautogui` is **not yet installed**.~~ Installed (`pyautogui` 0.9.54).

---

## Phase 0 — Project Scaffolding ✅
**Goal:** a clean repo skeleton matching §21 of the design doc.

- [x] `git init` (repo is now version-controlled; baseline committed).
- [x] Create folder structure: `auto_mouse_mover.py`, `requirements.txt`, `README.md`.
- [x] `requirements.txt` → `pyautogui`.
- [x] Add `.gitignore` (`.venv/`, `.idea/`, `dist/`, `build/`, `__pycache__/`, `*.spec`).
- [x] Recreate the virtual environment on Python 3.13 and
      `pip install -r requirements.txt`.

**Exit criteria:** ✅ `python -c "import pyautogui"` succeeds inside the venv.

---

## Phase 1 — MVP Core Script ✅
**Goal:** the §11 "Small Effective Script" running end-to-end. This is the standalone
deliverable in its simplest form.

- [x] Implement `move_mouse(move_pixels)` — nudge right, return to origin.
- [x] Implement `argparse` CLI: `--interval`, `--pixels`, `--duration`, `--failsafe`
      (with positive-value validation).
- [x] Graceful `import pyautogui` guard with a helpful install message.
- [x] Main loop: move → sleep → honor duration timeout.
- [x] Stop controls: `Ctrl+C` (KeyboardInterrupt) and `FailSafeException`.
- [x] Startup banner: interval, pixel distance, duration, stop hint.

**Exit criteria (maps to FR-1…FR-4):**
- [x] Runs forever with defaults; stops cleanly on `Ctrl+C` (verified via mocked loop).
- [x] `--duration N` exits after N minutes (verified).
- [x] `--failsafe` stops when the mouse hits the top-left corner (handler verified).
- [x] Same script runs on both Windows and macOS (pure `pyautogui`, no OS-specific code).

> **Note:** logic verified with a mocked `pyautogui`. A real cursor-movement run on
> macOS needs Accessibility permission granted to the terminal — recommended manual
> check: `python auto_mouse_mover.py --interval 2 --duration 1`.

---

## Phase 2 — Permissions & Cross-Platform Hardening ✅
**Goal:** make the script behave predictably on each OS (§9, §10, FR-5).

- [x] macOS: detect missing Accessibility permission and print clear guidance
      (System Settings → Privacy & Security → Accessibility) instead of failing
      opaquely — `check_macos_accessibility()`.
- [x] Windows: no admin requirement baked into the code; elevation is left to
      Task Scheduler / OS mechanisms (documented in README).
- [x] Screen-bounds safety: `move_mouse()` nudges left near the right edge so a
      move is never clamped to a no-op (verified at x=1919 on a 1920px screen).
- [x] Logic verified via mocked `pyautogui`; live macOS run documented for the user.

**Exit criteria:** ✅ friendly, documented behavior when permissions are missing.

---

## Phase 3 — Configuration & Logging ✅
**Goal:** configurable without code changes + audit-friendly output (§15, §16, SR-4).

- [x] `config.json` loader (`interval_seconds`, `move_pixels`, `duration_minutes`,
      `failsafe`); CLI flags override file values (CLI > config > defaults).
      `config.example.json` shipped; real `config.json` is gitignored.
- [x] Replaced bare `print` with the `logging` module (console by default).
- [x] Optional `--log-file` writing to the recommended OS path
      (Win: `C:\ProgramData\AutoMouseMover\`, macOS: `~/Library/Logs/`), with a
      console-only fallback if the path is not writable.
- [x] Logs start, stop, interval, and errors only — **never** user activity (SR-3).

**Exit criteria:** ✅ behavior fully driven by `config.json`; log file shows start/stop/interval (verified).

---

## Phase 4 — Packaging (Standalone Binaries) ✅
**Goal:** distributable executables, no Python required on the target (§13, §14).

- [x] Added `pyinstaller` to `requirements-dev.txt`.
- [x] macOS: `pyinstaller --onefile auto_mouse_mover.py` → `dist/auto_mouse_mover`
      (10 MB self-contained arm64 Mach-O); smoke-tested (`--help`, config validation).
- [x] Windows build command documented (`pyinstaller --onefile …` →
      `dist/auto_mouse_mover.exe`); must be run on Windows (cannot cross-build from macOS).
- [x] Build artifacts (`dist/`, `build/`, `*.spec`) gitignored — binaries are not committed.

**Exit criteria:** ✅ a single standalone macOS executable that runs the full app;
Windows build is one documented command away on a Windows host.

---

## Phase 5 — Documentation & Acceptance ✅
**Goal:** ship-ready repo (§22, §18).

- [x] `README.md`: solution design, flow diagrams, install, usage, all CLI flags,
      configure (config.json), stop methods, per-OS permission setup, packaging.
- [x] Acceptable-use note (legitimate keep-awake only) per §18 risk mitigations.
- [x] Deployment notes: Task Scheduler (Windows) and LaunchAgent (macOS) examples.
- [x] Final review against Security Requirements SR-1…SR-5 (see README "Security").

**Exit criteria:** ✅ a new user can install/run from the README with no extra help.

---

## Phase 6 — Future Enhancements (Backlog, optional) ⏳
Not required for the standalone deliverable; intentionally **not implemented**.
Pull in as needed (§20).

- [ ] System tray icon.
- [ ] Pause/resume hotkey.
- [ ] Signed Windows executable / notarized macOS app.
- [ ] Centralized / policy-based runtime limits for enterprise (Intune, Jamf, SCCM).

---

## Milestone Summary

| Phase | Outcome                          | Status                       |
| ----- | -------------------------------- | ---------------------------- |
| 0     | Repo scaffold + working venv     | ✅ Done                      |
| 1     | MVP script runs (FR-1…FR-4)      | ✅ Done                      |
| 2     | Cross-platform permission polish | ✅ Done                      |
| 3     | Config file + logging            | ✅ Done                      |
| 4     | PyInstaller binaries             | ✅ Done (macOS built)        |
| 5     | Docs + acceptance                | ✅ Done                      |
| 6     | Enhancements backlog             | ⏳ Optional — not started    |

**Definition of "standalone, done":** Phases 1–5 complete — a self-contained
executable (Phase 4) plus README, configurable via flags/`config.json`, with safe
stop controls and audit logging, meeting all functional and security requirements.
**Status: achieved ✅** (Phase 6 is an optional future backlog, by design.)
