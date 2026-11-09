#!/usr/bin/env python3
"""make_all.py - one command from specs to the finished drawing package (names from branding.json - always asked, never assumed).

Usage: python make_all.py SPEC_DIR OUT_DIR [--target pdf|autocad|solidworks|fusion|freecad|all] [--no-zip] [--check]
  --target pdf (default, "no dedicated software"): PDFs only - Blueprint Set PDF (key sheet first) and the
           Technical Manual PDF(s). Parts list and trim matrix are inside the PDFs.
  --target <cad>: the PDFs PLUS files tailored to that program (see cad_export.py), sheet PNGs and CSVs.
  Several targets: --target autocad,freecad.  Documentation is ALWAYS PDF (never Word).
SPEC_DIR may hold: sheets.json and/or panel.json (dashboard sheet), model.json (3-D envelope, drives isometric,
orthographic views and CAD exports), tiers.json (every trim / package / option), figures/*.json,
doc.json or doc-*.json (one PDF per volume), bom.csv.
"""
import sys, os, json, glob, csv, zipfile, subprocess, datetime, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
BRAND = {}
def fname(s): return re.sub(r'[\\/:*?"<>|]+', "-", str(s)).strip()
def bom_rows(spec):
    for sh in spec.get("sheets", []):
        for p in sh.get("panels", []):
            if p.get("type") == "table" and any(w in p.get("title", "").upper() for w in ("PARTS", "BOM", "BILL OF MATERIAL")):
                return [p.get("columns", [])] + p["rows"]
    return None
