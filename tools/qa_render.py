#!/usr/bin/env python3
"""Automated technical QA for a rendered (or source) video.

Usage:
    python3 tools/qa_render.py VIDEO [--out DIR] [--expect WxH] [--fps N]
                               [--lufs -14] [--tp -1.0] [--sheet-cols 5 --sheet-rows 4]

Writes DIR/qa.json and DIR/contact_sheet.jpg. Exit code 1 if a hard check fails.
Only what this script measures is reported as checked; visual and creative QA
is still done by inspecting frames and the contact sheet.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if r.returncode != 0:
        raise SystemExit(f"ffprobe failed: {r.stderr.strip()}")
    return json.loads(r.stdout)


def fps_of(stream):
    num, den = stream.get("avg_frame_rate", "0/1").split("/")
    return float(num) / float(den) if float(den) else 0.0


def detect_video_issues(path):
    """Black and frozen intervals in one decode pass."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-map", "0:v:0",
             "-vf", "blackdetect=d=0.1:pic_th=0.98,freezedetect=n=0.001:d=0.5", "-an", "-f", "null", "-"])
    black = [{"start": float(a), "end": float(b)} for a, b in
             re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)]
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", r.stderr)]
    frozen = [{"start": s, "end": ends[i] if i < len(ends) else None} for i, s in enumerate(starts)]
    return black, frozen


def detect_audio(path):
    """Integrated loudness, LRA, true peak (EBU R128), silences and sample peak."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a:0",
             "-af", "ebur128=peak=true,silencedetect=n=-50dB:d=0.7,astats=metadata=0:reset=0",
             "-f", "null", "-"])
    err = r.stderr
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else ""

    def grab(pattern, text):
        m = re.search(pattern, text)
        return float(m.group(1)) if m else None

    s_starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    s_ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    silences = [{"start": s, "end": s_ends[i] if i < len(s_ends) else None} for i, s in enumerate(s_starts)]
    peaks = [float(x) for x in re.findall(r"Peak level dB: (-?[\d.]+|-inf)", err) if x != "-inf"]
    return {
        "integrated_lufs": grab(r"I:\s+(-?[\d.]+) LUFS", summary),
        "lra_lu": grab(r"LRA:\s+(-?[\d.]+) LU", summary),
        "true_peak_dbtp": grab(r"Peak:\s+(-?[\d.]+) dBFS", summary),
        "sample_peak_dbfs": max(peaks) if peaks else None,
        "silences": silences,
    }


def contact_sheet(path, duration, out, cols, rows, width=1080):
    n = cols * rows
    tile_w = width // cols
    # One frame at the centre of each of n equal slices.
    times = [duration * (i + 0.5) / n for i in range(n)]
    tmp = out.parent / "_sheet"
    tmp.mkdir(exist_ok=True)
    for i, t in enumerate(times):
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
             "-vf", f"scale={tile_w}:-2,drawtext=text='{t:.1f}s':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6",
             str(tmp / f"{i:03d}.png")])
    run(["ffmpeg", "-y", "-v", "error", "-framerate", "1", "-i", str(tmp / "%03d.png"),
         "-vf", f"tile={cols}x{rows}:padding=4:color=0x0A0F16", "-frames:v", "1", "-q:v", "3", str(out)])
    for f in tmp.glob("*.png"):
        f.unlink()
    tmp.rmdir()
    return times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--expect", default=None, help="expected WxH, e.g. 1080x1920")
    ap.add_argument("--fps", type=float, default=None)
    ap.add_argument("--lufs", type=float, default=-14.0, help="integrated loudness target")
    ap.add_argument("--lufs-tol", type=float, default=1.0)
    ap.add_argument("--tp", type=float, default=-1.0, help="max true peak dBTP")
    ap.add_argument("--sheet-cols", type=int, default=5)
    ap.add_argument("--sheet-rows", type=int, default=4)
    a = ap.parse_args()

    video = Path(a.video)
    out = Path(a.out) if a.out else video.parent / f"{video.stem}_qa"
    out.mkdir(parents=True, exist_ok=True)

    info = probe(video)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    duration = float(info["format"]["duration"])
    report = {"file": str(video), "duration_s": round(duration, 3), "checks": {}, "fail": []}

    def check(name, ok, detail):
        report["checks"][name] = {"ok": ok, "detail": detail}
        if ok is False:
            report["fail"].append(name)

    check("video_stream", v is not None, v and f"{v['codec_name']} {v['width']}x{v['height']} {fps_of(v):.3f}fps {v.get('pix_fmt')}")
    check("audio_stream", au is not None, au and f"{au['codec_name']} {au.get('sample_rate')}Hz {au.get('channels')}ch")
    if v and a.expect:
        check("resolution", f"{v['width']}x{v['height']}" == a.expect, f"{v['width']}x{v['height']} (expected {a.expect})")
    if v and a.fps:
        check("frame_rate", abs(fps_of(v) - a.fps) < 0.01, f"{fps_of(v):.3f} (expected {a.fps})")

    if v:
        black, frozen = detect_video_issues(video)
        report["black_intervals"], report["frozen_intervals"] = black, frozen
        check("no_black_frames", not black, f"{len(black)} interval(s)")
        check("no_frozen_frames", not frozen, f"{len(frozen)} interval(s) ≥0.5s")
        report["contact_sheet"] = str(out / "contact_sheet.jpg")
        report["contact_sheet_times"] = [round(t, 2) for t in contact_sheet(video, duration, out / "contact_sheet.jpg", a.sheet_cols, a.sheet_rows)]

    if au:
        audio = detect_audio(video)
        report["audio"] = audio
        lufs, tp = audio["integrated_lufs"], audio["true_peak_dbtp"]
        check("loudness", lufs is not None and abs(lufs - a.lufs) <= a.lufs_tol, f"{lufs} LUFS (target {a.lufs}±{a.lufs_tol})")
        check("true_peak", tp is not None and tp <= a.tp, f"{tp} dBTP (max {a.tp})")
        check("no_clipping", audio["sample_peak_dbfs"] is None or audio["sample_peak_dbfs"] < -0.1, f"sample peak {audio['sample_peak_dbfs']} dBFS")
        # Silences are reported for review, not auto-failed: pauses can be intentional.
        report["checks"]["silences_for_review"] = {"ok": None, "detail": f"{len(audio['silences'])} silence(s) ≥0.7s at -50dB"}

    (out / "qa.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    for k, c in report["checks"].items():
        mark = "PASS" if c["ok"] is True else ("FAIL" if c["ok"] is False else "INFO")
        print(f"[{mark}] {k}: {c['detail']}")
    print(f"report: {out / 'qa.json'}")
    sys.exit(1 if report["fail"] else 0)


if __name__ == "__main__":
    main()
