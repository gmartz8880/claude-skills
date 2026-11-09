# CAD integration - AutoCAD, SolidWorks, Fusion, FreeCAD (and future connectors)

Contents: 1 output choice · 2 what each program gets · 3 metadata mapping · 4 axes & units ·
5 connectors (FreeCAD MCP and others) · 6 limits

## 1. Output choice (ask at intake, one question)
"Will you open this in dedicated CAD software?"  No -> `--target pdf` (default): PDFs only.
Yes -> "Which one?" AutoCAD / SolidWorks / Fusion (Fusion 360) / FreeCAD / several -> `--target autocad`
(or a comma list). The documentation is always PDF, never Word, whatever the target. Remember the answer
in references/style-preferences.md if the owner says it's their usual software.

## 2. What each target gets (from model.json via `scripts/cad_export.py`; all PDFs always included)
| Target | Files | How the user opens them |
|---|---|---|
| autocad | `<DWG> <MODEL> 2D.dxf` (R2018, mm): third-angle TOP/FRONT/RIGHT, isometric, layers OUTLINE / HIDDEN (DASHED) / CENTER / DIM / TEXT / TITLE / ISO / BOM / KEY, real DIMENSION entities (BLUEPRINT dimstyle), title block **block with ATTRIBs**, parts list + key text, DWGPROPS custom properties. `<base>.step` for 3-D (IMPORT). BOM csv | OPEN the DXF; IMPORT the STEP |
| solidworks | `<base> SW Y-up.step` (rotated for Y-up; each component named `ID_PARTNO_NAME`), `SolidWorks Properties.bas` VBA macro (writes PartNo, Description, Material, Callout, ModelNo per component + Company/ModelNo/DwgNo/Tier/DrawnBy/Revision on the assembly), `2D.dxf` (sketch/drawing import), BOM csv with SW property names | Open STEP as assembly -> Tools > Macro > New, paste .bas, run `main` |
| fusion | `Fusion Build.py` (creates a component per part with **partNumber** and **description**, design attributes `Blueprint.*`, handles Y-up or Z-up preference, cm conversion), `<base>.step`, `2D.dxf`, BOM csv | Utilities > Scripts and Add-Ins > + > run; or Upload STEP |
| freecad | `FreeCAD Build.FCMacro` (App::Part assembly, Part::Box/Cylinder/extrusions, Label = `ID PARTNO NAME`, Label2, typed properties group *Blueprint* PartNumber/Description/Material/Callout/Qty/ModelNo, doc.Company/Comment/Meta, **TechDraw page**: third-angle ProjGroup Front/Top/Right + isometric, template EditableTexts filled), `<base>.step`; `.FCStd` built automatically when `freecadcmd` is on PATH | Macro > Macros > Execute (or `freecadcmd file.FCMacro`) |

## 3. Metadata mapping (one source: model.json identity + parts)
| Field | AutoCAD | SolidWorks | Fusion | FreeCAD | STEP |
|---|---|---|---|---|---|
| Model no. | ATTRIB MODEL_NO, DWGPROPS MODEL_NO | custom prop ModelNo | root.partNumber, attr model_no | doc.Meta ModelNo, PN template field | assembly product name |
| Part no. | BOM text | PartNo | component.partNumber | PartNumber property | product name prefix |
| Description | BOM text | Description | component.description | Label2 / Description | product name |
| Material | BOM text | Material (text prop) | attr material | Material property | - |
| Callout | BOM text | Callout | - | Callout property | - |
| Dwg no. / company / drawn / checked | ATTRIBs | DwgNo / Company / DrawnBy / CheckedBy | design attributes | template fields, doc.Company | - |
| Tier (Grade/Trim/Series) | DWGPROPS TIER | TierLabel / Tier | attrs tier_label / tier | Meta TierLabel / Tier | - |

## 4. Axes and units
model.json uses standard CAD axes: **X right, Y toward the back, Z up**; the FRONT view looks from -Y.
Vehicles: nose toward +X (side elevation = FRONT view; END VIEW = right view shows the front of the vehicle).
Exports are millimetres (`units` + `dim_factor` convert). SolidWorks/Fusion Y-up: (x, y, z) -> (x, z, -y).

## 5. Connectors
If an MCP connector for FreeCAD (or AutoCAD / SolidWorks / Fusion) is available in the session (look for tool
names containing freecad, autocad, solidworks, fusion), prefer it: send model.json geometry + metadata,
build the parts there with the same names/properties, create the TechDraw/drawing sheet (third angle,
isometric, dimensions), export PDF/SVG/PNG of the drawing and bring it back as an `image` element on a sheet
(then it gets the title block and aging). Without a connector, generate the files in section 2.
Never require a connector: PDF output must always work.

## 6. Limits - say these plainly
- Geometry is a simplified envelope (boxes, cylinders, extrusions) built from published dimensions; it is for
  layout, mounting, clearance and documentation - not a manufacturer-accurate surface model.
- Native .dwg / .sldprt / .f3d / .FCStd files are produced by the program itself from the files above
  (FreeCAD .FCStd automatically when freecadcmd exists).
