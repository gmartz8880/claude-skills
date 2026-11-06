#!/usr/bin/env python3
"""forge_gate.py - put a generated docs skill through the skill-forge quality gate.

Usage:
  python forge_gate.py fix   SKILL_DIR [--json]   mechanical fixes (safe to repeat)
  python forge_gate.py check SKILL_DIR [--json]   skill-forge validate_skill.py + extra gate checks
  python forge_gate.py ship  SKILL_DIR [--json]   skill-forge permissions_helper, package_skill, install_skill

fix:   renames folder/name to a valid name, deletes empty folders and junk, adds license/compatibility/
       metadata to the frontmatter, adds a table of contents to reference files over 100 lines,
       writes an evals/evals.json skeleton if missing.
check: PASS only when skill-forge reports 0 ERROR and 0 WARN and the extra checks are clean
       (real description, numbered workflow, evals filled in, no leftover placeholder text).
ship:  only runs after check passes. Packages to SKILL_DIR/../dist and installs into ~/.claude/skills.
The skill-forge folder is found the same way as setup_env.py (env SKILL_FORGE_DIR or ~/.claude).
Exit 0 = pass / done, 1 = issues remain, 2 = usage or missing skill-forge.
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

GENERIC = re.compile(r"^use when working with", re.I)
PLACEHOLDER = re.compile(r"TODO|\{\{|Pattern \d+:", re.I)
RESERVED = ("claude", "anthropic")


def find_forge():
    env = os.environ.get("SKILL_FORGE_DIR")
    cands = [Path(env)] if env else []
    home = Path.home() / ".claude"
    cands.append(home / "skills" / "skill-forge")
    if (home / "plugins").is_dir():
        cands += [p.parent.parent for p in (home / "plugins").glob("**/skill-forge/scripts/validate_skill.py")]
    for c in cands:
        if (c / "scripts" / "validate_skill.py").is_file():
            return c
    return None


def split_front(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def get_field(front, key):
    m = re.search(rf"^{key}:\s*(.*)$", front, re.M)
    return m.group(1).strip().strip("\"'") if m else ""


def valid_name(n):
    s = re.sub(r"[^a-z0-9]+", "-", n.lower())
    for w in RESERVED:
        s = s.replace(w, "")
    return re.sub(r"-{2,}", "-", s).strip("-")[:64].strip("-") or "site-docs"


def add_toc(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    if len(lines) <= 100 or "## Contents" in text[:2000]:
        return False
    heads = [l for l in lines if re.match(r"^#{2,3} \S", l)]
    if not heads:
        return False
    toc = ["## Contents", ""]
    for h in heads[:60]:
        level, title = len(h) - len(h.lstrip("#")), h.lstrip("#").strip()
        anchor = re.sub(r"[^a-z0-9 -]", "", title.lower()).replace(" ", "-")
        toc.append(f"{'  ' * (level - 2)}- [{title}](#{anchor})")
    first = 1 if lines and lines[0].startswith("# ") else 0
    path.write_text("\n".join(lines[:first] + [""] + toc + [""] + lines[first:]) + "\n", encoding="utf-8")
    return True


def do_fix(d):
    done = []
    sk = d / "SKILL.md"
    front, body = split_front(sk.read_text(encoding="utf-8", errors="ignore"))
    name = get_field(front, "name") or d.name
    good = valid_name(name)
    if good != name:
        front = re.sub(r"^name:.*$", f"name: {good}", front, flags=re.M)
        done.append(f"name {name} -> {good}")
    adds = {"license": "Documentation content belongs to its publisher; see references/SOURCE.md",
            "compatibility": "Claude.ai, Claude Desktop, Cowork, Claude Code, Claude API. Reference-only skill, no scripts needed."}
    for k, v in adds.items():
        if not get_field(front, k):
            front += f"\n{k}: {v}"
            done.append(f"added {k}")
    if "metadata:" not in front:
        front += '\nmetadata:\n  version: "1.0.0"\n  generator: docs-to-skill (Skill Seekers + skill-forge)'
        done.append("added metadata")
    sk.write_text(f"---\n{front.strip()}\n---\n{body}", encoding="utf-8")
    for sub in ("assets", "scripts", "templates"):
        p = d / sub
        if p.is_dir() and not any(p.iterdir()):
            p.rmdir(); done.append(f"removed empty {sub}/")
    for junk in list(d.rglob("__pycache__")) + list(d.rglob(".DS_Store")) + list(d.rglob("Thumbs.db")):
        shutil.rmtree(junk, ignore_errors=True) if junk.is_dir() else junk.unlink()
    if (d / "references").is_dir():
        for ref in (d / "references").glob("*.md"):
            if add_toc(ref):
                done.append(f"TOC added to references/{ref.name}")
    ev = d / "evals" / "evals.json"
    if not ev.exists():
        ev.parent.mkdir(exist_ok=True)
        ev.write_text(json.dumps({"skill": good, "should_trigger": [
            {"prompt": "TODO realistic question this documentation answers", "expected": ["skill triggers", "answer cites the references"]}
            for _ in range(3)], "should_not_trigger": ["TODO unrelated request", "TODO near-miss request"]}, indent=1), encoding="utf-8")
        done.append("evals/evals.json skeleton written (fill in the TODO prompts)")
    if d.name != good:
        target = d.parent / good
        if target.exists():
            shutil.rmtree(target)
        d.rename(target); d = target
        done.append(f"folder renamed to {good}")
    return d, done


def do_check(d, forge):
    r = subprocess.run([sys.executable, str(forge / "scripts" / "validate_skill.py"), str(d), "--json"],
                       capture_output=True, text=True)
    try:
        rep = json.loads(r.stdout)
        items = rep if isinstance(rep, list) else rep.get("findings", [])
    except Exception:
        items = [{"level": "ERROR", "msg": "validator output unreadable: " + (r.stdout + r.stderr)[-300:]}]
    errors = [i for i in items if i.get("level") == "ERROR"]
    warns = [i for i in items if i.get("level") == "WARN"]
    extra = []
    front, body = split_front((d / "SKILL.md").read_text(encoding="utf-8", errors="ignore"))
    desc = get_field(front, "description")
    if GENERIC.search(desc) or len(desc) < 60:
        extra.append("description is generic or short: rewrite it (what the docs cover + trigger words, <= 200 chars)")
    if not re.search(r"^#+ .*(workflow|how to use)", body, re.I | re.M) or not re.search(r"^\s*1\. ", body, re.M):
        extra.append("SKILL.md needs a numbered 'How to use' workflow section")
    if PLACEHOLDER.search(body):
        extra.append("SKILL.md still has placeholder or raw 'Pattern N:' text")
    ev = d / "evals" / "evals.json"
    if not ev.exists() or "TODO" in ev.read_text(encoding="utf-8", errors="ignore"):
        extra.append("evals/evals.json is missing or still has TODO prompts")
    if not (d / "references" / "SOURCE.md").is_file():
        extra.append("references/SOURCE.md missing (source URL, date scraped, license found)")
    ok = r.returncode == 0 and not errors and not warns and not extra
    return {"skill_dir": str(d), "validator_exit": r.returncode, "errors": errors, "warns": warns,
            "extra": extra, "pass": ok}


def do_ship(d, forge):
    res = do_check(d, forge)
    if not res["pass"]:
        res["ship"] = "refused: check did not pass"
        return res, False
    dist = d.parent / "dist"
    steps = [["permissions_helper.py", str(d)],
             ["package_skill.py", str(d), "--out", str(dist)],
             ["install_skill.py", str(dist / d.name / f"{d.name}.zip")]]
    log = []
    for s in steps:
        r = subprocess.run([sys.executable, str(forge / "scripts" / s[0])] + s[1:], capture_output=True, text=True)
        log.append({"step": s[0], "exit": r.returncode, "tail": (r.stdout + r.stderr).strip()[-400:]})
        if r.returncode != 0:
            return {"ship": log}, False
    installed = Path.home() / ".claude" / "skills" / d.name / "SKILL.md"
    return {"ship": log, "zip": str(dist / d.name / f"{d.name}.zip"), "installed": installed.is_file()}, installed.is_file()


def main():
    ap = argparse.ArgumentParser(description="skill-forge quality gate for generated docs skills.")
    ap.add_argument("mode", choices=["fix", "check", "ship"])
    ap.add_argument("skill_dir")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    d = Path(a.skill_dir).expanduser().resolve()
    if not (d / "SKILL.md").is_file():
        print(f"ERROR: no SKILL.md in {d}"); sys.exit(2)
    forge = find_forge()
    if a.mode != "fix" and not forge:
        print("ERROR: skill-forge not found. Install it into ~/.claude/skills or set SKILL_FORGE_DIR."); sys.exit(2)
    if a.mode == "fix":
        d, done = do_fix(d)
        out, ok = {"skill_dir": str(d), "fixed": done}, True
    elif a.mode == "check":
        out = do_check(d, forge); ok = out["pass"]
    else:
        out, ok = do_ship(d, forge)
    print(json.dumps(out, indent=1) if a.json else json.dumps(out, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
