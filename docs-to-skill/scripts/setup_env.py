#!/usr/bin/env python3
"""setup_env.py - check-then-install what docs-to-skill needs. Safe to run every time.

Usage: python setup_env.py [--check] [--json]

Checks:
  skill-seekers  the Skill Seekers CLI (scrapes docs sites into skill folders)
  skill-forge    the skill-forge skill (its validate/package/install scripts are the quality gate)
Installs skill-seekers if missing: `uv tool install` when uv exists, else `pip install --user`.
On Windows, when this process runs inside a packaged (MSIX) app such as the Claude desktop app,
installs into AppData are redirected to the app's private storage. In that case the install is run
once through a temporary Task Scheduler task (outside the package), then the task is deleted.
Exit 0 = ready, 1 = something required is missing.
"""
import argparse, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path

status = {}


def find_forge():
    """Return the skill-forge folder (contains scripts/validate_skill.py) or None."""
    env = os.environ.get("SKILL_FORGE_DIR")
    cands = [Path(env)] if env else []
    home = Path.home() / ".claude"
    cands.append(home / "skills" / "skill-forge")
    plug = home / "plugins"
    if plug.is_dir():
        cands += [p.parent.parent for p in plug.glob("**/skill-forge/scripts/validate_skill.py")]
    for c in cands:
        if (c / "scripts" / "validate_skill.py").is_file():
            return c
    return None


def seekers_version():
    exe = shutil.which("skill-seekers")
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip() or "unknown"
    except Exception:
        return None


def in_msix_package():
    """True when this process runs inside a packaged Windows app (MSIX)."""
    if platform.system() != "Windows":
        return False
    try:
        import ctypes
        n = ctypes.c_uint32(0)
        rc = ctypes.windll.kernel32.GetCurrentPackageFullName(ctypes.byref(n), None)
        return rc == 122  # ERROR_INSUFFICIENT_BUFFER means the process has a package identity
    except Exception:
        return False


def install_cmd():
    if shutil.which("uv"):
        return [shutil.which("uv"), "tool", "install", "--force", "skill-seekers[mcp]"]
    return [sys.executable, "-m", "pip", "install", "--user", "--quiet", "skill-seekers[mcp]"]


def install_outside_package(cmd):
    """Run cmd once through a scheduled task so files land in the real AppData, then remove the task."""
    work = Path.home() / ".docs-to-skill-install"
    work.mkdir(exist_ok=True)
    log, bat = work / "install.log", work / "install.cmd"
    if log.exists():
        log.unlink()
    bat.write_text("@echo off\r\nset UV_HTTP_TIMEOUT=300\r\n"
                   f"{subprocess.list2cmdline(cmd)} > \"{log}\" 2>&1\r\n"
                   f"echo EXIT=%ERRORLEVEL% >> \"{log}\"\r\n", encoding="utf-8")
    ps = ("$a=New-ScheduledTaskAction -Execute '%s';"
          "$s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries "
          "-ExecutionTimeLimit (New-TimeSpan -Minutes 30);"
          "Register-ScheduledTask -TaskName DocsToSkillInstall -Action $a -Settings $s -Force | Out-Null;"
          "Start-ScheduledTask DocsToSkillInstall" % str(bat))
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
    for _ in range(360):  # wait up to 30 minutes
        if log.exists() and "EXIT=" in log.read_text(errors="ignore"):
            break
        time.sleep(5)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Unregister-ScheduledTask DocsToSkillInstall -Confirm:$false"], capture_output=True)
    return log.read_text(errors="ignore") if log.exists() else "no install log was written"


def main():
    ap = argparse.ArgumentParser(description="Check-then-install for docs-to-skill.")
    ap.add_argument("--check", action="store_true", help="only report, install nothing")
    ap.add_argument("--json", action="store_true", help="print JSON")
    a = ap.parse_args()
    status["python"] = platform.python_version()
    ready = True

    v = seekers_version()
    if v:
        status["skill-seekers"] = f"ok ({v})"
    elif a.check:
        status["skill-seekers"] = "missing"
        ready = False
    else:
        cmd = install_cmd()
        os.environ.setdefault("UV_HTTP_TIMEOUT", "300")
        if in_msix_package():
            status["install-route"] = "outside the app package (one-shot scheduled task)"
            out = install_outside_package(cmd)
        else:
            status["install-route"] = "direct"
            r = subprocess.run(cmd, capture_output=True, text=True)
            out = r.stdout + r.stderr
        v = seekers_version()
        status["skill-seekers"] = f"installed ({v})" if v else "FAILED: " + out.strip()[-400:]
        ready &= bool(v)

    forge = find_forge()
    status["skill-forge"] = str(forge) if forge else "MISSING - install the skill-forge skill into ~/.claude/skills"
    ready &= bool(forge)
    status["ready"] = bool(ready)
    print(json.dumps(status, indent=1) if a.json else "\n".join(f"{k:16} {v}" for k, v in status.items()))
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
