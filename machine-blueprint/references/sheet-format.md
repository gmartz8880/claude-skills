# Spec formats (JSON) read by make_all.py

Contents: 1 sheets.json (any machine, multi-sheet) · 2 element types · 2a electrical · 2b isometric ·
2c projection symbol · 3 panel.json (dashboard preset) ·
4 figures/*.json · 5 doc.json · 6 bom.csv · 7 layout grid & legibility rules
Worked examples: `templates/example-engine/` (2-sheet engine set + manual) and
`templates/example-vehicle-tundra/` (single dashboard sheet, poverty-button mode).

## 1. sheets.json
```
{"set": {"dwg_no","company","tagline","owner","machine_line","date","drawn","checked","scale","proprietary",
         "title_size": 56, "aging": {"stains": 3, "folds": [2, 2]}},
 "sheets": [ {"title","subtitle","block_title","sheet"(auto "n OF N"),"scale","title_block":true,
              "panels":[ PANEL, ... ]}, ... ]}
```
Sheet is 3300 x 2250 px. Keep panels inside x 100..3200, y 250..2150, and out of the title block
(1640..3180 x 1720..2150) unless `"title_block": false`.

PANEL types (all have `box:[x,y,w,h]`, optional `title`, `frame` (default true)):
| type | extra fields |
|---|---|
| view | `elements:[...]`, `origin:[dx,dy]` (offset inside box), `scale` (multiplies coordinates, not text), `caption` |
| table | `columns`, `col_x` (px offsets), `rows`, `size` (default 21), `row_h`, `footnotes`, `first_col_yellow` |
| specs | same as table, default columns ITEM / VALUE |
| notes / text | `lines:[...]`, `size` (22), `line_h` |
| legend | `items:[{"kind": line|hidden|center|dim|hatch|callout|blank|red, "label"}]` |
| revisions | `rows:[[rev,date,desc,by]]`, `sources:[...]`, `verify` |
A table titled with PARTS / BOM / BILL OF MATERIALS is exported automatically as `<DWG> Parts List.csv`.

## 2. Element types (inside view panels, coordinates relative to box + origin)
| t | fields |
|---|---|
| rect / switch / blank | x y w h [rx sw style dash label size] - `blank` = dashed yellow option slot |
| circle | x y r [label size sw style] |
| polygon | pts [fill sw style] |
| line | pts [style sw dash] |
| path | d: [["M",x,y],["L",x,y],["Q",cx,cy,x,y],["C",c1x,c1y,c2x,c2y,x,y],["Z"]] |
| arc | x y r start end (degrees, 0 = 3 o'clock, clockwise) |
| hidden | pts - dashed hidden edge |
| centerline | p1 p2 - dash-dot |
| dim | p1 p2 offset text [size] - linear dimension with extension lines + arrows (offset sign picks side) |
| diameter | c r angle text - leader-style diameter/radius callout |
| leader | pts (arrow tip first ... text end) text [text_style size] |
| hatch | x y w h or pts, angle spacing [outline] - section hatching |
| section | p1 p2 label [dir] - cutting-plane line with arrows + letters (A-A) |
| gear | x y r teeth [depth bore pitch] |
| spring | p1 p2 coils width |
| boltcircle | x y r n hole_r [phase] |
| arrow | p1 p2 |
| gauge | x y r label [label_dy] |
| vent | x y w h n |
| wheel | x y r hub spokes(deg list) hub_label |
| text | x y text [size style anchor(ls/ms/rs/mm/lm/rm) font(body/head/hand)] |
| callout | x y n - numbered yellow circle |
| image | path x y w h [invert] - your OWN line-art PNG (dark lines on white) tinted to blueprint white |
Styles: line (white) · dim (light blue) · blank (yellow) · red · pencil · or [r,g,b].

## 2a. Electrical schematic elements
| t | fields |
|---|---|
| esym | kind x y [rot 0/90/180/270, size (default 120), ref, label, label_dy, label_dy2, style, inner, w, h, letter] |
| wire | pts [label label_seg size style dots:[[x,y]...]] - conductor; dots = junctions |
| junction | x y - solder dot |
`esym` kinds: battery, fuse, fusible_link, switch, switch_nc, pushbutton, key_switch, relay (coil + NO contact
60 px above), solenoid, coil/inductor, transformer (ignition coil; primary terminals at y+14, secondary y-14),
resistor, diode, capacitor, lamp, motor, generator, sensor, meter, spark_plug, ground, chassis, connector,
box (module/ECU/rectifier: w, h, inner). Terminals sit at local (-size/2, 0) and (+size/2, 0) before rotation,
so wires end exactly at x +- 60 (size 120). Vertical symbols (rot 90/270) print ref + label to the right.
Layout tips: grid of 60 px; power rails on top, ground bus at the bottom; one ref designator per part
(BT1, F1, S1, K1, M1, T1, D1...); label every wire with gauge + colour; matching WIRE / CONNECTION table panel.

## 2b. Isometric element (`t: "iso"`)
```
{"t":"iso","x":900,"y":640,"scale":1.2,
 "solids":[{"type":"box","p":[x,y,z],"size":[dx,dy,dz]},
           {"type":"cyl","p":[x,y,z],"r":r,"h":h,"axis":"x|y|z","bore":r2},
           {"type":"prism","pts":[[x,y],...CCW],"z":z,"h":h},
           {"type":"line3","pts":[[x,y,z],...],"dash":true,"style":"dim"}],
 "dims":[{"p1":[x,y,z],"p2":[x,y,z],"off":[dx,dy,dz],"text":"L 15.6 in"}],
 "labels":[{"p":[x,y,z],"dx":px,"dy":px,"n":1} or {"p":..,"dx":..,"dy":..,"text":"..."}]}
```
World axes: x = width (left-right), y = depth (toward the viewer), z = up. True 30 deg isometric viewed from
+x +y +z, faces shaded (top lightest). Solids are painter-sorted by centre depth; give `order` to override.
Model the machine from 5-25 simple solids at real proportions (units = any, e.g. 1 unit = 0.03 in); add
overall L/W/H dims (off pushes the dimension line outward) and numbered callouts matching the other sheets.

## 2c. Projection symbol
`{"t":"projsym","x","y","size":1.5,"angle":"third|first"}` - put it on every multi-view sheet.

## 2d. model.json - the single 3-D source (drives iso, ortho views and every CAD export)
```
{"identity":{"make","model","model_no","year","tier_label","tier","dwg_no","company","owner","description"},
 "units":"in|mm|cm|m|ft","dim_factor":1,"dim_format":"{:.1f} in",
 "parts":[{"id":"P01","name":"Crankcase","part_no":"...","callout":4,"material":"...","qty":1,
           "shape":"box","p":[x,y,z],"size":[dx,dy,dz]} | {"shape":"cyl","p":[x,y,z],"r":..,"h":..,"axis":"x|y|z"}
           | {"shape":"prism","pts":[[x,y]...CCW],"z":..,"h":..}]}
```
Axes: X right, Y back, Z up (front view looks from -Y; vehicles: nose to +X). 10-40 envelope parts at true
proportions from published dimensions. Parts with `callout` get numbered leaders automatically.
- `{"t":"iso","model":"model.json"}` in a view panel: auto-fit, shaded, L/W/H dims, callouts on a ring.
- `{"t":"ortho","model":"model.json","view":"front|top|right|rear|left","x","y","scale","title"}`: projected
  view with overall dims; use the SAME scale for all three and place TOP above FRONT, RIGHT beside it.

## 2e. Trim / option matrix panel
`{"type":"matrix","box":[...],"title":"...","source":"tiers.json","size":19,"feature_w":1000,"rows_from":0,"rows_to":40}`
Draws tier headers (with codes), group bands and S/O/P/- symbols; legend at the bottom. Long matrices:
split across sheets with rows_from / rows_to. Format of tiers.json: references/vehicles-and-tiers.md.

## 2f. Automatic KEY & INDEX sheet
Sheet 1 is generated: sheet index, line & mark key, electrical symbol key, colour key, callout index from
model.json, abbreviations (`set.abbreviations` to override) and matrix/difficulty key. Disable only with
`set.key_sheet: false` (not recommended - the owner wants a key in everything).

## 3. panel.json (dashboard / control-panel preset - one sheet)
Fixed layout: drawing (origin 120,300), callout schedule (5 columns), general notes, legend, revisions,
detail box, title block. See the Tundra example; fields: `sheet{...}`, `drawing{origin,width,height,dim_label,elements}`,
`schedule{title,columns,rows,footnotes,size}`, `notes`, `legend_fitted`, `revisions`, `sources`, `verify_line`, `detail{title,elements,caption}`.

## 4. figures/<name>.json - schematics / block diagrams (1500 x 760)
`{"title","boxes":[{x,y,w,h,label,sub,style}],"wires":[{pts,style,label,lx,ly,sw}],"grounds":[[x,y]],"texts":[...],"notes":["..." or ["...","red"]]}`
Rendered + aged to `{work}/<name>.png` - reference that path from doc.json. Max 3 notes.

## 5. doc.json (or doc-1-*.json, doc-2-*.json ... one PDF per volume) - the Technical Manual
```
{"meta":{"company","tagline","doc_no","rev","date","title"(<br/> allowed),"cover_image":"{work}/blueprint.jpg",
         "cover_caption","applicability":[[k,v]],"stamps":{"1":"CONTROLLED COPY","4":"FIELD VERIFIED"},"signoff":[p,c,a]},
 "blocks":[ ... ]}
```
Blocks: `h1` `h2` `p` `bullets[]` `steps[]` `warn` `pagebreak` `table{rows,widths(in, total 6.6),size}`
`fig{path,caption,width}` `specs{rows}` `troubleshoot{rows: [symptom,cause,fix]}`
`procedure{title,purpose,tools[],caution,steps[],verify,fig,fig_caption}`
`feature{n,title,diff,where,trim,what,route_o,route_a,steps,verify,caution,fig,fig_caption}` (poverty-button callouts)
`sheets{caption}` - appendix: every drawing sheet on its own page, rotated to fill it.
`key{extra:[[term, meaning]]}` - key to symbols/abbreviations (required). `matrix{source}` - full trim/option matrix from tiers.json.
meta.model_no is required (cover + every page header).
Text accepts `<b> <u> <br/> &amp;`. Unicode arrows/stars are auto-converted to ASCII.

## 6. bom.csv (optional) - overrides the auto-exported parts list. First row = header.

## 7. Layout grid & legibility rules
- Text >= 19 px on sheets (labels 17+ only inside small drawn parts); tables 21-22 px; PDF body 10.8 pt.
- Leave 25 px padding inside every panel; check every label's right end stays inside its box.
- Long table cells: shorten, or widen `col_x`. Never shrink fonts below the minimums to make text fit.
