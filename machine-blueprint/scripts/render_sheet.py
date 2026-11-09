#!/usr/bin/env python3
"""render_sheet.py - render a multi-sheet engineering blueprint SET for any machine from sheets.json.

Usage: python render_sheet.py SHEETS.json OUT_DIR [--check] [--json]
Writes OUT_DIR/<dwg_no>-S<n>_crisp.png per sheet (run age.py on each, or use make_all.py).
Each sheet = border + zones + title + free-placed PANELS (view / table / specs / notes / legend /
revisions / text / image) + title block (names from branding.json). Format: references/sheet-format.md.
Exit: 0 ok, 1 bad spec, 2 usage.
"""
import sys, os, json, math, copy, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
from _common import BG, COL, colour, text, poly, dashed, path_points, font, FONT_DIR, FONTS
import render_blueprint as RB
import eng_elements as EE

W, H = 3300, 2250
BASE = ["."]   # spec directory, for model.json paths

# ---------- geometry helpers ----------
def scale_el(e, k, ox, oy):
    """Return element with coordinates scaled by k (text sizes untouched) - origin handled by caller."""
    if k == 1: return e
    e = copy.deepcopy(e)
    for key in ("x", "y", "w", "h", "r", "offset", "depth", "width", "hole_r", "rx", "label_dy"):
        if key in e and isinstance(e[key], (int, float)): e[key] = e[key] * k
    for key in ("pts",):
        if e.get("t") in ("iso", "ortho"): break
        if key in e: e[key] = [[a * k, b * k] for a, b in e[key]]
    for key in ("p1", "p2", "c"):
        if key in e: e[key] = [e[key][0] * k, e[key][1] * k]
    if "d" in e: e["d"] = [[c[0]] + [v * k for v in c[1:]] for c in e["d"]]
    if "hub" in e: e["hub"] = [v * k for v in e["hub"]]
    return e

def arrowhead(d, tip, frm, c, size=18):
    ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    p1 = (tip[0] - size * math.cos(ang - .38), tip[1] - size * math.sin(ang - .38))
    p2 = (tip[0] - size * math.cos(ang + .38), tip[1] - size * math.sin(ang + .38))
    d.polygon([tip, p1, p2], fill=c)

def dashdot(d, p1, p2, c, w):
    (x1, y1), (x2, y2) = p1, p2; L = math.hypot(x2 - x1, y2 - y1)
    if not L: return
    ux, uy = (x2 - x1) / L, (y2 - y1) / L; pos = 0; pat = [(34, True), (8, False), (6, True), (8, False)]; i = 0
    while pos < L:
        seg, on = pat[i % 4]; e = min(pos + seg, L)
        if on: d.line([(x1 + ux * pos, y1 + uy * pos), (x1 + ux * e, y1 + uy * e)], fill=c, width=w)
        pos = e; i += 1

def hatch(img, poly_pts, c, spacing=16, angle=45, width=2):
    xs = [p[0] for p in poly_pts]; ys = [p[1] for p in poly_pts]
    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1
    mask = Image.new("L", (x1 - x0, y1 - y0), 0); ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in poly_pts], fill=255)
    lay = Image.new("RGB", mask.size, BG); ld = ImageDraw.Draw(lay); Wd, Hd = mask.size; D = math.hypot(Wd, Hd)
    a = math.radians(angle); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux; cx, cy = Wd / 2, Hd / 2; off = -D
    while off < D:
        px, py = cx + nx * off, cy + ny * off; ld.line([(px - ux * D, py - uy * D), (px + ux * D, py + uy * D)], fill=c, width=width); off += spacing
    img.paste(lay, (x0, y0), mask)

