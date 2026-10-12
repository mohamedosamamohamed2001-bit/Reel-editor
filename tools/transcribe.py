#!/usr/bin/env python3
"""Word-level transcription with faster-whisper (local, CPU, no paid API).

Usage:
    .venv/bin/python tools/transcribe.py VIDEO [--out DIR] [--model medium] [--lang ar]

Writes DIR/<stem>.words.json (segments + per-word start/end/probability) and DIR/<stem>.srt.
The transcript is a draft: words with low probability are flagged and must be checked by
ear before they are used as captions (captions must be the speaker's exact words).
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

LOW_PROB = 0.5


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def load_audio(path, sr=16000):
    # Decode with system FFmpeg instead of PyAV (PyAV/faster-whisper version skew breaks decode_audio).
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="medium")
    ap.add_argument("--lang", default=None, help="e.g. ar, en; omit to auto-detect")
    a = ap.parse_args()

    video = Path(a.video)
    out = Path(a.out) if a.out else video.parent
    out.mkdir(parents=True, exist_ok=True)

    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(load_audio(video), language=a.lang, word_timestamps=True,
                                      vad_filter=True, beam_size=5)
    data = {"language": info.language, "language_probability": round(info.language_probability, 3),
            "model": a.model, "segments": []}
    for s in segments:
        words = [{"w": w.word.strip(), "start": round(float(w.start), 3), "end": round(float(w.end), 3),
                  "p": round(float(w.probability), 3), "check": bool(w.probability < LOW_PROB)} for w in (s.words or [])]
        data["segments"].append({"start": round(s.start, 3), "end": round(s.end, 3),
                                 "text": s.text.strip(), "words": words})

    stem = video.stem[:40]
    (out / f"{stem}.words.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    lines = []
    for i, s in enumerate(data["segments"], 1):
        lines += [str(i), f"{srt_time(s['start'])} --> {srt_time(s['end'])}", s["text"], ""]
    (out / f"{stem}.srt").write_text("\n".join(lines))
    flagged = sum(w["check"] for s in data["segments"] for w in s["words"])
    total = sum(len(s["words"]) for s in data["segments"])
    print(f"{video.name}: lang={data['language']} ({data['language_probability']}), "
          f"{len(data['segments'])} segments, {total} words, {flagged} flagged for checking")


if __name__ == "__main__":
    main()
