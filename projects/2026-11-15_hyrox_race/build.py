"""HYROX CAIRO race film (Coach Osama 2026-11-15): his own race footage, edited in the style of his reference (Vedio1.mov).

Reference analysis (analysis/ref_*.jpg): music ~105 bpm (beat 0.571 s), quiet build to a drop at ~5.7 s, cuts on beats every 1-2
beats with a few holds; intro title "HYROX" (tall condensed caps, echo/double-exposure entrance + light-leak flash, a second word
flying in as giant letters then settling as wide-tracked small caps, tiny eyebrow above) held while footage cuts underneath;
light leaks, prism/chromatic hits, one mirrored-kaleidoscope glitch, slow-motion holds, and a closing white iris "black hole".
His brief: same editing approach, but footage natural (no stylised grade), every station clear, story = the whole race.

Footage: iPhone HLG (most clips 120 fps -> real slow motion) kept in its own 10-bit HLG; his photos (sRGB) converted SDR -> HLG at
203-nit graphics white like the graphics. Picture cuts snap to the 105 bpm beat grid. Music: original track (tools/music.py, 105 bpm,
trap) built on the same section plan; SFX (tools/sfx.py) on every cut / hit; the race's own crowd sound under it, low.

    python3 projects/2026-11-15_hyrox_race/build.py [--preview]
"""
import json, os, subprocess, sys
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_edit as R  # noqa: E402

FPS = 30
BPM = 105
BEAT = 60 / BPM
V = lambda n: P / "source" / f"IMG_{n}.mov" if (P / "source" / f"IMG_{n}.mov").exists() else P / "source" / f"IMG_{n}.MOV"
AIDX = {"5025": 1, "5041": 1}                                    # AAC stream index (others: 2; stream 1 there is Apple APAC)
PHOTO = lambda n: P / "work" / "photos" / f"IMG_{n}.png"
HDR_TAGS = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
SDR2HLG = "format=gbrpf32le,zscale=tin=bt709:pin=bt709:min=gbr:rin=full:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,format=yuv420p10le"
GFX = ("format=rgba,split[c{n}][a{n}];[c{n}]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,"
       "format=yuv420p10le[cy{n}];[a{n}]alphaextract,format=gray10le[al{n}];[cy{n}][al{n}]alphamerge")
X265 = "crf=12:preset=medium:pools=2:frame-threads=2:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error"

