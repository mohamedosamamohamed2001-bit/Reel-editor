"""Export the collection: name the finals, verify them, and make send-size copies.

    python3 projects/_c5/export.py

For each video: renders/<project>.mp4 -> exports/OSM_<n>_<slug>.mp4 (+ _no-music). The file is trimmed (stream copy,
lossless) to the composition's exact frame count if the render has trailing frames. Every export is fully decoded
(ffmpeg -f null) and probed. Files over 29 MB also get a _send.mp4 copy (2-pass x264 to ~28 MB, audio copied) because
the chat file transfer is limited to 30 MB; the masters in exports/ stay at full quality.
"""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import sys
BATCHES = {
    "c5": ("2026-10-13_c5-", 0, [("comeback", "back-to-training"), ("stretch", "stretch-right"), ("whey", "whey-protein"),
                                 ("crossfit", "crossfit-or-gym"), ("legday", "leg-day")]),
    "n6": ("2026-10-14_", 5, [("n1-0112", "creatine"), ("n2-training", "copying-workouts"), ("n3-scale", "scale-progress"),
                              ("n4-pulldown", "seated-row-wide-vs-close"), ("n5-lumbar", "glutes-lower-back"),
                              ("n6-triceps", "triceps-cable")]),
}
BATCH = sys.argv[1] if len(sys.argv) > 1 else "c5"
PREFIX, NUM0, ORDER = BATCHES[BATCH]
LIMIT = 29 * 1024 * 1024


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                        "stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,sample_rate:format=duration,size",
                        "-of", "json", str(p)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def decode_ok(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "null", "-"], capture_output=True, text=True)
    return r.returncode == 0 and not r.stderr.strip()


def send_copy(src, dst, target_mb=28.0):
    info = probe(src)
    dur = float(info["format"]["duration"])
    abr = 256_000
    vbr = int(target_mb * 8 * 1024 * 1024 / dur - abr)
    log = dst.with_suffix("")
    common = ["-c:v", "libx264", "-preset", "slow", "-b:v", str(vbr), "-pix_fmt", "yuv420p",
              "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-passlogfile", str(log)]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), *common, "-pass", "1", "-an", "-f", "mp4", "/dev/null"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), *common, "-pass", "2", "-c:a", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)
    for f in log.parent.glob(log.name + "*.log*"):
        f.unlink()


def main():
    report = []
    for n, (slug, name) in enumerate(ORDER, 1):
        proj = ROOT / "projects" / f"{PREFIX}{slug}"
        edit = json.loads((proj / "edit.json").read_text())
        out = proj / "exports"
        out.mkdir(exist_ok=True)
        n += NUM0
        pairs = [(proj / "renders" / f"{PREFIX}{slug}.mp4", out / f"OSM_{n:02d}_{name}.mp4")]
        nm = proj / "renders" / f"{PREFIX}{slug}_nomusic.mp4"
        if nm.exists():
            pairs.append((nm, out / f"OSM_{n:02d}_{name}_no-music.mp4"))
        # expected frames: clips (frame-exact) + tail
        fps = edit["fps"]
        frames = 0
        for c in edit["clips"]:
            sp = c.get("speed", 1)
            frames += (round(c["out"] * fps) - round(c["in"] * fps)) if (sp == 1 or c.get("freeze")) else round((c["out"] - c["in"]) / sp * fps)
        ov_end = max([round((o["at"] + o["dur"]) * fps) for o in edit["overlays"]] + [0])
        expect = max(frames + round(edit.get("tail", 0) * fps), ov_end)
        for src, dst in pairs:
            got = int(probe(src)["streams"][0]["nb_read_frames"])
            if got > expect:  # trailing frames past the end card (pre-fix renders): lossless trim
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0", "-c", "copy",
                                "-t", f"{expect / fps:.4f}", "-movflags", "+faststart", str(dst)], check=True)
            else:
                shutil.copy2(src, dst)
            info = probe(dst)
            v = next(s for s in info["streams"] if s["codec_type"] == "video")
            a = next(s for s in info["streams"] if s["codec_type"] == "audio")
            size = int(info["format"]["size"])
            row = {"file": str(dst.relative_to(ROOT)), "frames": int(v["nb_read_frames"]), "expected_frames": expect,
                   "trimmed": got > expect, "video": f"{v['codec_name']} {v['width']}x{v['height']} {v['r_frame_rate']}",
                   "audio": f"{a['codec_name']} {a['sample_rate']} Hz", "duration": round(float(info["format"]["duration"]), 3),
                   "size_mb": round(size / 1048576, 1), "decodes": decode_ok(dst)}
            if size > LIMIT:
                send = dst.with_name(dst.stem + "_send.mp4")
                send_copy(dst, send)
                row["send_copy"] = str(send.relative_to(ROOT))
                row["send_mb"] = round(send.stat().st_size / 1048576, 1)
            report.append(row)
            print(json.dumps(row, ensure_ascii=False))
    (ROOT / "projects" / ("_c5" if BATCH == "c5" else "_n6") / "export_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
