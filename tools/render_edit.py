#!/usr/bin/env python3
"""Render a project's edit.json with the OSM Remotion studio, master the audio, and run QA.

Usage:
    python3 tools/render_edit.py projects/<name> [--preview] [--frames A-B] [--no-master] [--lufs -14] [--tp -1]

projects/<name>/edit.json uses media KEYS instead of paths:
    "media":    {"main": "source/talk.mp4", "broll1": "source/set.mp4"}   (relative to the project folder)
    "clips":    [{"src": "main", "in": 0.4, "out": 12.8}, ...]
    "captions": {"wordsFile": "work/talk.words.json", "keywords": ["خطة"]}
    "overlays": [{"type": "insetCard", "src": "broll1", "in": 3, "at": 5, "dur": 4}, ...]
Media files are hard-linked (or copied) into studio/public/media/<name>/ (git-ignored); sources are never modified.

Outputs (git-ignored): projects/<name>/renders/<name>[_preview].mp4 plus a _qa folder.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "studio"


def dims(path):
    """Display width/height of the first video stream (rotation-aware)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data=rotation", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    st = json.loads(r.stdout)["streams"][0]
    w, h = st["width"], st["height"]
    rot = next((abs(int(sd.get("rotation", 0))) for sd in st.get("side_data_list", [])), 0)
    return (h, w) if rot in (90, 270) else (w, h)


def resolve(edit, proj, name):
    media = edit.pop("media", {})
    edit["_audio_clips"] = [{"path": str((proj / media[c["src"]]).resolve()), "in": c["in"], "out": c["out"],
                             "volume": c.get("volume", 1)} for c in edit["clips"]]
    link_dir = STUDIO / "public" / "media" / name
    link_dir.mkdir(parents=True, exist_ok=True)
    paths, sizes = {}, {}
    for key, rel in media.items():
        src = (proj / rel).resolve()
        if not src.exists():
            raise SystemExit(f"media '{key}' not found: {src}")
        link = link_dir / f"{key}{src.suffix.lower()}"
        if link.is_symlink() or link.exists():
            link.unlink()
        # Remotion copies public/ when bundling and does not follow file symlinks:
        # hard-link (no extra disk, source untouched), or copy across filesystems.
        try:
            os.link(src, link)
        except OSError:
            shutil.copy2(src, link)
        paths[key] = f"media/{name}/{link.name}"
        sizes[key] = dims(src)

    def p(key):
        if key not in paths:
            raise SystemExit(f"unknown media key '{key}' (define it under \"media\")")
        return paths[key]

    for c in edit["clips"]:
        c["srcW"], c["srcH"] = sizes.get(c["src"], (None, None))
        c["src"] = p(c["src"])
    for o in edit.get("overlays", []):
        if "src" in o:
            o["srcW"], o["srcH"] = sizes.get(o["src"], (None, None))
            o["src"] = p(o["src"])
        if o.get("type") == "split":
            for side in ("top", "bottom"):
                o[side]["src"] = p(o[side]["src"])
    cap = edit.get("captions")
    if cap and "wordsFile" in cap:
        data = json.loads((proj / cap.pop("wordsFile")).read_text())
        cap["words"] = [{"w": w["w"], "start": w["start"], "end": w["end"]} for s in data["segments"] for w in s["words"]]
    return edit


def build_dialogue(clips, total, dst):
    """Cut the dialogue straight from the sources with FFmpeg (sample-accurate, honours the AAC edit list).

    Remotion's audio path ignores the source's AAC priming edit list, which put the dialogue ~42 ms behind the
    picture on the first real edit (measured by cross-correlation). Video is rendered muted; this is the audio.
    Each clip gets 8 ms fades so cuts don't click.
    """
    # Clips that only change framing (same source, out == next in) are one continuous take: merge them,
    # otherwise the per-clip fades dip the audio mid-word at every punch-in.
    merged = []
    for c in clips:
        m = merged[-1] if merged else None
        if m and m["path"] == c["path"] and abs(m["out"] - c["in"]) < 1e-6 and m["volume"] == c["volume"]:
            m["out"] = c["out"]
        else:
            merged.append(dict(c))
    clips = merged
    inputs, parts = [], []
    paths = sorted({c["path"] for c in clips})
    for p in paths:
        inputs += ["-i", p]
    for i, c in enumerate(clips):
        d = c["out"] - c["in"]
        parts.append(f"[{paths.index(c['path'])}:a:0]atrim=start={c['in']}:end={c['out']},asetpts=PTS-STARTPTS,"
                     f"aresample=48000,aformat=channel_layouts=stereo,volume={c['volume']},"
                     f"afade=t=in:d=0.008,afade=t=out:st={max(0, d - 0.008):.3f}:d=0.008[a{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[a{i}]" for i in range(len(clips))) + \
        f"concat=n={len(clips)}:v=0:a=1,apad=whole_dur={total:.3f}[out]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-c:a", "pcm_s24le", str(dst)], check=True)