# (source, start s, beats, options). source = clip number, or "p:NNNN" for a photo. Options: z=(from,to) zoom, fx/fy framing,
# speed, ramp=[(output s, speed), ...], prism (chromatic hit on the first frames), mirror (kaleidoscope glitch), kb (photo push-in)
SHOTS = [
    # INTRO (build): race atmosphere under the title
    ("5032", 0.0, 2, dict(z=(1.15, 1.25), prism=True)),
    ("5025", 2.6, 2, dict(z=(1.0, 1.1))),
    ("5026", 0.3, 2, dict(z=(1.1, 1.2))),
    ("5029", 1.5, 2, dict(z=(1.05, 1.15))),
    # 01 SKIERG (drop)
    ("5024", 0.8, 2, dict(z=(1.15, 1.2), prism=True)),
    ("5024", 3.0, 2, dict(z=(1.25, 1.35), ramp=[(0.25, 1.0), (9, 0.4)])),
    ("5024", 6.6, 2, dict(z=(1.1, 1.18))),
    ("5025", 4.4, 2, dict(z=(1.1, 1.2))),                                      # run
    # 02 SLED PUSH
    ("5026", 9.6, 2, dict(z=(1.3, 1.4), fy=.6)),
    ("5029", 13.0, 2, dict(z=(1.15, 1.25), fy=.55)),
    ("5026", 11.4, 2, dict(z=(1.35, 1.45), fy=.6, speed=0.5)),
    ("5032", 2.2, 2, dict(z=(1.1, 1.2))),                                      # run
    # burpee-broad-jump zone (his photos there)
    ("p:2085", 0, 1, dict(kb=(1.0, 1.08))),
    ("p:5036", 0, 1, dict(kb=(1.04, 1.12))),
    # 05 ROW
    ("5041", 1.5, 2, dict(z=(1.2, 1.3), fy=.6)),
    ("p:2098", 0, 1, dict(kb=(1.0, 1.08))),
    ("p:2100", 0, 1, dict(kb=(1.05, 1.12))),
    ("5041", 6.5, 2, dict(z=(1.3, 1.4), fy=.6, speed=0.6)),
    ("2149", 2.6, 2, dict(z=(1.05, 1.12))),                                    # Roxzone run with water
    # 06 FARMERS CARRY
    ("2149", 0.0, 2, dict(z=(1.0, 1.08))),
    ("p:5044", 0, 2, dict(kb=(1.0, 1.1))),
    ("5050", 1.8, 2, dict(z=(1.0, 1.08))),                                     # water station
    # 07 SANDBAG LUNGES
    ("5050", 13.2, 2, dict(z=(1.15, 1.22), prism=True)),
    ("5050", 16.6, 2, dict(z=(1.2, 1.3), ramp=[(0.2, 1.0), (9, 0.45)])),
    ("5050", 20.4, 2, dict(z=(1.1, 1.18))),
    # 08 WALL BALLS
    ("5057", 0.6, 2, dict(z=(1.05, 1.12))),
    ("5058", 2.0, 0.5, dict(z=(1.1, 1.1), mirror=True)),
    ("5058", 2.3, 1.5, dict(z=(1.2, 1.28))),
    ("5058", 8.4, 2, dict(z=(1.3, 1.4), speed=0.5)),
    ("5032", 3.2, 2, dict(z=(1.1, 1.2), prism=True)),                         # final run
    # FINISH
    ("5071", 0.0, 3, dict(z=(1.0, 1.08))),
    ("p:5051", 0, 1, dict(kb=(1.0, 1.06))),
    ("5071", 1.8, 2, dict(z=(1.08, 1.2))),
    ("white", 0, 1, {}),                                                         # iris closes to white
]
LABELS = [(4, "SKIERG"), (16, "SLED PUSH"), (26, "ROW"), (34, "FARMERS CARRY"), (40, "SANDBAG LUNGES"), (46, "WALL BALLS"), (54, "FINISH")]


def bt(k):                     # beat -> frame (cuts land on the nearest frame of the 105 bpm grid)
    return round(k * BEAT * FPS)


def plan():
    tl, k = [], 0.0
    for src, a, beats, o in SHOTS:
        f0, f1 = bt(k), bt(k + beats)
        n = f1 - f0
        if o.get("ramp"):
            st, rem = f0, n
            for i, (d, spd) in enumerate(o["ramp"]):
                m = rem if i == len(o["ramp"]) - 1 else min(rem, round(d * FPS))
                tl.append(dict(src=src, a=round(a, 4), speed=spd, n=m, start=st, o=o, first=(i == 0)))
                a += m * spd / FPS; st += m; rem -= m
        else:
            tl.append(dict(src=src, a=a, speed=o.get("speed", 1.0), n=n, start=f0, o=o, first=True))
        k += beats
    return tl, bt(k)


def ff(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], check=True)


