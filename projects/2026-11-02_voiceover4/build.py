"""+1 kg on the scale in one day is not fat: his voice-over (main.mov audio, untouched) as the spine; the script screenshot is NOT used.
Same voice-over system as 2026-11-01_voiceover/_voiceover4: OSM data/science motion scenes (motion/pieces/scale_science, facts from
PubMed-verified papers), 2 Coverr stock clips (non-AI, non-premium, manifest in source/stock) and his B-roll library
(library/broll, check-in poses = progress photos and online follow-up). Output time = voice-over time. Captions = his spoken words
(large-v3, cross-checked with medium; corrections in FIX / MERGE / INSERT).

    .venv/bin/python projects/2026-11-02_voiceover4/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-02_voiceover4
"""
import json, math, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[0] / "_c5"))
sys.path.insert(0, str(P.parents[0] / "_n6"))
from common import END_DUR, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402
from common2 import END_IMAGE  # noqa: E402

VO_DUR = 54.10
GFX = "format=yuv420p"            # motion graphics / screen recordings are SDR brand pixels: never graded

FIX = {1.22: "كام", 20.72: "بيه", 29.20: "لـ12", 30.34: "الـSets", 33.60: "وارجع", 34.10: "لـ8", 40.20: "ماقالتش", 40.52: "ده",
       41.54: "نوتة"}
MERGE = {43.42: ("OSM App", 43.88), 50.86: ("OSM Coach Osama", [51.40, 51.80]), 52.50: ("Google Play", 52.92), 53.32: ("App Store", 53.56)}
DROP = set()
INSERT = []
UNSURE = {24.22: "حط تحتها كذا خط دي (both models)", 13.46: "لوحده (medium: اللي واحده)", 0.0: "لو (low confidence)"}

