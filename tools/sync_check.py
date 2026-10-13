#!/usr/bin/env python3
"""Measure dialogue sync per clip: rendered audio vs. the source dialogue, by cross-correlation.

    python3 tools/sync_check.py projects/<name> RENDER.mp4

For every clip with dialogue, a 1.2 s window of the render (from 0.15 s into the clip) is matched against the source
dialogue around the clip's frame-exact start; the lag (ms) is how late the render's sound is relative to where the
edit puts it. The picture is frame-exact by construction (plates start on frame floor(in*fps)), so lag ~0 means
lips and voice are in sync. |lag| <= 10 ms passes.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 16000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    proj, render = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    edit = json.loads((proj / "edit.json").read_text())
    fps = edit["fps"]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import render_edit as R
    out = load(render)
    srcs = {}
    t_out = 0.0
    worst = 0.0
    for i, c in enumerate(edit["clips"]):
        n = R.plate_frames(c, fps) if edit.get("plates") else R.jsround(c["out"] * fps) - R.jsround(c["in"] * fps)
        silent = c.get("freeze") or c.get("speed", 1) != 1
        if not silent and n / fps >= 1.0:
            path = proj / edit.get("audio", {}).get(c["src"], edit["media"][c["src"]])
            if path not in srcs:
                srcs[path] = load(path)
            src = srcs[path]
            start = R.first_frame(c, fps) / fps
            a = int((t_out + 0.15) * SR)
            seg = out[a:a + int(1.2 * SR)]
            b = int((start + 0.15) * SR)
            maxlag = int(0.1 * SR)
            ref = src[max(0, b - maxlag):b + len(seg) + maxlag]
            if len(seg) and np.std(seg) > 1e-4 and len(ref) >= len(seg):
                cc = np.correlate(ref, seg, mode="valid")
                lag = (np.argmax(cc) - (b - max(0, b - maxlag))) / SR * 1000
                worst = max(worst, abs(lag))
                print(f"clip {i:2d}  out {t_out:6.2f}s  src {c['in']:6.2f}s  lag {-lag:+6.1f} ms")
        t_out += n / fps
    print(f"worst |lag| {worst:.1f} ms -> {'PASS' if worst <= 10 else 'CHECK'}")


if __name__ == "__main__":
    main()
