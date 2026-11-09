"""eng_elements.py - electrical schematic symbols, wires, isometric 3-D solids and projection symbol.

Used by render_sheet.py (element types: esym, wire, junction, iso, projsym). Coordinates are sheet pixels
already offset by the caller. See references/sheet-format.md sections 2a-2c.
"""
import math
from PIL import Image, ImageDraw
from _common import BG, COL, colour, text, font

# ---------------- electrical ----------------
def _tf(cx, cy, rot):
    a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
    return lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)

def esym(d, e, X, Y):
    """Schematic symbol centred at (x,y); terminals at local (-L/2,0) and (+L/2,0) before rotation."""
    k = e["kind"]; L = e.get("size", 120); h = L / 2; c = colour(e.get("style", "line")); w = e.get("sw", 3)
    T = _tf(X(e["x"]), Y(e["y"]), e.get("rot", 0))
    ln = lambda pts: d.line([T(*p) for p in pts], fill=c, width=w, joint="curve")
    def circle(x, y, r): pts = [T(x + r * math.cos(t / 24 * 2 * math.pi), y + r * math.sin(t / 24 * 2 * math.pi)) for t in range(25)]; d.line(pts, fill=c, width=w)
    if k == "battery":
        ln([(-h, 0), (-12, 0)]); ln([(12, 0), (h, 0)])
        for xx, hh in ((-12, 34), (-2, 18), (8, 34), (18, 18)): ln([(xx, -hh), (xx, hh)])
        text(d, *T(-h + 8, -26), "+", 26, e.get("style", "line"), "mm"); text(d, *T(h - 8, -26), "-", 26, e.get("style", "line"), "mm")
    elif k in ("fuse", "fusible_link"):
        ln([(-h, 0), (-30, 0)]); ln([(30, 0), (h, 0)]); d.polygon([T(-30, -12), T(30, -12), T(30, 12), T(-30, 12)], outline=c, width=w)
        ln([(-30, 0), (30, 0)]) if k == "fuse" else ln([(-30, -12), (30, 12)])
    elif k in ("switch", "key_switch", "pushbutton", "switch_nc"):
        ln([(-h, 0), (-25, 0)]); ln([(25, 0), (h, 0)]); circle(-25, 0, 5); circle(25, 0, 5)
        if k == "switch_nc": ln([(-25, 0), (28, 6)])
        elif k == "pushbutton": ln([(-25, -18), (25, -18)]); ln([(0, -18), (0, -40)])
        else: ln([(-25, 0), (22, -26)])
        if k == "key_switch": ln([(-6, -46), (6, -46), (6, -30), (-6, -30), (-6, -46)])
    elif k == "relay":     # coil box + NO contact drawn above
        ln([(-h, 0), (-25, 0)]); ln([(25, 0), (h, 0)]); d.polygon([T(-25, -16), T(25, -16), T(25, 16), T(-25, 16)], outline=c, width=w); ln([(-25, 16), (25, -16)])
        ln([(-h, -60), (-22, -60)]); ln([(22, -60), (h, -60)]); ln([(-22, -60), (18, -80)]); ln([(0, -16), (0, -66)]) if e.get("linkage", True) else None
    elif k == "solenoid":
        ln([(-h, 0), (-30, 0)]); ln([(30, 0), (h, 0)])
        for i in range(4): d.arc([*T(-30 + i * 15, -10), *T(-15 + i * 15, 10)], 180, 360, fill=c, width=w) if e.get("rot", 0) % 180 == 0 else None
        ln([(-30, 18), (30, 18)])
    elif k in ("coil", "inductor"):
        ln([(-h, 0), (-36, 0)]); ln([(36, 0), (h, 0)])
        for i in range(4):
            pts = [T(-36 + i * 18 + 9 - 9 * math.cos(t / 10 * math.pi), -12 * math.sin(t / 10 * math.pi)) for t in range(11)]; d.line(pts, fill=c, width=w)
    elif k == "transformer":   # ignition coil: primary bottom, secondary top, core lines
        for yy in (14, -14):
            for i in range(4):
                pts = [T(-36 + i * 18 + 9 - 9 * math.cos(t / 10 * math.pi), yy + (12 if yy > 0 else -12) * math.sin(t / 10 * math.pi) * (1 if yy > 0 else 1)) for t in range(11)]; d.line(pts, fill=c, width=w)
        ln([(-40, -2), (40, -2)]); ln([(-40, 2), (40, 2)]); ln([(-h, 14), (-36, 14)]); ln([(36, 14), (h, 14)]); ln([(-h, -14), (-36, -14)]); ln([(36, -14), (h, -14)])
    elif k == "resistor":
        ln([(-h, 0), (-36, 0)]); ln([(36, 0), (h, 0)]); ln([(-36, 0)] + [(-30 + i * 12, -14 if i % 2 == 0 else 14) for i in range(6)] + [(36, 0)])
    elif k == "diode":
        ln([(-h, 0), (-16, 0)]); ln([(16, 0), (h, 0)]); d.polygon([T(-16, -16), T(-16, 16), T(14, 0)], outline=c, width=w); ln([(16, -16), (16, 16)])
    elif k == "capacitor":
        ln([(-h, 0), (-6, 0)]); ln([(6, 0), (h, 0)]); ln([(-6, -22), (-6, 22)]); ln([(6, -22), (6, 22)])
    elif k in ("lamp", "motor", "generator", "sensor", "meter"):
        ln([(-h, 0), (-26, 0)]); ln([(26, 0), (h, 0)]); circle(0, 0, 26)
        if k == "lamp": ln([(-18, -18), (18, 18)]); ln([(-18, 18), (18, -18)])
        else: text(d, *T(0, 0), {"motor": "M", "generator": "G", "sensor": "S", "meter": e.get("letter", "V")}[k], 26, e.get("style", "line"), "mm", "head")
    elif k == "spark_plug":
        ln([(-h, 0), (-8, 0)]); ln([(8, 0), (8, 22)]); ln([(-8, -14), (-8, 14)]); ln([(8, 22), (h, 22)])
        text(d, *T(0, -24), "GAP", 13, "dim", "mm")
    elif k == "ground":
        ln([(0, -h), (0, 0)])
        for i, wd in enumerate((26, 17, 8)): ln([(-wd, i * 8), (wd, i * 8)])
    elif k == "chassis":
        ln([(0, -h), (0, 0)]); ln([(-24, 0), (24, 0)])
        for i in range(4): ln([(-24 + i * 16, 0), (-32 + i * 16, 12)])
    elif k == "connector":
        ln([(-h, 0), (-10, 0)]); ln([(10, 0), (h, 0)]); ln([(-10, -12), (-10, 12)]); d.arc([*T(4, -12), *T(28, 12)], 90, 270, fill=c, width=w) if e.get("rot", 0) % 180 == 0 else ln([(10, -12), (10, 12)])
    elif k == "box":           # module / ECU / rectifier: labelled block with N terminals each side
        bw, bh = e.get("w", 160), e.get("h", 100); d.polygon([T(-bw / 2, -bh / 2), T(bw / 2, -bh / 2), T(bw / 2, bh / 2), T(-bw / 2, bh / 2)], outline=c, width=w, fill=COL["fill"])
        text(d, *T(0, 0), e.get("inner", "MODULE"), 18, e.get("style", "line"), "mm", "head")
    else:
        raise ValueError(f"unknown esym kind {k!r}")
    cx, cy = X(e["x"]), Y(e["y"])
    if e.get("rot", 0) % 180 == 90:       # vertical symbol: text to the right, always horizontal
        if e.get("ref"): text(d, cx + 42, cy - 14, e["ref"], 19, "blank", "lm", "head")
        if e.get("label"): text(d, cx + 42, cy + 14, e["label"], 17, "line", "lm")
    else:
        if e.get("ref"): text(d, cx, cy - e.get("label_dy", 44), e["ref"], 19, "blank", "mm", "head")
        if e.get("label"): text(d, cx, cy + e.get("label_dy2", 46), e["label"], 17, "line", "mm")

