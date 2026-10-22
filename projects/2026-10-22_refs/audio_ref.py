"""Coach Osama 2026-10-22: each edit carries the original sound of its Drive source file (Video 1 exercise / Video 2 photo /
Video 3 photo.mp4 = the reference recordings), sample-for-sample from t=0 (the edits keep the references' timeline 1:1, so
the sound lines up with the on-screen text), with the OSM music bed kept well underneath. Master -14 LUFS / -1 dBTP."""
import re, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parent
SRC = {"1": "source/ref1.mp4", "2": "source/ref2.mp4", "3": "source/ref3.mp4"}
PIC = {"1": "work/OSM_Video_1_musiconly.mp4", "2": "renders/OSM_Video_2.mp4", "3": "renders/OSM_Video_3.mp4"}


def lufs(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)


for k in sys.argv[1:]:
    w = P / f"work/v{k}"; pic = P / PIC[k]; T = dur(pic)
    orig = w / "orig.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / SRC[k]), "-vn", "-t", str(T), "-ar", "48000", "-ac", "2", str(orig)], check=True)
    go = round(-16.0 - lufs(orig), 1); gm = round(-28.0 - lufs(w / "music.wav"), 1)
    mix = w / "mix_ref.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(orig), "-i", str(w / "music.wav"), "-filter_complex",
                    f"[0:a]volume={go}dB[o];[1:a]volume={gm}dB,atrim=duration={T}[m];[o][m]amix=inputs=2:normalize=0:duration=longest[a]",
                    "-map", "[a]", "-t", str(T), str(mix)], check=True)
    g = round(-14.0 - lufs(mix), 2); mst = w / "master_ref.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mix), "-af", f"volume={g}dB,aresample=192000,"
                    "alimiter=limit=0.66:attack=1:release=50:level=false,aresample=48000", str(mst)], check=True)
    if not (w / "picture.mp4").exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pic), "-map", "0:v", "-c", "copy", str(w / "picture.mp4")], check=True)
    out = P / f"renders/OSM_Video_{k}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(w / "picture.mp4"), "-i", str(mst), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out)], check=True)
    print(k, f"source {SRC[k]} gain {go} dB, music {gm} dB, master {g} dB -> {lufs(out)} LUFS")
