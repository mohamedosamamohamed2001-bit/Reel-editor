"""Version 2 (Coach Osama 2026-11-20): first half = his run, second half = the TREND'S OWN footage from the injuries on, no text.

His request: "take the second half of the video from video 1, from the injuries on, and remove the text completely; no captions".
  0.000-1.633  his run, real speed (same segment as v1)                      | no caption
  1.633-3.000  his run, slow motion 0.3x (same segment as v1)                | no caption
  3.000-6.267  the reference Reel from its injury cut (recording 3.85-7.10 s): knee, heart, foot, lower back, skeleton.
               Cropped to a clean 9:16 window of the Reel (screen x 57-1170, y 190-2169: below the status bar, left of the
               Instagram icons, above the account/caption bar), scaled 1113 -> 1080. Its burned-in "Problem! Engine Kaput"
               is erased on every skeleton frame (letters + outline masked per frame, Navier-Stokes fill, softened, feathered edge).
               SDR -> HLG at 203-nit reference white, so it sits in his HDR timeline.
Audio: the trend's sound, recording 0.850-7.100 s, unchanged. No captions or graphics anywhere.

    .venv/bin/python -I projects/2026-11-20_run_trend/build_v2.py      (run build.py first: it makes work/s0.mkv, s1.mkv)
"""
import glob, subprocess
from pathlib import Path
import cv2
import numpy as np

P = Path(__file__).resolve().parent
FPS = 30
REF_IN, REF_OUT = 0.850, 7.100
HDR = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
SDR2HLG = "format=gbrpf32le,zscale=tin=bt709:pin=bt709:min=gbr:rin=full:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,format=yuv420p10le"
SKEL_FROM = 48                     # part-2 frame where the skeleton shot starts (reel 4.600 s)


def ff(a):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *a], check=True)


def text_mask(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    m = ((hsv[:, :, 2] > 185) & (hsv[:, :, 1] < 80)).astype(np.uint8) * 255
    band = np.zeros_like(m); band[1228:1338, 20:1080] = 255          # the sentence's rows only
    m &= band
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))   # letters + their dark outline


def main():
    W = P / "work"; d = W / "p2"; d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.png"):
        f.unlink()
    ff(["-ss", "3.85", "-i", str(P / "ref/trend.mp4"), "-t", "3.25", "-vf", "fps=30,crop=1113:1979:57:190,scale=1080:1920:flags=lanczos",
        "-start_number", "0", str(d / "f_%03d.png")])
    fs = sorted(glob.glob(str(d / "f_*.png")))
    assert len(fs) == 98, len(fs)
    for f in fs[SKEL_FROM:]:
        im = cv2.imread(f)
        m = text_mask(im)
        fill = cv2.GaussianBlur(cv2.inpaint(im, m, 25, cv2.INPAINT_NS), (0, 0), 6)      # soft fill, no smeared letter shapes
        w = np.clip(cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 8)[..., None] * 1.6, 0, 1)   # feathered edge
        cv2.imwrite(f, (im * (1 - w) + fill * w).astype(np.uint8))
    p2 = W / "p2.mkv"
    ff(["-framerate", str(FPS), "-i", str(d / "f_%03d.png"), "-vf", SDR2HLG + ",setsar=1", "-frames:v", "98", "-r", str(FPS),
        "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", "crf=6:preset=fast:log-level=error", "-tag:v", "hvc1", *HDR, str(p2)])
    lst = W / "list_v2.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in (W / "s0.mkv", W / "s1.mkv", p2)))
    base = W / "base_v2.mkv"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])
    audio = W / "trend_audio.wav"
    out = P / "renders/run_engine_kaput_v2.mp4"
    ff(["-i", str(base), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-frames:v", "188", "-r", str(FPS),
        "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params",
        "crf=12:preset=medium:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error",
        "-tag:v", "hvc1", *HDR, "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(out)])
    print("output", out)


if __name__ == "__main__":
    main()
