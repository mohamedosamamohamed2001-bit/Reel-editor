#!/usr/bin/env python3
"""Review a folder of raw clips before cutting a montage.

    .venv/bin/python tools/footage_review.py SOURCE_DIR OUT_DIR [--per-row 8]

For every clip: specs (size after rotation, fps, duration, slow-motion capture), a motion curve (mean frame
difference at 10 fps, 0-1) with its peaks (the explosive moments of a rep), and the audio level curve (plate
clanks, grunts). Writes OUT_DIR/review.json and OUT_DIR/sheet_XX.jpg contact sheets: one row per clip, 8 frames
spread over the clip, each labelled with the clip name and its time, plus a motion bar under each frame.
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,codec_name:stream_side_data=rotation:"
                        "stream_tags=rotate:format=duration", "-of", "json", str(p)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    s = d["streams"][0]
    rot = 0
    for sd in s.get("side_data_list", []):
        rot = int(sd.get("rotation", 0) or 0)
    rot = rot or int(s.get("tags", {}).get("rotate", 0) or 0)
    w, h = s["width"], s["height"]
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = map(int, s["avg_frame_rate"].split("/"))
    return {"w": w, "h": h, "fps": round(num / den, 3) if den else 0, "rot": rot, "codec": s.get("codec_name"),
            "dur": float(d["format"]["duration"])}


def frames(p, fps, width):
    """Autorotated gray frames at `fps`, `width` px wide."""
    info = probe(p)
    h = int(round(info["h"] * width / info["w"] / 2) * 2)
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"fps={fps},scale={width}:{h}", "-f", "rawvideo",
                           "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    n = width * h
    while True:
        b = pr.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, width).astype(np.float32)


def audio_curve(p, rate=10):
    pr = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                        capture_output=True)
    x = np.frombuffer(pr.stdout, np.int16).astype(np.float32) / 32768
    if not len(x):
        return []
    hop = 8000 // rate
    rms = [float(np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(x) - hop, hop)]
    return [round(20 * np.log10(v), 1) for v in rms]


def peaks(curve, rate, min_gap=0.8, top=6):
    c = np.array(curve)
    if len(c) < 3:
        return []
    idx = [i for i in range(1, len(c) - 1) if c[i] >= c[i - 1] and c[i] >= c[i + 1]]
    idx.sort(key=lambda i: -c[i])
    out = []
    for i in idx:
        if all(abs(i - j) / rate >= min_gap for j in out):
            out.append(i)
        if len(out) >= top:
            break
    return sorted(round(i / rate, 2) for i in out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--per-row", type=int, default=8)
    ap.add_argument("--rows", type=int, default=8)
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    clips = sorted(p for p in src.iterdir() if p.suffix.lower() in (".mov", ".mp4", ".m4v"))
    report = []
    rows = []
    for p in clips:
        info = probe(p)
        f = list(frames(p, 10, 96))
        mot = [0.0] + [float(np.mean(np.abs(f[i] - f[i - 1]))) / 255 for i in range(1, len(f))]
        mot = [round(m, 4) for m in mot]
        aud = audio_curve(p)
        rec = dict(info, name=p.name, motion=mot, audio=aud, motion_peaks=peaks(mot, 10), audio_peaks=peaks(aud, 10),
                   motion_mean=round(float(np.mean(mot)) if mot else 0, 4))
        report.append(rec)
        # thumbnails
        n = a.per_row
        ts = [info["dur"] * (i + 0.5) / n for i in range(n)]
        tw = 150
        th = int(tw * info["h"] / info["w"])
        thumbs = []
        for t in ts:
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(p), "-frames:v", "1", "-vf",
                                f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
            if len(r.stdout) == tw * th * 3:
                im = Image.frombytes("RGB", (tw, th), r.stdout)
            else:
                im = Image.new("RGB", (tw, th))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, tw, 14], fill=(0, 0, 0))
            d.text((2, 1), f"{p.stem[-4:]} {t:.1f}s", fill=(255, 255, 0))
            k = min(len(mot) - 1, int(t * 10)) if mot else 0
            m = mot[k] if mot else 0
            d.rectangle([0, th - 6, int(tw * min(1, m * 20)), th], fill=(255, 60, 60))
            thumbs.append(im)
        row = Image.new("RGB", (tw * n, th))
        for i, im in enumerate(thumbs):
            row.paste(im, (i * tw, 0))
        rows.append(row)
        print(f"{p.name}: {info['w']}x{info['h']} {info['fps']}fps {info['dur']:.1f}s motion {rec['motion_mean']:.4f}"
              f" peaks {rec['motion_peaks']}", flush=True)
    (out / "review.json").write_text(json.dumps(report))
    for s in range(0, len(rows), a.rows):
        chunk = rows[s:s + a.rows]
        W = max(r.width for r in chunk)
        sheet = Image.new("RGB", (W, sum(r.height for r in chunk)))
        y = 0
        for r in chunk:
            sheet.paste(r, (0, y))
            y += r.height
        sheet.save(out / f"sheet_{s // a.rows + 1:02d}.jpg", quality=85)


if __name__ == "__main__":
    main()