SHOTS = [
    (0.00, 1.55, "s_bench", 3.0, dict(zoom=[1.08, 1.0], focusX=0.45)),
    (1.55, 3.65, "m_hook", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (3.65, 5.10, "s_row", 2.0, dict(zoom=[1.0, 1.08], focusX=0.85, tin={"type": "whip", "dir": "left"})),
    (5.10, 7.85, "s_mirror", 2.0, dict(zoom=[1.0, 1.07], focusX=0.5, tin={"type": "whip", "dir": "right"})),
    (7.85, 11.85, "m_same", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (11.85, 14.70, "s_note", 1.0, dict(zoom=[1.05, 1.14], focusX=0.5, tin={"type": "whip", "dir": "left"})),
    (14.70, 16.10, "m_when", 0.0, dict(grade=GFX, tin={"type": "flash"})),
    (16.10, 19.50, "m_range", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (19.50, 21.50, "s_adjust", 3.0, dict(zoom=[1.0, 1.08], focusX=0.5, speed=1.5, tin={"type": "whip", "dir": "right"})),
    (21.50, 24.20, "s_bench", 12.0, dict(zoom=[1.0, 1.07], focusX=0.45, tin={"type": "zoom"})),
    (24.20, 31.95, "m_ladder", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (31.95, 35.40, "m_bump", 0.0, dict(grade=GFX, tin={"type": "flash"})),
    (35.40, 38.00, "m_target", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "left"})),
    (38.00, 40.75, "b_7565", 1.6, dict(zoom=[1.0, 1.05], focusY=0.4, tin={"type": "whip", "dir": "right"})),
    (40.75, 42.30, "s_note", 5.0, dict(zoom=[1.08, 1.15], focusX=0.5, tin={"type": "whip", "dir": "left"})),
    (42.30, 48.00, "bg", 0.0, dict(grade=GFX, freeze=True, tin={"type": "zoom"})),
    (48.00, 50.50, "b_7542", 1.0, dict(zoom=[1.0, 1.07], focusY=0.4, tin={"type": "whip", "dir": "up"})),
    (50.50, VO_DUR, "bg", 0.0, dict(grade=GFX, freeze=True, tin={"type": "whip", "dir": "left"})),
]
ST = "source/stock/coverr-"
MEDIA = {
    "s_bench": ST + "weight-lifting-in-the-gym-7769.mp4", "s_back": ST + "back-training-in-the-gym-9672.mp4",
    "s_mirror": ST + "looking-in-the-mirror-2261.mp4", "s_note": ST + "close-up-of-handwriting-in-notebook.mp4",
    "s_adjust": ST + "adjusting-machine-in-the-gym-3815.mp4", "s_row": ST + "woman-lifting-weights-3487.mp4",
    "b_7565": "source/IMG_7565.MOV", "b_7542": "source/IMG_7542.MOV", "bg": "../_mkt/bg_night.mp4",
    "app_log": "source/screen_0030.mp4", "app_store": "source/screen_0037.mp4",
    **{f"m_{n}": f"work/motion/{n}.mp4" for n in ("hook", "same", "when", "range", "ladder", "bump", "target")},
}
CARD_W, CARD_TOP = 780, 150
CARDS = [  # (output at, src, region (x, y, w, h) as fractions, segments [(in, dur)])
    (42.30, "app_log", (0.0, 0.035, 1.0, 0.66), [(3.8, 2.4), (10.6, 1.6), (20.4, 1.7)]),
    (50.50, "app_store", (0.0, 0.03, 1.0, 0.62), [(5.75, 2.1, 0.45), (7.85, 1.5, 0.36)]),  # skips the results list (another app's price) and the reviews
]


def words():
    d = json.loads((P / "work/tx/main.words.json").read_text())
    ws = [w for s in d["segments"] for w in s["words"]]
    out, skip = [], set()
    for w in ws:
        k = round(w["start"], 2)
        if k in skip or k in DROP:
            if k in DROP and out:
                out[-1]["end"] = w["end"]
            continue
        if k in MERGE:
            word, nxt = MERGE[k]
            nxt = nxt if isinstance(nxt, (list, tuple)) else [nxt]
            skip.update(nxt)
            end = next(x["end"] for x in ws if round(x["start"], 2) == nxt[-1])
            out.append({"w": word, "start": w["start"], "end": end})
            continue
        out.append({"w": FIX.get(k, w["w"].strip()), "start": w["start"], "end": w["end"]})
    for ins in INSERT:
        for o in out:
            if o["start"] < ins["start"] < o["end"]:
                o["end"] = ins["start"]
        out.append(dict(ins))
    return sorted(out, key=lambda o: o["start"])


def main():
    vo = P / "work" / "vo.wav"     # his voice-over, sample-exact, untouched (only resampled for the mixer)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / "source/main.mov"), "-map", "0:a:0", "-ar", "48000", "-ac", "2",
                    "-t", f"{VO_DUR + END_DUR:.3f}", "-af", f"apad=whole_dur={VO_DUR + END_DUR:.3f}", "-c:a", "pcm_s24le", str(vo)], check=True)
    clips = []
    fr = lambda x: math.floor(x * 30 + 0.5) / 30          # every cut on an exact frame (no per-clip rounding drift)
    for a, b, key, sin, kw in SHOTS:
        a, b, sin = fr(a), fr(b), fr(sin)
        sp = kw.get("speed", 1)
        c = {"src": key, "in": round(sin, 4), "out": round(sin + (b - a) * sp, 4)}
        c.update(kw)
        clips.append(c)
    T = sum(round((c["out"] - c["in"]) / c.get("speed", 1) * 30) for c in clips) / 30   # frame-exact clip total (end card on the next frame)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / "source/main.mov"), "-map", "0:a:0", "-ar", "48000", "-ac", "2",
                    "-t", f"{T + END_DUR:.4f}", "-af", f"apad=whole_dur={T + END_DUR:.4f}", "-c:a", "pcm_s24le", str(vo)], check=True)
    ov, zones = [], []
    for at, key, (x, y, w, h), segs in CARDS:
        dur = round(sum(sg[1] for sg in segs), 3)
        ov.append({"type": "screenCard", "at": at, "dur": dur, "src": key, "plate": True, "backdrop": "none", "entrance": "tilt",
                   "width": CARD_W, "top": CARD_TOP, "region": {"x": x, "y": y, "w": w, "h": h}, "srcW": 1320, "srcH": 2868,
                   "segments": [{"in": sg[0], "rate": (sg[2] if len(sg) > 2 else 1), "dur": sg[1]} for sg in segs]})
        bottom = (CARD_TOP + CARD_W * (h * 2868) / (w * 1320)) / 1920
        zones.append({"at": round(at - 0.05, 3), "dur": round(dur + 0.05, 3), "top": round(min(0.79, bottom + 0.012), 3)})
    ov.append(dict(end_card(T), image=END_IMAGE, sub="Source: Plotkin et al. 2022 (PeerJ)"))
    cues = [cue(0.0, "impact", -9), cue(0.02, "boom", -12), cue(0.05, "whoosh_in", -18)]
    for a, b, key, sin, kw in SHOTS[1:]:
        t = kw.get("tin", {}).get("type")
        cues.append(cue(a, {"whip": "whip", "flash": "click"}.get(t, "whoosh_in"), {"whip": -15, "flash": -10}.get(t, -16)))
    H = 1.55
    cues += [cue(H + 0.15 + i * 0.11, "key", -24) for i in range(8)] + [cue(H + 0.75, "thump", -15), cue(H + 1.25, "impact", -11)]  # months flip / ?? KG / هتعرف
    Sm = 7.85
    cues += [cue(Sm + 0.1 + i * 0.25, "click", -26) for i in range(13)] + [cue(Sm + x, "thump", -14) for x in (1.0, 2.35, 3.2)]  # week counter / نفس ×3
    cues += [cue(14.7 + 0.35, "impact", -11)]                                                                          # إمتى تزوّد؟ +
    R = 16.1
    cues += [cue(R + 0.4, "accent", -17), cue(R + 0.9, "accent", -17), cue(R + 0.5, "swell", -21)]                      # 8 / 12 / bar
    L = 24.2
    cues += [cue(L + 0.5, "whoosh_in", -21)] + [cue(L + x, "blip", -19) for x in (1.15, 2.0, 2.8, 3.6, 4.4)] + [cue(L + 4.8, "chime", -17), cue(L + 5.3, "accent", -16)]
    B = 31.95
    cues += [cue(B + 0.35, "impact", -10), cue(B + 0.8, "thump", -13), cue(B + 1.5, "whoosh_out", -20), cue(B + 2.0, "accent", -17)]
    cues += [cue(35.4 + 0.25, "swell", -21), cue(35.4 + 1.6, "chime", -18)]
    cues += [cue(42.3 + x, "click", -19) for x in (0.6, 2.6, 4.2)] + [cue(50.5 + 1.0, "key", -20), cue(50.5 + 2.5, "chime", -18)]
    cues += end_card_sfx(T)
    wf = P / "work" / "vo.words.json"
    wf.write_text(json.dumps({"segments": [{"words": words()}]}, ensure_ascii=False))
    mus = make_music(P, {"bpm": 120, "key": "A", "mode": "minor", "style": "trap", "seed": 41, "duration": round(T + END_DUR, 3),
                         "sections": [{"type": "intro", "until": 3.65}, {"type": "groove", "until": 14.7}, {"type": "build", "until": 16.1, "stop": True},
                                      {"type": "drop", "until": round(T, 3)}, {"type": "outro", "until": round(T + END_DUR, 3)}]}, gain_db=-11)
    edit = {"title": "Log your lifts: double progression (research reel)", "fps": 30, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": ov,
            "shakes": [], "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
            "voiceTrack": "work/vo.wav", "dialogueLufs": -16.0,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "plateColor": "#56A0FB", "keywordColor": "#FFFFFF",
                         "keywords": ["هتعرف؟", "زي", "إمتى", "12", "عدة", "الوزن", "واضح", "بتتقدم", "OSM App", "OSM Coach Osama"],
                         "zones": zones + [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.74}]}}
    write_edit(P, edit)
    tot = sum((c["out"] - c["in"]) / c.get("speed", 1) for c in clips)
    print(f"clips cover {tot:.3f}s (VO {VO_DUR}s); unsure words: {UNSURE}")


if __name__ == "__main__":
    main()
