#!/usr/bin/env python3
"""Sheets of the burned-in caption band, one row per caption change, to READ a finished video's caption text.

    python3 tools/read_strips.py VIDEO OUT_PREFIX [--band 0.40 0.90] [--step 0.4] [--rows 14]

Every --step seconds the band is cropped; a row is kept when its bright-text pixels differ from the last kept row
(a new phrase). Rows are labelled with their time. Writes OUT_PREFIX_1.jpg, _2.jpg ...
"""
import argparse
import subprocess

import numpy as np
from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--band", nargs=2, type=float, default=[0.40, 0.90])
    ap.add_argument("--step", type=float, default=0.4)
    ap.add_argument("--rows", type=int, default=14)
    ap.add_argument("--width", type=int, default=540)
    a = ap.parse_args()
    w = a.width
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height:stream_side_data=rotation",
                         "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout.split()
    W, H = map(int, pr[0].split(",")[:2])
    if len(pr) > 1 and pr[1].strip("-") in ("90", "270"):
        W, H = H, W
    h = round(H * w / W / 2) * 2
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.video, "-vf", f"fps=1/{a.step},scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    y0, y1 = int(h * a.band[0]), int(h * a.band[1])
    # keep the COMPLETE state of each phrase: the last sample before the text shrinks or changes a lot
    samples, i = [], 0
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        fr = np.frombuffer(buf, np.uint8).reshape(h, w, 3)[y0:y1]
        samples.append((i * a.step, fr.copy(), fr.min(axis=2) > 200))
        i += 1
    # fixed grid: every sample (typewriter captions show each full phrase at some sample when step < phrase length)
    rows = [(t, fr) for t, fr, txt in samples]
    per, cols = a.rows, 2
    for k in range(0, len(rows), per):
        chunk = rows[k:k + per]
        rh = y1 - y0
        nr = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (w + 50), rh * nr), "black")
        d = ImageDraw.Draw(sheet)
        for j, (t, fr) in enumerate(chunk):
            x, y = (j % cols) * (w + 50), (j // cols) * rh
            sheet.paste(Image.fromarray(fr), (x + 50, y))
            d.text((x + 4, y + 4), f"{t:.1f}", fill="yellow")
        sheet.save(f"{a.out}_{k // per + 1}.jpg", quality=85)
    print(f"{len(rows)} rows -> {a.out}_*.jpg")


if __name__ == "__main__":
    main()
