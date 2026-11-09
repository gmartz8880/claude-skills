#!/usr/bin/env python3
"""render_blueprint.py - draw a crisp blueprint sheet (dashboard / control panel map) from a JSON spec.

Usage: python render_blueprint.py SPEC.json OUT_DIR [--check] [--json]
Writes OUT_DIR/<dwg_no>_crisp.png. Run age.py on it for the vintage cyanotype look.
Spec format: see references/spec-format.md (example: templates/example-tundra/panel.json).
Exit: 0 ok, 1 bad spec/missing fonts, 2 usage.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from _common import BG, COL, colour, text, poly, dashed, path_points, font, safe, FONT_DIR, FONTS

W, H = 3300, 2250
def rect(d, x, y, w, h, style="line", sw=3, rx=0, dash=None, fill=None):
    c = colour(style)
    if dash:
        if fill: d.rounded_rectangle([x, y, x + w, y + h], rx, fill=fill)
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]; poly(d, pts, c, sw, dash=(14, 9), closed=True)
    else:
        d.rounded_rectangle([x, y, x + w, y + h], radius=rx, outline=c, width=sw, fill=fill)
def circ(d, x, y, r, style="line", sw=3, fill=None):
    d.ellipse([x - r, y - r, x + r, y + r], outline=colour(style), width=sw, fill=fill)
def tag(d, x, y, n):
    circ(d, x, y, 27, "blank", 5, fill=BG); text(d, x, y + 1, n, 30, "blank", "mm", "head")

def element(d, e, ox, oy):
    t = e["t"]; s = e.get("style", "blank" if t == "blank" else "line"); sw = e.get("sw", 3)
    X = lambda v: ox + v; Y = lambda v: oy + v
    if t in ("rect", "switch", "blank"):
        dash = e.get("dash", t == "blank")
        rect(d, X(e["x"]), Y(e["y"]), e["w"], e["h"], s, sw, e.get("rx", 6 if t != "rect" else 0), dash)
        lab = e.get("label", "[ ]" if t == "blank" else None)
        if lab:
            text(d, X(e["x"] + e["w"] / 2), Y(e["y"] + e["h"] / 2), lab, e.get("size", 17), s if t == "blank" else e.get("label_style", "line"), "mm")
    elif t == "circle":
        circ(d, X(e["x"]), Y(e["y"]), e["r"], s, sw)
        if e.get("label"): text(d, X(e["x"]), Y(e["y"]), e["label"], e.get("size", 16), e.get("label_style", "line"), "mm")
    elif t == "line":
        p = [(X(a), Y(b)) for a, b in e["pts"]]; poly(d, p, colour(s), sw, (14, 9) if e.get("dash") else None)
    elif t == "path":
        for seg in path_points(e["d"], ox, oy): poly(d, seg, colour(s), sw, (14, 9) if e.get("dash") else None)
    elif t == "vent":
        x, y, w, h, n = e["x"], e["y"], e["w"], e["h"], e.get("n", 6)
        rect(d, X(x), Y(y), w, h, s, 3, 14)
        for k in range(n):
            yy = Y(y + 14 + k * (h - 28) / max(1, n - 1)); d.line([(X(x + 10), yy), (X(x + w - 10), yy)], fill=COL["dim"], width=2)
    elif t == "gauge":
        x, y, r = X(e["x"]), Y(e["y"]), e["r"]
        circ(d, x, y, r, s, 3); circ(d, x, y, r - 12, "dim", 1)
        d.line([(x, y), (x + r * .55, y - r * .5)], fill=COL["blank"], width=3)
        if e.get("label"): text(d, x, y + e.get("label_dy", r * .55), e["label"], e.get("size", 17), "line", "ms")
    elif t == "wheel":   # steering wheel: spokes given as angle list (deg, 0 = right, 90 = down)
        import math
        x, y, r = X(e["x"]), Y(e["y"]), e["r"]
        circ(d, x, y, r, s, 7); circ(d, x, y, r - 30, "dim", 1)
        hw, hh = e.get("hub", [160, 124])
        rect(d, x - hw / 2, y - hh / 2, hw, hh, s, 4, 46); text(d, x, y, e.get("hub_label", "SRS"), 20, "dim", "mm")
        for a in e.get("spokes", [190, -10, 115, 65]):
            ra = math.radians(a); x1, y1 = x + math.cos(ra) * hw * .5, y + math.sin(ra) * hh * .5
            d.line([(x1, y1), (x + math.cos(ra) * (r - 25), y + math.sin(ra) * (r - 25))], fill=colour(s), width=7)
    elif t == "text":
        text(d, X(e["x"]), Y(e["y"]), e["text"], e.get("size", 16), s, e.get("anchor", "ls"), e.get("font", "body"))
    elif t == "callout":
        tag(d, X(e["x"]), Y(e["y"]), str(e["n"]))
    else:
        raise ValueError(f"unknown element type {t!r}")

def render(spec, out_dir):
    sh = spec["sheet"]
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    for x in range(0, W, 30): d.line([(x, 0), (x, H)], fill=COL["grid"], width=1)
    for y in range(0, H, 30): d.line([(0, y), (W, y)], fill=COL["grid"], width=1)
    for x in range(0, W, 150): d.line([(x, 0), (x, H)], fill=COL["grid2"], width=2)
    for y in range(0, H, 150): d.line([(0, y), (W, y)], fill=COL["grid2"], width=2)
    rect(d, 40, 40, W - 80, H - 80, "line", 6); rect(d, 55, 55, W - 110, H - 110, "line", 2)
    for i in range(1, 11):
        x = 55 + i * (W - 110) / 10
        if i < 10:
            d.line([(x, 55), (x, 80)], fill=COL["line"], width=2); d.line([(x, H - 55), (x, H - 80)], fill=COL["line"], width=2)
        text(d, x - (W - 110) / 20, 75, i, 18, "dim", "ms"); text(d, x - (W - 110) / 20, H - 60, i, 18, "dim", "ms")
    for j, c in enumerate("ABCDEFG"):
        y = 55 + (j + .5) * (H - 110) / 7; text(d, 68, y, c, 18, "dim", "mm"); text(d, W - 68, y, c, 18, "dim", "mm")
    text(d, 120, 150, sh["title"], 56, "line", "ls", "head")
    text(d, 120, 205, sh.get("subtitle", ""), 30, "dim")
    if sh.get("model_no"): text(d, W - 120, 150, "MODEL " + sh["model_no"], 34, "blank", "rs", "head")
    dr = spec["drawing"]; ox, oy = dr.get("origin", [120, 300])
    for e in dr["elements"]: element(d, e, ox, oy)
    # dimension line under drawing
    dy = oy + dr.get("height", 650)
    d.line([(ox, dy), (ox + dr.get("width", 2080), dy)], fill=COL["dim"], width=2)
    for xx in (ox, ox + dr.get("width", 2080)): d.line([(xx, dy - 15), (xx, dy + 15)], fill=COL["dim"], width=2)
    text(d, ox + dr.get("width", 2080) / 2, dy + 26, dr.get("dim_label", "PANEL WIDTH (REF)"), 16, "dim", "ms")
    # schedule
    sc = spec["schedule"]; tx, ty = 120, 1030
    text(d, tx, ty, sc.get("title", "CALLOUT SCHEDULE"), 30, "line", "ls", "head"); d.line([(tx, ty + 15), (tx + 2140, ty + 15)], fill=COL["line"], width=3)
    cols = sc.get("col_x", [0, 70, 520, 1235, 1565])
    for x, h in zip(cols, sc["columns"]): text(d, tx + x, ty + 55, h, 23, "dim", "ls", "head")
    rh = sc.get("row_h", 48)
    for i, r in enumerate(sc["rows"]):
        y = ty + 100 + i * rh
        if i % 2 == 0: d.rectangle([tx - 10, y - 32, tx + 2150, y + 14], fill=COL["fill"])
        for k, (x, v) in enumerate(zip(cols, r)): text(d, tx + x + (14 if k == 0 else 0), y, v, sc.get("size", 22), "blank" if k == 0 else "line")
    yb = ty + 100 + len(sc["rows"]) * rh - 20
    d.line([(tx, yb), (tx + 2140, yb)], fill=COL["line"], width=2)
    for k, f in enumerate(sc.get("footnotes", [])): text(d, tx, yb + 40 + k * 32, f, 21, "dim")
    # right column: notes / legend / revisions
    rx = 2300
    rect(d, rx, 240, 880, 640); text(d, rx + 30, 290, "GENERAL NOTES", 28, "line", "ls", "head"); d.line([(rx + 30, 305), (rx + 850, 305)], fill=COL["line"], width=2)
    for i, n in enumerate(spec.get("notes", [])[:13]): text(d, rx + 30, 345 + i * 40, n, 22)
    rect(d, rx, 900, 880, 330); text(d, rx + 30, 950, "LEGEND", 28, "line", "ls", "head"); d.line([(rx + 30, 965), (rx + 850, 965)], fill=COL["line"], width=2)
    rect(d, rx + 40, 995, 120, 40, "line", 2); text(d, rx + 190, 1024, spec.get("legend_fitted", "FITTED CONTROL"), 22)
    rect(d, rx + 40, 1055, 120, 40, "blank", 3, dash=True); text(d, rx + 190, 1084, "BLANK / HIGHER-TRIM SLOT", 22)
    tag(d, rx + 100, 1140, "n"); text(d, rx + 190, 1150, "CALLOUT (see schedule)", 22)
    text(d, rx + 40, 1205, "[5/5] = needs dealer programming", 20, "dim")
    rect(d, rx, 1250, 880, 330); text(d, rx + 30, 1300, "REVISIONS", 28, "line", "ls", "head"); d.line([(rx + 30, 1315), (rx + 850, 1315)], fill=COL["line"], width=2)
    text(d, rx + 30, 1355, "REV  DATE        DESCRIPTION        BY", 20, "dim")
    for i, r in enumerate(spec.get("revisions", [["A", sh.get("date", ""), "INITIAL RELEASE", sh.get("owner", "")]])[:2]):
        text(d, rx + 30, 1395 + i * 34, f"{r[0]:<4} {r[1]:<11} {r[2]:<18} {r[3]}", 20)
    for i, s in enumerate(spec.get("sources", [])[:3]): text(d, rx + 30, 1470 + i * 28, s, 19, "dim")
    text(d, rx + 30, 1560, spec.get("verify_line", "VERIFY ALL P/N BY VIN / SERIAL WITH A DEALER."), 19, "red")
    # detail box
    det = spec.get("detail")
    rect(d, 120, 1690, 1440, 460)
    if det:
        text(d, 145, 1735, det["title"], 24, "line", "ls", "head"); d.line([(145, 1750), (1535, 1750)], fill=COL["line"], width=2)
        for e in det["elements"]: element(d, e, 120, 1690)
        if det.get("caption"): text(d, 145, 2130, det["caption"], 19, "dim")
    # title block
    bx, by, bw, bh = 1640, 1720, 1540, 430
    rect(d, bx, by, bw, bh, "line", 5)
    for yy, wdt in ((150, 3), (260, 3), (345, 2)): d.line([(bx, by + yy), (bx + bw, by + yy)], fill=COL["line"], width=wdt)
    text(d, bx + bw / 2, by + 88, sh.get("company", ""), 80, "line", "ms", "head")
    text(d, bx + bw / 2, by + 132, sh.get("tagline", "ENGINEERING · FABRICATION · VEHICLE SYSTEMS"), 24, "dim", "ms")
    text(d, bx + 25, by + 190, "TITLE:", 18, "dim"); text(d, bx + 130, by + 200, sh.get("block_title", sh["title"])[:58], 30, "line", "ls", "head")
    text(d, bx + 130, by + 240, sh.get("vehicle_line", ""), 22)
    cells = (("OWNER", sh.get("owner", "")), ("MODEL NO.", sh.get("model_no", "-")), ("DWG NO.", sh["dwg_no"]), ("SHEET", sh.get("sheet", "1 OF 1")), ("SCALE", sh.get("scale", "NTS")))
    cw = bw / len(cells)
    for i, (k, v) in enumerate(cells):
        x = bx + 20 + i * cw; text(d, x, by + 290, k + ":", 17, "dim"); sz = 27
        while sz > 15 and font("head", sz).getlength(str(v)) > cw - 30: sz -= 1
        text(d, x, by + 330, v, sz, "blank" if k == "MODEL NO." else "line", "ls", "head")
        if i: d.line([(x - 12, by + 260), (x - 12, by + 345)], fill=COL["line"], width=2)
    text(d, bx + 25, by + 382, "DRAWN:", 17, "dim"); text(d, bx + 110, by + 385, sh.get("drawn", ""), 25, "line", "ls", "hand")
    text(d, bx + 520, by + 382, "DATE: " + sh.get("date", ""), 19)
    text(d, bx + 900, by + 382, "CHECKED:", 17, "dim"); text(d, bx + 1030, by + 385, sh.get("checked", ""), 27, "pencil", "ls", "hand")
    text(d, bx + 25, by + 414, sh.get("proprietary", "PROPRIETARY. DO NOT SCALE DRAWING."), 16, "dim")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{sh['dwg_no']}_crisp.png"); img.save(out); return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?"); ap.add_argument("out_dir", nargs="?", default="out")
    ap.add_argument("--check", action="store_true", help="only verify fonts are present"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    missing = [f for f in FONTS.values() if not os.path.exists(os.path.join(FONT_DIR, f))]
    if a.check or not a.spec:
        r = {"fonts_missing": missing, "ok": not missing}
        print(json.dumps(r) if a.json else ("ready" if not missing else f"missing fonts: {missing}"))
        sys.exit(0 if not missing else 1) if a.check else sys.exit(2 if not a.spec else 0)
    try:
        spec = json.load(open(a.spec, encoding="utf-8")); out = render(spec, a.out_dir)
    except (KeyError, ValueError, OSError) as e:
        print(f"ERROR: {e}. Check the spec against references/spec-format.md", file=sys.stderr); sys.exit(1)
    print(json.dumps({"ok": True, "png": out}) if a.json else out)
if __name__ == "__main__": main()
