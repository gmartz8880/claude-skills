# Optimization rules: battery, stability, snappy feel

Every rule here is checked by `calc_lint.py` or `nspire_sim.py` where possible. Use the checklist at the end
before delivery.

## Where battery goes on these calculators
1. **Backlight** (largest single draw on color models) - you can only control it directly in CE C.
2. **CPU busy time** - a loop that spins waiting for a key keeps the CPU at full speed.
3. **Screen updates** - redrawing unchanged frames wastes CPU and LCD bus time.
4. **Staying on** - an app that never lets the OS auto-power-down drains overnight.

## TI-Nspire Lua
- Event-driven only. Never `while true do` / `repeat ... until false`. Work happens in on.* handlers.
- Timer: `timer.start(period)` only when animating; `timer.stop()` the moment animation ends, in
  `on.deactivate`, `on.destroy`, and on errors. 0.05 s for animation, 0.5-1 s for clocks.
- `platform.window:invalidate()` only after a state change. For small changes invalidate a rectangle:
  `platform.window:invalidate(x, y, w, h)`.
- Build fonts, images (`image.new`), tables, and layout once (top level / on.construction / on.resize). No
  allocation inside on.paint (it causes garbage collection pauses = stutter).
- Long calculations: split into chunks processed per timer tick and show progress; never block > 0.2 s.
- Wrap every handler in a `safe()` pcall helper; show errors on screen; stop the timer on error.
- Set `platform.apiLevel` as the first line (template: "2.0"). Request the lowest level that has the API you use.
- Persist with `on.save`/`on.restore` (validate everything restored) or `var.store` for values other pages use.
- Layout from `on.resize(w, h)`; it must work at 318x212 handheld and larger computer windows.
- Monochrome original CAS: `platform.isColorDisplay()` false -> use high-contrast grays, no color-only meaning.
- Touchpad: support `on.mouseDown` for main actions, plus keys for everything.

## TI-Nspire Python (CX II)
- `use_buffer()` once, `paint_buffer()` after each full frame (no flicker).
- Wait for keys with `get_key(1)` when supported; otherwise `time.sleep(0.05)` between `get_key()` checks.
- Redraw only when state changes. Keep lists small; catch `MemoryError`.
- Top-level try/except that shows the error on screen; esc always exits.

## TI-Nspire TI-Basic
- Put reusable math in `Func` (fast, returns values, uses CAS); use `Prgm` only for interaction.
- `Local` every temp variable. Validate with `getType(`. Use `Try ... Else ... EndTry` around risky math.
- `Request`/`RequestStr` wait for input without polling. Key loops: `getKey(1)` waits for a key.
- Libraries: `Define LibPub name()=...`, save in MyLib, Refresh Libraries.
- CX II drawing: `UseBuffer` ... `PaintBuffer` to avoid flicker.

## TI-84 Plus CE TI-BASIC
- Waiting for input: `Menu(`, `Input`, `Prompt`, `Pause` wait efficiently. Custom key loops must rest:
  `Repeat K:Wait .05:getKey→K:End` (Wait needs OS 5.2+; on older OS keep the loop minimal).
- **Never `Goto` out of an open `If-Then`/`For(`/`While`/`Repeat` block** - leaks memory until ERR:MEMORY.
  Leave the block via its End (use a flag), then Goto.
- Speed: `Ans` for temp values; avoid re-drawing the whole screen; `Output(` only the changed cell;
  `For(` loops are faster than `While` with manual counters; precompute constants; `DelVar` frees RAM.
- Store settings in a named list (e.g. `∟MYSET`) so they survive between runs; validate on load (`dim(`).
- Restore everything changed: `StoreGDB 1`/`RecallGDB 1`/`DelVar GDB1` for graph settings, `Float`, `Func`,
  `ClrHome` at the end. Archive the program on send so RAM clears do not delete it.
- Show "[on] to break" in help.

## TI-84 Plus CE Python
- `ti_system.wait_key()` waits without spinning. Validate `input()` with try/except ValueError.
- Heap is tiny: avoid big lists/strings, `del` large objects, avoid recursion depth.

## TI-84 Plus CE C (CEdev)
- `gfx_Begin(); gfx_SetDrawBuffer();` draw the frame, `gfx_SwapDraw();`. Draw only when `dirty`.
- `kb_SetMode(MODE_3_CONTINUOUS)` + edge detection (new presses only) for instant, repeat-free input.
- Idle: `delay(20-50)` between checks when nothing changes; dim backlight after ~20 s
  (`lcd_BacklightLevel`, restore on wake/exit); auto-save and exit after ~4 min idle (like OS APD).
- Optional: `boot_Set6MHzMode()` while dimmed, `boot_Set48MHzMode()` on wake/exit (test on hardware first).
- Integer/fixed-point math in hot paths (floats are software-emulated). `-Oz`, `COMPRESSED = YES`, `ARCHIVED = YES`.
- No big locals (4 KB stack); check every malloc/ti_Open; settings struct with version + checksum.
- Exit path restores: backlight, CPU speed, `kb_Reset()`, `gfx_End()`. Every path, including errors.
- Zero compiler warnings with `-Wall -Wextra`.

## Snappy feel (all platforms)
- First screen appears instantly: no splash delays, no loading work before the menu.
- Key response within one frame; highlight follows the arrow immediately.
- Menus wrap around top/bottom; esc/clear always goes back one level; selection is remembered.
- Long work shows progress and can be cancelled.

## Delivery checklist
- [ ] No busy-wait loop anywhere (lint clean)
- [ ] Timer/backlight/CPU/graph settings restored; temp vars deleted
- [ ] Every input validated; every IO/alloc checked; top-level error catch
- [ ] Redraw only on change; double buffer where available
- [ ] Clean exit from every screen; help + about screens; settings persist
- [ ] Text fits the screen (simulator WARN-free); readable at handheld size
- [ ] Logic tests pass; build report saved; test status stated honestly
