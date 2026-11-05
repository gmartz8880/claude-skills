# Script patterns (copy these)

## Rules
- Python 3.8+, standard library first. One job per script. `argparse` with `--help` text that explains usage.
- Idempotent: running twice is safe. `--check` = report only. `--json` = machine-readable output for Claude.
- Exit codes: 0 ok, 1 problem found / failed, 2 cannot run (missing dependency) - and print how to fix it.
- Paths: `pathlib`/`os.path`, relative to the script (`Path(__file__).parent`), never hard-coded user folders.
- Windows safe: no `rm -rf`/bash-only syntax inside Python; quote paths with spaces; UTF-8 file I/O
  (`encoding="utf-8"`); call `sys.executable` (not `python3`) for sub-processes.
- Network: timeouts, 3 retries with backoff, and an offline fallback or clear message.
- Never print or store secrets. Read keys from environment variables.

## Check-then-install (Python package)
```python
import importlib, subprocess, sys
def ensure(pkg, module=None):
    module = module or pkg
    try:
        return importlib.import_module(module)
    except ImportError:
        pass
    base = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", pkg]
    for extra in ([], ["--user"], ["--user", "--break-system-packages"]):
        if subprocess.run(base + extra, capture_output=True).returncode == 0:
            break
    importlib.invalidate_caches()
    return importlib.import_module(module)   # raises with a clear error if still missing
```

## Check-then-install (desktop app, Windows)
```python
import shutil, subprocess, os
def ensure_app(exe_name, winget_id, known_paths):
    hit = shutil.which(exe_name) or next((p for p in known_paths if os.path.exists(p)), None)
    if hit:
        return hit
    r = subprocess.run(["winget", "install", "--id", winget_id, "-e", "--silent",
                        "--accept-package-agreements", "--accept-source-agreements"], capture_output=True, text=True)
    return shutil.which(exe_name) or next((p for p in known_paths if os.path.exists(p)), None)
```

## Status report for Claude
```python
import json; print(json.dumps({"python": "ok", "tivars": "installed", "app": "not found"}, indent=1))
```

## Office outputs
Word: `python-docx` (or `pandoc` when present). Excel: `openpyxl`. PDF: `reportlab` or Word -> PDF.
Always re-open the generated file to verify it is valid before delivery.
