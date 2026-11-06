# Enhancing a scraped docs skill (done by the running Claude session)

Skill Seekers was run with `--enhance-level 0`, so the raw folder has a generic SKILL.md and
categorized reference files. You do the enhancement here, in this session. Do not run
`skill-seekers enhance` (its LOCAL mode starts `claude --dangerously-skip-permissions`).

## 1. Read before writing
- Read `references/index.md` and skim the headings of every reference file (`grep -n "^#" references/*.md`).
- Read 2-3 sections fully to learn the library's core concepts, main API, and install command.

## 2. Rewrite SKILL.md (keep it under 300 lines)
Frontmatter (leave `license`, `compatibility` and `metadata` from `forge_gate.py fix` in place):
- `name`: as produced, e.g. `click-docs`.
- `description`: <= 200 characters, third person, trigger words first. Pattern:
  "<Library> reference from the official docs: <3-5 core topics>. Use when writing, debugging or
  answering questions about <library> code." No angle brackets.

Body, in this order:
1. One paragraph: what the library is, which version the docs cover, and the scrape date.
2. `## How to use (workflow)` with numbered steps, for example:
   1. Find the topic in the Reference map below.
   2. Open only that reference file and search it for the API or term.
   3. Answer or write code from what the docs say; quote the section heading you used.
   4. If the docs don't cover it, say so instead of guessing.
3. `## Quick reference`: 5-15 of the most-used commands, APIs or patterns, each with a short, correct
   code block taken from the docs. Delete the raw "Pattern N:" blocks Skill Seekers generated.
4. `## Reference map`: a table of every file in `references/` with one line on what it covers.
5. `## Hard rules`: answer from the references; name the docs version; never invent APIs.

## 3. Reference files
- Split a reference file over ~1,500 lines by topic, at its `##` headings, into files named by topic,
  e.g. `references/commands.md`. Then update the Reference map.
- `forge_gate.py fix` adds a table of contents to any file over 100 lines; rerun it after splitting.
- Remove navigation junk (repeated menus, "Edit this page", cookie text) if it was captured.

## 4. references/SOURCE.md (required)
```
# Source
- Docs URL: <url>
- Scraped: <YYYY-MM-DD> with Skill Seekers <version>, preset <preset>, max pages <n>, <pages> pages kept
- Docs license: <license found, with the page or file where you found it, or "not stated">
- Redistributable: yes / no / unclear
```
Find the license on the docs site footer, its "License" page, or the project's GitHub repo LICENSE
file (docs in a repo usually share its license). Record exactly what you found.

## 5. evals/evals.json
Replace every TODO: 3 realistic questions this documentation answers (should trigger) and 2 that
should not: one unrelated, one near-miss (a different library in the same field).
