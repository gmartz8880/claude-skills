#!/usr/bin/env python3
"""setup_env.py - check-then-install everything the TI calculator app builder needs.

Never reinstalls something that already works. Safe to run every time (idempotent).

Usage:
  python setup_env.py                 # check + install the Python packages (tivars, lupa)
  python setup_env.py --with-c        # also download the CE C/C++ toolchain (CEdev) if missing
  python setup_env.py --check         # report only, change nothing
  python setup_env.py --json          # machine-readable status (for Claude)

What it manages:
  tivars   - TI-BASIC text -> .8xp tokenizer (TI-84 Plus CE)            [pip]
  lupa     - Lua 5.1 runtime for the Nspire desktop simulator           [pip, optional]
  CEdev    - CE C/C++ toolchain for TI-84 Plus CE C apps                [GitHub release, --with-c]
What it only detects (manual installs from TI, free):
  TI Connect CE (send files to the TI-84 Plus CE)
  TI-Nspire CX Student/Teacher Software or TI-Nspire Computer Link (send .tns files)
  CEmu (TI-84 Plus CE emulator - needs a ROM dumped from YOUR calculator)
Built in (no install): tns_builder.py makes .tns files with only the Python standard library.
"""
import sys, os, subprocess, shutil, json, platform, argparse, urllib.request, zipfile, tarfile, importlib

HOME = os.path.expanduser("~")
CEDEV_DIR = os.environ.get("CEDEV") or os.path.join(HOME, "CEdev")
status = {}


def pip_install(pkg, check_only):
    mod = {"tivars": "tivars", "lupa": "lupa"}[pkg]
    try:
        importlib.import_module(mod)
        status[pkg] = "ok"
        return True
    except ImportError:
        pass
    if check_only:
        status[pkg] = "missing"
        return False
    cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", pkg]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:                       # PEP 668 / locked environments
        r = subprocess.run(cmd + ["--user"], capture_output=True, text=True)
    if r.returncode != 0:
        r = subprocess.run(cmd + ["--user", "--break-system-packages"], capture_output=True, text=True)
    try:
        importlib.invalidate_caches(); importlib.import_module(mod)
        status[pkg] = "installed"
        return True
    except ImportError:
        status[pkg] = "FAILED: " + (r.stderr.strip().splitlines() or ["pip error"])[-1][:160]
        return False


def find_cedev():
    for cand in [shutil.which("cedev-config"), os.path.join(CEDEV_DIR, "bin", "cedev-config"),
                 os.path.join(CEDEV_DIR, "bin", "cedev-config.exe"), r"C:\CEdev\bin\cedev-config.exe"]:
        if cand and os.path.exists(cand):
            return os.path.dirname(os.path.dirname(cand))
    return None


def install_cedev(check_only):
    root = find_cedev()
    if root:
        status["CEdev"] = "ok: " + root
        return root
    if check_only:
        status["CEdev"] = "missing"
        return None
    sysname = platform.system()
    asset = {"Windows": "CEdev-Windows.zip", "Linux": "CEdev-Linux.tar.gz"}.get(sysname)
    if sysname == "Darwin":
        status["CEdev"] = ("manual: download CEdev-macOS-arm.dmg (Apple silicon) or CEdev-macOS-intel.dmg from "
                           "https://github.com/CE-Programming/toolchain/releases/latest and copy CEdev to ~/CEdev")
        return None
    url = "https://github.com/CE-Programming/toolchain/releases/latest/download/" + asset
    dest = os.path.join(HOME, asset)
    try:
        print("Downloading", url, "(~40 MB)...")
        urllib.request.urlretrieve(url, dest)
        if asset.endswith(".zip"):
            zipfile.ZipFile(dest).extractall(HOME)
        else:
            with tarfile.open(dest) as t:
                t.extractall(HOME)
        os.remove(dest)
    except Exception as e:
        status["CEdev"] = f"FAILED download/extract: {e}"
        return None
    root = find_cedev()
    status["CEdev"] = ("installed: " + root) if root else "FAILED: extracted but cedev-config not found"
    if root and sysname == "Windows":
        status["CEdev_note"] = "Build from the CEdev folder's cedev.bat window, or let build.py set PATH for you."
    return root


def detect_apps():
    pf = [os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]
    found = {}
    checks = {
        "TI Connect CE": [os.path.join(p, "TI Education", "TI Connect CE", "TI Connect CE.exe") for p in pf]
                         + ["/Applications/TI Connect CE.app"],
        "TI-Nspire software": [os.path.join(p, "TI Education", d) for p in pf for d in
                               ("TI-Nspire CX Student Software", "TI-Nspire CX Premium Teacher Software",
                                "TI-Nspire CX CAS Student Software", "TI-Nspire CX CAS Premium Teacher Software",
                                "TI-Nspire Computer Link")]
                              + ["/Applications/TI-Nspire CX Student Software.app", "/Applications/TI-Nspire Computer Link.app"],
        "CEmu": [shutil.which("CEmu") or "", shutil.which("cemu") or "", os.path.join(HOME, "CEmu", "CEmu.exe")],
        "TiLP (Linux transfer)": [shutil.which("tilp") or ""],
    }
    for name, paths in checks.items():
        hit = next((p for p in paths if p and os.path.exists(p)), None)
        found[name] = hit or "not found"
    status["apps"] = found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-c", action="store_true")
    ap.add_argument("--no-sim", action="store_true", help="skip the optional lupa simulator package")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    status["python"] = platform.python_version() + (" ok" if sys.version_info >= (3, 8) else " TOO OLD (need 3.8+)")
    status["os"] = platform.system() + " " + platform.release()
    pip_install("tivars", a.check)
    if not a.no_sim:
        pip_install("lupa", a.check)
    if a.with_c:
        install_cedev(a.check)
    else:
        r = find_cedev(); status["CEdev"] = ("ok: " + r) if r else "not installed (only needed for C apps: --with-c)"
    status["tns_builder"] = "ok (built in, standard library only)"
    detect_apps()
    if a.json:
        print(json.dumps(status, indent=1)); return
    print("TI app builder environment")
    for k, v in status.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                print(f"  {k2:28} {v2}")
        else:
            print(f"  {k:28} {v}")
    if any(isinstance(v, str) and v.startswith("FAILED") for v in status.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
