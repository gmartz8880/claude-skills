#!/usr/bin/env python3
"""Transcribe a Telegram voice note (.oga/.ogg/.mp3/.wav/.m4a) locally with faster-whisper.

Usage:  python transcribe.py <audio-file> [--model small.en]
Prints the transcript to stdout. Nothing leaves the PC except the one-time
free model download from Hugging Face.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DEFAULT_WHISPER_MODEL, VOICE_DIR, find_ffmpeg, log  # noqa: E402


def ensure_faster_whisper():
    try:
        from faster_whisper import WhisperModel  # noqa: F401
    except ImportError:
        log("faster-whisper missing; installing (free, one time)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "faster-whisper"])


def to_wav(src: Path) -> Path:
    """Convert to 16 kHz mono WAV so decoding never depends on the container."""
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        return src  # faster-whisper can usually decode .oga directly via PyAV
    out = Path(tempfile.mkdtemp(dir=VOICE_DIR)) / "in.wav"
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "16000", str(out)], check=True)
    return out


def load_pcm(wav: Path):
    """Read 16 kHz mono 16-bit WAV into float32 without depending on PyAV."""
    import wave
    import numpy as np
    with wave.open(str(wav), "rb") as w:
        frames = w.readframes(w.getnframes())
    return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--model", default=DEFAULT_WHISPER_MODEL, help="tiny.en | base.en | small.en | medium.en")
    args = ap.parse_args()

    src = Path(args.audio).expanduser()
    if not src.exists():
        sys.exit(f"audio file not found: {src}")

    ensure_faster_whisper()
    from faster_whisper import WhisperModel

    wav = to_wav(src)
    model = WhisperModel(args.model, device="cpu", compute_type="int8", download_root=str(VOICE_DIR / "whisper"))
    audio = load_pcm(wav) if wav.suffix == ".wav" else str(wav)  # skip PyAV when we already have clean WAV
    segments, info = model.transcribe(audio, vad_filter=True, beam_size=5)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    log(f"[voice-line] {info.duration:.1f}s of audio, language={info.language}")
    print(text if text else "(no speech detected)")


if __name__ == "__main__":
    main()
