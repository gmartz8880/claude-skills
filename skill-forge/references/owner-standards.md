# Default standards - apply to every skill built

These are the skill author's defaults. At intake, also ask the user for their name (for the skill's `author` field) and their main operating system, and let their answers and any stated preferences override the defaults below.

- Ask questions up front with the question tool, in one round; never repeat a question already answered.
- After the questions, work autonomously: install what is missing, open apps, and finish the job.
- Check whether a dependency is already installed before installing it (check-then-install).
- Skills must work in both the Claude app (upload zip, folder at zip root) and Claude Code (`~/.claude/skills`).
- Give commands for the user's main operating system first (PowerShell on Windows, bash on macOS/Linux).
- Documents: Word (.docx) by default for guides, reports, forms, and academic work; revisions as new files.
- Plain, conversational wording; numbered steps; minimal bolding; no decoration on forms.
- Comparisons between AI services: neutral.
- Research: dig deeper when asked; prefer authoritative/official sources; cite them.
- Be honest about verification: say what was tested and what was not.
- After changing a skill, show the full updated workflow.
- Each skill ships with its own detailed technical document and its own zip (no combined bundle unless asked).
- Stay compatible with the skills the user already has installed (check `~/.claude/skills` or ask).
