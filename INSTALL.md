# How to install these skills

Each folder in this repo is one skill. Pick the ones you want and install them using the section that matches how you use Claude.

The first time you use most of these skills, Claude will ask for your name (and, for the school skills, your school and library access). That's expected. Nothing is pre-filled with someone else's details.

---

## Option A: claude.ai, the Claude desktop app, or the mobile app

Skills you upload on claude.ai work in the desktop and mobile apps on the same account.

### 1. Turn on code execution (one time)

1. Open [claude.ai](https://claude.ai) and go to **Settings → Capabilities**.
2. Turn on **Code execution and file creation**. Skills don't run without it.

### 2. Get the skill zip

Easiest way: go to the [Releases page](https://github.com/gmartz8880/claude-skills/releases/latest) and download the `.zip` for each skill you want (for example `sds-bible.zip`). Don't unzip it.

Or build the zip yourself from a clone. The skill folder has to be at the top of the zip, not loose files:

Windows (PowerShell):

```powershell
Compress-Archive -Path .\sds-bible -DestinationPath .\sds-bible.zip
```

macOS / Linux:

```bash
zip -r sds-bible.zip sds-bible
```

### 3. Upload it

1. Go to **Settings → Capabilities → Skills** (on some accounts it's **Customize → Skills**).
2. Click **Upload skill** (or **+ → Upload a skill**) and choose the zip.
3. Make sure the skill's toggle is on.
4. Repeat for each skill.

### 4. Use it

Just ask normally, for example "make an SDS for acetone" or "research the history of OSHA". Claude loads the right skill on its own. You can also name it: "use the sru-research skill to ...".

---

## Option B: Claude Code (terminal or the Code tab)

Copy the skill folders into your personal skills folder. Claude Code picks them up in the next session.

Windows (PowerShell):

```powershell
git clone https://github.com/gmartz8880/claude-skills.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse .\claude-skills\sds-bible "$HOME\.claude\skills\"
```

macOS / Linux:

```bash
git clone https://github.com/gmartz8880/claude-skills.git
mkdir -p ~/.claude/skills
cp -r claude-skills/sds-bible ~/.claude/skills/
```

To install all of them, copy every folder except `README.md` and `INSTALL.md`.

Start a new Claude Code session, then run `/skills` (or just ask "what skills do you have?") to confirm they loaded.

To update later: `git pull` in the clone and copy the folders again.

---

## Extra setup for specific skills

| Skill | What it needs |
|---|---|
| sds-bible, humanize-ai-text, assignment-completion, sru-research | Make Word/PDF files. Claude.ai has the libraries built in. In Claude Code, have Python with `python-docx` and `reportlab` (`pip install python-docx reportlab`). |
| machine-blueprint | Python with `pillow`, `numpy`, `reportlab` (`python scripts/setup_env.py` installs them). Optional for CAD files: `ezdxf`, `cadquery`, FreeCAD. |
| sru-research, assignment-completion | JSTOR through a school library is optional. Without it, they use Google Scholar and the other search engines. Library sign-ins work best with the Claude in Chrome extension. |
| ti-calc-app-builder | Claude Code only for building real calculator files. Run `python ~/.claude/skills/ti-calc-app-builder/scripts/setup_env.py` once. |
| skill-forge | Works anywhere. Its scripts (validate, package, install) work best in Claude Code. |
| voice-line | Claude Code only, Windows-focused. Needs the Telegram plugin (`/plugin install telegram@claude-plugins-official`, then `/telegram:configure <your bot token>`), plus ffmpeg, `faster-whisper` and `piper-tts`. Run `python ~/.claude/skills/voice-line/scripts/doctor.py` to see what's missing. Then tell Claude your name: `python ~/.claude/skills/voice-line/scripts/speak.py --remember-name "Your Name"`. |
| docs-to-skill | Python 3.10+, internet, and the skill-forge skill. scripts/setup_env.py installs Skill Seekers (pip/uv package skill-seekers) if missing. |
| accounting-questions, ancient-script-translator, evidence-research, advanced-search, sassy-meemaw | Nothing extra. |

---

## Troubleshooting

- **"Invalid skill" on upload:** the zip has loose files instead of a folder. Rebuild it so the zip contains `skill-name/SKILL.md`.
- **Skill never triggers:** check its toggle is on (claude.ai), or that the folder is directly inside `~/.claude/skills/` (Claude Code), and start a new chat or session.
- **It asks for your name every time:** that's on purpose in a new chat. If you want it remembered, tell Claude to save your name to memory, or keep a short "about me" note in your profile or preferences.
