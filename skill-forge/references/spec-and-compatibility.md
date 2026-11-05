# Spec and compatibility (verified November 2026)

Sources: Claude Code skills docs (code.claude.com/docs/en/skills), Claude Help Center "How to create
custom skills", Agent Skills spec (agentskills.io). Re-check if this file is more than ~6 months old.

## Portable profile (use by default)
Claude.ai uploads, the Skills API, and Anthropic's `package_skill.py` accept ONLY these frontmatter keys:
`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
Any other key -> upload fails with "unexpected key". Put extra data inside `metadata:` (free-form map,
e.g. `version`, `author`, `dependencies`).

| Field | Rule |
|---|---|
| name | required for uploads; <= 64 chars; lowercase letters, digits, hyphens; matches folder; no "claude"/"anthropic" |
| description | required; Claude.ai upload limit 200 chars (spec 1024); no `<` `>` |
| license | optional short string |
| compatibility | optional; environment requirements (spec <= 500 chars) |
| metadata | optional map; `dependencies` is read by Claude.ai as the package list |
| allowed-tools | optional; Claude Code grants these tools without prompting during the skill's turn; ignored elsewhere |

## Claude Code-only fields (profile `claude-code`)
`when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation` (manual `/name` only),
`user-invocable` (false = hidden from `/` menu), `disallowed-tools`, `model`, `effort`
(low|medium|high|xhigh|max), `context: fork` + `agent` + `background`, `hooks`, `paths` (globs that
auto-activate), `shell` (bash|powershell).
Body features: `$ARGUMENTS`, `$1`, named `$arg`; dynamic context with `` !`command` `` (runs before the
skill text is shown to Claude); fenced ```` ```! ```` blocks.

## Where skills live
| Surface | How to install | Notes |
|---|---|---|
| Claude.ai / Desktop chat | Settings > Capabilities/Customize > Skills > Upload (zip) | needs code execution on; per user |
| Cowork (Desktop) | same upload as Claude apps | `~/.claude/skills` is NOT loaded in Cowork or cloud sessions |
| Claude Code personal | `~/.claude/skills/<name>/SKILL.md` | all projects on that machine |
| Claude Code project | `<repo>/.claude/skills/<name>/SKILL.md` | commit to share with a team |
| Plugins | `<plugin>/skills/<name>/` | namespaced `/plugin:name` |
| Claude API | Skills API upload / container skills | no network installs at run time: bundle or avoid packages |

## Zip layout (uploads)
```
my-skill.zip
└── my-skill/
    ├── SKILL.md
    ├── scripts/ references/ templates/ assets/
```
Folder at the zip root, folder name = `name`. No `__pycache__`, `.DS_Store`, `.git`, secrets.

## Runtime differences to design for
| Capability | Claude.ai / Desktop | Cowork | Claude Code | API |
|---|---|---|---|---|
| Run scripts | sandbox (Linux) | user's machine (VM/local) | user's machine | container |
| pip/npm installs | usually yes | yes | yes | no (pre-bundle) |
| Open desktop apps | computer use (if enabled) | computer use | via shell / computer use | no |
| Question tool | question card | AskUserQuestion | AskUserQuestion | your app's UI |
| Files out | download links | local folder | local folder | Files API |

## Perplexity and other SKILL.md hosts
The same folder format works in other agents that support Agent Skills. Avoid host-specific tool names
in the body; say "search the web", "ask with the question tool", "share the file".
