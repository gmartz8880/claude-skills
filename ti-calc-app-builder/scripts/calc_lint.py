#!/usr/bin/env python3
"""calc_lint.py - battery / stability / speed checks for TI calculator source code.

Supports:  .lua (TI-Nspire Lua)   .py (Nspire or CE Python)   .c/.cpp/.h (CE C toolchain)
           .txt/.basic/.8xp.txt (TI-84 Plus CE TI-BASIC)   .tib/.nsb (TI-Nspire TI-Basic text)

Usage:  python calc_lint.py FILE [FILE ...] [--target nspire|ce] [--json]
Exit 0 = no errors (warnings allowed), 1 = errors found.

Each finding: level (ERROR/WARN/TIP), category (battery|stability|speed|compat|ux), line, message, fix.
"""
import re, sys, json, os, argparse

F = []


def add(level, cat, path, line, msg, fix):
    F.append({"level": level, "category": cat, "file": os.path.basename(path), "line": line, "message": msg, "fix": fix})


def lint_lua(path, src):
    lines = src.splitlines()
    has = lambda pat: re.search(pat, src) is not None
    if has(r"\bwhile\s+true\s+do") or has(r"\brepeat\b[\s\S]*?until\s+false"):
        for i, l in enumerate(lines, 1):
            if re.search(r"while\s+true\s+do|until\s+false", l):
                add("ERROR", "battery", path, i, "Infinite loop. Nspire Lua is event-driven; a loop freezes the UI and burns battery.",
                    "Move the work into on.timer (start/stop it) or into the key/paint events.")
    if has(r"timer\.start") and not has(r"timer\.stop"):
        add("ERROR", "battery", path, 0, "timer.start is used but timer.stop never is: the timer runs forever.",
            "Stop the timer as soon as the animation ends and in on.deactivate.")
    if has(r"timer\.start") and not has(r"on\.deactivate|function\s+on\.deactivate"):
        add("WARN", "battery", path, 0, "No on.deactivate handler: the timer keeps running when the page is not visible.",
            "Add on.deactivate = function() timer.stop() end")
    for m in re.finditer(r"timer\.start\(\s*([0-9.]+)", src):
        if float(m.group(1)) < 0.03:
            ln = src[:m.start()].count("\n") + 1
            add("WARN", "battery", path, ln, f"Timer period {m.group(1)}s is very fast (>33 ticks/s).",
                "Use 0.05 s (20 fps) for animation, 0.2-1 s for clocks; nothing faster unless measured.")
    if not has(r"platform\.apiLevel"):
        add("WARN", "compat", path, 1, "platform.apiLevel is not set.",
            'Add platform.apiLevel = "2.0" (OS 3.2+) as the first line so behavior is predictable.')
    if not has(r"pcall"):
        add("WARN", "stability", path, 0, "No pcall anywhere: any runtime error kills the script for the rest of the session.",
            "Wrap event handlers in a safe() helper that pcalls and shows the error on screen.")
    if not has(r"on\.save|function\s+on\.save"):
        add("TIP", "ux", path, 0, "No on.save/on.restore: user settings will not persist.", "Return a small table from on.save and validate it in on.restore.")
    if not has(r"on\.resize|function\s+on\.resize"):
        add("WARN", "compat", path, 0, "No on.resize: layout will break on the computer software / different windows.",
            "Store w,h in on.resize and lay out from them.")
    if not has(r"on\.escapeKey|function\s+on\.escapeKey"):
        add("TIP", "ux", path, 0, "No on.escapeKey: users expect esc to go back.", "Handle esc for back/close.")
    for i, l in enumerate(lines, 1):
        if re.search(r"\b(io|os)\.\w+", l) and not l.strip().startswith("--"):
            add("ERROR", "compat", path, i, "io/os libraries do not exist in TI-Nspire Lua.", "Use var.store/var.recall or on.save for data.")
        if re.search(r"\brequire\s*\(?\s*[\"'](?!physics|color|strict)", l):
            add("WARN", "compat", path, i, "require() only loads built-in Nspire libraries (physics, color, strict).", "Inline the code instead.")
        if re.search(r"\bgoto\b|::\w+::", l):
            add("ERROR", "compat", path, i, "goto/labels are Lua 5.2+; TI-Nspire runs Lua 5.1.", "Restructure with loops/functions.")
        if re.search(r"string\.pack|utf8\.|table\.unpack|\bbit32\b", l):
            add("ERROR", "compat", path, i, "Lua 5.2+/5.3 function; not available in Nspire Lua 5.1.", "Use unpack(), string.byte/char.")
        if re.search(r"gc:drawText|gc:setColor\(|gc:print", l):
            add("ERROR", "compat", path, i, "Not a TI-Nspire gc method.", "Use gc:drawString(text,x,y,'top') and gc:setColorRGB(r,g,b).")
        if re.search(r"invalidate\(\)", l) and re.search(r"on\.timer|function on\.timer", "\n".join(lines[max(0, i-15):i])) and "if" not in "\n".join(lines[max(0, i-6):i]):
            add("TIP", "battery", path, i, "invalidate() in the timer without a change check.", "Only invalidate when the state actually changed.")
    # allocation inside on.paint
    m = re.search(r"on\.paint\s*=\s*\w*\(?function\s*\(gc\)([\s\S]*?)\nend\)?|function\s+on\.paint\s*\(gc\)([\s\S]*?)\nend", src)
    if m:
        body = m.group(1) or m.group(2) or ""
        if re.search(r"image\.new|\{\s*\}|table\.insert", body):
            add("WARN", "speed", path, src[:m.start()].count("\n") + 1, "Creates tables/images inside on.paint (garbage every frame = stutter).",
                "Build images/tables once (on.construction / top level) and reuse them.")


