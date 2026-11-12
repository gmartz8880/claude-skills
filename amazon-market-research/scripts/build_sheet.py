#!/usr/bin/env python3
"""Build a styled Amazon comparison workbook from a JSON research file.

Usage:
  python build_sheet.py research.json -o Comparison.xlsx
  python build_sheet.py --check            # verify openpyxl is available
  python build_sheet.py --example          # print an example research.json

Rows are sorted by listing price (low to high), then by feature count (high to low).
Pictures: an item's "image_path" (local file) is embedded as a real picture; otherwise
the cell gets Excel 365 IMAGE() pointing at "image_url" (or an ASIN image link).
Exit codes: 0 ok, 1 bad input, 2 missing dependency.
"""
import argparse, json, sys

EXAMPLE = {
  "title": "Wireless Earbuds Research",
  "criteria": ["Active noise cancelling", "8h+ battery", "Under $150"],
  "font": "Comfortaa",
  "researched": "2026-11-12",
  "spec_columns": ["Battery (h)", "ANC"],
  "items": [
    {"group": "user", "name": "Example Earbuds Model A", "asin": "B0AAAAAAAA",
     "price": 129.00, "list_price": 179.00, "price_source": "Amazon via camelcamelcamel, <date>",
     "specs": {"Battery (h)": 10, "ANC": "Yes"}, "feature_count": 6,
     "features": "ANC, transparency mode, wireless charging case, IPX4, multipoint",
     "meets": "YES", "note": "Longest battery"},
    {"group": "outlier_positive", "name": "Example premium pick", "asin": "B0XXXXXXXX", "price": 249.99,
     "specs": {"Battery (h)": 8, "ANC": "Yes"}, "feature_count": 7, "features": "...",
     "meets": "OVER BUDGET", "note": "Best tech, over budget"}
  ],
  "summary": [["Best value", "..."], ["Market reality", "..."]],
  "sources": [["camelcamelcamel - Model A", "https://camelcamelcamel.com/product/B0AAAAAAAA"]]
}

GROUP_LABEL = {"user": "Your pick", "new": "New find", "outlier_positive": "Outlier (+)", "outlier_negative": "Outlier (-)"}
STATUS_COLOR = {"YES": "2E9E5B", "NO": "D64545", "VERIFY": "E0A100", "OVER BUDGET": "7B5CD6"}


def need_openpyxl():
    try:
        import openpyxl  # noqa
        return True
    except ImportError:
        return False


def image_formula(item):
    url = item.get("image_url") or (
        "https://ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=%s&Format=_SL250_"
        "&ID=AsinImage&MarketPlace=US&ServiceVersion=20070822&WS=1" % item["asin"])
    return '=IFERROR(_xlfn.IMAGE("%s",,1),"see link")' % url


