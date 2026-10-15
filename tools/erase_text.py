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


def boxes_at(covers, t, W, H, pad=0.03, slack=0.08, full_width=True, pad_x=0.12):
    out = []
    for c in covers:
        if c["at"] - slack <= t < c["at"] + c["dur"] + slack:
            x0, y0, x1, y1 = c["box"]
            if full_width:  # detection boxes can stop short of a line's ends; the glyph test keeps the mask selective
                x0, x1 = 0.0, 1.0
            else:
                x0, x1 = x0 - pad_x, x1 + pad_x
            out.append((max(0, int((x0 - pad) * W)), max(0, int((y0 - pad) * H)),
                        min(W, int((x1 + pad) * W + 1)), min(H, int((y1 + pad) * H + 1))))
    return out


_FACE = None


def face_guard(rgb, p):
    """Mask (1 = protected) over every detected face + beard/neck, never erased (Coach Osama's face is off limits)."""
    global _FACE
    H, W = rgb.shape[:2]
    k = 360 / W
    sw, sh = 360, int(round(H * k))
    if _FACE is None:  # YuNet (OpenCV model zoo, MIT), ~/.cache/osm-models/yunet.onnx
        _FACE = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (sw, sh), 0.6, 0.3, 50)
    _FACE.setInputSize((sw, sh))
    _, faces = _FACE.detect(cv2.cvtColor(cv2.resize(rgb, (sw, sh)), cv2.COLOR_RGB2BGR))
    g = np.zeros((H, W), np.uint8)
    for f in (faces if faces is not None else []):
        x, y, w, h = f[:4]
        eye_y = (f[5] + f[7]) / 2
        mouth_y = max(f[11], f[13])
        beard = mouth_y + p.get("beard", 0.95) * (mouth_y - eye_y)  # chin + beard below the mouth
        # face + beard as an ellipse (not a box): text beside the jaw stays erasable
        cx, cy = (x + w / 2) / k, ((y - 0.25 * h) + beard) / 2 / k
        ax, ay = 0.56 * w / k, (beard - (y - 0.25 * h)) / 2 / k
        cv2.ellipse(g, (int(cx), int(cy)), (int(ax), int(ay)), 0, 0, 360, 1, -1)
    return g


def candidates(rgb, boxes, p, t=0.0):
    """Pixels that look like old-caption glyphs in this frame (before the timing and shape tests).
    Computed only on the rows the boxes span (+ margin): ~3x faster on a caption band."""
    H, W = rgb.shape[:2]
    if not boxes:
        return np.zeros((H, W), np.uint8)
    ya = max(0, min(b[1] for b in boxes) - 40)
    yb = min(H, max(b[3] for b in boxes) + 40)
    out = np.zeros((H, W), np.uint8)
    guard = face_guard(rgb, p) if p.get("protect_faces", True) else None
    out[ya:yb] = _candidates(rgb[ya:yb], [(x0, y0 - ya, x1, y1 - ya) for x0, y0, x1, y1 in boxes], p, t, ya, H)
    if guard is not None:
        out *= 1 - guard
    return out


def _candidates(rgb, boxes, p, t, y_off, H):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    bright = ((v >= p["v_min"]) & (s <= p["s_max"])).astype(np.uint8)
    if p.get("contrast"):
        # soft-shadow captions (batch 3): a glyph pixel is clearly brighter than the darkest pixel a few px away
        # (its own shadow / the background), so smooth white areas (shirt, pants, walls) drop out
        r = int(round((p["r_dark"] * 2 + 3) * p.get("_scale", 1.0))) | 1
        local_min = cv2.erode(v, np.ones((r, r), np.uint8))
        near_dark = ((v.astype(np.int16) - local_min) >= p["contrast"]).astype(np.uint8)
    else:
        near_dark = cv2.dilate((v <= p["dark_max"]).astype(np.uint8), np.ones((2 * p["r_dark"] + 1,) * 2, np.uint8))
    cand = bright & near_dark
    if any(a <= t < b for a, b in p.get("color_only", [])):  # white rule off (paper documents, face close-ups)
        cand = np.zeros_like(cand)
    for hue in p.get("colors", []):  # caption colours used by this video (keywords), with the same contrast test
        lo, hi, smin, vmin = {"blue": (98, 122, 120, 90), "red": (0, 6, 120, 60), "red2": (170, 180, 120, 60),
                          "dred": (165, 180, 150, 70)}[hue]
        col = ((h >= lo) & (h <= hi) & (s >= smin) & (v >= vmin)).astype(np.uint8)
        if hue == "dred":  # dark red caption words on a red garment: only the clearly darker-than-garment strokes
            col &= (v.astype(np.int16) < cv2.blur(v, (41, 41)).astype(np.int16) - p.get("dred_dv", 28)).astype(np.uint8)
            col = cv2.dilate(col, np.ones((3, 3), np.uint8))
        r = int(round((p["r_dark"] * 2 + 3) * p.get("_scale", 1.0))) | 1
        edge = ((cv2.dilate(v, np.ones((r, r), np.uint8)).astype(np.int16) - v) >= 40) | \
               ((v.astype(np.int16) - cv2.erode(v, np.ones((r, r), np.uint8))) >= 40)
        cand |= (col & edge.astype(np.uint8)) * 2  # bit 2: coloured words, shape-tested on their own
    for t0, t1, hue in p["color_windows"]:  # coloured caption words, only where a colour scan found static text
        if t0 <= t < t1:
            lo, hi, smin, vmin = {"blue": (105, 118, 170, 110), "brown": (5, 25, 150, 90)}[hue]
            cand |= ((h >= lo) & (h <= hi) & (s >= smin) & (v >= vmin)).astype(np.uint8)
    if p.get("big_dark"):
        # bright pixels bordering a LARGE dark shape (a printed logo, hair, a dark garment) are not caption glyphs:
        # a caption's shadow is only a few px thick and vanishes under a morphological opening
        k = p["big_dark"]
        dark = (v.astype(np.int16) < cv2.blur(v, (31, 31)).astype(np.int16) - 35).astype(np.uint8)
        big = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        cand *= 1 - cv2.dilate(big, np.ones((9, 9), np.uint8))
    region = np.zeros_like(cand)
    for x0, y0, x1, y1 in boxes:
        region[max(y0, int(p["y_min"] * H) - y_off, 0):y1, x0:x1] = 1
    return cand * region


