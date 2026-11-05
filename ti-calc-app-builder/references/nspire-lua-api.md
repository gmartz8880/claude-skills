# TI-Nspire Lua API cheat sheet (Lua 5.1)

Only functions listed here (or in TI's "TI-Nspire Lua Scripting API Reference Guide") exist. The
simulator raises "API does not exist" for anything else in `gc`, `platform`, `timer`, `var`, etc.

## Events (assign to `on.<name>`)
| Event | When |
|---|---|
| `construction()` | once at start (apiLevel 2.0+) |
| `resize(w, h)` | window size known/changed - do layout here |
| `paint(gc)` | draw the whole visible screen with `gc` |
| `activate()` / `deactivate()` | page shown / hidden - start/stop timers |
| `save()` -> table / `restore(t)` | persist state in the document |
| `destroy()` | script closing |
| `timer()` | after `timer.start(sec)` until `timer.stop()` |
| `arrowKey(key)` | "up" "down" "left" "right" |
| `enterKey()` `escapeKey()` `tabKey()` `backtabKey()` `returnKey()` `backspaceKey()` `deleteKey()` `clearKey()` | keys |
| `charIn(ch)` | typed characters (digits, letters, operators) |
| `contextMenu()` `help()` | ctrl+menu, help key |
| `mouseDown(x,y)` `mouseUp(x,y)` `mouseMove(x,y)` `grabDown(x,y)` | touchpad / mouse |
| `varChange(list)` | monitored variables changed (`var.monitor`) |

## Graphics context `gc`
`setColorRGB(r,g,b)`  `setFont(family, style, size)` family "sansserif"/"serif", style "r" "b" "i" "bi", size 7-24
`drawString(text, x, y, "top"|"middle"|"bottom"|"baseline")`  `getStringWidth(s)`  `getStringHeight(s)`
`drawLine(x1,y1,x2,y2)` `drawRect(x,y,w,h)` `fillRect(x,y,w,h)` `drawArc(x,y,w,h,start,arc)` `fillArc(...)`
`drawPolyLine({x1,y1,...})` `fillPolygon({...})` `setPen("thin"|"medium"|"thick", "smooth"|"dotted"|"dashed")`
`drawImage(img, x, y)` `clipRect("set"|"reset", x,y,w,h)`

## Platform / window / timer / data
`platform.apiLevel = "2.0"` (first line)  `platform.window:invalidate([x,y,w,h])`  `platform.window:width()/height()`
`platform.isColorDisplay()`  `platform.hw()`  `platform.isDeviceModeRendering()`
`timer.start(sec)` (>= 0.01)  `timer.stop()`  `timer.getMilliSecCounter()`
`var.store(name, value)`  `var.recall(name)`  `var.list()`  `var.monitor(name)`
`math.eval(expr)` -> result using the calculator engine (CAS on CAS models)  `math.evalStr(expr)`
`document.markChanged()`  `cursor.set("default"|"pointer"|...)`  `cursor.show()/hide()`
`toolpalette.register({ {"Menu", {"Item", fn}, ...}, ... })`  `clipboard.addText(s)` `clipboard.getText()`
`image.new(data)` (TI image string) `img:width()` `img:height()` `img:copy(w,h)`
`D2Editor.newRichText()` for editable text boxes (`:move`, `:resize`, `:setText`, `:getText`, `:registerFilter`)

## Not available
`io`, `os`, `require` of user files, `goto`, `//`, `utf8`, `string.pack`, `table.unpack` (use `unpack`), threads, sound.

## Patterns
```lua
local function safe(fn) return function(...) local ok,e = pcall(fn,...) if not ok then S.err=tostring(e); timer.stop(); platform.window:invalidate() end end end
on.paint = safe(function(gc) ... end)
```
Timer only while animating; stop on idle/deactivate. Layout in on.resize. Persist with on.save/on.restore.
