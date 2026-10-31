#!/usr/bin/env python3
"""Colour scopes + numbers for grading decisions (docs/COLOR_GRADING.md).

    .venv/bin/python tools/scopes.py IMAGE_OR_VIDEO [--t 1.5] [--out DIR]     metrics JSON + scope sheet (waveform, RGB parade,
                                                                              vectorscope, histogram) for a still or one frame
Metrics are measured on display-referred sRGB (BT.709) pixels, i.e. what the viewer sees:
- exposure: luma percentiles p0.5 / p50 / p99.5, luma_clipped % (luma >= 250), clipped % (any channel >= 250: saturated colours
  hitting the channel limit lose texture too), crushed % (luma <= 4)
- contrast: RMS contrast of L*
- colour: mean chroma C* (Lab), Hasler-Suesstrunk colourfulness
- neutral cast: mean a*/b* of near-neutral pixels (C* < 12, 25 < L* < 92); b* > +3 reads yellow, a* < -3 green
- skin: Lab hue angle / chroma of skin pixels inside YuNet face boxes (natural skin ~ hue 40-65 deg, C* 14-34)
"""
import argparse, json, subprocess, sys
from pathlib import Path

import cv2
import numpy as np

YUNET = Path.home() / ".cache/osm-models/yunet.onnx"


def lab(rgb8):
    l = cv2.cvtColor(rgb8, cv2.COLOR_RGB2LAB).astype(np.float32)
    return l[..., 0] * 100 / 255, l[..., 1] - 128, l[..., 2] - 128


def faces(rgb8):
    if not YUNET.exists():
        return []
    h, w = rgb8.shape[:2]
    s = 640 / max(h, w)
    small = cv2.resize(rgb8, (int(w * s), int(h * s)))
    d = cv2.FaceDetectorYN.create(str(YUNET), "", (small.shape[1], small.shape[0]), 0.7, 0.3, 20)
    _, f = d.detect(cv2.cvtColor(small, cv2.COLOR_RGB2BGR))
    return [] if f is None else [[int(v / s) for v in r[:4]] for r in f]


def metrics(rgb8):
    rgb = rgb8.astype(np.float32)
    y = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    L, A, B = lab(rgb8)
    C = np.hypot(A, B)
    rg, yb = rgb[..., 0] - rgb[..., 1], 0.5 * (rgb[..., 0] + rgb[..., 1]) - rgb[..., 2]
    colorful = float(np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean()))
    neu = (C < 12) & (L > 25) & (L < 92)
    m = {
        "luma_p0_5": round(float(np.percentile(y, 0.5)), 1), "luma_p50": round(float(np.percentile(y, 50)), 1),
        "luma_p99_5": round(float(np.percentile(y, 99.5)), 1),
        "clipped_pct": round(float((rgb8.max(axis=2) >= 250).mean() * 100), 2), "luma_clipped_pct": round(float((y >= 250).mean() * 100), 2), "crushed_pct": round(float((y <= 4).mean() * 100), 2),
        "contrast_rms": round(float(L.std()), 1), "chroma_mean": round(float(C.mean()), 1), "colourfulness": round(colorful, 1),
        "neutral_px_pct": round(float(neu.mean() * 100), 1),
        "neutral_a": round(float(A[neu].mean()), 2) if neu.any() else None, "neutral_b": round(float(B[neu].mean()), 2) if neu.any() else None,
    }
    sk = []
    for x, y0, w, h in faces(rgb8):
        x0, x1, y1, y2 = max(0, x + w // 5), min(rgb8.shape[1], x + w * 4 // 5), max(0, y0 + h // 2), min(rgb8.shape[0], y0 + h * 9 // 10)
        if x1 <= x0 or y2 <= y1:
            continue
        a, b, l = A[y1:y2, x0:x1], B[y1:y2, x0:x1], L[y1:y2, x0:x1]
        k = (l > 20) & (l < 95) & (np.hypot(a, b) > 6)            # cheeks / lower face, no shadows or speculars
        if k.sum() > 50:
            sk.append((float(np.degrees(np.arctan2(b[k].mean(), a[k].mean()))), float(np.hypot(a[k].mean(), b[k].mean()))))
    if sk:
        m["skin_hue"] = round(float(np.mean([s[0] for s in sk])), 1)
        m["skin_chroma"] = round(float(np.mean([s[1] for s in sk])), 1)
    return m


def read_frame(path, t=None, vf="format=rgb24"):
    if Path(path).suffix.lower() in (".png", ".jpg", ".jpeg"):
        return cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                                    path], capture_output=True, text=True).stdout.split(",")[:2])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t or 0), "-i", path, "-frames:v", "1", "-vf", vf + ",format=rgb24",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    n = len(raw) // 3
    hh = int(round((n / (w * h)) ** 0.5 * h)) if n != w * h else h
    ww = n // hh
    return np.frombuffer(raw, np.uint8).reshape(hh, ww, 3)


def scope_sheet(png, dst):
    """waveform (luma), RGB parade, vectorscope, histogram of an sRGB still -> one image"""
    g = ("[0:v]format=rgb24,split=4[a][b][c][d];"
         "[a]format=yuv444p,waveform=mode=column:components=1:display=overlay:intensity=0.12:graticule=green:flags=numbers,format=rgb24,scale=512:256,setsar=1[w];"
         "[b]waveform=mode=column:components=7:display=parade:intensity=0.12:graticule=green,format=rgb24,scale=512:256,setsar=1[p];"
         "[c]format=yuv444p,vectorscope=mode=color3:graticule=color:intensity=0.08,format=rgb24,scale=256:256,setsar=1[v];"
         "[d]format=gbrp,histogram=display_mode=overlay:levels_mode=linear,format=rgb24,scale=256:256,setsar=1[h];"
         "[v][h]hstack[vh];[w][p][vh]vstack=inputs=3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-filter_complex", g, "-frames:v", "1", str(dst)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--t", type=float, default=None)
    ap.add_argument("--vf", default="format=rgb24", help="ffmpeg chain applied before measuring (e.g. a grade)")
    ap.add_argument("--out")
    a = ap.parse_args()
    img = read_frame(a.src, a.t, a.vf)
    m = metrics(img)
    print(json.dumps(m))
    if a.out:
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out / "frame.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        scope_sheet(out / "frame.png", out / "scopes.png")
        (out / "metrics.json").write_text(json.dumps(m, indent=1))


if __name__ == "__main__":
    main()
