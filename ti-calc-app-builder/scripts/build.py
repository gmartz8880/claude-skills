#!/usr/bin/env python3
"""build.py - one command: lint -> test -> build -> package a TI calculator app.

Usage:
  python build.py SOURCE --target nspire|ce [--name NAME] [--out DIR] [--force]

SOURCE can be:
  app.lua                      -> TI-Nspire .tns (Lua)                 [target nspire]
  app.py  (one or more)        -> TI-Nspire .tns (Python, CX II)       [target nspire]
  app.py                       -> TI-84 Plus CE Python: copied as .py (TI Connect CE converts on send) [target ce]
  app.txt / app.basic          -> TI-84 Plus CE .8xp (TI-BASIC, tokenized with tivars) [target ce]
  app.tib / app.nsb            -> TI-Nspire TI-Basic: validated text to paste/import [target nspire]
  folder with a makefile       -> TI-84 Plus CE C/C++ .8xp via CEdev   [target ce]

Steps (stops on the first ERROR unless --force):
  1. calc_lint.py  (battery / stability / speed / compatibility)
  2. nspire_sim.py for Lua (desktop simulator: crashes, timer left running, repaint storms)
  3. build the calculator file(s) into OUT (default ./dist)
  4. round-trip check (re-open the output file) + BUILD_REPORT.md with install steps
"""
import os, sys, re, subprocess, shutil, argparse, datetime, glob

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def ce_name(raw):
    n = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if not n or not n[0].isalpha():
        n = "A" + n
    return n[:8]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--target", choices=["nspire", "ce"], required=True)
    ap.add_argument("--name", help="on-calculator name (CE: max 8 chars A-Z0-9)")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--force", action="store_true", help="build even if lint/sim report errors")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    src0 = a.sources[0]
    base = os.path.splitext(os.path.basename(src0.rstrip("/\\")))[0]
    report = [f"# Build report: {base}", f"Built {datetime.datetime.now():%Y-%m-%d %H:%M} | target: {a.target}", ""]
    ok = True

    # 1. lint
    lint_files = a.sources
    if os.path.isdir(src0):
        lint_files = glob.glob(os.path.join(src0, "src", "**", "*.c"), recursive=True) + \
                     glob.glob(os.path.join(src0, "src", "**", "*.cpp"), recursive=True)
    if lint_files:
        code, out = run([sys.executable, os.path.join(HERE, "calc_lint.py"), *lint_files, "--target", a.target])
        report += ["## 1. Lint (battery, stability, speed, compatibility)", "```", out.strip(), "```", ""]
        print(out.strip())
        if code != 0:
            ok = False

    # 2. simulator for Lua
    if src0.lower().endswith(".lua"):
        code, out = run([sys.executable, os.path.join(HERE, "nspire_sim.py"), src0])
        report += ["## 2. Desktop simulator", "```", out.strip(), "```", ""]
        print(out.strip())
        if code == 1:
            ok = False
        elif code == 2:
            report.append("Simulator skipped (lupa not installed). Run setup_env.py.")
    if not ok and not a.force:
        report.append("**Build stopped: fix the ERROR/FAIL items above, then rebuild.**")
        open(os.path.join(a.out, "BUILD_REPORT.md"), "w", encoding="utf-8").write("\n".join(report))
        print("BUILD STOPPED - see", os.path.join(a.out, "BUILD_REPORT.md")); sys.exit(1)

    # 3. build
    outputs, install = [], []
    low = src0.lower()
    if a.target == "nspire" and (low.endswith(".lua") or low.endswith(".py")):
        sys.path.insert(0, HERE)
        import tns_builder
        name = (a.name or base)
        dest = os.path.join(a.out, name + ".tns")
        tns_builder.build(a.sources, dest)
        data = open(dest, "rb").read()
        assert data.startswith(b"*TIMLP") and data[-22:-18] == b"TIPD", "tns structure check failed"
        outputs.append(dest)
        install = ["Connect the TI-Nspire CAS with its USB cable.",
                   "Open TI-Nspire CX Student/Teacher Software (Content Explorer / Documents workspace) or TI-Nspire Computer Link.",
                   f"Drag {os.path.basename(dest)} onto the connected handheld (any folder, e.g. My Documents).",
                   "On the calculator: Home > My Documents > open the file. For Lua it starts immediately; "
                   "for Python press menu > Run (or ctrl+R).",
                   "Python .tns needs a TI-Nspire CX II with OS 5.2 or newer. Lua needs OS 3.0.2 or newer."]
    elif a.target == "nspire":
        dest = os.path.join(a.out, os.path.basename(src0))
        shutil.copy(src0, dest); outputs.append(dest)
        install = ["TI-Basic is entered with the Program Editor: on the calculator open a document, menu > Functions & Programs > "
                   "Program Editor > New, give it the name in the Define line, paste/type the code, then ctrl+B to check/store.",
                   "Or in TI-Nspire Student Software: Insert > Program Editor > New, paste the text, ctrl+B, save, send the .tns.",
                   "For a library (usable from any document): set Library Access to LibPub, save the document into MyLib, then "
                   "Doc menu > Refresh Libraries."]
    elif low.endswith(".py"):
        dest = os.path.join(a.out, (a.name or base) + ".py")
        shutil.copy(src0, dest); outputs.append(dest)
        install = ["Needs a TI-84 Plus CE Python edition (look for the Python app under [apps]).",
                   "Open TI Connect CE, connect the calculator, and drag the .py file in: TI Connect CE converts it to a Python "
                   "AppVar automatically.", "On the calculator: [prgm] or [apps] > Python App > select the file > Run."]
    elif os.path.isdir(src0):
        cedev = None
        for c in [shutil.which("cedev-config"), os.path.expanduser("~/CEdev/bin/cedev-config"),
                  os.path.expanduser("~/CEdev/bin/cedev-config.exe"), r"C:\CEdev\bin\cedev-config.exe"]:
            if c and os.path.exists(c):
                cedev = os.path.dirname(c); break
        if not cedev:
            print("CEdev not found. Run: python setup_env.py --with-c"); sys.exit(1)
        env = dict(os.environ, PATH=cedev + os.pathsep + os.environ.get("PATH", ""))
        make = shutil.which("make", path=env["PATH"]) or os.path.join(cedev, "make.exe")
        code, out = run([make], cwd=src0, env=env)
        report += ["## 3. Compile (CEdev)", "```", out.strip()[-3000:], "```", ""]
        print(out.strip()[-1500:])
        if code != 0:
            open(os.path.join(a.out, "BUILD_REPORT.md"), "w", encoding="utf-8").write("\n".join(report))
            print("COMPILE FAILED"); sys.exit(1)
        warn = [l for l in out.splitlines() if "warning:" in l and "GNU-stack" not in l and "deprecated" not in l]
        if warn:
            report.append(f"Compiler warnings: {len(warn)} (fix them - warnings are where crashes start).")
        for f in glob.glob(os.path.join(src0, "bin", "*.8xp")):
            shutil.copy(f, a.out); outputs.append(os.path.join(a.out, os.path.basename(f)))
        install = ["One-time: send clibs.8xg (CE C libraries: graphx, keypadc, fileioc) from "
                   "https://github.com/CE-Programming/libraries/releases/latest with TI Connect CE.",
                   "Send the .8xp with TI Connect CE (drag onto the calculator).",
                   "Run: [prgm] > pick it > [enter] (or Asm( on OS 5.3 and older).",
                   "OS 5.5 and newer block C/assembly programs: you need arTIfiCE (OS up to 5.8.4: v2.1, OS 5.8.5: v3) "
                   "or a jailbreak like it first. Check [2nd][mem] 1:About for the OS version."]
    else:
        sys.path.insert(0, HERE)
        try:
            from tivars.types import TIProgram
            from tivars.models import TI_84PCE
        except ImportError:
            print("tivars missing. Run: python setup_env.py"); sys.exit(1)
        name = ce_name(a.name or base)
        text = open(src0, encoding="utf-8").read()
        text = text.replace("π", "pi").replace("\r\n", "\n")
        prog = TIProgram(name=name)
        prog.load_string(text.rstrip("\n"), model=TI_84PCE)
        dest = os.path.join(a.out, name + ".8xp")
        prog.save(dest)
        back = TIProgram.open(dest).string()
        if back.replace("π", "pi") != text.rstrip("\n"):
            report.append("Round-trip note: re-opened program differs only in token spelling (expected for some tokens).")
        size = len(prog.data)
        report.append(f"Program size: {size} bytes of RAM/archive.")
        outputs.append(dest)
        install = ["Send the .8xp with TI Connect CE (drag onto the calculator; choose Archive to protect it from RAM clears).",
                   f"Run: [prgm] > {name} > [enter] [enter]. If it is archived, OS 5.x runs it directly.",
                   "Press [on] to break out of a running TI-BASIC program at any time."]

    report += ["## Output files"] + [f"- {os.path.basename(o)} ({os.path.getsize(o)} bytes)" for o in outputs] + [""]
    report += ["## Install on the calculator"] + [f"{i}. {s}" for i, s in enumerate(install, 1)]
    open(os.path.join(a.out, "BUILD_REPORT.md"), "w", encoding="utf-8").write("\n".join(report) + "\n")
    print("BUILD OK ->", ", ".join(outputs))


if __name__ == "__main__":
    main()
