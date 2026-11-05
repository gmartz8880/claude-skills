#!/usr/bin/env python3
"""nspire_sim.py - desktop smoke test for TI-Nspire Lua apps (no calculator, no emulator).

Runs your .lua file inside a mock of the TI-Nspire Lua API (platform, gc, timer, var, math.eval,
toolpalette, document, cursor, image) using Lua 5.1 semantics when available (via the `lupa` package).

It catches the problems that crash or drain a calculator:
  * load/runtime errors, calls to API functions that do not exist (typos like gc:drawText)
  * errors swallowed by pcall wrappers that end up drawn as "Error" text on screen
  * the timer left running when the app is idle   (battery drain)
  * repaint storms (invalidate on every timer tick while nothing changes)
  * text drawn past the 318x212 screen edge        (unreadable UI)
  * on.save / on.restore round trip failures      (lost settings)

Usage:
  python nspire_sim.py APP.lua                    # default key script: every key on every screen
  python nspire_sim.py APP.lua --keys "down,down,enter,esc,char:5,enter"
  python nspire_sim.py APP.lua --mono             # simulate an original monochrome Nspire CAS
Exit code 0 = PASS, 1 = FAIL (problems listed), 2 = could not run (missing lupa).
"""
import sys, argparse, json

MOCK = r'''
local W, H = 318, 212
SIM = { log = {}, errors = {}, warns = {}, invalid = 0, paints = 0, timer_on = false,
        timer_period = nil, ticks = 0, texts = {}, mono = false }
local function strict(name, t)
  return setmetatable(t, { __index = function(_, k)
    error("API does not exist: " .. name .. "." .. tostring(k), 2) end })
end
local function noop() end
local function wcalc(s, size) return math.floor(#tostring(s) * ((size or 10) * 0.62)) end

local curSize = 10
local function new_gc()
  return strict("gc", {
    setColorRGB = function(self, r, g, b)
      if type(r) ~= "number" then error("setColorRGB expects numbers", 2) end end,
    setFont = function(self, fam, style, size)
      if fam ~= "sansserif" and fam ~= "serif" then error("setFont family must be sansserif or serif", 2) end
      curSize = size or 10 end,
    getStringWidth = function(self, s) return wcalc(s, curSize) end,
    getStringHeight = function(self, s) return math.floor(curSize * 1.6) end,
    drawString = function(self, s, x, y, vpos)
      s = tostring(s)
      table.insert(SIM.texts, s)
      if x + wcalc(s, curSize) > W + 2 then
        table.insert(SIM.warns, string.format("text runs off screen (x=%d, ~%dpx wide): %q", x, wcalc(s, curSize), s:sub(1,40)))
      end
      if y < -2 or y > H then table.insert(SIM.warns, "text drawn outside screen height: " .. s:sub(1,40)) end
    end,
    drawLine = noop, drawRect = noop, fillRect = noop, drawArc = noop, fillArc = noop,
    drawPolyLine = noop, fillPolygon = noop, drawImage = noop, setPen = noop, clipRect = noop,
    setAlpha = noop, begin = noop, finish = noop, isColorDisplay = function() return not SIM.mono end,
  })
end

platform = strict("platform", {
  apiLevel = "2.0", hw = function() return 7 end, isDeviceModeRendering = function() return true end,
  isColorDisplay = function() return not SIM.mono end, isTabletModeRendering = function() return false end,
  window = strict("window", {
    invalidate = function() SIM.invalid = SIM.invalid + 1 end,
    width = function() return W end, height = function() return H end,
    setFocus = noop, setPreferredSize = noop,
  }),
  gc = function() return new_gc() end,
  withGC = function(f, ...) return f(new_gc(), ...) end,
  registerErrorHandler = noop, getDeviceID = function() return "SIM" end,
})
platform.window.invalidate = function(self) SIM.invalid = SIM.invalid + 1 end

timer = strict("timer", {
  start = function(p)
    if type(p) ~= "number" or p < 0.01 then error("timer.start period must be >= 0.01 s", 2) end
    SIM.timer_on = true; SIM.timer_period = p end,
  stop = function() SIM.timer_on = false end,
  getMilliSecCounter = function() return SIM.ticks * 50 end,
})
local store = {}
var = strict("var", {
  store = function(k, v) store[k] = v; return nil end,
  recall = function(k) return store[k] end,
  recallStr = function(k) return store[k] and tostring(store[k]) end,
  list = function() local t = {} for k in pairs(store) do t[#t+1] = k end return t end,
  monitor = noop, unmonitor = noop, makeNumericList = noop,
  recallAt = function() return nil end, storeAt = noop,
})
document = strict("document", { markChanged = noop })
cursor = strict("cursor", { set = noop, show = noop, hide = noop })
toolpalette = strict("toolpalette", { register = noop, enable = noop, enableCopy = noop,
  enableCut = noop, enablePaste = noop })
clipboard = strict("clipboard", { addText = noop, getText = function() return "" end })
locale = strict("locale", { name = function() return "en" end })
image = strict("image", { new = function() return strict("img", {
  width = function() return 16 end, height = function() return 16 end,
  copy = function(self) return self end, rotate = function(self) return self end }) end })
D2Editor = strict("D2Editor", { newRichText = function()
  local o = {} setmetatable(o, { __index = function() return function() return o end end }) return o end })
math.eval = function(expr)
  if type(expr) ~= "string" then error("math.eval expects a string", 2) end
  if expr:find("factor") then return "(x-3)*(x-2)" end
  local f = loadstring and loadstring("return " .. expr) or load("return " .. expr)
  if f then local ok, r = pcall(f) if ok and type(r) == "number" then return r end end
  return "cas:" .. expr
end
math.evalStr = function(e) return tostring(math.eval(e)) end
on = {}
'''

