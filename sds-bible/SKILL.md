---
name: sds-bible
description: "Generates a complete 16-section GHS Safety Data Sheet (SDS/MSDS) as Word, PDF, or both per 29 CFR 1910.1200 Appendix D with general industry (1910) and construction (1926) requirements side by side, industrial hygiene exposure controls, and a hazard vulnerability assessment for gases, vapors, and dusts. The sole SDS generator for all skills. Load when the user asks to make, generate, or write an SDS/MSDS for any chemical, solvent, fuel, gas, dust, or product. Not for exposure-limit questions without an SDS request."
metadata:
  author: Gabriel Martz
  version: '1.0'
---

# SDS Bible

Merged SDS requirements from the safety-bible and industrial-hygiene-bible skills, covering both general industry (29 CFR 1910) and construction (29 CFR 1926). This is the only skill that generates SDSs; other skills (safety-bible, industrial-hygiene-bible, sds-generator) hand off to it. Before any research, ask the user once whether they want a Word document, a PDF, or both, then produce that format for each substance. Do not ask whether an SDS is wanted.

## Workflow

0. **Ask for the preparer's details first.** Before doing anything else, ask the user what name (and optional organization) should appear on the "Prepared by" line. If a profile skill, memory, or an earlier message in this conversation already gives any of these, show what you found and ask the user to confirm it instead of asking again. Never guess, and never use the skill author's name or school. Do not start the task until the user has answered.
1. **Identify each substance** named by the user (pure chemicals, industrial materials, trade-name products, welding gases, refrigerants, solvents, adhesives, coatings, fuels, lubricants, cleaners, compressed gases). For a mixture/trade product, identify every hazardous ingredient above cut-off limits.
2. **Research** in this priority order:
   1. NIOSH Pocket Guide — https://www.cdc.gov/niosh/npg (limits, IDLH, respirators, symptoms, target organs, sampling methods)
   2. OSHA Occupational Chemical Database — https://www.osha.gov/chemicaldata (PEL, REL, TLV, Cal/OSHA, skin notations by agency, IARC)
   3. PubChem — https://pubchem.ncbi.nlm.nih.gov (CAS, properties, GHS H/P codes, toxicology)
   4. OSHA HazCom 29 CFR 1910.1200 and eCFR — https://www.ecfr.gov (current regulatory text)
   5. ACGIH substance page (TLV notations: Skin, SEN, OTO, A1–A5, BEI)
   6. EPA ChemView / Envirofacts (RCRA, SARA, CERCLA)
   7. Manufacturer SDS databases as a reference model
   8. Construction sources — read `references/construction-1926.md` for the 1926 standards, NFPA 241, and ANSI/ASSP A10 materials to check for every substance.
   When sources disagree, never pick one: list every value and tag each with its origin (agency, standard/table, year), e.g. "Skin: No — ACGIH (2006); Yes — Cal/OSHA PEL; 'Skin' — OSHA toluene page (outdated)". Note which listing is most current.
3. **Collect:** CAS, formula, MW, synonyms; GHS Rev. 3 classification, signal word, all H-codes, P-codes, pictogram names; physical properties (flash point, BP, VP, vapor density, LEL/UEL, SG, solubility, autoignition, pH); exposure limits (OSHA PEL TWA/STEL/C/peak, Cal/OSHA, NIOSH REL/IDLH, ACGIH TLV/STEL with notations and year, BEI, action level if a substance-specific standard exists); first aid by route; fire data (incl. BLEVE risk); spill; handling/storage (1910.106 for flammable liquids); PPE (1910.132–.138, respirators 1910.134); toxicology (LD50/LC50, IARC/NTP/OSHA carcinogen); DOT (UN number, class, packing group, ERG guide per 49 CFR 171–180); RCRA codes (40 CFR 261), SARA 302/311/312/313, CERCLA RQ, CAA HAP, TSCA, Prop 65, state RTK.
4. **Three-way comparison.** For every requirement that differs by sector, give all three answers with citations: (1) General Industry — 29 CFR 1910, (2) Construction — 29 CFR 1926, (3) Consensus/recommended — NIOSH, ACGIH, NFPA, ANSI/ASSP, Cal/OSHA. If two agree, still list all three and mark "same as 1910." Applies to limits, HazCom, PPE, respirators, storage, fire protection, training, and medical surveillance.
5. **Hazard vulnerability assessment.** Always run it when the substance is a gas, vapor (VP ≥ ~1 mmHg or flash point below 100 °F), dust, fume, mist, or fiber; otherwise include a short note that airborne hazard is low and why. Read `references/hva-airborne.md` for the method and table.
6. **Build all 16 sections** per 29 CFR 1910.1200 Appendix D Table D.1 (sections 12–15 non-mandatory but always included). Write "No applicable information available." for any true gap; never leave a subheading blank.
7. **Render the chosen format(s)**: PDF, Word (.docx), or both. Inspect every page, fix defects, then share.

## Section Contents

