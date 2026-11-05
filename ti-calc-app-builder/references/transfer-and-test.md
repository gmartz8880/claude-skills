# Transfer to the calculator and testing

## Tools (all free)
| Tool | For | Notes |
|---|---|---|
| TI Connect CE | TI-84 Plus CE: send .8xp/.8xv/.8xg/.py, screenshots, Program Editor | education.ti.com. Converts .py to Python AppVars on send |
| TI-Nspire CX Student / Premium Teacher Software (CAS versions) | Nspire: send .tns, Program Editor, Script Editor (Lua), emulator in Teacher version | Trial or license from TI |
| TI-Nspire Computer Link | Nspire: file transfer only | Free, lightweight |
| CEmu | TI-84 Plus CE emulator for testing C/BASIC | Needs a ROM dumped from the user's own calculator (ROM Dumper app in CEmu) |
| Firebird | Nspire emulator | Needs boot/flash images from the user's own calculator |
| Cemetech SourceCoder 3 | Online TI-BASIC editor + CE emulator | sc.cemetech.net |

## Sending, step by step
TI-84 Plus CE: open TI Connect CE > connect USB > Calculator Explorer > drag files > choose Archive >
Send. C programs also need clibs.8xg once. Run from [prgm].

TI-Nspire: open the TI-Nspire software (or Computer Link) > connect USB > Content/Documents workspace >
drag the .tns to the handheld folder. On the calculator: Home > My Documents > open.

## Autonomous sending (Claude Code / Cowork / computer use on the user's PC)
1. Ask the user once: "Plug in the calculator with the USB cable and turn it on."
2. Launch the transfer program yourself (Windows paths found by `setup_env.py`):
   `Start-Process "C:\Program Files (x86)\TI Education\TI Connect CE\TI Connect CE.exe"` (path may differ).
3. With computer use, drag the file from the dist folder onto the calculator in the app and confirm the
   transfer finished (file appears in the calculator list). Take a screenshot as proof.
4. On Linux, `tilp` can send from the command line: `tilp --no-gui file.8xp`.
If the app or cable is missing, say exactly what is needed and leave the files ready.

## Testing levels (report which ones ran)
1. Lint (`calc_lint.py`) - always.
2. Desktop simulator for Nspire Lua (`nspire_sim.py`) - always for Lua.
3. Logic tests on the PC (`tests/test_logic.py`) - always when there is math.
4. Compile with zero warnings - C.
5. Emulator run (CEmu / Teacher Software / SourceCoder) - when available.
6. Real calculator run - only the user can confirm; ask them to report back.
