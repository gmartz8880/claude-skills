# Design guide: writing skills that trigger, run fast, and finish the job

## 1. Name and description (decide triggering)
- Name: `lowercase-with-hyphens`, <= 64 chars, letters/digits/hyphens, no leading/trailing/double hyphen,
  must not contain "claude" or "anthropic", same as the folder name. Prefer a noun phrase or gerund
  (`sds-generator`, `processing-pdfs`).
- Description: <= 200 characters for Claude.ai uploads (spec max 1024). Third person. Pattern:
  "<Does X> for <domain>. <Key steps/outputs>." Put the most likely trigger words first; name the file
  types, apps, and nouns users will actually say. No angle brackets.
- Claude Code-only skills can add `when_to_use` (extra trigger phrases; description + when_to_use <= 1,536 chars).

## 2. Body structure (SKILL.md)
1. One-paragraph purpose: what "done" looks like.
2. Defaults / owner context (known hardware, preferences, accounts).
3. Numbered workflow: Step 0 environment (check-then-install) -> Step 1 intake (one round) -> work steps ->
   verify -> deliver. Each step: what to do, the exact script/command, what "good" looks like.
4. Autonomy rules (what not to ask about; the always-ask list).
5. Hard rules (quality, safety, honesty).
6. Files list (every bundled file with one line each).

## 3. Keep context small (optimization)
- SKILL.md < 300 lines ideal, < 500 max. Only the workflow lives here.
- Details go to `references/*.md` one level deep, loaded only when a step needs them. Name them by topic.
- Long references (> 100 lines) start with a short table of contents.
- Deterministic or fragile work -> scripts (they run without being read into context; only output costs tokens).
- No duplicated content between SKILL.md and references. No history/changelog in SKILL.md.
- Tables beat paragraphs for lookups; examples beat abstract rules.

## 4. Degrees of freedom
| Task type | Give Claude | Example |
|---|---|---|
| Judgment, writing, research | principles + checklist | report tone, what to research |
| Preferred pattern with variation | template + rules | document layout, code skeleton |
| Fragile / exact | a script, "run it, do not rewrite it" | file format conversion, packaging |

## 5. Plug-and-play rules
- Zero setup by the user beyond uploading/copying: the skill installs what it needs on first run.
- Relative paths only (scripts/..., references/...); forward slashes in docs; scripts use `os.path`/`pathlib`.
- Python standard library first; when a package is needed, check -> install -> verify -> fall back.
- Windows-first commands with macOS/Linux equivalents (`python` vs `python3`, PowerShell vs bash).
- Works without network when possible; says clearly what needs network.
- No secrets in files; credentials come from the platform's connector or an environment variable.
- Date-stamp time-sensitive facts ("verified Nov 2026") and tell Claude to re-check if older than ~6 months.

## 6. Make it understandable
Every deliverable the skill produces must explain itself to a non-expert: plain words, numbered steps,
what to click, what to expect, what was and was not verified, and how to fix common problems.
