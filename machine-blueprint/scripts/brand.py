#!/usr/bin/env python3
"""brand.py - every name that appears on a drawing, manual or CAD file comes from branding.json.

The skill never invents or assumes a name: it ASKS the user for each one (company / brand, tagline, owner,
drawn by, checked by, approved by, drawing-number prefix) and writes their answers here.

Usage: python brand.py SPEC_DIR --check            -> exit 1 if branding.json is missing / incomplete
       python brand.py SPEC_DIR --write '{"company": "...", ...}'
Fields: company (required), owner (required), drawn (required), checked (required), approved (optional),
        tagline (optional), dwg_prefix (required, e.g. initials), proprietary (optional; built from company).
"""
import sys, os, json
REQUIRED = ("company", "owner", "drawn", "checked", "dwg_prefix")
PLACEHOLDERS = ("", "ASK", "TBD", "YOUR COMPANY", "?")
def load(spec_dir):
    p = os.path.join(spec_dir, "branding.json")
    b = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    b.setdefault("tagline", ""); b.setdefault("approved", "")
    b.setdefault("proprietary", f"PROPRIETARY - {b.get('company', '').upper()}. DO NOT SCALE DRAWING." if b.get("company") else "DO NOT SCALE DRAWING.")
    return b
def missing(spec_dir):
    b = load(spec_dir); return [k for k in REQUIRED if str(b.get(k, "")).strip().upper() in PLACEHOLDERS]
def apply(spec_dir, sheets=None, panel=None, doc=None, model=None, figure=None):
    """Inject the user's names into whichever spec dicts are given (in place)."""
    b = load(spec_dir)
    if sheets is not None:
        st = sheets.setdefault("set", {})
        for k in ("company", "tagline", "owner", "drawn", "checked", "proprietary"): st[k] = b.get(k, "")
    if panel is not None:
        sh = panel.setdefault("sheet", {})
        for k in ("company", "tagline", "owner", "drawn", "checked", "proprietary"): sh[k] = b.get(k, "")
    if doc is not None:
        m = doc.setdefault("meta", {}); m["company"] = b.get("company", ""); m["tagline"] = b.get("tagline", "")
        m["signoff"] = [b.get("drawn", ""), b.get("checked", ""), b.get("approved", "") or "________________"]
    if model is not None:
        i = model.setdefault("identity", {})
        for k in ("company", "owner", "drawn", "checked"): i[k] = b.get(k, "")
    if figure is not None: figure["company"] = b.get("company", "")
    return b
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"): print(__doc__); sys.exit(0 if a else 2)
    if a[0] == "--check": print("ready"); sys.exit(0)
    if "--write" in a:
        data = json.loads(a[a.index("--write") + 1]); p = os.path.join(a[0], "branding.json")
        cur = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}; cur.update(data)
        json.dump(cur, open(p, "w", encoding="utf-8"), indent=1); print(p); sys.exit(0)
    miss = missing(a[0])
    print("OK" if not miss else "ASK THE USER FOR: " + ", ".join(miss)); sys.exit(1 if miss else 0)
