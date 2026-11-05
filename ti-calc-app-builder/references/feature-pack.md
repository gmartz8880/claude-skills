# Feature pack (included by default)

Include these unless the user says no. They make an app feel finished.

| Feature | Nspire Lua | Nspire Python | CE TI-BASIC | CE C |
|---|---|---|---|---|
| Main menu with wrap-around selection | yes | yes | `Menu(` | yes |
| Help screen (controls + what the app does) | menu item + help key | menu item | menu item | [mode] key |
| About screen (name, version) | yes | yes | yes | yes |
| Saved settings (dark mode, last choice) | on.save/on.restore | - (session only) | named list `∟APPNM` | appvar, archived, checksummed |
| Dark / light toggle | yes | optional | - | yes |
| Input validation with plain messages | yes | yes | yes | yes |
| Error screen instead of crash | pcall safe() | try/except | input checks | checked I/O |
| Clean exit from anywhere | esc | esc | Quit item / [on] | [clear] |
| Battery indicator | - | - | - | header icon |
| Idle saver (dim + auto-exit) | timer stopped when idle | blocking waits | blocking waits | dim 20 s, exit 4 min |
| Touchpad/mouse support | on.mouseDown | - | - | - |
| CAS results (exact + decimal) | math.eval | - | - | - |
| Logic unit tests on the PC | tests/test_logic.py | same | same | same |

Optional extras to offer when they fit the app: history of last results, unit switching, formula
reference page, high-score table (games), step-by-step solution view, quick "copy result" to a calculator
variable (`var.store` on Nspire, `→Ans`/list on CE), graph of the result, practice/quiz mode.
