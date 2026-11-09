#!/usr/bin/env python3
"""cad_export.py - CAD hand-off files from model.json (+ tiers.json, BOM) for the chosen software.

Usage: python cad_export.py SPEC_DIR OUT_DIR --target autocad|solidworks|fusion|freecad|all [--check]
Targets and what each gets (metadata mapped to that program's own fields - see references/cad-integration.md):
  autocad    : <base> 2D.dxf (R2018, mm, layers + linetypes, true DIMENSION entities, TITLE block with
               ATTRIBs, BOM + KEY text, DWGPROPS custom properties) and <base>.step (Z-up, for 3-D IMPORT)
  solidworks : <base> SW Y-up.step (named components), <base> SolidWorks Properties.bas (VBA macro that
               writes PartNo/Description/Material/ModelNo... custom properties), <base> 2D.dxf, BOM csv
  fusion     : <base> Fusion Build.py (script: components with partNumber/description, Y-up or Z-up aware),
               <base>.step, <base> 2D.dxf
  freecad    : <base> FreeCAD Build.FCMacro (App::Part assembly, typed properties, TechDraw third-angle
               page with filled template), <base>.step, <base>.FCStd when freecadcmd is installed
Units: everything exported in millimetres. Geometry = the simplified envelope solids in model.json.
Exit: 0 ok, 1 error, 2 usage. Missing optional libraries (cadquery for STEP, ezdxf for DXF) are reported, not fatal.
"""
import sys, os, json, math, csv, re, shutil, subprocess, datetime, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

def load(spec_dir):
    m = json.load(open(os.path.join(spec_dir, "model.json"), encoding="utf-8"))
    import brand; brand.apply(spec_dir, model=m)          # names come only from branding.json (asked of the user)
    tiers = None
    if os.path.exists(os.path.join(spec_dir, "tiers.json")): tiers = json.load(open(os.path.join(spec_dir, "tiers.json"), encoding="utf-8"))
    return m, tiers

def mm_factor(m):
    u = m.get("units", "mm").lower(); f = m.get("dim_factor", 1)
    return f * {"in": 25.4, "inch": 25.4, "mm": 1.0, "cm": 10.0, "m": 1000.0, "ft": 304.8}.get(u, 1.0)

def safe_name(s): return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(s)).strip("_")[:60]
def ident(m): return m.get("identity", {})
def base_name(m):
    i = ident(m); return f"{i.get('dwg_no', 'DWG')} {i.get('model_no', 'MODEL')}".strip()
def parts(m): return [p for p in m.get("parts", []) if p.get("shape", "box") != "line"]
def label(p): return f"{p.get('id', '')} {p.get('part_no', '')} {p.get('name', '')}".strip()

# ---------------- geometry in mm ----------------
def part_mm(p, f):
    q = dict(p)
    for k in ("p", "size"):
        if k in q: q[k] = [v * f for v in q[k]]
    for k in ("r", "h", "z"):
        if k in q: q[k] = q[k] * f
    if "pts" in q: q["pts"] = [[v * f for v in pt] for pt in q["pts"]]
    return q

def bounds_mm(m, f):
    import eng_elements as EE
    (x0, x1), (y0, y1), (z0, z1) = EE._bounds(m); return (x0 * f, x1 * f), (y0 * f, y1 * f), (z0 * f, z1 * f)

# ---------------- STEP (cadquery) ----------------
def export_step(m, path, yup=False):
    try:
        import cadquery as cq
    except ImportError:
        return "cadquery not installed - STEP skipped (pip install cadquery, or run the FreeCAD/Fusion script which builds the same solids)"
    f = mm_factor(m); i = ident(m)
    assy = cq.Assembly(name=safe_name(f"{i.get('model_no', 'MODEL')}_{i.get('model', '')}"))
    for p in parts(m):
        q = part_mm(p, f); sh = q.get("shape", "box")
        if sh == "box":
            solid = cq.Workplane("XY").box(*q["size"], centered=False).translate(tuple(q["p"]))
        elif sh in ("cyl", "cylinder"):
            ax = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[q.get("axis", "z")]
            solid = cq.Workplane("XY").add(cq.Solid.makeCylinder(q["r"], q["h"], cq.Vector(*q["p"]), cq.Vector(*ax)))
        elif sh == "prism":
            solid = cq.Workplane("XY").polyline([tuple(v) for v in q["pts"]]).close().extrude(q["h"]).translate((0, 0, q["z"]))
        else: continue
        if yup: solid = solid.rotate((0, 0, 0), (1, 0, 0), -90)
        assy.add(solid, name=safe_name(label(p)), color=cq.Color(0.55, 0.65, 0.8))
    assy.save(path, exportType="STEP")
    return None

