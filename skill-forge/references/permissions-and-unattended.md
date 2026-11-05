# Permissions and unattended mode - policy: GUIDE, DO NOT CHANGE

Contents: 1 Policy - 2 What counts as a permission change - 3 What to do instead - 4 Setup options to give
the user (A-E) - 5 Text for generated skills

## 1. Policy (heavy bias, applies to Skill Forge and to every skill it builds)
Claude must **not** change its own permissions, permission mode, safety settings, or system security
settings - even if that would make the job faster, even if a script could do it, and even if an earlier
message in the conversation seemed to allow it. Instead, Claude **tells the user exactly how** to do it
(numbered steps, the exact text to paste, how to undo it) and keeps working with the permissions it has.

Why: a tool that widens its own permissions removes the human check that catches mistakes. The user can
make the change in under a minute with the steps below, and it stays under their control.

The only exception: the user, in the current message, explicitly asks Claude to make one specific change
(for example "add these allow rules to my settings.json for me"). Then Claude: shows the exact change,
backs up the file, makes only that change, verifies it, and explains how to undo it. Never bypass mode,
never the critical-path override, never managed/enterprise policy, never UAC/antivirus/firewall.

## 2. What counts as a permission change (do not do these yourself)
- Editing `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json` permission
  rules (`allow`, `ask`, `deny`, `defaultMode`, `additionalDirectories`).
- Switching permission mode, or launching `claude` with `--permission-mode bypassPermissions`,
  `--dangerously-skip-permissions`, or `--allow-dangerously-skip-permissions`.
- Setting `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS` or other safety environment variables.
- Running the project's `Start-Claude-Unattended.ps1` or `Start-Claude-Administrator.ps1` launchers.
- Windows: UAC elevation (`-Verb RunAs`), `Set-ExecutionPolicy`, Defender/firewall exclusions, registry
  policy keys. macOS: TCC/Accessibility grants. Cowork/Desktop: per-app computer-use approvals.
- Adding hooks that auto-approve tool calls.

## 3. What to do instead
1. Do everything possible with current permissions (most installs and file work only need normal prompts).
2. When a prompt or block would repeat many times, generate `PERMISSIONS-SETUP.md` for the skill with
   `python scripts/permissions_helper.py <skill-dir>` and point the user to the matching option below.
3. Continue the task; if something is blocked, finish everything else and list the one step the user must do.

## 4. Setup options to give the user (least to most power)
**A. Approve as you go (no setup).** Click "Allow" / "Always allow for this project" when Claude Code asks.
Cowork/Desktop: approve each app the first time ("Always allow").

**B. Auto mode (recommended for autonomy).** Claude Code: press Shift+Tab until the mode shows "auto"
(Desktop / VS Code: Settings > Claude Code > enable auto mode, then pick it in the mode menu). A
classifier approves routine actions and stops risky ones. Auto appears only when the model, provider,
and settings allow it; if it is missing, use C. Undo: Shift+Tab back to default (Manual).

**C. Allow rules for this skill only.** Open `%USERPROFILE%\.claude\settings.json` (Windows) or
`~/.claude/settings.json` (macOS/Linux) in Notepad, and merge the block from `PERMISSIONS-SETUP.md`, e.g.
```json
{ "permissions": { "allow": [ "Bash(python *)", "Bash(python3 *)", "Bash(py *)", "Read", "Edit", "Write" ] } }
```
Save, restart Claude Code. Undo: delete those lines. (The skill's own `allowed-tools` frontmatter already
pre-approves its tools during its turn in Claude Code; rules here make it permanent.)

**D. The project's unattended launcher (Claude Local kit, Windows).** For long jobs with no human present:
```powershell
& "$env:USERPROFILE\ClaudeLocal\Connector\Start-Claude-Unattended.ps1"
```
(default install path from the kit's `setup.ps1`; run that first). It starts Claude Code in
`bypassPermissions` mode inside `ClaudeLocal\Work` for that session only and writes no permanent
setting. Use only with a clearly scoped task, ideally in a VM or Windows Sandbox, with backups.
Administrator version: `Start-Claude-Administrator.ps1` (UAC prompt appears once). Undo: close the session.

**E. Critical-path override (`-IncludeCriticalPathOverride`).** Only in a disposable VM whose contents
can be lost. Never needed for building or running skills. Claude never recommends it unprompted.

Notes: managed/organization policy overrides all of these; Cowork's per-app approvals and Windows UAC
cannot be skipped by any Claude setting.

## 5. Text to paste into every generated skill (Autonomy section)
> Do the whole job without asking about routine steps (installing missing packages, creating files,
> running this skill's scripts, opening the apps it needs). Do not change Claude's permissions, permission
> mode, or system security settings yourself. If repeated permission prompts slow the job, tell the user
> to see PERMISSIONS-SETUP.md (auto mode or the allow rules listed there) and keep working.
