---
name: docs-to-skill
description: "Converts a documentation website or docs URL into an installable skill: scrapes it with Skill Seekers, then makes it pass skill-forge validation, tests, packaging and install."
license: MIT
compatibility: Claude Code and Cowork on a computer with Python 3.10+ and internet. Windows first; macOS and Linux work too. Needs the skill-forge skill installed.
metadata:
  version: "1.0.0"
  dependencies: "skill-seekers (installed by scripts/setup_env.py), skill-forge skill"
---

# Docs to Skill

Turns a documentation website (for example `https://click.palletsprojects.com/`) into a finished
skill that has passed the skill-forge quality gate. Done means:
- skill-forge's validator reports 0 errors and 0 warnings
- the evals are written and walked through
- the skill is packaged as an upload-ready zip and installed into `~/.claude/skills`
- the user gets a short report saying what was verified

Load the skill-forge skill when this one starts. Its rules (one intake round, check-then-install,
honest testing, no permission changes) apply to every step here.

## Defaults
- Output folder: `~/ClaudeMove/doc-skills/<name>/`
- Skill name: derived from the site, ending in `-docs` (e.g. `click-docs`), never containing "claude"
  or "anthropic"
- Depth: preset `standard`, at most 200 pages
- Enhancement: done by this session, at no API cost. Never use Skill Seekers' own enhancement or upload
  commands.

## Workflow (follow in order)

### Step 0 - Environment (automatic)
Run `python scripts/setup_env.py --json`. It checks first and installs Skill Seekers only if missing.
On Windows inside the Claude desktop app, it installs through a one-time scheduled task, because the
app redirects AppData installs into private storage. Then it confirms skill-forge is present. If
`ready` is false, report the failing item and stop.

### Step 1 - Intake (one round)
With the question tool, ask only what the request did not already answer:
1. Docs URL (required). If the user gave a site name but no link, find the official docs URL yourself
   and confirm it in this same round.
2. Skill name (default: derived from the site).
3. Depth: quick (up to 50 pages), standard (up to 200, default), or full (comprehensive, up to 1000).
Do not ask about anything else; use the Defaults.

### Step 2 - Scrape
Run `python scripts/convert.py <url> --name <name> --preset <preset> --max-pages <n> --json`. A large
site can take 10-60 minutes, so run it in the background and wait for it to finish. Good result:
`exit` is 0, `reference_files` is at least 1, and `enhancement_ran` is false. Otherwise, read the log
it names, fix the cause (wrong URL, site blocks scrapers, network), and rerun once.

### Step 3 - Enhance (this session does the writing)
1. Run `python scripts/forge_gate.py fix <skill_dir> --json`. It makes the mechanical fixes: name and
   folder, frontmatter, empty folders, tables of contents, and an evals skeleton.
2. Follow `references/enhance-guide.md`. It covers:
   - rewriting the description and SKILL.md with a numbered workflow, quick reference and reference
     map
   - splitting oversized reference files
   - writing the generated skill's `SOURCE.md` (in its references folder), including the docs license
   - filling in `evals/evals.json`
3. Run `fix` again after splitting files.

### Step 4 - skill-forge gate (must pass)
1. Run `python scripts/forge_gate.py check <skill_dir> --json`. It runs skill-forge's
   `validate_skill.py` plus extra checks.
2. Fix every item in `errors`, `warns` and `extra`, then rerun until `pass` is true. Don't skip a
   warning; skill-forge treats them as must-fix unless there's a stated reason.
3. Test it like a user, following skill-forge's testing guide (`testing.md` in skill-forge's references folder). Walk through the 3
   should-trigger prompts and answer each one from the new skill's references. Confirm the 2
   should-not-trigger prompts would not match the description.

### Step 5 - Package and install
Run `python scripts/forge_gate.py ship <skill_dir> --json`. It calls skill-forge's
`permissions_helper.py`, `package_skill.py` and `install_skill.py`, writing the zip to
`<output folder>/dist/<name>/`. Good result: `installed` is true.

### Step 6 - Publish (only when the docs may be shared)
Read `Redistributable` in the generated skill's `SOURCE.md`.
- **yes** (MIT, BSD, Apache, CC-BY or similar): publish with skill-forge Step 10:
  `python <skill-forge>/scripts/publish_to_github.py <skill_dir> --summary "..." --setup "Nothing extra"`.
- **no or unclear:** do not publish. The docs are someone else's content. Say so in the report; the
  skill stays installed locally.

### Step 7 - Deliver
Report in plain words:
- the skill name and example prompts that will use it
- where the zip is (the Claude app upload steps are in the package's INSTALL.md)
- pages scraped, and the gate results (errors and warnings, which should both be 0)
- which eval prompts were walked through
- the license found and whether the skill was published
- anything not verified

## Autonomy
Do the whole job without asking about routine steps (installing missing packages, creating files,
running this skill's scripts, opening the apps it needs). Do not change Claude's permissions,
permission mode, or system security settings yourself. If repeated permission prompts slow the job,
tell the user to see PERMISSIONS-SETUP.md (auto mode or the allow rules listed there) and keep working.

## Hard rules
- Never run `skill-seekers enhance`, `install`, `upload` or `package --upload`, and never pass an API
  key. They add permission bypass flags or paid API use.
- Never publish documentation whose license does not allow redistribution.
- Never claim the gate passed unless `forge_gate.py check` printed `"pass": true` in this session.
- Write for a non-expert: plain words, numbered steps, what to click.

## Files
- `scripts/setup_env.py` - check-then-install Skill Seekers; finds skill-forge
- `scripts/convert.py` - scrapes the docs site with Skill Seekers (no AI enhancement)
- `scripts/forge_gate.py` - fix, check and ship through skill-forge's own scripts
- `references/enhance-guide.md` - how this session writes the generated SKILL.md, SOURCE.md and evals
- `evals/evals.json` - trigger tests for this skill