def build(data, out):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    F = data.get("font", "Comfortaa")
    navy, teal, coral, lav, white = "1F2A44", "13A89E", "FF6B6B", "EEF2FF", "FFFFFF"
    thin = Side(style="thin", color="D0D7E5"); B = Border(left=thin, right=thin, top=thin, bottom=thin)
    specs = data.get("spec_columns", [])
    H = ["#", "Picture", "Product", "ASIN", "Listing Price", "List / Was Price", "Price Source & Date"] + specs + \
        ["Feature Count", "Features", "Amazon Link", "Meets All?", "Group", "Notes"]
    W = [5, 22, 34, 14, 13, 13, 30] + [12] * len(specs) + [10, 52, 16, 13, 12, 34]
    ncol = len(H)
    items = data["items"]
    for it in items:
        if not it.get("asin") or len(it["asin"]) != 10:
            raise ValueError("Every item needs a 10-character ASIN: %r" % it.get("name"))
    main = [i for i in items if not i.get("group", "").startswith("outlier")]
    outl = [i for i in items if i.get("group", "").startswith("outlier")]
    key = lambda i: (i["price"] if isinstance(i.get("price"), (int, float)) else 1e9, -i.get("feature_count", 0))
    main.sort(key=key); outl.sort(key=lambda i: 0 if i["group"] == "outlier_positive" else 1)

    wb = Workbook(); ws = wb.active; ws.title = "Comparison"; ws.sheet_view.showGridLines = False
    last = get_column_letter(ncol)
    ws.merge_cells("A1:%s1" % last); ws["A1"] = data.get("title", "Market Research") + "  -  Amazon only"
    ws["A1"].font = Font(name=F, size=20, bold=True, color=white); ws["A1"].fill = PatternFill("solid", fgColor=navy)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center"); ws.row_dimensions[1].height = 42
    ws.merge_cells("A2:%s2" % last)
    ws["A2"] = "Must-haves: " + "  |  ".join(data.get("criteria", [])) + \
        ".   Sorted by price (low to high), then feature count.   Prices dated per row - confirm at checkout."
    ws["A2"].font = Font(name=F, size=10, italic=True, color=navy); ws["A2"].fill = PatternFill("solid", fgColor="DDF4F1")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); ws.row_dimensions[2].height = 30

    def header(r):
        for c, h in enumerate(H, 1):
            x = ws.cell(r, c, h); x.font = Font(name=F, bold=True, color=white, size=11)
            x.fill = PatternFill("solid", fgColor=teal); x.border = B
            x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[r].height = 34

    pics = []
    def put(r, idx, it, band):
        lp = it.get("list_price")
        vals = [idx, None, it["name"], it["asin"], it["price"] if isinstance(it.get("price"), (int, float)) else "Check listing",
                lp if lp else "-", it.get("price_source", "")] + [it.get("specs", {}).get(s, "") for s in specs] + \
               [it.get("feature_count", ""), it.get("features", ""), "Open on Amazon", it.get("meets", ""),
                GROUP_LABEL.get(it.get("group", "new"), it.get("group", "")), it.get("note", "")]
        for c, v in enumerate(vals, 1):
            x = ws.cell(r, c, v); x.font = Font(name=F, size=10, color=navy); x.border = B
            x.fill = PatternFill("solid", fgColor=band)
            x.alignment = Alignment(vertical="center", wrap_text=True,
                                    horizontal="left" if H[c - 1] in ("Product", "Price Source & Date", "Features", "Notes") else "center")
        ws.cell(r, 3).font = Font(name=F, size=10, bold=True, color=navy)
        if isinstance(it.get("price"), (int, float)):
            ws.cell(r, 5).number_format = "$#,##0.00"; ws.cell(r, 5).font = Font(name=F, size=12, bold=True, color="0B7A5E")
        if isinstance(lp, (int, float)):
            ws.cell(r, 6).number_format = "$#,##0.00"; ws.cell(r, 6).font = Font(name=F, size=10, color="8A94A6", strike=True)
        link = ws.cell(r, H.index("Amazon Link") + 1)
        link.hyperlink = "https://www.amazon.com/dp/%s" % it["asin"]
        link.font = Font(name=F, size=10, bold=True, color="1565C0", underline="single")
        ok = ws.cell(r, H.index("Meets All?") + 1)
        ok.font = Font(name=F, size=10, bold=True, color=white)
        if it.get("meets") in STATUS_COLOR: ok.fill = PatternFill("solid", fgColor=STATUS_COLOR[it["meets"]])
        if it.get("image_path"):
            pics.append((r, it["image_path"]))
        else:
            ws.cell(r, 2).value = image_formula(it)
        ws.row_dimensions[r].height = 110

    hr = 4; header(hr); r = hr + 1
    for i, it in enumerate(main, 1):
        put(r, i, it, lav if i % 2 else white); r += 1
    if outl:
        r += 1; ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
        x = ws.cell(r, 1, "Outliers  -  one positive, one negative (shown for comparison)")
        x.font = Font(name=F, size=13, bold=True, color=white); x.fill = PatternFill("solid", fgColor=coral)
        x.alignment = Alignment(horizontal="center", vertical="center"); r += 1; header(r); r += 1
        for it in outl:
            put(r, "+" if it["group"] == "outlier_positive" else "-", it,
                "FFF6E0" if it["group"] == "outlier_positive" else "FDECEC"); r += 1
    for c, w in enumerate(W, 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    if pics:
        from openpyxl.drawing.image import Image as XImg
        for row, path in pics:
            im = XImg(path); scale = min(140 / im.width, 135 / im.height, 1.0)
            im.width, im.height = int(im.width * scale), int(im.height * scale)
            ws.add_image(im, "B%d" % row)
    ws.freeze_panes = "D5"; ws.auto_filter.ref = "A%d:%s%d" % (hr, last, hr + len(main))
    ws.page_setup.orientation = "landscape"; ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0

    s = wb.create_sheet("Summary"); s.sheet_view.showGridLines = False
    s.column_dimensions["A"].width = 30; s.column_dimensions["B"].width = 95
    s.merge_cells("A1:B1"); s["A1"] = "Bottom line"
    s["A1"].font = Font(name=F, size=18, bold=True, color=white); s["A1"].fill = PatternFill("solid", fgColor=navy)
    rows = list(data.get("summary", [])) + [["Researched", data.get("researched", "")]]
    for i, (a, b) in enumerate(rows, 3):
        s.cell(i, 1, a).font = Font(name=F, bold=True, color=white)
        s.cell(i, 1).fill = PatternFill("solid", fgColor=[teal, coral, "E0A100", "7B5CD6"][i % 4])
        s.cell(i, 1).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        s.cell(i, 2, b).font = Font(name=F, size=11, color=navy)
        s.cell(i, 2).alignment = Alignment(vertical="center", wrap_text=True); s.row_dimensions[i].height = 44
    src = wb.create_sheet("Sources"); src.column_dimensions["A"].width = 40; src.column_dimensions["B"].width = 90
    src["A1"], src["B1"] = "Source", "URL"
    for x in (src["A1"], src["B1"]): x.font = Font(name=F, bold=True, color=white); x.fill = PatternFill("solid", fgColor=teal)
    for i, (a, b) in enumerate(data.get("sources", []), 2):
        src.cell(i, 1, a).font = Font(name=F, size=10)
        y = src.cell(i, 2, b); y.hyperlink = b; y.font = Font(name=F, size=10, color="1565C0", underline="single")
    wb.calculation.fullCalcOnLoad = True
    wb.save(out)
    return {"output": out, "main_rows": len(main), "outliers": len(outl), "embedded_pictures": len(pics)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("research", nargs="?"); ap.add_argument("-o", "--out", default="Comparison.xlsx")
    ap.add_argument("--check", action="store_true"); ap.add_argument("--example", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.example:
        print(json.dumps(EXAMPLE, indent=2)); return 0
    if a.check:
        ok = need_openpyxl(); print(json.dumps({"openpyxl": ok}) if a.json else ("ok" if ok else "missing openpyxl: pip install openpyxl"))
        return 0 if ok else 2
    if not a.research:
        ap.error("give a research.json file (see --example)")
    if not need_openpyxl():
        print("missing openpyxl: run  pip install openpyxl", file=sys.stderr); return 2
    try:
        with open(a.research, encoding="utf-8") as f: data = json.load(f)
        res = build(data, a.out)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print("Input problem: %s" % e, file=sys.stderr); return 1
    print(json.dumps(res) if a.json else "Saved %(output)s (%(main_rows)d rows, %(outliers)d outliers)" % res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
