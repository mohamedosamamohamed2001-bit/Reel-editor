"""One feast meal doesn't ruin your diet: his voice-over (main.mov audio, untouched) as the spine; the script screenshot is NOT used.
Same voice-over system: OSM motion scenes (motion/pieces/feast_science; Palascha 2015 + Shukla 2018 from PubMed), Coverr stock
(non-AI, non-premium), his B-roll library (IMG_8385 "be smart", IMG_7542 friendly ending). Captions = his words (large-v3 + medium).

    .venv/bin/python projects/2026-11-02_voiceover5/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-02_voiceover5
"""
import json, math, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[0] / "_c5"))
sys.path.insert(0, str(P.parents[0] / "_n6"))
from common import END_DUR, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402
from common2 import END_IMAGE  # noqa: E402

VO_DUR = 37.20
GFX = "format=yuv420p"

FIX = {2.08: "أصلًا", 4.32: "لأ", 4.78: "شبعت", 5.68: "بيتملي", 9.26: "هتبوّظ", 10.72: "بيبوّظه", 11.24: "إنك", 13.70: "باظ",
       15.26: "الأسبوع", 16.42: "ذكي", 18.26: "هتبوّظلك", 19.82: "أسبوع", 26.76: "بكمية", 30.90: "تعويض", 31.76: "أي",
       33.54: "ابعت", 34.36: "للي", 34.78: "عزومة", 35.58: "قوله"}
MERGE = {}
DROP = set()
INSERT = []
UNSURE = {13.70: "باظ (large-v3: بوز; medium: بووز)", 35.58: "قوله على الهادي (last words, low clarity)", 33.54: "ابعت (large-v3: بعد)"}

