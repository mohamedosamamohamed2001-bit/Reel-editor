"""Version 4 (Coach Osama 2026-11-25): NO compositing (he found the cut-out versions muddy). His HYROX Cairo sandbag lunges full
frame, untouched picture (iPhone HLG kept in HLG, no grade), IMG_5050 16.8 s on at 0.5x of its 120 fps (real slow motion), one
continuous shot like the reference, the reference's caption on top (bold white, dark outline; sRGB -> HLG at 203-nit white) and the
reference's own sound, same Reel length (recording 0.28-7.33 s).

    .venv/bin/python -I projects/2026-11-25_hyrox_recreate/build_v4.py
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
FPS = 30
REF_IN, REF_OUT = 0.28, 7.33
N = round((REF_OUT - REF_IN) * FPS)
SRC_IN, SPEED = 16.8, 0.5
TEXT = ["Doctor: Can you show", "me what you were doing", "when your lower", "back pain started"]
HDR = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
GFX = ("format=rgba,split[c][a];[c]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:"
       "npl=203,format=yuv420p10le[cy];[a]alphaextract,format=gray10le[al];[cy][al]alphamerge")


def caption(path):
    f = ImageFont.truetype(str(ROOT / "brand/fonts/Inter[opsz,wght].ttf"), 70)
    try:
        f.set_variation_by_axes([32, 800])
    except Exception:
        pass
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 150
    for line in TEXT:
        b = d.textbbox((0, 0), line, font=f, stroke_width=5)
        d.text(((1080 - (b[2] - b[0])) / 2 - b[0], y), line, font=f, fill="white", stroke_width=5, stroke_fill=(15, 15, 15))
        y += 86
    im.save(path)


def main():
    W = P / "work"; W.mkdir(exist_ok=True)
    caption(W / "caption4.png")
    out = P / "renders/hyrox_backpain_v4.mp4"
    g = (f"[0:v]trim=start={SRC_IN},setpts=(PTS-STARTPTS)/{SPEED},fps={FPS},trim=end_frame={N},setpts=PTS-STARTPTS,format=yuv420p10le[b];"
         f"[1:v]{GFX}[c];[b][c]overlay=format=yuv420p10,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / "source/IMG_5050_lunges.mov"), "-loop", "1", "-i", str(W / "caption4.png"),
                    "-ss", str(REF_IN), "-to", str(REF_OUT), "-i", str(P / "ref/screen.mp4"),
                    "-filter_complex", g, "-map", "[v]", "-map", "2:a", "-frames:v", str(N), "-r", str(FPS),
                    "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params",
                    "crf=12:preset=medium:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error",
                    "-tag:v", "hvc1", *HDR, "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-map", "0:v", "-c", "copy", "-movflags", "+faststart",
                    str(P / "renders/hyrox_backpain_v4_silent.mp4")], check=True)
    print("done", N)


if __name__ == "__main__":
    main()
