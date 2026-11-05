# Testing a skill

## 1. Static (automatic)
`python scripts/validate_skill.py <dir>` - frontmatter, name/description limits, allowed keys, paths that
SKILL.md mentions exist, Python scripts compile, no secrets/absolute user paths/junk files, size, line counts.

## 2. Scripts
For each script: `--help` works; `--check`/dry run works; one real input produces the expected output;
one bad input gives a readable error and non-zero exit.

## 3. Evals (behavior)
`evals/evals.json`:
```json
{"skill": "my-skill",
 "should_trigger": [{"prompt": "...", "expected": ["asks intake once", "creates X.docx", "states test status"]}],
 "should_not_trigger": ["unrelated request 1", "near-miss request 2"]}
```
Run at least 3 should-trigger prompts in a fresh conversation/context with only this skill's text. Check each
expected behavior. Run 2 should-not-trigger prompts and confirm the description does not over-match.

## 4. Fresh-machine test
Run `setup_env.py` in a clean environment (new venv or sandbox) to prove plug-and-play.

## 5. Record
Write results into the skill's README or delivery message: what passed, what was not tested (for example
"not run on a physical calculator").
