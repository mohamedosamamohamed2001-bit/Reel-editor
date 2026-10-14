#!/usr/bin/env python3
"""Erase burned-in captions from a finished video (no box, no blur): the glyph pixels are rebuilt from their surroundings.

    .venv/bin/python tools/erase_text.py projects/<p> [--out work/clean/original.clean.mp4] [--test t1,t2,...]

Where: the edit's `covers` (source time + box, the old-caption map from tools/burned_text.py, also used to place the
new captions). What: inside those boxes, a pixel is old-caption text when it is bright and low-saturation (the white
glyphs) AND has a dark pixel close by (their outline/shadow); line-shaped clusters of such pixels are kept, big or
sparse blobs (a white shirt, window light) are dropped. The mask is grown to take the outline and soft edges with it,
then filled with OpenCV's Telea inpainting (each pixel from its neighbours: thin strokes fill cleanly).

The source is never modified: a new file is written with the same size, frame rate and frame count
(x264 CRF 10, near-lossless), so every cut, hold and seek of the edit lands on the same frame.
--test writes before/after/mask PNGs for a few source times instead (to check by eye).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np


def probe(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_frames", "-of", "json", str(src)],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = map(int, s["r_frame_rate"].split("/"))
    return s["width"], s["height"], num, den, int(s.get("nb_frames", 0))


def boxes_at(covers, t, W, H, pad=0.03, slack=0.08, full_width=True):
    out = []
    for c in covers:
        if c["at"] - slack <= t < c["at"] + c["dur"] + slack:
            x0, y0, x1, y1 = c["box"]
            if full_width:  # detection boxes can stop short of a line's ends; the glyph test keeps the mask selective
                x0, x1 = 0.0, 1.0
            out.append((max(0, int((x0 - pad) * W)), max(0, int((y0 - pad) * H)),
                        min(W, int((x1 + pad) * W + 1)), min(H, int((y1 + pad) * H + 1))))
    return out


def candidates(rgb, boxes, p, t=0.0):
    """Pixels that look like old-caption glyphs in this frame (before the timing and shape tests)."""
    H, W = rgb.shape[:2]
    if not boxes:
        return np.zeros((H, W), np.uint8)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    bright = ((v >= p["v_min"]) & (s <= p["s_max"])).astype(np.uint8)
    near_dark = cv2.dilate((v <= p["dark_max"]).astype(np.uint8), np.ones((2 * p["r_dark"] + 1,) * 2, np.uint8))
    cand = bright & near_dark
    for t0, t1, hue in p["color_windows"]:  # coloured caption words, only where a colour scan found static text
        if t0 <= t < t1:
            lo, hi, smin, vmin = {"blue": (105, 118, 170, 110), "brown": (5, 25, 150, 90)}[hue]
            cand |= ((h >= lo) & (h <= hi) & (s >= smin) & (v >= vmin)).astype(np.uint8)
    region = np.zeros_like(cand)
    for x0, y0, x1, y1 in boxes:
        region[max(y0, int(p["y_min"] * H)):y1, x0:x1] = 1
    return cand & region


def final_mask(prev, cur, nxt, p):
    """Old captions are fixed on screen; clothing stripes and edges move. Keep a candidate only if it is also a
    candidate a moment before OR after (OR: a caption's first and last frames still pass), then judge the shapes."""
    cand = cur & (prev | nxt) if p["persist"] else cur
    if not cand.any():
        return cand
    def text_like(w, h, dens):
        return p["h_min"] <= h <= p["h_max"] and w >= p["w_min"] and p["dens_min"] <= dens <= p["dens_max"]

    def clusters(px, jy):
        joined = cv2.dilate(px, cv2.getStructuringElement(cv2.MORPH_RECT, (p["join_x"], jy)))
        n, lab, st, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
        return n, lab, st

    n, lab, st = clusters(cand, p["join_y"])
    m = np.zeros_like(cand)
    for i in range(1, n):
        x, y, w, h, _ = st[i]
        sub = cand[y:y + h, x:x + w] * (lab[y:y + h, x:x + w] == i)
        if text_like(w, h, sub.sum() / max(1, w * h)):
            m[y:y + h, x:x + w] |= sub
        else:  # a caption line merged with something sparse (equipment, an edge): judge its lines on their own
            n2, lab2, st2 = clusters(sub, 1)
            for k in range(1, n2):
                x2, y2, w2, h2, _ = st2[k]
                sub2 = sub[y2:y2 + h2, x2:x2 + w2] * (lab2[y2:y2 + h2, x2:x2 + w2] == k)
                if w2 >= 3 * p["w_min"] and text_like(w2, h2, sub2.sum() / max(1, w2 * h2)):
                    m[y + y2:y + y2 + h2, x + x2:x + x2 + w2] |= sub2
    # dots and small marks right next to kept letters belong to them
    m |= cand & cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    # take the outline / shadow / antialiased edge with the glyph
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * p["grow"] + 1,) * 2))
    # fill the inside of letters (counters) that are bright-ish but missed by the threshold
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    return m * 255


