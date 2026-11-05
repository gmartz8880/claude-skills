# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| CE: "ERR:INVALID" / program won't run (C) | OS 5.5+ blocks native code | arTIfiCE for the user's OS (v2.1 up to 5.8.4, v3 for 5.8.5 only; v3 installs the AsmHook2 app - after any RAM reset, open AsmHook2 once), or rebuild in TI-BASIC |
| CE: "Need libLoad" / missing library | clibs.8xg not sent | Send clibs.8xg from CE-Programming/libraries |
| CE: ERR:MEMORY after a while | Goto out of an If-Then/loop block | Restructure (lint flags it) |
| CE: program vanished | RAM reset; not archived | Send as Archive |
| CE: Python file not listed | Not a Python edition, or sent as raw file | Check [apps] for Python App; send via TI Connect CE |
| Nspire: Lua page blank | runtime error before first paint, or OS < 3.0.2 | Run nspire_sim.py; check OS |
| Nspire: "This document format is not supported" | Python .tns on non-CX II or OS < 5.2 | Use Lua build |
| Nspire: app slow/stutters | allocation in on.paint, full redraws | Precompute; invalidate only changes |
| Nspire: battery drains in sleep | timer left running | Stop timer on idle/deactivate (sim checks) |
| Nspire: TI-Basic "Define" error | name clash or wrong folder | Rename; for libraries save in MyLib and Refresh Libraries |
| Exam mode hides the app | Press-to-Test | Expected; exit Press-to-Test to use it |
| pip install fails (Claude.ai sandbox) | no network | tns_builder needs no pip; deliver TI-BASIC source with paste steps |
