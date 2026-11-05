#!/usr/bin/env python3
"""setup_env.py - check-then-install everything needed to BUILD skills (and a target skill's own deps).

Runs automatically (no questions). Installs only what is missing. Safe to repeat.

Usage:
  python setup_env.py                      # Skill Forge's own tools
  python setup_env.py --for SKILL_DIR      # plus the target skill's dependencies:
                                           #   SKILL_DIR/requirements.txt (pip) and
                                           #   metadata.dependencies entries marked "(pip)" or "(winget:Id)"/"(brew:name)"
  python setup_env.py --check              # report only
  python setup_env.py --json               # machine-readable

Skill Forge tools:
  required: Python 3.8+ (standard library covers validate/package/install/init)
  optional, auto-installed: pyyaml (exact YAML parsing), python-docx (technical guides in Word)
  detected: pandoc (Markdown -> Word), git, winget/brew (desktop app installs)
"""
import sys, os, re, json, shutil, subprocess, importlib, argparse, platform

status = {}


def pip_ensure(pkg, module, check):
    try:
        importlib.import_module(module); status[pkg] = "ok"; return True
    except ImportError:
        pass
    if check:
        status[pkg] = "missing"; return False
    base = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", pkg]
    err = ""
    for extra in ([], ["--user"], ["--user", "--break-system-packages"]):
        r = subprocess.run(base + extra, capture_output=True, text=True)
        if r.returncode == 0:
            break
        err = (r.stderr or "").strip().splitlines()[-1:] or ["pip failed"]
        err = err[0]
    importlib.invalidate_caches()
    try:
        importlib.import_module(module); status[pkg] = "installed"; return True
    except ImportError:
        status[pkg] = f"FAILED ({err[:120]}) - optional, continuing"; return False


def app_ensure(label, exe, winget_id=None, brew=None, check=False):
    hit = shutil.which(exe)
    if hit:
        status[label] = "ok: " + hit; return True
    if check:
        status[label] = "missing"; return False
    sysname = platform.system()
    cmd = None
    if sysname == "Windows" and winget_id and shutil.which("winget"):
        cmd = ["winget", "install", "--id", winget_id, "-e", "--silent",
               "--accept-package-agreements", "--accept-source-agreements"]
    elif sysname == "Darwin" and brew and shutil.which("brew"):
        cmd = ["brew", "install", brew]
    if not cmd:
        status[label] = "not installed (optional; no package manager available)"; return False
    r = subprocess.run(cmd, capture_output=True, text=True)
    status[label] = "installed" if r.returncode == 0 else f"FAILED to install ({r.returncode}) - optional"
    return r.returncode == 0


PIP_MODULE = {"pyyaml": "yaml", "python-docx": "docx", "pillow": "PIL", "beautifulsoup4": "bs4",
              "opencv-python": "cv2", "scikit-learn": "sklearn", "pymupdf": "fitz"}


def target_deps(skill_dir, check):
    req = os.path.join(skill_dir, "requirements.txt")
    pkgs = []
    if os.path.exists(req):
        for line in open(req, encoding="utf-8"):
            line = line.split("#")[0].strip()
            if line:
                pkgs.append(line)
    md = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(md):
        t = open(md, encoding="utf-8").read()
        m = re.search(r"(?m)^\s+dependencies:\s*(.+)$", t)
        if m:
            for item in m.group(1).split(","):
                item = item.strip()
                pm = re.match(r"([A-Za-z0-9_.\-]+)[^()]*\((pip)[^)]*\)", item)
                wm = re.match(r"([A-Za-z0-9_.\- ]+?)\s*\(winget:([^)]+)\)", item)
                bm = re.match(r"([A-Za-z0-9_.\- ]+?)\s*\(brew:([^)]+)\)", item)
                if pm:
                    pkgs.append(pm.group(1))
                elif wm:
                    app_ensure(wm.group(1).strip(), wm.group(1).strip().lower(), winget_id=wm.group(2).strip(), check=check)
                elif bm:
                    app_ensure(bm.group(1).strip(), bm.group(1).strip().lower(), brew=bm.group(2).strip(), check=check)
    for p in pkgs:
        name = re.split(r"[<>=!~\[ ]", p)[0]
        pip_ensure(p, PIP_MODULE.get(name.lower(), name.replace("-", "_")), check)
    setup = os.path.join(skill_dir, "scripts", "setup_env.py")
    if os.path.exists(setup) and os.path.abspath(setup) != os.path.abspath(__file__):
        r = subprocess.run([sys.executable, setup] + (["--check"] if check else []), capture_output=True, text=True)
        status["target setup_env.py"] = "ok" if r.returncode == 0 else "reported problems (see its output)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--for", dest="target")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    ok = sys.version_info >= (3, 8)
    status["python"] = platform.python_version() + (" ok" if ok else " TOO OLD - install 3.12: winget install -e --id Python.Python.3.12")
    status["os"] = f"{platform.system()} {platform.release()}"
    pip_ensure("pyyaml", "yaml", a.check)
    pip_ensure("python-docx", "docx", a.check)
    app_ensure("pandoc", "pandoc", winget_id="JohnMacFarlane.Pandoc", brew="pandoc", check=a.check)
    status["git"] = "ok" if shutil.which("git") else "not found (optional)"
    if a.target:
        target_deps(a.target, a.check)
    if a.json:
        print(json.dumps(status, indent=1))
    else:
        print("Skill Forge environment")
        for k, v in status.items():
            print(f"  {k:24} {v}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
