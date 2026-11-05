---
name: ti-calc-app-builder
description: Builds TI-Nspire CAS and TI-84 Plus CE calculator apps (Lua, Python, TI-BASIC, C). Asks what the app should do, then codes, tests, and packages fast, stable, battery-friendly apps.
license: MIT (bundled tns_builder.py is a port of Luna, MPL-1.1)
compatibility: Claude.ai, Claude Desktop, Cowork, Claude Code, Claude API (code execution). Python 3.8+. Windows, macOS, Linux.
metadata:
  version: "1.0.0"
  author: Gabriel Martz
  dependencies: python>=3.8, tivars (pip), lupa (pip, optional), CEdev (only for C apps)
---

# TI Calculator App Builder

Turns "build me an app for my calculator that does X" into a finished, tested, installable app for
the **TI-Nspire CAS family** and/or the **TI-84 Plus CE**, tuned for battery life, stability, and a
snappy feel. You (Claude) do the whole job: ask the questions once, then pick the language, write the
code, test it, build the calculator file, and hand over install steps. Do not stop halfway to ask
permission for routine steps.

## Owner's calculators (defaults)

- **TI-Nspire CAS** - variant not yet confirmed. Ask once (Question 2 below): original CAS
  (monochrome, clickpad/touchpad), **CX CAS** (color, OS 3.x-4.x), or **CX II CAS** (color, OS 5.x-6.x).
  If the user does not know: CX II CAS if the screen is color and the case has a rounded "touchpad"
  with white/gray keys bought after 2019; otherwise CX CAS. The skill output must state which it assumed.
