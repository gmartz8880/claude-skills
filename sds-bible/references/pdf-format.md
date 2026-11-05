# SDS PDF Format (from the original sds-generator layout)

Use Python `reportlab` (`SimpleDocTemplate` + flowables). Letter size, 0.75" margins.

## Fonts and colors
- Body Helvetica 9pt, 1.15x line spacing; sub-labels Helvetica-Bold 9pt; section bar titles Helvetica-Bold 11pt.
- Navy #1B3A5C for section bars, the product-name line, and the rule under the header.
- Table header rows shaded light gray-blue (e.g. #D9E2EC) with bold black text; thin gray (#B0B7C3) grid lines.

## Page 1 header
1. "SAFETY DATA SHEET" — large Helvetica-Bold (~22pt), centered.
2. "GHS Format — OSHA HazCom 2012 (29 CFR 1910.1200 Appendix D)" — 9pt, centered.
3. Product name — Helvetica-Bold ~13pt, navy, centered.
4. "Prepared by: Gabriel Martz" — 9pt, centered.
5. Navy horizontal rule, full width.

## Section bars
Full-width navy bars with white bold text "SECTION N — NAME" (all caps), small padding, space above each bar.

## Body layout
- Label/value pairs (Section 1, signal word, pictograms, 2(c)–2(e), Section 9, etc.): two-column table, bold label column about 35% width, value column wraps; light horizontal separator lines between rows, no outer box.
- Number Appendix D subheadings in bold, e.g. "2(a) GHS Classification per 29 CFR 1910.1200(d)(1):", "2(b) GHS Label Elements:", "9(a) ...".
- Section 2 classification as a gridded table: Hazard Class | Category | Basis.
- Pictograms, H-codes, and P-codes as bullet lists, one per line, formatted "• H315 — Causes skin irritation"; pictogram names in bold with the hazard in parentheses. Combined P-codes stay together (P305+P351+P338).
- Include HMIS and NFPA 704 ratings as label/value rows at the end of Section 2.
- Section 3 as a gridded table: Chemical Name | CAS No. | Conc. (wt%) | Other Names; put formulation notes in 8pt below it.
- Section 8 limits, Section 15 three-way comparison, abbreviation legend (two columns: Abbreviation | Meaning), and HVA matrix as gridded tables with shaded headers; HVA risk cells green/yellow/orange/red.
- Section 16 "References and Data Sources:" as bullets, "• Source name — description: full URL".
- End with a bold "EDUCATIONAL DISCLAIMER:" paragraph (8pt) stating the SDS is for educational/training use, built from public manufacturer SDS and OSHA/NIOSH data, must be verified against the manufacturer's current SDS and regulations before workplace use, does not replace professional safety guidance, and cites 29 CFR 1910.1200 Appendix D Table D.1 with its Federal Register history.

## Footer (every page)
8pt gray text above a thin rule: left product name, center "GHS SDS — 16 Sections", right "Page X of Y". Build once to a buffer on a `copy.deepcopy` of the flowables to get the total, then build the real file (reused flowables raise LayoutError).

## File
Save to `/home/user/workspace/<Substance_Name>_SDS.pdf` (underscores, no spaces).
