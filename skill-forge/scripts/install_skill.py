#!/usr/bin/env python3
"""install_skill.py - install a skill (.zip or folder) into Claude Code, safely.

Usage:
  python install_skill.py SKILL.zip|SKILL_DIR            # personal: ~/.claude/skills/<name>
  python install_skill.py SKILL.zip --project REPO_DIR   # project: REPO_DIR/.claude/skills/<name>
  python install_skill.py SKILL.zip --check              # show what would happen

Backs up an existing copy to <name>.backup-YYYYmmdd-HHMMSS, verifies SKILL.md, then runs the skill's
scripts/setup_env.py (check-then-install) if present. Works on Windows, macOS, Linux.
Note: Cowork and Claude.ai do not read ~/.claude/skills - upload the zip in the app for those.
"""
import os, sys, zipfile, shutil, argparse, tempfile, datetime, subprocess


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--project")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--no-setup", action="store_true")
    a = ap.parse_args()
    base = os.path.join(a.project, ".claude", "skills") if a.project else os.path.join(os.path.expanduser("~"), ".claude", "skills")
    tmp = None
    src = a.src
    if src.lower().endswith(".zip"):
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(src) as z:
            z.extractall(tmp)
        tops = [d for d in os.listdir(tmp) if os.path.isdir(os.path.join(tmp, d))]
        if len(tops) != 1:
            print("Zip must contain one skill folder at its root."); sys.exit(1)
        src = os.path.join(tmp, tops[0])
    if not os.path.exists(os.path.join(src, "SKILL.md")):
        print("No SKILL.md found in", src); sys.exit(1)
    name = os.path.basename(os.path.normpath(src))
    target = os.path.join(base, name)
    print(f"Install '{name}' -> {target}")
    if a.check:
        print("exists, would back up" if os.path.exists(target) else "new install"); return
    os.makedirs(base, exist_ok=True)
    if os.path.exists(target):
        bak = f"{target}.backup-{datetime.datetime.now():%Y%m%d-%H%M%S}"
        shutil.move(target, bak); print("Backed up old copy to", bak)
    shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".git"))
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = os.path.exists(os.path.join(target, "SKILL.md"))
    print("Installed." if ok else "FAILED.")
    setup = os.path.join(target, "scripts", "setup_env.py")
    if ok and not a.no_setup and os.path.exists(setup):
        print("Running dependency check...")
        subprocess.run([sys.executable, setup])
    print("Restart Claude Code or run /skills to see it.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
