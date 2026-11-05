#!/usr/bin/env python3
"""validate_skill.py - check a skill folder (or .zip) against the Agent Skills spec, Claude upload rules,
and plug-and-play quality rules.

Usage:
  python validate_skill.py SKILL_DIR_OR_ZIP [--profile portable|claude-code] [--json]

Profiles:
  portable    (default) Claude.ai upload + Skills API + Claude Code: only name, description, license,
              compatibility, metadata, allowed-tools; description <= 200 chars.
  claude-code all Claude Code fields allowed; description + when_to_use <= 1536 chars.
Exit: 0 = no errors (warnings allowed), 1 = errors.
"""
import sys, os, re, json, argparse, zipfile, tempfile, py_compile, shutil

PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CC_KEYS = PORTABLE_KEYS | {"when_to_use", "argument-hint", "arguments", "disable-model-invocation",
                           "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
                           "background", "hooks", "paths", "shell", "version"}
HOST_SPECIFIC = ["search_web", "fetch_url", "share_file", "request_user_input", "load_skill",
                 "browser_task", "memory_search", "deploy_website", "spawn_agent"]
SECRET_PAT = re.compile(r"(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[bp]-[A-Za-z0-9-]{20,}|"
                        r"AIza[0-9A-Za-z_\-]{30,}|-----BEGIN (RSA |EC )?PRIVATE KEY-----)")
USER_PATH = re.compile(r"(C:\\Users\\(?!<|\{|%|USERNAME|YourName|you)[A-Za-z0-9._-]+|/home/(?!user/workspace|<)[a-z0-9._-]+/|/Users/(?!<|you)[A-Za-z0-9._-]+/)")
JUNK = {"__pycache__", ".DS_Store", ".git", "Thumbs.db", ".ipynb_checkpoints", "node_modules", ".venv", "venv"}

out = []


def rep(level, msg, fix=""):
    out.append({"level": level, "message": msg, "fix": fix})


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not m:
        return None, text
    raw, body = m.group(1), text[m.end():]
    try:
        import yaml  # optional
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict):
            raise ValueError
        return data, body
    except Exception:
        pass
    data, cur = {}, None
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^\S[^:]*:", line):
            k, _, v = line.partition(":")
            v = v.strip()
            if v.startswith(("'", '"')) and v.endswith(v[0]) and len(v) > 1:
                v = v[1:-1]
            data[k.strip()] = v if v else {}
            cur = k.strip()
        elif cur is not None and isinstance(data.get(cur), dict):
            k, _, v = line.strip().partition(":")
            data[cur][k.strip()] = v.strip().strip('"\'')
        elif cur is not None and isinstance(data.get(cur), str):
            data[cur] += " " + line.strip()
    return data, body


