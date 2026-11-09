---
name: machine-blueprint
description: Blueprint set + PDF technical manual for ANY machine or ENTIRE vehicle (every trim/option) from a model, part no. or VIN. Vintage blueprint style; AutoCAD/SolidWorks/Fusion/FreeCAD.
license: MIT
compatibility: Claude.ai, Claude Desktop, Cowork, Claude Code, Claude API (code execution). Python 3.8+. Windows, macOS, Linux. Optional ezdxf, cadquery, FreeCAD.
metadata:
  version: "2.3.0"
  author: gmartz8880
  dependencies: python>=3.8, pillow, numpy, reportlab (fonts bundled); optional ezdxf, cadquery
---

# Machine Blueprint

Turn any machine or an entire vehicle - identified by name, model number, part number, serial, VIN or a
photo - into a professional **vintage-blueprint drawing package** carrying the user's own names: an aged, old-school blueprint set, a
comprehensive technical manual (always PDF), every trim / package / option in the maker's own terms, model
numbers on everything, a key for everything, and - if the user works in CAD - files tailored to AutoCAD,
SolidWorks, Fusion or FreeCAD. Use it whenever someone wants a blueprint, schematic, dimensions, "how it
works", service/setup manual, trim or option breakdown, poverty-button map or CAD model of a vehicle, engine,
mower, tractor, tool, appliance, industrial or vintage machine - even if they only say "draw me my X".

## Deliverables
- `<DWG> <MODEL> Blueprint Set.pdf` - sheet 1 is an automatic **KEY & INDEX** (every line, symbol, colour,
  abbreviation, callout); then the required sheets: **multi-view** third-angle drawing (top / front / right,
  aligned) with **build dimensions**, shaded **isometric**, **electrical schematic(s)** with wire table, and for
  anything with tiers a **trim / package / option matrix**; plus sections, other systems, dashboard /
  controls, exploded parts and service data as the machine needs.
- `<DWG> <MODEL> Technical Manual.pdf` (or several volumes) - vintage typewritten manual on aged paper with
  a key section, the full option matrix, build dimensions, electrical section, procedures, troubleshooting,
  parts and a drawing appendix. **Never a Word document.**
- CAD target only: sheet PNGs, parts / matrix CSVs and a `CAD/` folder made for the chosen program.
- `<DWG> <MODEL> Package.zip` with everything; in chat: short summary + **parts to buy / key parts** with
  part numbers and a photo of each.

## Read first, every run
1. `references/style-preferences.md` - the owner's standing instructions. **When the owner asks for any
   change, add a dated line there in the same session and apply it**; those requests are permanent. If the
   skill folder is read-only, hand back the updated file or skill.
2. `references/scope-and-safety.md` - the few things not to draw and the cautions every package needs.

## Workflow
### Step 0 - Environment (automatic)
`python scripts/setup_env.py --json` (pillow, numpy, reportlab; optional ezdxf + cadquery for CAD files).
Build on the user's computer when connected (a project folder they choose), else here. Make a task list.

### Step 1 - Intake (one round with the question tool; skip what's already answered)
0. **Names - ask every time a name is needed or used; never invent or assume one.** Company / brand for the
   title block and manual cover, tagline (optional), owner, drawn by, checked by, approved by (optional),
   drawing-number prefix - plus any other name that comes up later (stamps, sign-offs, CAD author). Offer
   last-used names as a choice, but ask. Save with `python scripts/brand.py <spec_dir> --write '{...}'`.
1. Exact machine: model/year/serial/VIN; for vehicles cab/body, engine, drivetrain, trim/grade if known.
2. **"Will you use dedicated CAD software for this?"** No (default) -> PDF only. Yes -> **"Which one?"**
   AutoCAD / SolidWorks / Fusion / FreeCAD (multi-select). Save a stated "usual" program as a preference.
3. A photo of the machine or its dash/control panel (use any photo already sent).
Never ask for confirmation to proceed (names are always asked).

