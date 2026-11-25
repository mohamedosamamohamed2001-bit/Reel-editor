"""Version 3 (Coach Osama 2026-11-25): THE REFERENCE'S OWN doctor scene, same seconds (Reel 0.28-7.33 s of the recording), with HIM
in place of the original athlete. His request: "the same video I sent you, the doctor one, same seconds, same everything".

Reference frames (screen recording, 1320x2868): crop x 170-1320, y 295-2340 (9:16, below the Reels header, above the account bar,
whole doctor kept), scaled to 1080x1920. Camera is static, so:
  - original athlete removed: the area he ever covers (motion map) is replaced by a clean plate built from the moments each pixel was
    uncovered (per-pixel brightest-frame percentile; never-uncovered remnants inpainted); the rest of every frame stays live (doctor);
  - Instagram icons over the doctor's coat erased (static thin strokes + red heart, Telea inpainting, per frame);
  - the burned-in caption (cut at the left by the 9:16 crop) erased and redrawn identically, whole, bold white with dark outline.
Him: HYROX Cairo sandbag lunges (IMG_5050, 120 fps 20.95-23.28 s at 0.33x, real slow motion), MODNet cut-out (him only), feet on the
exam table where the athlete stood, contact shadow. Sound: the reference's own audio, same span.

    .venv/bin/python -I projects/2026-11-25_hyrox_recreate/build_v3.py
"""
import subprocess, sys
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
N = round((REF_OUT - REF_IN) * FPS)
CX, CY, CW, CH = 170, 295, 1150, 2045
LUNGE_IN, LUNGE_SPEED = 20.95, 0.33
FEET_Y, HEIGHT, FEET_X = 1200, 660, 290
TM = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=rgb24"
TEXT = ["Doctor: Can you show", "me what you were doing", "when your lower", "back pain started"]


def stream(cmd, w, h):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3).copy()
    p.wait()


REF_CMD = ["ffmpeg", "-v", "error", "-ss", str(REF_IN), "-to", str(REF_OUT), "-i", str(P / "ref/screen.mp4"), "-vf",
           f"fps={FPS},crop={CW}:{CH}:{CX}:{CY},format=rgb24", "-f", "rawvideo", "-"]


def caption_png(path):
    f = ImageFont.truetype(str(ROOT / "brand/fonts/Inter[opsz,wght].ttf"), 70)
    try:
        f.set_variation_by_axes([32, 800])
    except Exception:
        pass
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 18
    for line in TEXT:
        b = d.textbbox((0, 0), line, font=f, stroke_width=5)
        d.text(((1080 - (b[2] - b[0])) / 2 - b[0], y), line, font=f, fill="white", stroke_width=5, stroke_fill=(15, 15, 15))
        y += 86
    im.save(path)


