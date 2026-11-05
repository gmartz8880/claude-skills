---
name: skill-forge
description: Creates, upgrades, or converts Claude skills into plug-and-play packages. Asks once, researches, writes SKILL.md and scripts, validates, tests, and packages for Claude and Claude Code.
license: MIT
compatibility: Claude.ai, Claude Desktop, Cowork, Claude Code, Claude API (code execution). Python 3.8+. Windows, macOS, Linux.
metadata:
  version: "1.0.0"
  author: Gabriel Martz
  dependencies: python>=3.8, pyyaml (pip, optional), python-docx (pip, optional), pandoc (winget:JohnMacFarlane.Pandoc, optional)
---

# Skill Forge

Builds skills that let Claude finish a whole job from one request: it asks the right questions once,
then does everything required (installs what is missing, opens apps, runs tools, checks its own work)
carefully, and delivers a result anyone can understand. Every skill this produces must be
**optimized** (small context cost, fast), **compatible** (Claude.ai, Desktop, Cowork, Claude Code, API;
Windows first, macOS/Linux too), and **plug-and-play** (upload the zip or copy the folder; nothing else).

Use for: "make a skill that...", "turn this workflow/prompt/Perplexity skill into a Claude skill",
"improve/fix my skill", "why doesn't my skill trigger", "package my skills".

## Workflow (follow in order, do not skip validation or tests)

### Step 0 - Environment (automatic, no questions)
Run `python scripts/setup_env.py` (add `--for <skill-dir>` once the target skill exists or when upgrading
one). It checks first and installs only what is missing: pyyaml, python-docx, pandoc (winget/brew), and
the target skill's own pip/winget/brew dependencies. Install anything else the build needs the same way
(check -> install -> verify) without asking. If an install fails, use the fallback and say so.

### Step 1 - Classify the request
New skill / upgrade an existing skill (read it fully first) / convert from another format (Perplexity
skill, prompt, Custom GPT, CLAUDE.md, script) / package or install existing skills.

### Step 2 - Intake: one round of questions, then work
Use the built-in question tool (AskUserQuestion in Claude Code / Cowork; the question card in the Claude
apps). Ask only what the request did not already answer, using `references/intake.md`:
the job and the finished output, trigger phrases, inputs, output format, where it will run (default: all),
autonomy level (default: full autonomy inside the safety rules), and any accounts/apps it must use.
Then proceed without further questions unless an answer would change the design.

### Step 3 - Research and verify
Look up current facts the skill depends on (APIs, file formats, app versions, laws/standards), using
official docs first. Record the date checked inside the reference file. Never rely on memory for version
numbers, limits, or commands. Prefer facts the skill can re-check at run time (a version command) over
hard-coded ones.

### Step 4 - Design (write it down before writing files)
Decide with `references/design-guide.md`:
- **Name**: lowercase-hyphen, <= 64 chars, no "claude"/"anthropic", matches the folder.
- **Description**: <= 200 chars (Claude.ai upload limit), what it does + when to use it, key trigger words first.
- **Degrees of freedom**: instructions for judgment work, scripts for anything deterministic or fragile.
- **Progressive disclosure**: SKILL.md = the workflow (< 300 lines ideal, < 500 max); details in
  `references/` (one level deep); runnable code in `scripts/`; starter files in `templates/`/`assets/`.
- **Autonomy plan** from `references/autonomy-playbook.md`: what it does without asking, the one question
  round, the short list of actions that always need the user's OK, and the standard permissions text from
  `references/permissions-and-unattended.md` section 5.
- **Environment plan**: check-then-install for every dependency, offline fallback, Windows commands.

### Step 5 - Build
1. `python scripts/init_skill.py <name> --out <dir>` creates the folder from `templates/SKILL.template.md`
   with a check-then-install `scripts/setup_env.py`, `evals/evals.json`, and a README.
2. Write SKILL.md with the template's sections: purpose, defaults/owner context, numbered workflow
   (environment -> intake -> work -> verify -> deliver), autonomy rules, hard rules, files list.
