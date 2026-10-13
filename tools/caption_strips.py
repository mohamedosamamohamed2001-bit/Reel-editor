#!/usr/bin/env python3
"""Crop every distinct burned-in caption (from burned_text.py's JSON) into one tall sheet, to read the original text.

    python3 tools/caption_strips.py VIDEO TEXT_JSON OUT.jpg [--band 0.45 0.85]
A new strip is taken whenever the detected caption box changes noticeably (a new phrase appeared).
"""
import argparse
import json
import subprocess
from io import BytesIO

from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("text_json"); ap.add_argument("out")
ap.add_argument("--band", type=float, nargs=2, default=[0.45, 0.85])
a = ap.parse_args()
d = json.load(open(a.text_json))
W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout.strip().split(","))
# group consecutive frames whose caption box stays put; one strip per group, late in it (text fully animated in)
groups, cur = [], []
for f in d["frames"]:
    bs = [b for b in f["boxes"] if a.band[0] <= b[1] and b[3] <= a.band[1] and b[3] - b[1] <= 0.08]
    b = max(bs, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])) if bs else None
    if b and cur and abs(b[0] - cur[-1][1][0]) + abs(b[2] - cur[-1][1][2]) + abs(b[1] - cur[-1][1][1]) <= 0.04:
        cur.append((f["t"], b))
        continue
    if len(cur) >= 3:
        groups.append(cur)
    cur = [(f["t"], b)] if b else []
if len(cur) >= 3:
    groups.append(cur)
picks = [(g[int(len(g) * 0.75)][0], max((x[1] for x in g), key=lambda b: b[3] - b[1])) for g in groups]
strips = []
for t, b in picks:
    y0, y1 = max(0, b[1] - 0.012), min(1, b[3] + 0.012)
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1", "-vf",
                          f"crop={W}:{int((y1 - y0) * H)}:0:{int(y0 * H)}", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    im = Image.open(BytesIO(png)).convert("RGB")
    canvas = Image.new("RGB", (im.width + 70, im.height), (0, 0, 0))
    canvas.paste(im, (70, 0))
    ImageDraw.Draw(canvas).text((4, 4), f"{t:.1f}", fill=(255, 255, 0))
    strips.append(canvas)
pages = [strips[i:i + 16] for i in range(0, len(strips), 16)]
for k, page in enumerate(pages):
    sheet = Image.new("RGB", (max(s.width for s in page), sum(s.height for s in page)))
    y = 0
    for s in page:
        sheet.paste(s, (0, y))
        y += s.height
    sheet.save(a.out.replace(".jpg", f"_{k + 1}.jpg"), quality=92)
print(len(strips), "strips in", len(pages), "pages")