# ---------- element renderer (engineering primitives + everything from render_blueprint) ----------
def element(img, d, e, ox, oy, k=1):
    e = scale_el(e, k, ox, oy); t = e["t"]; s = e.get("style", "line"); c = colour(s); sw = e.get("sw", 3)
    X = lambda v: ox + v; Y = lambda v: oy + v; P = lambda p: (ox + p[0], oy + p[1])
    if t == "dim":           # linear dimension: p1, p2, offset (perpendicular), text
        a, b = P(e["p1"]), P(e["p2"]); off = e.get("offset", 40)
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1; nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
        a2, b2 = (a[0] + nx * off, a[1] + ny * off), (b[0] + nx * off, b[1] + ny * off); dc = colour(e.get("style", "dim"))
        for p, q in ((a, a2), (b, b2)): d.line([(p[0] + nx * 6, p[1] + ny * 6), (q[0] + nx * 12, q[1] + ny * 12)], fill=dc, width=2)
        d.line([a2, b2], fill=dc, width=2); arrowhead(d, a2, b2, dc); arrowhead(d, b2, a2, dc)
        mx, my = (a2[0] + b2[0]) / 2 + nx * 18, (a2[1] + b2[1]) / 2 + ny * 18
        tw = font("body", e.get("size", 20)).getlength(str(e["text"])) + 12
        if abs(ny) > .5: d.rectangle([mx - tw / 2, my - 15, mx + tw / 2, my + 15], fill=BG)
        text(d, mx, my, e["text"], e.get("size", 20), "line", "mm")
    elif t == "diameter":    # circle diameter callout: c, r, angle, text
        cx, cy = P(e["c"]); r = e["r"]; ang = math.radians(e.get("angle", -35)); tip = (cx + r * math.cos(ang), cy + r * math.sin(ang))
        out = (cx + (r + 70) * math.cos(ang), cy + (r + 70) * math.sin(ang)); dc = colour(e.get("style", "dim"))
        d.line([out, tip], fill=dc, width=2); arrowhead(d, tip, out, dc); d.line([out, (out[0] + (40 if math.cos(ang) >= 0 else -40), out[1])], fill=dc, width=2)
        text(d, out[0] + (48 if math.cos(ang) >= 0 else -48), out[1], e["text"], e.get("size", 20), "line", "lm" if math.cos(ang) >= 0 else "rm")
    elif t == "leader":      # pts from arrow tip to text end
        pts = [P(p) for p in e["pts"]]; dc = colour(e.get("style", "dim"))
        d.line(pts, fill=dc, width=2); arrowhead(d, pts[0], pts[1], dc, 16)
        right = pts[-1][0] >= pts[-2][0]
        text(d, pts[-1][0] + (8 if right else -8), pts[-1][1], e["text"], e.get("size", 19), e.get("text_style", "line"), "lm" if right else "rm")
    elif t == "centerline":
        dashdot(d, P(e["p1"]), P(e["p2"]), colour(e.get("style", "dim")), 2)
    elif t == "hidden":
        poly(d, [P(p) for p in e["pts"]], colour(e.get("style", "dim")), 2, (12, 8))
    elif t == "hatch":
        pts = [P(p) for p in e["pts"]] if "pts" in e else [P((e["x"], e["y"])), P((e["x"] + e["w"], e["y"])), P((e["x"] + e["w"], e["y"] + e["h"])), P((e["x"], e["y"] + e["h"]))]
        hatch(img, pts, colour(e.get("style", "dim")), int(e.get("spacing", 16)), e.get("angle", 45))
        if e.get("outline", True): d.polygon(pts, outline=c, width=sw)
    elif t == "polygon":
        pts = [P(p) for p in e["pts"]]; d.polygon(pts, outline=c, width=sw, fill=colour(e["fill"]) if e.get("fill") else None)
    elif t == "arc":
        x, y, r = X(e["x"]), Y(e["y"]), e["r"]; d.arc([x - r, y - r, x + r, y + r], e.get("start", 0), e.get("end", 180), fill=c, width=sw)
    elif t == "gear":
        x, y, r, n = X(e["x"]), Y(e["y"]), e["r"], int(e.get("teeth", 20)); dep = e.get("depth", r * .12); pts = []
        for i in range(n * 4):
            a = 2 * math.pi * i / (n * 4); rr = r if (i % 4) in (1, 2) else r - dep; pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, outline=c, width=sw); RB.circ(d, x, y, e.get("bore", r * .25), s, sw)
        if e.get("pitch", True): RB.circ(d, x, y, r - dep / 2, "dim", 1)
    elif t == "spring":
        a, b = P(e["p1"]), P(e["p2"]); n = int(e.get("coils", 8)); wdt = e.get("width", 30); L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = -uy, ux; pts = [a]
        for i in range(1, 2 * n): f = i / (2 * n); sgn = 1 if i % 2 else -1; pts.append((a[0] + ux * L * f + nx * wdt * sgn, a[1] + uy * L * f + ny * wdt * sgn))
        pts.append(b); d.line(pts, fill=c, width=sw, joint="curve")
    elif t == "boltcircle":
        x, y, r, n = X(e["x"]), Y(e["y"]), e["r"], int(e.get("n", 6)); hr = e.get("hole_r", 10)
        RB.circ(d, x, y, r, "dim", 1)
        for i in range(n):
            a = 2 * math.pi * i / n + math.radians(e.get("phase", 0)); RB.circ(d, x + r * math.cos(a), y + r * math.sin(a), hr, s, 2)
    elif t == "arrow":
        a, b = P(e["p1"]), P(e["p2"]); d.line([a, b], fill=c, width=sw); arrowhead(d, b, a, c, 20)
    elif t == "section":     # cutting-plane line A-A
        a, b = P(e["p1"]), P(e["p2"]); dashdot(d, a, b, colour("line"), 4); L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        nx, ny = -(b[1] - a[1]) / L * e.get("dir", 1), (b[0] - a[0]) / L * e.get("dir", 1)
        for p in (a, b):
            q = (p[0] + nx * 50, p[1] + ny * 50); d.line([p, q], fill=colour("line"), width=4); arrowhead(d, q, p, colour("line"), 22)
            text(d, q[0] + nx * 22, q[1] + ny * 22, e["label"], 32, "line", "mm", "head")
    elif t == "image":       # embed a line-art PNG (already traced / own drawing), tinted to linework colour
        im = Image.open(e["path"]).convert("L").resize((int(e["w"]), int(e["h"])))
        mask = im.point(lambda v: 255 - v if e.get("invert", True) else v); lay = Image.new("RGB", im.size, colour(s)); img.paste(lay, (int(X(e["x"])), int(Y(e["y"]))), mask)
    elif t == "esym": EE.esym(d, e, X, Y)
    elif t == "wire": EE.wire(d, e, P)
    elif t == "junction": q = P((e["x"], e["y"])); d.ellipse([q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7], fill=c)
    elif t == "iso": EE.iso(img, d, e, X, Y, BASE[0])
    elif t == "ortho": EE.ortho(img, d, e, X, Y, BASE[0])
    elif t == "projsym": EE.projsym(d, e, X, Y)
    else:
        RB.element(d, e, ox, oy)

