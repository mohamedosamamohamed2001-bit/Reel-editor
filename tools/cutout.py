#!/usr/bin/env python3
"""Person cut-outs for behind-the-head titles: RGBA PNGs of plate frames, alpha = MODNet portrait matte.

    .venv/bin/python tools/cutout.py PLATE_DIR OUT_DIR --frames A-B[,C-D...]

PLATE_DIR holds the clip's JPEG plate frames (00001.jpg ...) exactly as the studio shows them; frame indices are
1-based plate indices. The PNG keeps the plate's pixels and size, so the studio can draw it with the same geometry
(zoom, settle, whips) above a title: the title then sits behind him. Model: MODNet (Apache-2.0, ONNX from
huggingface.co/Xenova/modnet, cached in ~/.cache/osm-models/modnet.onnx), CPU ~0.7 s/frame at 512 px.
The matte is smoothed over time (EMA 0.35) so its edge doesn't shimmer, and cached per frame (existing PNGs are kept).
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

MODEL = Path.home() / ".cache/osm-models/modnet.onnx"


def matte(sess, rgb):
    h, w = rgb.shape[:2]
    ih = 896 if h >= w else 512
    iw = int(round(ih * w / h / 32) * 32)
    x = (cv2.resize(rgb, (iw, ih), interpolation=cv2.INTER_AREA).astype(np.float32) / 127.5 - 1).transpose(2, 0, 1)[None]
    m = sess.run(None, {"input": x})[0][0, 0]
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("out")
    ap.add_argument("--frames", required=True)
    a = ap.parse_args()
    plate, out = Path(a.plate), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    idx = []
    for part in a.frames.split(","):
        lo, hi = map(int, part.split("-"))
        idx += list(range(lo, hi + 1))
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    prev = None
    for i in sorted(set(idx)):
        dst = out / f"{i:05d}.png"
        src = plate / f"{i:05d}.jpg"
        if not src.exists():
            continue
        bgr = cv2.imread(str(src))
        m = matte(sess, cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        if prev is not None and prev.shape == m.shape:
            m = 0.65 * m + 0.35 * prev
        prev = m
        if dst.exists():
            continue
        # firm up the matte's soft halo a little (keeps hair edges, drops faint background ghosts)
        a8 = np.clip((m - 0.08) / 0.84 * 255, 0, 255).astype(np.uint8)
        cv2.imwrite(str(dst), np.dstack([bgr, a8]), [cv2.IMWRITE_PNG_COMPRESSION, 1])
    print(f"cut-outs: {len(set(idx))} frames -> {out}")


if __name__ == "__main__":
    main()
