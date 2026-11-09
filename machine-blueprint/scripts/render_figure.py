#!/usr/bin/env python3
"""render_figure.py - draw a blueprint-style wiring / block diagram from a JSON spec (crisp PNG).

Usage: python render_figure.py FIG.json OUT.png [--check]
FIG.json: {"title","w","h","boxes":[{"x","y","w","h","label","sub","style"}],
           "wires":[{"pts":[[x,y],...],"style","label","lx","ly"}], "grounds":[[x,y]],
           "texts":[{"x","y","text","style","size"}], "notes":[["text","style"],...]}
styles: line | dim | blank (yellow) | red | pencil | "#rrggbb"-style RGB list. Run age.py afterwards.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from _common import BG, COL, colour, text
def render(spec, out):
    w, h = spec.get("w", 1500), spec.get("h", 760)
    img = Image.new("RGB", (w, h), BG); d = ImageDraw.Draw(img)
    for x in range(0, w, 25): d.line([(x, 0), (x, h)], fill=COL["grid"])
    for y in range(0, h, 25): d.line([(0, y), (w, y)], fill=COL["grid"])
    d.rectangle([10, 10, w - 10, h - 10], outline=COL["line"], width=3)
    text(d, 30, 56, spec["title"], 30, "line", "ls", "head"); text(d, w - 30, 52, spec.get("company", ""), 22, "dim", "rs", "head")
    for wi in spec.get("wires", []):
        d.line([tuple(p) for p in wi["pts"]], fill=colour(wi.get("style", "line")), width=wi.get("sw", 4), joint="curve")
        if wi.get("label"): text(d, wi["lx"], wi["ly"], wi["label"], 19, wi.get("style", "line"))
    for b in spec.get("boxes", []):
        c = colour(b.get("style", "line"))
        d.rounded_rectangle([b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]], 8, fill=COL["fill"], outline=c, width=3)
        cy = b["y"] + b["h"] / 2
        text(d, b["x"] + b["w"] / 2, cy - (10 if b.get("sub") else 0), b["label"], 24, b.get("style", "line"), "mm", "head")
        if b.get("sub"): text(d, b["x"] + b["w"] / 2, cy + 24, b["sub"], 20, "line", "mm")
    for gx, gy in spec.get("grounds", []):
        for i, wd in enumerate((30, 20, 10)): d.line([(gx - wd, gy + i * 8), (gx + wd, gy + i * 8)], fill=COL["dim"], width=3)
    for t in spec.get("texts", []): text(d, t["x"], t["y"], t["text"], t.get("size", 19), t.get("style", "line"), t.get("anchor", "ls"))
    for i, n in enumerate(spec.get("notes", [])):
        tx, st = (n, "dim") if isinstance(n, str) else n
        text(d, 30, h - 30 - (len(spec["notes"]) - 1 - i) * 38, tx, 24, st)
    img.save(out); return out
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"): print(__doc__); sys.exit(0 if a else 2)
    if a[0] == "--check": print("ready"); sys.exit(0)
    try: print(render(json.load(open(a[0], encoding="utf-8")), a[1]))
    except (KeyError, IndexError, OSError) as e: print(f"ERROR: {e}. See references/spec-format.md", file=sys.stderr); sys.exit(1)
