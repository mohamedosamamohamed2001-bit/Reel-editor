#!/usr/bin/env python3
"""Motion QC for motion pieces and edits (docs/motion/MOTION_SYSTEM.md, Spec 1 build 5 / Spec 2 build 5).

    python3 tools/motion_qc.py VIDEO [--bpm 120] [--max-hold 0.5] [--loop] [--out DIR]

Checks (numbers, not opinions; the visual review of the per-beat sheet is still required):
- holds: stretches where the picture is (nearly) static for longer than --max-hold seconds (Spec 2 bans holds > 0.5 s)
- beats (with --bpm): visual change and an audio onset at every beat ("something happens on every beat")
- loop (with --loop): first vs last frame PSNR (Spec 2: the final frame matches the first)
- sheet: one frame per beat (or per second without --bpm) -> DIR/beats.jpg, to look at before any full render is approved
Writes DIR/motion_qc.json. Exit 1 if a hard check fails.
"""
import argparse, json, math, subprocess
from pathlib import Path

import numpy as np


def probe(v):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                                   "-of", "json", v], capture_output=True, text=True, check=True).stdout)
    vs = next(s for s in j["streams"] if s["codec_type"] == "video")
    n, d = vs["r_frame_rate"].split("/")
    return float(n) / float(d), float(j["format"]["duration"]), int(vs["width"]), int(vs["height"]), any(s["codec_type"] == "audio" for s in j["streams"])


def frames(v, w=96):
    fps, dur, W, H, _ = probe(v)
    h = int(round(w * H / W / 2)) * 2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32), fps


def audio_env(v, sr=8000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-map", "0:a:0", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32), sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--max-hold", type=float, default=0.5)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    v = a.video
    out = Path(a.out or Path(v).with_suffix("")).with_name(Path(a.out).name if a.out else Path(v).stem + "_motionqc")
    out.mkdir(parents=True, exist_ok=True)
    fps, dur, W, H, has_audio = probe(v)
    fr, fps = frames(v)
    diff = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))           # change between frame i and i+1 (0-255)
    rep, ok = {"video": v, "fps": fps, "duration": round(dur, 3), "size": [W, H]}, True

    # holds
    static = diff < 0.15
    holds, i = [], 0
    while i < len(static):
        if static[i]:
            j = i
            while j < len(static) and static[j]:
                j += 1
            if (j - i) / fps > a.max_hold:
                holds.append([round(i / fps, 3), round(j / fps, 3)])
            i = j
        else:
            i += 1
    rep["holds"] = holds
    print(f"{'PASS' if not holds else 'FAIL'} holds > {a.max_hold}s: {holds or 'none'}")
    ok &= not holds

    # beats
    times = []
    if a.bpm:
        bl = 60 / a.bpm
        times = [k * bl for k in range(int(dur / bl + 1e-6) + 1) if k * bl < dur - 1e-6]
        med = float(np.median(diff)) + 1e-6
        dead = []
        for t in times:
            k = int(round(t * fps))
            win = diff[max(0, k - 2):k + 4]
            if win.size == 0 or win.max() < 0.25:
                dead.append(round(t, 3))
        rep["beats"] = {"count": len(times), "visually_static": dead}
        print(f"{'PASS' if not dead else 'FAIL'} visual change at every beat ({len(times)} beats): static at {dead or 'none'}")
        ok &= not dead
        if has_audio:
            x, sr = audio_env(v)
            hop = int(sr * 0.01)
            env = np.sqrt(np.convolve(x * x, np.ones(hop) / hop, mode="same"))[::hop]
            on = np.maximum(0, np.diff(env, prepend=env[0]))
            thr = max(1e-4, np.percentile(on, 90))
            silent = [round(t, 3) for t in times if on[max(0, int(t * 100) - 3):int(t * 100) + 4].max(initial=0) < thr]
            rep["beats"]["audio_without_onset"] = silent
            print(f"{'PASS' if not silent else 'WARN'} audio onset on every beat: missing at {silent or 'none'}")

    # loop
    if a.loop:
        f0, f1 = fr[0], fr[-1]
        mse = float(((f0 - f1) ** 2).mean())
        psnr = 99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse)
        rep["loop_psnr"] = round(psnr, 1)
        print(f"{'PASS' if psnr >= 30 else 'FAIL'} loop: first vs last frame PSNR {psnr:.1f} dB (>= 30)")
        ok &= psnr >= 30

    # per-beat sheet
    pts = times or [float(t) for t in range(int(dur) + 1) if t < dur]
    sel = "+".join(f"eq(n\\,{int(round(t * fps))})" for t in pts)
    cols = min(8, len(pts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", f"select='{sel}',scale=240:-2,tile={cols}x{math.ceil(len(pts) / cols)}:padding=4:color=0x0A0F16",
                    "-vsync", "0", "-frames:v", "1", str(out / "beats.jpg")], check=True)
    rep["sheet"] = str(out / "beats.jpg")
    rep["pass"] = bool(ok)
    (out / "motion_qc.json").write_text(json.dumps(rep, indent=1))
    print(f"sheet: {out / 'beats.jpg'}\n{'ALL PASS' if ok else 'CHECK FAILED'}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