def seg(s, W, i, total_shot):
    out = W / "seg" / f"s{i:02d}.mkv"
    n, o = s["n"], s["o"]
    enc = ["-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", "crf=6:preset=fast:pools=2:frame-threads=1:log-level=error",
           "-tag:v", "hvc1", *HDR_TAGS, "-frames:v", str(n), "-r", str(FPS), str(out)]
    if s["src"] == "white":
        ff(["-f", "lavfi", "-i", f"color=c=white:s=1080x1920:r={FPS}:d={n / FPS + 0.1}", "-vf", "format=rgb24," + SDR2HLG, *enc])
        return out
    if s["src"].startswith("p:"):
        z0, z1 = o.get("kb", (1.0, 1.08))
        Z = f"({z0}+({z1}-{z0})*t/{n / FPS:.4f})"
        im = Image.open(PHOTO(s["src"][2:])); w, h = im.size
        sc = max(1080 / w, 1920 / h)                                  # cover-fit to 9:16 (centre crop)
        g = (f"[0:v]scale={round(w * sc / 2) * 2}:{round(h * sc / 2) * 2}:flags=lanczos,crop=1080:1920,format=rgb24,"
             f"scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.4,{SDR2HLG}[v]")
        ff(["-loop", "1", "-framerate", str(FPS), "-t", f"{n / FPS + 0.1}", "-i", str(PHOTO(s["src"][2:])), "-filter_complex", g, "-map", "[v]", *enc])
        return out
    sp = s["speed"]
    z0, z1 = o.get("z", (1.0, 1.0))
    L = total_shot / FPS
    t0 = (s["start"] - s["shot_start"]) / FPS                           # zoom continues across ramp pieces of one shot
    Z = f"({z0}+({z1}-{z0})*(t+{t0:.4f})/{L:.4f})"
    f = [f"[0:v]trim=start={s['a']:.4f}:end={s['a'] + n * sp / FPS + 0.3:.4f},setpts=PTS-STARTPTS"]
    if sp != 1:
        f.append(f"setpts=PTS/{sp}")
    f.append(f"fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS")
    f.append(f"scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,"
             f"crop=1080:1920:x='(iw-1080)*{o.get('fx', .5)}':y='(ih-1920)*{o.get('fy', .5)}',format=yuv420p10le")
    if o.get("mirror") and s["first"]:                                  # kaleidoscope glitch: top half mirrored down
        f.append("split[m1][m2];[m1]crop=1080:960:0:0[top];[m2]crop=1080:960:0:0,vflip[bot];[top][bot]vstack")
    if o.get("prism") and s["first"]:                                   # chromatic split on the first 5 frames (the hit), easing out
        f.append("chromashift=cbh=-14:crh=14:cbv=4:crv=-4:enable='lt(n,5)'")
    f.append("setsar=1")
    ff(["-i", str(V(s["src"])), "-filter_complex", ",".join(f) + "[v]", "-map", "[v]", "-an", *enc])
    return out


def count_frames(p):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets",
                               "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True).stdout.strip())


def ambience(tl, total, dst):
    """The race's own sound (crowd, machines) under the music: real-speed video shots only, low, 20 ms crossfades."""
    ins, g, lab = [], [], []
    for i, s in enumerate(tl):
        if s["src"].startswith("p:") or s["src"] == "white" or s["speed"] != 1:
            continue
        ins += ["-i", str(V(s["src"]))]; j = len(ins) // 2 - 1
        d = s["n"] / FPS
        g.append(f"[{j}:{AIDX.get(s['src'], 2)}]atrim=start={s['a']:.4f}:end={s['a'] + d:.4f},asetpts=PTS-STARTPTS,aresample=48000,"
                 f"aformat=channel_layouts=stereo,afade=t=in:d=0.02,afade=t=out:st={max(0, d - 0.02):.3f}:d=0.02,adelay={round(s['start'] / FPS * 1000)}:all=1[a{i}]")
        lab.append(f"[a{i}]")
    g.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0,apad=whole_dur={total:.3f},atrim=end={total:.3f},highpass=f=120,lowpass=f=9000[o]")
    ff([*ins, "-filter_complex", ";".join(g), "-map", "[o]", "-c:a", "pcm_s24le", str(dst)])


