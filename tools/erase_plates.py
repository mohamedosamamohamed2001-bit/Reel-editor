#!/usr/bin/env python3
"""Erase burned-in SOLID caption plates (e.g. brand-blue boxes with white words) from a finished video.

    .venv/bin/python tools/erase_plates.py SRC OUT [--test t1,t2,...] [--cuts f1,f2,...]

tools/erase_text.py rebuilds thin glyph strokes from their neighbours; a solid plate is far too big for that
(inpainting a 400x400 px box smears). Here:
  1. Mask: plate pixels by colour (saturated light blue, hue ~205-225 deg), holes closed (the white words inside)
     and grown 5 px (anti-aliased edges). Faces are never touched (YuNet face guard).
  2. Fill, per shot (tripod camera): "nearest" = each pixel from the nearest frame where it is uncovered (best for
     exercise demos over the floor); "median" (--median-shots) = a clean background plate, the per-pixel median over
     the uncovered frames (people moving through drop out). Check the --test stills and choose per shot.
  3. Whatever no frame of the shot ever shows (a plate on screen for the whole shot) is inpainted (OpenCV Telea).
Shot boundaries come from --cuts (frame numbers) or from a frame-difference scan. Output: same size, frame rate
and frame count, x264 CRF 10. The source is never modified. --test writes before/after/mask PNGs instead.
"""
import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np


def probe(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(src)],
                         capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h = int(out[0]), int(out[1])
    num, den = map(int, out[2].split("/"))
    return w, h, num, den


def read_frames(src, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3).copy()


_FACE = None


def face_mask(bgr, neck=0.5, min_score=0.6):
    global _FACE
    H, W = bgr.shape[:2]
    k = 360 / W
    sw, sh = 360, int(round(H * k))
    if _FACE is None:
        _FACE = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (sw, sh), 0.6, 0.3, 50)
    _FACE.setInputSize((sw, sh))
    _, faces = _FACE.detect(cv2.resize(bgr, (sw, sh)))
    m = np.zeros((H, W), np.uint8)
    for f in faces if faces is not None else []:
        if f[-1] < min_score:  # a blurred hand can score ~0.7
            continue
        x, y, w, h = (f[:4] / k).astype(int)
        cv2.rectangle(m, (x - w // 3, y - h // 3), (x + w + w // 3, y + h + int(h * neck)), 1, -1)  # face + beard + neck
    return m


def plate_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    blue = ((h >= 100) & (h <= 114) & (s >= 95) & (v >= 170)).astype(np.uint8)
    # only plate-sized solid regions (not a blue sticker or a shirt print): keep components of >= 1500 px
    n, lab, stats, _ = cv2.connectedComponentsWithStats(blue, 8)
    keep = np.zeros_like(blue)
    for i in range(1, n):
        x, y, w, hh, a = stats[i]
        if a >= 1500 and a / (w * hh) >= 0.35:
            keep[lab == i] = 1
    # the words inside the plate: close the holes, then grow over the anti-aliased edge
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (31, 31)))
    filled = keep.copy()
    cnts, _ = cv2.findContours(keep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    return cv2.dilate(filled, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))


def find_cuts(frames, thr=12.0):
    cuts, prev = [], None
    for i, f in enumerate(frames):
        g = cv2.cvtColor(cv2.resize(f, (270, 480)), cv2.COLOR_BGR2GRAY)[:216].astype(np.float32)
        if prev is not None and float(np.mean(np.abs(g - prev))) > thr:
            cuts.append(i)
        prev = g
    return cuts


def fill_shot_nearest(frames, masks):
    """Each masked pixel <- the same pixel in the nearest frame of the shot where it is uncovered; the rest Telea.
    Best when the plate sits over the floor / background and people move a lot (exercise demos)."""
    n = len(frames)
    out = []
    for i in range(n):
        f, m = frames[i].copy(), masks[i].astype(bool)
        todo = m.copy()
        for k in range(1, n):
            if not todo.any():
                break
            for j in (i - k, i + k):
                if 0 <= j < n:
                    ok = todo & ~masks[j].astype(bool)
                    if ok.any():
                        f[ok] = frames[j][ok]
                        todo &= ~ok
        if todo.any():
            f = cv2.inpaint(f, todo.astype(np.uint8), 5, cv2.INPAINT_TELEA)
        out.append((f, m, todo))
    return out


def fill_shot_median(frames, masks, min_samples=3):
    """Tripod shots: a clean background plate per shot = per-pixel MEDIAN over the frames where that pixel is not
    covered (people who move through drop out of the median, so no ghost limbs). Every covered pixel takes the
    background plate; pixels the shot never shows uncovered (fewer than min_samples frames) are inpainted (Telea)."""
    n = len(frames)
    union = np.zeros(masks[0].shape, bool)
    for m in masks:
        union |= m.astype(bool)
    out = []
    if not union.any():
        return [(f.copy(), m.astype(bool), np.zeros(m.shape, bool)) for f, m in zip(frames, masks)]
    ys, xs = np.where(union)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    bg = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
    count = np.zeros((y1 - y0, x1 - x0), np.int32)
    for r0 in range(y0, y1, 64):  # row bands keep the stack in memory bounds
        r1 = min(y1, r0 + 64)
        st = np.stack([f[r0:r1, x0:x1] for f in frames]).astype(np.float32)
        mk = np.stack([m[r0:r1, x0:x1].astype(bool) for m in masks])
        st[mk] = np.nan
        bg[r0 - y0:r1 - y0] = np.nanmedian(st, axis=0) if (~mk).any() else 0
        count[r0 - y0:r1 - y0] = (~mk).sum(0)
    have = count >= min_samples
    bg = np.nan_to_num(bg).round().clip(0, 255).astype(np.uint8)
    for i in range(n):
        f = frames[i].copy()
        m = masks[i][y0:y1, x0:x1].astype(bool)
        use = m & have
        f[y0:y1, x0:x1][use] = bg[use]
        todo = np.zeros(masks[i].shape, bool)
        todo[y0:y1, x0:x1] = m & ~have
        if todo.any():
            f = cv2.inpaint(f, todo.astype(np.uint8), 5, cv2.INPAINT_TELEA)
        out.append((f, masks[i].astype(bool), todo))
    return out