def lint_basic_ce(path, src):
    lines = src.splitlines()
    depth, block_lines = 0, []
    opens = re.compile(r"^(?:.*:)?\s*(Then|For\(|While |Repeat )")
    for i, raw in enumerate(lines, 1):
        for stmt in raw.split(":"):
            s = stmt.strip()
            if not s or s.startswith('"'):
                continue
            if s == "Then" or s.startswith("For(") or s.startswith("While ") or s.startswith("Repeat "):
                depth += 1; block_lines.append(i)
            elif s == "End":
                depth = max(0, depth - 1)
                if block_lines: block_lines.pop()
            elif s.startswith("Goto ") and depth > 0:
                add("ERROR", "stability", path, i, "Goto jumps out of an open If-Then/For/While/Repeat block: leaks memory, eventually ERR:MEMORY.",
                    "Leave the block first (set a flag, let it reach End) and Goto after the End.")
            elif s.startswith("Lbl ") and len(s[4:].strip()) > 2:
                add("ERROR", "compat", path, i, "Label names are 1-2 characters (A-Z, 0-9, θ).", "Rename the label.")
    if depth:
        add("ERROR", "stability", path, len(lines), f"{depth} block(s) opened without a matching End.", "Add the missing End.")
    for i, l in enumerate(lines, 1):
        if re.search(r"getKey", l):
            window = "\n".join(lines[max(0, i-3):i+2])
            if re.search(r"Repeat|While", window) and "Wait" not in window:
                add("WARN", "battery", path, i, "Key loop polls getKey with no rest: CPU runs flat out while waiting.",
                    "Add Wait .05 inside the loop (OS 5.2+), or use Menu(/Input/Pause which wait without spinning.")
        if re.search(r"AxesOff|GridOn|FnOff|PlotsOff", l) and not re.search(r"AxesOn|GridOff|FnOn|StoreGDB|RecallGDB", src):
            add("WARN", "ux", path, i, "Changes graph settings without restoring them.", "StoreGDB 1 at start, RecallGDB 1 + DelVar GDB1 at exit.")
        if re.search(r"ClrDraw", l) and "ClrHome" not in src:
            add("TIP", "ux", path, i, "Graph screen used but home screen not cleared on exit.", "End with ClrHome (and Disp a closing line) so the user is not left on a stale graph.")
        if re.search(r"Output\(\s*(\d+)", l):
            r = int(re.search(r"Output\(\s*(\d+)", l).group(1))
            if r > 10:
                add("ERROR", "compat", path, i, "Output( row >10: the CE home screen has 10 rows.", "Use rows 1-10, columns 1-26.")
        if re.search(r"Text\(\s*(\d+)\s*,\s*(\d+)", l):
            y, x = map(int, re.search(r"Text\(\s*(\d+)\s*,\s*(\d+)", l).groups())
            if y > 164 or x > 264:
                add("WARN", "compat", path, i, "Text( position near/over the CE graph screen edge (265x165).", "Keep Text(row 0-164, col 0-264).")


