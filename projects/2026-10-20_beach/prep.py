"""Beach carousel prep: 4:5 crop + Lanczos resize of the sRGB copies (no colour change), YuNet face box, MODNet body extent."""
import json, sys
from pathlib import Path
import cv2, numpy as np, onnxruntime as ort
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from cutout import MODEL, matte
P = Path(__file__).resolve().parent
CROPS = json.loads((P / "crops.json").read_text())  # [[n, src, vy]]
sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
det = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (540, 675), 0.5, 0.3, 50)
info = {}
for n, src, vy in CROPS:
    im = cv2.imread(str(P / "work" / f"{src}.png")); H, W = im.shape[:2]
    ch = int(round(W * 5 / 4)); y0 = int(round((H - ch) * vy))
    out = cv2.resize(im[y0:y0 + ch], (1080, 1350), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(str(P / "work" / f"bg_{n}.png"), out)
    det.setInputSize((540, 675)); _, fs = det.detect(cv2.resize(out, (540, 675)))
    m = matte(sess, cv2.cvtColor(out, cv2.COLOR_BGR2RGB)) > 0.5
    k, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8); m = lab == 1 + np.argmax(st[1:, 4])
    rows = {y: [int(v) for v in np.where(m[y:y + 50].any(0))[0][[0, -1]]] for y in range(0, 1350, 50) if m[y:y + 50].any()}
    info[n] = {"src": src, "face": [int(v * 2) for v in fs[0][:4]] if fs is not None else None, "rows": rows}
    print(n, src, "face", info[n]["face"], " ".join(f"{y}:{a}-{b}" for y, (a, b) in rows.items() if y % 100 == 0))
(P / "work" / "layout_info.json").write_text(json.dumps(info))