# ---------- panels ----------
def panel_frame(d, p):
    x, y, w, h = p["box"]
    if p.get("frame", True): RB.rect(d, x, y, w, h, "line", 3)
    if p.get("title"):
        text(d, x + 25, y + 45, p["title"], p.get("title_size", 26), "line", "ls", "head"); d.line([(x + 25, y + 60), (x + w - 25, y + 60)], fill=COL["line"], width=2)
    return x, y, w, h

def panel(img, d, p, base_dir):
    typ = p["type"]; x, y, w, h = panel_frame(d, p)
    if typ == "view":
        ox, oy = p.get("origin", [0, 0]); k = p.get("scale", 1)
        for e in p["elements"]:
            if e.get("t") == "image" and not os.path.isabs(e["path"]): e = dict(e, path=os.path.join(base_dir, e["path"]))
            if e.get("t") == "iso" and "x" not in e: e = dict(e, x=0, y=0, fit_box=[x + 20, y + (75 if p.get("title") else 20), w - 40, h - (125 if p.get("caption") else 95)])
            element(img, d, e, x + ox, y + oy, k)
        if p.get("caption"): text(d, x + w / 2, y + h - 18, p["caption"], p.get("caption_size", 24), "line", "ms", "head")
    elif typ in ("table", "specs"):
        cols = p.get("columns", ["ITEM", "VALUE"]) ; cx = p.get("col_x") or [int(i * (w - 50) / len(cols)) for i in range(len(cols))]
        size = p.get("size", 21); rh = p.get("row_h", int(size * 1.9)); top = y + (95 if p.get("title") else 40)
        for xx, hd in zip(cx, cols): text(d, x + 25 + xx, top, hd, size + 1, "dim", "ls", "head")
        d.line([(x + 20, top + 12), (x + w - 20, top + 12)], fill=COL["line"], width=2)
        for i, r in enumerate(p["rows"]):
            yy = top + 12 + rh * (i + 1) - 8
            if yy > y + h - 20: break
            if i % 2 == 0: d.rectangle([x + 15, yy - rh + 12, x + w - 15, yy + 10], fill=COL["fill"])
            for j, (xx, v) in enumerate(zip(cx, r)): text(d, x + 25 + xx, yy, v, size, "blank" if j == 0 and p.get("first_col_yellow", True) else "line")
        for i, f in enumerate(p.get("footnotes", [])): text(d, x + 25, y + h - 22 - (len(p["footnotes"]) - 1 - i) * 30, f, size - 2, "dim")
    elif typ in ("notes", "text"):
        size = p.get("size", 22); lh = p.get("line_h", int(size * 1.8))
        for i, ln in enumerate(p["lines"]): text(d, x + 30, y + (100 if p.get("title") else 50) + i * lh, ln, size, "line" if typ == "notes" else p.get("style", "line"))
    elif typ == "legend":
        for i, it in enumerate(p["items"]):
            yy = y + 105 + i * p.get("row_h", 54); kind = it["kind"]; lx = x + 40
            if kind == "line": RB.rect(d, lx, yy - 20, 120, 40, "line", 2)
            elif kind == "blank": RB.rect(d, lx, yy - 20, 120, 40, "blank", 3, dash=True)
            elif kind == "callout": RB.tag(d, lx + 60, yy, "n")
            elif kind == "hidden": poly(d, [(lx, yy), (lx + 120, yy)], COL["dim"], 2, (12, 8))
            elif kind == "center": dashdot(d, (lx, yy), (lx + 120, yy), COL["dim"], 2)
            elif kind == "hatch": hatch(img, [(lx, yy - 20), (lx + 120, yy - 20), (lx + 120, yy + 20), (lx, yy + 20)], COL["dim"]); d.rectangle([lx, yy - 20, lx + 120, yy + 20], outline=COL["line"], width=2)
            elif kind == "dim": d.line([(lx, yy), (lx + 120, yy)], fill=COL["dim"], width=2); arrowhead(d, (lx, yy), (lx + 120, yy), COL["dim"]); arrowhead(d, (lx + 120, yy), (lx, yy), COL["dim"])
            elif kind == "red": d.line([(lx, yy), (lx + 120, yy)], fill=COL["red"], width=4)
            text(d, lx + 150, yy + 8, it["label"], p.get("size", 22))
    elif typ == "revisions":
        text(d, x + 30, y + 100, "REV  DATE        DESCRIPTION        BY", 20, "dim")
        for i, r in enumerate(p.get("rows", [])[:3]): text(d, x + 30, y + 140 + i * 34, f"{r[0]:<4} {r[1]:<11} {r[2]:<18} {r[3]}", 20)
        for i, s in enumerate(p.get("sources", [])[:4]): text(d, x + 30, y + 250 + i * 28, s, 19, "dim")
        if p.get("verify"): text(d, x + 30, y + h - 24, p["verify"], 19, "red")
    elif typ == "matrix":
        matrix_panel(d, p, base_dir, x, y, w, h)
    else:
        raise ValueError(f"unknown panel type {typ!r}")

