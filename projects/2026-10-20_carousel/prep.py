"""Carousel prep: 4:5 crop + resize (Lanczos, no colour change) of the sRGB working copies, MODNet person matte, YuNet face box."""
import json, sys
from pathlib import Path
import cv2, numpy as np, onnxruntime as ort
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from cutout import MODEL, matte
P = Path(__file__).resolve().parent
SLIDES = [("01", "IMG_1140", 0.5), ("02", "IMG_1253", 0.5), ("03", "IMG_2089", 0.5), ("04", "IMG_2093", 0.5), ("05", "IMG_2100", 0.5)]
if (P / "crops.json").exists():
    SLIDES = [(n, s, v) for n, s, v in json.loads((P / "crops.json").read_text())]
sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
det = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (540, 675), 0.7, 0.3, 50)
info = {}
for n, src, vy in SLIDES:
    im = cv2.imread(str(P / "work" / f"{src}.png"))
    H, W = im.shape[:2]; ch = int(round(W * 5 / 4)); y0 = int(round((H - ch) * vy))
    crop = im[y0:y0 + ch]
    out = cv2.resize(crop, (1080, 1350), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(str(P / "work" / f"bg_{n}.png"), out)
    m = matte(sess, cv2.cvtColor(cv2.resize(crop, (1080 * 2, 1350 * 2), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB))
    m = cv2.resize(m, (1080, 1350), interpolation=cv2.INTER_AREA)
    rgba = np.dstack([out, (np.clip(m, 0, 1) * 255).astype(np.uint8)])
    cv2.imwrite(str(P / "work" / f"person_{n}.png"), rgba)
    det.setInputSize((540, 675)); _, fs = det.detect(cv2.resize(out, (540, 675)))
    face = [int(v * 2) for v in fs[0][:4]] if fs is not None else None
    ys, xs = np.where(m > 0.5)
    info[n] = {"src": src, "crop_y0": y0, "face": face, "body": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]}
    print(n, src, info[n])
(P / "work" / "layout_info.json").write_text(json.dumps(info, indent=1))
