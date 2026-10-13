#!/usr/bin/env python3
"""Track one object through a shot (template matching, numpy only) for motion-tracked graphics.

    python3 tools/track.py VIDEO --start 3.6 --end 9.0 --box 0.40 0.80 0.60 0.95 [--fps 10] [--out keys.json]

box = the object in the first frame, as source-frame fractions (x0 y0 x1 y1). Each frame, the template is searched in a
window around the last position by normalised cross-correlation; the template is refreshed slowly (10 %) so lighting
changes don't lose it. Prints/writes keyframes [{"t": source s, "x", "y"}] (object centre, source-frame fractions)
and the match score per frame (a low score = check that stretch by eye).
"""
import argparse
import json
import subprocess

import numpy as np


def frames(path, start, end, fps, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(end - start), "-i", path, "-vf",
                          f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    n = w * h
    i = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield start + i / fps, np.frombuffer(b, np.uint8).reshape(h, w).astype(np.float32)
        i += 1


def ncc_search(img, tpl, cx, cy, r):
    th, tw = tpl.shape
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum()) + 1e-6
    best = (-2, cx, cy)
    H, W = img.shape
    for y in range(max(0, cy - r), min(H - th, cy + r) + 1, 1):
        rows = img[y:y + th]
        for x in range(max(0, cx - r), min(W - tw, cx + r) + 1, 1):
            p = rows[:, x:x + tw]
            pm = p - p.mean()
            s = (pm * t).sum() / (np.sqrt((pm * pm).sum()) * tn + 1e-6)
            if s > best[0]:
                best = (s, x, y)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--box", type=float, nargs=4, required=True)
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--width", type=int, default=180)
    ap.add_argument("--out")
    a = ap.parse_args()
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", a.video],
                           capture_output=True, text=True).stdout.strip().split(",")
    W0, H0 = int(probe[0]), int(probe[1])
    w = a.width
    h = round(H0 * w / W0)
    x0, y0, x1, y1 = (int(a.box[0] * w), int(a.box[1] * h), int(a.box[2] * w), int(a.box[3] * h))
    keys, tpl, x, y = [], None, x0, y0
    for t, img in frames(a.video, a.start, a.end, a.fps, w, h):
        if tpl is None:
            tpl = img[y0:y1, x0:x1].copy()
            score = 1.0
        else:
            score, x, y = ncc_search(img, tpl, x, y, 8)
            tpl = tpl * 0.9 + img[y:y + tpl.shape[0], x:x + tpl.shape[1]] * 0.1
        keys.append({"t": round(t, 3), "x": round((x + tpl.shape[1] / 2) / w, 4), "y": round((y + tpl.shape[0] / 2) / h, 4), "score": round(float(score), 3)})
    if a.out:
        json.dump(keys, open(a.out, "w"), indent=1)
    for k in keys:
        print(k)


if __name__ == "__main__":
    main()
