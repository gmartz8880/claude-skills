#!/usr/bin/env python3
"""build_doc.py - build the vintage "Technical Order" PDF (typewriter text on aged paper) from a JSON spec.

Usage: python build_doc.py DOC.json OUT.pdf [--paper DIR] [--check]
DOC.json = {"meta": {...}, "blocks": [...]}  - see references/spec-format.md (example: templates/example-tundra/doc.json)
Block types: h1, h2, p, bullets, steps, warn, table{rows,widths}, fig{path,caption,width}, pagebreak, specs{rows},
             troubleshoot{rows}, procedure{title,purpose,tools,caution,steps,verify,fig}, sheets{caption},
             feature{n,title,diff,where,trim,what,route_o,route_a,steps,verify,caution,fig,fig_caption}
Paths in fig are relative to the JSON file. Paper backgrounds come from paper.py (made automatically).
"""
import sys, os, json, random, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from _common import FONT_DIR, safe
def build(spec_path, out, paper_dir=None, work=None, spec_override=None):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    spec = spec_override or json.load(open(spec_path, encoding="utf-8")); base = os.path.dirname(os.path.abspath(spec_path)); m = spec["meta"]
    for n, f in (("Body", "CourierPrime-Regular.ttf"), ("BodyB", "CourierPrime-Bold.ttf"), ("Stencil", "StardosStencil-Bold.ttf"), ("Type", "SpecialElite-Regular.ttf"), ("Hand", "ArchitectsDaughter-Regular.ttf")):
        pdfmetrics.registerFont(TTFont(n, os.path.join(FONT_DIR, f)))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyB", italic="Body", boldItalic="BodyB")
    paper_dir = paper_dir or os.path.join(os.path.dirname(os.path.abspath(out)), "_paper")
    if not os.path.exists(os.path.join(paper_dir, "paper0.jpg")):
        import paper; os.makedirs(paper_dir, exist_ok=True); [paper.paper(os.path.join(paper_dir, f"paper{i}.jpg"), 100 + i) for i in range(4)]
    INK = colors.HexColor("#15120e"); BLUE = colors.HexColor("#1b3a66"); RED = colors.HexColor("#8f2318")
    H1 = ParagraphStyle("h1", fontName="Stencil", fontSize=19, leading=23, textColor=BLUE, spaceBefore=10, spaceAfter=6)
    H2 = ParagraphStyle("h2", fontName="Stencil", fontSize=14, leading=18, textColor=INK, spaceBefore=9, spaceAfter=4)
    B = ParagraphStyle("b", fontName="Body", fontSize=10.8, leading=14.6, textColor=INK, spaceAfter=5)
    BL = ParagraphStyle("bl", parent=B, leftIndent=16, bulletIndent=2); W = ParagraphStyle("w", parent=B, textColor=RED, fontName="BodyB")
    CAP = ParagraphStyle("cap", parent=B, fontSize=9.5, alignment=1, textColor=BLUE)
    P = lambda t, s=B: Paragraph(safe(t), s)
    def table(rows, widths, fs=9.4):
        st = ParagraphStyle("t", parent=B, fontSize=fs, leading=fs + 3); sth = ParagraphStyle("th", parent=st, fontName="Stencil", textColor=BLUE, fontSize=fs + .6)
        t = Table([[P(c, sth) for c in rows[0]]] + [[P(c, st) for c in r] for r in rows[1:]], colWidths=[w * inch for w in widths], repeatRows=1)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .6, colors.HexColor("#5a4e3c")), ("LINEBELOW", (0, 0), (-1, 0), 1.4, BLUE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        return t
    def warn(t):
        tb = Table([[P("<font name='Stencil'>CAUTION -</font> " + t, W)]], colWidths=[6.6 * inch])
        tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1.6, RED), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)])); return tb
    def fig(path, cap, w=6.6):
        from PIL import Image as PI
        path = path.replace("{work}", work or base)
        path = path if os.path.isabs(path) else os.path.join(base, path); iw, ih = PI.open(path).size
        return KeepTogether([Image(path, width=w * inch, height=w * inch * ih / iw), P(cap, CAP)])
    bl = lambda items: [Paragraph(safe(i), BL, bulletText="-") for i in items]
    steps = lambda items: [Paragraph(safe(i), BL, bulletText=f"{k}.") for k, i in enumerate(items, 1)]
    stamps = {int(k): v for k, v in m.get("stamps", {"1": "CONTROLLED COPY", "4": "FIELD VERIFIED"}).items()}
    def onpage(c, doc):
        n = doc.page; c.drawImage(os.path.join(paper_dir, f"paper{n % 4}.jpg"), 0, 0, width=letter[0], height=letter[1])
        c.setStrokeColor(INK); c.setLineWidth(1.2); c.rect(.55 * inch, .55 * inch, letter[0] - 1.1 * inch, letter[1] - 1.1 * inch)
        c.setLineWidth(.5); c.rect(.6 * inch, .6 * inch, letter[0] - 1.2 * inch, letter[1] - 1.2 * inch)
        if n > 1:
            c.setFont("Stencil", 10); c.setFillColor(BLUE)
            c.drawString(.8 * inch, letter[1] - .8 * inch, safe(f"{m['company']} · {m['doc_no']} · MODEL {m.get('model_no', '-')}"))
            c.drawRightString(letter[0] - .8 * inch, letter[1] - .8 * inch, safe(f"REV. {m.get('rev', 'A')} · {m['date']}"))
            c.line(.8 * inch, letter[1] - .86 * inch, letter[0] - .8 * inch, letter[1] - .86 * inch)
            c.setFont("Body", 9); c.setFillColor(INK); c.drawCentredString(letter[0] / 2, .75 * inch, f"- {n} -     CONTROLLED COPY · VERIFY ALL PART NUMBERS BY VIN / SERIAL")
        if n in stamps:
            random.seed(n); c.saveState(); c.translate(letter[0] - 2.4 * inch, 1.55 * inch); c.rotate(random.uniform(-14, -6))
            col = colors.Color(.62, .12, .1, .5); c.setStrokeColor(col); c.setFillColor(col); c.setLineWidth(2.2)
            c.roundRect(-.1 * inch, -.15 * inch, 2.05 * inch, .62 * inch, 6); c.setFont("Stencil", 15); c.drawString(.02 * inch, .18 * inch, stamps[n])
            c.setFont("Body", 7.5); c.drawString(.05 * inch, 0, safe(f"{m['company']} · QA DEPT.")); c.restoreState()
    doc = BaseDocTemplate(out, pagesize=letter, leftMargin=.95 * inch, rightMargin=.95 * inch, topMargin=1.05 * inch, bottomMargin=1.0 * inch, title=f"{m['doc_no']} {m['title']}", author=m["company"])
    doc.addPageTemplates([PageTemplate(frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)], onPage=onpage)])
    S = [Spacer(1, .1 * inch), P(m["company"], ParagraphStyle("c0", fontName="Stencil", fontSize=40, leading=46, alignment=1, textColor=BLUE)),
         P(m.get("tagline", ""), ParagraphStyle("c1", fontName="Body", fontSize=11.5, alignment=1, textColor=INK)), Spacer(1, .2 * inch),
         P(f"TECHNICAL ORDER<br/>{m['doc_no']}", ParagraphStyle("c2", fontName="Stencil", fontSize=25, leading=31, alignment=1, textColor=INK)), Spacer(1, .12 * inch),
         P(m["title"], ParagraphStyle("c3", fontName="Body", fontSize=13, leading=18, alignment=1, textColor=INK)),
         P(f"MODEL NO. {m.get('model_no', '-')}", ParagraphStyle("c4", fontName="Stencil", fontSize=16, leading=22, alignment=1, textColor=RED)), Spacer(1, .15 * inch)]
    if m.get("cover_image"): S += [fig(m["cover_image"], m.get("cover_caption", ""), 5.6), Spacer(1, .1 * inch)]
    if m.get("applicability"): S.append(table([["APPLICABILITY", "DATA"]] + m["applicability"], [1.6, 5.0], 9.6))
    S.append(PageBreak())
    for blk in spec["blocks"]:
        k, v = next(iter(blk.items()))
        if k == "h1": S.append(P(v, H1))
        elif k == "h2": S.append(P(v, H2))
        elif k == "p": S.append(P(v))
        elif k == "bullets": S += bl(v)
        elif k == "steps": S += steps(v)
        elif k == "warn": S += [warn(v), Spacer(1, 6)]
        elif k == "table": S.append(table(v["rows"], v["widths"], v.get("size", 9.4)))
        elif k == "fig": S.append(fig(v["path"], v.get("caption", ""), v.get("width", 6.6)))
        elif k == "pagebreak": S.append(PageBreak())
        elif k == "feature":
            S += [P(f"CALLOUT {v['n']} - {v['title']}  {v.get('diff', '')}", H2),
                  table([["LOCATION", "FACTORY ON", "WHAT IT DOES"], [v["where"], v["trim"], v["what"]]], [1.8, 1.6, 3.2]), Spacer(1, 4),
                  P("<b>Route O (OEM):</b> " + v["route_o"]), P("<b>Route A (Aftermarket):</b> " + v["route_a"]), P("<b>Procedure (recommended route):</b>")]
            S += steps(v["steps"]); S.append(P("<b>Verify:</b> " + v["verify"]))
            if v.get("caution"): S.append(warn(v["caution"]))
            if v.get("fig"): S += [Spacer(1, 6), fig(v["fig"], v.get("fig_caption", ""))]
            S.append(Spacer(1, 8))
        elif k == "procedure":
            S.append(P(v["title"], H2))
            if v.get("purpose"): S.append(P("<b>Purpose:</b> " + v["purpose"]))
            if v.get("tools"): S.append(P("<b>Tools / parts:</b> " + ", ".join(v["tools"])))
            if v.get("caution"): S += [warn(v["caution"]), Spacer(1, 4)]
            S += steps(v["steps"])
            if v.get("verify"): S.append(P("<b>Verify:</b> " + v["verify"]))
            if v.get("fig"): S += [Spacer(1, 6), fig(v["fig"], v.get("fig_caption", ""))]
            S.append(Spacer(1, 8))
        elif k == "specs":
            S.append(table([["ITEM", "VALUE"]] + v["rows"], v.get("widths", [2.6, 4.0]), v.get("size", 9.4)))
        elif k == "troubleshoot":
            S.append(table([["SYMPTOM", "LIKELY CAUSE", "CHECK / FIX"]] + v["rows"], v.get("widths", [1.8, 2.0, 2.8]), v.get("size", 9.2)))
        elif k == "matrix":   # full trim / option matrix from tiers.json, split into 6-tier chunks
            tpath = v.get("source", "tiers.json"); tpath = tpath if os.path.isabs(tpath) else os.path.join(base, tpath)
            t = json.load(open(tpath, encoding="utf-8")); tiers = t["tiers"]; sym = {"S": "STD", "O": "OPT", "P": "PKG", "-": "-", "": "-"}
            for c0 in range(0, len(tiers), 6):
                chunk = tiers[c0:c0 + 6]
                rows = [[f"FEATURE / OPTION ({t.get('tier_label', 'TRIM')} ->)"] + [tr["name"] + (f"<br/>{tr['code']}" if tr.get("code") else "") for tr in chunk]]
                for g in t["groups"]:
                    rows.append([f"<b>{g['group'].upper()}</b>"] + [""] * len(chunk))
                    for f_ in g["features"]:
                        rows.append([f_["feature"] + (f" [{f_['code']}]" if f_.get("code") else "")] + [sym.get(str(x).upper(), str(x)) for x in f_["values"][c0:c0 + 6]])
                fw = 2.4; S.append(table(rows, [fw] + [(6.6 - fw) / len(chunk)] * len(chunk), v.get("size", 8.4))); S.append(Spacer(1, 8))
            S.append(P("Key: STD = standard, OPT = optional, PKG = part of a package, - = not available. Codes in [ ] are the manufacturer's option / package codes.", CAP))
        elif k == "key":      # key to symbols, abbreviations and conventions used in the manual and drawings
            rows = [["SYMBOL / TERM", "MEANING"], ["CAUTION box (red)", "Hazard - read before the step it precedes"], ["[n/5]", "Difficulty: 1 bolt-on ... 5 dealer programming"],
                    ["STD / OPT / PKG / -", "Standard / optional / in a package / not available"], ["Callout n", "Numbered part on the drawings (Callout Index, sheet 1)"],
                    ["REF / APPROX. / TYP.", "Reference / approximate / typical value - verify on your unit"], ["Third-angle", "TOP view above FRONT, RIGHT view beside FRONT"],
                    ["AWG, GND, LOTO, SRS", "Wire gauge, ground, lockout-tagout, airbag system"], ["MODEL NO.", "Manufacturer model number this document applies to"]] + v.get("extra", [])
            S.append(table(rows, [2.2, 4.4], 9.6))
        elif k == "sheets":   # every blueprint sheet as a full-width appendix figure
            import glob as _g
            from PIL import Image as _PI
            for i, pth in enumerate(sorted(_g.glob(os.path.join(work or base, "sheet-*.jpg"))), 1):
                rot = pth.replace(".jpg", "_rot.jpg"); _PI.open(pth).rotate(90, expand=True).save(rot, quality=90)   # landscape sheet fills a portrait page
                S += [PageBreak(), fig(rot, f"{v.get('caption', 'DRAWING SHEET')} {i}  (rotated - turn page to read)", 5.85)]
        else: raise ValueError(f"unknown block {k!r}")
    if m.get("signoff"): S += [Spacer(1, 18), table([["PREPARED", "CHECKED", "APPROVED"], m["signoff"]], [2.2, 2.2, 2.2], 10)]
    doc.build(S); return out
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?"); ap.add_argument("out", nargs="?"); ap.add_argument("--paper"); ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        try: import reportlab; print("ready"); sys.exit(0)
        except ImportError: print("missing reportlab - run setup_env.py"); sys.exit(1)
    if not a.spec or not a.out: ap.print_help(); sys.exit(2)
    try: print(build(a.spec, a.out, a.paper))
    except (KeyError, ValueError, OSError) as e: print(f"ERROR: {e}. See references/spec-format.md", file=sys.stderr); sys.exit(1)
