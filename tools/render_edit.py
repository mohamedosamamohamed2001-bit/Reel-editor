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


def resolve(edit, proj, name):
    media = edit.pop("media", {})
    link_dir = STUDIO / "public" / "media" / name
    link_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
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

    def p(key):
        if key not in paths:
            raise SystemExit(f"unknown media key '{key}' (define it under \"media\")")
        return paths[key]

    for c in edit["clips"]:
        c["src"] = p(c["src"])
    for o in edit.get("overlays", []):
        if "src" in o:
            o["src"] = p(o["src"])
        for side in ("top", "bottom"):
            if side in o:
                o[side]["src"] = p(o[side]["src"])
    cap = edit.get("captions")
    if cap and "wordsFile" in cap:
        data = json.loads((proj / cap.pop("wordsFile")).read_text())
        cap["words"] = [{"w": w["w"], "start": w["start"], "end": w["end"]} for s in data["segments"] for w in s["words"]]
    return edit


def master_audio(src, dst, lufs, tp):
    """Two-pass EBU R128 loudness normalisation; video stream copied untouched."""
    first = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af",
                            f"loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", first, re.S).group(0))
    af = (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-c:v", "copy", "-af", af,
                    "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(dst)], check=True)


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
    renders = proj / "renders"
    renders.mkdir(exist_ok=True)
    props = renders / "_props.json"
    props.write_text(json.dumps({"edit": edit}, ensure_ascii=False))

    suffix = "_preview" if a.preview else ""
    raw = renders / f"{name}{suffix}_raw.mp4"
    cmd = ["npx", "remotion", "render", "src/index.ts", "ReelEdit", str(raw), f"--props={props}",
           f"--concurrency={4}", "--log=error"]
    if a.preview:
        cmd.append("--scale=0.5")
    if a.frames:
        cmd.append(f"--frames={a.frames}")
    print("rendering:", " ".join(cmd[2:5]), flush=True)
    subprocess.run(cmd, cwd=STUDIO, check=True)

    final = renders / f"{name}{suffix}.mp4"
    if a.no_master:
        raw.replace(final)
    else:
        master_audio(raw, final, a.lufs, a.tp)
        raw.unlink()
    print("output:", final, flush=True)

    w, h = (edit["width"] // 2, edit["height"] // 2) if a.preview else (edit["width"], edit["height"])
    qa = subprocess.run([sys.executable, str(ROOT / "tools" / "qa_render.py"), str(final), "--expect", f"{w}x{h}",
                         "--fps", str(edit["fps"]), "--lufs", str(a.lufs), "--tp", str(a.tp)])
    sys.exit(qa.returncode)


if __name__ == "__main__":
    main()
