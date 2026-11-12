# Amazon Market Research (amazon-market-research)

What it does: researches anything you want to buy on Amazon. Asks what you are shopping for, any examples you already found, how many more to find and your must-have features, then builds a colorful Excel comparison (ASIN, dated price, list price, features, Amazon link, picture) sorted by price then features, with one positive and one negative outlier.

## Use it
Ask Claude in plain words, for example: "I'm shopping for a robot vacuum under $400 with a self-emptying base - here are two I like, find me 5 more".

## Install
- Claude app / Cowork: Settings > Capabilities (or Customize) > Skills > Upload `amazon-market-research.zip`.
- Claude Code: run `install-claude-code.ps1` (Windows) or `install-claude-code.sh`, or copy the folder to `~/.claude/skills/`.

## Tested
validate_skill.py PASS (portable). build_sheet.py tested with --check, --example, bad input, and a real 11-product research file (rows sorted by price then features, outlier section, hyperlinks, IMAGE() pictures, Comfortaa font). Pictures embed for real only when image files can be downloaded (e.g. on your own computer).