### Step 2 - Research (web, not memory)
`references/research-playbook.md` + for vehicles and anything tiered `references/vehicles-and-tiers.md`:
identity and model numbers, published dimensions, specs, every tier with the maker's own name and codes,
every package / option with codes, systems and wiring, procedures with real values, parts with numbers,
prices and dates. Keep a dated source list; mark each value verified or typical.

### Step 3 - Write the specs (copy the closest template, then edit; formats in `references/sheet-format.md`)
- `branding.json` - the names the user gave (step 1.0). Required.
- `model.json` - envelope 3-D model with identity + model no. and a `part_no` on every part. It drives the
  isometric, the orthographic views and every CAD export.
- `tiers.json` - all tiers / packages / options (S / O / P / -), tier codes, option codes.
- `sheets.json` - required sheets (multi-view via `ortho` or hand-drawn views + `projsym`, `iso`,
  electrical `esym` + wire table, `matrix`), plus what the machine needs (`references/drawing-set-guide.md`).
  Optional `panel.json` adds the dashboard / poverty-button sheet right after the key.
- `figures/*.json`, `doc.json` (or `doc-1-*.json`... volumes) following `references/manual-outline.md`
  including `{"key":{}}`, `{"matrix":{}}` and `{"sheets":{}}` blocks; `meta.model_no` set.
Templates: `templates/example-engine/` (machine, 6 sheets) and `templates/example-vehicle-tundra/`
(entire vehicle: multi-view, isometric, grade/package matrix, dashboard, added-circuit schematic).

### Step 4 - Check and render
`python scripts/check_specs.py <spec_dir>` (fix every ERROR - a missing name means: ask the user), then
`python scripts/make_all.py <spec_dir> <spec_dir>/out --target pdf` (or `autocad`, `solidworks`, `fusion`,
`freecad`, comma list, `all`). CAD details and metadata mapping: `references/cad-integration.md`.
If a CAD MCP connector (e.g. FreeCAD) is available, prefer it as that reference describes.

### Step 5 - Verify by looking (don't skip)
Open `preview-key.jpg`, `preview.jpg`, several sheets and manual pages (e.g. `pdftoppm -r 50`). Check: matches
the real machine/photo; views aligned; dimensions and model number present; no overlapping/clipped text;
callouts agree across key sheet, drawings and manual; matrix complete; cautions present. For CAD targets
re-open the DXF/STEP (ezdxf / cadquery) to confirm they load. Fix and re-render until clean.

### Step 6 - Deliver
Send the package zip and the PDFs (and the CAD folder files when targeted); save to the owner's PC folder when
connected. Reply briefly: what's in it, what's verified vs typical, how to open the CAD files in their
program, then **Parts to buy / key parts** with numbers and an image search per main part (chat only).

## Autonomy
Do the whole job without asking about routine steps. Ask only before buying, publishing or pushing anything
(including to GitHub), sending to other people, or deleting user files. Never change Claude's permissions or
security settings; if permission prompts slow things down, tell the user how to allow them in their own settings.

## Files
- `scripts/make_all.py` build + zip (`--target`) · `scripts/check_specs.py` standards linter · `scripts/brand.py` names · `scripts/setup_env.py`
- `scripts/render_sheet.py` sheets, key sheet, matrix, tables · `scripts/eng_elements.py` electrical symbols,
  isometric + orthographic from model.json, projection symbol · `scripts/render_blueprint.py` dashboard preset
- `scripts/cad_export.py` DXF / STEP / FreeCAD macro / Fusion script / SolidWorks VBA / BOMs
- `scripts/render_figure.py` · `scripts/age.py` · `scripts/paper.py` · `scripts/build_doc.py` · `scripts/_common.py`
- `references/` style-preferences (LIVE), scope-and-safety, research-playbook, vehicles-and-tiers,
  drawing-set-guide, manual-outline, sheet-format, cad-integration · `assets/fonts/` · `templates/`