def wire(d, e, P):
    pts = [P(p) for p in e["pts"]]; c = colour(e.get("style", "line")); d.line(pts, fill=c, width=e.get("sw", 3), joint="curve")
    for j in e.get("dots", []): q = P(j); d.ellipse([q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7], fill=c)
    if e.get("label"):
        i = e.get("label_seg", 0); a, b = pts[i], pts[i + 1]; mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        horiz = abs(b[0] - a[0]) >= abs(b[1] - a[1])
        text(d, mx, my - 12 if horiz else my, e["label"], e.get("size", 16), e.get("label_style", "dim"), "ms" if horiz else "lm")

def projsym(d, e, X, Y):
    """Third-angle (default) or first-angle projection symbol."""
    x, y = X(e["x"]), Y(e["y"]); c = COL["line"]; s = e.get("size", 1)
    cone = [(x, y - 25 * s), (x + 70 * s, y - 40 * s), (x + 70 * s, y + 40 * s), (x, y + 25 * s)]
    circ_x = x + 130 * s if e.get("angle", "third") == "third" else x - 60 * s
    if e.get("angle", "third") == "first": cone = [(x + 70 * s, y - 25 * s), (x, y - 40 * s), (x, y + 40 * s), (x + 70 * s, y + 25 * s)]
    d.polygon(cone, outline=c, width=3)
    for r in (40, 25): d.ellipse([circ_x - r * s, y - r * s, circ_x + r * s, y + r * s], outline=c, width=3)
    text(d, x + 35 * s, y + 70 * s, "THIRD ANGLE PROJECTION" if e.get("angle", "third") == "third" else "FIRST ANGLE PROJECTION", 16, "dim", "ms")

