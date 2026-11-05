#!/usr/bin/env python3
"""package_skill.py - validate and package skills for every Claude surface.

Usage:
  python package_skill.py SKILL_DIR [SKILL_DIR ...] --out dist [--profile portable|claude-code] [--bundle NAME]
                                    [--extra FILE ...] [--skip-validate]

For each skill it writes into OUT/<name>/ :
  <name>.zip                 upload-ready (skill folder at the zip root) - Claude.ai / Desktop / Cowork / API
  install-claude-code.ps1    Windows: installs into %USERPROFILE%\\.claude\\skills (backs up an old copy)
  install-claude-code.sh     macOS/Linux: installs into ~/.claude/skills
  INSTALL.md                 plain-language install steps for every surface
  PERMISSIONS-SETUP.md       optional ways for the USER to reduce prompts (the skill never changes settings)
  any --extra files          (for example the skill's technical guide .docx)
and then OUT/<name>-package.zip containing all of the above (one zip per skill).
--bundle NAME additionally makes one zip with several skills (only when the user asks for a bundle).
"""
import os, sys, zipfile, argparse, subprocess, shutil, re

HERE = os.path.dirname(os.path.abspath(__file__))
JUNK = {"__pycache__", ".DS_Store", ".git", "Thumbs.db", ".ipynb_checkpoints", "node_modules", ".venv", "venv"}

PS1 = r'''# Installs the "{name}" skill for Claude Code (Windows PowerShell)
# Run:  powershell -ExecutionPolicy Bypass -File .\install-claude-code.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$zip  = Join-Path $here "{name}.zip"
$dest = Join-Path $env:USERPROFILE ".claude\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$target = Join-Path $dest "{name}"
if (Test-Path $target) {{
  $bak = "$target.backup-" + (Get-Date -Format "yyyyMMdd-HHmmss")
  Move-Item $target $bak
  Write-Host "Old copy backed up to $bak"
}}
Expand-Archive -Path $zip -DestinationPath $dest -Force
if (Test-Path (Join-Path $target "SKILL.md")) {{ Write-Host "Installed: $target" }} else {{ throw "Install failed: SKILL.md not found" }}
$py = (Get-Command python -ErrorAction SilentlyContinue) ; if (-not $py) {{ $py = Get-Command py -ErrorAction SilentlyContinue }}
if ($py -and (Test-Path (Join-Path $target "scripts\setup_env.py"))) {{
  Write-Host "Checking dependencies (installs only what is missing)..."
  & $py.Source (Join-Path $target "scripts\setup_env.py")
}} elseif (-not $py) {{ Write-Host "Python not found. Install it with:  winget install -e --id Python.Python.3.12" }}
Write-Host "Done. Restart Claude Code (or run /skills) to see '{name}'."
'''

SH = r'''#!/usr/bin/env bash
# Installs the "{name}" skill for Claude Code (macOS / Linux)
set -euo pipefail
here="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
dest="$HOME/.claude/skills"; mkdir -p "$dest"
target="$dest/{name}"
if [ -d "$target" ]; then mv "$target" "$target.backup-$(date +%Y%m%d-%H%M%S)"; echo "Old copy backed up"; fi
python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$here/{name}.zip" "$dest"
[ -f "$target/SKILL.md" ] && echo "Installed: $target" || {{ echo "Install failed"; exit 1; }}
if [ -f "$target/scripts/setup_env.py" ]; then python3 "$target/scripts/setup_env.py" || true; fi
echo "Done. Restart Claude Code (or run /skills) to see '{name}'."
'''

INSTALL = '''# Installing the {name} skill

## Claude app (Claude.ai, Claude Desktop, Cowork)
1. Make sure code execution is on: Settings > Capabilities (or Customize) > "Code execution and file creation".
2. Go to Settings > Capabilities (or Customize) > Skills > Upload skill.
3. Choose `{name}.zip` (do not unzip it). Turn the skill on.
4. Start a new chat and ask for the task in your own words. Example: {example}

## Claude Code (Windows)
1. Right-click `install-claude-code.ps1` > Run with PowerShell, or run:
   `powershell -ExecutionPolicy Bypass -File .\\install-claude-code.ps1`
2. Restart Claude Code. Type `/skills` to confirm it is listed, or `/{name}` to run it.

## Claude Code (macOS / Linux)
`bash install-claude-code.sh`, then restart Claude Code.

## Claude Code project (share with a repo)
Unzip `{name}.zip` into `<your-repo>/.claude/skills/`.

## Updating
Upload the new zip again (Claude app) or re-run the installer (it backs up the old copy).
'''