def load_tiers(p, base_dir):
    if "tiers" in p and isinstance(p["tiers"], dict): return p["tiers"]
    src = p.get("source", "tiers.json"); return json.load(open(src if os.path.isabs(src) else os.path.join(base_dir, src), encoding="utf-8"))

def tier_rows(t):
    rows = []
    for g in t["groups"]:
        rows.append(("group", g["group"]))
        for f in g["features"]: rows.append(("feat", f))
    return rows

def matrix_capacity(h, size=20):
    return int((h - 200) // int(size * 1.75))

def matrix_panel(d, p, base_dir, x, y, w, h):
    t = load_tiers(p, base_dir); tiers = t["tiers"]; size = p.get("size", 20); rh = int(size * 1.75)
    rows = tier_rows(t)[p.get("rows_from", 0):p.get("rows_to", None)]
    fw = p.get("feature_w", int(w * .42)); cw = (w - 50 - fw) / len(tiers); top = y + (80 if p.get("title") else 30)
    text(d, x + 25, top + 52, t.get("tier_label", "TRIM").upper() + " ->", size, "dim", "ls", "head")
    for i, tr in enumerate(tiers):        # header: tier name (2 lines max) + model code
        cx = x + 25 + fw + cw * i + cw / 2; words = tr["name"].split(); line1, line2 = "", ""
        for wd in words:
            if font("head", size).getlength((line1 + " " + wd).strip()) <= cw - 10 and not line2: line1 = (line1 + " " + wd).strip()
            else: line2 = (line2 + " " + wd).strip()
        text(d, cx, top + 22, line1, size, "line", "ms", "head"); text(d, cx, top + 46, line2, size, "line", "ms", "head")
        if tr.get("code"): text(d, cx, top + 70, tr["code"], size - 4, "blank", "ms")
        d.line([(cx - cw / 2, top), (cx - cw / 2, y + h - 60)], fill=COL["grid2"], width=1)
    yy = top + 84; d.line([(x + 20, yy), (x + w - 20, yy)], fill=COL["line"], width=2)
    for i, (kind, r) in enumerate(rows):
        yy += rh
        if yy > y + h - 70: text(d, x + 25, y + h - 40, "(continued on next sheet)", size - 2, "dim"); break
        if kind == "group":
            d.rectangle([x + 15, yy - rh + 6, x + w - 15, yy + 6], fill=COL["grid2"]); text(d, x + 25, yy - 2, r.upper(), size, "line", "ls", "head"); continue
        lab = r["feature"] + (f"  [{r['code']}]" if r.get("code") else "")
        while font("body", size).getlength(lab) > fw - 10 and len(lab) > 8: lab = lab[:-2]
        text(d, x + 25, yy - 2, lab, size, "line")
        for j, v in enumerate(r["values"]):
            cx = x + 25 + fw + cw * j + cw / 2; cy = yy - size * .35; rr = size * .42; v = str(v).upper()
            if v == "S": d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=COL["line"])
            elif v == "O": d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=COL["line"], width=3)
            elif v == "P": d.rectangle([cx - rr, cy - rr, cx + rr, cy + rr], outline=COL["blank"], width=3)
            elif v in ("-", "", "N"): d.line([(cx - rr, cy), (cx + rr, cy)], fill=COL["dim"], width=3)
            else: text(d, cx, yy - 2, v, size - 2, "blank", "ms")
        d.line([(x + 20, yy + 6), (x + w - 20, yy + 6)], fill=COL["grid2"], width=1)
    ly = y + h - 22; lx = x + 25
    for sym, lab in (("S", "STANDARD"), ("O", "OPTIONAL"), ("P", "IN PACKAGE"), ("-", "NOT AVAILABLE")):
        rr = 9; cy = ly - 7
        if sym == "S": d.ellipse([lx, cy - rr, lx + 2 * rr, cy + rr], fill=COL["line"])
        elif sym == "O": d.ellipse([lx, cy - rr, lx + 2 * rr, cy + rr], outline=COL["line"], width=3)
        elif sym == "P": d.rectangle([lx, cy - rr, lx + 2 * rr, cy + rr], outline=COL["blank"], width=3)
        else: d.line([(lx, cy), (lx + 2 * rr, cy)], fill=COL["dim"], width=3)
        text(d, lx + 30, ly, lab, 17, "dim"); lx += 260

