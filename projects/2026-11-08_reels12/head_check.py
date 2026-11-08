"""Head check for the HDR run edits (the studio's tools/head_check.py works on Remotion props; this pipeline has its own layers).

For sampled frames: YuNet finds his face in the final video (HLG tone-mapped for detection only); the forbidden zone is the face box
grown for hair and beard plus the whole column above it. The overlay layer of that same frame (work/<name>/ov/f_NNNNN.png, the only
place graphics live) must have no visible pixel inside the zone. The end card (full-frame artwork, no footage) is skipped.

    .venv/bin/python projects/2026-11-08_run8k/head_check.py v1_me_reedit [--every 5]
"""
import json, subprocess, sys
from pathlib import Path
import cv2, numpy as np
from PIL import Image

P = Path(__file__).resolve().parent
name = sys.argv[1]
every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 5
spec = json.loads((P / "work" / name / "overlay_spec.json").read_text())
end_f = int(round(spec["end"]["at"] * 30))
video = P / "renders" / (f"{name}.mp4" if "--preview" not in sys.argv else f"{name}_preview.mp4")
det = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (540, 960), 0.7, 0.3, 50)
cmd = ["ffmpeg", "-v", "error", "-i", str(video), "-vf",
       f"select=not(mod(n\\,{every})),zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
       "zscale=t=bt709:m=bt709:r=tv,format=bgr24,scale=540:960", "-fps_mode", "passthrough", "-f", "rawvideo", "-"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
fsz = 540 * 960 * 3
bad, checked, faces_found, n = [], 0, 0, 0
while True:
    buf = proc.stdout.read(fsz)
    if len(buf) < fsz:
        break
    fi = n * every; n += 1
    if fi >= end_f:
        continue
    img = np.frombuffer(buf, np.uint8).reshape(960, 540, 3)
    _, faces = det.detect(img)
    checked += 1
    if faces is None:
        continue
    faces_found += 1
    x, y, w, h = (max(faces, key=lambda f: f[2] * f[3])[:4] * 2).tolist()
    zx0, zx1 = int(x - 0.25 * w), int(x + 1.25 * w)          # face box grown for hair / ears
    zy1 = int(y + h * 1.22)                                      # down to the beard / chin
    ov = np.asarray(Image.open(P / "work" / name / "ov" / f"f_{fi:05d}.png"))[:, :, 3]
    zone = ov[0:max(0, zy1), max(0, zx0):min(1080, zx1)]
    hit = int((zone > 24).sum())
    if hit > 40:
        ys, xs = np.where(zone > 24)
        bad.append({"frame": fi, "t": round(fi / 30, 2), "pixels": hit, "lowest_text_y_in_zone": int(ys.max()), "chin_y": zy1})
proc.wait()
out = {"name": name, "sampled": checked, "with_face": faces_found, "violations": bad}
(P / "work" / name / "head_check.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: (v if k != "violations" else v[:12]) for k, v in out.items()}, indent=1))
print("CLEAN" if not bad else f"{len(bad)} frame(s) with text on or above his head")
sys.exit(1 if bad else 0)
