"""Collaboration video (Coach Osama 2026-11-17): his own finished edit + captions ONLY.

His brief: keep the edit exactly as it is (no change to timing, cuts, pacing, picture, sound), nothing from outside the video, no OSM
logo / branding / outro, no transitions, effects or music; just captions in his usual style (#56A0FB bar, white text).
So: every source frame is kept with its own timestamp (4K 2160x3840 HLG 60 fps, iPhone original), the captions are drawn on top
(sRGB -> HLG at 203-nit graphics white, like the HYROX film), and the stereo AAC sound is copied bit for bit.

Words: English, his exact speech. The track carries a loud 149 Hz hum + fan noise; Whisper large-v3 on a noise-subtracted copy
(transcription only) + per-window passes + the picture (he picks up the bottle, the bottle lands at 12.9 s) give the lines below.
Phrase times = measured voice onsets on the cleaned copy (Whisper's own times ran 0.3-0.4 s early).

    .venv/bin/python projects/2026-11-17_collab_captions/build.py
"""
import json, os, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
SRC = P / "source/IMG_2544.MOV"
TOP = 0.72                                   # his usual caption position (bar top edge, fraction of the height)
# (text, start, end) - 1-3 words per phrase, studio style; ends hold briefly after the voice stops
GROUPS = [
    ("Let's do Bulgarian", 0.00, 0.70),
    ("split squats.", 0.70, 1.85),
    ("Why?", 2.27, 3.05),
    ("If you can", 4.54, 5.05),
    ("do this,", 5.05, 5.85),
    ("you won't", 6.07, 6.50),
    ("have to do", 6.50, 7.05),
    ("Bulgarian", 7.05, 7.45),
    ("split squats.", 7.45, 8.30),
    ("Deal?", 8.64, 9.40),
    ("Sorry,", 13.67, 14.30),
    ("you lost.", 14.30, 15.45),
]
HDR = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
GFX = ("format=rgba,split[c][a];[c]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:"
       "npl=203,format=yuv420p10le[cy];[a]alphaextract,format=gray10le[al];[cy][al]alphamerge")


def frame_times():
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(SRC)],
                         capture_output=True, text=True, check=True).stdout
    return [float(l.strip().strip(",")) for l in out.splitlines() if l.strip().strip(",")]


def main():
    W = P / "work"; W.mkdir(exist_ok=True); (P / "renders").mkdir(exist_ok=True)
    times = frame_times()
    spec = {"top": TOP, "times": times, "groups": [{"text": t, "start": a, "end": b} for t, a, b in GROUPS]}
    (W / "captions_spec.json").write_text(json.dumps(spec))
    ov = W / "cap"
    subprocess.run(["node", str(P / "render_captions.js"), str(W / "captions_spec.json"), str(ov)], check=True)
    # overlay frames carry the source's exact frame durations, so each caption frame lands on its own source frame
    durs = [b - a for a, b in zip(times, times[1:])] + [1 / 60]
    (W / "cap_list.txt").write_text("".join(f"file '{ov}/f_{i:05d}.png'\nduration {d:.6f}\n" for i, d in enumerate(durs)))
    out = P / "renders/collab_captions.mp4"
    g = f"[1:v]{GFX}[ov];[0:v][ov]overlay=format=yuv420p10:eof_action=pass,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[v]"
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(SRC), "-f", "concat", "-safe", "0", "-i", str(W / "cap_list.txt"),
                    "-filter_complex", g, "-map", "[v]", "-map", "0:2", "-fps_mode", "passthrough", "-c:v", "libx265", "-pix_fmt", "yuv420p10le",
                    "-x265-params", "crf=14:preset=medium:pools=4:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error",
                    "-tag:v", "hvc1", *HDR, "-c:a", "copy", "-movflags", "+faststart", str(out)], check=True)
    print("output", out)


if __name__ == "__main__":
    main()