def measure(path):
    """Integrated loudness (LUFS) and true peak (dBTP) of the first audio stream, via ebur128."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a:0",
                          "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summ = err[err.rfind("Summary:"):]
    return (float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1)),
            float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1)))


def master_audio(src, dst, lufs, tp, video=None):
    """Gain to the loudness target + peak limiter, measured and corrected (max 3 rounds); video copied.

    Two-pass loudnorm in linear mode refuses gain it can't fit under the true-peak ceiling (first real
    edit: -15.2 LUFS). Here the gain is applied directly, a limiter 1 dB under the ceiling (alimiter is
    sample-peak, so the margin covers inter-sample peaks) holds the peaks, and the result is re-measured.
    """
    limit = 10 ** ((tp - 1.0) / 20)
    i0, _ = measure(src)  # src: any file with the dialogue as its first audio stream
    gain = lufs - i0
    tmp = Path(dst).with_suffix(".master.wav")  # stay uncompressed until the final mux (AAC delay handled once)
    for _ in range(3):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vn", "-af",
                        f"volume={gain:.2f}dB,alimiter=limit={limit:.4f}:level=false:attack=5:release=50",
                        "-ar", "48000", "-c:a", "pcm_s24le", str(tmp)], check=True)
        i, peak = measure(tmp)
        if abs(i - lufs) <= 0.3 and peak <= tp:
            break
        gain += lufs - i
    print(f"audio master: {i0:.1f} -> {i:.1f} LUFS, true peak {peak:.1f} dBTP (gain {gain:+.1f} dB)", flush=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video or src), "-i", str(tmp), "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(dst)], check=True)
    tmp.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--preview", action="store_true", help="half resolution, faster")
    ap.add_argument("--frames", default=None, help="frame range, e.g. 0-150")
    ap.add_argument("--no-master", action="store_true")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    a = ap.parse_args()

    proj = Path(a.project).resolve()
    name = proj.name
    edit = resolve(json.loads((proj / "edit.json").read_text()), proj, name)
    audio_clips = edit.pop("_audio_clips")
    renders = proj / "renders"
    renders.mkdir(exist_ok=True)
    props = renders / "_props.json"
    props.write_text(json.dumps({"edit": edit}, ensure_ascii=False))

    suffix = "_preview" if a.preview else ""
    raw = renders / f"{name}{suffix}_raw.mp4"
    cmd = ["npx", "remotion", "render", "src/index.ts", "ReelEdit", str(raw), f"--props={props}",
           f"--concurrency={4}", "--log=error", "--muted"]
    if a.preview:
        cmd.append("--scale=0.5")
    if a.frames:
        cmd.append(f"--frames={a.frames}")
    print("rendering:", " ".join(cmd[2:5]), flush=True)
    subprocess.run(cmd, cwd=STUDIO, check=True)

    final = renders / f"{name}{suffix}.mp4"
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(raw)], capture_output=True, text=True, check=True).stdout)
    if a.frames:
        print("note: --frames renders a range; dialogue is built for the full cut list", flush=True)
    dialogue = renders / f"{name}{suffix}_dialogue.wav"
    build_dialogue(audio_clips, total, dialogue)
    if a.no_master:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-i", str(dialogue), "-map", "0:v:0", "-map", "1:a:0",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(final)], check=True)
    else:
        master_audio(dialogue, final, a.lufs, a.tp, video=raw)
    raw.unlink()
    dialogue.unlink()
    print("output:", final, flush=True)

    w, h = (edit["width"] // 2, edit["height"] // 2) if a.preview else (edit["width"], edit["height"])
    qa = subprocess.run([sys.executable, str(ROOT / "tools" / "qa_render.py"), str(final), "--expect", f"{w}x{h}",
                         "--fps", str(edit["fps"]), "--lufs", str(a.lufs), "--tp", str(a.tp)])
    sys.exit(qa.returncode)


if __name__ == "__main__":
    main()
