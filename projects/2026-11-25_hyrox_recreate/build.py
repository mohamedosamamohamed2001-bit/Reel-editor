""""Doctor: can you show me what you were doing when your lower back pain started" trend, HYROX version (Coach Osama 2026-11-25).

Reference (ref/screen.mp4, screen recording, reference only): one continuous shot, the athlete repeatedly heaving a heavy load on an
exam table while a doctor watches; caption at the top; the Reel plays 0.28-7.33 s of the recording (7.05 s) then loops.
His version: HIS HYROX Cairo sandbag lunges (IMG_5050, 120 fps: 20.25-23.25 s at 0.42x = real slow motion), cut out with MODNet
(largest person only) and composited on the desk of a REAL doctor's office (Mixkit #12913, free Mixkit licence, no AI): stock
cropped to a 9:16 window and mirrored so the doctor sits on the right like the reference, slowed 1.16x to the Reel length.
Contact shadow under his feet. Caption = the reference's line, Instagram-classic look (bold white, dark outline). HYROX only, no
other brands or sports. Sound: the trend's own audio from the recording; a silent copy for "Use audio".

    .venv/bin/python -I projects/2026-11-25_hyrox_recreate/build.py
"""
import json, subprocess, sys
from pathlib import Path
import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cutout import MODEL, matte  # noqa: E402

FPS = 30
REF_IN, REF_OUT = 0.28, 7.33
N = round((REF_OUT - REF_IN) * FPS)              # 212 frames
LUNGE_IN, LUNGE_SPEED = 20.95, 0.33            # 20.95-23.28 s: nobody beside him; 0.33x of 120 fps = real frames
STOCK = P / "source/stock/mixkit-12913-720.mp4"
STOCK_X = 380                                     # 405x720 window of the 1280x720 stock: doctor's face, laptop, desk (mirrored: doctor on the right)
FEET_Y, HEIGHT, FEET_X = 1515, 820, 300           # on the desk top (left half after the mirror), standing height, centre x (px)
TM = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=rgb24"
TEXT = ["Doctor: Can you show", "me what you were doing", "when your lower", "back pain started"]


def frames(cmd, w, h):
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def caption_png(path):
    f = ImageFont.truetype(str(ROOT / "brand/fonts/Inter[opsz,wght].ttf"), 66)
    try:
        f.set_variation_by_axes([32, 800])
    except Exception:
        pass
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 150
    for line in TEXT:
        b = d.textbbox((0, 0), line, font=f, stroke_width=4)
        d.text(((1080 - (b[2] - b[0])) / 2 - b[0], y), line, font=f, fill="white", stroke_width=4, stroke_fill=(20, 20, 20))
        y += 80
    im.save(path)


