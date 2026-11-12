# Search strategy

## Contents
1. Source types (who is the authority?)
2. Query patterns by goal
3. Fix ladder, explained
4. Worked examples
5. When to stop

## 1. Source types (who is the authority?)

Work out who *created* the information before searching, then aim at them. These are
patterns to reason from, not a fixed list of sites: pick the authority that fits the
actual question.

| Kind of question | Primary source to aim for | Typical query shape |
|---|---|---|
| A law, regulation or government rule | the agency or legislature that issued it; the official code | citation in quotes + `site:` the agency, or `site:.gov` |
| A technical standard | the standards body | standard number in quotes + body name |
| Product specs, manuals, recalls | the manufacturer; the regulator that handles recalls | model number in quotes + `filetype:pdf` |
| Scientific or medical findings | the paper itself; journals; public health agencies | key terms + `filetype:pdf`, scholar search, `site:.edu`/`.gov` |
| Statistics and data | the agency or organization that collected it | dataset name + `filetype:csv` or `xlsx` |
| Software errors and how-tos | official docs; the project's issue tracker; Q&A sites | error text in quotes + `site:` the docs or tracker |
| A company's own facts | the company's site, filings, press releases | company name + `inurl:investor` / `inurl:press` |
| Real-world experience, opinions, workarounds | forums and community sites | topic + `site:` the community |
| News and recent events | established outlets, the original announcement | topic + date limit; then find the original statement |
| A definition or concept | dictionaries, textbooks, encyclopedias | `define:` or term + "definition" |

Domain endings help when you don't know the exact site: `.gov` (governments, US mostly;
other countries use forms like `.gov.uk`, `.gc.ca`), `.edu` (universities), `.org`
(nonprofits; mixed quality), `.mil`, `.int` (international bodies).

## 2. Query patterns by goal

- **Find a specific document:** `intitle:"exact title"` or `"title" filetype:pdf`
- **Find the official version:** `"name or citation" site:.gov` (or the issuing body)
- **Find recent changes:** `topic (update OR change OR amendment) after:YYYY-MM-DD`
- **Find a fix for an error:** `"exact error text"` + product/version, then add a docs or
  tracker `site:` if results are noisy
- **Find data:** `topic statistics filetype:xlsx OR filetype:csv`
- **Find alternatives to X:** `"X" alternatives OR competitors OR vs`
- **Find criticism or the other side:** `topic (criticism OR problems OR limitations)`
- **Find a definition from experts:** `intitle:glossary topic` or `define:term`
- **Settle a disagreement:** quote the specific disputed claim and search for it with
  the primary source's `site:`

## 3. Fix ladder, explained

Change one thing per new search so you know what helped.

1. **Off-topic results.** The engine matched your words loosely. Quote the core phrase or
   require it in the title with `intitle:`.
2. **Low-quality sites dominate.** Point at a primary source with `site:`, or remove the
   offenders with `-site:`.
3. **Too few results.** You over-constrained. Drop the least essential word or operator,
   or widen a term with `(word OR synonym OR abbreviation)`.
4. **Results are stale.** Add the current year, a range, or `after:`.
5. **A word has two meanings.** Exclude a word tied to the wrong one
   (`python -snake`, `mercury -planet`).
6. **Operators had no effect.** The backend may not support them. Rewrite as a plain
   sentence that names the source and the year.
7. **The tool offers a domain filter.** Use it instead of `site:`; it's more reliable.
8. **You know the page already.** Fetch it directly.

## 4. Worked examples (general, to reason from)

**A regulation's exact requirement**
- Weak: `rules for ladders at work`
- Better: `"ladder" requirements site:.gov`
- Best once you know the citation: `"<citation number>" site:<issuing agency>`, then open
  the official text and quote it.

**A product's spec**
- Weak: `how much can a <product> hold`
- Better: `"<model number>" specifications`
- Best: `"<model number>" (manual OR "spec sheet") filetype:pdf` -> read the
  manufacturer's PDF.

**A software error**
- Weak: `my program crashes on start`
- Better: `"<exact error line>"`
- Best: `"<exact error line>" <program> <version> site:<project tracker or docs>`

**A recent development**
- Weak: `new rules for drones`
- Better: `drone regulations 2026`
- Best: `drone (rule OR regulation) (final OR proposed) after:2026-01-01`, then find the
  agency's own announcement.

**A study's findings**
- Weak: `does coffee cause heart problems`
- Better: `coffee consumption cardiovascular risk meta-analysis`
- Best: `coffee "cardiovascular" "meta-analysis" filetype:pdf after:2022-01-01`, then read
  the paper's abstract and results, not a news write-up of it.

**Comparison of two things**
- Don't: `A vs B vs C features prices`
- Do: three searches, one per item, each targeted at its own primary source; then a
  fourth if needed for an independent head-to-head review.

## 5. When to stop

Stop searching an item when every part of the answer rests on a page you actually read.
If three fixes in a row fail, stop and report: what you searched, what you found, and
what is still unknown. A clear "not found" is better than a guess.
