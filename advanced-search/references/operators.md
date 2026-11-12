# Search operator reference

Status checked 2026-11-12 against current operator guides. Base list from the Google Guide
cheat sheet (2012), with removed operators moved to their own section and `before:`/`after:`
(added 2019) included.

## Contents
1. Syntax rules
2. Working operators
3. Unreliable operators
4. Removed operators (do not use)
5. Support across search backends
6. Combining operators

## 1. Syntax rules

- No space between an operator and its value: `site:example.org`, not `site: example.org`.
- `OR` must be uppercase. Lowercase `or` is just a word. `|` works the same as `OR`.
- The minus sign touches the word: `-forum`, not `- forum`.
- Use straight double quotes `"` in matched pairs.
- `#..#` has no spaces: `2018..2022`, `$50..$100`.
- A single `in...:` operator (`intitle:`, `inurl:`, `intext:`, `inanchor:`) applies only to
  the one word or quoted phrase right after it.
- An `allin...:` operator (`allintitle:`, `allinurl:`, `allintext:`, `allinanchor:`) applies to
  every word after it. Put it first and don't combine it with other operators.
- Dates for `before:`/`after:` are `YYYY-MM-DD`; `YYYY` and `YYYY-MM` usually work too.
  They filter by when the engine indexed the page, which is close to but not always the
  publication date.

## 2. Working operators

| Operator | Meaning | Example |
|---|---|---|
| `a b` | all words must appear | `biking Italy` |
| `"..."` | exact phrase, no variants | `"I have a dream"` |
| `OR`, `\|` | either term | `recycle steel OR iron` |
| `-term` | exclude a word | `salsa -dance` |
| `-site:` | exclude a site | `recipes -site:pinterest.com` |
| `( )` | group terms | `(teacher OR educator) salary survey` |
| `*` | wildcard (inside quotes) | `"a * saved is a * earned"` |
| `#..#` | number range | `"world cup" 1990..2002` |
| `site:` | one site, subdomain, path, or domain ending | `site:nasa.gov`, `site:.edu`, `site:.org` |
| `filetype:`, `ext:` | file type | `annual report filetype:pdf` |
| `intitle:` | term in title | `budget intitle:template` |
| `allintitle:` | all terms in title | `allintitle: beginner woodworking guide` |
| `inurl:` | term in URL | `inurl:careers` |
| `allinurl:` | all terms in URL | `allinurl: pez faq` |
| `intext:` | term in body | `intext:"shipping policy"` |
| `allintext:` | all terms in body | `allintext: ingredients cilantro chicken lime` |
| `before:` / `after:` | date limit | `"heat pump" rebate after:2025-06-01` |
| `define:` | definitions | `define:kerning` |
| math / units | calculator, conversions | `45% of 39`, `300 euros in USD`, `31 in hex` |

Common `filetype:` values: `pdf`, `doc`/`docx`, `xls`/`xlsx`, `ppt`/`pptx`, `csv`, `txt`.

## 3. Unreliable operators (work sometimes; don't depend on them)

`inanchor:` / `allinanchor:` (terms in link text pointing at a page), `AROUND(n)`
(words within n words of each other), `related:` (returns little or nothing now).
If you use one and get nothing, drop it rather than concluding nothing exists.

## 4. Removed operators (do not use)

| Operator | Was for | Removed | Use instead |
|---|---|---|---|
| `cache:` | cached copy | 2024 | an archive service, or fetch the page |
| `related:` | similar sites | 2023 (unreliable) | search the topic plus "alternatives" |
| `link:` | pages linking to a URL | 2017 | search the URL in quotes |
| `info:` / `id:` | page info | 2017 | fetch the page |
| `+term` | force exact word | 2011 | `"term"` |
| `~term` | synonyms | 2013 | `(term OR synonym)` |
| `daterange:` | Julian date range | deprecated | `before:` / `after:` |
| `phonebook:` | phone numbers | 2010 | none |
| `book`, `movie:`, `stocks:`, `weather` | special result boxes | unreliable | plain words |
| `author:`, `group:`, `insubject:` | old Google Groups | gone | `site:` the forum |
| `source:`, `location:` | old Google News | unreliable | `site:` the outlet, add the place as a word |

## 5. Support across search backends

The search tool Claude uses may not be Google. Roughly:
- Works almost everywhere: `"quotes"`, `site:`, `OR`, `-exclude`.
- Usually works: `filetype:`, `intitle:`, `inurl:`.
- Often ignored outside Google: `before:`/`after:`, `#..#`, `allin...:`, `*`, `AROUND()`.
- Many AI search tools accept a domain filter setting; prefer it over `site:` when offered.

Check the first results. If an operator plainly had no effect (results ignore the site,
file type or date), rewrite in plain words ("2025 report from the World Bank on ...").

## 6. Combining operators

Operators stack with AND logic. Order doesn't matter except for `allin...:`.

- `"phrase" site:.gov filetype:pdf` -> official PDF containing an exact phrase
- `intitle:"user manual" "model X100" filetype:pdf` -> a specific manual
- `(recall OR "service bulletin") "model X100" after:2024-01-01` -> recent notices
- `topic -site:youtube.com -site:pinterest.com` -> strip video and image farms
- `"exact error text" site:github.com OR site:stackoverflow.com` -> code fixes
