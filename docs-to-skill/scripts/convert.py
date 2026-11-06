#!/usr/bin/env python3
"""convert.py - scrape a documentation website into a raw skill folder with Skill Seekers.

Usage:
  python convert.py URL [--name NAME] [--preset quick|standard|comprehensive] [--max-pages N]
                        [--out-root DIR] [--check] [--json]

Always runs `skill-seekers create URL --enhance-level 0`: scrape and organize only. Enhancement is
done afterwards by the running Claude session (see references/enhance-guide.md), because Skill
Seekers' own LOCAL enhancement launches `claude --dangerously-skip-permissions`, which this skill
never uses. This script never calls `skill-seekers enhance`, `install`, or `upload`.

Output: OUT_ROOT/NAME/ (default OUT_ROOT = ~/ClaudeMove/doc-skills). Skill Seekers' scratch data goes
to OUT_ROOT/.work/ so nothing is left in the current folder. Exit 0 = skill folder created.
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse

RESERVED = ("claude", "anthropic")


def clean_name(raw):
    s = re.sub(r"[^a-z0-9]+", "-", raw.lower())
    for w in RESERVED:
        s = s.replace(w, "")
    s = re.sub(r"-{2,}", "-", s).strip("-")
    if not s.endswith("docs"):
        s = (s + "-docs").strip("-")
    return s[:64].strip("-") or "site-docs"


def name_from_url(url):
    host = urlparse(url).netloc.lower()
    host = re.sub(r"^(www|docs|doc|developer|developers|api)\.", "", host)
    return clean_name(host.split(".")[0] if host else "site")


def main():
    ap = argparse.ArgumentParser(description="Scrape a docs site into a raw skill folder (no AI enhancement).")
    ap.add_argument("url")
    ap.add_argument("--name", help="skill name (cleaned to lowercase-hyphen, no claude/anthropic)")
    ap.add_argument("--preset", default="standard", choices=["quick", "standard", "comprehensive"])
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument("--out-root", default=str(Path.home() / "ClaudeMove" / "doc-skills"))
    ap.add_argument("--check", action="store_true", help="print the plan, run nothing")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if not re.match(r"^https?://", a.url):
        print("ERROR: URL must start with http:// or https:// (example: https://click.palletsprojects.com/)")
        sys.exit(2)
    name = clean_name(a.name) if a.name else name_from_url(a.url)
    root = Path(a.out_root).expanduser()
    out, work = root / name, root / ".work"
    exe = shutil.which("skill-seekers")
    cmd = [exe or "skill-seekers", "create", a.url, "--name", name, "-o", str(out),
           "-p", a.preset, "--max-pages", str(a.max_pages), "--enhance-level", "0"]
    plan = {"name": name, "skill_dir": str(out), "command": cmd}
    if a.check:
        plan["skill-seekers"] = "found" if exe else "MISSING - run scripts/setup_env.py"
        print(json.dumps(plan, indent=1))
        sys.exit(0 if exe else 1)
    if not exe:
        print("ERROR: skill-seekers is not installed. Run: python scripts/setup_env.py")
        sys.exit(1)

    work.mkdir(parents=True, exist_ok=True)
    if out.exists():
        backup = root / f"{name}.previous"
        shutil.rmtree(backup, ignore_errors=True)
        out.rename(backup)
        plan["previous_copy"] = str(backup)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    env.pop("ANTHROPIC_API_KEY", None)  # scrape-only: never paid API enhancement
    log = work / f"{name}.log"
    with open(log, "w", encoding="utf-8") as fh:
        r = subprocess.run(cmd, cwd=work, env=env, stdout=fh, stderr=subprocess.STDOUT)
    for junk in list(work.glob(f"{name}_data*")) + list(root.glob(f"{name}_data*")):
        shutil.rmtree(junk, ignore_errors=True) if junk.is_dir() else junk.unlink()

    text = log.read_text(encoding="utf-8", errors="ignore")
    plan.update(exit=r.returncode, log=str(log),
                enhancement_ran=bool(re.search(r"dangerously-skip-permissions|Enhancing SKILL|LOCAL mode", text, re.I)))
    ok = r.returncode == 0 and (out / "SKILL.md").is_file()
    if ok:
        refs = list((out / "references").glob("*.md")) if (out / "references").is_dir() else []
        plan["reference_files"] = len(refs)
        plan["reference_lines"] = sum(len(p.read_text(encoding="utf-8", errors="ignore").splitlines()) for p in refs)
    else:
        plan["error_tail"] = text.strip()[-800:]
    print(json.dumps(plan, indent=1) if a.json else "\n".join(f"{k:18} {v}" for k, v in plan.items()))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
