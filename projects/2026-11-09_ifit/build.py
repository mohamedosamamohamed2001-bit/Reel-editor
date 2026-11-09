"""iFit - White Friday campaign Reel (Coach Osama 2026-11-09).

BLACK -> WHITE: dark gym cuts under "BLACK FRIDAY?" -> the music stops on "NO..." -> a white flash: "WHITE FRIDAY" -> a fast
beat-cut training montage (speed ramps from his clips) -> a white flash into the iFit website screen recording, shown COMPLETE and
uninterrupted (all 17.77 s / 533 frames at 30 fps, original order; the Athletes scroll is untouched and the shot settles on him with
a slow push-in on his card) -> "WHITE FRIDAY IS HERE!" -> iFit logo end card.

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
CROP = (0, 130, 1320, 2480)            # x, y, w, h in the 1320x2868 recording
CARD = (82, 100, 916, 1720)            # x, y, w, h on the 1080x1920 frame
SCREEN_FRAMES = 533                    # 17.768 s at 30 fps = every frame pair of the 60 fps recording
HIS_CARD_Y = CARD[1] + CARD[3] * ((0.53 * 2868 - CROP[1]) / CROP[3])   # his athlete card centre on the frame (measured at 16 s)

# shots: (src, start in source s, output seconds, options). t9e / ms1 carry burned-in labels bottom-left ("Me to Me", "POV"):
# those shots are punched in >= 1.42x and framed fully right (fx=1.0) so the labels stay outside the frame.
# Cuts on the 120 bpm grid (0.5 s = a beat).
B = 0.5
SHOTS = [
    # HOOK - dark: BLACK FRIDAY?   (faces high in these takes: the hook type sits in the lower third)
    ("t7d", 4.4, B, dict(z=(1.18, 1.25), fy=.35)),
    ("ms1", 7.4, B, dict(z=(1.42, 1.48), fx=1.0, fy=.2)),
    ("t9e", 5.0, B, dict(z=(1.42, 1.48), fx=1.0, fy=.08)),
    ("t7d", 9.0, B, dict(z=(1.3, 1.36), fy=.35)),
    ("ms1", 9.6, B, dict(z=(1.42, 1.48), fx=1.0, fy=.2)),
    ("t9e", 6.6, B, dict(z=(1.42, 1.48), fx=1.0, fy=.08)),
    ("t7d", 13.4, B, dict(z=(1.2, 1.3), fy=.35, speed=0.5)),
    ("black", 0, B, {}),                                                        # 3.5 s: music stops - "NO..."
    ("white", 0, 1.5, {}),                                                      # 4.0 s: WHITE FRIDAY (graphics on white)
    # MONTAGE - on the drop
    ("t9e", 8.2, B, dict(z=(1.42, 1.48), fx=1.0, fy=.4)),
    ("ms1", 7.0, B, dict(z=(1.42, 1.48), fx=1.0, fy=.2)),
    ("t7d", 1.0, B, dict(z=(1.25, 1.3), fy=.35)),
    ("t9e", 10.6, B, dict(z=(1.42, 1.48), fx=1.0, fy=.45)),
    ("ms1", 11.0, B, dict(z=(1.42, 1.48), fx=1.0, fy=.2)),
    ("t9e", 11.6, 1.0, dict(z=(1.42, 1.48), fx=1.0, fy=.5, ramp=[(0.3, 1.0), (9, 0.35)])),
    ("t7d", 5.0, B, dict(z=(1.3, 1.36), fy=.35)),
    ("ms1", 8.6, B, dict(z=(1.42, 1.48), fx=1.0, fy=.2)),
    ("t7d", 14.6, 1.0, dict(z=(1.2, 1.3), fy=.35, ramp=[(0.3, 1.2), (9, 0.35)])),
    ("t9e", 13.4, B, dict(z=(1.42, 1.48), fx=1.0, fy=.55)),
    ("ms1", 12.0, B, dict(z=(1.42, 1.48), fx=1.0, fy=.2)),
    # WEBSITE - complete, uninterrupted, then held on him to the bar (push-in on his card while it settles)
    ("screen", 0, (SCREEN_FRAMES + 7) / FPS, dict(tin=("fadewhite", 0.0))),
    ("white", 0, 4.5, {}),                                                      # 30.0 s: WHITE FRIDAY IS HERE! -> iFit logo
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
        Z = f"(1+({z_end}-1)*pow(min(1,max(0,(t-{t0})/{5.0 + 7 / FPS})),1.6))"
        cy = HIS_CARD_Y
        g = (f"[0:v]fps={FPS},trim=end_frame={SCREEN_FRAMES},setpts=PTS-STARTPTS,crop={CROP[2]}:{CROP[3]}:{CROP[0]}:{CROP[1]},"
             f"scale={w}:{h}:flags=lanczos:in_color_matrix=bt709:in_range=tv:out_range=full,format=rgba[pg];[2:v]format=gray[mk];[pg][mk]alphamerge[card];"
             f"[1:v]loop=loop=-1:size=1,format=rgb24[bg];[bg][card]overlay={x}:{y}:shortest=1,"
             f"tpad=stop_mode=clone:stop=7,"
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
    spec = {"dur": T, "screen": [t_screen, t_screen + SCREEN_FRAMES / FPS], "end": t_end}
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
             "sections": [{"type": "build", "bars": 2, "stop": True}, {"type": "drop", "bars": 4}, {"type": "groove", "bars": 8},
                          {"type": "build", "bars": 1, "stop": True}, {"type": "drop", "bars": 1}, {"type": "outro", "bars": 2}]}
    (W / "music.json").write_text(json.dumps(music))
    subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "tools/music.py"), str(W / "music.json"), str(W / "music.wav")], check=True)
    cue = lambda at, snd, g, **k: {"at": round(at, 4), "sound": snd, "gain_db": g, **k}
    cues = [cue(0.0, "impact", -8), cue(0.12, "slam", -9), cue(0.62, "slam", -12)]
    cues += [cue(s["start"] / FPS, "whoosh_in", -18) for s in tl[1:7]]
    cues += [cue(3.5, "reverse_hit", -14, dur=0.5), cue(3.52, "click", -14)]                    # NO...
    cues += [cue(4.0, "impact", -7), cue(4.0, "whoosh_out", -12), cue(4.02, "chime", -15)]     # WHITE FRIDAY
    for s in tl:
        t = s["start"] / FPS
        if 5.5 <= t < t_screen:
            cues.append(cue(t, "whip" if s.get("speed", 1) > 1 else "whoosh_in", -15))
            if s.get("speed", 1) < 1:
                cues.append(cue(t, "thump", -12))
    cues += [cue(t_screen, "impact", -10), cue(t_screen, "whoosh_out", -13)]
    for t in SWIPES:                                                                             # athlete cards sliding by
        cues.append(cue(t_screen + t, "whoosh_in", -20))
    cues += [cue(t_screen + SCREEN_FRAMES / FPS - 4.8, "swell", -17, dur=4.6)]
    cues += [cue(t_end, "boom", -7), cue(t_end, "impact", -9), cue(t_end + 2.0, "whoosh_in", -14), cue(t_end + 2.02, "thump", -12)]
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
