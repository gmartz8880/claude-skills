# Owner style preferences (LIVE FILE - update it whenever the owner asks for a change)

These are the standing instructions for whoever uses this skill. Apply all of them on every run unless the
current request says otherwise. When the owner asks for any change to look, detail, wording, format or workflow,
ADD or EDIT a dated line here in the same session (newest at the bottom of its section) and apply it.

## Names - always ask, never assume
- Any time the package needs or uses a name, ASK the user for it: company / brand on the title block and
  manual cover, tagline, owner, drawn by, checked by, approved by, the drawing-number prefix, and any other
  name (QA stamp, sign-off, CAD author / company properties). Do not invent names and do not reuse names from
  an earlier run without asking - you may offer the last-used names as a one-click choice.
- Store the answers in the project's `branding.json` (`python scripts/brand.py <spec_dir> --write '{...}'`);
  every script reads names only from there. `check_specs.py` blocks rendering until they are filled in.
- Drawing numbers: `<dwg_prefix>-<3-letter model code>-<year>-<nn>` (e.g. ABC-TUN-2010-01).

## Look and feel
- Old-school engineering blueprint: Prussian-blue cyanotype sheet, white linework, border with zone
  letters/numbers, title block, general notes, legend, revisions block, detail views, callout schedule.
- Old fonts (stencil headings, typewriter text, hand-lettered signatures) and simulated old printing:
  paper grain, mottled exposure, fold creases, faint stains, edge wear, pin holes, torn corner, rubber stamps.
- **Legibility beats aging.** Body text Courier Prime Bold >= 22 px on the 3300 px sheet, >= 10.5 pt in the PDF;
  aging never covers linework or text.
- Technical document = vintage "Technical Order" on aged manila paper with typewriter text, CAUTION boxes,
  stamps and aged blueprint figures.

## Accuracy and detail
- The drawings must match the user's actual machine; trace from a photo when given and say so on the sheet.
- Detailed and technical: location, function, tier, OEM and aftermarket route, difficulty, steps, verification,
  cautions, wiring figures.
- End every reply with the exact part numbers to buy / key parts and a picture of each (chat only).

## Required content
- Every package: multi-view third-angle drawing with build dimensions, shaded isometric, electrical
  schematic(s) with wire table, key & index sheet, and a technical manual.
- Entire vehicles supported; for vehicles every trim / grade / package / option. Use the manufacturer's own
  name for tiers (Grade, Trim, Series, Package...).
- Model numbers in everything: sheets, title block, manual cover/headers, file names, CAD properties, BOMs,
  tier and option codes.
- A key for everything: key & index sheet first, key section in every manual, KEY layer in CAD exports.

## Output
- Ask once whether a dedicated CAD program will be used. Yes -> which (AutoCAD, SolidWorks, Fusion, FreeCAD)
  and tailor the exports and metadata. No -> export everything as PDF.
- Documentation is ALWAYS PDF - never a Word document.
- If a FreeCAD (or other CAD) MCP connector is available, prefer it (references/cad-integration.md).

## Workflow
- Build on the user's computer when it is connected, and also send the files in chat.
- Don't ask redundant confirmation questions; the request is the approval (names are the exception - ask).