SHOTS = [
    (0.00, 1.12, "s_appet", 1.0, dict(zoom=[1.08, 1.0], focusX=0.55)),
    (1.12, 3.50, "m_plates", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (3.50, 5.10, "s_friends", 5.5, dict(zoom=[1.0, 1.07], focusX=0.42, tin={"type": "whip", "dir": "left"})),
    (5.10, 6.70, "s_turkey", 13.0, dict(zoom=[1.04, 1.12], focusX=0.55, tin={"type": "whip", "dir": "right"})),
    (6.70, 8.55, "s_dinner", 1.0, dict(zoom=[1.0, 1.1], focusX=0.5, tin={"type": "zoom"})),
    (8.55, 15.75, "m_week", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (15.75, 17.95, "b_8385", 0.4, dict(zoom=[1.0, 1.06], focusY=0.35, tin={"type": "flash"})),
    (17.95, 20.20, "m_meals", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "left"})),
    (20.20, 21.65, "s_dinner", 5.0, dict(zoom=[1.0, 1.08], focusX=0.45, tin={"type": "whip", "dir": "right"})),
    (21.65, 22.95, "s_chicken", 7.0, dict(zoom=[1.02, 1.1], focusX=0.5, tin={"type": "whip", "dir": "up"})),
    (22.95, 23.65, "s_steak", 6.0, dict(zoom=[1.05, 1.12], focusX=0.5, tin={"type": "zoom"})),
    (23.65, 24.75, "s_salad", 3.0, dict(zoom=[1.0, 1.08], focusX=0.5, tin={"type": "whip", "dir": "left"})),
    (24.75, 26.30, "s_sweets", 5.0, dict(zoom=[1.0, 1.06], focusX=0.45, tin={"type": "whip", "dir": "right"})),
    (26.30, 28.30, "m_order", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (28.30, 33.50, "m_rules", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (33.50, 35.50, "s_phone", 2.0, dict(zoom=[1.0, 1.07], focusX=0.55, tin={"type": "whip", "dir": "left"})),
    (35.50, VO_DUR, "b_7542", 4.4, dict(zoom=[1.0, 1.05], focusY=0.4, tin={"type": "whip", "dir": "up"})),
]
ST = "source/stock/coverr-"
MEDIA = {
    "s_turkey": ST + "putting-roast-turkey-on-the-table-275.mp4", "s_friends": ST + "friends-talking-at-a-restaurant-8705.mp4",
    "s_dinner": ST + "thanksgiving-dinner-9881.mp4", "s_appet": ST + "serving-appetizers-5268.mp4",
    "s_chicken": ST + "men-grilling-chicken-7212.mp4", "s_steak": ST + "cutting-steak-1062.mp4", "s_salad": ST + "colorful-salad-bowl-1709.mp4",
    "s_sweets": ST + "eating-sweets-at-a-cafe-5445.mp4", "s_phone": ST + "man-types-on-iphone-15.mp4",
    "b_8385": "source/IMG_8385.MOV", "b_7542": "source/IMG_7542.MOV",
    **{f"m_{n}": f"work/motion/{n}.mp4" for n in ("plates", "week", "meals", "order", "rules")},
}


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
    zones = []
    ov = [
        {"type": "lowerLabel", "at": 21.72, "dur": 1.9, "title": "بروتين الأول", "eyebrow": "1", "top": 0.56, "plate": True},
        {"type": "lowerLabel", "at": 23.7, "dur": 1.0, "title": "بعدين خضار", "eyebrow": "2", "top": 0.56, "plate": True},
        {"type": "lowerLabel", "at": 24.8, "dur": 1.45, "title": "اللي نفسك فيه", "eyebrow": "3", "top": 0.56, "plate": True},
    ]
    ov.append(dict(end_card(T), image=END_IMAGE, sub="Sources: Palascha 2015 · Shukla 2018"))
    cues = [cue(0.0, "impact", -9), cue(0.02, "boom", -12), cue(0.05, "whoosh_in", -18)]
    for a, b, key, sin, kw in SHOTS[1:]:
        t = kw.get("tin", {}).get("type")
        cues.append(cue(a, {"whip": "whip", "flash": "click"}.get(t, "whoosh_in"), {"whip": -15, "flash": -10}.get(t, -16)))
    Pl = 1.12
    cues += [cue(Pl + 0.0, "accent", -17), cue(Pl + 0.55, "blip", -18), cue(Pl + 0.9, "blip", -18), cue(Pl + 1.25, "thump", -14)]
    W = 8.55
    cues += [cue(W + 0.05 + i * 0.07, "click", -26) for i in range(7)] + [cue(W + 0.6, "accent", -16), cue(W + 3.7, "impact", -10)]
    cues += [cue(W + 5.35 + i * 0.12, "thump", -18) for i in range(6)] + [cue(W + 5.6, "boom", -13)]                # domino
    M = 17.95
    cues += [cue(M + 0.05 + i * 0.035 * 3, "blip", -27) for i in range(7)] + [cue(M + 0.9, "impact", -11)]
    cues += [cue(x, "accent", -17) for x in (21.72, 23.7, 24.8)]
    cues += [cue(26.3 + 0.05 + i * 0.22, "blip", -19) for i in range(3)]
    R = 28.3
    cues += [cue(R + 0.3, "chime", -18), cue(R + 2.2, "thump", -14), cue(R + 3.1, "thump", -14)]
    cues += [cue(33.5 + 0.6, "key", -21), cue(33.5 + 1.0, "key", -22)]
    cues += end_card_sfx(T)
    wf = P / "work" / "vo.words.json"
    wf.write_text(json.dumps({"segments": [{"words": words()}]}, ensure_ascii=False))
    mus = make_music(P, {"bpm": 120, "key": "C", "mode": "minor", "style": "trap", "seed": 53, "duration": round(T + END_DUR, 3),
                         "sections": [{"type": "intro", "until": 3.5}, {"type": "groove", "until": 13.9}, {"type": "build", "until": 15.75, "stop": True},
                                      {"type": "drop", "until": round(T, 3)}, {"type": "outro", "until": round(T + END_DUR, 3)}]}, gain_db=-11)
    edit = {"title": "One feast meal (research reel)", "fps": 30, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": ov,
            "shakes": [], "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
            "voiceTrack": "work/vo.wav", "dialogueLufs": -16.0,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "plateColor": "#56A0FB", "keywordColor": "#FFFFFF",
                         "keywords": ["طبقين", "الحقيقة", "باظ", "ذكي", "بالبروتين", "الخضار", "معقولة", "العادي", "صيام", "عزومة"],
                         "zones": zones + [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.74}]}}
    write_edit(P, edit)
    tot = sum((c["out"] - c["in"]) / c.get("speed", 1) for c in clips)
    print(f"clips cover {tot:.3f}s (VO {VO_DUR}s); unsure words: {UNSURE}")


if __name__ == "__main__":
    main()
