---
name: advanced-search
description: "Write sharp web search queries with operators (quotes, site:, filetype:, OR, -, intitle:, before:/after:). Use before any web search, research, fact-check or source hunt."
license: MIT
compatibility: "Any Claude surface with a web search tool. Operator support depends on the search backend; the skill checks results and falls back to plain wording."
metadata:
  version: "1.0.0"
  based-on: "Google Guide advanced operator cheat sheet (Blachman, Peek, Bergson-Michelson), updated for operators Google has since removed. Operator status checked 2026-11-12."
---

# Advanced Search

Turns a question into search queries that land on the right pages the first time, using
search operators where they help and plain wording where they don't. The goal is fewer,
better searches and answers built on primary sources.

This skill decides **how to write and refine searches**. Whether to search at all, and
how to cite, follows the user's own research rules and any research skill in use
(such as evidence-research). If those conflict with this skill, they win; a direct
instruction from the user in the chat beats both.

## Why this matters

A search engine only sees the words you send. Vague queries return SEO pages and
summaries of summaries; precise ones return the source itself. Operators are how you
tell the engine *where* the words must appear (title, URL, a given site, a PDF) and
*what to leave out*. Used carelessly they also hide good results, so the habit is:
start simple, read what comes back, then tighten.

## Workflow (every search)

1. **Pick the key terms.** The 2-4 words most specific to the question, in the
   vocabulary an expert in that field would use (the formal name of a rule, part,
   condition or process, not a casual description). Put the most important term first.
2. **Lock exact strings in "quotes".** Error messages, model or part numbers, legal or
   standard citations, product names, titles, and any phrase whose wording matters.
3. **Decide the best kind of source** before searching (see
   `references/strategy.md` > Source types). If one domain or domain type is the
   obvious authority, add `site:` for it. Don't add `site:` on the first try when you
   don't know who the authority is.
4. **Add a format filter** (`filetype:pdf` etc.) when the answer is a document:
   manuals, standards, forms, data sheets, reports, papers, slide decks, spreadsheets.
5. **Add a time limit** when the answer can change: the current year, a year range
   (`2023..2026`), or `after:YYYY-MM-DD`.
6. **Run it, then judge the results.** Weak results means: off-topic, too old, only
   low-quality sites (content farms, listicles, AI-spun pages), or missing the exact
   fact needed. If weak, apply one fix from the fix ladder below and search again.
7. **Separate items get separate searches.** For comparisons, lists or multi-part
   questions, run steps 1-6 per item. A combined query returns shallow results for all.
8. **Read before you rely.** Open the actual page for any number, quote, date,
   requirement or instruction. Snippets are for choosing what to open.

Full operator syntax, engine support and removed operators: `references/operators.md`.
Source types, the full fix ladder and worked examples: `references/strategy.md`.

## Core operators (quick card)

| Operator | Does | Example |
|---|---|---|
| `word word` | all words | `solar panel efficiency` |
| `"phrase"` | exact phrase | `"statute of limitations"` |
| `OR` | either term (must be caps) | `laptop OR notebook` |
| `-word` | exclude | `jaguar speed -car` |
| `( )` | group | `(heat OR thermal) stress` |
| `*` | wildcard in quotes | `"the * of the problem"` |
| `#..#` | number range | `camera $300..$600` |
| `site:` | one site / domain type | `site:.gov`, `site:wikipedia.org` |
| `-site:` | drop a site | `-site:pinterest.com` |
| `filetype:` / `ext:` | file type | `filetype:pdf` |
| `intitle:` | word in title | `intitle:review` |
| `inurl:` | word in URL | `inurl:faq` |
| `intext:` | word in body | `intext:"warranty"` |
| `before:` / `after:` | date limit | `after:2025-01-01` |
| `define:` | definition | `define:entropy` |

Syntax that trips people up: no space after the colon (`site:x.org`); `OR` must be
uppercase; `-` touches the word (`-car`); `allintitle:`/`allinurl:`/`allintext:` apply
to every word after them, so put them first and don't mix them with other operators.

Never use removed operators: `cache:` `link:` `info:` `id:` `related:` `~` `+`
`daterange:` `phonebook:` and the old Google Groups/News ones (`author:` `group:`
`insubject:` `source:` `location:`). Use quotes instead of `+`.

## Fix ladder (one change per new search)

1. Off-topic -> quote the main term, or add `intitle:`.
2. Junk sites -> `site:` a primary source, or `-site:` the junk.
3. Too few results -> drop the least important word, or add `(word OR synonym)`.
4. Too old -> add the year, a range, or `after:`.
5. Wrong meaning of a word -> `-` the word that signals the wrong meaning.
6. Operators seem ignored -> rewrite in plain words and name the source in words.
7. The search tool has its own domain filter -> use that instead of `site:`.
8. You already know the exact page -> open it directly instead of searching.

Every new query must differ from all earlier ones; repeating a query wastes a turn.
After three failed fixes on the same item, stop and report what was tried and what is
still missing rather than guessing.

## Rules

- Prefer primary sources (the body that wrote the rule, made the product, ran the
  study, published the data). Use a secondary source only when no primary one is
  findable, and say so.
- Check dates; flag anything that may be outdated.
- When sources disagree, search specifically to settle it; if it can't be settled,
  show both sides and say it's unresolved.
- Never invent a source, URL, quote or result. If it wasn't found, say so.
- Don't narrate the query-building to the user; just search well. Mention operators
  only if the user asks how you searched.

## Files

- `references/operators.md` - full syntax, per-engine support, removed operators
- `references/strategy.md` - source types, query patterns, worked examples
- `evals/evals.json` - test prompts