def final_mask(prev, cur, nxt, p):
    """White glyphs (bit 1) and coloured words (bit 2) are tested separately, so a coloured garment fold can't merge
    with a white caption line into one rejected shape."""
    out = np.zeros(cur.shape, np.uint8)
    for bit in (1, 2):
        if (cur & bit).any():
            out |= _final_mask(((prev & bit) > 0).astype(np.uint8), ((cur & bit) > 0).astype(np.uint8),
                               ((nxt & bit) > 0).astype(np.uint8), dict(p, _colorbit=(bit == 2)))
    return out


def _final_mask(prev, cur, nxt, p):
    """Old captions are fixed on screen; clothing stripes and edges move. Keep a candidate only if it is also a
    candidate a moment before OR after (OR: a caption's first and last frames still pass), then judge the shapes."""
    cand = cur & (prev | nxt) if p["persist"] else cur
    if not cand.any():
        return cand
    k = p.get("_scale", 1.0)  # pixel sizes below are for 720 px wide video
    sz = lambda v: max(1, int(round(v * k)))
    persisted = cand
    if p.get("strokes") and not p.get("_colorbit"):
        # text rows are dense with short strokes; a logo outline or a garment edge crosses a row only once or twice.
        # Count stroke starts within +-40 px on the same row (+-2 rows) and keep candidates with enough of them.
        starts = (cand & (1 - np.roll(cand, 1, axis=1))).astype(np.float32)
        dens = cv2.boxFilter(starts, -1, (sz(81) | 1, 5), normalize=False)
        cand = cand & (dens >= p["strokes"]).astype(np.uint8)
        if not cand.any():
            return cand
    def text_like(w, h, dens):
        return sz(p["h_min"]) <= h <= sz(p["h_max"]) and w >= sz(p["w_min"]) and p["dens_min"] <= dens <= p["dens_max"]

    def clusters(px, jy):
        joined = cv2.dilate(px, cv2.getStructuringElement(cv2.MORPH_RECT, (sz(p["join_x"]), jy)))
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
                if w2 >= 3 * sz(p["w_min"]) and text_like(w2, h2, sub2.sum() / max(1, w2 * h2)):
                    m[y + y2:y + y2 + h2, x + x2:x + x2 + w2] |= sub2
    # dots and small marks right next to kept letters belong to them
    # (taken from the persisted candidates BEFORE the stroke test: isolated dots fail it)
    if m.any():
        m |= persisted & cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (sz(21) | 1,) * 2))
    # take the outline / shadow / antialiased edge with the glyph
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * sz(p["grow"]) + 1,) * 2))
    # fill the inside of letters (counters) that are bright-ish but missed by the threshold
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    return m * 255


PARAMS = {"v_min": 200, "s_max": 70, "dark_max": 90, "r_dark": 3, "join_x": 15, "join_y": 3, "h_min": 8, "h_max": 200,
          "w_min": 10, "dens_min": 0.08, "dens_max": 0.75, "grow": 4, "radius": 6, "persist": 0.15, "y_min": 0.0,
          "color_windows": []}


