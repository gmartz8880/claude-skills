# TI-Nspire CX II (CAS) Python app skeleton - OS 5.2+
# Battery : waits for keys with a blocking call when the OS supports it; otherwise rests
#           50 ms between key checks. Draws only when something changed.
# Stability: all work is wrapped in try/except; the app always exits cleanly with [esc].
# Snappy  : ti_draw double buffering (use_buffer/paint_buffer) = no flicker.
# Controls: up/down move, enter select, esc back/quit
import time
try:
    from ti_draw import (clear, set_color, fill_rect, draw_text, use_buffer, paint_buffer,
                         get_screen_dim)
    from ti_system import get_key
    ON_CALC = True
except ImportError:                       # running on a computer for a quick logic test
    ON_CALC = False

TITLE, VERSION = "My Nspire App", "1.0"
ITEMS = ["Start", "Help", "About", "Quit"]


def wait_key():
    """Return the next key name without spinning the CPU."""
    try:
        k = get_key(1)                    # blocking wait on newer OS versions
        if k:
            return k
    except TypeError:
        pass
    while True:                           # older OS: rest between checks
        k = get_key()
        if k:
            return k
        time.sleep(0.05)


def screen(title, lines, sel=None):
    clear()
    w, h = get_screen_dim() if ON_CALC else (318, 212)
    set_color(24, 64, 120); fill_rect(0, 0, w, 22)
    set_color(255, 255, 255); draw_text(6, 17, title)
    for i, t in enumerate(lines):
        y = 46 + i * 22
        if i == sel:
            set_color(210, 228, 250); fill_rect(0, y - 16, w, 21)
        set_color(0, 0, 0); draw_text(14, y, t)
    set_color(90, 90, 90); draw_text(6, h - 6, "enter: select   esc: back")
    paint_buffer()


def info(title, lines):
    screen(title, lines)
    while wait_key() not in ("esc", "enter"):
        pass


def main():
    use_buffer()
    sel, dirty = 0, True
    while True:
        if dirty:
            screen(TITLE, ITEMS, sel); dirty = False
        k = wait_key()
        if k == "up":
            sel = (sel - 1) % len(ITEMS); dirty = True
        elif k == "down":
            sel = (sel + 1) % len(ITEMS); dirty = True
        elif k == "esc":
            return
        elif k == "enter":
            dirty = True
            if ITEMS[sel] == "Start":
                info("Main", ["Your app runs here."])
            elif ITEMS[sel] == "Help":
                info("Help", ["Arrows move, enter selects,", "esc goes back."])
            elif ITEMS[sel] == "About":
                info("About", [TITLE + " v" + VERSION])
            else:
                return


if ON_CALC:
    try:
        main()
    except Exception as e:                # show the problem instead of a silent crash
        clear(); set_color(200, 0, 0); draw_text(6, 30, "Error: " + str(e)[:40]); paint_buffer()
else:
    print(TITLE, "- logic test mode (ti_draw not available on this computer)")