def frame(d, sh):
    for xx in range(0, W, 30): d.line([(xx, 0), (xx, H)], fill=COL["grid"])
    for yy in range(0, H, 30): d.line([(0, yy), (W, yy)], fill=COL["grid"])
    for xx in range(0, W, 150): d.line([(xx, 0), (xx, H)], fill=COL["grid2"], width=2)
    for yy in range(0, H, 150): d.line([(0, yy), (W, yy)], fill=COL["grid2"], width=2)
    RB.rect(d, 40, 40, W - 80, H - 80, "line", 6); RB.rect(d, 55, 55, W - 110, H - 110, "line", 2)
    for i in range(1, 11):
        xx = 55 + i * (W - 110) / 10
        if i < 10: d.line([(xx, 55), (xx, 80)], fill=COL["line"], width=2); d.line([(xx, H - 55), (xx, H - 80)], fill=COL["line"], width=2)
        text(d, xx - (W - 110) / 20, 75, i, 18, "dim", "ms"); text(d, xx - (W - 110) / 20, H - 60, i, 18, "dim", "ms")
    for j, ch in enumerate("ABCDEFG"):
        yy = 55 + (j + .5) * (H - 110) / 7; text(d, 68, yy, ch, 18, "dim", "mm"); text(d, W - 68, yy, ch, 18, "dim", "mm")