# ---------------- isometric ----------------
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
SHADE = {"top": (34, 88, 150), "px": (26, 76, 136), "py": (20, 66, 122)}

def _proj(ox, oy, k):
    """True isometric, standard CAD axes (x right, y back, z up), viewed from front-right-top (+x, -y, +z)."""
    return lambda p: (ox + (p[0] + p[1]) * C30 * k, oy + ((p[0] - p[1]) * S30 - p[2]) * k)

def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3: return pts
    cr = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]

def _circle3(c, r, axis, n=48):
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n; a, b = r * math.cos(t), r * math.sin(t)
        out.append((c[0], c[1] + a, c[2] + b) if axis == "x" else (c[0] + a, c[1], c[2] + b) if axis == "y" else (c[0] + a, c[1] + b, c[2]))
    return out

def _depth(s):
    p = s.get("p", [0, 0, 0]); sz = s.get("size", [0, 0, 0])
    if s["type"] == "cyl":
        h = s["h"]; ax = s.get("axis", "z"); off = [0, 0, 0]; off["xyz".index(ax)] = h / 2; return p[0] + off[0] - (p[1] + off[1]) + p[2] + off[2]
    if s["type"] == "line3": return 1e9
    if s["type"] == "prism": return sum(q[0] - q[1] for q in s["pts"]) / len(s["pts"]) + s["z"] + s["h"] / 2
    return p[0] + sz[0] / 2 - (p[1] + sz[1] / 2) + p[2] + sz[2] / 2

