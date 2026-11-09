"""Shared drawing helpers: fonts, colours, glyph-safe text, PIL primitives (dashed lines, curves)."""
import os, math
from PIL import ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(HERE), "assets", "fonts")
FONTS = {"body": "CourierPrime-Bold.ttf", "type": "SpecialElite-Regular.ttf", "head": "StardosStencil-Bold.ttf", "stencil": "StardosStencil-Regular.ttf",
         "mono": "CourierPrime-Regular.ttf", "monob": "CourierPrime-Bold.ttf", "hand": "ArchitectsDaughter-Regular.ttf"}
BG = (0x12, 0x3f, 0x73)          # renderer background; age.py keys off this exact colour
COL = {"line": (232, 241, 255), "dim": (156, 195, 238), "blank": (255, 211, 107), "red": (255, 138, 122),
       "pencil": (255, 156, 138), "fill": (22, 74, 133), "grid": (42, 92, 148), "grid2": (58, 110, 168)}
# glyphs the vintage fonts lack -> ASCII stand-ins
GLYPH = {"→": "->", "←": "<-", "≥": ">=", "≤": "<=", "★": "*", "☆": "o", "✓": "OK", "✗": "X", "−": "-", "≈": "~", "°": " deg"}
_cache = {}
def font(kind, size):
    k = (kind, int(size))
    if k not in _cache:
        _cache[k] = ImageFont.truetype(os.path.join(FONT_DIR, FONTS[kind]), int(size))
    return _cache[k]
def safe(t):
    t = str(t)
    for a, b in GLYPH.items():
        t = t.replace(a, b)
    return t
def colour(style):
    return COL.get(style, COL["line"]) if isinstance(style, str) else tuple(style)
def dashed(d, p1, p2, fill, width, dash=(16, 10)):
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    if L == 0: return
    ux, uy = (x2 - x1) / L, (y2 - y1) / L; pos = 0; on = True; i = 0
    while pos < L:
        seg = dash[i % 2]; e = min(pos + seg, L)
        if on: d.line([(x1 + ux * pos, y1 + uy * pos), (x1 + ux * e, y1 + uy * e)], fill=fill, width=width)
        pos = e; on = not on; i += 1
def poly(d, pts, fill, width, dash=None, closed=False):
    pts = list(pts) + ([pts[0]] if closed else [])
    if dash:
        for a, b in zip(pts, pts[1:]): dashed(d, a, b, fill, width, dash)
    else:
        d.line(pts, fill=fill, width=width, joint="curve")
def path_points(cmds, ox=0, oy=0, steps=40):
    """cmds: [["M",x,y],["L",x,y],["Q",cx,cy,x,y],["C",c1x,c1y,c2x,c2y,x,y],["Z"]] -> list of point lists."""
    out, cur, start = [], None, None
    for c in cmds:
        op = c[0].upper(); v = [float(z) for z in c[1:]]
        if op == "M":
            if cur: out.append(cur)
            start = (v[0] + ox, v[1] + oy); cur = [start]
        elif op == "L":
            cur.append((v[0] + ox, v[1] + oy))
        elif op == "Q":
            x0, y0 = cur[-1]; cx, cy, x, y = v[0] + ox, v[1] + oy, v[2] + ox, v[3] + oy
            for k in range(1, steps + 1):
                t = k / steps; cur.append(((1-t)**2*x0 + 2*(1-t)*t*cx + t*t*x, (1-t)**2*y0 + 2*(1-t)*t*cy + t*t*y))
        elif op == "C":
            x0, y0 = cur[-1]; a, b, c2, d2, x, y = [z + (ox if i % 2 == 0 else oy) for i, z in enumerate(v)]
            for k in range(1, steps + 1):
                t = k / steps; m = 1 - t
                cur.append((m**3*x0 + 3*m*m*t*a + 3*m*t*t*c2 + t**3*x, m**3*y0 + 3*m*m*t*b + 3*m*t*t*d2 + t**3*y))
        elif op == "Z":
            cur.append(start)
    if cur: out.append(cur)
    return out
def text(d, x, y, t, size=28, style="line", anchor="ls", kind="body"):
    """anchor: PIL anchors; 'ls' left-baseline, 'ms' middle-baseline, 'rs' right-baseline."""
    d.text((x, y), safe(t), font=font(kind, size), fill=colour(style), anchor=anchor)