def title_block(d, s):
    bx, by, bw, bh = s.get("title_block_box", [1640, 1720, 1540, 430])
    RB.rect(d, bx, by, bw, bh, "line", 5)
    for yy, wd in ((150, 3), (260, 3), (345, 2)): d.line([(bx, by + yy), (bx + bw, by + yy)], fill=COL["line"], width=wd)
    text(d, bx + bw / 2, by + 88, s.get("company", ""), 80, "line", "ms", "head")
    text(d, bx + bw / 2, by + 132, s.get("tagline", ""), 24, "dim", "ms")
    text(d, bx + 25, by + 190, "TITLE:", 18, "dim"); text(d, bx + 130, by + 200, s.get("block_title", s.get("title", ""))[:56], 30, "line", "ls", "head")
    text(d, bx + 130, by + 240, s.get("machine_line", ""), 22)
    cells = (("OWNER", s.get("owner", "")), ("MODEL NO.", s.get("model_no", "-")), ("DWG NO.", s["dwg_no"]), ("SHEET", s.get("sheet", "1 OF 1")), ("SCALE", s.get("scale", "NTS")))
    cw = bw / len(cells)
    for i, (kk, v) in enumerate(cells):
        xx = bx + 20 + i * cw; text(d, xx, by + 290, kk + ":", 17, "dim"); sz = 27
        while sz > 15 and font("head", sz).getlength(str(v)) > cw - 30: sz -= 1
        text(d, xx, by + 330, v, sz, "blank" if kk == "MODEL NO." else "line", "ls", "head")
        if i: d.line([(xx - 12, by + 260), (xx - 12, by + 345)], fill=COL["line"], width=2)
    text(d, bx + 25, by + 382, "DRAWN:", 17, "dim"); text(d, bx + 110, by + 385, s.get("drawn", ""), 25, "line", "ls", "hand")
    text(d, bx + 520, by + 382, "DATE: " + s.get("date", ""), 19)
    text(d, bx + 900, by + 382, "CHECKED:", 17, "dim"); text(d, bx + 1030, by + 385, s.get("checked", ""), 27, "pencil", "ls", "hand")
    text(d, bx + 25, by + 414, s.get("proprietary", "DO NOT SCALE DRAWING."), 16, "dim")

