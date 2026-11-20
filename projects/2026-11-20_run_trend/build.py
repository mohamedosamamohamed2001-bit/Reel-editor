""""Start, no problem / 5 minute / Problem! Engine Kaput" HYROX trend, OSM version (Coach Osama 2026-11-20).

Reference (ref/trend.mp4, screen recording, reference only): the Reel plays 0.850-7.100 s of the recording (6.25 s, then loops).
Reel-time beats, measured by frame difference: 0-1.633 race start "Start, no problem" | 1.633-3.000 exhausted runners "5 minute" |
hard cuts 3.000 knee, 3.300 heart, 3.600 foot, 4.033 lower back (3D X-ray pain renders) | 4.600-6.250 dark skeleton walking
"Problem! Engine Kaput" (voice line, audio fades out). His version, same frames (30 fps, 188 frames):
  A his run at real speed (src 0.0) | B the next stretch in heavy slow motion (src 1.633, 0.3x, real 120 fps frames) |
  C his own body, frozen mid-stride (src 1.3): OSM pain cards (Night dim, clear circle, brand status red #F26D6D ring + word),
    push-in centred on the body part; AI/3D anatomy is rejected for OSM, so the X-ray renders are rebuilt on HIS body |
  D the end of his run (src 2.45-2.80) at 0.21x (motion-interpolated), sinking to grey and toward Night.
Captions: the locked OSM caption bar (#56A0FB, white Inter 700). Picture: his iPhone HLG kept in HLG (no creative grade);
graphics sRGB -> HLG at 203-nit white. Source is 1080x1920, so the output is 1080x1920 (no fake 4K).
Audio: the trend's own sound, recording 0.850-7.100 s, untouched (re-encoded once to AAC 256k).

    .venv/bin/python -I projects/2026-11-20_run_trend/build.py
"""
import json, os, subprocess
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parent
FPS = 30
SRC = P / "source/IMG_5050.mov"
REF_IN, REF_OUT = 0.850, 7.100
HDR = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
GFX = ("format=rgba,split[c][a];[c]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:"
       "npl=203,format=yuv420p10le[cy];[a]alphaextract,format=gray10le[al];[cy][al]alphamerge")
FREEZE = 1.30
# body parts on the freeze frame (px of 1080x1920), measured on a grid over src 1.30 s
PARTS = {"knee": (792, 952), "heart": (702, 702), "foot": (556, 1100), "back": (786, 805)}
# ring radius per part: the heart ring stays below his chin (face box ends ~y 600), none covers his face
RADIUS = {"knee": 80, "heart": 82, "foot": 78, "back": 72}
# (frames, kind, params)
SEGS = [
    (49, "run", dict(src=0.0, speed=1.0)),                                  # 0.000-1.633  Start, no problem
    (41, "run", dict(src=49 / FPS, speed=0.3)),                             # 1.633-3.000  5 minute
    (9, "card", dict(part="knee")),                                         # 3.000-3.300
    (9, "card", dict(part="heart")),                                        # 3.300-3.600
    (13, "card", dict(part="foot")),                                        # 3.600-4.033
    (17, "card", dict(part="back")),                                        # 4.033-4.600
    (50, "kaput", dict(src=2.45, end=2.8175)),                              # 4.600-6.267  Problem! Engine Kaput
]
CARD_WORDS = {"knee": "KNEE", "heart": "HEART", "foot": "FOOT", "back": "LOWER BACK"}
CARD_SIDE = {"knee": "left", "heart": "left", "foot": "left", "back": "left"}


def ff(a):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *a], check=True)


ENC = ["-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", "crf=6:preset=fast:log-level=error", "-tag:v", "hvc1", *HDR]


