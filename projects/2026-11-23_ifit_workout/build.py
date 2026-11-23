"""iFit workout campaign Reel (Coach Osama 2026-11-23): one high-energy workout edit for iFit. No music, SFX only. No offers,
prices, discounts or Black Friday: it's a workout film that carries the iFit brand.

Arc on a 0.5 s pulse (120 bpm feel, cuts on it): FUEL (his pre-workout ritual in real 120 fps slow motion: scoop, pour, stir,
the drink) -> impact -> PULL (lat pulldowns, back + side; machine reverse fly with speed ramps 2x -> 1x) -> LIFT (curls, rep tops)
-> REPEAT (half-beat montage, iFit chip slides in) -> the double-biceps flex under a white flash -> white iFit end card,
"THE MARK OF AUTHENTICITY" (iFit's own line from their campaign animation). Picture: his iPhone HLG kept in HLG, no grade.
Graphics sRGB -> HLG at 203-nit white. iFit wordmark = official file, #4C4C4C, only on white (never recoloured / cropped).

    .venv/bin/python -I projects/2026-11-23_ifit_workout/build.py [--preview]
"""
import json, os, subprocess, sys
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_edit as R  # noqa: E402

FPS = 30
B = 0.5
fr = lambda x: round(x * FPS)
SRC = {k: P / "source" / v for k, v in {"scoop": "IMG_5669.mov", "prep": "IMG_5670.MOV", "pd_back": "IMG_2233b.MOV", "pd_side": "IMG_2234.MOV",
                                         "fly": "IMG_2235.mov", "curl": "IMG_2238.mov", "flex": "IMG_2233a.mov"}.items()}
HDR_TAGS = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
SDR2HLG = "format=gbrpf32le,zscale=tin=bt709:pin=bt709:min=gbr:rin=full:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,format=yuv420p10le"
GFX = ("format=rgba,split[c][a];[c]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,"
       "format=yuv420p10le[cy];[a]alphaextract,format=gray10le[al];[cy][al]alphamerge")
X265 = "crf=12:preset=medium:pools=4:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error"
# (src, source start, output seconds, options). speed < 1 only on the 120 fps prep clips (real frames); ramps = [(out s, speed), ...]
SHOTS = [
    # FUEL
    ("scoop", 0.05, 3 * B, dict(speed=0.45, z=(1.10, 1.18), fy=.45)),
    ("prep", 4.30, 2 * B, dict(speed=0.5, z=(1.25, 1.32), fy=.62)),
    ("prep", 13.20, 2 * B, dict(speed=0.5, z=(1.30, 1.36), fy=.66)),
    ("prep", 36.55, 3 * B, dict(speed=0.42, z=(1.10, 1.16), fy=.35)),
    # PULL
    ("pd_back", 0.20, 2 * B, dict(z=(1.15, 1.22), fy=.4)),
    ("pd_side", 1.00, 2 * B, dict(z=(1.15, 1.2), fy=.4)),
    ("pd_back", 2.50, 2 * B, dict(z=(1.25, 1.3), fy=.35)),
    ("fly", 11.00, 3 * B, dict(ramp=[(0.5, 2.0), (9, 1.0)], z=(1.12, 1.18), fy=.45)),
    ("fly", 15.20, 2 * B, dict(z=(1.25, 1.3), fy=.42)),
    # LIFT
    ("curl", 2.70, 2 * B, dict(z=(1.15, 1.2), fy=.42)),
    ("curl", 6.50, 2 * B, dict(ramp=[(0.33, 2.0), (9, 1.0)], z=(1.3, 1.36), fy=.38)),
    ("curl", 12.20, 2 * B, dict(z=(1.2, 1.25), fy=.4)),
    # REPEAT: half-beat montage
    ("pd_side", 2.50, B, dict(z=(1.3, 1.34), fy=.35)),
    ("fly", 13.50, B, dict(z=(1.35, 1.4), fy=.42)),
    ("curl", 10.20, B, dict(z=(1.35, 1.4), fy=.38)),
    ("pd_back", 3.80, B, dict(z=(1.3, 1.34), fy=.35)),
    ("fly", 17.50, B, dict(z=(1.35, 1.4), fy=.42)),
    ("curl", 16.30, B, dict(z=(1.35, 1.4), fy=.38)),
    # the flex
    ("flex", 0.00, 2 * B, dict(z=(1.05, 1.12), fy=.3)),
    ("white", 0, 6 * B, {}),
]
WORDS = [("FUEL.", 0, 1330), ("PULL.", 4, 1330), ("LIFT.", 9, 820), ("REPEAT.", 12, 1330)]   # (word, shot index, top px: LIFT sits on his black tank, not the white shorts/wall)


def plan():
    tl, f = [], 0
    for src, a, dur, o in SHOTS:
        n = fr(dur)
        if o.get("ramp"):
            st = f
            for k, (d, sp) in enumerate(o["ramp"]):
                m = n - (st - f) if k == len(o["ramp"]) - 1 else fr(d)
                tl.append(dict(src=src, a=round(a, 4), speed=sp, n=m, start=st, shot_start=f, shot_n=n, o=o))
                a += m * sp / FPS; st += m
        else:
            tl.append(dict(src=src, a=a, speed=o.get("speed", 1.0), n=n, start=f, shot_start=f, shot_n=n, o=o))
        f += n
    return tl, f


def ff(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], check=True)


