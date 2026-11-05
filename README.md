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
| sru-research | Multi-engine academic source research (built around Slippery Rock University library access) |
| ti-calc-app-builder | Builds TI-84 Plus CE and TI-Nspire calculator apps |
| voice-line | Two-way voice chat with Claude Code over Telegram (needs the Telegram plugin, whisper, piper, ffmpeg) |

## Install

**claude.ai:** zip a skill folder (the folder itself at the zip root), then go to Settings → Capabilities → Skills → Upload skill.

**Claude Code:** copy the skill folder into `~/.claude/skills/`:

```bash
git clone https://github.com/gmartz8880/claude-skills.git
cp -r claude-skills/sds-bible ~/.claude/skills/
```

## Notes

- A few skills are tuned to me: they put my name on documents ("Prepared by", author lines) or rename "Gary Martz" to "Gabriel Martz". Search the SKILL.md for "Martz" and swap in your own name.
- sru-research expects Slippery Rock University library (JSTOR proxy) access. Without it, that step falls back to the other search engines.
- I left the reference PDFs out of ancient-script-translator because they're other people's copyrighted papers. `references/README.md` lists what they were. The skill works without them.
