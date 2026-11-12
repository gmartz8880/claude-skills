---
name: amazon-market-research
description: Amazon shopping research - compare products, find more like ones you found, check must-have features, build a styled Excel sheet with prices, ASINs, links, pictures. Use for any "what should I buy".
license: MIT
compatibility: Claude.ai, Claude Desktop, Cowork, Claude Code, Claude API (code execution). Python 3.8+. Windows, macOS, Linux.
metadata:
  version: "1.0.0"
  author: Gabe Martz
  dependencies: python>=3.8, openpyxl
---

# Amazon Market Research

Turns "I'm shopping for X" into a finished, colorful Excel comparison of Amazon listings: the user's own
picks plus N new ones that meet every must-have feature, each with ASIN, listing price (dated), list price,
features, Amazon link and picture, sorted by price then by features, plus one positive and one negative
outlier. Done = the .xlsx delivered and a short plain-language verdict (best value, what fails and why).

## Defaults
- Amazon US only. Every row has its 10-character ASIN and an `https://www.amazon.com/dp/<ASIN>` link.
- Font Comfortaa (fall back silently in the file if the viewer lacks it; mention it once).
- New finds: 5. Outliers: 1 positive (clearly better, may break a rule such as budget) and 1 negative
  (a tempting option that is worse value or fails a must-have).
- Sort: listing price low to high, then feature count high to low. Unknown prices sort last.

## Workflow (follow in order)

### Step 0 - Environment (automatic)
Run `python scripts/setup_env.py --json` (installs openpyxl if missing). Do not ask first.

### Step 1 - Intake (one round, question tool)
Ask only what the request did not already answer, all at once:
1. **What are you researching?** (product type; budget if not stated)
2. **Already found some?** Paste links, ASINs or names. (Option: "None yet")
3. **How many more should I find?** (3 / 5 (default) / 10 / you pick)
4. **Must-have features** - list them, e.g. "1000W+, air fry, under $200". Turn each into a pass/fail
   check with a number where possible. Ask the user to confirm the list if it is vague.
Then work to the end without more questions. If the user is away or this is unattended, use the defaults
and state them at the top of the Summary sheet.

### Step 2 - Identify the user's examples
Short links (a.co, amzn.to) and Amazon pages usually block automated tools. Resolve them per
`references/sourcing.md` (ask once for the ASIN or title if every route fails; never bypass Amazon's
"access restricted" page). Record each one's real specs - the user's own picks often fail a must-have,
and saying so is the most valuable thing this skill does.

### Step 3 - Find candidates and verify every must-have
Follow `references/sourcing.md`: ASINs from search results, price from an Amazon price tracker with its
date, specs from the maker or a big retailer's spec sheet. A row only gets "YES" when every must-have is
backed by a source. Price unknown -> "VERIFY". Fails a rule -> "NO" and say which rule in Notes.
Count distinct models honestly: color variants and second listings of the same model are fine as rows
(they have their own ASIN and price) but say so in Notes and in the Summary.

### Step 4 - Build the workbook
Write `research.json` (format: `python scripts/build_sheet.py --example`), then:
`python scripts/build_sheet.py research.json -o "<Topic>_Amazon_Research.xlsx" --json`
- Groups: `user`, `new`, `outlier_positive`, `outlier_negative`.
- `spec_columns`: one column per measurable must-have (e.g. Watts, Capacity).
- Pictures: if images could be downloaded (see sourcing), pass `image_path` to embed real pictures;
  otherwise the sheet uses Excel 365 `IMAGE()` from `image_url` or the ASIN, with an Amazon link fallback.
- Summary rows: Best value, Most features, What failed and why, Market reality, Outliers, How prices were checked.
- Sources sheet: every URL a price or spec came from.

### Step 5 - Verify
Re-open the file (openpyxl or render to PDF) and check: row order, every ASIN is 10 characters, every link
works as `amazon.com/dp/<ASIN>`, no "YES" row breaks a rule, prices show their dates, outliers are in
their own section. Do not run LibreOffice recalc on this file: it cannot evaluate IMAGE() and would bake
in errors; the file is set to recalculate when Excel opens it.

### Step 6 - Deliver
Send the .xlsx. In 4-6 lines: best pick and why, which of the user's picks fail and why, anything left
to verify (unknown prices), and that prices change - confirm at checkout.

## Autonomy
Do everything without asking about routine steps (installs, files, searches, scripts). Never buy, add to
cart, sign in, post reviews, or contact sellers. Do not change Claude's permissions or system settings.

## Hard rules
- Never invent a price, ASIN, spec or image URL. Unknown stays "Check listing" / "VERIFY".
- Every price carries its source and date; say "as of", never "current", unless checked today.
- Respect site blocks: if Amazon says automated access is restricted, stop using it.

## Files
- `scripts/setup_env.py` check-then-install environment
- `scripts/build_sheet.py` builds the styled workbook from research.json (`--example`, `--check`, `--json`)
- `references/sourcing.md` where to get ASINs, prices, specs and pictures when Amazon blocks tools
- `evals/` test cases
