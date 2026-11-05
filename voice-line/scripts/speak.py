#!/usr/bin/env python3
"""Turn text into a Telegram voice note and send it (free: Piper TTS + Telegram Bot API).

Usage:
  python speak.py "Short spoken sentence."                  # uses remembered chat
  python speak.py --chat 123456789 "Hello"                  # explicit chat id
  python speak.py --text "long written detail" "Spoken summary."
  python speak.py --remember-chat 123456789                 # store default chat id
  python speak.py --remember-name "Alex"                    # store the name used in greetings
  python speak.py --dry-run "test"                          # make the .ogg, do not send

Voice order: Piper (local, open source) -> Windows System.Speech fallback.
Telegram's sendVoice wants OGG/Opus, so ffmpeg converts the WAV first.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DEFAULT_PIPER_VOICE, VOICE_DIR, bot_token, find_ffmpeg, load_state, log, remembered_chat, save_state  # noqa: E402

PIPER_DIR = VOICE_DIR / "piper"


def piper_voice_files(name: str) -> Path | None:
    onnx = PIPER_DIR / f"{name}.onnx"
    if onnx.exists() and onnx.with_suffix(".onnx.json").exists():
        return onnx
    return None


def ensure_piper(name: str) -> Path | None:
    """Install piper-tts and download the voice once. Returns the .onnx path or None."""
    try:
        import piper  # noqa: F401
    except ImportError:
        log("piper-tts missing; installing (free, one time)...")
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "piper-tts"])
        if r.returncode != 0:
            return None
    voice = piper_voice_files(name)
    if voice:
        return voice
    PIPER_DIR.mkdir(parents=True, exist_ok=True)
    log(f"downloading Piper voice {name} (free, one time)...")
    r = subprocess.run([sys.executable, "-m", "piper.download_voices", name, "--data-dir", str(PIPER_DIR)])
    return piper_voice_files(name) if r.returncode == 0 else None


def tts_piper(text: str, wav: Path, voice_name: str) -> bool:
    voice = ensure_piper(voice_name)
    if not voice:
        return False
    r = subprocess.run([sys.executable, "-m", "piper", "-m", str(voice), "-f", str(wav), "--", text],
                       capture_output=True, text=True)
    if r.returncode != 0:
        log(r.stderr[-800:])
    return r.returncode == 0 and wav.exists()


def tts_windows(text: str, wav: Path) -> bool:
    """Zero-install fallback: the voice that ships with Windows."""
    if os.name != "nt":
        return False
    ps = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SetOutputToWaveFile('{wav}'); "
        "$s.Speak([Console]::In.ReadToEnd()); $s.Dispose()"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], input=text, text=True, capture_output=True)
    return r.returncode == 0 and wav.exists()


def wav_to_ogg(wav: Path, ogg: Path) -> bool:
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        log("ffmpeg not found. Install with: winget install Gyan.FFmpeg  (then open a new terminal)")
        return False
    r = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libopus", "-b:a", "32k",
                        "-application", "voip", str(ogg)])
    return r.returncode == 0 and ogg.exists()


def send_voice(token: str, chat_id: str, ogg: Path, caption: str | None) -> dict:
    boundary = uuid.uuid4().hex
    parts = []

    def field(name: str, value: str):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())

    field("chat_id", chat_id)
    if caption:
        field("caption", caption[:1024])
    parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"voice\"; filename=\"voice.ogg\"\r\n"
                  "Content-Type: audio/ogg\r\n\r\n").encode() + ogg.read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendVoice", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def send_text(token: str, chat_id: str, text: str) -> None:
    for i in range(0, len(text), 4000):
        data = json.dumps({"chat_id": chat_id, "text": text[i:i + 4000]}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=30).read()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("speech", nargs="?", help="what to say out loud (keep it short)")
    ap.add_argument("--chat", help="Telegram chat_id (defaults to remembered)")
    ap.add_argument("--text", help="optional longer written message sent after the voice note")
    ap.add_argument("--voice", default=os.environ.get("VOICE_LINE_PIPER_VOICE", DEFAULT_PIPER_VOICE))
    ap.add_argument("--remember-chat", metavar="CHAT_ID", help="store a default chat id and exit")
    ap.add_argument("--remember-name", metavar="NAME", help="store the name used in spoken greetings and exit")
    ap.add_argument("--dry-run", action="store_true", help="build the audio file but do not send")
    args = ap.parse_args()

    if args.remember_name:
        st = load_state(); st["name"] = args.remember_name.strip(); save_state(st)
        print(f"remembered name {args.remember_name.strip()}")
        return
    if args.remember_chat:
        st = load_state(); st["chat_id"] = str(args.remember_chat); save_state(st)
        print(f"remembered chat_id {args.remember_chat}")
        return
    if not args.speech:
        ap.error("give me something to say")

    chat = args.chat or remembered_chat()
    token = bot_token()
    if not args.dry_run:
        if not token:
            sys.exit("No TELEGRAM_BOT_TOKEN. Run /telegram:configure <token> in Claude Code first.")
        if not chat:
            sys.exit("No chat id. Pass --chat <id> or run: speak.py --remember-chat <id>")

    work = Path(tempfile.mkdtemp(dir=VOICE_DIR))
    wav, ogg = work / "say.wav", work / "say.ogg"
    if not tts_piper(args.speech, wav, args.voice):
        log("Piper unavailable, using Windows built-in voice")
        if not tts_windows(args.speech, wav):
            sys.exit("No text-to-speech engine worked. Run doctor.py.")
    if not wav_to_ogg(wav, ogg):
        sys.exit("Could not convert to OGG/Opus (ffmpeg problem).")

    if args.dry_run:
        print(f"dry run: {ogg} ({ogg.stat().st_size} bytes)")
        return

    res = send_voice(token, chat, ogg, caption=None)
    if not res.get("ok"):
        sys.exit(f"Telegram rejected the voice note: {res}")
    if args.text:
        send_text(token, chat, args.text)
    print(f"sent voice note ({ogg.stat().st_size // 1024} KB) to chat {chat}")
    for p in (wav, ogg):
        try: p.unlink()
        except OSError: pass


if __name__ == "__main__":
    main()