3. Write scripts per `references/script-patterns.md`: Python standard library first, idempotent,
   `--check` and `--json` flags, clear exit codes, readable errors that say how to fix, no hard-coded
   user paths, no secrets.
4. Write the references and templates the workflow points to. Every path mentioned must exist.

### Step 6 - Validate (must be clean)
`python scripts/validate_skill.py <skill-dir>` (portable profile by default; `--profile claude-code`
allows Claude Code-only fields). Fix every ERROR; fix WARNs or note why they stay.

### Step 7 - Test like a user
Follow `references/testing.md`:
- Run every script with `--help`, `--check`, and one real case.
- Walk through 3 realistic prompts from `evals/evals.json` end to end in a fresh context; confirm the
  skill triggers, asks the intake once, completes, and the output matches the expected behavior.
- 2 prompts that should NOT trigger it. Adjust the description if needed.
- If anything fails, fix and re-run Steps 6-7.

### Step 8 - Package and install
1. `python scripts/permissions_helper.py <skill-dir>` writes `PERMISSIONS-SETUP.md` (read-only: it only
   tells the user how to reduce prompts; it changes nothing).
2. `python scripts/package_skill.py <skill-dir> --out dist --extra <technical-guide.docx>` produces
   `dist/<name>-package.zip` containing the upload-ready `<name>.zip` (folder at the zip root),
   `install-claude-code.ps1` / `.sh`, `INSTALL.md`, `PERMISSIONS-SETUP.md`, and the guide.
   One package per skill; build a multi-skill bundle (`--bundle`) only if the user asks.
If running in Claude Code or Cowork on the user's machine, install it yourself:
`python scripts/install_skill.py dist/<name>/<name>.zip` (copies to `~/.claude/skills`, backs up any old copy).
For the Claude apps, tell the user: Settings (or Customize) > Skills (Capabilities) > Upload skill > choose the zip.

### Step 9 - Deliver
Give: what the skill does, how to trigger it (example prompts), install steps, what was tested and
what was not, and a technical guide (Word .docx when the user prefers Word). After any change to an
existing skill, show the full updated workflow, not just the diff.

## Rules every generated skill must follow
- Asks all its questions in one round with the question tool, offers sensible defaults and "you pick".
- After intake, completes the job end to end without asking permission for routine, reversible steps
  (installing missing packages, creating files, opening apps, running its own scripts).
- Still stops for: spending money, sending/publishing anything to other people, deleting user data,
  credentials (never stored in files), and legal/medical/safety decisions.
- **Never changes Claude's permissions or permission mode, or system security settings, itself** (heavy bias):
  no settings.json edits, no bypass/skip-permission flags or variables, no Claude Local unattended or
  administrator launchers, no UAC/execution-policy/antivirus changes. It tells the user exactly how (see
  `references/permissions-and-unattended.md`, options A-E with undo steps) and keeps working.
- Checks its own work (tests, validators, re-reads output) and reports honestly what was verified.
- Works offline or degrades gracefully; never fails silently.
- Output is written for a non-expert: plain words, numbered steps, what to click.
- Portable frontmatter only (`name`, `description`, `license`, `compatibility`, `metadata`,
  `allowed-tools`) unless the user asks for a Claude Code-only skill.

## Files
- `scripts/init_skill.py` scaffold a new skill
- `scripts/validate_skill.py` spec + portability + quality checks
- `scripts/package_skill.py` upload zips, bundle zip, Claude Code installers
- `scripts/install_skill.py` install a skill zip/folder into Claude Code (personal or project)
- `scripts/setup_env.py` check-then-install build tools and the target skill's dependencies
- `scripts/permissions_helper.py` write PERMISSIONS-SETUP.md (guidance only, never edits settings)
- `references/intake.md` `design-guide.md` `spec-and-compatibility.md` `autonomy-playbook.md`
  `script-patterns.md` `testing.md` `owner-standards.md` `permissions-and-unattended.md`
- `templates/` SKILL.template.md, setup_env.template.py, evals.template.json, README.template.md
