#!/usr/bin/env python3
"""Measure a project's mix bus by bus (dialogue / ducked music / SFX), before rendering any picture.

    python3 tools/mix_report.py projects/<name> [--window 0.5]

Rebuilds the dialogue exactly as render_edit.py does, then runs the same music ducking chain but outputs each bus
alone, and prints short-term loudness per window plus the voice-to-music gap while he talks (target: music
>= 12 dB under the voice during speech; in music-only stretches the bed may come up to about the voice level).
Levels are pre-master (the master adds one constant gain to everything), so the gaps are what matter.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_edit as R  # noqa: E402
import sfx as sfxkit  # noqa: E402


def short_term(path):
    out = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-",
                          "-f", "null", "-"], capture_output=True, text=True).stdout
    ts, vs, cur = [], [], None
    for line in out.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            cur = float(m.group(1))
        m = re.search(r"M=(-?[\d.]+|-inf)", line)
        if m and cur is not None:
            ts.append(cur)
            vs.append(-120.0 if m.group(1) == "-inf" else float(m.group(1)))
    return ts, vs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--window", type=float, default=0.5)
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    edit = json.loads((proj / "edit.json").read_text())
    fps = edit["fps"]
    amap = edit.get("audio", {})
    clips = []
    total = 0
    for c in edit["clips"]:
        sp = c.get("speed", 1)
        silent = c.get("freeze", False) or sp != 1
        n = R.plate_frames(c, fps) if edit.get("plates") else R.jsround(c["out"] * fps) - R.jsround(c["in"] * fps)
        clips.append({"path": str((proj / amap.get(c["src"], edit["media"][c["src"]])).resolve()), "in": c["in"], "out": c["out"],
                      "volume": c.get("volume", 1), "silent": silent, "len": n / fps,
                      "start": R.first_frame(c, fps) / fps if edit.get("plates") else c["in"]})
        total += n / fps
    total += edit.get("tail", 0)
    tmp = Path(tempfile.mkdtemp())
    dlg = tmp / "dialogue.wav"
    R.build_dialogue(clips, total, dlg, edit.get("dialogueFx"), edit.get("dialogueLufs"))
    bus, _ = sfxkit.render_cues(edit.get("sfx", {}).get("cues", []), total, fps)
    sfx_wav = tmp / "sfx.wav"
    sfxkit.write_wav(sfx_wav, bus)
    m = edit.get("music")
    music_wav = tmp / "music_ducked.wav"
    if m:
        graph = (f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={total:.3f},apad=whole_dur={total:.3f},"
                 f"highpass=f=30,equalizer=f=2200:t=q:w=1.0:g={m.get('voice_dip_db', -4)},volume={m.get('gain_db', -8)}dB[m];"
                 f"[m][0:a]sidechaincompress=threshold={m.get('duck_threshold', 0.02)}:ratio={m.get('duck_ratio', 4)}:attack=15:release=320:knee=4[out]")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(dlg), "-i", str((proj / m["src"]).resolve()), "-filter_complex", graph,
                        "-map", "[out]", str(music_wav)], check=True)
    sfx_proc = tmp / "sfx_proc.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(sfx_wav), "-af", "highpass=f=40,equalizer=f=2500:t=q:w=1.2:g=-4", str(sfx_proc)], check=True)
    buses = {"voice": short_term(dlg), "music": short_term(music_wav) if m else ([], []), "sfx": short_term(sfx_proc)}
    print(f"{'t':>6} {'voice':>7} {'music':>7} {'sfx':>7}  gap(v-m)")
    t = 0.0
    gaps = []
    while t < total:
        row = []
        for k in ("voice", "music", "sfx"):
            ts, vs = buses[k]
            sel = [v for tt, v in zip(ts, vs) if t <= tt < t + a.window]
            row.append(max(sel) if sel else -120.0)
        gap = row[0] - row[1] if row[0] > -40 and row[1] > -70 else None
        if gap is not None:
            gaps.append(gap)
        print(f"{t:6.1f} {row[0]:7.1f} {row[1]:7.1f} {row[2]:7.1f}  {'' if gap is None else f'{gap:5.1f}'}")
        t += a.window
    if gaps:
        print(f"\nvoice-over-music while talking: min {min(gaps):.1f} dB, median {sorted(gaps)[len(gaps) // 2]:.1f} dB")


if __name__ == "__main__":
    main()