def seg(s, W, i):
    out = W / "seg" / f"s{i:02d}.mkv"
    n = s["n"]
    enc = ["-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", "crf=6:preset=fast:pools=4:log-level=error",
           "-tag:v", "hvc1", *HDR_TAGS, "-frames:v", str(n), "-r", str(FPS), str(out)]
    if s["src"] == "white":
        ff(["-f", "lavfi", "-i", f"color=c=white:s=1080x1920:r={FPS}:d={n / FPS + 0.1}", "-vf", "format=rgb24," + SDR2HLG, *enc])
        return out
    o, sp = s["o"], s["speed"]
    z0, z1 = o.get("z", (1, 1))
    t0, L = (s["start"] - s["shot_start"]) / FPS, s["shot_n"] / FPS            # zoom runs across ramp pieces of one shot
    Z = f"({z0}+({z1}-{z0})*(t+{t0:.4f})/{L:.4f})"
    f = [f"[0:v]trim=start={s['a']:.4f}:end={s['a'] + n * sp / FPS + 0.3:.4f},setpts=PTS-STARTPTS"]
    if sp > 1:
        f.append(f"tmix=frames=2,setpts=PTS/{sp}")                                 # sped-up: 2-frame blend = motion blur
    elif sp < 1:
        f.append(f"setpts=PTS/{sp}")                                               # 120 fps source: real slow-motion frames
    f.append(f"fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS")
    f.append(f"scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,"
             f"crop=1080:1920:x='(iw-1080)*{o.get('fx', .5)}':y='(ih-1920)*{o.get('fy', .5)}',format=yuv420p10le,setsar=1")
    ff(["-i", str(SRC[s["src"]]), "-filter_complex", ",".join(f) + "[v]", "-map", "[v]", "-an", *enc])
    return out


def count_frames(p):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets",
                               "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True).stdout.strip())


def build(preview=False):
    W = P / "work"; (W / "seg").mkdir(parents=True, exist_ok=True); (P / "renders").mkdir(exist_ok=True)
    tl, total = plan()
    T = total / FPS
    shot_t = []
    k = 0
    for src, a, dur, o in SHOTS:
        shot_t.append(k / FPS); k += fr(dur)
    t_flex, t_end = shot_t[-2], shot_t[-1]
    t_rep = shot_t[12]
    spec = {"dur": T, "words": [{"text": w, "at": shot_t[i] + 0.02, "dur": 0.85 if w != "REPEAT." else 0.7, "top": y} for w, i, y in WORDS],
            "chip": {"at": t_rep + 0.1, "dur": t_flex - t_rep - 0.1}, "flashes": [shot_t[4], t_flex, t_end], "end": t_end}
    (W / "overlay_spec.json").write_text(json.dumps(spec))
    ov = W / "ov"
    subprocess.run(["node", str(P / "render_overlay.js"), str(W / "overlay_spec.json"), str(ov)], check=True)
    for f in sorted(ov.glob("f_*.png")):
        with Image.open(f) as im:
            if im.mode == "RGBA":
                continue
            tmp = f.with_suffix(".tmp.png"); im.convert("RGBA").save(tmp)
        os.replace(tmp, f)
    files = [seg(s, W, i) for i, s in enumerate(tl)]
    lst = W / "seg/list.txt"; lst.write_text("".join(f"file '{f}'\n" for f in files))
    base = W / "base.mkv"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])
    assert count_frames(base) == total, (count_frames(base), total)
    raw = W / "video.mp4"
    x265 = X265.replace("crf=12", "crf=20").replace("preset=medium", "preset=faster") if preview else X265
    g2 = (f"[0:v]settb=1/{FPS},setpts=N[b];[1:v]settb=1/{FPS},setpts=N,{GFX}[ov];"
          "[b][ov]overlay=format=yuv420p10:eof_action=repeat,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[vout]")
    ff(["-i", str(base), "-reinit_filter", "0", "-framerate", str(FPS), "-i", str(ov / "f_%05d.png"), "-filter_complex", g2, "-map", "[vout]",
        "-frames:v", str(total), "-r", str(FPS), "-fps_mode", "cfr", "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", x265,
        "-tag:v", "hvc1", *HDR_TAGS, str(raw)])
    assert count_frames(raw) == total
    # SFX only
    cue = lambda at, snd, g, **kw: {"at": round(at, 4), "sound": snd, "gain_db": g, **kw}
    cues = [cue(0.0, "air", -20, dur=4.0), cue(0.0, "thump", -12, freq=45, dur=0.6), cue(shot_t[4] - 1.4, "swell", -15, dur=1.4)]
    for i, t in enumerate(shot_t[1:-1], 1):
        if i < 4:
            cues.append(cue(t, "whoosh_in", -16))                                  # slow-motion fuel: soft transitions
        elif i == 4:
            cues += [cue(t, "impact", -7), cue(t, "boom", -9)]                     # the workout hits
        elif i < 12:
            cues += [cue(t, "whip", -13), cue(t + 0.02, "thump", -15, freq=55, dur=0.25)]
        else:
            cues.append(cue(t, "click", -13) if i % 2 else cue(t, "key", -14))
    for w, i, _ in WORDS:
        cues.append(cue(shot_t[i] + 0.02, "slam", -12))
    cues += [cue(t_rep + 0.1, "whoosh_in", -18), cue(t_flex, "reverse_hit", -11, dur=0.6), cue(t_flex, "impact", -8),
             cue(t_end, "boom", -9), cue(t_end + 0.05, "chime", -18)]
    silent = W / "silence.wav"
    ff(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{T:.3f}", "-c:a", "pcm_s24le", str(silent)])
    mix = W / "mix.wav"
    R.build_mix(silent, cues, T, FPS, mix, None)
    final = P / "renders" / ("ifit_workout_preview.mp4" if preview else "ifit_workout.mp4")
    R.master_audio(mix, final, -14.0, -1.0, video=raw)
    raw.unlink()
    print("output", final, f"{T:.2f}s", flush=True)


if __name__ == "__main__":
    build(preview="--preview" in sys.argv)
