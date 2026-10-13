#!/usr/bin/env python3
"""Find burned-in captions/labels in a finished video, frame by frame.

    python3 tools/burned_text.py VIDEO --out DIR [--fps 10] [--band 0.05 0.97]

Burned captions are white (or coloured) glyphs with a dark outline/shadow. A pixel counts as "text" when it is very
bright and has a dark pixel within 2 px (the outline): smooth bright areas (a white shirt, windows, ceiling lights)
have no dark edge right next to them, so they mostly drop out. Text pixels are merged horizontally into lines; lines
that are too sparse or too tall to be type are rejected.

Writes DIR/<stem>.text.json = {fps, w, h, frames: [{t, boxes: [[x0,y0,x1,y1] as 0-1 fractions], px}]} and a
DIR/<stem>.text.jpg sheet with the boxes drawn, to check the detection by eye.
"""
import argparse
import json
import pathlib
import subprocess

import numpy as np
from PIL import Image, ImageDraw


def frames(path, fps, w):
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.split(",")
    W, H = int(probe[0]), int(probe[1])
    h = round(H * w / W / 2) * 2
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:{h}:flags=area",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    i = 0
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield i / fps, np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        i += 1


def dilate(m, r, axis=None):
    out = m.copy()
    for d in range(1, r + 1):
        if axis in (None, 0):
            out[d:] |= m[:-d]; out[:-d] |= m[d:]
        if axis in (None, 1):
            out[:, d:] |= m[:, :-d]; out[:, :-d] |= m[:, d:]
    return out


def detect(img, band):
    h, w, _ = img.shape
    f = img.astype(np.int16)
    lum = (f[..., 0] * 3 + f[..., 1] * 6 + f[..., 2]) // 10
    sat = f.max(-1) - f.min(-1)
    bright = (lum > 215) & (sat < 60)          # white glyphs
    coloured = (sat > 110) & (f.max(-1) > 150)  # keyword glyphs in red/blue
    dark = lum < 70
    edge = dilate(dark, 2)
    text = (bright | coloured) & edge
    y0, y1 = int(band[0] * h), int(band[1] * h)
    text[:y0] = False; text[y1:] = False
    rows = text.sum(1)
    # line candidates: rows with enough text pixels, merged with a small vertical gap
    on = rows > max(3, w * 0.012)
    boxes = []
    y = 0
    while y < h:
        if not on[y]:
            y += 1; continue
        s = y
        gap = 0
        while y < h and (on[y] or gap < 3):
            gap = 0 if on[y] else gap + 1
            y += 1
        e = y - gap
        if e - s < max(4, h * 0.008) or e - s > h * 0.09:  # too thin (noise) or too tall (not type)
            continue
        cols = text[s:e].sum(0) > 0
        xs = np.where(dilate(cols[None], int(w * 0.03), axis=1)[0])[0]
        if len(xs) == 0:
            continue
        # the widest run of columns is the line
        runs = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
        run = max(runs, key=len)
        x0, x1 = run[0], run[-1]
        density = text[s:e, x0:x1 + 1].mean()
        if density < 0.04 or (x1 - x0) < w * 0.06:
            continue
        boxes.append([x0 / w, s / h, (x1 + 1) / w, e / h, float(density)])
    # merge lines of one caption block (stacked lines within ~1 line height)
    boxes.sort(key=lambda b: b[1])
    merged = []
    for b in boxes:
        if merged and b[1] - merged[-1][3] < 0.025:
            m = merged[-1]
            merged[-1] = [min(m[0], b[0]), m[1], max(m[2], b[2]), b[3], max(m[4], b[4])]
        else:
            merged.append(b)
    return [[round(v, 4) for v in b[:4]] for b in merged], int(text.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--width", type=int, default=360)
    ap.add_argument("--band", type=float, nargs=2, default=[0.05, 0.97])
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = pathlib.Path(a.video).stem
    res, thumbs = [], []
    for t, img in frames(a.video, a.fps, a.width):
        boxes, px = detect(img, a.band)
        res.append({"t": round(t, 3), "boxes": boxes, "px": px})
        if round(t * a.fps) % max(1, round(a.fps / 2)) == 0:  # sheet at 2 fps
            im = Image.fromarray(img).copy()
            d = ImageDraw.Draw(im)
            for b in boxes:
                d.rectangle([b[0] * im.width, b[1] * im.height, b[2] * im.width, b[3] * im.height], outline=(0, 255, 0), width=2)
            d.text((4, 4), f"{t:.1f}", fill=(255, 255, 0))
            thumbs.append(im.resize((im.width // 2, im.height // 2)))
    json.dump({"fps": a.fps, "frames": res}, open(out / f"{stem}.text.json", "w"))
    cols = 12
    tw, th = thumbs[0].size
    sheet = Image.new("RGB", (tw * cols, th * ((len(thumbs) + cols - 1) // cols)))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(out / f"{stem}.text.jpg", quality=85)
    print(out / f"{stem}.text.json")


if __name__ == "__main__":
    main()
