"""+1 kg on the scale in one day is not fat: his voice-over (main.mov audio, untouched) as the spine; the script screenshot is NOT used.
Same voice-over system as 2026-11-01_voiceover/_voiceover3: OSM data/science motion scenes (motion/pieces/scale_science, facts from
PubMed-verified papers), 2 Coverr stock clips (non-AI, non-premium, manifest in source/stock) and his B-roll library
(library/broll, check-in poses = progress photos and online follow-up). Output time = voice-over time. Captions = his spoken words
(large-v3, cross-checked with medium; corrections in FIX / MERGE / INSERT).

    .venv/bin/python projects/2026-11-01_voiceover3/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-01_voiceover3
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[0] / "_c5"))
sys.path.insert(0, str(P.parents[0] / "_n6"))
from common import END_DUR, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402
from common2 import END_IMAGE  # noqa: E402

VO_DUR = 50.30
GFX = "format=yuv420p"            # motion graphics are SDR brand pixels: never graded

FIX = {14.72: "صوديوم", 16.14: "حابس", 16.78: "مية", 17.00: "وعامل", 21.26: "إنك", 22.06: "اتوزن", 23.72: "الأكل", 24.36: "4",
       25.28: "الأسبوع", 26.96: "وقارن", 28.02: "الأسبوع", 28.56: "بالأسبوع", 33.28: "أسبوعين", 41.16: "أسبوعين", 41.64: "أو", 41.78: "تلاتة",
       44.14: "بالظبط", 45.90: "الأونلاين", 46.56: "أسبوع", 49.10: "ابعتلي"}
MERGE = {17.40: ("Water Retention", 17.64), 37.76: ("ومتغيّرش", 38.30)}   # start -> (word, start of the swallowed next word)
DROP = set()
INSERT = []
UNSURE = {16.14: "حابس (both models: 'حبس')", 22.06: "اتوزن (both models: 'اوزن')", 18.10: "لو (low confidence; script: طب لو)"}

SHOTS = [
    (0.00, 3.40, "m_scale", 0.0, dict(grade=GFX)),
    (3.40, 6.00, "s_pizza", 3.0, dict(zoom=[1.0, 1.08], focusX=0.5, tin={"type": "whip", "dir": "up"})),
    (6.00, 11.00, "m_kcal", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (11.00, 13.45, "m_days", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "left"})),
    (13.45, 15.30, "s_salt", 1.0, dict(zoom=[1.05, 1.15], focusX=0.5, tin={"type": "whip", "dir": "right"})),
    (15.30, 18.05, "m_water", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (18.05, 21.20, "b_8385", 0.0, dict(zoom=[1.0, 1.08], focusY=0.35, tin={"type": "whip", "dir": "up"})),
    (21.20, 25.60, "m_routine", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "left"})),
    (25.60, 29.40, "m_average", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (29.40, 31.90, "m_waist", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (31.90, 33.80, "b_7565", 1.6, dict(zoom=[1.0, 1.05], focusY=0.4, tin={"type": "flash"})),
    (33.80, 37.70, "m_trend", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "right"})),
    (37.70, 39.60, "b_7546", 3.6, dict(zoom=[1.0, 1.06], focusY=0.4, tin={"type": "whip", "dir": "left"})),
    (39.60, 43.70, "m_plateau", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (43.70, 47.00, "b_7542", 4.0, dict(zoom=[1.0, 1.07], focusY=0.4, tin={"type": "zoom"})),
    (47.00, 49.05, "b_7565", 10.6, dict(zoom=[1.0, 1.05], focusY=0.4, tin={"type": "whip", "dir": "right"})),
    (49.05, VO_DUR, "m_cta", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
]
ST = "source/stock/coverr-"
MEDIA = {
    "s_pizza": ST + "picking-up-a-slice-of-pizza-3860.mp4", "s_salt": ST + "white-salt-falls-against-a-black-background-9461.mp4",
    **{f"b_{n}": f"source/IMG_{n}.MOV" for n in ("8385", "7565", "7546", "7542")},
    **{f"m_{n}": f"work/motion/{n}.mp4" for n in ("scale", "kcal", "days", "water", "routine", "average", "waist", "trend", "plateau", "cta")},
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
            skip.add(nxt)
            end = next(x["end"] for x in ws if round(x["start"], 2) == nxt)
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
    for a, b, key, sin, kw in SHOTS:
        sp = kw.get("speed", 1)
        c = {"src": key, "in": round(sin, 4), "out": round(sin + (b - a) * sp, 4)}
        c.update(kw)
        clips.append(c)
    T = SHOTS[-1][1]
    ov = [
        {"type": "lowerLabel", "at": 32.0, "dur": 1.75, "title": "صورة كل أسبوعين", "top": 0.58, "plate": True},
        {"type": "lowerLabel", "at": 43.8, "dur": 3.1, "title": "متابعة كل أسبوع", "top": 0.6, "plate": True},
    ]
    ov.append(dict(end_card(T), image=END_IMAGE, sub="Sources: Hall 2008 · Orsama 2014"))
    cues = [cue(0.0, "impact", -9), cue(0.02, "boom", -12), cue(0.05, "whoosh_in", -18)]
    for a, b, key, sin, kw in SHOTS[1:]:
        t = kw.get("tin", {}).get("type")
        cues.append(cue(a, {"whip": "whip", "flash": "click"}.get(t, "whoosh_in"), {"whip": -15, "flash": -10}.get(t, -16)))
    cues += [cue(0.35 + i * 0.1, "key", -24) for i in range(8)] + [cue(1.1, "impact", -10), cue(1.9, "thump", -13)]   # scale ticks / +1 KG / fat ✕
    K = 6.0
    cues += [cue(K + 0.3 + i * 0.16, "blip", -25) for i in range(8)] + [cue(K + 2.3, "swell", -21), cue(K + 3.35, "impact", -11)]  # 7000 / bars / NO
    D = 11.0
    cues += [cue(D + 0.05 + i * 0.12, "click", -22) for i in range(5)] + [cue(D + 0.5, "whoosh_out", -22)]
    W = 15.3
    cues += [cue(W + 0.3 + i * 0.12, "blip", -24) for i in range(6)] + [cue(W + 0.5, "swell", -19)]
    cues += [cue(18.05, "boom", -13)]                                                                                # mid hook
    R = 21.2
    cues += [cue(R + x, "accent", -18) for x in (0.2, 1.1, 1.8)] + [cue(R + 2.5 + i * 0.2, "click", -22) for i in range(4)] + [cue(R + 3.5, "impact", -12)]
    A = 25.6
    cues += [cue(A + 0.6, "thump", -15), cue(A + 1.4, "thump", -15), cue(A + 2.0, "impact", -11)]
    cues += [cue(29.4 + 0.2, "whoosh_in", -20), cue(29.4 + 1.0, "click", -20), cue(32.0, "accent", -17)]           # tape / progress photo
    Tr = 33.8
    cues += [cue(Tr + 1.0, "accent", -17), cue(Tr + 1.1, "swell", -21), cue(Tr + 2.4, "chime", -18)]
    Pl = 39.6
    cues += [cue(Pl + 0.1 + i * 0.25, "thump", -17) for i in range(3)] + [cue(Pl + 1.4, "click", -18), cue(Pl + 2.0, "click", -18), cue(Pl + 2.8, "impact", -12)]
    cues += [cue(43.8, "accent", -17), cue(49.05 + 0.42, "blip", -16), cue(49.05 + 0.5, "chime", -19)]
    cues += end_card_sfx(T)
    wf = P / "work" / "vo.words.json"
    wf.write_text(json.dumps({"segments": [{"words": words()}]}, ensure_ascii=False))
    mus = make_music(P, {"bpm": 120, "key": "F", "mode": "minor", "style": "trap", "seed": 37, "duration": round(T + END_DUR, 3),
                         "sections": [{"type": "intro", "until": 3.4}, {"type": "groove", "until": 15.3}, {"type": "build", "until": 18.05, "stop": True},
                                      {"type": "drop", "until": round(T, 3)}, {"type": "outro", "until": round(T + END_DUR, 3)}]}, gain_db=-11)
    edit = {"title": "Scale +1 kg is not fat (research reel)", "fps": 30, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": ov,
            "shakes": [], "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
            "voiceTrack": "work/vo.wav", "dialogueLufs": -16.0,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "plateColor": "#56A0FB", "keywordColor": "#FFFFFF",
                         "keywords": ["مستحيل", "7000", "صوديوم", "Water Retention", "المتوسط", "وسطك", "صورة", "ماشي", "ملتزم", "متابعة"],
                         "zones": [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.74}]}}
    write_edit(P, edit)
    tot = sum((c["out"] - c["in"]) / c.get("speed", 1) for c in clips)
    print(f"clips cover {tot:.3f}s (VO {VO_DUR}s); unsure words: {UNSURE}")


if __name__ == "__main__":
    main()