def _solid_pts(s):
    if s["type"] == "box":
        (x, y, z), (a, b, c) = s["p"], s["size"]; return [(x + i * a, y + j * b, z + k * c) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    if s["type"] == "cyl":
        end = list(s["p"]); end["xyz".index(s.get("axis", "z"))] += s["h"]; return _circle3(s["p"], s["r"], s.get("axis", "z"), 16) + _circle3(end, s["r"], s.get("axis", "z"), 16)
    if s["type"] == "prism": return [(q[0], q[1], zz) for q in s["pts"] for zz in (s["z"], s["z"] + s["h"])]
    return [tuple(q) for q in s.get("pts", [])]

def iso(img, d, e, X, Y, base_dir="."):
    ring = None
    if e.get("model"):
        m = load_model(e["model"] if _os.path.isabs(e["model"]) else _os.path.join(base_dir, e["model"]))
        e = dict(e); e.setdefault("solids", model_solids(m))
        if e.get("auto_dims", True) and "dims" not in e: e["dims"] = auto_dims(m)
        if e.get("auto_labels", True) and "labels" not in e: ring = [l for l in auto_labels(m, 1)]
    if e.get("fit_box") and e.get("fit", True):          # auto scale + centre inside the panel
        pts = [q for s_ in e["solids"] for q in _solid_pts(s_)]
        for dm in e.get("dims", []): pts += [tuple(dm["p1"][i] + dm["off"][i] for i in range(3)), tuple(dm["p2"][i] + dm["off"][i] for i in range(3))]
        pr0 = _proj(0, 0, 1); sp = [pr0(q) for q in pts]; bx0, bx1 = min(q[0] for q in sp), max(q[0] for q in sp); by0, by1 = min(q[1] for q in sp), max(q[1] for q in sp)
        fx, fy, fw, fh = e["fit_box"]; margin = 150 if ring else 60
        k = min((fw - 2 * margin) / max(bx1 - bx0, 1), (fh - 2 * margin) / max(by1 - by0, 1))
        e["scale"] = k; e["_ox"] = fx + fw / 2 - (bx0 + bx1) / 2 * k; e["_oy"] = fy + fh / 2 - (by0 + by1) / 2 * k
    k = e.get("scale", 1)
    ox = e["_ox"] if "_ox" in e else X(e["x"]); oy = e["_oy"] if "_oy" in e else Y(e["y"])
    pr = _proj(ox, oy, k); lc = COL["line"]; sw = e.get("sw", 3)
    if ring is not None:                                   # callouts on a ring, spread so leaders don't cross
        pts = [pr(q) for s_ in e["solids"] for q in _solid_pts(s_)]; cx = (min(q[0] for q in pts) + max(q[0] for q in pts)) / 2; cy = (min(q[1] for q in pts) + max(q[1] for q in pts)) / 2
        R = max(math.hypot(q[0] - cx, q[1] - cy) for q in pts) + 70
        if e.get("fit_box"): fx, fy, fw, fh = e["fit_box"]; R = min(R, min(fw, fh) / 2 - 40)
        items = sorted(((math.atan2(pr(l["p"])[1] - cy, pr(l["p"])[0] - cx), l) for l in ring), key=lambda t: t[0])
        n = len(items); gap = min(2 * math.pi / max(n, 1) * .8, math.radians(28)); angs = [a for a, _ in items]
        for _ in range(60):
            for i in range(1, n):
                if angs[i] - angs[i - 1] < gap: mid = (angs[i] + angs[i - 1]) / 2; angs[i - 1], angs[i] = mid - gap / 2, mid + gap / 2
        e["labels"] = []
        for a, (_, l) in zip(angs, items):
            A = pr(l["p"]); rx = 1.25 if e.get("fit_box") else 1; tx, ty = cx + R * rx * math.cos(a), cy + R * math.sin(a)
            if e.get("fit_box"): tx = min(max(tx, fx + 40), fx + fw - 40); ty = min(max(ty, fy + 40), fy + fh - 40)
            e["labels"].append({"p": l["p"], "dx": tx - A[0], "dy": ty - A[1], "n": l["n"]})
    for s in sorted(e["solids"], key=lambda s: s.get("order", _depth(s))):
        st = colour(s.get("style", "line")); fill = s.get("fill", True)
        if s["type"] == "box":
            (x, y, z), (a, b, cz) = s["p"], s["size"]
            V = lambda dx, dy, dz: pr((x + dx, y + dy, z + dz))
            faces = {"py": [V(0, 0, 0), V(a, 0, 0), V(a, 0, cz), V(0, 0, cz)], "px": [V(a, 0, 0), V(a, b, 0), V(a, b, cz), V(a, 0, cz)], "top": [V(0, 0, cz), V(a, 0, cz), V(a, b, cz), V(0, b, cz)]}
            for f in ("py", "px", "top"): d.polygon(faces[f], fill=SHADE[f] if fill else BG, outline=st, width=sw)
        elif s["type"] == "prism":   # vertical extrusion of a 2-D outline (x,y) from z to z+h
            z, h = s["z"], s["h"]; base = s["pts"]; n = len(base)
            sides = []
            for i in range(n):
                a, b = base[i], base[(i + 1) % n]; nx, ny = (b[1] - a[1]), -(b[0] - a[0])   # outward normal for CCW outline
                if nx - ny > 0: sides.append(((a[0] + b[0] - a[1] - b[1]) / 2, [pr((a[0], a[1], z)), pr((b[0], b[1], z)), pr((b[0], b[1], z + h)), pr((a[0], a[1], z + h))], "px" if nx >= -ny else "py"))
            for _, poly, f in sorted(sides): d.polygon(poly, fill=SHADE[f] if fill else BG, outline=st, width=sw)
            d.polygon([pr((p[0], p[1], z + h)) for p in base], fill=SHADE["top"] if fill else BG, outline=st, width=sw)
        elif s["type"] == "cyl":
            ax = s.get("axis", "z"); p = s["p"]; r = s["r"]; h = s["h"]; end = list(p); end["xyz".index(ax)] += h
            c0 = [pr(q) for q in _circle3(p, r, ax)]; c1 = [pr(q) for q in _circle3(end, r, ax)]
            d.polygon(_hull(c0 + c1), fill=SHADE["px" if ax != "y" else "py"] if fill else BG, outline=st, width=sw)
            d.polygon(c1, fill=SHADE["top"] if fill else BG, outline=st, width=sw)
            if s.get("bore"): d.polygon([pr(q) for q in _circle3(end, s["bore"], ax)], fill=BG, outline=st, width=2)
        elif s["type"] == "line3":
            pts = [pr(q) for q in s["pts"]]; c = colour(s.get("style", "dim"))
            if s.get("dash"):
                from _common import poly as _poly; _poly(d, pts, c, s.get("sw", 2), (14, 9))
            else: d.line(pts, fill=c, width=s.get("sw", 2))
    for dm in e.get("dims", []):      # 3-D dimension: p1, p2, off (3-D offset vector), text
        a, b = dm["p1"], dm["p2"]; o = dm["off"]
        a2 = [a[i] + o[i] for i in range(3)]; b2 = [b[i] + o[i] for i in range(3)]
        A, B, A2, B2 = pr(a), pr(b), pr(a2), pr(b2); dc = COL["dim"]
        d.line([A, A2], fill=dc, width=2); d.line([B, B2], fill=dc, width=2); d.line([A2, B2], fill=dc, width=2)
        for tip, frm in ((A2, B2), (B2, A2)):
            ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
            d.polygon([tip, (tip[0] - 18 * math.cos(ang - .38), tip[1] - 18 * math.sin(ang - .38)), (tip[0] - 18 * math.cos(ang + .38), tip[1] - 18 * math.sin(ang + .38))], fill=dc)
        mx, my = (A2[0] + B2[0]) / 2, (A2[1] + B2[1]) / 2; tw = font("body", 20).getlength(dm["text"]) + 14
        d.rectangle([mx - tw / 2, my - 15, mx + tw / 2, my + 15], fill=BG); text(d, mx, my, dm["text"], 20, "line", "mm")
    for lb in e.get("labels", []):    # leader from a 3-D point to 2-D text offset
        A = pr(lb["p"]); Bp = (A[0] + lb["dx"], A[1] + lb["dy"]); dc = COL["dim"]
        d.line([A, Bp], fill=dc, width=2); d.ellipse([A[0] - 5, A[1] - 5, A[0] + 5, A[1] + 5], fill=dc)
        if lb.get("n") is not None:
            d.ellipse([Bp[0] - 27, Bp[1] - 27, Bp[0] + 27, Bp[1] + 27], outline=COL["blank"], width=5, fill=BG); text(d, Bp[0], Bp[1] + 1, str(lb["n"]), 30, "blank", "mm", "head")
        else:
            text(d, Bp[0] + (8 if lb["dx"] >= 0 else -8), Bp[1], lb["text"], 19, "line", "lm" if lb["dx"] >= 0 else "rm")

# ---------------- model.json (single source of truth) ----------------
import json as _json, os as _os
def load_model(path):
    m = _json.load(open(path, encoding="utf-8"))
    return m

def model_solids(m):
    """Convert model.json parts into iso solids (box / cyl / prism / line3)."""
    out = []
    for p in m.get("parts", []):
        s = {k: v for k, v in p.items() if k in ("p", "size", "r", "h", "axis", "bore", "pts", "z", "order", "fill", "style", "dash")}
        s["type"] = {"box": "box", "cyl": "cyl", "cylinder": "cyl", "prism": "prism", "line": "line3"}[p.get("shape", "box")]
        if s["type"] == "line3": s["pts"] = p["pts"]
        out.append(s)
    return out

def _bounds(m):
    xs, ys, zs = [], [], []
    for p in m.get("parts", []):
        sh = p.get("shape", "box")
        if sh == "box":
            for i, arr in enumerate((xs, ys, zs)): arr += [p["p"][i], p["p"][i] + p["size"][i]]
        elif sh in ("cyl", "cylinder"):
            ax = "xyz".index(p.get("axis", "z"))
            for i, arr in enumerate((xs, ys, zs)):
                arr += [p["p"][i], p["p"][i] + p["h"]] if i == ax else [p["p"][i] - p["r"], p["p"][i] + p["r"]]
        elif sh == "prism":
            xs += [q[0] for q in p["pts"]]; ys += [q[1] for q in p["pts"]]; zs += [p["z"], p["z"] + p["h"]]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

def auto_labels(m, length=240):
    """Callout leaders for every part that has a 'callout', pointing away from the model centre."""
    (x0, x1), (y0, y1), (z0, z1) = _bounds(m); cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    ctr = ((cx + cy) * C30, (cx - cy) * S30 - cz); out = []
    for p in m.get("parts", []):
        if p.get("callout") is None or p.get("shape") == "line": continue
        sh = p.get("shape", "box")
        if sh == "box": a = [p["p"][0] + p["size"][0] / 2, p["p"][1] + p["size"][1] / 2, p["p"][2] + p["size"][2]]
        elif sh == "prism": a = [sum(q[0] for q in p["pts"]) / len(p["pts"]), sum(q[1] for q in p["pts"]) / len(p["pts"]), p["z"] + p["h"]]
        else:
            ax = "xyz".index(p.get("axis", "z")); a = list(p["p"]); a[ax] += p["h"] / 2
            if ax != 2: a[2] += p["r"]
            else: a[2] += p["h"] / 2
        sx, sy = (a[0] + a[1]) * C30 - ctr[0], (a[0] - a[1]) * S30 - a[2] - ctr[1]; L = math.hypot(sx, sy) or 1
        out.append({"p": a, "dx": sx / L * length, "dy": sy / L * length, "n": p["callout"]})
    return out

def auto_dims(m):
    (x0, x1), (y0, y1), (z0, z1) = _bounds(m); u = m.get("units", "mm"); f = m.get("dim_factor", 1); fmt = m.get("dim_format", "{:.0f} " + u)
    gap = 0.25 * max(x1 - x0, y1 - y0)
    return [{"p1": [x0, y0, z0], "p2": [x1, y0, z0], "off": [0, -gap, 0], "text": "L " + fmt.format((x1 - x0) * f)},
            {"p1": [x1, y0, z0], "p2": [x1, y1, z0], "off": [gap, 0, 0], "text": "W " + fmt.format((y1 - y0) * f)},
            {"p1": [x0, y0, z0], "p2": [x0, y0, z1], "off": [-gap, 0, 0], "text": "H " + fmt.format((z1 - z0) * f)}]

def ortho(img, d, e, X, Y, base_dir="."):
    """Orthographic view of model.json parts. view: front (look -y), top (look -z), right (look -x), rear, left.
    Third-angle layout: front at bottom-left, top above it, right to its right (all share scale)."""
    m = load_model(e["model"] if _os.path.isabs(e["model"]) else _os.path.join(base_dir, e["model"]))
    v = e.get("view", "front"); k = e.get("scale", 1); ox, oy = X(e["x"]), Y(e["y"])
    (x0, x1), (y0, y1), (z0, z1) = _bounds(m)
    # (u, v_screen, depth) per view; screen origin = model min corner
    # standard CAD axes; (u right, v down, depth toward viewer); third-angle arrangement
    P = {"front": lambda p: (p[0] - x0, z1 - p[2], -p[1]), "rear": lambda p: (x1 - p[0], z1 - p[2], p[1]),
         "top": lambda p: (p[0] - x0, y1 - p[1], p[2]), "right": lambda p: (p[1] - y0, z1 - p[2], p[0]),
         "left": lambda p: (y1 - p[1], z1 - p[2], -p[0])}[v]
    axis_of_view = {"front": "y", "rear": "y", "top": "z", "right": "x", "left": "x"}[v]
    S = lambda q: (ox + q[0] * k, oy + q[1] * k)
    items = []
    for p in m.get("parts", []):
        sh = p.get("shape", "box")
        if sh == "line": continue
        if sh == "box":
            pts = [(p["p"][0] + a * p["size"][0], p["p"][1] + b * p["size"][1], p["p"][2] + c * p["size"][2]) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
            pr = [P(q) for q in pts]; us = [q[0] for q in pr]; vs = [q[1] for q in pr]
            items.append((max(q[2] for q in pr), "rect", (min(us), min(vs), max(us), max(vs)), p))
        elif sh in ("cyl", "cylinder"):
            ax = p.get("axis", "z"); c0 = list(p["p"]); c1 = list(p["p"]); c1["xyz".index(ax)] += p["h"]
            if ax == axis_of_view:
                cc = P(c1); depth = max(P(c0)[2], P(c1)[2]); items.append((depth, "circle", (cc[0], cc[1], p["r"]), p))
            else:
                ring = _circle3(c0, p["r"], ax, 16) + _circle3(c1, p["r"], ax, 16); pr = [P(q) for q in ring]
                items.append((max(q[2] for q in pr), "rect", (min(q[0] for q in pr), min(q[1] for q in pr), max(q[0] for q in pr), max(q[1] for q in pr)), p))
        elif sh == "prism":
            pts3 = [(q[0], q[1], zz) for q in p["pts"] for zz in (p["z"], p["z"] + p["h"])]; pr = [P(q) for q in pts3]
            if v == "top": items.append((max(q[2] for q in pr), "poly", [P((q[0], q[1], p["z"] + p["h"]))[:2] for q in p["pts"]], p))
            else: items.append((max(q[2] for q in pr), "rect", (min(q[0] for q in pr), min(q[1] for q in pr), max(q[0] for q in pr), max(q[1] for q in pr)), p))
    lc = COL["line"]; fill = (24, 72, 128) if e.get("shade", True) else BG
    for depth, kind, g, p in sorted(items, key=lambda t: t[0]):
        st = colour(p.get("style", "line"))
        if kind == "rect": d.rectangle([*S(g[:2]), *S(g[2:])], fill=fill, outline=st, width=3)
        elif kind == "circle":
            c = S(g[:2]); r = g[2] * k; d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=fill, outline=st, width=3)
            d.line([(c[0] - r - 14, c[1]), (c[0] + r + 14, c[1])], fill=COL["dim"], width=1); d.line([(c[0], c[1] - r - 14), (c[0], c[1] + r + 14)], fill=COL["dim"], width=1)
        else: d.polygon([S(q) for q in g], fill=fill, outline=st, width=3)
    # overall dimensions for this view
    if e.get("dims", True):
        u = m.get("units", "mm"); f = m.get("dim_factor", 1); fmt = m.get("dim_format", "{:.0f} " + u)
        W_ = {"front": x1 - x0, "rear": x1 - x0, "top": x1 - x0, "right": y1 - y0, "left": y1 - y0}[v]
        H_ = {"front": z1 - z0, "rear": z1 - z0, "top": y1 - y0, "right": z1 - z0, "left": z1 - z0}[v]
        a, b = S((0, H_)), S((W_, H_)); _dim2(d, (a[0], a[1] + 50), (b[0], b[1] + 50), fmt.format(W_ * f))
        a, b = S((W_, 0)), S((W_, H_)); _dim2(d, (a[0] + 50, a[1]), (b[0] + 50, b[1]), fmt.format(H_ * f), vertical=True)
    if e.get("label", True):
        text(d, ox + (({"front": x1 - x0, "rear": x1 - x0, "top": x1 - x0}.get(v, y1 - y0)) * k) / 2, oy - 18, e.get("title", v.upper() + " VIEW"), 22, "line", "ms", "head")

def _dim2(d, a, b, label, vertical=False):
    dc = COL["dim"]; d.line([a, b], fill=dc, width=2)
    for tip, frm in ((a, b), (b, a)):
        ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
        d.polygon([tip, (tip[0] - 18 * math.cos(ang - .38), tip[1] - 18 * math.sin(ang - .38)), (tip[0] - 18 * math.cos(ang + .38), tip[1] - 18 * math.sin(ang + .38))], fill=dc)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; tw = font("body", 20).getlength(label) + 14
    if vertical: d.rectangle([mx - tw / 2, my - 15, mx + tw / 2, my + 15], fill=BG)
    else: d.rectangle([mx - tw / 2, my - 15, mx + tw / 2, my + 15], fill=BG)
    text(d, mx, my, label, 20, "line", "mm")
