#!/usr/bin/env python3
"""Publish a skill to the owner's shared GitHub skills repo.

What it does, in order:
  1. Clones or updates the shared repo (from publish-config.json next to this skill).
  2. Copies the skill folder in (skips caches, .env, publish-config.json), unless --no-copy.
  3. Blocks the publish if the repo copy still contains the owner's personal details or secrets.
     Fix those lines in the REPO copy (turn them into "ask the user first" steps), then rerun with --no-copy.
  4. Adds the skill to README.md's skill table and INSTALL.md's "Extra setup" table if missing.
  5. Commits, pushes, rebuilds the upload zip, and replaces it on the latest GitHub release.

Usage:
  python publish_to_github.py <skill-dir> --summary "One line for the README" [--setup "What it needs"]
  python publish_to_github.py <skill-dir> --no-copy        # after fixing the repo copy by hand
  python publish_to_github.py <skill-dir> --dry-run        # scan and show changes, push nothing

Exit codes: 0 published (or dry run clean), 2 personal info/secrets found, 1 other error.
Needs git and the GitHub CLI (gh) signed in.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "publish-config.json"
SKIP_NAMES = {"__pycache__", ".DS_Store", ".env", "publish-config.json", ".git"}
SKIP_SUFFIXES = {".pyc"}
SECRET_PATTERNS = [
    r"gh[pousr]_[A-Za-z0-9]{20,}", r"sk-[A-Za-z0-9_-]{20,}", r"sk-ant-[A-Za-z0-9_-]{20,}",
    r"\b[0-9]{8,10}:[A-Za-z0-9_-]{35}\b", r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
]
TEXT_SUFFIXES = {".md", ".py", ".json", ".txt", ".ps1", ".sh", ".lua", ".js", ".ts", ".yaml", ".yml",
                 ".toml", ".c", ".h", ".tib", ".html", ".css", ".csv", ".xml", ".ini", ".cfg", ""}


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd)}\n{r.stdout}{r.stderr}")
    return r.stdout.strip()


def skippable(p: Path) -> bool:
    return any(part in SKIP_NAMES for part in p.parts) or p.suffix in SKIP_SUFFIXES


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def scan(folder: Path, patterns: list[str], allowed: list[str]) -> list[str]:
    hits = []
    personal = re.compile("|".join(patterns), re.I) if patterns else None
    secret = re.compile("|".join(SECRET_PATTERNS))
    for f in sorted(folder.rglob("*")):
        if not f.is_file() or skippable(f.relative_to(folder)):
            continue
        rel = f.relative_to(folder.parent).as_posix()
        if f.suffix.lower() == ".pdf":
            hits.append(f"{rel}: PDF bundled - confirm it is yours to share publicly, or remove it from the repo copy")
        if f.suffix.lower() not in TEXT_SUFFIXES:
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if secret.search(line):
                hits.append(f"{rel}:{n}: possible secret")
            elif personal and personal.search(line) and not any(a in line or a in rel for a in allowed):
                hits.append(f"{rel}:{n}: {line.strip()[:160]}")
    return hits


def add_table_row(path: Path, header_start: str, name: str, row: str, merge_marker: str | None = None) -> bool:
    """Add `name` to a Markdown table. With merge_marker, append the name to the row containing it."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        h = next(i for i, l in enumerate(lines) if l.startswith(header_start))
    except StopIteration:
        print(f"  {path.name}: table '{header_start}' not found - add {name} by hand")
        return False
    end = h + 2
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    first_cells = [l.split("|")[1] for l in lines[h + 2:end] if l.count("|") >= 2]
    if any(name in [c.strip() for c in cell.split(",")] for cell in first_cells):
        return False
    if merge_marker:
        for i in range(h + 2, end):
            if merge_marker in lines[i]:
                parts = lines[i].split("|")
                parts[1] = f" {parts[1].strip()}, {name} "
                lines[i] = "|".join(parts)
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return True
    insert_at = end
    for i in range(h + 2, end):  # keep the "Nothing extra" catch-all row last
        if "Nothing extra" in lines[i]:
            insert_at = i
            break
    lines.insert(insert_at, row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--summary", help="one line for the README table (default: first sentence of description)")
    ap.add_argument("--setup", default="Nothing extra", help="INSTALL.md 'Extra setup' text for this skill")
    ap.add_argument("--no-copy", action="store_true", help="publish the repo copy as it is (after hand fixes)")
    ap.add_argument("--dry-run", action="store_true", help="scan and edit tables locally, but do not commit or push")
    a = ap.parse_args()

    if not CONFIG.exists():
        sys.exit(f"No {CONFIG}. Ask the user which GitHub repo to publish to, then create it.")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    repo = cfg["repo"]
    clone = Path(cfg["clone_dir"]).expanduser()
    zip_dir = Path(cfg["zip_dir"]).expanduser()
    src = Path(a.skill_dir).expanduser().resolve()
    name = src.name
    if not a.no_copy and not (src / "SKILL.md").exists():
        sys.exit(f"{src} has no SKILL.md")

    # 1. clone / update
    if not (clone / ".git").exists():
        clone.parent.mkdir(parents=True, exist_ok=True)
        run(["gh", "repo", "clone", repo, str(clone)])
    run(["git", "pull", "-q", "--ff-only"], cwd=clone)
    if not run(["git", "config", "user.email"], cwd=clone, check=False):
        uid = run(["gh", "api", "user", "--jq", ".id"])
        login = run(["gh", "api", "user", "--jq", ".login"])
        run(["git", "config", "user.name", cfg.get("git_name", login)], cwd=clone)
        run(["git", "config", "user.email", f"{uid}+{login}@users.noreply.github.com"], cwd=clone)

    dest = clone / name
    if a.dry_run:  # never touch the repo: scan a temporary copy and report
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            target = dest if a.no_copy else Path(tmp) / name
            if not a.no_copy:
                shutil.copytree(src, target, ignore=lambda d, names: [n for n in names if n in SKIP_NAMES or Path(n).suffix in SKIP_SUFFIXES])
            hits = scan(target, cfg.get("personal_patterns", []), cfg.get("allowed_lines", []))
        for f, label in (("README.md", "README"), ("INSTALL.md", "INSTALL")):
            listed = re.search(rf"^\|[^|]*\b{re.escape(name)}\b", (clone / f).read_text(encoding="utf-8"), re.M)
            print(f"{label}: {'already lists' if listed else 'would add'} {name}")
        print("Dry run, nothing changed." + ("" if not hits else " Would be BLOCKED by:"))
        for h in hits:
            print("  " + h)
        sys.exit(2 if hits else 0)

    # 2. copy
    if not a.no_copy:
        if dest.exists():
            shutil.rmtree(dest)  # tracked in git; the old version stays recoverable from history
        shutil.copytree(src, dest, ignore=lambda d, names: [n for n in names if n in SKIP_NAMES or Path(n).suffix in SKIP_SUFFIXES])
        print(f"Copied {src} -> {dest}")
    if not (dest / "SKILL.md").exists():
        sys.exit(f"{dest} has no SKILL.md")

    # 3. scan
    hits = scan(dest, cfg.get("personal_patterns", []), cfg.get("allowed_lines", []))
    if hits:
        print("BLOCKED - the repo copy still has personal details, secrets, or PDFs to review:")
        for h in hits:
            print("  " + h)
        print(f"\nEdit the files under {dest} (not the live skill): replace the owner's details with a step that asks\n"
              "the user for their own (name, school, etc.) and confirms anything a profile or memory already has.\n"
              f"Then rerun: python {Path(__file__).name} {src} --no-copy")
        sys.exit(2)
    print("Scan clean: no personal details or secrets.")

    # 4. README + INSTALL
    fm = frontmatter(dest / "SKILL.md")
    summary = a.summary or re.split(r"(?<=\.)\s", fm.get("description", name))[0].rstrip(".")
    changed = []
    if add_table_row(clone / "README.md", "| Skill |", name, f"| {name} | {summary} |"):
        changed.append("README.md")
    nothing = a.setup.strip().lower().startswith("nothing extra")
    if add_table_row(clone / "INSTALL.md", "| Skill | What it needs |", name, f"| {name} | {a.setup} |",
                     merge_marker="Nothing extra" if nothing else None):
        changed.append("INSTALL.md")
    print("Updated: " + (", ".join(changed) if changed else "README/INSTALL already list this skill"))

    status = run(["git", "status", "--porcelain"], cwd=clone)
    # 5. commit, push, zip, release
    if status:
        run(["git", "add", "-A"], cwd=clone)
        run(["git", "commit", "-q", "-m", f"Add/update {name} skill\n\nCo-Authored-By: Claude <noreply@anthropic.com>"], cwd=clone)
        run(["git", "push", "-q"], cwd=clone)
        print("Pushed to GitHub.")
    else:
        print("Nothing changed in the repo; skipping commit.")

    zip_dir.mkdir(parents=True, exist_ok=True)
    zp = zip_dir / f"{name}.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(dest.rglob("*")):
            if f.is_file() and not skippable(f.relative_to(dest)):
                z.write(f, f.relative_to(clone).as_posix())
    tag = run(["gh", "release", "list", "--repo", repo, "--limit", "1", "--json", "tagName", "--jq", ".[0].tagName"], check=False)
    if not tag:
        tag = "v1.0"
        run(["gh", "release", "create", tag, "--repo", repo, "--title", "Skills", "--notes",
             "Upload-ready zips for claude.ai. See INSTALL.md."])
    run(["gh", "release", "upload", tag, str(zp), "--clobber", "--repo", repo])
    print(f"Release {tag}: uploaded {zp.name}")
    print(f"Done: https://github.com/{repo}/tree/main/{name}")


if __name__ == "__main__":
    main()
