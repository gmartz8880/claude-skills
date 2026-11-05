---
name: {{name}}
description: {{description}}
license: MIT
compatibility: Claude.ai, Claude Desktop, Cowork, Claude Code, Claude API (code execution). Python 3.8+. Windows, macOS, Linux.
metadata:
  version: "1.0.0"
  author: TODO
  dependencies: python>=3.8
---

# {{title}}

TODO one paragraph: what this skill finishes for the user and what "done" looks like (the files or answer delivered).

## Defaults
- TODO known preferences (output format, style, accounts, hardware). Use these unless the user says otherwise.

## Workflow (follow in order)

### Step 0 - Environment (automatic)
Run `python scripts/setup_env.py --json`. It checks first and installs only what is missing. Do not ask
before running it. If something cannot be installed, use the fallback in the step that needs it and say so.

### Step 1 - Intake (one round)
Ask everything you need in one round with the question tool (multiple choice where possible, always a
"you pick" default). Skip what the request already answered. Then work without more questions unless
an answer is truly ambiguous.
TODO list the questions.

### Step 2 - TODO main work
TODO exact actions, scripts to run, what good output looks like.

### Step 3 - Verify
TODO checks: run tests/validators, re-open every output file, compare against the request checklist.

### Step 4 - Deliver
Give the files plus a short plain-language summary: what was done, how to use it, what was verified and
what was not.

## Autonomy
Do the whole job without asking about routine steps (installing missing packages, creating files,
running this skill's scripts, opening the apps it needs). Ask once, in one batch, before: spending money,
sending or publishing anything to other people, deleting user data, or entering credentials. Do not
change Claude's permissions, permission mode, or system security settings yourself. If repeated
permission prompts slow the job, tell the user to see PERMISSIONS-SETUP.md (auto mode or the allow
rules listed there) and keep working.

## Hard rules
- Never invent facts, commands, or file formats; check official docs and date-stamp what you rely on.
- Never claim something was tested, sent, or installed unless it was.
- Write for a non-expert: plain words, numbered steps, what to click.

## Files
- `scripts/setup_env.py` check-then-install environment
- TODO list every bundled file