def main():
    W = P / "work"; W.mkdir(exist_ok=True); (P / "renders").mkdir(exist_ok=True)
    # pass 1: statistics over the reference crop (every 2nd frame, half size) -> motion map + per-pixel bright percentile
    small = [cv2.resize(f, (CW // 2, CH // 2), interpolation=cv2.INTER_AREA) for i, f in enumerate(stream(REF_CMD, CW, CH)) if i % 2 == 0]
    st = np.stack(small).astype(np.float32)
    motion = st.mean(-1).std(0)
    athlete = (motion > 6).astype(np.uint8)
    athlete[:220] = 0                                                        # top band = static caption, not him
    athlete = cv2.dilate(cv2.morphologyEx(athlete, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)), np.ones((31, 31), np.uint8))
    lum = st.mean(-1)
    order = np.argsort(lum, axis=0)[-3:]                                     # per pixel: the 3 frames where it is brightest (uncovered)
    plate_s = np.mean([np.take_along_axis(st, order[k][None, ..., None].repeat(3, -1), 0)[0] for k in range(3)], axis=0).astype(np.uint8)
    # remnants never uncovered (dark, where he always was): inpaint them
    rem = ((plate_s.mean(-1) < 70) & (athlete > 0)).astype(np.uint8)
    rem[ :, :] &= 1
    plate_s = cv2.inpaint(plate_s, cv2.dilate(rem, np.ones((5, 5), np.uint8)) * 255, 9, cv2.INPAINT_TELEA)
    # the wall behind him is plain: above the table top, his whole area is refilled smoothly from the surrounding wall
    #  (the time-based plate there kept a grey patch + wavy outlines: he never left that spot)
    WALL_BOTTOM = 540                                                        # half-res crop y: wall ends here (pillow / table below)
    wall = np.zeros_like(athlete); wall[:WALL_BOTTOM] = athlete[:WALL_BOTTOM]
    wall = cv2.dilate(wall, np.ones((15, 15), np.uint8))
    # fit the plain beige wall (quadratic per channel) on clean wall pixels around his area, fill his area with it
    hsvp = cv2.cvtColor(plate_s, cv2.COLOR_RGB2HSV)
    ring = cv2.dilate(wall, np.ones((91, 91), np.uint8)) & (1 - wall)
    ring[:200] = 0; ring[WALL_BOTTOM:] = 0                                   # below the caption band, above the table
    good = (ring > 0) & (hsvp[..., 2] > 120) & (hsvp[..., 1] > 25) & (hsvp[..., 1] < 120)
    yy, xx = np.nonzero(good)
    A = np.stack([np.ones_like(xx), xx, yy, xx * xx, yy * yy, xx * yy], 1).astype(np.float64) / [1, 600, 1000, 600**2, 1000**2, 600e3]
    Y, X = np.mgrid[0:plate_s.shape[0], 0:plate_s.shape[1]]
    B = np.stack([np.ones_like(X), X, Y, X * X, Y * Y, X * Y], -1).astype(np.float64) / [1, 600, 1000, 600**2, 1000**2, 600e3]
    fit = np.zeros(plate_s.shape, np.float64)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, plate_s[yy, xx, c].astype(np.float64), rcond=None)
        fit[..., c] = B @ coef
    rng = np.random.default_rng(3)
    fit += rng.normal(0, 1.2, fit.shape)                                     # the wall's fine grain, so it isn't flat plastic
    ww = cv2.GaussianBlur(wall.astype(np.float32), (0, 0), 4)[..., None]
    plate_s = np.clip(plate_s * (1 - ww) + fit * ww, 0, 255).astype(np.uint8)
    # the exam table under him (sheet + mattress edge are horizontal): each row's masked run is interpolated from the clean
    # pixels left and right of it in the same row, so the sheet/edge lines continue straight through
    tab = cv2.dilate(athlete, np.ones((11, 11), np.uint8))
    for yrow in range(WALL_BOTTOM, 680):
        mrow = tab[yrow] > 0
        if not mrow.any() or mrow.all():
            continue
        xsr = np.arange(plate_s.shape[1]); okp = ~mrow
        for c in range(3):
            plate_s[yrow, mrow, c] = np.interp(xsr[mrow], xsr[okp], plate_s[yrow, okp, c].astype(np.float64)).astype(np.uint8)
    plate = cv2.resize(plate_s, (CW, CH), interpolation=cv2.INTER_CUBIC)
    amask = cv2.GaussianBlur(cv2.resize(athlete.astype(np.float32), (CW, CH)), (0, 0), 6)[..., None]
    med = np.median(st, axis=0).astype(np.uint8)
    del st, small
    # static UI icons (right strip) + burned caption (top band): masks from the static median frame
    medf = cv2.resize(med, (CW, CH), interpolation=cv2.INTER_CUBIC)
    g = cv2.cvtColor(medf, cv2.COLOR_RGB2GRAY).astype(np.int16)
    hsv = cv2.cvtColor(medf, cv2.COLOR_RGB2HSV)
    icon = np.zeros((CH, CW), np.uint8)
    strip = (slice(1020, CH), slice(990, CW))
    stroke = (np.abs(g - cv2.medianBlur(g.astype(np.uint8), 31).astype(np.int16)) > 28)
    red = (hsv[..., 0] < 8) | (hsv[..., 0] > 170)
    red &= hsv[..., 1] > 120
    icon[strip] = (stroke[strip] | red[strip]).astype(np.uint8)
    icon = cv2.dilate(icon, np.ones((7, 7), np.uint8)) * 255
    cap = np.zeros((CH, CW), np.uint8)
    capreg = (slice(0, 440), slice(0, CW))
    cap[capreg] = ((g[capreg] > 215) | (g[capreg] < 60)).astype(np.uint8)
    cap = cv2.dilate(cap, np.ones((9, 9), np.uint8)) * 255
    cap = cv2.dilate(cap, np.ones((13, 13), np.uint8))
    filled = cv2.inpaint(medf, cap, 25, cv2.INPAINT_NS)
    soft = cv2.GaussianBlur(filled, (0, 0), 9)                                # no blotches: smooth fill inside the erased text
    wcap = cv2.GaussianBlur(cap.astype(np.float32) / 255, (0, 0), 5)[..., None]
    top_clean = (filled * (1 - wcap) + soft * wcap)[:460]                     # static top band, caption-free
    caption_png(W / "caption3.png")
    capimg = np.asarray(Image.open(W / "caption3.png")).astype(np.float32) / 255
    # him: mattes (same rules as the stock version)
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    det = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (1080, 1920), 0.35, 0.3, 50)
    fgs, mats, boxes = [], [], []
    for f in stream(["ffmpeg", "-v", "error", "-i", str(P / "source/IMG_5050_lunges.mov"), "-vf",
                     f"trim=start={LUNGE_IN},setpts=(PTS-STARTPTS)/{LUNGE_SPEED},fps={FPS},{TM}", "-frames:v", str(N), "-f", "rawvideo", "-"],
                    1080, 1920):
        m = matte(sess, f)
        core = cv2.erode((m > 0.8).astype(np.uint8), np.ones((21, 21), np.uint8))
        n, lab, s_, _ = cv2.connectedComponentsWithStats(core)
        big = 1 + int(np.argmax(s_[1:, cv2.CC_STAT_AREA]))
        keep = cv2.dilate((lab == big).astype(np.uint8), np.ones((27, 27), np.uint8))
        xs_ = np.where(keep.any(0))[0]
        col = np.zeros_like(keep); col[:, max(0, xs_.min() - 20):xs_.max() + 20] = 1
        m = m * keep * col
        _, F = det.detect(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
        if F is not None:
            own = [r for r in F if m[int(min(1919, r[1] + r[3] / 2)), int(min(1079, r[0] + r[2] / 2))] > 0.5]
            if own:
                x, y, w, h = max(own, key=lambda r: r[2] * r[3])[:4]
                band = int(min(1920, y + 2.6 * h))                            # head, sandbag, hands: spectators only show up here
                m[:max(0, int(y - 0.5 * h))] = 0
                m[:band, :max(0, int(x - 0.7 * w))] = 0
                m[:band, int(min(1080, x + 5.5 * w)):] = 0
        # final: largest connected piece only, soft 1.5 px edge (no hard cut-out line)
        nn, lab2, st2, _ = cv2.connectedComponentsWithStats((m > 0.3).astype(np.uint8), connectivity=8)
        if nn > 2:
            big2 = 1 + int(np.argmax(st2[1:, cv2.CC_STAT_AREA]))
            m = m * cv2.dilate((lab2 == big2).astype(np.uint8), np.ones((5, 5), np.uint8))
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)
        ys, xs = np.where(m > 0.5)
        fgs.append(f); mats.append(m.astype(np.float16)); boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    bx = np.array(boxes, float)
    sm = lambda a: np.convolve(np.pad(a, 7, mode="edge"), np.ones(15) / 15, "valid")
    cxs, bot, hgt = sm((bx[:, 0] + bx[:, 2]) / 2), sm(bx[:, 3]), np.median(bx[:, 3] - bx[:, 1])
    s = HEIGHT / hgt
    out = W / "comp5"; out.mkdir(exist_ok=True)
    for i, f in enumerate(stream(REF_CMD, CW, CH)):
        if i >= N:
            break
        fr_ = f.astype(np.float32)
        fr_ = fr_ * (1 - amask) + plate.astype(np.float32) * amask                    # original athlete removed
        fr_ = cv2.inpaint(np.clip(fr_, 0, 255).astype(np.uint8), icon, 5, cv2.INPAINT_TELEA).astype(np.float32)   # UI icons
        fr_[:460] = top_clean                                                         # caption band (static)
        canvas = cv2.resize(fr_, (1080, 1920), interpolation=cv2.INTER_AREA)
        fgi = cv2.resize(fgs[i], None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
        ms = cv2.resize(mats[i].astype(np.float32), None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        ox, oy = int(round(FEET_X - cxs[i] * s)), int(round(FEET_Y - bot[i] * s))
        sh = np.zeros((1920, 1080), np.float32)
        cv2.ellipse(sh, (FEET_X, FEET_Y + 4), (140, 18), 0, 0, 360, 0.45, -1)
        canvas *= (1 - cv2.GaussianBlur(sh, (0, 0), 12)[..., None])
        H_, W_ = fgi.shape[:2]
        x0, y0, x1, y1 = max(0, ox), max(0, oy), min(1080, ox + W_), min(1920, oy + H_)
        a = ms[y0 - oy:y1 - oy, x0 - ox:x1 - ox][..., None]
        canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + fgi[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * a
        ca = capimg[..., 3:4]
        canvas = canvas * (1 - ca) + capimg[..., :3] * 255 * ca
        cv2.imwrite(str(out / f"f_{i:04d}.png"), cv2.cvtColor(np.clip(canvas, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    silent = P / "renders/hyrox_backpain_v5_silent.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(out / "f_%04d.png"), "-c:v", "libx264", "-crf", "15",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-movflags", "+faststart", str(silent)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-ss", str(REF_IN), "-to", str(REF_OUT), "-i", str(P / "ref/screen.mp4"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
                    str(P / "renders/hyrox_backpain_v5.mp4")], check=True)
    cv2.imwrite(str(W / "plate5.png"), cv2.cvtColor(plate, cv2.COLOR_RGB2BGR))
    print("done", N)


if __name__ == "__main__":
    main()
