#!/usr/bin/env python3
"""OSM Instagram Reel cover: the mandatory last step of every video (docs/COVER_SYSTEM.md, Coach Osama 2026-11-01).

    .venv/bin/python tools/make_cover.py projects/<p>            reads projects/<p>/cover.json, writes renders/<p>_cover.{png,jpg}

cover.json:
  "frame":  {"media": "<edit.json media key>", "from": s, "to": s}   his shot as used in the edit (source seconds);
            the sharpest frame with a confident face is picked, and the clip's own grade from work/grades.json is applied.
            or {"image": "path"} (a photo from the edit, already sRGB), optional "time" to force one frame.
  "faceH":  face-box height on the canvas in px (YuNet box = brows-to-chin, no hair), default 300
  "faceTop": y of the face box top, default 400 (keeps hair + brackets inside the 3:4 grid crop, y 240)
  "eyebrow": "TOPIC × TOPIC" (Inter caps, × in Core Blue), "headline": [line, line] (his words / the video's hook),
  "accent": the ONE Core Blue word, "chips": [{"text": "41", "blue": true}], "sub": short Arabic line read after the chips
  ("chipSide": "left" puts the chips after the line instead). The wordmark sits top-left on a dark field, else under the chips.
  "layout": optional overrides {fadeStart, fadeEnd, eyebrowY, headSize, logo: [x, y]}

Checks (report in work/cover/report.json, exit 1 on a failure):
  1080x1920; every text/logo box inside the profile-grid crop (x 40-1040, y 240-1680); no text box in the column above or
  on his head (face box widened 25 %, from y 0 to the chin); the blue chip samples exactly #56A0FB; face not upscaled > 1.6x.
Never changes his face or body: crop, uniform scale, the reel's measured grade, nothing else.
"""
import json, shutil, subprocess, sys
from pathlib import Path

import os
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "motion/cover/cover.html"
W, H = 1080, 1920
GRID = (40, 240, 1040, 1680)
DEFAULT_LAYOUT = {"fadeStart": 960, "fadeEnd": 1230, "eyebrowY": 1180, "headSize": 134, "logo": [66, 262]}


cv2.setLogLevel(0) if hasattr(cv2, "setLogLevel") else None


def detector(w, h):
    return cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (w, h), 0.75, 0.3, 50)


def face_of(rgb):
    h, w = rgb.shape[:2]
    s = min(1.0, 1280 / max(w, h))
    small = cv2.resize(rgb, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    n, faces = detector(small.shape[1], small.shape[0]).detect(cv2.cvtColor(small, cv2.COLOR_RGB2BGR))
    if faces is None or not len(faces):
        return None
    f = max(faces, key=lambda r: r[2] * r[3])
    x, y, fw, fh = (f[:4] / s).tolist()
    return {"x": x, "y": y, "w": fw, "h": fh, "score": float(f[-1])}


def sharp(rgb, f):
    x0, y0 = max(0, int(f["x"])), max(0, int(f["y"]))
    crop = cv2.cvtColor(rgb[y0:int(f["y"] + f["h"]), x0:int(f["x"] + f["w"])], cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(crop, cv2.CV_64F).var()) if crop.size else 0.0


def grade_for(P, src, t0, t1):
    gj = P / "work/grades.json"
    if not gj.exists():
        return None
    best = None
    for v in json.loads(gj.read_text()).values():
        r = v.get("report", {})
        if Path(r.get("source", "")).resolve() == src.resolve() and r.get("range") and r["range"][0] <= t0 + 1e-3 and t1 <= r["range"][1] + 0.5:
            if best is None or "pchip" in v["grade"]:
                best = v["grade"]
    return best


def frames_from_video(P, spec, edit):
    src = (P / edit["media"][spec["media"]]).resolve()
    t0, t1 = spec.get("time", spec["from"]), spec.get("time", spec.get("to", spec["from"]))
    g = grade_for(P, src, spec["from"], spec.get("to", spec["from"]))
    vf = (g + "," if g else "") + "format=rgb24"
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                    "-of", "json", str(src)], capture_output=True, text=True).stdout)
    num, den = map(int, pr["streams"][0]["r_frame_rate"].split("/"))
    fps = num / den
    out = []
    step = max(1, round(fps / 30))
    tmp = P / "work/cover/frames"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    n = max(1, int(round((t1 - t0) * fps)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t0 - 0.25 / fps):.4f}", "-i", str(src), "-frames:v", str(-(-n // step)),
                    "-vf", f"select='not(mod(n\\,{step}))',{vf}", "-vsync", "vfr", str(tmp / "f%04d.png")], check=True)
    for i, p in enumerate(sorted(tmp.glob("f*.png"))):
        if t0 + i * step / fps > t1 + 1e-3:
            break
        out.append((t0 + i * step / fps, np.asarray(Image.open(p).convert("RGB"))))
    return out, str(src), g


