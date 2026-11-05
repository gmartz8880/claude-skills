# Platforms, models, and languages

Verified November 2026. Re-check jailbreak/OS support if the user's OS is newer than listed here.

## How to read the model and OS
| Calculator | Where |
|---|---|
| TI-Nspire (any) | Home > 5 Settings > Status (older OS: Settings > About). Also on the back label. |
| TI-84 Plus CE | [2nd] [mem] > 1:About. Python edition: "Python App" under [apps]. |

## TI-Nspire CAS family
| Model | Screen | Lua | Python | TI-Basic | C (Ndless) |
|---|---|---|---|---|---|
| TI-Nspire CAS (original, clickpad/touchpad) | 320x240, 16 grays | OS 3.0.2+ | no | yes (Func/Prgm) | older OS 3.x versions, see Ndless list |
| TI-Nspire CX CAS | 320x240 color | yes | no | yes | OS 4.5.x (e.g. 4.5.3.14, 4.5.4.48) |
| TI-Nspire CX II CAS (incl. -T/-C) | 320x240 color | yes (apiLevel up to 2.7) | OS 5.2+ | yes, plus UseBuffer/PaintBuffer and drawing commands | OS 5.2.0.771, 5.3.0.564, 6.2.0.333, 6.4.0.74 (6.3 must upgrade to 6.4.0.74) |

- Usable app area in a Lua page on the handheld: **318 x 212** (always read it from on.resize).
- CAS: Lua can call the CAS through `math.eval("solve(x^2=4,x)")`; TI-Basic Func/Prgm uses it directly.
- Press-to-Test (exam mode) hides existing documents and can disable Lua/Python; say so in the guide.
- Nspire file type: `.tns` (a TI document). Built by `scripts/tns_builder.py` for Lua and Python.
  TI-Basic is typed/pasted in the Program Editor (no reliable open-source text-to-.tns tool for TI-Basic).

## TI-84 Plus CE family
| Item | Value |
|---|---|
| CPU / screen | eZ80 48 MHz, 320x240 16-bit color (C full screen); home screen 26 x 10 chars; graph area 265 x 165 |
| Memory | ~150 KB user RAM, ~3 MB archive (flash) |
| TI-BASIC | every OS. `Wait` command OS 5.2+. Programs `.8xp`, on-calc name 1-8 chars A-Z 0-9 (first a letter) |
| Python | Python editions only (TI-84 Plus CE Python / CE-T Python). Small heap (tens of KB). Modules: math, random, time, ti_system, ti_plotlib, ti_hub, plus add-ons (ti_draw, ti_image on newer app versions). Send `.py` with TI Connect CE |
| C / C++ / assembly | CE C/C++ Toolchain (CEdev, v15 current, template verified on v13 and v15). Runs natively on OS <= 5.4. OS 5.5-5.8.4: needs arTIfiCE (v2.x); OS 5.8.5: arTIfiCE v3 (released Sept 2026). Always tell the user what their OS needs |
| Libraries for C | graphx, keypadc, fileioc, fontlibc... shipped as `clibs.8xg` (CE-Programming/libraries releases). Send once |
| TI-84 Evo (2025+, 156 MHz, new OS) | not a target of this skill's C path; TI-BASIC/Python only if TI documents support. Say so if asked |

## Language decision table
| Need | Nspire CAS pick | TI-84 Plus CE pick |
|---|---|---|
| Menus, graphics, animation, games | Lua | C (if jailbreak OK or OS <= 5.4), else TI-BASIC |
| Symbolic math, solving, exact answers | TI-Basic Func (library) or Lua + math.eval | TI-BASIC (numeric solver, `solve(`/`nDeriv(`/`fnInt(`) |
| Simple formula / quiz, easy to edit | Lua or Python (CX II) | TI-BASIC, or Python on Python editions |
| Long-running data work | Lua (timer-chunked) | C |
| Maximum battery control | Lua (event-driven) | C (dim backlight, 6 MHz idle, dirty redraw) |
| Must work on every unit, no install | Lua or TI-Basic | TI-BASIC |

## Sizes and limits to respect
- CE TI-BASIC: 10 home rows; `Output(` row 1-10, col 1-26; `Text(` row 0-164, col 0-264; lists max 999 elements.
- CE C: stack ~4 KB (no big local arrays), heap ~60 KB, appvar names <= 8 chars.
- Nspire Lua: Lua 5.1 (no goto, no integer division `//`, no utf8 lib); no io/os; fonts `sansserif`/`serif` sizes 7-24.
- Nspire Python: MicroPython-based, modules math, random, time, ti_system, ti_draw, ti_plotlib, ti_image, ti_hub.
