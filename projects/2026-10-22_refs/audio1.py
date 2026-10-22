"""Video 1 audio: each shot's ORIGINAL camera sound (same file, same in-point, same duration as the picture), levelled per
clip, joined with 10 ms fades at cuts; the original music bed sits under it at -24 LUFS; master -14 LUFS / -1 dBTP."""
import json, re, subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
c = json.loads((P / "videos.json").read_text())["1"]
T = c["duration"]


def lufs(args):
    r = subprocess.run(["ffmpeg", "-hide_banner", *args, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])


TARGET = {"source/train_b.mov": -20.0}  # train_b's own track is a music bed: keep it, but under the speech-level clips
ins, parts = [], []
for i, s in enumerate(c["shots"]):
    L = lufs(["-ss", str(s["in"]), "-t", str(s["dur"]), "-i", str(P / s["src"]), "-vn"])
    g = min(12.0, round(TARGET.get(s["src"], -17.0) - L, 1))  # cap: more just lifts room hiss
    ins += ["-i", str(P / s["src"])]
    parts.append(f"[{i}:a:0]atrim=start={s['in']}:duration={s['dur']},asetpts=PTS-STARTPTS,aresample=48000,"
                 f"aformat=channel_layouts=stereo,volume={g}dB,afade=t=in:d=0.01,afade=t=out:st={s['dur'] - 0.01}:d=0.01[s{i}]")
    print(f"shot {i}: {s['src']} {s['in']}+{s['dur']}s  clip {L} LUFS -> gain {g} dB")
n = len(c["shots"])
m = P / "work/v1/music.wav"
gm = round(-24.0 - lufs(["-i", str(m)]), 1)
ins += ["-i", str(m)]
g = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[orig];" \
    f"[{n}:a]volume={gm}dB,atrim=duration={T}[mus];[orig][mus]amix=inputs=2:normalize=0:duration=first[mix]"
tmp = P / "work/v1/mix.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", g, "-map", "[mix]", "-t", str(T), str(tmp)], check=True)
gain = round(-14.0 - lufs(["-i", str(tmp)]), 2)
out = P / "work/v1/master.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", f"volume={gain}dB,aresample=192000,"
                "alimiter=limit=0.70:attack=1:release=50:level=false,aresample=48000", str(out)], check=True)
print("music", gm, "dB; master gain", gain, "dB ->", lufs(["-i", str(out)]), "LUFS")