def main():
    P = Path(sys.argv[1]).resolve()
    cfg = json.loads((P / "cover.json").read_text())
    edit = json.loads((P / "edit.json").read_text())
    work = P / "work/cover"
    work.mkdir(parents=True, exist_ok=True)
    fr = cfg["frame"]
    if "image" in fr:
        cands, src, g = [(0.0, np.asarray(Image.open(P / fr["image"]).convert("RGB")))], fr["image"], None
    else:
        cands, src, g = frames_from_video(P, fr, edit)
    scored = []
    for t, rgb in cands:
        f = face_of(rgb)
        if f and f["score"] > 0.8:
            scored.append((sharp(rgb, f), t, rgb, f))
    if not scored:
        sys.exit("no frame with a confident face")
    scored.sort(key=lambda s: -s[0])
    lap, t, rgb, f = scored[0]
    # place: uniform scale so the face box is faceH tall, face centred on x=540, face top at faceTop; never leave canvas bare
    faceH, faceTop = cfg.get("faceH", 300), cfg.get("faceTop", 400)
    ih, iw = rgb.shape[:2]
    s = max(faceH / f["h"], W / iw, H / ih)
    ox = min(0, max(W - iw * s, 540 - (f["x"] + f["w"] / 2) * s))
    oy = min(0, max(H - ih * s, faceTop - f["y"] * s))
    M = np.float32([[s, 0, ox], [0, s, oy]])
    canvas = cv2.warpAffine(rgb, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    Image.fromarray(canvas).save(work / "photo.png")
    face = {"x": f["x"] * s + ox, "y": f["y"] * s + oy, "w": f["w"] * s, "h": f["h"] * s}
    layout = dict(DEFAULT_LAYOUT, **cfg.get("layout", {}))
    if layout["logo"] != "bottom":     # the wordmark JPEG only works on a dark field (lighten blend): bright wall -> under the chips
        lx, ly = layout["logo"]
        if canvas[ly:ly + 62, lx:lx + 180].mean() > 70:
            layout["logo"] = "bottom"
            if "eyebrowY" not in cfg.get("layout", {}):     # make room under the chips, inside the grid crop
                layout["eyebrowY"] -= 80
                layout["fadeStart"] -= 80
                layout["fadeEnd"] -= 80
    page = {k: cfg.get(k) for k in ("eyebrow", "headline", "accent", "chips", "sub", "chipSide")}
    page.update(face=face, layout=layout)
    (work / "cfg.json").write_text(json.dumps(page, ensure_ascii=False, indent=1))
    shutil.copy(TEMPLATE, work / "piece.html")
    out = work / "render"
    subprocess.run(["node", str(ROOT / "tools/seek_render.js"), str(work / "piece.html"), str(out), "--stills", "0", "--dump", "window.boxes"],
                   check=True, capture_output=True)
    png = out / "t0.000.png"
    boxes = json.loads((out / "dump.json").read_text())
    img = np.asarray(Image.open(png).convert("RGB"))
    fails = []
    if img.shape[:2] != (H, W):
        fails.append(f"size {img.shape[1]}x{img.shape[0]}")
    hx0, hx1, chin = face["x"] - 0.125 * face["w"], face["x"] + 1.125 * face["w"], face["y"] + face["h"]
    for k, b in boxes.items():
        if not b or k == "blueChip":
            continue
        if b[0] < GRID[0] or b[1] < GRID[1] or b[2] > GRID[2] or b[3] > GRID[3]:
            fails.append(f"{k} outside the grid crop: {b}")
        if b[1] < chin and b[0] < hx1 and b[2] > hx0:
            fails.append(f"{k} in the head column: {b} vs face x {hx0:.0f}-{hx1:.0f}, chin {chin:.0f}")
    if boxes.get("blueChip"):
        x0, y0, x1, y1 = boxes["blueChip"]
        px = img[y0 + 4, x0 + 4]
        if tuple(int(v) for v in px) != (0x56, 0xA0, 0xFB):
            fails.append("blue chip is #%02X%02X%02X, not #56A0FB" % tuple(px))
    if s * 1.0 > 1.6 and "image" not in fr:
        fails.append(f"face upscaled {s:.2f}x (soft): use a closer frame or a smaller faceH")
    name = P.name
    dst = P / "renders"
    dst.mkdir(exist_ok=True)
    shutil.copy(png, dst / f"{name}_cover.png")
    Image.open(png).convert("RGB").save(dst / f"{name}_cover.jpg", quality=97, subsampling=0)
    grid = Image.open(png).crop((0, 240, 1080, 1680))
    sheet = Image.new("RGB", (540 + 405 + 30, 960 + 20), (40, 40, 40))
    sheet.paste(Image.open(png).resize((540, 960), Image.LANCZOS), (10, 10))
    sheet.paste(grid.resize((405, 540), Image.LANCZOS), (560, 10))
    sheet.save(work / "check_sheet.jpg", quality=92)
    rep = {"source": src, "time": round(t, 3), "grade": g, "face_sharpness": round(lap, 1), "scale": round(s, 3), "face": face,
           "boxes": boxes, "fails": fails, "outputs": [str(dst / f"{name}_cover.png"), str(dst / f"{name}_cover.jpg")], "sheet": str(work / "check_sheet.jpg")}
    (work / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(json.dumps({k: rep[k] for k in ("time", "scale", "face_sharpness", "fails", "outputs", "sheet")}, ensure_ascii=False, indent=1))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