def fill_shot_matched(frames, masks, reach=20, ring_px=24, max_err=7.0):
    """Handheld shots (selfies): each frame's whole plate area comes from ONE nearby frame where that area is fully
    uncovered, shifted onto this frame (phase correlation on a ring around the plate) and kept only if the ring then
    matches (mean abs error <= max_err): no patchwork from several frames, no pasted skin over the shirt when a hand
    passes. Otherwise (hand in front, fast motion) OpenCV Telea. Pasted with a feathered edge."""
    n = len(frames)
    out = []
    for i in range(n):
        f, m = frames[i].copy(), masks[i].astype(bool)
        todo = np.zeros(m.shape, bool)
        if m.any():
            ys, xs = np.where(m)
            pad = ring_px + 12
            y0, y1 = max(0, ys.min() - pad), min(m.shape[0], ys.max() + pad + 1)
            x0, x1 = max(0, xs.min() - pad), min(m.shape[1], xs.max() + pad + 1)
            mc = m[y0:y1, x0:x1].astype(np.uint8)
            ring = (cv2.dilate(mc, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ring_px + 1,) * 2)) > 0) & (mc == 0)
            gi = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
            win = cv2.createHanningWindow(gi.shape[::-1], cv2.CV_32F)
            best = None
            for k in range(1, reach + 1):
                for j in (i - k, i + k):
                    if not 0 <= j < n:
                        continue
                    grown = cv2.dilate(mc, np.ones((25, 25), np.uint8)) > 0
                    if (masks[j][y0:y1, x0:x1].astype(bool) & grown).any():
                        continue
                    gj = cv2.cvtColor(frames[j][y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
                    gi_r, gj_r = gi.copy(), gj.copy()
                    gi_r[~ring] = gi[ring].mean()
                    gj_r[~ring] = gj[ring].mean()
                    (dx, dy), _ = cv2.phaseCorrelate(gj_r, gi_r, win)
                    if abs(dx) > 24 or abs(dy) > 24:
                        continue
                    M = np.float32([[1, 0, dx], [0, 1, dy]])
                    sh = cv2.warpAffine(frames[j], M, (f.shape[1], f.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                    err = float(np.abs(sh[y0:y1, x0:x1].astype(np.float32) - f[y0:y1, x0:x1].astype(np.float32))[ring].mean())
                    if best is None or err < best[0]:
                        best = (err, sh)
                if best is not None and best[0] <= max_err * 0.6:
                    break
            if best is not None and best[0] <= max_err:
                src = best[1]
            else:
                src = cv2.inpaint(f, m.astype(np.uint8), 5, cv2.INPAINT_TELEA)
                todo = m
            a = cv2.GaussianBlur(cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32), (0, 0), 3)[..., None]
            f = (src.astype(np.float32) * a + f.astype(np.float32) * (1 - a)).round().clip(0, 255).astype(np.uint8)
        out.append((f, m, todo))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--test", default=None)
    ap.add_argument("--cuts", default=None)
    ap.add_argument("--neck", type=float, default=0.5, help="face guard below the chin, x face height (selfies: 0.15)")
    ap.add_argument("--face-score", type=float, default=0.6, help="min YuNet score for the face guard")
    ap.add_argument("--matched", action="store_true", help="handheld: one aligned frame per plate (fill_shot_matched)")
    ap.add_argument("--median-shots", default="", help="shot indices (0-based) filled from the median background plate")
    a = ap.parse_args()
    w, h, num, den = probe(a.src)
    fps = num / den
    frames = list(read_frames(a.src, w, h))
    cuts = [int(x) for x in a.cuts.split(",")] if a.cuts else find_cuts(frames)
    bounds = [0] + cuts + [len(frames)]
    masks = []
    for f in frames:
        m = plate_mask(f)
        m[face_mask(f, a.neck, a.face_score) > 0] = 0
        masks.append(m)
    result = [None] * len(frames)
    rest = 0
    for s0, s1 in zip(bounds, bounds[1:]):
        si = bounds.index(s0)
        fill = fill_shot_median if str(si) in a.median_shots.split(",") else fill_shot_matched if a.matched else fill_shot_nearest
        for k, (f, m, todo) in enumerate(fill(frames[s0:s1], masks[s0:s1])):
            result[s0 + k] = f
            rest += int(todo.sum())
    cov = sum(int(m.sum()) for m in masks)
    print(f"{len(frames)} frames, cuts {cuts}; masked px {cov}, inpainted (never visible in the shot) {rest} "
          f"({100 * rest / max(1, cov):.1f}%)")
    if a.test:
        od = Path(a.out)
        od.mkdir(parents=True, exist_ok=True)
        for t in a.test.split(","):
            i = min(len(frames) - 1, int(round(float(t) * fps)))
            cv2.imwrite(str(od / f"t{t}_before.png"), frames[i])
            cv2.imwrite(str(od / f"t{t}_after.png"), result[i])
            cv2.imwrite(str(od / f"t{t}_mask.png"), masks[i] * 255)
        return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                          "-r", f"{num}/{den}", "-i", "-", "-c:v", "libx264", "-crf", "10", "-preset", "medium",
                          "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          str(a.out)], stdin=subprocess.PIPE)
    for f in result:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    print("wrote", a.out)


if __name__ == "__main__":
    main()
