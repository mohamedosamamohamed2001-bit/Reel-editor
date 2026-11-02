"""Recreation of a reference Reel (source/reference.mp4, a screen recording of an Instagram "Made with Edits" reel) with HIS footage.

Kept from the reference, frame-exact: cut points (measured by frame difference), the 2-frame black dip, shot lengths, slow push-ins,
the speed-ramped cut, high-contrast black & white look, short caption phrases timed to the voice.
OSM brand: captions on the #56A0FB bar, white Inter (English), no other creator's branding.
Audio: the reference voice-over belongs to another creator. It is used here ONLY as the sync guide for the internal render;
the delivered file is video-only and the original audio is added in Instagram ("Use audio", start 0:00), which keeps it
licensed and credited.

    .venv/bin/python projects/2026-11-02_recreate/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-02_recreate
"""
import json, math, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[0] / "_c5"))
from common import write_edit  # noqa: E402

FPS = 30
fr = lambda x: math.floor(x * FPS + 0.5) / FPS
HLG = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
       "tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=gbrp16le")
# reference look: monochrome, deep blacks, soft highlight roll-off, a touch of contrast (no colour cast: pure luma)
BW = HLG + ",hue=s=0,curves=master='0/0 0.12/0.02 0.40/0.24 0.70/0.58 0.90/0.80 1/0.90':interp=pchip,vignette=angle=PI/4.5,format=yuv420p"
# caption phrases exactly where the reference changes its on-screen text (start times from the reference)
PHRASES = [0.00, 1.02, 1.56, 2.62, 3.32, 3.88, 4.24, 4.68, 5.18, 5.96, 6.38, 6.88, 7.48, 8.88, 9.60, 10.08, 10.56, 10.88, 11.52,
           12.08, 12.46, 12.80, 13.56, 14.14]

# (start, end, media, source in, kwargs). Reference cuts: 3.55 / 5.45 / 7.58 black 7.65 / 10.15 (ramp) / 11.25 / 12.75 / 15.75 / end 16.30
SHOTS = [
    (0.000, 3.550, "walk", 0.70, dict(zoom=[1.00, 1.10], focusX=0.5, focusY=0.42)),        # walking toward camera: "There is a relationship between"
    (3.550, 5.450, "mirror", 1.55, dict(zoom=[1.04, 1.10], focusX=0.5, focusY=0.38)),      # close, eyes to camera: "discipline, motivation and obsession, right"
    (5.450, 7.570, "row", 3.00, dict(zoom=[1.02, 1.09], focusX=0.5, focusY=0.45)),         # rowing effort: "So discipline is I will make myself do the thing"
    (7.570, 7.633, "black", 0.00, dict()),                                                 # 2-frame dip to black (as in the reference)
    (7.633, 10.150, "box", 11.55, dict(zoom=[1.06, 1.00], focusX=0.5, focusY=0.5, speed=0.5)),  # box jump, 120 fps slow motion
    (10.150, 11.250, "box", 7.90, dict(zoom=[1.10, 1.02], focusX=0.5, focusY=0.48, speed=1.6)),  # speed-ramped cut: "I want to do the thing"
    (11.250, 12.750, "box", 4.30, dict(zoom=[1.00, 1.06], focusX=0.5, focusY=0.5)),        # step-up from the front: "and obsession"
    (12.750, 15.750, "row", 12.00, dict(zoom=[1.00, 1.12], focusX=0.5, focusY=0.42)),      # rowing, slow push: "is I can't not do the thing"
    (15.750, 16.300, "mirror", 2.65, dict(zoom=[1.12, 1.16], focusX=0.5, focusY=0.3)),     # face close-up to end (loops to the start)
]
MEDIA = {"walk": "source/IMG_2254.mov", "mirror": "source/IMG_2258.MOV", "row": "source/IMG_2256.MOV", "box": "source/IMG_2257.MOV",
         "black": "work/black.mp4"}


def main():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30:d=1", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", str(P / "work/black.mp4")], check=True)
    # sync guide (internal only): the reference audio, padded
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / "source/reference.mp4"), "-vn", "-ac", "2", "-ar", "48000",
                    "-af", "apad=whole_dur=16.3", "-t", "16.3", "-c:a", "pcm_s24le", str(P / "work/ref_audio.wav")], check=True)
    clips = []
    for a, b, key, sin, kw in SHOTS:
        a, b, sin = fr(a), fr(b), fr(sin)
        sp = kw.get("speed", 1)
        c = {"src": key, "in": round(sin, 4), "out": round(sin + (b - a) * sp, 4), **kw}
        if key != "black":
            c["grade"] = BW
        else:
            c["grade"] = "format=yuv420p"
        clips.append(c)
    d = json.loads((P / "work/tx/reference.words.json").read_text())
    ws = [{"w": w["w"].strip(), "start": w["start"], "end": w["end"]} for s in d["segments"] for w in s["words"]]
    fix = {"Discipline": "discipline,", "motivation": "motivation", "right": "right.", "so": "So", "thing": "thing.", "Obsession": "obsession"}
    for w in ws:
        w["w"] = fix.get(w["w"], w["w"])
    ws[-1]["end"] = min(ws[-1]["end"], 16.25)
    (P / "work/ref.words.json").write_text(json.dumps({"segments": [{"words": ws}]}))
    T = sum(round((c["out"] - c["in"]) / c.get("speed", 1) * FPS) for c in clips) / FPS
    edges = [max(0.0, p - 0.03) for p in PHRASES] + [round(T + 0.01, 3)]
    zones = [{"at": round(a, 3), "dur": round(b - a, 3), "top": 0.6} for a, b in zip(edges, edges[1:])]
    edit = {"title": "Discipline / Motivation / Obsession (reference recreation)", "fps": FPS, "width": 1080, "height": 1920,
            "media": MEDIA, "plates": {"grade": "auto", "sharpen": "cas=strength=0.3"}, "clips": clips, "overlays": [],
            "shakes": [], "sfx": {"cues": []}, "tail": 0, "voiceTrack": "work/ref_audio.wav", "dialogueLufs": -14.0,
            "captions": {"wordsFile": "work/ref.words.json", "outputTime": True, "style": "plate", "karaoke": False,
                         "maxWords": 3, "maxChars": 18, "plateColor": "#56A0FB", "keywordColor": "#FFFFFF", "keywords": [],
                         "zones": zones}}
    write_edit(P, edit)
    print(f"clips {T:.3f}s")


if __name__ == "__main__":
    main()