def key_sheet(spec, base_dir):
    """Auto-built KEY & INDEX sheet: sheet index, line/symbol key, electrical symbols, matrix symbols,
    colour key, abbreviations and the callout index from model.json. Always sheet 1 of the set."""
    st = spec.get("set", {}); sheets = spec["sheets"]; n = len(sheets) + 1
    ins = spec.get("_inserted", [])          # sheets rendered elsewhere (e.g. dashboard preset) placed after the key
    idx = [["1", "KEY & INDEX (this sheet)"]] + [[str(2 + j), t[:70]] for j, t in enumerate(ins)] + [[str(i + 2 + len(ins)), sh.get("title", "")[:70]] for i, sh in enumerate(sheets)]
    callouts = []
    mp = os.path.join(base_dir, "model.json")
    if os.path.exists(mp):
        m = json.load(open(mp, encoding="utf-8"))
        callouts = [[str(q.get("callout")), q.get("name", "")[:30], str(q.get("part_no", ""))[:22]] for q in m.get("parts", []) if q.get("callout") is not None]
        callouts.sort(key=lambda r: int(r[0]) if r[0].isdigit() else 999)
    abbr = st.get("abbreviations") or [["REF", "Reference dimension"], ["APPROX.", "Approximate"], ["TYP.", "Typical"], ["NTS", "Not to scale"], ["CL", "Centerline"],
            ["P/N", "Part number"], ["S/N", "Serial number"], ["OEM", "Original equipment"], ["AWG", "American wire gauge"], ["GND", "Ground"], ["LOTO", "Lockout / tagout"], ["SRS", "Airbag system"]]
    esyms = [dict(t="esym", kind=k, x=110 + (i % 5) * 200, y=170 + (i // 5) * 150, size=96, label=lab) for i, (k, lab) in enumerate((("battery", "BATTERY"), ("fuse", "FUSE"), ("switch", "SWITCH (NO)"),
             ("switch_nc", "SWITCH (NC)"), ("relay", "RELAY"), ("motor", "MOTOR"), ("lamp", "LAMP"), ("diode", "DIODE"), ("resistor", "RESISTOR"), ("transformer", "IGN. COIL"),
             ("capacitor", "CAPACITOR"), ("spark_plug", "SPARK PLUG"), ("connector", "CONNECTOR"), ("generator", "GENERATOR"), ("sensor", "SENSOR")))]
    esyms.append(dict(t="esym", kind="ground", x=110, y=640, size=60, label="")); esyms.append(dict(t="text", x=160, y=652, text="GROUND", size=17))
    panels = [dict(type="table", box=[100, 250, 1060, 900], title="SHEET INDEX", columns=["SHEET", "TITLE"], col_x=[0, 120], rows=idx, size=18),
              dict(type="legend", box=[1180, 250, 640, 520], title="LINE & MARK KEY", row_h=48, items=[dict(kind="line", label="VISIBLE OUTLINE"), dict(kind="hidden", label="HIDDEN EDGE"),
                   dict(kind="center", label="CENTERLINE"), dict(kind="dim", label="DIMENSION"), dict(kind="hatch", label="SECTION / GUARD"), dict(kind="callout", label="CALLOUT NUMBER"),
                   dict(kind="blank", label="OPTION / BLANK SLOT"), dict(kind="red", label="DANGER / BATTERY +")]),
              dict(type="view", box=[1840, 250, 1360, 760], title="ELECTRICAL SYMBOL KEY", elements=esyms),
              dict(type="table", box=[1180, 790, 640, 360], title="COLOUR KEY", columns=["COLOUR", "MEANING"], col_x=[0, 200], size=19, first_col_yellow=False,
                   rows=[["WHITE", "Geometry, text"], ["LIGHT BLUE", "Dims, notes, optional"], ["YELLOW", "Callouts, model no."], ["RED", "Cautions, hazards"], ["RED PENCIL", "Checker's marks"]]),
              dict(type="table", box=[100, 1170, 1060, 980], title="CALLOUT INDEX (FROM 3-D MODEL)", columns=["NO.", "COMPONENT", "PART NO."], col_x=[0, 100, 640], rows=callouts or [["-", "No model.json callouts", "-"]], size=19),
              dict(type="table", box=[1180, 1170, 640, 530], title="ABBREVIATIONS", columns=["ABBR.", "MEANING"], col_x=[0, 180], rows=abbr, size=18, row_h=33),
              dict(type="text", box=[1840, 1030, 1360, 660], title="MATRIX & DIFFICULTY KEY", size=20, line_h=40, lines=[
                   "TRIM / OPTION MATRIX (manufacturer's own tier names):", "  filled circle = STANDARD    open circle = OPTIONAL", "  yellow square = PART OF A PACKAGE   dash = NOT AVAILABLE",
                   "  text in a cell = manufacturer option / RPO / package code", "DIFFICULTY  [1/5] bolt-on ... [5/5] dealer programming", "PROJECTION  third angle: TOP above FRONT, RIGHT beside it",
                   "UNITS  as noted on each dimension; CAD exports in mm", "MODEL NO.  shown top-right and in the title block of every sheet"])]
    return dict(title="KEY & INDEX · SYMBOLS, ABBREVIATIONS, CALLOUTS", subtitle=f"READ FIRST - EXPLAINS EVERY LINE, SYMBOL, COLOUR AND ABBREVIATION USED IN SET {st.get('dwg_no', '')}",
                block_title="KEY & INDEX", panels=panels)