1. Identification — product name, CAS, synonyms, recommended use and restrictions, manufacturer info (or "Educational SDS — refer to supplier SDS"), CHEMTREC 1-800-424-9300
2. Hazard(s) Identification — GHS classification, signal word, H-codes, P-codes, pictogram names in bold, hazards not otherwise classified (e.g. ototoxicant)
3. Composition — chemical name, CAS, concentration; all hazardous ingredients for mixtures
4. First-Aid Measures — by route; key symptoms; when to seek medical attention
5. Fire-Fighting — suitable/unsuitable media, specific hazards (vapor density, flashback, BLEVE), flash point, LEL/UEL, autoignition, firefighter PPE
6. Accidental Release — personal precautions/PPE, environmental precautions (CERCLA RQ reporting), containment and cleanup
7. Handling and Storage — precautions, incompatibles; flammable liquid class and storage per 1910.106 and 1926.152 (container/cabinet/indoor quantity limits); compressed gas cylinders per 1910.101/.253 and 1926.350
8. Exposure Controls/PPE (industrial hygiene depth):
   - Limits table: Agency | TWA | STEL/Ceiling/Peak | Skin | Source — rows for OSHA General Industry PEL (1910.1000 Z-table or substance standard), OSHA Construction PEL (1926.55 Appendix A or 1926 substance standard such as 1926.62 lead, 1926.1101 asbestos, 1926.1153 silica), NIOSH REL, ACGIH TLV (year + notations), Cal/OSHA PEL, NIOSH IDLH, plus action level if applicable
   - Biological monitoring (BEI determinants and timing) where one exists
   - Sampling methods: NIOSH NMAM and OSHA method numbers, media, analytical technique
   - Engineering controls following the hierarchy of controls
   - Respiratory protection by concentration with APFs, MUC = APF × OEL, IDLH/escape options, 1910.134 program and cartridge change schedule (applies to construction via 1926.103)
   - Glove material by permeation resistance (state unsuitable materials), eye/face (ANSI Z87.1), skin/body, eyewash/shower
9. Physical and Chemical Properties — all 18 subproperties (a)–(r) per Table D.1(9), plus formula/MW
10. Stability and Reactivity — reactivity, stability, hazardous reactions, conditions to avoid, incompatibles, decomposition products
11. Toxicological — routes, target organs, symptoms, acute/chronic effects, LD50/LC50, IARC/NTP/OSHA/ACGIH carcinogen status
12. Ecological — ecotoxicity, persistence, bioaccumulation (log Kow), soil mobility
13. Disposal — waste handling, RCRA codes, 40 CFR 261
14. Transport — UN number, proper shipping name, DOT class, packing group, ERG guide, marine pollutant
15. Regulatory — three-way comparison table (1910 | 1926 | Consensus) for HazCom (1910.1200 / 1926.59), exposure limits, PPE (1910.132 / 1926.28, .95–.106), training (1926.21), fire protection (1910 Subpart L / 1926 Subpart F, NFPA 241), confined spaces (1910.146 / 1926 Subpart AA); then SARA, CERCLA RQ, RCRA, CAA HAP, TSCA, Prop 65, state RTK
16. Other — preparation date, revision note, abbreviation legend (PEL, TLV, REL, STEL, TWA, C, IDLH, LEL, UEL, BEI, APF, RCRA, CERCLA, SARA, GHS), full source URLs

After Section 16, add a full-width "HAZARD VULNERABILITY ASSESSMENT — AIRBORNE RELEASE" addendum (from step 5).

## Output Specifications

- PDF: read `references/pdf-format.md` and follow it exactly (fonts, navy section bars, page 1 header with "Prepared by: <the name the user gave in step 0>", label/value tables, bulleted H/P codes, gridded tables, references list, educational disclaimer, footer, file name).
- Word: use `python-docx` and reproduce the same layout from `references/pdf-format.md` (Arial, navy-shaded section-bar cells with white bold text, same header, tables, bullets, disclaimer, footer with product name, "GHS SDS — 16 Sections", and Page X of Y fields). Save as `/home/user/workspace/<Substance_Name>_SDS.docx`.

## Delivery

Share each file in the chosen format(s), then add a "Generated SDS" section to the answer: substance name and CAS, signal word and top hazard classes, key PPE, the top HVA scenario and its risk rating, any notable 1910 vs 1926 vs consensus differences, one critical safety/IH note (e.g. BLEVE risk, vapor accumulation, carcinogen status, ototoxicity), and a note that the full file is attached. For multiple substances, share the file(s) for each and summarize all in one "Generated SDS" section. Note that the SDS and HVA are educational and should be checked against the supplier's SDS before workplace use.

## Running This Skill in Claude

This skill was exported from Perplexity Computer. When a step names a tool Claude does not have, use the closest Claude equivalent:

- `search_web`, `search_vertical` (academic), `fetch_url` — use Claude's web search and web fetch.
- `browser_task` / `use_local_browser` — use Claude in Chrome if it is enabled; otherwise use web search and ask the user to paste content from login-only sites (such as a school library or JSTOR).
- `read` — open the file from the skill folder or the user's upload.
- `share_file` — save the finished file and provide it as a downloadable file.
- Other skills named here (for example `humanize-ai-text`, `sds-bible`, `office/pdf`) — use the matching uploaded skill if installed; otherwise follow the instructions directly with code execution (python-docx, openpyxl, reportlab).
- Workspace paths like `/home/user/workspace/...` — save output to Claude's normal output folder instead.