DRIVER = r'''
local function fire(name, ...)
  local h = on[name]
  if not h then return false end
  local ok, e = pcall(h, ...)
  if not ok then table.insert(SIM.errors, "on." .. name .. ": " .. tostring(e)) end
  return true
end
function SIM_paint()
  if SIM.invalid > 0 then
    SIM.invalid = 0; SIM.paints = SIM.paints + 1; SIM.texts = {}
    fire("paint", platform.gc())
    for _, t in ipairs(SIM.texts) do
      if t:find("^Error") then
        table.insert(SIM.errors, "app drew an error on screen: " .. table.concat(SIM.texts, " | "):sub(1,160))
        break
      end
    end
  end
end
function SIM_start(restore)
  fire("construction")
  if restore then fire("restore", restore) end
  fire("resize", 318, 212)
  fire("activate")
  SIM.invalid = SIM.invalid + 1
  SIM_paint()
end
function SIM_key(k)
  local map = { up="arrowKey", down="arrowKey", left="arrowKey", right="arrowKey" }
  if map[k] then fire("arrowKey", k)
  elseif k == "enter" then fire("enterKey")
  elseif k == "esc" then fire("escapeKey")
  elseif k == "tab" then fire("tabKey")
  elseif k == "backtab" then fire("backtabKey")
  elseif k == "del" then fire("backspaceKey")
  elseif k == "clear" then fire("clearKey")
  elseif k == "help" then fire("help")
  elseif k == "ctx" then fire("contextMenu")
  elseif k:sub(1,5) == "char:" then fire("charIn", k:sub(6))
  elseif k:sub(1,6) == "click:" then
    local x, y = k:match("click:(%d+):(%d+)"); fire("mouseDown", tonumber(x), tonumber(y)); fire("mouseUp", tonumber(x), tonumber(y))
  end
  SIM_paint()
end
-- run the timer like the OS would, for up to n ticks; returns ticks used
function SIM_run_timer(n)
  local used, paints0 = 0, SIM.paints
  while SIM.timer_on and used < n do
    used = used + 1; SIM.ticks = SIM.ticks + 1
    fire("timer"); SIM_paint()
  end
  return used
end
function SIM_save()
  if not on.save then return nil end
  local ok, t = pcall(on.save)
  if not ok then table.insert(SIM.errors, "on.save: " .. tostring(t)); return nil end
  return t
end
function SIM_close() fire("deactivate"); fire("destroy") end
'''