- **TI-84 Plus CE** - confirm the OS version and whether it is a Python edition.
- Save confirmed answers so they are never asked again (memory, or a note in the project's CLAUDE.md).

## Workflow (follow in order)

### Step 0 - Environment (silent, automatic)
Run `python scripts/setup_env.py --json` (add `--with-c` only when a C app is chosen). It checks first
and installs only what is missing. Do not ask before running it. If pip has no network (some Claude.ai
sandboxes), keep going: `.tns` building needs only the standard library, and for TI-BASIC you can
deliver the text source plus paste instructions. Never claim a tool ran if it did not.

### Step 1 - Intake (one round of questions, then work)
Use the built-in question tool (AskUserQuestion in Claude Code / Cowork, the multiple-choice question
card in the Claude apps). Fall back to a short numbered list in chat only if no question tool exists.
Ask everything in **one round** using `references/intake-questions.md`. Skip any question the user's
request already answered. Defaults when the user says "you pick": both calculators, stock (no
jailbreak), the language from the decision table, dark/light toggle, help screen, saved settings.

Ask a second round only if an answer is truly ambiguous and would change the build (for example "a game"
with no idea which game). Otherwise proceed.

### Step 2 - Pick the platform and language
Use `references/platforms.md`. Short version:

| Goal | TI-Nspire CAS (any) | TI-Nspire CX II CAS | TI-84 Plus CE |
|---|---|---|---|
| Interactive app, menus, graphics, games | **Lua** | **Lua** | **C** if jailbroken/OS <= 5.4, else **TI-BASIC** |
| Math / CAS formula tool | **TI-Basic Func** (uses CAS) or Lua + `math.eval` | same | **TI-BASIC** |
| Easy-to-read code the user will edit | Lua | **Python** | **Python** (Python edition only) or TI-BASIC |
| Max speed / best battery control | Lua (Ndless C only if user insists + OS supported) | same | **C (CEdev)** |

Explain the pick in one or two plain sentences. When building for **both**, write one shared spec
(features, screens, math, controls) and implement it twice with matching behavior; produce a parity table.

### Step 3 - Write a one-screen spec
App name (CE on-calc name: max 8 chars A-Z 0-9), purpose, screens, controls, math/logic with test
cases (inputs -> expected outputs), saved settings, language per calculator, and the feature pack items
included (`references/feature-pack.md`). Show it, then continue building in the same turn unless the
user asked to review first.

### Step 4 - Build from the templates
Start from the matching template in `templates/` (each one already implements the battery, stability,
and speed rules and the feature pack). Never start from a blank file.

| Template | Platform |
|---|---|
| `templates/nspire_lua_app.lua` | Nspire Lua: event-driven, pcall-safe handlers, timer only while animating, on.save/on.restore, touchpad, CAS via math.eval |
| `templates/nspire_python_app.py` | Nspire CX II Python: ti_draw double buffer, blocking key wait |
| `templates/nspire_basic_app.tib` | Nspire TI-Basic library Func + Prgm (LibPub) |
| `templates/ce_basic_app.txt` | CE TI-BASIC: Menu(, validated Input, Wait in key loops, cleanup |
| `templates/ce_python_app.py` | CE Python edition: wait_key, validated input |
| `templates/ce_c_app/` | CE C (CEdev v13-v15 verified): double buffer, dirty redraw, idle dim + auto-exit, checksummed settings |

Apply every rule in `references/optimization.md` for the chosen language. Use the API cheat sheets
(`references/nspire-lua-api.md`, `references/ce-reference.md`) instead of guessing function names.
Put pure math/logic in small functions and mirror it in a desktop Python test (`tests/test_logic.py`)
with the spec's test cases.

### Step 5 - Test (all must pass before delivery)
1. `python scripts/build.py SOURCE --target nspire|ce --name NAME --out dist` - runs the linter
   (`calc_lint.py`), the Nspire Lua desktop simulator (`nspire_sim.py`: crashes, wrong API names, timer
   left running, repaint storms, text off screen, save/restore), then builds. It stops on any ERROR.
2. Fix every ERROR and WARN (a WARN may stay only with a written reason in the report).
3. Run the logic tests (`python tests/test_logic.py`).
4. C apps: zero compiler warnings. If CEmu + the user's own ROM are available, run it there too.
5. Re-read the code once against `references/optimization.md` checklist.

### Step 6 - Deliver
Put everything in one folder `<AppName>/` and zip it:
- calculator files (`.tns`, `.8xp`, `.py`), full source, `BUILD_REPORT.md` (lint + sim + build results),
- `HOW-TO-INSTALL-AND-USE` guide (Word .docx when the user prefers Word, else Markdown): plain-language
  install steps per calculator, controls, features, troubleshooting, and what was and was not tested.
- In the reply: what was built, which language and why, how to install, and the honest test status
  ("tested in the desktop simulator and linter; not yet run on your physical calculator").

### Step 7 - Send to the calculator (when Claude can control the computer)
If you have computer use or are running locally (Claude Code / Cowork on the user's PC), you may open
TI Connect CE or the TI-Nspire software yourself and drag the file onto the connected calculator.
Ask the user only to plug in the cable. See `references/transfer-and-test.md`.
Do not change Claude's permissions, permission mode, or system security settings yourself. If repeated
permission prompts slow the job, point the user to `PERMISSIONS-SETUP.md` (options with undo steps) and
keep working.

## Hard rules
- Battery: no busy-wait loops; stop timers when idle; redraw only on change; restore backlight/CPU speed.
- Stability: every handler/IO call is error-checked; the app always has a clean exit ([esc]/[clear]/[on]);
  never leave the OS screen, graph settings, or variables in a changed state.
- Snappy: response to a key press within one frame; heavy work split into chunks or done once up front.
- Readability: plain-language labels, help screen, consistent keys (arrows, enter, esc/clear back).
- Never design an app to hide from or bypass Press-to-Test / exam mode. Note exam-mode behavior in the guide.
- Never invent API functions. If unsure, check the cheat sheet or the official docs, then test.
- Never say it was tested on a real calculator unless the user confirmed it ran.

## Files
- `scripts/setup_env.py` check-then-install environment
- `scripts/build.py` one-command lint -> simulate -> build -> report
- `scripts/tns_builder.py` pure-Python .tns builder (byte-identical to Luna 2.1 output)
- `scripts/nspire_sim.py` TI-Nspire Lua desktop simulator
- `scripts/calc_lint.py` battery/stability/speed/compatibility linter
- `PERMISSIONS-SETUP.md` optional ways for the user to reduce permission prompts
- `references/` platforms, intake questions, optimization rules, feature pack, API cheat sheets, transfer/test, troubleshooting
