#!/usr/bin/env python3
"""init_skill.py - scaffold a new plug-and-play skill.

Usage:
  python init_skill.py NAME [--out DIR] [--description "..."] [--force]

Creates DIR/NAME/ with:
  SKILL.md (from templates/SKILL.template.md), scripts/setup_env.py (check-then-install),
  references/README.md, templates/.keep, evals/evals.json, README.md
"""
import os, re, sys, argparse, shutil, json

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(os.path.dirname(HERE), "templates")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name")
    ap.add_argument("--out", default=".")
    ap.add_argument("--description", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    name = a.name.strip().lower().replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^a-z0-9-]", "", name)
    name = re.sub(r"-+", "-", name).strip("-")
    if not name or len(name) > 64 or re.search(r"claude|anthropic", name):
        print("Invalid name (lowercase-hyphen, <= 64 chars, no claude/anthropic)."); sys.exit(1)
    root = os.path.join(a.out, name)
    if os.path.exists(root) and not a.force:
        print(root, "already exists (use --force to overwrite the scaffold files)."); sys.exit(1)
    for sub in ("scripts", "references", "templates", "evals"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    title = a.title or name.replace("-", " ").title()
    desc = a.description or f"TODO: what {title} does and when to use it (<= 200 chars, trigger words first)."
    s = open(os.path.join(TPL, "SKILL.template.md"), encoding="utf-8").read()
    s = s.replace("{{name}}", name).replace("{{title}}", title).replace("{{description}}", desc)
    open(os.path.join(root, "SKILL.md"), "w", encoding="utf-8").write(s)
    shutil.copy(os.path.join(TPL, "setup_env.template.py"), os.path.join(root, "scripts", "setup_env.py"))
    ev = json.load(open(os.path.join(TPL, "evals.template.json"), encoding="utf-8"))
    ev["skill"] = name
    json.dump(ev, open(os.path.join(root, "evals", "evals.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(root, "references", "README.md"), "w", encoding="utf-8").write(
        "# References\n\nOne topic per file. SKILL.md says when to read each one.\n")
    open(os.path.join(root, "templates", ".keep"), "w").close()
    r = open(os.path.join(TPL, "README.template.md"), encoding="utf-8").read()
    open(os.path.join(root, "README.md"), "w", encoding="utf-8").write(r.replace("{{name}}", name).replace("{{title}}", title))
    print("Created", root)
    print("Next: fill SKILL.md TODOs, add scripts/references, then run validate_skill.py", root)


if __name__ == "__main__":
    main()
