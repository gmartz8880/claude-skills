# Sourcing Amazon data when Amazon blocks tools (checked 2026-11-12)

Amazon pages and a.co short links refuse automated fetchers (robots disallow, and a browser shows
"Access restricted ... unauthorized AI agent"). Do not click past that page. Use these routes instead.

## 1. Resolve a short link or a product name to an ASIN
- Ask the user to paste the ASIN (Product information section) or title - fastest and certain.
- Web search the title or model number; Amazon result URLs contain `/dp/<ASIN>` or `/clp/<ASIN>`.
- In a browser tool, DuckDuckGo HTML search works: `https://html.duckduckgo.com/html/?q=site%3Aamazon.com+<words>`
  and read `.result__url` (shows `www.amazon.com/clp/<ASIN>`).
- Reseller mirrors list the ASIN in a spec table: desertcart, manuals.plus/asin/<ASIN>, fado.vn.

## 2. Price (always with a date)
- camelcamelcamel product page: `https://camelcamelcamel.com/product/<ASIN>` - "Amazon" (sold by Amazon),
  "3rd Party New", dates for each. Plain fetch tools are refused; a browser tool works, ~10 s apart
  (faster gets HTTP 429). Its search page is behind a bot check - use product pages only.
- Web search `camelcamelcamel <exact product title>` often returns the page text with prices.
- Deal posts that quote the Amazon price (The Inventory, dealnews, slickdeals) - note their date.
- "-" in Current means not available new right now; mark VERIFY or drop it.

## 3. Specs
Maker spec sheets first, then Best Buy / Lowe's / Home Depot / AJ Madison spec tables, then the Amazon
title via search snippets. Watch for marketing numbers vs rated specs (e.g. input vs output power, peak vs rated battery life); use the rated figure.

## 4. Pictures
- Image IDs (`https://m.media-amazon.com/images/I/<id>.jpg`) appear on camelcamelcamel pages (img tags),
  desertcart `.md` pages, and search snippets. Append `._AC_SL300_` before `.jpg` for 300 px.
- The cloud sandbox usually cannot download from Amazon's image host. If the user's computer is
  connected (device shell or browser), download there and embed with `image_path`; otherwise
  `build_sheet.py` writes Excel 365 `IMAGE()` formulas that load when the file is opened.

## 5. Honesty checks
- Same model, different color or listing = separate row only if it has its own ASIN; say so.
- If fewer distinct products qualify than requested, say how many really exist instead of padding with
  ones that break a rule.