def seg(i, n, kind, o, W):
    out = W / f"s{i}.mkv"
    if kind == "run":
        sp = o["speed"]
        f = f"trim=start={o['src']:.4f},setpts=(PTS-STARTPTS)/{sp},fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS"
    elif kind == "card":
        px, py = PARTS[o["part"]]
        Z = f"(1.10+0.08*t/{n / FPS:.4f})"                                   # push-in centred on the body part
        f = (f"trim=start={FREEZE}:end={FREEZE + 0.05},setpts=PTS-STARTPTS,trim=end_frame=1,loop=loop={n - 1}:size=1:start=0,"
             f"setpts=N/{FPS}/TB,scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,"
             f"crop=1080:1920:x='{px}*({Z}-1)':y='{py}*({Z}-1)'")
    else:  # kaput: real slow motion, interpolated, draining to grey
        sp = (o["end"] - o["src"]) / (n / FPS)
        f = (f"trim=start={o['src']:.4f},setpts=(PTS-STARTPTS)/{sp:.5f},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
             f"trim=end_frame={n},setpts=PTS-STARTPTS,hue=s='max(0.25,1-0.75*t/0.6)'")
    ff(["-i", str(SRC), "-vf", f + ",format=yuv420p10le,setsar=1", "-an", "-frames:v", str(n), "-r", str(FPS), *ENC, str(out)])
    return out


def main():
    W = P / "work"; W.mkdir(exist_ok=True); (P / "renders").mkdir(exist_ok=True)
    starts, k = [], 0
    for n, _, _ in SEGS:
        starts.append(k); k += n
    total = k; T = total / FPS
    s = lambda f: round(f / FPS, 4)
    cards = []
    for (n, kind, o), st in zip(SEGS, starts):
        if kind == "card":
            x, y = PARTS[o["part"]]
            cards.append({"start": s(st), "end": s(st + n), "x": x, "y": y, "word": CARD_WORDS[o["part"]], "side": CARD_SIDE[o["part"]], "r": RADIUS[o["part"]]})
    spec = {"dur": T,
            "captions": [{"text": "Start, no problem", "start": -1, "end": s(starts[1]), "x": 34, "y": 288, "cut_out": True},
                         {"text": "5 minute", "start": s(starts[1]), "end": s(starts[2]), "x": 34, "y": 288, "cut_out": True},
                         {"text": "Problem!<br>Engine Kaput", "start": s(starts[6]), "end": T + 1, "x": 34, "y": 900, "cut_out": True}],
            "cards": cards, "fade": {"start": s(starts[6]), "end": T + 1, "ramp": 0.6, "max": 0.35}}
    (W / "overlay_spec.json").write_text(json.dumps(spec, indent=1))
    ov = W / "ov"
    subprocess.run(["node", str(P / "render_overlay.js"), str(W / "overlay_spec.json"), str(ov)], check=True)
    for f in sorted(ov.glob("f_*.png")):
        with Image.open(f) as im:
            if im.mode == "RGBA":
                continue
            tmp = f.with_suffix(".tmp.png"); im.convert("RGBA").save(tmp)
        os.replace(tmp, f)
    files = [seg(i, n, kind, o, W) for i, (n, kind, o) in enumerate(SEGS)]
    lst = W / "list.txt"; lst.write_text("".join(f"file '{f}'\n" for f in files))
    base = W / "base.mkv"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])
    audio = W / "trend_audio.wav"
    ff(["-ss", str(REF_IN), "-to", str(REF_OUT), "-i", str(P / "ref/trend.mp4"), "-vn", "-af", f"apad=whole_dur={T:.4f}",
        "-ar", "48000", "-c:a", "pcm_s24le", str(audio)])
    out = P / "renders/run_engine_kaput.mp4"
    g = (f"[0:v]settb=1/{FPS},setpts=N[b];[1:v]settb=1/{FPS},setpts=N,{GFX}[ov];"
         "[b][ov]overlay=format=yuv420p10:eof_action=repeat,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[v]")
    ff(["-i", str(base), "-reinit_filter", "0", "-framerate", str(FPS), "-i", str(ov / "f_%05d.png"), "-i", str(audio),
        "-filter_complex", g, "-map", "[v]", "-map", "2:a", "-frames:v", str(total), "-r", str(FPS), "-fps_mode", "cfr",
        "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params",
        "crf=12:preset=medium:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error",
        "-tag:v", "hvc1", *HDR, "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(out)])
    print("output", out, total, "frames")


if __name__ == "__main__":
    main()
