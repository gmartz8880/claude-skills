"""Shared helpers for the voice-line skill (free, local, no accounts beyond Telegram)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CLAUDE_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
TELEGRAM_DIR = Path(os.environ.get("TELEGRAM_STATE_DIR", CLAUDE_DIR / "channels" / "telegram"))
ENV_FILE = TELEGRAM_DIR / ".env"
STATE_FILE = TELEGRAM_DIR / "voice-line.json"
VOICE_DIR = CLAUDE_DIR / "voice-line"          # models, voices, temp audio
VOICE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PIPER_VOICE = "en_US-lessac-medium"
DEFAULT_WHISPER_MODEL = os.environ.get("VOICE_LINE_WHISPER_MODEL", "small.en")


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def bot_token() -> str | None:
    """Same lookup order as the official Telegram plugin: shell env first, then .env."""
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    if tok:
        return tok.strip()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def remembered_chat() -> str | None:
    return load_state().get("chat_id") or os.environ.get("VOICE_LINE_CHAT_ID")


def find_ffmpeg() -> str | None:
    import shutil
    for name in ("ffmpeg", "ffmpeg.exe"):
        p = shutil.which(name)
        if p:
            return p
    # winget installs Gyan.FFmpeg under WinGet\Packages; look there as a fallback
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
        if base.exists():
            for p in base.rglob("ffmpeg.exe"):
                return str(p)
    return None
