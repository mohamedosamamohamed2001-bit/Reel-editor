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

Optional "plates" (recommended for footage): {"grade": "<ffmpeg filters>", "sharpen": "cas=strength=0.4"}.
Each clip is then pre-framed by FFmpeg (crop at its zoom/focus -> grade -> Lanczos scale to the frame size ->
sharpen) into projects/<name>/work/plates/, so Remotion shows footage 1:1 instead of resampling 4K in the
browser (measured 2x softer). screenCard overlays with "plate": true are Lanczos-scaled to the card width.

Outputs (git-ignored): projects/<name>/renders/<name>[_preview].mp4 plus a _qa folder.
"""
import hashlib
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


def _even(x):
    return max(2, int(round(x / 2)) * 2)


def _plate(src, dst_dir, vf, extra_in, extra_out, fps):
    """Write one plate as a JPEG image sequence (cached by a hash of source + filters + trim + fps).

    Image frames, not video: Remotion's <OffthreadVideo> frame extraction softened footage ~7x
    (face Laplacian variance 311 -> 44 on the same frame) while <Img> keeps it (JPEG q1 4:4:4).
    """
    key = hashlib.sha1(json.dumps([str(src), os.path.getmtime(src), vf, extra_in, extra_out, fps, "jpg-q1-444"]).encode()).hexdigest()[:12]
    dst = dst_dir / f"{Path(src).stem}_{key}"
    done = dst / ".done"
    if not done.exists():
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", *extra_in, "-i", str(src), *extra_out, "-an",
                        "-vf", f"{vf},fps={fps},format=yuvj444p", "-q:v", "1", "-qmin", "1",
                        str(dst / "%05d.jpg")], check=True)
        done.write_text("ok")
    return dst


def _count(d):
    return len(list(Path(d).glob("*.jpg")))


def make_plates(edit, proj):
    """Pre-frame every clip (and opted-in screen cards) with FFmpeg into image sequences. Mutates edit."""
    cfg = edit.get("plates")
    if not cfg:
        return
    W, H = edit["width"], edit["height"]
    media = edit["media"]
    out_dir = proj / "work" / "plates"
    grade = cfg.get("grade")
    sharpen = cfg.get("sharpen")
    scale = f"scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int"
    for i, c in enumerate(edit["clips"]):
        src = (proj / media[c["src"]]).resolve()
        sw, sh = dims(src)
        z = c.get("zoom", 1)
        z0, z1 = (z if isinstance(z, list) else (z, z))
        # same framing maths as studio/src/components/FramedVideo.tsx, evaluated at the clip's first zoom
        s = max(W / sw, H / sh) * z0
        cw, ch = _even(W / s), _even(H / s)
        x = min(max(c.get("focusX", 0.5) * sw - cw / 2, 0), sw - cw)
        y = min(max(c.get("focusY", 0.5) * sh - ch / 2, 0), sh - ch)
        vf = ",".join(f for f in [f"crop={cw}:{ch}:{_even(x)}:{_even(y)}", grade, scale, sharpen] if f)
        # frame-exact trim: start ON the frame the timeline shows at `in` (floor), not the next one
        # (a plain -ss picks the first frame AFTER `in`: measured 1 frame late after the cut), and take
        # exactly as many frames as the clip lasts on the timeline
        fps = edit["fps"]
        first = int(c["in"] * fps + 1e-6)
        n = round((c["out"] - c["in"]) * fps) + 1
        plate = _plate(src, out_dir, vf, ["-ss", f"{(first - 0.25) / fps:.5f}" if first else "0"], ["-frames:v", str(n)], fps)
        key = f"plate{i}"
        media[key] = str(plate.relative_to(proj))
        c.update({"orig": {"in": c["in"], "out": c["out"]},
                  "src": key, "in": 0, "out": round(c["out"] - c["in"], 3), "focusX": 0.5, "focusY": 0.5,
                  "zoom": [1, round(z1 / z0, 4)] if z1 != z0 else 1})
    for j, o in enumerate(edit.get("overlays", [])):
        if o.get("type") == "screenCard" and o.get("plate"):
            src = (proj / media[o["src"]]).resolve()
            width = o.get("width", 920)
            plate = _plate(src, out_dir, f"scale={_even(width / o.get('region', {}).get('w', 1))}:-2:"
                                         "flags=lanczos+accurate_rnd+full_chroma_int", [], [], 60)
            media[f"screenplate{j}"] = str(plate.relative_to(proj))
            o["src"] = f"screenplate{j}"


def resolve(edit, proj, name):
    media = edit.pop("media", {})
    edit.pop("plates", None)
    link_dir = STUDIO / "public" / "media" / name
    link_dir.mkdir(parents=True, exist_ok=True)
    paths, sizes, seqs = {}, {}, {}
    if link_dir.exists():
        shutil.rmtree(link_dir)  # stale plates from earlier renders
    link_dir.mkdir(parents=True)
    for key, rel in media.items():
        src = (proj / rel).resolve()
        if not src.exists():
            raise SystemExit(f"media '{key}' not found: {src}")
        if src.is_dir():  # image-sequence plate
            link = link_dir / key
            if link.exists():
                shutil.rmtree(link)
            link.mkdir()
            for f in sorted(src.glob("*.jpg")):
                try:
                    os.link(f, link / f.name)
                except OSError:
                    shutil.copy2(f, link / f.name)
            first = sorted(src.glob("*.jpg"))[0]
            paths[key] = f"media/{name}/{key}"
            sizes[key] = dims(first)
            seqs[key] = _count(src)
            continue
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
        if c["src"] in seqs:
            c["frames"] = {"count": seqs[c["src"]], "fps": edit["fps"]}
        c["src"] = p(c["src"])
    for o in edit.get("overlays", []):
        if "src" in o:
            o["srcW"], o["srcH"] = sizes.get(o["src"], (None, None))
            if o["src"] in seqs:
                o["frames"] = {"count": seqs[o["src"]], "fps": 60}
            o["src"] = p(o["src"])
        if o.get("type") == "split":
            for side in ("top", "bottom"):
                o[side]["src"] = p(o[side]["src"])
    cap = edit.get("captions")
    if cap and "wordsFile" in cap:
        data = json.loads((proj / cap.pop("wordsFile")).read_text())
        rep = cap.pop("replace", {})
        seqs = cap.pop("replaceSeq", [])  # [{"from": ["الويب", "سايت"], "to": "Website"}]: merges consecutive words
        words = [{"w": w["w"], "start": w["start"], "end": w["end"]} for s in data["segments"] for w in s["words"]]
        for sq in sorted(seqs, key=lambda q: -len(q["from"])):  # longest first
            n, out, i, hits = len(sq["from"]), [], 0, 0
            while i < len(words):
                if [w["w"] for w in words[i:i + n]] == sq["from"]:
                    out.append({"w": sq["to"], "start": words[i]["start"], "end": words[i + n - 1]["end"]})
                    i += n
                    hits += 1
                else:
                    out.append(words[i])
                    i += 1
            if not hits:
                raise SystemExit(f"captions.replaceSeq not found in transcript: {sq['from']}")
            words = out
        # replaceAt: fix ONE occurrence, found by its transcript start time (±0.06 s): new text and/or a corrected
        # start measured from the audio (transcript word edges can be off by 0.3–0.6 s around pauses)
        for fix in cap.pop("replaceAt", []):
            hit = [w for w in words if abs(w["start"] - fix["at"]) <= 0.06]
            if len(hit) != 1:
                raise SystemExit(f"captions.replaceAt matched {len(hit)} words at {fix['at']}s (need exactly 1)")
            if "to" in fix:
                hit[0]["w"] = fix["to"]
                hit[0]["fixed"] = True
            if "start" in fix:
                hit[0]["start"] = fix["start"]
        cap["words"] = [{"w": w["w"] if w.pop("fixed", False) else rep.get(w["w"], w["w"]), "start": w["start"], "end": w["end"]}
                        for w in words]
        hits = {k: sum(w["w"] == k for s in data["segments"] for w in s["words"]) for k in rep}
        missing = [k for k, n in hits.items() if n == 0]
        if missing:
            raise SystemExit(f"captions.replace keys not found in transcript: {missing}")
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


def build_mix(dialogue, cues, total, fps, dst):
    """Dialogue + synthesised SFX bus (tools/sfx.py). The voice always wins:
    SFX bus is high-passed at 40 Hz, dipped -4 dB around 2.5 kHz (speech presence), and sidechain-ducked
    by the dialogue before the two are summed. Returns the cue placements (frame-snapped times)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import sfx as sfxkit
    bus, placed = sfxkit.render_cues(cues, total, fps)
    sfx_wav = Path(dst).with_suffix(".sfx.wav")
    sfxkit.write_wav(sfx_wav, bus)
    graph = ("[1:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=40,"
             "equalizer=f=2500:t=q:w=1.2:g=-4[s];"
             "[0:a]asplit=2[d][dk];"
             "[s][dk]sidechaincompress=threshold=0.03:ratio=2:attack=10:release=180[sd];"
             "[d][sd]amix=inputs=2:normalize=0:duration=first[out]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(dialogue), "-i", str(sfx_wav), "-filter_complex", graph,
                    "-map", "[out]", "-c:a", "pcm_s24le", str(dst)], check=True)
    sfx_wav.unlink()
    return placed


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
                        # 4x oversampling around the limiter = true-peak limiting (a 48 kHz sample-peak limiter let
                        # inter-sample overs through: -0.3 dBTP on the second video, which needed +8.9 dB of gain)
                        f"aresample=192000,volume={gain:.2f}dB,alimiter=limit={limit:.4f}:level=false:attack=2:release=60,"
                        "aresample=48000",
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
    edit = json.loads((proj / "edit.json").read_text())
    # dialogue always comes from the ORIGINAL sources and cut points, before any plate rewriting
    audio_clips = [{"path": str((proj / edit["media"][c["src"]]).resolve()), "in": c["in"], "out": c["out"],
                    "volume": c.get("volume", 1)} for c in edit["clips"]]
    make_plates(edit, proj)
    edit_sfx = edit.pop("sfx", None)
    edit = resolve(edit, proj, name)
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
    cues = (edit_sfx or {}).get("cues", [])
    if cues:
        mixed = renders / f"{name}{suffix}_mix.wav"
        placed = build_mix(dialogue, cues, total, edit["fps"], mixed)
        print(f"sfx: {len(placed)} cues placed on frame times", flush=True)
        (renders / "_sfx_placed.json").write_text(json.dumps(placed))
        dialogue.unlink()
        dialogue = mixed
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