def validate(root, profile):
    folder = os.path.basename(os.path.abspath(root))
    skill_md = None
    for cand in ("SKILL.md", "skill.md", "Skill.md"):
        if os.path.exists(os.path.join(root, cand)):
            skill_md = os.path.join(root, cand); break
    if not skill_md:
        rep("ERROR", "No SKILL.md at the top of the skill folder.", "Create SKILL.md with YAML frontmatter.")
        return
    if os.path.basename(skill_md) != "SKILL.md":
        rep("WARN", f"File is named {os.path.basename(skill_md)}.", "Rename to SKILL.md (works everywhere).")
    text = open(skill_md, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    if fm is None:
        rep("ERROR", "SKILL.md does not start with a --- YAML frontmatter block.", "Add ---\\nname: ...\\ndescription: ...\\n---")
        return
    allowed = PORTABLE_KEYS if profile == "portable" else CC_KEYS
    for k in fm:
        if k not in allowed:
            lvl = "ERROR" if profile == "portable" else "WARN"
            rep(lvl, f"Frontmatter key '{k}' is not allowed in the {profile} profile.",
                "Move it under metadata: (portable) or use --profile claude-code for Claude Code-only skills.")
    name = str(fm.get("name", "")).strip()
    if not name:
        rep("ERROR", "Missing name.", "Add name: my-skill (matches the folder).")
    else:
        if len(name) > 64: rep("ERROR", f"name is {len(name)} chars (max 64).", "Shorten it.")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            rep("ERROR", f"name '{name}' must be lowercase letters/digits with single hyphens.", "e.g. my-skill-name")
        if re.search(r"anthropic|claude", name):
            rep("ERROR", "name contains a reserved word (claude/anthropic).", "Pick another name.")
        if name != folder and not folder.startswith("tmp"):
            rep("ERROR", f"name '{name}' does not match folder '{folder}'.", "Rename the folder or the name.")
    desc = fm.get("description", "")
    desc = desc if isinstance(desc, str) else str(desc)
    desc = " ".join(desc.split())
    if not desc:
        rep("ERROR", "Missing description.", "Say what it does and when to use it.")
    else:
        lim = 200 if profile == "portable" else 1024
        if len(desc) > 1024:
            rep("ERROR", f"description is {len(desc)} chars (spec max 1024).", "Shorten it.")
        elif len(desc) > lim:
            rep("ERROR", f"description is {len(desc)} chars; Claude.ai uploads allow 200.", "Shorten to <= 200 chars; put triggers first.")
        if "<" in desc or ">" in desc:
            rep("ERROR", "description contains < or >.", "Remove angle brackets.")
        if len(desc) < 40:
            rep("WARN", "description is very short; the skill may not trigger.", "Name the task, file types, and trigger words.")
        if profile == "claude-code" and isinstance(fm.get("when_to_use"), str) and len(desc) + len(fm["when_to_use"]) > 1536:
            rep("ERROR", "description + when_to_use exceed 1,536 chars.", "Trim.")
    comp = fm.get("compatibility")
    if isinstance(comp, str) and len(comp) > 500:
        rep("ERROR", "compatibility longer than 500 chars.", "Shorten.")
    if "metadata" in fm and not isinstance(fm["metadata"], dict):
        rep("ERROR", "metadata must be a key: value map.", "metadata:\\n  version: \"1.0\"")

    lines = body.count("\n") + 1
    if lines > 500:
        rep("ERROR", f"SKILL.md body is {lines} lines (keep < 500).", "Move details to references/.")
    elif lines > 300:
        rep("WARN", f"SKILL.md body is {lines} lines (ideal < 300).", "Move lookups/examples to references/.")
    if not re.search(r"(?im)^#+\s.*(workflow|steps|how to|process)", body) and not re.search(r"(?m)^\s*1\.\s", body):
        rep("WARN", "No numbered workflow found.", "Add a numbered Workflow section.")

    # referenced files exist
    for ref in sorted(set(re.findall(r"(?<![\w/.-])((?:scripts|references|templates|assets|evals|examples)/[\w./-]+)", text))):
        ref = ref.rstrip(".,)`")
        if any(ch in ref for ch in "<>*{}") or ref.endswith("/"):
            continue
        if not os.path.exists(os.path.join(root, ref)):
            rep("ERROR", f"SKILL.md mentions '{ref}' but it does not exist.", "Add the file or fix the path.")
    for h in HOST_SPECIFIC:
        if re.search(r"\b%s\b" % h, text):
            rep("WARN", f"Host-specific tool name '{h}' in SKILL.md.", "Use neutral wording (e.g. 'search the web').")

    total = 0
    for dp, dns, fns in os.walk(root):
        for d in list(dns):
            if d in JUNK:
                rep("WARN", f"Junk folder in skill: {os.path.relpath(os.path.join(dp, d), root)}", "Delete it (package_skill.py skips it).")
        for fn in fns:
            p = os.path.join(dp, fn); rel = os.path.relpath(p, root)
            if any(part in JUNK for part in rel.split(os.sep)):
                continue
            total += os.path.getsize(p)
            if fn in JUNK or fn.endswith((".pyc", ".pyo")):
                rep("WARN", f"Junk file: {rel}", "Delete it.")
                continue
            if fn == ".env" or fn.endswith((".pem", ".key")):
                rep("ERROR", f"Possible secret file bundled: {rel}", "Remove it; use environment variables.")
            if os.path.getsize(p) < 2_000_000 and fn.endswith((".md", ".py", ".txt", ".json", ".yaml", ".yml", ".ps1", ".sh", ".js", ".ts", ".lua", ".c", ".h", ".html", ".csv")):
                s = open(p, encoding="utf-8", errors="replace").read()
                if SECRET_PAT.search(s):
                    rep("ERROR", f"Possible API key/secret in {rel}.", "Remove it; read from an environment variable.")
                m = USER_PATH.search(s)
                if m:
                    rep("WARN", f"Hard-coded user path in {rel}: {m.group(0)}", "Use ~, %USERPROFILE%, or paths relative to the skill.")
            if fn.endswith(".py"):
                try:
                    py_compile.compile(p, doraise=True, cfile=os.path.join(tempfile.gettempdir(), "vs_check.pyc"))
                except py_compile.PyCompileError as e:
                    rep("ERROR", f"Python syntax error in {rel}: {str(e).splitlines()[-1][:150]}", "Fix the script.")
            if fn.endswith(".sh"):
                if not open(p, "rb").read(2) == b"#!":
                    rep("WARN", f"{rel} has no #! line.", "Start with #!/usr/bin/env bash")
            if rel.startswith("references") and fn.endswith(".md"):
                n = open(p, encoding="utf-8", errors="replace").read().count("\n")
                if n > 300 and not re.search(r"(?i)contents", open(p, encoding="utf-8", errors="replace").read()[:1500]):
                    rep("TIP", f"{rel} is {n} lines with no table of contents.", "Add a short contents list at the top.")
    sh_only = [f for f in os.listdir(os.path.join(root, "scripts"))] if os.path.isdir(os.path.join(root, "scripts")) else []
    if sh_only and all(f.endswith(".sh") for f in sh_only):
        rep("WARN", "Scripts are bash-only; Windows users cannot run them without WSL/Git Bash.", "Use Python scripts (cross-platform).")
    if total > 30 * 1024 * 1024:
        rep("WARN", f"Skill is {total/1048576:.1f} MB.", "Keep uploads small; download large assets at run time.")
    if not os.path.exists(os.path.join(root, "evals")):
        rep("TIP", "No evals/ folder.", "Add evals/evals.json with trigger and non-trigger prompts.")
    return {"name": name, "description_chars": len(desc), "body_lines": lines, "bytes": total}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--profile", choices=["portable", "claude-code"], default="portable")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    path, tmp = a.path, None
    if path.lower().endswith(".zip"):
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            tops = {n.split("/")[0] for n in names if n.strip("/")}
            if len(tops) != 1 or not any(n.count("/") >= 1 for n in names):
                rep("ERROR", "Zip must contain exactly one skill folder at its root.", "Zip the folder itself, not its contents.")
            z.extractall(tmp)
        path = os.path.join(tmp, sorted(tops)[0]) if tops else tmp
    info = validate(path, a.profile) or {}
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    errors = sum(o["level"] == "ERROR" for o in out)
    if a.json:
        print(json.dumps({"info": info, "findings": out, "errors": errors}, indent=1))
    else:
        print(f"validate_skill [{a.profile}] {a.path}")
        if info:
            print(f"  name={info.get('name')}  description={info.get('description_chars')} chars  body={info.get('body_lines')} lines  size={info.get('bytes',0)/1024:.0f} KB")
        for o in out:
            print(f"  {o['level']:5} {o['message']}" + (f"\n        fix: {o['fix']}" if o["fix"] else ""))
        print("  RESULT:", "PASS" if not errors else f"FAIL ({errors} error(s))")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
