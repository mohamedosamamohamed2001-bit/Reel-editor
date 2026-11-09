"""iFit - White Friday campaign Reel (Coach Osama 2026-11-09, revised: website first, little B-roll, White Friday only).

The iFit website screen recording OPENS the Reel and is shown COMPLETE and uninterrupted (every recorded frame, original order; the
Athletes scroll is untouched and the shot settles on him with a slow push-in on his card while the music builds and stops) -> a white
flash into a short burst of his training (four 0.5 s cuts on the drop, "WHITE" / "FRIDAY") -> "WHITE FRIDAY IS HERE!" -> iFit logo.
The term "Black Friday" is not used anywhere.

Colour: his HLG camera clips stay in their own 10-bit HLG (no grade); the SDR website recording and the SDR clip are converted
SDR -> HLG at 203-nit graphics white (BT.2408), the same conversion as the graphics, so the website white = the graphics white.
Audio: an original phonk track (tools/music.py, 120 bpm: a beat = 15 frames) + tools/sfx.py hits; no dialogue.

    python3 projects/2026-11-09_ifit/build.py [--preview]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_edit as R  # noqa: E402

FPS = 30
SRC = {"t9e": (P / "source/t9e.mp4", "hlg"), "t7d": (P / "source/t7d.mp4", "hlg"), "ms1": (P / "source/ms1.mp4", "sdr"),
       "screen": (P / "source/screen.mp4", "sdr")}
HDR_TAGS = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
YUV2HLG = "zscale=tin=bt709:pin=bt709:min=bt709:rin=tv:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,format=yuv420p10le"   # SDR video
SDR2HLG = ("format=gbrpf32le,zscale=tin=bt709:pin=bt709:min=gbr:rin=full:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,format=yuv420p10le")
GFX = ("format=rgba,split[c{n}][a{n}];[c{n}]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,"
       "format=yuv420p10le[cy{n}];[a{n}]alphaextract,format=gray10le[al{n}];[cy{n}][al{n}]alphamerge")
X265 = "crf=12:preset=medium:pools=2:frame-threads=2:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error"
fr = lambda x: round(x * FPS)

# website card on a white stage: crop the phone status bar (recording dot) and the floating Safari bar, keep the whole page width
CROP = (0, 155, 1320, 2455)            # x, y, w, h in the 1320x2868 recording (below the Dynamic Island, above the Safari bar)
CARD = (82, 108, 916, 1704)            # x, y, w, h on the 1080x1920 frame (same aspect as CROP)
SCREEN_FRAMES = 534                    # 1066 decoded frames at 60 fps: every 2nd (0..1064) + the final frame 1065 = 534 at 30 fps, start to end
HIS_CARD_Y = CARD[1] + CARD[3] * ((0.53 * 2868 - CROP[1]) / CROP[3])   # his athlete card centre on the frame (measured at 16 s)

# shots: (src, start in source s, output seconds, options). t9e / ms1 carry burned-in labels bottom-left ("Me to Me", "POV"):
# those shots are punched in >= 1.42x and framed fully right (fx=1.0) so the labels stay outside the frame.
# Cuts on the 120 bpm grid (0.5 s = a beat).
B = 0.5
SHOTS = [
    # WEBSITE first (the hook): complete, uninterrupted, then held on him while the build stops (push-in on his card as it settles)
    ("screen", 0, (SCREEN_FRAMES + 6) / FPS, {}),
    # B-roll burst on the drop: four quick cuts (faces high in these takes: the words sit in the lower third)
    ("t7d", 4.4, B, dict(z=(1.25, 1.32), fy=.35)),
    ("ms1", 7.4, B, dict(z=(1.42, 1.48), fx=1.0, fy=.2)),
    ("t9e", 5.0, B, dict(z=(1.42, 1.48), fx=1.0, fy=.08)),
    ("t7d", 13.4, B, dict(z=(1.2, 1.3), fy=.35, ramp=[(0.2, 1.2), (9, 0.4)])),
    ("white", 0, 4.5, {}),                                                      # WHITE FRIDAY IS HERE! -> iFit logo
]


def plan():
    tl, f = [], 0
    for src, a, dur, o in SHOTS:
        n = fr(dur)
        if o.get("ramp"):
            st = f
            for k, (d, sp) in enumerate(o["ramp"]):
                m = n - (st - f) if k == len(o["ramp"]) - 1 else fr(d)
                tl.append(dict(src=src, a=round(a, 4), speed=sp, n=m, start=st, z=o.get("z", (1, 1)), fx=o.get("fx", .5), fy=o.get("fy", .5)))
                a += m * sp / FPS; st += m
        else:
            tl.append(dict(src=src, a=a, speed=o.get("speed", 1.0), n=n, start=f, z=o.get("z", (1, 1)), fx=o.get("fx", .5), fy=o.get("fy", .5)))
        f += n
    return tl, f


def ff(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], check=True)


def stage_images(W):
    """White stage with the card's soft contact shadow, and the card's rounded-corner mask (sRGB PNGs, made once)."""
    x, y, w, h = CARD
    bg = Image.new("RGB", (1080, 1920), (255, 255, 255))
    sh = Image.new("L", (1080, 1920), 0)
    ImageDraw.Draw(sh).rounded_rectangle((x + 6, y + 22, x + w - 6, y + h + 18), 44, fill=70)
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    bg.paste((206, 208, 212), (0, 0), sh)
    bg.save(W / "stage.png")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=255)
    m.save(W / "mask.png")


def seg(s, W, i):
    out = W / "seg" / f"s{i:02d}.mkv"
    n = s["n"]
    enc = ["-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", "crf=6:preset=fast:pools=2:frame-threads=1:log-level=error",
           "-tag:v", "hvc1", *HDR_TAGS, "-frames:v", str(n), "-r", str(FPS), str(out)]
    if s["src"] in ("black", "white"):
        col = "black" if s["src"] == "black" else "white"
        ff(["-f", "lavfi", "-i", f"color=c={col}:s=1080x1920:r={FPS}:d={n / FPS + 0.1}", "-vf", "format=rgb24," + SDR2HLG, *enc])
        return out
    path, kind = SRC[s["src"]]
    if s["src"] == "screen":
        x, y, w, h = CARD
        z_end, t0 = 1.22, (SCREEN_FRAMES / FPS) - 5.0          # push-in during the last 5 s (his card is on screen and settling)
        # opening: the page lands on beat 1 (1.10x -> 1.0 in 0.4 s); closing: slow push-in on his card while the scroll settles
        Z = f"((1+0.10*pow(max(0,1-t/0.4),3))*(1+({z_end}-1)*pow(min(1,max(0,(t-{t0})/{5.0 + 6 / FPS})),1.6)))"
        cy = HIS_CARD_Y
        # every 2nd of the 1066 decoded frames + the very last one = 534; fps=30 dropped the final frame
        g = (f"[0:v]select='not(mod(n,2))+eq(n,1065)',setpts=N/({FPS}*TB),trim=end_frame={SCREEN_FRAMES},setpts=PTS-STARTPTS,crop={CROP[2]}:{CROP[3]}:{CROP[0]}:{CROP[1]},"
             f"scale={w}:{h}:flags=lanczos:in_color_matrix=bt709:in_range=tv:out_range=full,format=rgba[pg];[2:v]format=gray[mk];[pg][mk]alphamerge[card];"
             f"[1:v]loop=loop=-1:size=1,format=rgb24[bg];[bg][card]overlay={x}:{y}:shortest=1,"
             f"tpad=stop_mode=clone:stop=6,"
             f"scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,"
             f"crop=1080:1920:x='(iw-1080)/2':y='max(0,min(ih-1920,{cy}*ih/1920-960))',format=rgb24,{SDR2HLG}[v]")
        ff(["-i", str(path), "-i", str(W / "stage.png"), "-i", str(W / "mask.png"), "-filter_complex", g, "-map", "[v]", "-an", *enc])
        return out
    sp, z0, z1 = s["speed"], *s["z"]
    Z = f"({z0}+({z1}-{z0})*t/{max(n / FPS, 1e-3):.4f})"
    f = [f"[0:v]trim=start={s['a']:.4f}:end={s['a'] + n * sp / FPS + 0.3:.4f},setpts=PTS-STARTPTS"]
    if sp != 1:
        f.append(f"setpts=PTS/{sp}")
    f.append(f"fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS")
    f.append(f"scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,"
             f"crop=1080:1920:x='(iw-1080)*{s['fx']}':y='(ih-1920)*{s['fy']}'")
    f.append(YUV2HLG if kind == "sdr" else "format=yuv420p10le")
    ff(["-i", str(path), "-filter_complex", ",".join(f) + ",setsar=1[v]", "-map", "[v]", "-an", *enc])
    return out


def count_frames(p):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets",
                               "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True).stdout.strip())


def build(preview=False):
    W = P / "work"
    (W / "seg").mkdir(parents=True, exist_ok=True)
    tl, total = plan()
    T = total / FPS
    t_screen = next(s for s in tl if s["src"] == "screen")["start"] / FPS
    t_end = tl[-1]["start"] / FPS
    print(f"{len(tl)} shots, {T:.2f}s; website {t_screen:.2f}-{t_screen + SCREEN_FRAMES / FPS:.2f}s, end card {t_end:.2f}s", flush=True)
    stage_images(W)
    # graphics
    spec = {"dur": T, "screen": [t_screen, t_screen + SCREEN_FRAMES / FPS], "broll": [next(s for s in tl if s["src"] == "t7d")["start"] / FPS, t_end], "end": t_end}
    (W / "overlay_spec.json").write_text(json.dumps(spec))
    ov = W / "ov"
    subprocess.run(["node", str(P / "render_overlay.js"), str(W / "overlay_spec.json"), str(ov)], check=True)
    import os
    for f in sorted(ov.glob("f_*.png")):
        with Image.open(f) as im:
            if im.mode == "RGBA":
                continue
            tmp = f.with_suffix(".tmp.png"); im.convert("RGBA").save(tmp)
        os.replace(tmp, f)
    # picture: segments -> base (hard cuts; the white flashes are graphics) -> overlay
    files = [seg(s, W, i) for i, s in enumerate(tl)]
    lst = W / "seg" / "list.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in files))
    base = W / "base.mkv"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])
    assert count_frames(base) == total, (count_frames(base), total)
    for f in files:
        f.unlink()
    raw = W / "video.mp4"
    x265 = X265.replace("crf=12", "crf=20").replace("preset=medium", "preset=faster") if preview else X265
    g2 = (f"[0:v]settb=1/{FPS},setpts=N[b];[1:v]settb=1/{FPS},setpts=N," + GFX.format(n="o") + "[ov];"
          "[b][ov]overlay=format=yuv420p10:eof_action=repeat,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[vout]")
    ff(["-i", str(base), "-reinit_filter", "0", "-framerate", str(FPS), "-i", str(ov / "f_%05d.png"), "-filter_complex", g2, "-map", "[vout]",
        "-frames:v", str(total), "-r", str(FPS), "-fps_mode", "cfr", "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", x265, "-tag:v", "hvc1",
        *HDR_TAGS, str(raw)])
    assert count_frames(raw) == total
    # sound: original track + hits
    music = {"bpm": 120, "key": "F", "mode": "minor", "style": "phonk", "seed": 21, "duration": round(T, 3),
             "sections": [{"type": "drop", "bars": 2}, {"type": "groove", "bars": 6}, {"type": "build", "bars": 1, "stop": True},
                          {"type": "drop", "bars": 2}, {"type": "outro", "bars": 2}]}
    (W / "music.json").write_text(json.dumps(music))
    subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "tools/music.py"), str(W / "music.json"), str(W / "music.wav")], check=True)
    cue = lambda at, snd, g, **k: {"at": round(at, 4), "sound": snd, "gain_db": g, **k}
    cues = [cue(0.0, "impact", -8), cue(0.0, "whoosh_out", -12), cue(0.08, "slam", -13)]          # the page lands on beat 1
    for t in SWIPES:                                                                             # athlete cards sliding by
        cues.append(cue(t_screen + t, "whoosh_in", -19))
    t_set = t_screen + SCREEN_FRAMES / FPS
    cues += [cue(t_set - 4.8, "swell", -17, dur=4.6)]
    t_b = next(s for s in tl if s["src"] == "t7d")["start"] / FPS
    cues += [cue(t_b, "impact", -8), cue(t_b, "whoosh_out", -12)]
    for s in tl:
        t = s["start"] / FPS
        if t_b < t < t_end:
            cues.append(cue(t, "whip" if s.get("speed", 1) >= 1 else "thump", -14))
    cues += [cue(t_b, "slam", -11), cue(t_b + 1.0, "slam", -11)]                                 # WHITE / FRIDAY
    cues += [cue(t_end, "boom", -7), cue(t_end, "impact", -9), cue(t_end + 0.27, "slam", -13), cue(t_end + 0.52, "slam", -12),
             cue(t_end + 2.0, "whoosh_in", -14), cue(t_end + 2.02, "thump", -12)]
    silent = W / "silence.wav"
    ff(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", f"{T:.3f}", "-c:a", "pcm_s24le", str(silent)])
    mix = W / "mix.wav"
    R.build_mix(silent, cues, T, FPS, mix, {"path": str(W / "music.wav"), "gain_db": -3, "voice_dip_db": 0})
    final = P / "renders" / ("ifit_white_friday_preview.mp4" if preview else "ifit_white_friday.mp4")
    final.parent.mkdir(exist_ok=True)
    R.master_audio(mix, final, -14.0, -1.0, video=raw)
    raw.unlink()
    print("output", final, flush=True)
    return final


SWIPES = [10.0, 11.0, 12.0]          # replaced below by the measured slide times


def measure_swipes():
    """Frame-difference in the Athletes carousel band of the recording: the moments the cards slide (for the swipe SFX)."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "9", "-i", str(SRC["screen"][0]), "-vf", "fps=30,crop=1320:900:0:900,scale=132:90,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fs = 132 * 90
    fr_ = [np.frombuffer(raw[i:i + fs], np.uint8).astype(float) for i in range(0, len(raw) - fs + 1, fs)]
    d = [float(np.abs(fr_[i] - fr_[i - 1]).mean()) for i in range(1, len(fr_))]
    out, last = [], -9
    for i, v in enumerate(d):
        t = 9 + (i + 1) / 30
        if v > 6 and t - last > 0.6:
            out.append(round(t, 2)); last = t
    return out


if __name__ == "__main__":
    SWIPES = measure_swipes() or SWIPES
    print("swipes", SWIPES, flush=True)
    out = build(preview="--preview" in sys.argv)