def main():
    args = sys.argv[1:]; flags = [x for x in args if x.startswith("--")]; a = [x for x in args if not x.startswith("--")]
    target = "pdf"
    if "--target" in args:
        target = args[args.index("--target") + 1]; a = [x for x in a if x != target]
    if "--help" in flags or "-h" in args or not (a or flags): print(__doc__); sys.exit(0 if (a or flags) else 2)
    if "--check" in flags: sys.exit(subprocess.run([sys.executable, os.path.join(HERE, "setup_env.py"), "--check"]).returncode)
    targets = [t.strip().lower() for t in target.split(",")]; pdf_only = targets == ["pdf"]
    spec_dir = os.path.abspath(a[0]); out = os.path.abspath(a[1] if len(a) > 1 else "out"); work = os.path.join(out, "_work"); os.makedirs(work, exist_ok=True)
    import age, render_figure, build_doc, check_specs, brand
    global BRAND
    BRAND = brand.load(spec_dir)
    from PIL import Image
    report = check_specs.check(spec_dir)
    for w in report["warnings"]: print("WARN:", w, file=sys.stderr)
    if report["errors"]:
        for e in report["errors"]: print("ERROR:", e, file=sys.stderr)
        if "--force" not in flags: sys.exit(1)
    crisp, spec, dwg, model_no = [], {}, None, None
    if os.path.exists(os.path.join(spec_dir, "sheets.json")):
        import render_sheet
        spec = json.load(open(os.path.join(spec_dir, "sheets.json"), encoding="utf-8")); brand.apply(spec_dir, sheets=spec); dwg = spec["set"]["dwg_no"]; model_no = spec["set"].get("model_no")
    if os.path.exists(os.path.join(spec_dir, "panel.json")):
        import render_blueprint
        pj = json.load(open(os.path.join(spec_dir, "panel.json"), encoding="utf-8")); brand.apply(spec_dir, panel=pj); dwg = dwg or pj["sheet"]["dwg_no"]; model_no = model_no or pj["sheet"].get("model_no")
        crisp_panel = render_blueprint.render(pj, work)
    else: crisp_panel = None
    if spec:
        import render_sheet
        if crisp_panel:
            spec["_inserted"] = [pj["sheet"].get("block_title", pj["sheet"]["title"])]
            pj["sheet"]["sheet"] = f"2 OF {len(spec['sheets']) + 2}"; pj["sheet"].setdefault("model_no", model_no); crisp_panel = render_blueprint.render(pj, work)
        crisp = render_sheet.render(spec, work, spec_dir)
        if crisp_panel: crisp.insert(1, crisp_panel)          # dashboard sheet right after the key sheet
    elif crisp_panel: crisp = [crisp_panel]
    base = fname(f"{dwg} {model_no}" if model_no else dwg)
    sheets_png = []
    for i, c in enumerate(crisp, 1):
        ag = (spec.get("set") or {}).get("aging", {})
        o = os.path.join(work if pdf_only else out, f"{base} S{i}.png"); age.age(c, o, 6 + i, tuple(ag.get("folds", (2, 2))), ag.get("stains")); sheets_png.append(o)
        im = Image.open(o).convert("RGB"); im.save(os.path.join(work, f"sheet-{i:02d}.jpg"), quality=90)
        if i == min(2, len(crisp)): im.save(os.path.join(work, "blueprint.jpg"), quality=90)
        if i == 1 or i == min(2, len(crisp)): im.resize((im.width * 2 // 3, im.height * 2 // 3)).save(os.path.join(out, "preview.jpg" if i > 1 or len(crisp) == 1 else "preview-key.jpg"), quality=85)
    ims = [Image.open(p).convert("RGB") for p in sheets_png]
    set_pdf = os.path.join(out, f"{base} Blueprint Set.pdf"); ims[0].save(set_pdf, resolution=300, save_all=True, append_images=ims[1:])
    for f in sorted(glob.glob(os.path.join(spec_dir, "figures", "*.json"))):
        n = os.path.splitext(os.path.basename(f))[0]; c = os.path.join(work, n + "_crisp.png")
        fj = json.load(open(f, encoding="utf-8")); brand.apply(spec_dir, figure=fj); render_figure.render(fj, c); age.age(c, os.path.join(work, n + ".png"), 3)
    files = [set_pdf] + ([] if pdf_only else sheets_png)
    docs = sorted(glob.glob(os.path.join(spec_dir, "doc.json")) + glob.glob(os.path.join(spec_dir, "doc-*.json")))
    for dj in docs:
        tag = os.path.splitext(os.path.basename(dj))[0].replace("doc", "").strip("-")
        man = os.path.join(out, f"{base} Technical Manual{(' ' + tag.upper()) if tag else ''}.pdf"); dd = json.load(open(dj, encoding="utf-8")); brand.apply(spec_dir, doc=dd); build_doc.build(dj, man, os.path.join(work, "_paper"), work, dd); files.append(man)
    if not pdf_only:
        rows = list(csv.reader(open(os.path.join(spec_dir, "bom.csv"), encoding="utf-8"))) if os.path.exists(os.path.join(spec_dir, "bom.csv")) else bom_rows(spec)
        if rows:
            bom = os.path.join(out, f"{base} Parts List.csv"); csv.writer(open(bom, "w", newline="", encoding="utf-8")).writerows(rows); files.append(bom)
        if os.path.exists(os.path.join(spec_dir, "tiers.json")):
            t = json.load(open(os.path.join(spec_dir, "tiers.json"), encoding="utf-8")); mx = os.path.join(out, f"{base} Trim & Option Matrix.csv")
            with open(mx, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh); w.writerow(["Group", "Feature", "Code"] + [tr["name"] + (f" ({tr['code']})" if tr.get("code") else "") for tr in t["tiers"]])
                for g in t["groups"]:
                    for f_ in g["features"]: w.writerow([g["group"], f_["feature"], f_.get("code", "")] + f_["values"])
            files.append(mx)
        cad = [t for t in targets if t in ("autocad", "solidworks", "fusion", "freecad", "all")]
        if cad and os.path.exists(os.path.join(spec_dir, "model.json")):
            import cad_export
            cad_dir = os.path.join(out, "CAD"); made, notes = cad_export.export(spec_dir, cad_dir, cad); files += made
            for n_ in notes: print("NOTE:", n_, file=sys.stderr)
        elif cad: print("WARN: CAD target requested but no model.json - add one (references/sheet-format.md)", file=sys.stderr)
    readme = os.path.join(out, "README.txt")
    with open(readme, "w", encoding="utf-8") as fh:
        fh.write(f"{BRAND.get('company', '')} - DRAWING PACKAGE {dwg}\nMODEL NO. {model_no or '-'}\nOutput target: {target}\nGenerated {datetime.date.today():%d %b %Y}\n\nContents:\n")
        for f in files: fh.write(f"  - {os.path.relpath(f, out)}\n")
        fh.write("\nSheet 1 of the Blueprint Set is the KEY & INDEX - read it first.\nDocumentation is PDF. CAD files (if any) are in CAD/ and use millimetres.\n"
                 "Verify all specifications and part numbers against the manufacturer for your serial / VIN before work.\n")
    files.append(readme)
    if "--no-zip" not in flags:
        z = os.path.join(out, f"{base} Package.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files: zf.write(f, os.path.relpath(f, out))
    print(json.dumps({"ok": True, "out": out, "dwg": dwg, "model_no": model_no, "target": target, "sheets": len(sheets_png), "files": [os.path.relpath(f, out) for f in files]}))
if __name__ == "__main__": main()
