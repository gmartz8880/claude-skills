# Permissions setup for the skill-forge skill (optional)

The skill works without any of this - Claude Code just asks before some actions. Follow ONE option only
if the prompts slow you down. Claude will not change these settings for you; you stay in control.

## Option A - approve as you go (no setup)
Click **Allow** (or **Always allow for this project**) when Claude Code asks. In Cowork / Claude Desktop,
approve each app the first time it is opened ("Always allow").

## Option B - auto mode (recommended)
1. In Claude Code press **Shift+Tab** until the mode label shows **auto**.
   (Claude Desktop / VS Code: Settings > Claude Code > turn on auto mode, then choose it in the mode menu.)
   If auto does not appear, your model or plan does not offer it yet - use Option C instead.
2. Routine actions run without prompts; risky ones are still stopped.
Undo: Shift+Tab back to default.

## Option C - allow rules for this skill's commands
1. Windows: press Win+R, type `notepad %USERPROFILE%\.claude\settings.json`, Enter.
   macOS/Linux: `nano ~/.claude/settings.json`.
2. If the file is empty, paste the whole block. If it already has a `"permissions"` section, add the
   lines inside `"allow"` to the existing list.
```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(py *)",
      "Bash(python -m pip install *)",
      "Bash(pip install *)",
      "Bash(make *)",
      "Bash(make)",
      "Bash(npm *)",
      "Bash(node *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(pandoc *)",
      "Bash(winget install *)",
      "PowerShell(Start-Process *)"
    ]
  }
}
```
3. Save and restart Claude Code.
Undo: remove those lines and restart.

## Option D - unattended session (Claude Local kit, Windows; only for long jobs with nobody watching)
1. Run the kit's `setup.ps1` once (see the kit's GUIDE.md).
2. Start the session: `& "$env:USERPROFILE\ClaudeLocal\Connector\Start-Claude-Unattended.ps1"`
   It runs Claude Code in bypass-permissions mode inside `ClaudeLocal\Work` for this session only.
3. Give it one clearly scoped task. Prefer a VM or Windows Sandbox; keep backups.
Undo: close the window - nothing permanent is changed.

## Option E - critical-path override
Only inside a disposable virtual machine. Not needed for this skill. Not recommended.

Organization (managed) policy, Windows UAC prompts, and Cowork's per-app approvals cannot be skipped by any of these.
