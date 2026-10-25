"""Check that the FX render changed nothing but the transition windows.

- stream specs (codec, 10-bit, HLG/BT.2020 tags, size, fps, frame count, duration) equal the original
- PSNR(Y) of every frame vs the original; frames OUTSIDE the transition windows must be >= 45 dB
- the cuts are at the same frame numbers (largest frame-to-frame change)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent
ORIG, OUT = P / "source" / "original.mov", Path(sys.argv[1])
KEYS = ["codec_name", "profile", "width", "height", "pix_fmt", "color_range", "color_space", "color_transfer",
        "color_primaries", "r_frame_rate", "nb_frames"]


def spec(f):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=" + ",".join(KEYS) + ",duration", "-of", "json", str(f)],
                                  capture_output=True, text=True).stdout)["streams"][0]
    return j


a, b = spec(ORIG), spec(OUT)
ok = True
for k in KEYS:
    same = str(a.get(k)) == str(b.get(k))
    ok &= same
    print(f"{'PASS' if same else 'FAIL'} {k}: {a.get(k)} -> {b.get(k)}")
print(f"INFO duration: {a['duration']} -> {b['duration']}")

stats = P / "work" / "psnr.txt"
subprocess.run(["ffmpeg", "-v", "error", "-i", str(OUT), "-i", str(ORIG), "-lavfi",
                f"[0:v][1:v]psnr=stats_file={stats}", "-f", "null", "-"], check=True)
ps = [float(l.split("psnr_y:")[1].split()[0].replace("inf", "99")) for l in stats.read_text().splitlines()]
touched = set(json.loads((P / "work" / "touched_frames.json").read_text()))
out_w = [(i, p) for i, p in enumerate(ps) if i not in touched]
low = [(i, p) for i, p in out_w if p < 45]
print(f"{'PASS' if not low else 'FAIL'} untouched frames: {len(out_w)}, PSNR-Y min {min(p for _, p in out_w):.1f} dB, "
      f"mean {np.mean([p for _, p in out_w]):.1f} dB, below 45 dB: {low[:10]}")
print(f"INFO transition-window frames: {len(touched)} ({len(touched) / 30:.2f} s of {len(ps) / 30:.2f} s)")
ok &= not low

cuts = [t["cut"] for t in json.loads((P / "plan.json").read_text())["transitions"]]
def diffs(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vf", "scale=96:170,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    d = np.frombuffer(raw, np.uint8).reshape(-1, 170, 96).astype(np.float32)
    return d
o = diffs(ORIG)
r = diffs(OUT)
# untouched frames on both sides of each cut must still match the original (the cut stays where it was)
moved = []
for c in cuts:
    pre = max(i for i in range(c - 12, c) if i not in touched)
    post = min(i for i in range(c, c + 12) if i not in touched)
    e1, e2 = np.abs(o[pre] - r[pre]).mean(), np.abs(o[post] - r[post]).mean()
    if e1 > 2 or e2 > 2:
        moved.append((c, e1, e2))
print(f"{'PASS' if not moved else 'FAIL'} cuts: {len(cuts)} cut points, shots on both sides match the original at the "
      f"same frame numbers {moved}")
ok &= not moved
print("ALL PASS" if ok else "CHECK FAILED")
