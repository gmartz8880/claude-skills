#!/usr/bin/env python3
"""setup_env.py - check-then-install this skill's dependencies. Safe to run every time.

Usage: python setup_env.py [--check] [--json]
Edit PIP (pip name -> import name) and APPS below. Exit 0 = ready, 1 = something required is missing.
"""
import sys, json, shutil, subprocess, importlib, platform, argparse

PIP = {}            # e.g. {"python-docx": "docx", "openpyxl": "openpyxl"}
OPTIONAL_PIP = {}   # installed if possible; the skill has a fallback
APPS = {}           # e.g. {"pandoc": {"exe": "pandoc", "winget": "JohnMacFarlane.Pandoc", "brew": "pandoc", "required": False}}
status = {}


def pip_ensure(pkg, mod, check):
    try:
        importlib.import_module(mod); status[pkg] = "ok"; return True
    except ImportError:
        if check:
            status[pkg] = "missing"; return False
    base = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", pkg]
    for extra in ([], ["--user"], ["--user", "--break-system-packages"]):
        if subprocess.run(base + extra, capture_output=True).returncode == 0:
            break
    importlib.invalidate_caches()
    try:
        importlib.import_module(mod); status[pkg] = "installed"; return True
    except ImportError:
        status[pkg] = "FAILED"; return False


def app_ensure(name, spec, check):
    if shutil.which(spec["exe"]):
        status[name] = "ok"; return True
    if check:
        status[name] = "missing"; return False
    cmd = None
    if platform.system() == "Windows" and spec.get("winget") and shutil.which("winget"):
        cmd = ["winget", "install", "--id", spec["winget"], "-e", "--silent",
               "--accept-package-agreements", "--accept-source-agreements"]
    elif platform.system() == "Darwin" and spec.get("brew") and shutil.which("brew"):
        cmd = ["brew", "install", spec["brew"]]
    if cmd:
        subprocess.run(cmd, capture_output=True)
    ok = bool(shutil.which(spec["exe"]))
    status[name] = "installed" if ok else "FAILED (install manually)"
    return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    ready = sys.version_info >= (3, 8)
    status["python"] = platform.python_version()
    for p, m in PIP.items():
        ready &= pip_ensure(p, m, a.check)
    for p, m in OPTIONAL_PIP.items():
        pip_ensure(p, m, a.check)
    for n, s in APPS.items():
        ok = app_ensure(n, s, a.check)
        if s.get("required"):
            ready &= ok
    status["ready"] = bool(ready)
    print(json.dumps(status, indent=1) if a.json else "\n".join(f"{k:20} {v}" for k, v in status.items()))
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
