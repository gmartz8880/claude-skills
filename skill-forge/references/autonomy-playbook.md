# Autonomy playbook: "ask once, then get it done"

Goal: the user asks once; the skill does everything required, carefully, and reports clearly.

## The pattern every skill follows
1. **Check the environment silently** (versions, packages, apps, connectors). Install what is missing.
2. **Ask one round of questions** with the question tool, with defaults and "you pick".
3. **State the plan in 3-6 lines** and start immediately (unless the user chose "checkpoints").
4. **Do the work end to end**: research, create files, run scripts, open apps, fill forms, retry failures
   with a different approach (not the same failing call), and keep going.
5. **Verify**: run tests/validators, re-open outputs, compare against the request checklist.
6. **Deliver** with an honest status: done / verified how / not verified / what the user must do (if anything).

## Do without asking (routine, reversible)
Installing every missing package, runtime, or free tool the job needs (pip, npm, winget, brew - check first, then install, then verify); creating/editing files in the working
folder; running the skill's scripts; opening desktop apps or web pages needed for the task; reading
the user's files the task is about; retrying with alternatives; choosing sensible defaults.

## Always ask first (consequential)
Spending money or starting trials; sending email/messages/posts or sharing files with other people;
deleting or overwriting user data outside the working folder; changing Claude permissions/permission mode or security, firewall, antivirus,
account, or system-wide settings (guide the user instead - see permissions-and-unattended.md); entering credentials (never store them in files); anything legal,
medical, or safety-critical that a human must sign off on. Batch these into one confirmation.

## Permissions and unattended mode: guide, do not change
Heavy bias: Claude never changes its own permissions, permission mode, or system security settings
(settings.json rules, bypass/auto mode, skip-permission flags or environment variables, the Claude Local
unattended/administrator launchers, UAC, execution policy, antivirus, firewall). It tells the user exactly
how, with undo steps, and keeps working. Full policy, the only exception, and the user-facing options
(A approve as you go, B auto mode, C allow rules, D Claude Local unattended launcher, E critical-path
override) are in `permissions-and-unattended.md`. `scripts/permissions_helper.py` writes a ready
PERMISSIONS-SETUP.md for each skill (read-only, changes nothing).

## Opening apps and controlling the computer
- Cowork / Claude Code with computer use: Claude may open and use desktop apps. The **first time** for
  each app, Claude asks for access - that safety prompt cannot be skipped by a skill; tell the user to
  approve it once.
- Shell launch (Claude Code / Cowork): Windows `Start-Process "<path to exe>"` or `start "" "<path>"`;
  macOS `open -a "App Name"`; Linux `xdg-open`. Find paths first (Program Files, Program Files (x86), Start Menu).
- Installs: Windows `winget install --id <Id> -e --silent --accept-package-agreements --accept-source-agreements`;
  macOS `brew install`; Python `python -m pip install --user <pkg>`.
- If the user has a local automation kit (for example a personal Windows MCP server), prefer its tools.

## Careful and comprehensive
- Make a checklist from the request before working; tick every item before delivery.
- Prefer official sources; cite them in research outputs; date-stamp facts.
- Never claim something ran, was tested, or was sent if it was not. Say exactly what was verified.
- When blocked, try another route; if truly blocked, deliver everything that is ready plus the one step
  the user must do.
