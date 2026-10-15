"""Head check: is any text on or above Coach Osama's head? (Coach Osama 2026-10-15: never text on / above his head.)

    .venv/bin/python tools/head_check.py projects/<p> [--every 2] [--scale 0.25]

Uses the props of the project's last render (renders/_props.json) and renders two low-res QA passes with ReelEdit's
`debugLayer`: "text" (captions + text overlays alone on black) and "footage" (everything else: his picture, cards,
full-screen images, title cards). YuNet finds his face in the footage pass; the forbidden zone is the head (face box
grown for hair and beard) plus the whole column above it. Every sampled frame where text pixels fall in that zone is
reported with the overlays on screen at that moment. Writes renders/_head_check.json. Exit code 1 if anything is found.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
TEXT_TYPES = {"kineticTitle", "iconPop", "stepBadge", "lowerLabel", "checklist", "trackedLabel", "callout", "exerciseTitle"}


def render(props, mode, out, scale):
    p = dict(props)
    p["edit"] = dict(props["edit"], debugLayer=mode)
    pf = out.with_suffix(".json")
    pf.write_text(json.dumps(p, ensure_ascii=False))
    subprocess.run(["npx", "remotion", "render", "src/index.ts", "ReelEdit", str(out), f"--props={pf}", "--concurrency=4",
                    "--log=error", "--muted", f"--scale={scale}"], cwd=STUDIO, check=True)
    pf.unlink()


def frames(path, w, h, ch):
    pix = "gray" if ch == 1 else "bgr24"
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", pix, "-"], stdout=subprocess.PIPE)
    n = w * h * ch
    while True:
        b = pr.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape((h, w) if ch == 1 else (h, w, ch))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--every", type=int, default=2, help="check every Nth frame")
    ap.add_argument("--scale", type=float, default=0.25)
    ap.add_argument("--reuse-footage", action="store_true", help="reuse the kept footage pass (only the text moved)")
    ap.add_argument("--keep", action="store_true", help="keep the QA renders")
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    props = json.loads((proj / "renders/_props.json").read_text())
    edit = props["edit"]
    fps, W, H = edit["fps"], edit["width"], edit["height"]
    w, h = int(W * a.scale), int(H * a.scale)
    tmp = proj / "renders/_headcheck"
    tmp.mkdir(exist_ok=True)
    vt, vf = tmp / "text.mp4", tmp / "footage.mp4"
    if not (a.reuse_footage and vf.exists()):
        render(props, "footage", vf, a.scale)
    render(props, "text", vt, a.scale)

    det = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (w * 2, h * 2), 0.75, 0.3, 50)
    overlays = [o for o in edit["overlays"] if o["type"] in TEXT_TYPES and not o.get("backdrop")]
    zones = (edit.get("captions") or {}).get("zones", [])
    hits, chin, hx, face_log = [], {}, {}, []
    boxes = {i: None for i in range(len(overlays))}  # each text overlay's measured box (output px), from frames it is alone
    for i, (ft, ff) in enumerate(zip(frames(vt, w, h, 1), frames(vf, w, h, 3))):
        if i % a.every:
            continue
        t = i / fps
        text = ft > 40  # text layers on pure black (H.264 noise stays far below this)
        z = next((z for z in zones if z["at"] - 0.005 <= t < z["at"] + z["dur"]), None)
        cap_y = int((z["top"] if z else 0.6) * h) - 3  # the caption bar starts at its zone top
        on = [k for k, o in enumerate(overlays) if o["at"] <= t < o["at"] + o["dur"]]
        if len(on) == 1:
            ys, xs = np.nonzero(text[:cap_y])
            if len(ys):
                bb = [xs.min(), ys.min(), xs.max() + 1, ys.max() + 1]
                old = boxes[on[0]]
                boxes[on[0]] = bb if old is None else [min(old[0], bb[0]), min(old[1], bb[1]), max(old[2], bb[2]), max(old[3], bb[3])]
        _, faces = det.detect(cv2.resize(ff, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC))
        if faces is None:
            continue
        for fx, fy, fw, fh, *_ in faces / 2:
            # his face only: not tiny (background people / photos), face-shaped (hands and shirt prints fail this)
            if fw < w * 0.06 or not 0.6 < fw / fh < 1.15:
                continue
            face_log.append([round(t, 2)] + [round(v / a.scale) for v in (fx, fy, fx + fw, fy + fh)])
            x0, x1 = int(max(0, fx - 0.2 * fw)), int(min(w, fx + 1.2 * fw))
            y1 = int(min(h, fy + 1.2 * fh))  # chin + beard; everything above (hair and the air above the head) is out
            for k in on:
                chin[k] = max(chin.get(k, 0), y1)
                hx[k] = [min(hx.get(k, [w, 0])[0], x0), max(hx.get(k, [w, 0])[1], x1)]
            n_ov = int(text[:min(y1, cap_y), x0:x1].sum())
            n_cap = int(text[cap_y:y1, x0:x1].sum()) if y1 > cap_y else 0
            if n_ov + n_cap > 6:
                hits.append({"t": round(t, 2), "px": n_ov + n_cap, "captions": n_cap > 6, "head": [round(v / a.scale) for v in (x0, 0, x1, y1)],
                             "zone": [x0, 0, x1, min(y1, cap_y)], "overlays": [k for k in on if n_ov > 6]})
            break
    S = 1 / a.scale
    for x in hits:  # blame only the overlays whose own box reaches into the zone (unknown box: blame it)
        zx0, zy0, zx1, zy1 = x.pop("zone")
        x["overlays"] = [k for k in x["overlays"] if boxes[k] is None or
                         (boxes[k][0] < zx1 and boxes[k][2] > zx0 and boxes[k][1] < zy1)]
    hits = [x for x in hits if x["overlays"] or x["captions"]]
    report = []
    for k, o in enumerate(overlays):
        ts = [x["t"] for x in hits if k in x["overlays"]]
        if not ts:
            continue
        bb = boxes[k]
        report.append({"index": edit["overlays"].index(o), "type": o["type"], "at": o["at"], "dur": o["dur"], "top": o.get("top"),
                       "label": o["lines"][0]["text"] if o["type"] == "kineticTitle" else o.get("label") or o.get("title") or "",
                       "frames": len(ts), "from": min(ts), "to": max(ts), "chin_y": round(chin.get(k, 0) * S) / H,
                       "head_x": [round(v * S) for v in hx.get(k, [0, w])],
                       "box": [round(v * S) for v in bb] if bb is not None else None})
    caps = [x["t"] for x in hits if x["captions"]]
    out = proj / "renders/_head_check.json"
    out.write_text(json.dumps({"overlays": report, "caption_hits": caps, "frames": hits, "faces": face_log}, ensure_ascii=False, indent=1))
    for r in report:
        print(f"  {r['from']:6.2f}-{r['to']:6.2f}s {r['frames']:3d}f  #{r['index']} {r['type']} top={r['top']} chin={r['chin_y']:.3f} box={r['box']}  {r['label']}")
    if caps:
        print(f"  captions on the head: {len(caps)} frames, {min(caps):.2f}-{max(caps):.2f}s")
    print(f"{proj.name}: {len(hits)} frame(s) with text on/above the head" if hits else f"{proj.name}: clean")
    if not a.keep:
        shutil.rmtree(tmp)
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