PARAMS = {"v_min": 200, "s_max": 70, "dark_max": 90, "r_dark": 3, "join_x": 15, "join_y": 3, "h_min": 8, "h_max": 200,
          "w_min": 10, "dens_min": 0.08, "dens_max": 0.75, "grow": 4, "radius": 6, "persist": 0.15, "y_min": 0.0,
          "color_windows": []}


def inpaint(rgb, m):
    if not m.any():
        return rgb
    out = cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), m, PARAMS["radius"], cv2.INPAINT_TELEA)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


def read_frames(src, W, H, ss=None, count=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", f"{ss:.4f}"] if ss else []) + ["-i", str(src)]
    cmd += (["-frames:v", str(count)] if count else []) + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-vsync", "passthrough", "-"]
    rd = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        buf = rd.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    rd.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--src", default="source/original.mp4")
    ap.add_argument("--out", default="work/clean/original.clean.mp4")
    ap.add_argument("--test", default=None, help="comma-separated source times: write PNGs to --test-dir only")
    ap.add_argument("--test-dir", default=None)
    ap.add_argument("--params", default=None, help="JSON overrides for PARAMS")
    a = ap.parse_args()
    P = Path(a.project)
    edit = json.loads((P / "edit.json").read_text())
    covers = [c for c in edit.get("covers", []) if c.get("src", "main") == "main"]
    p = dict(PARAMS, **(json.loads(a.params) if a.params else {}))
    pf = P / "erase_params.json"
    if pf.exists():
        p.update(json.loads(pf.read_text()))
    src = P / a.src
    W, H, num, den, nb = probe(src)
    D = max(1, round(p["persist"] * num / den))  # frames before/after for the timing test
    fps = num / den
    cand_at = lambda rgb, t: candidates(rgb, boxes_at(covers, t, W, H), p, t)
    if a.test:
        od = Path(a.test_dir)
        od.mkdir(parents=True, exist_ok=True)
        for t in map(float, a.test.split(",")):
            fr = list(read_frames(src, W, H, ss=max(0.0, t - D / fps), count=2 * D + 1))
            cs = [cand_at(f, t + (k - D) / fps) for k, f in enumerate(fr)]
            rgb = fr[D].copy()
            m = final_mask(cs[0], cs[D], cs[-1], p)
            out = inpaint(rgb, m)
            ov = rgb.copy()
            ov[m > 0] = (255, 0, 255)
            cv2.imwrite(str(od / f"{P.name}_{t:06.2f}.png"), cv2.cvtColor(np.hstack([rgb, ov, out]), cv2.COLOR_RGB2BGR))
        return
    dst = P / a.out
    dst.parent.mkdir(parents=True, exist_ok=True)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", f"{num}/{den}", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "10",
                           "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                           "-movflags", "+faststart", str(dst)], stdin=subprocess.PIPE)
    frames, cands = [], []
    zero = np.zeros((H, W), np.uint8)
    i = touched = written = 0

    def emit(j):  # write frame j once its neighbours j-D and j+D are known
        nonlocal touched, written
        k = j - (i - len(frames))  # index into the buffer
        prev = cands[k - D] if k - D >= 0 else zero
        nxt = cands[k + D] if k + D < len(cands) else zero
        m = final_mask(prev, cands[k], nxt, p)
        touched += bool(m.any())
        wr.stdin.write(np.ascontiguousarray(inpaint(frames[k], m)).tobytes())
        written += 1

    for rgb in read_frames(src, W, H):
        frames.append(rgb)
        cands.append(cand_at(rgb, i / fps))
        i += 1
        j = i - 1 - D  # frame whose look-ahead is now complete
        if j >= 0:
            emit(j)
            if len(frames) > 2 * D + 1:
                frames.pop(0)
                cands.pop(0)
        if i % 600 == 0:
            print(f"{i}/{nb} frames", file=sys.stderr, flush=True)
    for j in range(max(0, i - D), i):
        emit(j)
    wr.stdin.close()
    wr.wait()
    print(json.dumps({"out": str(dst), "frames": written, "source_frames": nb, "frames_cleaned": touched, "persist_frames": D}))
    if written != nb or wr.returncode:
        sys.exit(1)


if __name__ == "__main__":
    main()