def main():
    W = P / "work"; W.mkdir(exist_ok=True); (P / "renders").mkdir(exist_ok=True)
    # background: real office, 9:16 window, mirrored, slowed to the Reel length
    k = (N / FPS) / 6.08
    bg = frames(["ffmpeg", "-v", "error", "-i", str(STOCK), "-vf", f"crop=405:720:{STOCK_X}:0,hflip,setpts=PTS*{k:.4f},fps={FPS},"
                 "scale=1080:1920:flags=lanczos,format=rgb24", "-frames:v", str(N), "-f", "rawvideo", "-"], 1080, 1920)
    if len(bg) < N:
        bg = np.concatenate([bg, np.repeat(bg[-1:], N - len(bg), 0)])
    # him: HYROX sandbag lunges, real 120 fps slow motion, BT.709
    fg = frames(["ffmpeg", "-v", "error", "-i", str(P / "source/IMG_5050_lunges.mov"), "-vf",
                 f"trim=start={LUNGE_IN},setpts=(PTS-STARTPTS)/{LUNGE_SPEED},fps={FPS},{TM}", "-frames:v", str(N), "-f", "rawvideo", "-"],
                1080, 1920)
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    det = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (1080, 1920), 0.35, 0.3, 50)
    mats, boxes = [], []
    for i, f in enumerate(fg):
        m = matte(sess, f)                                                      # 0..1 at frame size
        # him only: strict core, eroded so people touching him split off, largest core = him, grown back inside the soft matte
        core = cv2.erode((m > 0.8).astype(np.uint8), np.ones((21, 21), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(core)
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        keep = cv2.dilate((lab == big).astype(np.uint8), np.ones((27, 27), np.uint8))
        # and only inside a column around his body (the judge / runners stand beside or behind him)
        xs_ = np.where(keep.any(0))[0]
        col = np.zeros_like(keep); col[:, max(0, xs_.min() - 20):xs_.max() + 20] = 1
        m = m * keep * col
        # spectators far behind can sit right above his head in the picture: nothing above his own head is kept
        _, F = det.detect(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
        if F is not None:
            ys_, xs_ = np.where(m > 0.5)
            top, x0b, x1b = ys_.min(), xs_.min(), xs_.max()
            # his face = a face whose centre lies inside his own cut-out, in the upper part of it
            own = [r for r in F if x0b <= r[0] + r[2] / 2 <= x1b and r[1] < top + 0.35 * (ys_.max() - top)
                   and m[int(min(1919, r[1] + r[3] / 2)), int(min(1079, r[0] + r[2] / 2))] > 0.5]
            if own:
                x, y, w, h = max(own, key=lambda r: r[2] * r[3])[:4]
                m[:max(0, int(y - 0.6 * h))] = 0
                # distant spectators (behind the barrier, face < 0.65x his): remove their head + shoulders
                for r in F:
                    sx, sy, sw, shh = r[:4]
                    if sw > 0.65 * w or (abs(sx - x) < w and abs(sy - y) < h):
                        continue
                    m[max(0, int(sy - 0.7 * shh)):int(sy + 4.0 * shh), max(0, int(sx - 1.3 * sw)):int(sx + 2.3 * sw)] = 0
        # final: only the largest connected piece (spectators' hands / phones left loose after the face boxes)
        nn, lab2, st2, _ = cv2.connectedComponentsWithStats((m > 0.25).astype(np.uint8), connectivity=8)
        if nn > 2:
            big2 = 1 + int(np.argmax(st2[1:, cv2.CC_STAT_AREA]))
            m = m * cv2.dilate((lab2 == big2).astype(np.uint8), np.ones((5, 5), np.uint8))
        ys, xs = np.where(m > 0.5)
        mats.append(m); boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
        if i % 40 == 0:
            print("matte", i, flush=True)
    bx = np.array(boxes, float)
    sm = lambda a: np.convolve(np.pad(a, 7, mode="edge"), np.ones(15) / 15, "valid")     # steady placement (no jitter)
    cx, bot, hgt = sm((bx[:, 0] + bx[:, 2]) / 2), sm(bx[:, 3]), np.median(bx[:, 3] - bx[:, 1])
    s = HEIGHT / hgt
    caption_png(W / "caption.png")
    cap = np.asarray(Image.open(W / "caption.png")).astype(np.float32) / 255
    out = W / "comp"; out.mkdir(exist_ok=True)
    for i in range(N):
        canvas = bg[i].astype(np.float32)
        fgs = cv2.resize(fg[i], None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
        ms = cv2.resize(mats[i], None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        ox, oy = int(round(FEET_X - cx[i] * s)), int(round(FEET_Y - bot[i] * s))
        # contact shadow on the desk
        sh = np.zeros((1920, 1080), np.float32)
        cv2.ellipse(sh, (FEET_X, FEET_Y + 4), (150, 20), 0, 0, 360, 0.45, -1)
        sh = cv2.GaussianBlur(sh, (0, 0), 14)[..., None]
        canvas *= (1 - sh)
        H, Wd = fgs.shape[:2]
        x0, y0, x1, y1 = max(0, ox), max(0, oy), min(1080, ox + Wd), min(1920, oy + H)
        a = ms[y0 - oy:y1 - oy, x0 - ox:x1 - ox][..., None]
        canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + fgs[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * a
        ca = cap[..., 3:4]
        canvas = canvas * (1 - ca) + cap[..., :3] * 255 * ca
        cv2.imwrite(str(out / f"f_{i:04d}.png"), cv2.cvtColor(np.clip(canvas, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    silent = P / "renders/hyrox_backpain_silent.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(out / "f_%04d.png"), "-c:v", "libx264", "-crf", "15",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-movflags", "+faststart", str(silent)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-ss", str(REF_IN), "-to", str(REF_OUT), "-i", str(P / "ref/screen.mp4"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
                    str(P / "renders/hyrox_backpain.mp4")], check=True)
    (W / "place.json").write_text(json.dumps({"scale": s, "height_src": float(hgt)}))
    print("done", N, "frames")


if __name__ == "__main__":
    main()
