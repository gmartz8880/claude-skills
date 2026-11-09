# Drawing-set guide - what to draw for any machine

Goal: a set a technician could actually use, drawn in vintage blueprint style. Pick the sheets that fit the
machine; most machines need 3-6 sheets. Every sheet gets title, subtitle, panels, title block.

## Required in EVERY package (owner standard)
A. **Multi-view orthographic sheet** - third-angle projection (US): TOP view directly above FRONT, RIGHT view
   to the right of FRONT, same scale, aligned edges, projection symbol, hidden lines and centerlines.
   Physical build dimensions on the views (overall L x W x H, mounting pattern, shaft/axle heights, key
   clearances) AND a BUILD DIMENSIONS table panel. Add an auxiliary/rear view when needed.
B. **Isometric sheet** - shaded true-isometric model of the whole machine (`iso` element) with overall
   L/W/H dimensions and numbered callouts, plus principal-data and callout-key panels.
C. **Electrical schematic sheet** - standard symbols (`esym`), every wire labelled gauge/colour, reference
   designators, power at top / ground at bottom, plus a WIRE / CONNECTION table and electrical notes.
   Split large systems over several schematic sheets (starting, charging, lighting, accessories...).
   A machine with no electrics gets a short "NO ELECTRICAL SYSTEM" note on the GA sheet instead.

## Standard sheet list (after A-C, add what applies)
1. **General Arrangement (GA)** - if A doesn't already cover it: principal-data specs panel,
   callouts 1..n for major components, general notes, legend.
2. **Sections & Details** - section A-A through the heart of the machine (hatched), enlarged details
   (Detail B, scale 2:1), fits/clearances, fastener details.
3. **Systems Schematics** - electrical (wiring/ladder), hydraulic (ISO-style symbols as boxes/lines),
   pneumatic, fuel/air, lubrication, cooling, drivetrain/power flow. One system per view panel.
4. **Controls & Operator Panel** - dashboard/control panel layout, every control labeled; blanks/options
   shown dashed (poverty-button mode = `panel.json` preset or a view panel with `blank` elements).
5. **Exploded View & Parts List** - exploded assembly with leader callouts + BOM table (item, description,
   part no., qty, note). Exported to CSV automatically.
6. **Service Data** - torque table, fluids & capacities, intervals, adjustment specs, wear limits.

## Machine-class checklists (add these views/data)
- Cars/trucks/motorcycles: dash map, fuse/relay box layout, wiring for added circuits, fluids, torque, lift points.
- Small engines / mowers / tractors: GA, section, ignition/fuel flow, PTO/belt routing, deck/blade, safety interlocks.
- Heavy / construction / ag equipment: hydraulic schematic, boom/linkage geometry, lift points, grease points map.
- Power tools & shop machines (lathe, mill, saw, press): GA, drive train/gear train, guards, controls, alignment procedure.
- Pumps, compressors, generators: P&ID-style flow, electrical one-line, duty data, maintenance.
- HVAC / appliances: refrigerant or air-flow schematic, control wiring, component layout.
- Electronics / control panels: panel layout, one-line + wiring diagrams, terminal tables.
- Marine / aviation (non-certified reference only): systems schematics, controls; state "not an approved document".
- Vintage / antique machines: same set, plus history and original-spec table; mark reproduction vs original parts.

## Drawing conventions
- Line weights: outlines sw 4-5, details 2-3, dims/centerlines thin `dim` colour.
- Hidden edges `hidden`, centerlines through every bore/shaft, `section` marks matching the section view title.
- Dimensions: label units; add "(REF)" or "APPROX." when not taken from a manufacturer drawing.
- Scale: state on each view ("SCALE 1:4 APPROX."). Proportions must be believable - derive from real
  dimensions (spec sheets, owner photos with a known reference, manuals). Never invent precise values.
- Callout numbers are unique across the whole set and match the manual.
- Own drawings only: redraw from research; do not trace or paste a manufacturer's copyrighted drawing.