def zip_dir(src_dir, zip_path, arc_root):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, dns, fns in os.walk(src_dir):
            dns[:] = sorted(d for d in dns if d not in JUNK)
            for fn in sorted(fns):
                if fn in JUNK or fn.endswith((".pyc", ".pyo")):
                    continue
                p = os.path.join(dp, fn)
                rel = os.path.relpath(p, src_dir).replace(os.sep, "/")
                z.write(p, f"{arc_root}/{rel}")


def skill_name(d):
    t = open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()
    m = re.search(r"(?m)^name:\s*['\"]?([a-z0-9-]+)", t)
    return m.group(1) if m else os.path.basename(os.path.normpath(d))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="+")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--profile", default="portable", choices=["portable", "claude-code"])
    ap.add_argument("--bundle", help="also build one zip with all skills (only if asked)")
    ap.add_argument("--extra", nargs="*", default=[], help="files to add to each skill's package (e.g. guide.docx)")
    ap.add_argument("--example", default="describe your task in plain words")
    ap.add_argument("--skip-validate", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    built = []
    for d in a.skills:
        d = os.path.abspath(d)
        name = skill_name(d)
        if not a.skip_validate:
            r = subprocess.run([sys.executable, os.path.join(HERE, "validate_skill.py"), d, "--profile", a.profile])
            if r.returncode != 0:
                print(f"NOT PACKAGED: {name} has validation errors."); sys.exit(1)
        pkg = os.path.join(a.out, name)
        if os.path.exists(pkg):
            shutil.rmtree(pkg)
        os.makedirs(pkg)
        upload = os.path.join(pkg, f"{name}.zip")
        zip_dir(d, upload, name)
        open(os.path.join(pkg, "install-claude-code.ps1"), "w", encoding="utf-8", newline="\r\n").write(PS1.format(name=name))
        sh = os.path.join(pkg, "install-claude-code.sh")
        open(sh, "w", encoding="utf-8", newline="\n").write(SH.format(name=name)); os.chmod(sh, 0o755)
        open(os.path.join(pkg, "INSTALL.md"), "w", encoding="utf-8").write(INSTALL.format(name=name, example=a.example))
        perm = os.path.join(d, "PERMISSIONS-SETUP.md")
        if not os.path.exists(perm):
            subprocess.run([sys.executable, os.path.join(HERE, "permissions_helper.py"), d, "--out",
                            os.path.join(pkg, "PERMISSIONS-SETUP.md")], capture_output=True)
        else:
            shutil.copy(perm, pkg)
        for x in a.extra:
            shutil.copy(x, pkg)
        # verify the upload zip layout
        with zipfile.ZipFile(upload) as z:
            tops = {n.split("/")[0] for n in z.namelist()}
            assert tops == {name} and f"{name}/SKILL.md" in z.namelist(), "zip layout check failed"
        final = os.path.join(a.out, f"{name}-package.zip")
        zip_dir(pkg, final, f"{name}-package")
        built.append((name, d))
        print(f"PACKAGED {name}: {final}  (upload zip: {upload})")
    if a.bundle:
        bz = os.path.join(a.out, f"{a.bundle}.zip")
        with zipfile.ZipFile(bz, "w", zipfile.ZIP_DEFLATED) as z:
            for name, d in built:
                for dp, dns, fns in os.walk(d):
                    dns[:] = [x for x in dns if x not in JUNK]
                    for fn in fns:
                        if fn in JUNK or fn.endswith(".pyc"):
                            continue
                        p = os.path.join(dp, fn)
                        z.write(p, f"{name}/" + os.path.relpath(p, d).replace(os.sep, "/"))
        print("BUNDLE:", bz)


if __name__ == "__main__":
    main()
