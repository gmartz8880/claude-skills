#!/usr/bin/env python3
"""permissions_helper.py - write PERMISSIONS-SETUP.md for a skill. READ-ONLY: never edits any settings.

It reads the skill's `allowed-tools`, scans its scripts/SKILL.md for the commands it runs, and writes
step-by-step instructions the USER can follow to reduce permission prompts (options A-E, least to most
power), including the exact settings.json block to paste and how to undo it.

Usage:
  python permissions_helper.py SKILL_DIR [--out FILE] [--print]
"""
import os, re, sys, json, argparse

BASE_RULES = ["Read", "Edit", "Write", "Glob", "Grep"]
CMD_RULES = {
    r"\bpython3?\b|\bpy\b|\.py\b": ["Bash(python *)", "Bash(python3 *)", "Bash(py *)"],
    r"\bpip\b|pip install": ["Bash(python -m pip install *)", "Bash(pip install *)"],
    r"\bmake\b": ["Bash(make *)", "Bash(make)"],
    r"\bnpm\b|\bnode\b": ["Bash(npm *)", "Bash(node *)"],
    r"\bgit\b": ["Bash(git status)", "Bash(git diff *)", "Bash(git add *)", "Bash(git commit *)"],
    r"\bpandoc\b": ["Bash(pandoc *)"],
    r"\bwinget\b": ["Bash(winget install *)"],
    r"Start-Process|PowerShell": ["PowerShell(Start-Process *)"],
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skill")
    ap.add_argument("--out")
    ap.add_argument("--print", action="store_true")
    a = ap.parse_args()
    md = os.path.join(a.skill, "SKILL.md")
    text = open(md, encoding="utf-8").read()
    name = (re.search(r"(?m)^name:\s*([a-z0-9-]+)", text) or [None, os.path.basename(a.skill)])[1]
    corpus = text
    for dp, _, fns in os.walk(os.path.join(a.skill, "scripts")):
        for fn in fns:
            if fn.endswith((".py", ".ps1", ".sh")):
                corpus += open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()
    rules = list(BASE_RULES)
    m = re.search(r"(?m)^allowed-tools:\s*(.+)$", text)
    if m:
        rules += [t for t in re.split(r"[,\s]+(?![^()]*\))", m.group(1).strip()) if t]
    for pat, rr in CMD_RULES.items():
        if re.search(pat, corpus):
            rules += rr
    seen, final = set(), []
    for r in rules:
        if r not in seen:
            seen.add(r); final.append(r)
    block = json.dumps({"permissions": {"allow": final}}, indent=2)
    doc = f"""# Permissions setup for the {name} skill (optional)

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
1. Windows: press Win+R, type `notepad %USERPROFILE%\\.claude\\settings.json`, Enter.
   macOS/Linux: `nano ~/.claude/settings.json`.
2. If the file is empty, paste the whole block. If it already has a `"permissions"` section, add the
   lines inside `"allow"` to the existing list.
```json
{block}
```
3. Save and restart Claude Code.
Undo: remove those lines and restart.

## Option D - unattended session (Claude Local kit, Windows; only for long jobs with nobody watching)
1. Run the kit's `setup.ps1` once (see the kit's GUIDE.md).
2. Start the session: `& "$env:USERPROFILE\\ClaudeLocal\\Connector\\Start-Claude-Unattended.ps1"`
   It runs Claude Code in bypass-permissions mode inside `ClaudeLocal\\Work` for this session only.
3. Give it one clearly scoped task. Prefer a VM or Windows Sandbox; keep backups.
Undo: close the window - nothing permanent is changed.

## Option E - critical-path override
Only inside a disposable virtual machine. Not needed for this skill. Not recommended.

Organization (managed) policy, Windows UAC prompts, and Cowork's per-app approvals cannot be skipped by any of these.
"""
    out = a.out or os.path.join(a.skill, "PERMISSIONS-SETUP.md")
    if a.print:
        print(doc)
    else:
        open(out, "w", encoding="utf-8").write(doc)
        print("Wrote", out, f"({len(final)} allow rules suggested; no settings were changed)")


if __name__ == "__main__":
    main()
