# advanced-search

Makes Claude write better web searches: exact phrases, site and file-type limits, date
limits, exclusions, and a step-by-step way to fix weak results. Based on the Google Guide
advanced operator cheat sheet, updated to drop operators Google has removed.

## Use
It loads by itself whenever Claude searches the web. You can also ask directly:
- "search for the official text of ..."
- "find the PDF manual for ..."
- "look up the fix for this error: ..."

## Install
- **Claude apps:** Settings > Capabilities > Skills > Upload skill > choose `advanced-search.zip`.
- **Claude Code:** copy the `advanced-search` folder into `~/.claude/skills/`.

No extra software needed. How well operators work depends on the search tool; the skill
checks results and falls back to plain wording when an operator is ignored.

## Files
- `SKILL.md` workflow, operator quick card, fix ladder
- `references/operators.md` full syntax, removed operators, backend support
- `references/strategy.md` source types, query patterns, worked examples
