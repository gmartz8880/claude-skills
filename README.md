# Gabe's Claude Skills

Custom skills I built for Claude (claude.ai and Claude Code).

| Skill | What it does |
|---|---|
| accounting-questions | Fast answers for accounting homework / McGraw Hill Connect questions |
| ancient-script-translator | Reads and translates hieroglyphics, cuneiform, Latin/Greek inscriptions, and old European handwriting from photos |
| assignment-completion | Works through an assignment prompt or rubric start to finish (MLA/APA/Chicago) |
| evidence-research | Fact-checking and research with claim-level citations |
| humanize-ai-text | Rewrites AI-sounding text to read naturally, outputs a Word doc |
| sds-bible | Generates a full 16-section GHS Safety Data Sheet (Word/PDF) |
| skill-forge | Builds, upgrades, validates, and packages new Claude skills |
| sru-research | Multi-engine academic source research (Google Scholar, JSTOR through your school library if you have it, and web engines) |
| ti-calc-app-builder | Builds TI-84 Plus CE and TI-Nspire calculator apps |
| voice-line | Two-way voice chat with Claude Code over Telegram (needs the Telegram plugin, whisper, piper, ffmpeg) |
| docs-to-skill | Turns a documentation website into a skill: Skill Seekers scrape, then the skill-forge gate (validate, test, package, install); publishes only when the docs license allows. |
| machine-blueprint | Vintage blueprint set + PDF technical manual for any machine or entire vehicle (every trim/option, model numbers, key sheet, electrical schematics, isometric, multi-view), with optional AutoCAD / SolidWorks / Fusion / FreeCAD files. Asks for every name it uses. |
| amazon-market-research | Amazon shopping research: asks what you are buying, your examples, how many more and your must-haves, then builds a colorful Excel comparison (ASIN, dated price, features, link, picture) sorted by price with one positive and one negative outlier |
| advanced-search | Writes sharp web searches with operators (quotes, site:, filetype:, date limits) and a step-by-step fix ladder for weak results |

## Install

**Full step-by-step guide: [INSTALL.md](INSTALL.md)**

- **claude.ai / desktop / mobile:** download the skill zips from [Releases](https://github.com/gmartz8880/claude-skills/releases/latest), then upload each one in Settings → Capabilities → Skills.
- **Claude Code:** copy the skill folders into `~/.claude/skills/`.

## Notes

- Nothing is pre-filled with my details. The first time you use a skill, it asks for your own name, and the school skills also ask for your school, class level and library access. If Claude already knows them from your profile or memory, it asks you to confirm instead.
- sru-research and assignment-completion use JSTOR through your school library if you have it, and skip that step if you don't.
- humanize-ai-text matches your writing style if you give it a short sample. Otherwise it uses a default style.
- I left the reference PDFs out of ancient-script-translator because they're other people's copyrighted papers. `references/README.md` lists what they were. The skill works without them.
