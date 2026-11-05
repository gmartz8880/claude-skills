#!/usr/bin/env python3
"""Check every piece of the free voice line and print the fix for anything missing.

Usage: python doctor.py
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DEFAULT_PIPER_VOICE, ENV_FILE, VOICE_DIR, bot_token, find_ffmpeg, remembered_chat  # noqa: E402

ok = True


def check(label: str, passed: bool, fix: str = "") -> None:
    global ok
    print(f"[{'OK ' if passed else 'FIX'}] {label}" + ("" if passed else f"\n      -> {fix}"))
    ok = ok and passed


def have_module(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def main() -> None:
    v = sys.version_info
    check(f"Python {v.major}.{v.minor}", v >= (3, 10), "Install Python 3.10+ from python.org (free) and tick 'Add to PATH'.")
    check("faster-whisper (speech to text)", have_module("faster_whisper"), "pip install faster-whisper")
    check("piper-tts (text to speech)", have_module("piper"), "pip install piper-tts   (optional: Windows voice is the fallback)")
    voice = VOICE_DIR / "piper" / f"{DEFAULT_PIPER_VOICE}.onnx"
    check(f"Piper voice {DEFAULT_PIPER_VOICE}", voice.exists(),
          f"python -m piper.download_voices {DEFAULT_PIPER_VOICE} --data-dir \"{VOICE_DIR / 'piper'}\"")
    check("ffmpeg (OGG/Opus conversion)", bool(find_ffmpeg()), "winget install Gyan.FFmpeg   then open a NEW terminal")
    check("bun (needed by the Telegram channel plugin)", bool(shutil.which("bun") or shutil.which("bun.exe")),
          'powershell -c "irm bun.sh/install.ps1 | iex"   then open a NEW terminal')
    claude = shutil.which("claude") or shutil.which("claude.cmd") or shutil.which("claude.exe")
    check("claude (Claude Code CLI)", bool(claude), "Claude Code is not on PATH; install it or re-open the terminal.")
    if claude:
        try:
            ver = subprocess.run([claude, "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
            print(f"      claude version: {ver}")
        except Exception:
            pass
    check(f"Telegram token file {ENV_FILE}", bool(bot_token()),
          "In Claude Code: /plugin install telegram@claude-plugins-official then /telegram:configure <bot token>")
    check("Remembered chat id", bool(remembered_chat()),
          "Send the bot one message from your phone, then: python speak.py --remember-chat <chat_id from the <channel> tag>")
    whisper_dir = VOICE_DIR / "whisper"
    check("Whisper model cached", whisper_dir.exists() and any(whisper_dir.iterdir()) if whisper_dir.exists() else False,
          "Downloads automatically on first transcribe (one time, free).")
    print("\nAll good. Start the line with Start-Voice-Line.ps1" if ok else "\nFix the items above, then run doctor.py again.")


if __name__ == "__main__":
    main()
