"""HYROX training session (2026-10-24): one full edit of Coach Osama and Yousef from both Drive folders.

Personal video: no OSM branding, no text, no names, no logos, no end card. Natural colour (HLG decoded plainly,
light contrast only). Cuts sit on a 133 BPM grid ("Sweet but Psycho", added in Instagram at 0:00: commercial
songs can't be embedded here). Camera audio removed; the sound is the in-house SFX kit (tools/sfx.py).
"The end video" is the last shot, with nothing after it.

    python3 build.py [--preview]
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
SFXDIR = P.parents[0] / "2026-10-23_alphax" / "work" / "sfx"
W, H, FPS = 1080, 1920, 30
SRC = {"0651": "A_IMG_0651.MOV", "0731": "A_IMG_0731.MOV", "0751": "A_IMG_0751.MOV", "0767": "A_IMG_0767.MOV",
       "0768": "A_IMG_0768.MOV", "3926": "A_IMG_3926.MOV", "3927": "A_IMG_3927.MOV", "3929": "A_IMG_3929.MOV",
       "3933": "A_IMG_3933.MOV", "3935": "A_IMG_3935.MOV", "3936": "A_IMG_3936.MOV", "3941": "A_IMG_3941.MOV",
       "7129": "A_IMG_7129.mov", "END": "A_END.mov", "5d7a": "B_5d7aad9a.mov", "9982": "B_IMG_9982.mov",
       "9993": "B_IMG_9993.mov"}
SDR = {"7129", "5d7a"}
LOOK_HLG = "eq=contrast=1.07:saturation=1.04"   # plain HLG decode keeps his orange tank orange; light lift only
LOOK_SDR = "eq=contrast=1.0:saturation=0.93"    # the SDR phone clips run hotter: pull them to match
SFX = {"air": .252, "whoosh_in": .527, "whoosh_out": .09, "swell": .55, "thump": 0, "impact": 0, "click": 0,
       "boom": 0, "whip": .165, "riser": 1.0, "slam": 0, "bass_drop": 0, "reverse_hit": .7}


def run(c):
    subprocess.run(c, check=True)


def main(preview=False):
    c = json.loads((P / "edit.json").read_text())
    beat = 60.0 / c["bpm"]
    w, h = (540, 960) if preview else (W, H)
    ins, fl, t, cues = [], [], 0.0, []

    def shot(i, s, d):
        sp = s.get("sp", 1.0)
        z, fx, fy = s.get("z", 1.0), s.get("fx", 0.5), s.get("fy", 0.5)
        ins.extend(["-i", str(P / "source" / SRC[s["c"]])])
        look = LOOK_SDR if s["c"] in SDR else LOOK_HLG
        f = (f"[{i}:v]trim=start={s.get('in', 0)}:duration={d * sp + 0.05},setpts=(PTS-STARTPTS)/{sp},fps={FPS},"
             f"trim=duration={d},setpts=PTS-STARTPTS,format=yuv420p,{look},"
             f"scale={w}*{z}:{h}*{z}:force_original_aspect_ratio=increase:flags=lanczos,"
             f"crop={w}:{h}:(iw-{w})*{fx}:(ih-{h})*{fy},setsar=1")
        if s.get("flash"):
            f += ",fade=t=in:st=0:d=0.1:color=white"
        return f

    for i, s in enumerate(c["shots"]):
        d = round(round(s["b"] * beat * FPS) / FPS, 4)
        fl.append(shot(i, s, d) + f"[v{i}]")
        for snd in s.get("sfx", []):
            cues.append((t, snd[0], snd[1]))
        t += d
    n = len(c["shots"])
    e = c["end"]
    src_d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(P / "source" / SRC[e["c"]])], capture_output=True, text=True).stdout)
    de = round(int((src_d - 0.02) / e["sp"] * FPS) / FPS, 4)
    fl.append(shot(n, {**e, "flash": True}, de) + f",fade=t=out:st={de - 0.3}:d=0.3[v{n}]")
    for snd in e.get("sfx", []):
        cues.append((t, snd[0], snd[1]))
    T_end0, T = t, t + de
    fl.append("".join(f"[v{i}]" for i in range(n + 1)) + f"concat=n={n + 1}:v=1:a=0,format=yuv420p[vout]")

    ai = n + 1
    for q, (tc, name, gain) in enumerate(cues):
        ins.extend(["-i", str(SFXDIR / f"{name}.wav")])
        start = max(0.0, tc - SFX[name])
        fl.append(f"[{ai + q}:a]volume={gain}dB,adelay={int(start * 1000)}|{int(start * 1000)}[s{q}]")
    fl.append("".join(f"[s{q}]" for q in range(len(cues))) +
              f"amix=inputs={len(cues)}:normalize=0,apad,atrim=duration={T}[aout]")
    out = P / "renders"; out.mkdir(exist_ok=True)
    raw = P / "work" / "raw.mov"; raw.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "veryfast" if preview else "slow", "-crf", "23" if preview else "16",
         "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-r", str(FPS), "-c:a", "pcm_f32le", "-t", f"{T}", str(raw)])
    # SFX bus: peak-normalise to -3 dBFS, then a 4x-oversampled limiter (the song is added on top in the app)
    vd = subprocess.run(["ffmpeg", "-v", "info", "-i", str(raw), "-af", "volumedetect", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    peak = float(vd.split("max_volume: ")[1].split(" dB")[0])
    dst = out / (f"{c['name']}_preview.mp4" if preview else f"{c['name']}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af",
         f"volume={-3 - peak:.2f}dB,aresample=192000,alimiter=limit=0.708:attack=1:release=60:level=false,aresample=48000",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(dst)])
    raw.unlink()
    print(f"{dst.name}: {T:.2f}s, {n} shots + end video at {T_end0:.2f}s, beat {beat:.3f}s")


if __name__ == "__main__":
    main("--preview" in sys.argv)