def _basic_cleanup(path, src):
    if "DelVar" not in src:
        add("TIP", "stability", path, 0, "No DelVar cleanup: temp variables stay in RAM after exit.", "DelVar the variables you used before the program ends.")


def lint_c(path, src):
    src = re.sub(r"/\*[\s\S]*?\*/", lambda m: "\n" * m.group(0).count("\n"), src)   # drop comments,
    src = re.sub(r"//[^\n]*", "", src)                                                # keep line numbers
    if "gfx_Begin" in src and "gfx_End" not in src:
        add("ERROR", "stability", path, 0, "gfx_Begin without gfx_End: the OS screen stays broken after exit.", "Call gfx_End() on every exit path.")
    if "gfx_Begin" in src and "gfx_SetDrawBuffer" not in src:
        add("WARN", "speed", path, 0, "Drawing straight to the screen: visible flicker/tearing.", "gfx_SetDrawBuffer() after gfx_Begin and gfx_SwapDraw() per frame.")
    for m in re.finditer(r"while\s*\(\s*!?\s*os_GetCSC\(\)\s*\)\s*;", src):
        add("WARN", "battery", path, src[:m.start()].count("\n") + 1, "Tight os_GetCSC() spin loop.", "Add delay(20-50) inside the wait loop or use kb_SetMode(MODE_3_CONTINUOUS)+delay.")
    for m in re.finditer(r"(\w+)\s*=\s*(?:\([^)]*\)\s*)?malloc\(", src):
        var = m.group(1)
        tail = src[m.end():m.end() + 300]
        if not re.search(r"if\s*\(\s*!\s*%s\b|%s\s*==\s*NULL|NULL\s*==\s*%s" % (var, var, var), tail):
            add("ERROR", "stability", path, src[:m.start()].count("\n") + 1, f"malloc result '{var}' not checked for NULL (CE heap is ~60 KB).", "Check for NULL and fail gracefully.")
    if re.search(r"ti_Open\(", src) and not re.search(r"if\s*\(\s*!\s*\w+\s*\)|==\s*0", src):
        add("WARN", "stability", path, 0, "ti_Open handle may not be checked.", "if (!h) handle the missing/full-memory case.")
    if "lcd_BacklightLevel" in src and src.count("lcd_BacklightLevel") < 2:
        add("ERROR", "stability", path, 0, "Backlight changed but never restored.", "Save the level at start and restore it on exit.")
    if "boot_Set6MHzMode" in src and "boot_Set48MHzMode" not in src:
        add("ERROR", "stability", path, 0, "CPU slowed to 6 MHz but never restored to 48 MHz.", "Call boot_Set48MHzMode() before exit and before heavy work.")
    if re.search(r"\bfloat\b|\bdouble\b", src):
        add("TIP", "speed", path, 0, "Floating point on the eZ80 is software-emulated and slow.", "Use integer / fixed-point math in hot loops.")
    if re.search(r"\b(\w+)\s+\w+\s*\[\s*(\d{4,})\s*\]", src):
        for m in re.finditer(r"^\s*(?!static)(?:unsigned\s+)?\w+\s+\w+\s*\[\s*(\d{4,})\s*\]\s*;", src, re.M):
            if int(m.group(1)) > 1024:
                add("WARN", "stability", path, src[:m.start()].count("\n") + 1, "Large local array: the CE stack is ~4 KB; this can crash.", "Make it static/global or malloc it.")