def inpaint(rgb, m):
    if not m.any():
        return rgb
    ys = np.nonzero(m.any(axis=1))[0]
    ya, yb = max(0, ys[0] - 20), min(m.shape[0], ys[-1] + 21)  # only the rows around the mask
    out = rgb.copy()
    patch = cv2.inpaint(cv2.cvtColor(rgb[ya:yb], cv2.COLOR_RGB2BGR), m[ya:yb], PARAMS["radius"], cv2.INPAINT_TELEA)
    out[ya:yb] = cv2.cvtColor(patch, cv2.COLOR_BGR2RGB)
    return out


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
    ap.add_argument("--covers", default=None, help="covers JSON (instead of edit.json covers)")
    a = ap.parse_args()
    P = Path(a.project)
    cov_src = json.loads(Path(a.covers).read_text()) if a.covers else json.loads((P / "edit.json").read_text()).get("covers", [])
    covers = [c for c in cov_src if c.get("src", "main") == "main"]
    p = dict(PARAMS)
    pf = P / "erase_params.json"
    if pf.exists():
        p.update(json.loads(pf.read_text()))
    p.update(json.loads(a.params) if a.params else {})  # command-line overrides win over the project file
    src = P / a.src
    W, H, num, den, nb = probe(src)
    p["_scale"] = W / 720
    D = max(1, round(p["persist"] * num / den))  # frames before/after for the timing test
    fps = num / den
    cand_at = lambda rgb, t: candidates(rgb, boxes_at(covers, t, W, H, full_width=p.get("full_width", True)), p, t)
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
    # static_masks [[t0, t1, t_ref], ...]: an old caption that sits still from t0 to t1 is erased in every frame of that
    # span with the glyph mask measured at t_ref (a frame where nothing crosses it), e.g. when his hand moves through
    # the words and the per-frame shape test drops them (b3-01, 26.3-28.1 s)
    ref_masks = []
    for t0, t1, tr in p.get("static_masks", []):
        fr = list(read_frames(src, W, H, ss=max(0.0, tr - D / fps), count=2 * D + 1))
        cs = [cand_at(f, tr + (k - D) / fps) for k, f in enumerate(fr)]
        ref_masks.append((t0, t1, final_mask(cs[0], cs[D], cs[-1], p)))
    frames, cands = [], []
    zero = np.zeros((H, W), np.uint8)
    i = touched = written = 0
    L = round(p.get("static_s", 0) * fps)  # props/prints fixed on screen this long are not captions
    D2 = max(D, L)

    def emit(j):  # write frame j once its neighbours j-D2 .. j+D2 are known
        nonlocal touched, written
        k = j - (i - len(frames))  # index into the buffer
        prev = cands[k - D] if k - D >= 0 else zero
        nxt = cands[k + D] if k + D < len(cands) else zero
        cur = cands[k]
        if L and k - L >= 0 and k + L < len(cands):
            static = (cands[k - L] > 0) & (cands[k + L] > 0)
            static = cv2.dilate(static.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            cur = cur * (~static)
        m = final_mask(prev, cur.astype(np.uint8), nxt, p)
        tj = (i - len(frames) + k) / fps
        for t0, t1, rm in ref_masks:
            if t0 <= tj < t1:
                m = np.maximum(m, rm)
        # force_color [[t0, t1, "blue", [x0, y0, x1, y1]]]: every pixel of a caption colour in that box is old text
        # (the last strokes of a coloured word that the shape tests drop), grown 4 px
        for t0, t1, hue, (bx0, by0, bx1, by1) in p.get("force_color", []):
            if t0 <= tj < t1:
                lo, hi = {"blue": (98, 124)}[hue]
                y0, y1, x0, x1 = int(by0 * H), int(by1 * H), int(bx0 * W), int(bx1 * W)
                hsv = cv2.cvtColor(frames[k][y0:y1, x0:x1], cv2.COLOR_RGB2HSV)
                fm = ((hsv[..., 0] >= lo) & (hsv[..., 0] <= hi) & (hsv[..., 1] >= 90) & (hsv[..., 2] >= 60)).astype(np.uint8)
                fm = cv2.dilate(fm, np.ones((9, 9), np.uint8))
                m = m.copy()
                m[y0:y1, x0:x1] = np.maximum(m[y0:y1, x0:x1], fm * m.max() if m.max() else fm)
        touched += bool(m.any())
        wr.stdin.write(np.ascontiguousarray(inpaint(frames[k], m)).tobytes())
        written += 1

    for rgb in read_frames(src, W, H):
        frames.append(rgb)
        cands.append(cand_at(rgb, i / fps))
        i += 1
        j = i - 1 - D2  # frame whose look-ahead is now complete
        if j >= 0:
            emit(j)
            if len(frames) > 2 * D2 + 1:
                frames.pop(0)
                cands.pop(0)
        if i % 600 == 0:
            print(f"{i}/{nb} frames", file=sys.stderr, flush=True)
    for j in range(max(0, i - D2), i):
        emit(j)
    wr.stdin.close()
    wr.wait()
    print(json.dumps({"out": str(dst), "frames": written, "source_frames": nb, "frames_cleaned": touched, "persist_frames": D}))
    if written != nb or wr.returncode:
        sys.exit(1)


if __name__ == "__main__":
    main()
