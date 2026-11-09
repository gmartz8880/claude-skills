#!/usr/bin/env python3
"""check_specs.py - lint a spec folder BEFORE rendering so every package meets the owner's standard.

Usage: python check_specs.py SPEC_DIR [--json]      Exit 0 = no errors (warnings allowed), 1 = errors.
Errors: missing model number; missing multi-view (projsym / ortho), isometric, or electrical schematic
(esym) sheet - unless set.no_electrical is true; doc.json missing; a vehicle without tiers.json.
Warnings: BOM rows without part numbers, tiers rows whose value count != tier count, matrix overflow,
model.json parts without part_no, doc without key / matrix / sheets blocks, Word files in the folder.
"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def walk_elements(spec):
    for sh in spec.get("sheets", []):
        for p in sh.get("panels", []):
            for e in p.get("elements", []): yield sh, p, e
def check(spec_dir):
    E, W = [], []
    J = lambda n: json.load(open(os.path.join(spec_dir, n), encoding="utf-8")) if os.path.exists(os.path.join(spec_dir, n)) else None
    spec, panel, model, tiers = J("sheets.json"), J("panel.json"), J("model.json"), J("tiers.json")
    docs = sorted(glob.glob(os.path.join(spec_dir, "doc*.json")))
    if not spec and not panel: E.append("no sheets.json or panel.json")
    import brand
    miss = brand.missing(spec_dir)
    if miss: E.append("names not provided - ASK THE USER for: " + ", ".join(miss) + " (then: python brand.py SPEC_DIR --write '{...}')")
    st = (spec or {}).get("set", {})
    mno = st.get("model_no") or (panel or {}).get("sheet", {}).get("model_no") or (model or {}).get("identity", {}).get("model_no")
    if not mno: E.append("model number missing - set set.model_no (sheets.json), identity.model_no (model.json) and meta.model_no (doc.json)")
    if spec:
        kinds = {e.get("t") for _, _, e in walk_elements(spec)}; ptypes = {p.get("type") for sh in spec["sheets"] for p in sh.get("panels", [])}
        if not ({"projsym", "ortho"} & kinds): E.append("no multi-view sheet (needs a projsym or ortho element - third-angle top/front/right)")
        if "iso" not in kinds: E.append("no isometric drawing (iso element)")
        if "esym" not in kinds and not st.get("no_electrical"): E.append("no electrical schematic (esym elements) - or set set.no_electrical = true with a note")
        if not any(e.get("t") == "dim" for _, _, e in walk_elements(spec)) and "ortho" not in kinds: W.append("no dimension elements found - add build dimensions")
        is_vehicle = st.get("machine_class", "").lower() in ("vehicle", "car", "truck", "suv", "motorcycle", "atv", "utv", "van")
        if is_vehicle and not tiers: E.append("vehicle package needs tiers.json with every trim / package / option")
        if tiers and "matrix" not in ptypes: W.append("tiers.json present but no matrix panel on any sheet")
    if model:
        for q in model.get("parts", []):
            if not q.get("part_no"): W.append(f"model part {q.get('id')} has no part_no (use 'See maker parts list' if unknown)")
    if tiers:
        n = len(tiers["tiers"]); tl = tiers.get("tier_label")
        if not tl: W.append("tiers.json: set tier_label to the manufacturer's own word (Grade, Trim, Series, Package...)")
        for g in tiers["groups"]:
            for f in g["features"]:
                if len(f["values"]) != n: E.append(f"tiers.json: '{f['feature']}' has {len(f['values'])} values, expected {n}")
        for tr in tiers["tiers"]:
            if not tr.get("code"): W.append(f"tier '{tr['name']}' has no model / trim code")
    if not docs: E.append("no doc.json - the Technical Manual (PDF) is required")
    for dj in docs:
        d = json.load(open(dj, encoding="utf-8")); kinds = {next(iter(b)) for b in d.get("blocks", [])}
        if not d.get("meta", {}).get("model_no"): W.append(f"{os.path.basename(dj)}: meta.model_no missing")
        if "key" not in kinds: W.append(f"{os.path.basename(dj)}: add a {{'key': {{}}}} block (key to symbols)")
        if tiers and "matrix" not in kinds: W.append(f"{os.path.basename(dj)}: add a {{'matrix': {{}}}} block (all trims / options)")
        if "sheets" not in kinds: W.append(f"{os.path.basename(dj)}: add a {{'sheets': {{}}}} drawing appendix")
    if glob.glob(os.path.join(spec_dir, "*.docx")): W.append("Word files found - documentation must be PDF only")
    return {"errors": E, "warnings": W}
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"): print(__doc__); sys.exit(0 if a else 2)
    if a[0] == "--check": print("ready"); sys.exit(0)
    r = check(a[0])
    if "--json" in a: print(json.dumps(r, indent=1))
    else:
        for e in r["errors"]: print("ERROR:", e)
        for w in r["warnings"]: print("WARN: ", w)
        print("OK" if not r["errors"] else "FIX ERRORS BEFORE RENDERING")
    sys.exit(1 if r["errors"] else 0)
