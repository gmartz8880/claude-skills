# machine-blueprint

A Claude skill that turns any machine or entire vehicle - from a model name, model number, part number,
serial or VIN - into a vintage engineering drawing package:

- **Blueprint set (PDF)** - key & index sheet, third-angle multi-view drawing with build dimensions, shaded
  isometric, electrical schematics with wire tables, trim / package / option matrix (in the maker's own terms),
  sections, controls / dashboard, parts and service data. Model numbers on everything.
- **Technical manual (PDF, never Word)** - scope, safety, theory, specs, controls, procedures, troubleshooting,
  parts, key, drawing appendix.
- **Optional CAD files** tailored to AutoCAD (DXF + STEP), SolidWorks (STEP + property macro), Fusion
  (build script + STEP) or FreeCAD (build macro with TechDraw page + STEP).

The skill **asks for every name** it puts on a drawing or document (company, owner, drawn / checked by...)
and never invents one.

## Install
- Claude apps: Settings > Skills > Upload skill > choose the zip of this folder.
- Claude Code: copy this folder to `~/.claude/skills/machine-blueprint`.

## Quick test
```
python scripts/setup_env.py
python scripts/make_all.py templates/example-engine out            # PDFs only
python scripts/make_all.py templates/example-engine out --target freecad
```
The templates use placeholder names (EXAMPLE ENGINEERING CO.) - real runs ask you for yours.

Fonts in `assets/fonts` are OFL / Apache licensed (see FONTS-LICENSE.txt). Output files are generated locally
and are never part of this repository (see .gitignore).