def render(spec, out_dir, base_dir="."):
    BASE[0] = base_dir
    common = spec.get("set", {}); outs = []
    if common.get("key_sheet", True) and not spec.get("_key_added"):
        spec = dict(spec); spec["sheets"] = [key_sheet(spec, base_dir)] + list(spec["sheets"]); spec["_key_added"] = True
    extra = len(spec.get("_inserted", [])); n = len(spec["sheets"]) + extra
    os.makedirs(out_dir, exist_ok=True)
    for i, sheet in enumerate(spec["sheets"], 1):
        num = i if i == 1 or not common.get("key_sheet", True) else i + extra
        s = dict(common); s.update(sheet); s.setdefault("sheet", f"{num} OF {n}")
        img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img); frame(d, s)
        text(d, 120, 150, s["title"], s.get("title_size", 56), "line", "ls", "head"); text(d, 120, 205, s.get("subtitle", ""), 30, "dim")
        if s.get("model_no"): text(d, W - 120, 150, "MODEL " + s["model_no"], 34, "blank", "rs", "head")
        for p in s.get("panels", []): panel(img, d, p, base_dir)
        if s.get("title_block", True): title_block(d, s)
        out = os.path.join(out_dir, f"{common.get('dwg_no', s['dwg_no'])}-S{i}_crisp.png"); img.save(out); outs.append(out)
    return outs

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?"); ap.add_argument("out_dir", nargs="?", default="out"); ap.add_argument("--check", action="store_true"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    missing = [f for f in FONTS.values() if not os.path.exists(os.path.join(FONT_DIR, f))]
    if a.check: print("ready" if not missing else f"missing fonts {missing}"); sys.exit(0 if not missing else 1)
    if not a.spec: ap.print_help(); sys.exit(2)
    try: outs = render(json.load(open(a.spec, encoding="utf-8")), a.out_dir, os.path.dirname(os.path.abspath(a.spec)))
    except (KeyError, ValueError, OSError) as e: print(f"ERROR: {e}. Check against references/sheet-format.md", file=sys.stderr); sys.exit(1)
    print(json.dumps({"ok": True, "sheets": outs}) if a.json else "\n".join(outs))
if __name__ == "__main__": main()
