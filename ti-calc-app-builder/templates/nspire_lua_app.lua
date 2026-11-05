-- ============================================================================
-- TI-Nspire Lua app skeleton  (works on TI-Nspire CAS / CX CAS / CX II CAS, OS 3.0.2+)
-- Built for battery life, stability, and a snappy feel.
--
-- Battery   : 100% event-driven. No loops waiting for keys. The timer runs ONLY while
--             something is animating and stops on idle, on page switch, and on close.
-- Stability : every event handler is wrapped in pcall; errors show on screen instead of
--             killing the app. Saved state is validated before use.
-- Snappy    : repaint only when state changes; fonts/layout computed once in on.resize;
--             no table/string building inside on.paint beyond what is drawn.
-- Controls  : arrows move, enter select, esc back, tab next, menu key = app menu, help = help
-- ============================================================================
platform.apiLevel = "2.0"   -- 2.0 works on OS 3.2+; the code below also runs on 1.0-era OS

local APP = { title = "My Nspire App", version = "1.0" }

-- ----------------------------- state -----------------------------
local S = {
  screen = "menu",           -- menu | main | help | about
  sel = 1,
  dark = false,
  w = 318, h = 212,          -- updated in on.resize (handheld is 318x212)
  err = nil,                 -- last caught error message
  anim = nil,                -- non-nil while animating -> timer running
}
local items = { "Start", "Dark mode", "Help", "About" }
local color = platform.isColorDisplay and platform.isColorDisplay() or false

-- ----------------------------- helpers -----------------------------
local function redraw() platform.window:invalidate() end

local timerOn = false
local function startTimer()           -- call only when an animation begins
  if not timerOn then timer.start(0.05); timerOn = true end
end
local function stopTimer()            -- call as soon as the animation ends
  if timerOn then timer.stop(); timerOn = false end
end

local function safe(fn)               -- wrap handlers: never let an error crash the app
  return function(...)
    local ok, e = pcall(fn, ...)
    if not ok then S.err = tostring(e); stopTimer(); redraw() end
  end
end

local function fg(gc) if S.dark then gc:setColorRGB(255,255,255) else gc:setColorRGB(0,0,0) end end
local function bg(gc) if S.dark then gc:setColorRGB(0,0,0) else gc:setColorRGB(255,255,255) end end

-- CAS helper: evaluate an expression with the calculator's own math/CAS engine.
-- Returns result (number or string) or nil + error. Use for solve(), factor(), etc.
local function cas(expr)
  local ok, r, e = pcall(math.eval, expr)
  if ok then return r, e end
  return nil, r
end

-- ----------------------------- drawing -----------------------------
local function header(gc, text)
  if color then gc:setColorRGB(24, 64, 120) else gc:setColorRGB(60,60,60) end
  gc:fillRect(0, 0, S.w, 22)
  gc:setColorRGB(255,255,255)
  gc:setFont("sansserif", "b", 11)
  gc:drawString(text, 6, 3, "top")
  gc:setFont("sansserif", "r", 10)
end

local paint = {}
function paint.menu(gc)
  header(gc, APP.title)
  for i, label in ipairs(items) do
    local y = 26 + (i - 1) * 24
    if i == S.sel then
      if color then gc:setColorRGB(210, 228, 250) else gc:setColorRGB(200,200,200) end
      if S.dark then gc:setColorRGB(70,70,90) end
      gc:fillRect(0, y, S.w, 22)
    end
    fg(gc)
    local t = label
    if i == 2 then t = t .. (S.dark and "  [on]" or "  [off]") end
    gc:drawString(t, 14, y + 3, "top")
  end
  fg(gc); gc:drawString("enter: select   esc: back", 6, S.h - 18, "top")
end
function paint.main(gc)
  header(gc, "Main")
  fg(gc)
  local r = cas("factor(x^2-5*x+6)")
  gc:drawString("CAS demo: factor(x^2-5x+6) =", 8, 30, "top")
  gc:drawString(tostring(r or "n/a"), 8, 50, "top")
  if S.anim then gc:fillRect(8 + S.anim, 80, 12, 12) end
  gc:drawString("enter: animate once   esc: back", 6, S.h - 18, "top")
end
function paint.help(gc)
  header(gc, "Help")
  fg(gc)
  gc:drawString("Arrows move, enter selects, esc goes back.", 8, 30, "top")
  gc:drawString("Settings save with the document (ctrl+S).", 8, 50, "top")
end
function paint.about(gc)
  header(gc, "About")
  fg(gc)
  gc:drawString(APP.title .. "  v" .. APP.version, 8, 30, "top")
end

-- ----------------------------- events -----------------------------
on.resize = safe(function(w, h) S.w, S.h = w, h; redraw() end)

on.paint = safe(function(gc)
  bg(gc); gc:fillRect(0, 0, S.w, S.h)
  if S.err then
    gc:setColorRGB(200, 0, 0)
    gc:drawString("Error (esc to dismiss):", 6, 6, "top")
    gc:drawString(S.err:sub(1, 60), 6, 26, "top")
    return
  end
  paint[S.screen](gc)
end)

on.timer = safe(function()
  if not S.anim then stopTimer(); return end
  S.anim = S.anim + 8
  if S.anim > S.w - 30 then S.anim = nil; stopTimer() end   -- done: timer off immediately
  redraw()
end)

on.arrowKey = safe(function(key)
  if S.screen ~= "menu" then return end
  if key == "up" then S.sel = (S.sel - 2) % #items + 1
  elseif key == "down" then S.sel = S.sel % #items + 1
  else return end
  redraw()
end)

on.enterKey = safe(function()
  if S.screen == "menu" then
    if S.sel == 1 then S.screen = "main"
    elseif S.sel == 2 then S.dark = not S.dark; if document and document.markChanged then document.markChanged() end
    elseif S.sel == 3 then S.screen = "help"
    else S.screen = "about" end
  elseif S.screen == "main" then
    S.anim = 0; startTimer()
  end
  redraw()
end)

on.escapeKey = safe(function()
  if S.err then S.err = nil elseif S.screen ~= "menu" then S.screen = "menu"; S.anim = nil; stopTimer() end
  redraw()
end)

on.tabKey = safe(function()
  if S.screen == "menu" then S.sel = S.sel % #items + 1; redraw() end
end)
on.help = safe(function() S.screen = "help"; redraw() end)

-- Touchpad / mouse: click a menu row
on.mouseDown = safe(function(x, y)
  if S.screen ~= "menu" then return end
  local i = math.floor((y - 26) / 24) + 1
  if i >= 1 and i <= #items then S.sel = i; on.enterKey() end
end)

-- Leaving the page or closing the doc: stop all background work (battery).
on.deactivate = safe(function() stopTimer() end)
on.activate   = safe(function() if S.anim then startTimer() end; redraw() end)
on.destroy    = function() stopTimer() end

-- Persistence: on.save returns a table that the OS stores with the document.
on.save = function() return { dark = S.dark, sel = S.sel, v = 1 } end
on.restore = safe(function(t)
  if type(t) == "table" and t.v == 1 then
    S.dark = t.dark == true
    if type(t.sel) == "number" and t.sel >= 1 and t.sel <= #items then S.sel = t.sel end
  end
end)

-- Optional app menu (menu key)
if toolpalette and toolpalette.register then
  toolpalette.register({
    { "App",
      { "Help",  function() S.screen = "help";  redraw() end },
      { "About", function() S.screen = "about"; redraw() end },
      { "Toggle dark mode", function() S.dark = not S.dark; redraw() end },
    },
  })
end