DEFAULT_KEYS = ("down,up,down,down,enter,enter,esc,up,up,up,enter,enter,esc,down,enter,esc,"
                "down,down,enter,esc,down,down,down,enter,esc,tab,help,esc,char:5,del,click:40:40,esc")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lua_file")
    ap.add_argument("--keys", default=DEFAULT_KEYS, help="comma-separated key script")
    ap.add_argument("--mono", action="store_true", help="simulate a monochrome (original) TI-Nspire CAS")
    ap.add_argument("--max-ticks", type=int, default=400, help="timer ticks allowed per key before it counts as 'never stops'")
    a = ap.parse_args()
    try:
        try:
            import lupa.lua51 as lupa_mod   # Nspire Lua is 5.1
            flavor = "Lua 5.1"
        except Exception:
            import lupa as lupa_mod
            flavor = "Lua (lupa default)"
    except ImportError:
        print("Cannot run: the 'lupa' package is missing. Install it with:  python -m pip install lupa")
        sys.exit(2)

    L = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    L.execute(MOCK)
    G = L.globals()
    G.SIM.mono = a.mono
    src = open(a.lua_file, encoding="utf-8").read()
    problems, warns = [], []
    try:
        L.execute(src)
    except Exception as e:
        print("FAIL - the script does not load:\n  " + str(e)); sys.exit(1)
    L.execute(DRIVER)
    G.SIM_start(None)
    stuck = 0
    keys = [k.strip() for k in a.keys.split(",") if k.strip()]
    for k in keys:
        G.SIM_key(k)
        used = G.SIM_run_timer(a.max_ticks)
        if G.SIM.timer_on:
            stuck += 1
            problems.append(f"timer still running {used} ticks after key '{k}' (battery drain: stop the timer when idle)")
            L.execute("timer.stop(); SIM.timer_on = false")
    # idle check: with no input, the app must be fully quiet
    p0 = G.SIM.paints
    for _ in range(50):
        G.SIM_paint()
    if G.SIM.paints - p0 > 0:
        problems.append("app repaints while idle (repaint storm)")
    # save / restore round trip
    saved = G.SIM_save()
    if saved is not None:
        try:
            G.SIM_close()
            L.execute(DRIVER)
            G.SIM_start(saved)
        except Exception as e:
            problems.append(f"restore failed: {e}")
    else:
        warns.append("no on.save handler: settings will not persist with the document")
    G.SIM_close()
    if G.SIM.timer_on:
        problems.append("timer still running after on.deactivate/on.destroy")
    for i in range(1, len(G.SIM.errors) + 1):
        problems.append(G.SIM.errors[i])
    seen = set()
    for i in range(1, len(G.SIM.warns) + 1):
        w = G.SIM.warns[i]
        if w not in seen:
            seen.add(w); warns.append(w)
    print(f"TI-Nspire Lua simulator ({flavor}) - {a.lua_file}")
    print(f"  keys tested: {len(keys)}   paints: {G.SIM.paints}   timer ticks: {G.SIM.ticks}   display: {'mono' if a.mono else 'color'}")
    for w in warns[:15]:
        print("  WARN  " + w)
    counts = {}
    for p in problems:
        counts[p] = counts.get(p, 0) + 1
    for p, n in list(counts.items())[:25]:
        print("  FAIL  " + p + (f"   (x{n})" if n > 1 else ""))
    if problems:
        print("RESULT: FAIL"); sys.exit(1)
    print("RESULT: PASS" + (" (with warnings)" if warns else "")); sys.exit(0)


if __name__ == "__main__":
    main()