def lint_python(path, src, target):
    lines = src.splitlines()
    for i, l in enumerate(lines, 1):
        if re.search(r"^\s*import\s+(numpy|pandas|os|sys|tkinter|pygame|requests|threading)|^\s*from\s+(numpy|os|tkinter|pygame)\b", l):
            add("ERROR", "compat", path, i, "Module not available on TI calculator Python.", "Use math, random, time, ti_system, ti_draw (Nspire) / ti_plotlib.")
        if re.search(r"while\s+True\s*:", l):
            body = "\n".join(lines[i:i+12])
            if re.search(r"get_key\(\)", body) and not re.search(r"sleep|get_key\(1\)|wait_key", body):
                add("WARN", "battery", path, i, "Polling get_key() in a loop with no rest.", "Use get_key(1)/wait_key() or time.sleep(0.05) between checks.")
    if target == "nspire" and "ti_draw" in src and "use_buffer" not in src:
        add("WARN", "speed", path, 0, "ti_draw without use_buffer/paint_buffer flickers.", "Call use_buffer() once and paint_buffer() after each frame.")
    if re.search(r"range\(\s*\d{5,}", src) or re.search(r"\[0\]\s*\*\s*\d{4,}", src):
        add("WARN", "stability", path, 0, "Very large list/loop for calculator Python (small heap: MemoryError).", "Stream the work or shrink the data.")
    if "try" not in src:
        add("TIP", "stability", path, 0, "No try/except: a bad input ends the program with a traceback.", "Catch ValueError on input and Exception at top level.")


def lint_basic_nspire(path, src):
    if re.search(r"(?im)^\s*Define\s+\w+\(\)\s*=\s*Prgm", src) is None and re.search(r"(?im)Func|Prgm", src) is None:
        add("WARN", "compat", path, 1, "Nspire TI-Basic code must live inside Define name()=Prgm ... EndPrgm (or Func ... EndFunc).", "Wrap the code.")
    if re.search(r"(?i)\bLocal\b", src) is None:
        add("TIP", "stability", path, 0, "No Local declarations: variables leak into the problem.", "Declare Local for every temp variable.")
    if re.search(r"(?i)getKey\(\)", src) and re.search(r"(?i)getKey\(1\)", src) is None and re.search(r"(?i)\bWait\b", src) is None:
        add("WARN", "battery", path, 0, "getKey() polling loop without wait.", "Use getKey(1) (waits for a key) or add Wait 0.05.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--target", choices=["nspire", "ce"], default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    for p in a.files:
        src = open(p, encoding="utf-8", errors="replace").read()
        low = p.lower()
        if low.endswith(".lua"):
            lint_lua(p, src)
        elif low.endswith((".c", ".cpp", ".h", ".hpp")):
            lint_c(p, src)
        elif low.endswith(".py"):
            lint_python(p, src, a.target or ("nspire" if "ti_draw" in src and "get_key" in src else "ce"))
        elif low.endswith((".tib", ".nsb")) or (a.target == "nspire" and low.endswith(".txt")):
            lint_basic_nspire(p, src)
        else:
            lint_basic_ce(p, src); _basic_cleanup(p, src)
    if a.json:
        print(json.dumps(F, indent=1))
    else:
        if not F:
            print("calc_lint: no findings")
        for f in F:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"{f['level']:5} [{f['category']}] {loc}  {f['message']}\n       fix: {f['fix']}")
        e = sum(f["level"] == "ERROR" for f in F); w = sum(f["level"] == "WARN" for f in F)
        print(f"calc_lint: {e} error(s), {w} warning(s), {len(F)-e-w} tip(s)")
    sys.exit(1 if any(f["level"] == "ERROR" for f in F) else 0)


if __name__ == "__main__":
    main()