def build(preview=False):
    W = P / "work"
    (W / "seg").mkdir(parents=True, exist_ok=True)
    tl, total = plan()
    # remember each shot's first frame and length (zoom runs across ramp pieces)
    for s in tl:
        same = [x for x in tl if x["o"] is s["o"]]
        s["shot_start"], s["shot_len"] = same[0]["start"], sum(x["n"] for x in same)
    T = total / FPS
    print(f"{len(tl)} pieces, {total} frames = {T:.2f}s", flush=True)
    # graphics
    beat_s = lambda k: round(bt(k) / FPS, 4)
    spec = {"dur": T, "beat": BEAT,
            "title": {"at": beat_s(2), "until": beat_s(8)},
            "labels": [{"at": beat_s(k) + 0.03, "dur": 2 * BEAT, "text": t} for k, t in LABELS],
            "leaks": [beat_s(k) for k in (2, 8, 24, 38, 46, 54)],
            "flashes": [round(s["start"] / FPS, 4) for s in tl if s["src"].startswith("p:")],
            "iris": {"at": beat_s(59.3), "full": beat_s(60)}}
    (W / "overlay_spec.json").write_text(json.dumps(spec, indent=1))
    ov = W / "ov"
    subprocess.run(["node", str(P / "render_overlay.js"), str(W / "overlay_spec.json"), str(ov)], check=True)
    for f in sorted(ov.glob("f_*.png")):
        with Image.open(f) as im:
            if im.mode == "RGBA":
                continue
            tmp = f.with_suffix(".tmp.png"); im.convert("RGBA").save(tmp)
        os.replace(tmp, f)
    # picture
    files = [seg(s, W, i, s["shot_len"]) for i, s in enumerate(tl)]
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
    # sound: original 105 bpm track on the reference's shape (build -> drop on the first station), SFX on every cut
    music = {"bpm": BPM, "key": "E", "mode": "minor", "style": "trap", "seed": 33, "duration": round(T + 0.6, 3),
             "sections": [{"type": "build", "bars": 2, "stop": True}, {"type": "drop", "bars": 6}, {"type": "break", "bars": 1},
                          {"type": "build", "bars": 1, "stop": True}, {"type": "drop", "bars": 4}, {"type": "groove", "bars": 1},
                          {"type": "outro", "bars": 1}]}
    (W / "music.json").write_text(json.dumps(music))
    subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "tools/music.py"), str(W / "music.json"), str(W / "music.wav")], check=True)
    cue = lambda at, snd, g, **k: {"at": round(at, 4), "sound": snd, "gain_db": g, **k}
    cues = [cue(0.0, "whoosh_in", -12), cue(beat_s(2), "impact", -9), cue(beat_s(2), "reverse_hit", -14, dur=0.5), cue(beat_s(5.5), "swell", -15, dur=1.4)]
    for s in tl:
        if not s["first"] or s["start"] == 0:
            continue
        t = s["start"] / FPS
        if s["src"].startswith("p:"):
            cues.append(cue(t, "click", -12)); cues.append(cue(t, "whoosh_out", -18))
        elif s["o"].get("mirror"):
            cues.append(cue(t, "blip", -12)); cues.append(cue(t + 0.05, "key", -14))
        elif s["o"].get("prism"):
            cues.append(cue(t, "impact", -11)); cues.append(cue(t, "whip", -14))
        else:
            cues.append(cue(t, "whoosh_in", -17))
        if s["speed"] < 1 or s["o"].get("ramp"):
            cues.append(cue(t + (s["o"]["ramp"][0][0] if s["o"].get("ramp") else 0), "thump", -12, freq=48, dur=0.5))
    for k, _ in LABELS:
        cues.append(cue(beat_s(k) + 0.03, "slam", -15))
    cues += [cue(beat_s(8), "boom", -8), cue(beat_s(40), "boom", -9), cue(beat_s(38.5), "swell", -15, dur=0.8)]
    cues += [cue(beat_s(59.3), "reverse_hit", -11, dur=0.4), cue(beat_s(60), "impact", -8), cue(beat_s(60), "chime", -16)]
    silent = W / "silence.wav"
    ff(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{T:.3f}", "-c:a", "pcm_s24le", str(silent)])
    mix0 = W / "mix0.wav"
    R.build_mix(silent, cues, T, FPS, mix0, {"path": str(W / "music.wav"), "gain_db": -2, "voice_dip_db": 0})
    amb = W / "ambience.wav"
    ambience(tl, T, amb)
    mix = W / "mix.wav"
    ff(["-i", str(mix0), "-i", str(amb), "-filter_complex", "[1:a]volume=-17dB[b];[0:a][b]amix=inputs=2:normalize=0:duration=first[o]",
        "-map", "[o]", "-c:a", "pcm_s24le", str(mix)])
    final = P / "renders" / ("hyrox_race_preview.mp4" if preview else "hyrox_race.mp4")
    final.parent.mkdir(exist_ok=True)
    R.master_audio(mix, final, -14.0, -1.0, video=raw)
    raw.unlink()
    print("output", final, flush=True)
    return final


if __name__ == "__main__":
    build(preview="--preview" in sys.argv)
