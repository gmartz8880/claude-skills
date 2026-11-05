#!/usr/bin/env python3
"""Claude Code Notification hook: when Claude is waiting on you and you are away,
push a short voice note to your phone. Reads the hook JSON from stdin.

Wire it up with settings-hook-snippet.json (see INSTALL.md). Permission prompts
already arrive as Allow/Deny buttons through the Telegram relay; this hook adds
a spoken "I need you" so you notice it, and covers idle prompts too.
Never blocks Claude: all failures are swallowed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SPEAK = Path(__file__).with_name("speak.py")
sys.path.insert(0, str(Path(__file__).parent))
try:
    from common import load_state
    _NAME = (load_state().get("name") or "").strip()
except Exception:
    _NAME = ""
HEY = f"Hey {_NAME}" if _NAME else "Hey"


def main() -> None:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return
    kind = data.get("notification_type", "")
    msg = (data.get("message") or "").strip()
    if kind == "permission_prompt":
        say = f"{HEY}, Claude needs a permission answer. Check the buttons in Telegram."
    elif kind == "idle_prompt":
        say = f"{HEY}, Claude is waiting on you."
    else:
        say = f"{HEY}. {msg[:160]}" if msg else f"{HEY}, Claude has an update."
    try:
        subprocess.run([sys.executable, str(SPEAK), say], timeout=90, capture_output=True)
    except Exception:
        pass


if __name__ == "__main__":
    main()