# ---------------- DXF (ezdxf) ----------------
def export_dxf(m, path, tiers=None, bom=None):
    try:
        import ezdxf
        from ezdxf.enums import TextEntityAlignment
    except ImportError:
        return "ezdxf not installed - DXF skipped (pip install ezdxf)"
    import eng_elements as EE
    f = mm_factor(m); i = ident(m); (x0, x1), (y0, y1), (z0, z1) = bounds_mm(m, f)
    L, Wd, H = x1 - x0, y1 - y0, z1 - z0; gap = max(L, Wd, H) * 0.35; th = max(L, Wd, H) / 60
    doc = ezdxf.new("R2018", setup=True); doc.units = 4; doc.header["$INSUNITS"] = 4; doc.header["$MEASUREMENT"] = 1
    for name, color, lt, lw in (("OUTLINE", 7, "Continuous", 50), ("HIDDEN", 8, "DASHED", 25), ("CENTER", 4, "CENTER", 18), ("DIM", 3, "Continuous", 18),
                                 ("TEXT", 7, "Continuous", 25), ("TITLE", 7, "Continuous", 50), ("ISO", 5, "Continuous", 35), ("BOM", 7, "Continuous", 18), ("KEY", 2, "Continuous", 18), ("BORDER", 7, "Continuous", 70)):
        doc.layers.add(name, color=color, linetype=lt, lineweight=lw)
    ds = doc.dimstyles.duplicate_entry("Standard", "BLUEPRINT"); ds.dxf.dimtxt = th; ds.dxf.dimasz = th * .9; ds.dxf.dimexo = th * .4; ds.dxf.dimexe = th * .6
    msp = doc.modelspace()
    for k, v in (("COMPANY", i.get("company", "")), ("MODEL_NO", i.get("model_no", "")), ("DWG_NO", i.get("dwg_no", "")), ("MAKE", i.get("make", "")),
                 ("MODEL", i.get("model", "")), ("TIER_LABEL", i.get("tier_label", "")), ("TIER", i.get("tier", "")), ("OWNER", i.get("owner", "")), ("UNITS", "mm")):
        doc.header.custom_vars.append(k, str(v))
    # view origins (third-angle): FRONT at (0,0); TOP above; RIGHT to the right; ISO further right
    views = {"front": (0, 0), "top": (0, H + gap), "right": (L + gap, 0)}
    def proj(v, pt):
        x, y, z = pt
        if v == "front": return (x - x0, z - z0, -y)
        if v == "top": return (x - x0, y - y0, z)
        return (y - y0, z - z0, x)            # right
    for v, (ox, oy) in views.items():
        items = []
        for p in parts(m):
            q = part_mm(p, f); sh = q.get("shape", "box")
            if sh == "box": pts3 = [(q["p"][0] + a * q["size"][0], q["p"][1] + b * q["size"][1], q["p"][2] + c * q["size"][2]) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
            elif sh == "prism": pts3 = [(t[0], t[1], zz) for t in q["pts"] for zz in (q["z"], q["z"] + q["h"])]
            else:
                ax = q.get("axis", "z"); end = list(q["p"]); end["xyz".index(ax)] += q["h"]
                if ax == {"front": "y", "top": "z", "right": "x"}[v]:
                    c = proj(v, end if v != "front" else q["p"]); items.append(("circle", (c[0], c[1], q["r"]), max(proj(v, q["p"])[2], proj(v, end)[2]), p)); continue
                pts3 = EE._circle3(q["p"], q["r"], ax, 16) + EE._circle3(end, q["r"], ax, 16)
            pr = [proj(v, t) for t in pts3]; items.append(("rect", (min(t[0] for t in pr), min(t[1] for t in pr), max(t[0] for t in pr), max(t[1] for t in pr)), max(t[2] for t in pr), p))
        for kind, g, depth, p in items:
            hidden = False
            if kind == "rect":
                for k2, g2, d2, _ in items:
                    if k2 == "rect" and d2 > depth and g2[0] <= g[0] and g2[1] <= g[1] and g2[2] >= g[2] and g2[3] >= g[3] and g2 != g: hidden = True; break
                lay = "HIDDEN" if hidden else "OUTLINE"
                msp.add_lwpolyline([(ox + g[0], oy + g[1]), (ox + g[2], oy + g[1]), (ox + g[2], oy + g[3]), (ox + g[0], oy + g[3])], close=True, dxfattribs={"layer": lay})
            else:
                msp.add_circle((ox + g[0], oy + g[1]), g[2], dxfattribs={"layer": "OUTLINE"})
                for a, b in (((g[0] - g[2] * 1.3, g[1]), (g[0] + g[2] * 1.3, g[1])), ((g[0], g[1] - g[2] * 1.3), (g[0], g[1] + g[2] * 1.3))):
                    msp.add_line((ox + a[0], oy + a[1]), (ox + b[0], oy + b[1]), dxfattribs={"layer": "CENTER"})
        w_, h_ = {"front": (L, H), "top": (L, Wd), "right": (Wd, H)}[v]
        msp.add_linear_dim(base=(ox, oy - th * 4), p1=(ox, oy), p2=(ox + w_, oy), dimstyle="BLUEPRINT", dxfattribs={"layer": "DIM"}).render()
        msp.add_linear_dim(base=(ox + w_ + th * 4, oy), p1=(ox + w_, oy), p2=(ox + w_, oy + h_), angle=90, dimstyle="BLUEPRINT", dxfattribs={"layer": "DIM"}).render()
        msp.add_text(f"{v.upper()} VIEW", height=th * 1.4, dxfattribs={"layer": "TEXT"}).set_placement((ox + w_ / 2, oy + h_ + th * 2.5), align=TextEntityAlignment.MIDDLE_CENTER)
    # isometric (2-D projected edges)
    ix, iy = L + Wd + 2.2 * gap, H + gap * .5
    P = lambda t: (ix + (t[0] + t[1]) * math.cos(math.radians(30)), iy + (t[2] - (t[0] - t[1]) * .5))
    for p in parts(m):
        q = part_mm(p, f); sh = q.get("shape", "box")
        if sh == "box":
            (x, y, z), (a, b, c) = q["p"], q["size"]; V = [(x + i_ * a, y + j * b, z + k * c) for i_ in (0, 1) for j in (0, 1) for k in (0, 1)]
            for e1, e2 in ((0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)): msp.add_line(P(V[e1]), P(V[e2]), dxfattribs={"layer": "ISO"})
        elif sh in ("cyl", "cylinder"):
            ax = q.get("axis", "z"); end = list(q["p"]); end["xyz".index(ax)] += q["h"]
            for c in (q["p"], end): msp.add_lwpolyline([P(t) for t in EE._circle3(c, q["r"], ax, 36)], close=True, dxfattribs={"layer": "ISO"})
        elif sh == "prism":
            for zz in (q["z"], q["z"] + q["h"]): msp.add_lwpolyline([P((t[0], t[1], zz)) for t in q["pts"]], close=True, dxfattribs={"layer": "ISO"})
    msp.add_text("ISOMETRIC", height=th * 1.4, dxfattribs={"layer": "TEXT"}).set_placement((ix + (L + Wd) * .43, iy + H + gap * .6), align=TextEntityAlignment.MIDDLE_CENTER)
    # BOM + KEY text blocks
    by = -gap * 1.2; bx = 0
    rows = bom or [["ITEM", "PART NO.", "DESCRIPTION", "MATERIAL", "CALLOUT"]] + [[p.get("id", ""), p.get("part_no", ""), p.get("name", ""), p.get("material", ""), str(p.get("callout", "") or "")] for p in parts(m)]
    msp.add_text(f"PARTS LIST - MODEL {i.get('model_no', '')}", height=th * 1.3, dxfattribs={"layer": "BOM"}).set_placement((bx, by))
    for r_i, r in enumerate(rows): msp.add_text("   ".join(str(c) for c in r), height=th * .8, dxfattribs={"layer": "BOM"}).set_placement((bx, by - (r_i + 1.5) * th * 1.4))
    kx = L + gap; key = ["KEY", "OUTLINE - visible edges", "HIDDEN - hidden edges (dashed)", "CENTER - centrelines", "DIM - dimensions (mm)", "ISO - isometric projection", "BOM - parts list", "TITLE - title block (ATTRIBs)",
                         "Third-angle projection: TOP above FRONT, RIGHT to the right.", f"Units: millimetres. Model {i.get('model_no', '')}."]
    for k_i, t in enumerate(key): msp.add_text(t, height=th * (1.2 if k_i == 0 else .8), dxfattribs={"layer": "KEY"}).set_placement((kx, by - k_i * th * 1.4))
    # title block as a block with attributes (editable in AutoCAD: ATTEDIT / properties)
    tb = doc.blocks.new(name="TITLE_BLOCK"); tw, tht = th * 60, th * 14
    tb.add_lwpolyline([(0, 0), (tw, 0), (tw, tht), (0, tht)], close=True, dxfattribs={"layer": "TITLE"}); tb.add_line((0, tht * .55), (tw, tht * .55), dxfattribs={"layer": "TITLE"})
    fields = [("COMPANY", (tw * .02, tht * .7), 2.2), ("TITLE", (tw * .02, tht * .58), 1.2), ("MODEL_NO", (tw * .02, tht * .35), 1.2), ("DWG_NO", (tw * .35, tht * .35), 1.2),
              ("SHEET", (tw * .62, tht * .35), 1), ("SCALE", (tw * .8, tht * .35), 1), ("OWNER", (tw * .02, tht * .12), 1), ("DRAWN", (tw * .35, tht * .12), 1), ("CHECKED", (tw * .62, tht * .12), 1), ("DATE", (tw * .8, tht * .12), 1)]
    for tag, pos, hh in fields: tb.add_attdef(tag, insert=pos, height=th * hh, dxfattribs={"layer": "TITLE"})
    ins = msp.add_blockref("TITLE_BLOCK", (L + Wd + 2.2 * gap, by - th * 10), dxfattribs={"layer": "TITLE"})
    ins.add_auto_attribs({"COMPANY": i.get("company", ""), "TITLE": f"{i.get('make', '')} {i.get('model', '')}"[:60], "MODEL_NO": "MODEL NO. " + str(i.get("model_no", "")),
                          "DWG_NO": "DWG " + str(i.get("dwg_no", "")), "SHEET": "SHEET 1/1", "SCALE": "SCALE 1:1 (mm)", "OWNER": "OWNER " + str(i.get("owner", "")), "DRAWN": "DRAWN " + str(i.get("drawn", "")),
                          "CHECKED": "CHECKED " + str(i.get("checked", "")), "DATE": datetime.date.today().isoformat()})
    doc.saveas(path); return None

# ---------------- FreeCAD macro ----------------
def export_freecad(m, path, tiers=None):
    f = mm_factor(m); i = ident(m); L = []
    a = L.append
    a(f"# {i.get('company', '')} - FreeCAD build macro (Macro > Macros... > Execute, or: freecadcmd this_file)")
    a(f"# Model {i.get('model_no','')} - {i.get('make','')} {i.get('model','')} - units mm - generated {datetime.date.today()}")
    a("import FreeCAD as App, Part, os\nfrom FreeCAD import Vector, Rotation, Placement")
    a(f"doc = App.newDocument({json.dumps(safe_name(base_name(m)))})")
    a(f"doc.Company = {json.dumps(i.get('company',''))}; doc.CreatedBy = {json.dumps(i.get('drawn',''))}")
    a(f"doc.Comment = {json.dumps(f'MODEL {i.get(chr(109)+chr(111)+chr(100)+chr(101)+chr(108)+chr(95)+chr(110)+chr(111),chr(32))} | DWG {i.get(chr(100)+chr(119)+chr(103)+chr(95)+chr(110)+chr(111),chr(32))} | {i.get(chr(116)+chr(105)+chr(101)+chr(114)+chr(95)+chr(108)+chr(97)+chr(98)+chr(101)+chr(108),chr(84)+chr(105)+chr(101)+chr(114))}: {i.get(chr(116)+chr(105)+chr(101)+chr(114),chr(45))}')}")
    a("meta = dict(doc.Meta)")
    for k, v in (("ModelNo", i.get("model_no", "")), ("DwgNo", i.get("dwg_no", "")), ("Make", i.get("make", "")), ("Model", i.get("model", "")), ("TierLabel", i.get("tier_label", "")), ("Tier", i.get("tier", "")), ("Owner", i.get("owner", ""))):
        a(f"meta[{json.dumps(k)}] = {json.dumps(str(v))}")
    a("doc.Meta = meta")
    a(f"asm = doc.addObject('App::Part', {json.dumps(safe_name('ASM_' + str(i.get('model_no', 'MODEL'))))}); asm.Label = {json.dumps(f'{i.get(chr(109)+chr(111)+chr(100)+chr(101)+chr(108)+chr(95)+chr(110)+chr(111),chr(32))} {i.get(chr(109)+chr(111)+chr(100)+chr(101)+chr(108),chr(32))}')}")
    a("def props(o, d):\n    for k, v in d.items():\n        o.addProperty('App::PropertyString', k, 'Blueprint', k)\n        setattr(o, k, v)")
    for p in parts(m):
        q = part_mm(p, f); n = safe_name(p.get("id", "P")); sh = q.get("shape", "box")
        if sh == "box":
            a(f"o = doc.addObject('Part::Box', '{n}'); o.Length, o.Width, o.Height = {q['size'][0]:.3f}, {q['size'][1]:.3f}, {q['size'][2]:.3f}; o.Placement = Placement(Vector({q['p'][0]:.3f}, {q['p'][1]:.3f}, {q['p'][2]:.3f}), Rotation())")
        elif sh in ("cyl", "cylinder"):
            rot = {"z": "Rotation()", "x": "Rotation(Vector(0,1,0), 90)", "y": "Rotation(Vector(1,0,0), -90)"}[q.get("axis", "z")]
            a(f"o = doc.addObject('Part::Cylinder', '{n}'); o.Radius, o.Height = {q['r']:.3f}, {q['h']:.3f}; o.Placement = Placement(Vector({q['p'][0]:.3f}, {q['p'][1]:.3f}, {q['p'][2]:.3f}), {rot})")
        elif sh == "prism":
            pts = ", ".join(f"Vector({t[0]:.3f}, {t[1]:.3f}, {q['z']:.3f})" for t in q["pts"])
            a(f"o = doc.addObject('Part::Feature', '{n}'); w = Part.makePolygon([{pts}, Vector({q['pts'][0][0]:.3f}, {q['pts'][0][1]:.3f}, {q['z']:.3f})]); o.Shape = Part.Face(w).extrude(Vector(0, 0, {q['h']:.3f}))")
        a(f"o.Label = {json.dumps(label(p))}; o.Label2 = {json.dumps(p.get('name', ''))}")
        a(f"props(o, {json.dumps({'PartNumber': str(p.get('part_no', '')), 'Description': str(p.get('name', '')), 'Material': str(p.get('material', '')), 'Callout': str(p.get('callout', '') or ''), 'Qty': str(p.get('qty', 1)), 'ModelNo': str(i.get('model_no', ''))})})")
        a("asm.addObject(o)")
    a("doc.recompute()")
    a("# ---- TechDraw page: third-angle projection group + isometric, template fields filled ----")
    a("try:\n    import TechDraw\n    page = doc.addObject('TechDraw::DrawPage', 'Page'); tpl = doc.addObject('TechDraw::DrawSVGTemplate', 'Template')\n"
      "    cand = [os.path.join(App.getResourceDir(), 'Mod', 'TechDraw', 'Templates', n) for n in ('A3_LandscapeTD.svg', 'A3_Landscape_ISO7200TD.svg', 'A3_Landscape_blank.svg')]\n"
      "    tpl.Template = next((c for c in cand if os.path.exists(c)), cand[-1]); page.Template = tpl\n"
      f"    vals = {json.dumps({'DRAWING_TITLE': f'{i.get(chr(109)+chr(97)+chr(107)+chr(101),chr(32))} {i.get(chr(109)+chr(111)+chr(100)+chr(101)+chr(108),chr(32))}', 'PN': str(i.get('model_no', '')), 'FC-SH': '1/1', 'FC-SC': '1:1', 'AUTHOR_NAME': str(i.get('drawn', '')), 'FC-DATE': str(datetime.date.today()), 'COMPANY': str(i.get('company', ''))})}\n"
      "    et = dict(tpl.EditableTexts)\n    for k, v in vals.items():\n        if k in et: et[k] = v\n    tpl.EditableTexts = et\n"
      "    pg = doc.addObject('TechDraw::DrawProjGroup', 'ProjGroup'); page.addView(pg); pg.Source = [asm]; pg.ProjectionType = 'Third angle'\n"
      "    for v in ('Front', 'Top', 'Right'): pg.addProjection(v)\n"
      "    iso = doc.addObject('TechDraw::DrawViewPart', 'Isometric'); page.addView(iso); iso.Source = [asm]; iso.Direction = Vector(1, -1, 1); iso.X, iso.Y = 300, 200\n"
      "    doc.recompute()\nexcept Exception as ex:\n    App.Console.PrintWarning('TechDraw page skipped: %s\\n' % ex)")
    a(f"out = os.path.join(os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd(), {json.dumps(base_name(m))})")
    a("try:\n    import Import\n    Import.export([asm], out + ' (FreeCAD).step')\nexcept Exception as ex:\n    App.Console.PrintWarning('STEP export skipped: %s\\n' % ex)")
    a("doc.saveAs(out + '.FCStd')\nApp.Console.PrintMessage('Build complete: ' + out + '.FCStd\\n')")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")

# ---------------- Fusion 360 script ----------------
def export_fusion(m, path):
    f = mm_factor(m); i = ident(m)
    data = [{"id": p.get("id"), "label": label(p), "part_no": str(p.get("part_no", "")), "name": p.get("name", ""), "material": p.get("material", ""),
             **{k: v for k, v in part_mm(p, f).items() if k in ("shape", "p", "size", "r", "h", "axis", "pts", "z")}} for p in parts(m)]
    src = f'''# Blueprint package - Fusion build script. Fusion: Utilities > Scripts and Add-Ins > Scripts > + (create) and paste,
# or place this file in a folder and add it. Model {i.get("model_no","")} - {i.get("make","")} {i.get("model","")} - mm.
import adsk.core, adsk.fusion, traceback
IDENT = {json.dumps(i)}
PARTS = {json.dumps(data)}
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct); root = design.rootComponent
        yup = app.preferences.generalPreferences.defaultModelingOrientation == adsk.core.DefaultModelingOrientations.YUpModelingOrientation
        cm = 0.1   # Fusion API uses centimetres
        def P(x, y, z):   # model axes: x right, y back, z up  ->  Fusion (Z-up identical; Y-up = (x, z, -y))
            return adsk.core.Point3D.create(x * cm, z * cm, -y * cm) if yup else adsk.core.Point3D.create(x * cm, y * cm, z * cm)
        def Vd(x, y, z):
            return adsk.core.Vector3D.create(x, z, -y) if yup else adsk.core.Vector3D.create(x, y, z)
        root.partNumber = IDENT.get("model_no", ""); root.description = (IDENT.get("make", "") + " " + IDENT.get("model", "")).strip()
        for k in ("model_no", "dwg_no", "make", "model", "tier_label", "tier", "owner", "company"):
            design.attributes.add("Blueprint", k, str(IDENT.get(k, "")))
        tbm = adsk.fusion.TemporaryBRepManager.get()
        for p in PARTS:
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); comp = occ.component
            comp.name = p["label"][:100]; comp.partNumber = p["part_no"]; comp.description = p["name"]
            comp.attributes.add("Blueprint", "material", p.get("material", "")); comp.attributes.add("Blueprint", "model_no", IDENT.get("model_no", ""))
            body = None
            if p["shape"] == "box":
                x, y, z = p["p"]; a, b, c = p["size"]
                ctr = P(x + a / 2, y + b / 2, z + c / 2)
                obb = adsk.core.OrientedBoundingBox3D.create(ctr, Vd(1, 0, 0), Vd(0, 1, 0), a * cm, b * cm, c * cm)
                body = tbm.createBox(obb)
            elif p["shape"] in ("cyl", "cylinder"):
                x, y, z = p["p"]; d = {{"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}}[p.get("axis", "z")]; h = p["h"]
                body = tbm.createCylinderOrCone(P(x, y, z), p["r"] * cm, P(x + d[0] * h, y + d[1] * h, z + d[2] * h), p["r"] * cm)
            elif p["shape"] == "prism":
                sk = comp.sketches.add(comp.xYConstructionPlane if not yup else comp.xZConstructionPlane); lines = sk.sketchCurves.sketchLines; pts = p["pts"]
                for j in range(len(pts)):
                    a0, b0 = pts[j], pts[(j + 1) % len(pts)]
                    lines.addByTwoPoints(adsk.core.Point3D.create(a0[0] * cm, a0[1] * cm, 0), adsk.core.Point3D.create(b0[0] * cm, b0[1] * cm, 0))
                ext = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                ext.setDistanceExtent(False, adsk.core.ValueInput.createByReal(p["h"] * cm)); ext.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(p["z"] * cm))
                comp.features.extrudeFeatures.add(ext); continue
            if body is None: continue
            if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
                bf = comp.features.baseFeatures.add(); bf.startEdit(); comp.bRepBodies.add(body, bf); bf.finishEdit()
            else:
                comp.bRepBodies.add(body)
            if comp.bRepBodies.count: comp.bRepBodies.item(0).name = p["id"]
        ui.messageBox("Build complete - model " + IDENT.get("model_no", "") + ". Save as: " + IDENT.get("dwg_no", "") + " " + IDENT.get("model_no", ""))
    except:
        if ui: ui.messageBox("Failed:\\n" + traceback.format_exc())
'''
    open(path, "w", encoding="utf-8").write(src)

# ---------------- SolidWorks VBA ----------------
def export_solidworks(m, path):
    i = ident(m)
    rows = [(p.get("id", ""), str(p.get("part_no", "")), str(p.get("name", "")), str(p.get("material", "")), str(p.get("callout", "") or "")) for p in parts(m)]
    q = lambda s: str(s).replace('"', '""')
    L = ["' Blueprint package - SolidWorks custom-property macro", f"' Model {i.get('model_no','')} - {i.get('make','')} {i.get('model','')}",
         "' 1) File > Open the '... SW Y-up.step' (import as assembly).  2) Tools > Macro > New, paste this, Run (main).",
         "' Writes PartNo / Description / Material / Callout / ModelNo to each component and the assembly's own properties.",
         "Option Explicit", "Dim swApp As Object", "", "Sub SetP(mgr As Object, n As String, v As String)", "    mgr.Add3 n, 30, v, 2   ' swCustomInfoText, swCustomPropertyReplaceValue", "End Sub", "",
         "Sub main()", "    Dim doc As Object, mgr As Object, comps As Variant, c As Variant, cdoc As Object, nm As String",
         "    Set swApp = Application.SldWorks: Set doc = swApp.ActiveDoc", "    If doc Is Nothing Then MsgBox \"Open the imported STEP first.\": Exit Sub",
         "    Set mgr = doc.Extension.CustomPropertyManager(\"\")"]
    for k, v in (("Company", i.get("company", "")), ("ModelNo", i.get("model_no", "")), ("DwgNo", i.get("dwg_no", "")), ("Make", i.get("make", "")), ("Description", i.get("model", "")),
                 ("TierLabel", i.get("tier_label", "")), ("Tier", i.get("tier", "")), ("DrawnBy", i.get("drawn", "")), ("CheckedBy", i.get("checked", "")), ("Revision", "A")):
        L.append(f'    SetP mgr, "{k}", "{q(v)}"')
    L += ["    If doc.GetType <> 2 Then Exit Sub   ' 2 = assembly", "    comps = doc.GetComponents(False)", "    For Each c In comps", "        Set cdoc = c.GetModelDoc2", "        If Not cdoc Is Nothing Then",
          "            nm = UCase(c.Name2)", "            Set mgr = cdoc.Extension.CustomPropertyManager(\"\")"]
    for pid, pn, name, mat, co in rows:
        L.append(f'            If InStr(nm, "{q(safe_name(pid)).upper()}") = 1 Then SetP mgr, "PartNo", "{q(pn)}": SetP mgr, "Description", "{q(name)}": SetP mgr, "Material", "{q(mat)}": SetP mgr, "Callout", "{q(co)}": SetP mgr, "ModelNo", "{q(i.get("model_no", ""))}"')
    L += ["        End If", "    Next", "    MsgBox \"Properties written - model " + q(i.get("model_no", "")) + "\"", "End Sub"]
    open(path, "w", encoding="utf-8").write("\r\n".join(L) + "\r\n")

def export_bom_csv(m, path, flavour="generic"):
    i = ident(m)
    head = {"solidworks": ["ITEM NO.", "PartNo", "Description", "Material", "QTY.", "Callout", "ModelNo"], "fusion": ["Component", "Part Number", "Description", "Material", "Qty", "Callout", "Model No"],
            "freecad": ["Label", "PartNumber", "Description", "Material", "Qty", "Callout", "ModelNo"], "autocad": ["ITEM", "PART NO.", "DESCRIPTION", "MATERIAL", "QTY", "CALLOUT", "MODEL NO."]}.get(flavour, ["Item", "Part number", "Description", "Material", "Qty", "Callout", "Model number"])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(head)
        for p in parts(m): w.writerow([p.get("id", ""), p.get("part_no", ""), p.get("name", ""), p.get("material", ""), p.get("qty", 1), p.get("callout", "") or "", i.get("model_no", "")])

def export(spec_dir, out, targets):
    m, tiers = load(spec_dir); b = base_name(m); os.makedirs(out, exist_ok=True); made, notes = [], []
    tg = {"autocad", "solidworks", "fusion", "freecad"} if "all" in targets else set(targets)
    def step(yup=False):
        pth = os.path.join(out, f"{b} SW Y-up.step" if yup else f"{b}.step")
        if os.path.exists(pth): return
        err = export_step(m, pth, yup)
        (notes.append(err) if err else made.append(pth))
    def dxf():
        pth = os.path.join(out, f"{b} 2D.dxf")
        if os.path.exists(pth): return
        err = export_dxf(m, pth, tiers); (notes.append(err) if err else made.append(pth))
    if "autocad" in tg: dxf(); step(); export_bom_csv(m, os.path.join(out, f"{b} BOM (AutoCAD).csv"), "autocad"); made.append(os.path.join(out, f"{b} BOM (AutoCAD).csv"))
    if "solidworks" in tg:
        step(True); dxf(); pth = os.path.join(out, f"{b} SolidWorks Properties.bas"); export_solidworks(m, pth); made.append(pth)
        export_bom_csv(m, os.path.join(out, f"{b} BOM (SolidWorks).csv"), "solidworks"); made.append(os.path.join(out, f"{b} BOM (SolidWorks).csv"))
    if "fusion" in tg:
        step(); dxf(); pth = os.path.join(out, f"{b} Fusion Build.py"); export_fusion(m, pth); made.append(pth)
        export_bom_csv(m, os.path.join(out, f"{b} BOM (Fusion).csv"), "fusion"); made.append(os.path.join(out, f"{b} BOM (Fusion).csv"))
    if "freecad" in tg:
        step(); pth = os.path.join(out, f"{b} FreeCAD Build.FCMacro"); export_freecad(m, pth, tiers); made.append(pth)
        export_bom_csv(m, os.path.join(out, f"{b} BOM (FreeCAD).csv"), "freecad"); made.append(os.path.join(out, f"{b} BOM (FreeCAD).csv"))
        fc = shutil.which("freecadcmd") or shutil.which("FreeCADCmd")
        if fc:
            r = subprocess.run([fc, pth], cwd=out, capture_output=True, text=True, timeout=600)
            notes.append("FreeCAD headless build: " + ("ok" if r.returncode == 0 else "failed - open the macro in FreeCAD instead"))
        else: notes.append("freecadcmd not found - open the .FCMacro in FreeCAD (Macro > Macros > Execute) to build the .FCStd")
    return made, notes

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec_dir", nargs="?"); ap.add_argument("out", nargs="?"); ap.add_argument("--target", default="all"); ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        st = {}
        for mod in ("ezdxf", "cadquery"):
            try: __import__(mod); st[mod] = "ok"
            except ImportError: st[mod] = "missing (optional)"
        st["freecadcmd"] = shutil.which("freecadcmd") or shutil.which("FreeCADCmd") or "not found (optional)"; print(json.dumps(st, indent=1)); sys.exit(0)
    if not a.spec_dir or not a.out: ap.print_help(); sys.exit(2)
    made, notes = export(a.spec_dir, a.out, [t.strip().lower() for t in a.target.split(",")])
    print(json.dumps({"ok": True, "files": [os.path.basename(x) for x in made], "notes": notes}, indent=1))
if __name__ == "__main__": main()
