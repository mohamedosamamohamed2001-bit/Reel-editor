"""No perfect sitting posture: his voice-over (main.mov audio, untouched) as the spine; the script screenshot is NOT used.
Same concept as projects/2026-11-01_voiceover: real stock footage (Coverr, non-AI, non-premium, manifest in source/stock),
OSM science/research motion scenes (motion/pieces/posture_science, facts from PubMed-verified papers), his own clips/photo
where he is the coach the voice-over talks about. Output time = voice-over time. Captions = his spoken words
(large-v3, cross-checked with medium; corrections in FIX / MERGE / INSERT).

    .venv/bin/python projects/2026-11-01_voiceover2/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-01_voiceover2
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[0] / "_c5"))
sys.path.insert(0, str(P.parents[0] / "_n6"))
from common import END_DUR, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402
from common2 import END_IMAGE  # noqa: E402

VO_DUR = 40.0
GFX = "format=yuv420p"            # motion graphics are SDR brand pixels: never graded

# large-v3 start time -> spoken word, Egyptian spelling as in his own script (ضهر, قعدة). Both models agree on the sound.
FIX = {2.10: "للضهر", 4.02: "إن", 4.12: "القعدة", 4.58: "المفرودة", 5.56: "بتمنع", 5.86: "وجع", 6.10: "الضهر",
       7.90: "بتبقى", 8.22: "قاعدة", 8.54: "مايلة", 9.88: "وجع", 11.82: "القعدة", 13.74: "ضهرك", 15.10: "عشان",
       21.30: "القعدة", 22.68: "غيّر", 31.66: "وتتمرن", 33.06: "ويقويلك", 37.26: "ابعتلي", 38.70: "أقولك"}
MERGE = {0.00: ("مفيش", 0.16), 8.84: ("ومفيش", 9.24)}           # start -> (word, start of the swallowed next word)
DROP = {37.72, 38.88, 33.60}                                    # "لي" / "لك" / "لك" merged into the previous word
INSERT = [{"w": "مع", "start": 32.18, "end": 32.30}]            # medium hears "مع" (large-v3 swallowed it); trims وتتمرن's end
UNSURE = {7.90: "بتبقى قاعدة مايلة (script: بتقعد مايلة)", 32.18: "مع (only the medium model hears it)", 15.10: "عشان (heard 'شان')"}

SHOTS = [
    (0.00, 2.55, "m_posture", 0.0, dict(grade=GFX)),
    (2.55, 7.05, "m_research", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (7.05, 8.80, "s_laptop", 1.0, dict(zoom=[1.0, 1.08], focusX=0.6, tin={"type": "whip", "dir": "left"})),
    (8.80, 10.25, "s_desk", 17.0, dict(zoom=[1.02, 1.1], focusX=0.68, tin={"type": "zoom"})),
    (10.25, 11.38, "s_office", 3.0, dict(zoom=[1.05, 1.14], focusX=0.5, tin={"type": "whip", "dir": "right"})),
    (11.38, 13.00, "s_tired", 1.6, dict(zoom=[1.0, 1.08], focusX=0.42, tin={"type": "zoom"})),
    (13.00, 15.05, "s_night", 4.6, dict(zoom=[1.04, 1.12], focusX=0.42, tin={"type": "whip", "dir": "left"})),
    (15.05, 18.02, "m_hours", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (18.02, 19.55, "o_2258", 1.2, dict(zoom=[1.0, 1.05], focusY=0.45, speed=0.5, tin={"type": "whip", "dir": "right"})),
    (19.55, 22.15, "m_next", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (22.15, 24.00, "s_desk", 8.6, dict(zoom=[1.0, 1.07], focusX=0.75, tin={"type": "whip", "dir": "left"})),
    (24.00, 26.65, "m_timer", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (26.65, 27.12, "s_watch", 2.5, dict(zoom=[1.1, 1.18], focusX=0.5, tin={"type": "whip", "dir": "up"})),
    (27.12, 28.60, "s_walk", 4.0, dict(zoom=[1.02, 1.1], focusX=0.4, tin={"type": "whip", "dir": "right"})),
    (28.60, 30.38, "s_squat", 9.5, dict(zoom=[1.0, 1.07], focusX=0.5, tin={"type": "zoom"})),
    (30.38, 32.00, "o_2253", 11.0, dict(zoom=[1.0, 1.06], focusY=0.55, tin={"type": "whip", "dir": "left"})),
    (32.00, 34.78, "m_strength", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (34.78, 36.05, "s_type", 6.0, dict(zoom=[1.0, 1.08], focusX=0.5, tin={"type": "whip", "dir": "right"})),
    (36.05, 37.22, "s_bench", 9.0, dict(zoom=[1.02, 1.1], focusX=0.45, tin={"type": "zoom"})),
    (37.22, 38.45, "m_cta", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (38.45, VO_DUR, "o_photo", 0.0, dict(zoom=[1.0, 1.07], focusY=0.36, tin={"type": "zoom"})),
]
ST = "source/stock/coverr-"
MEDIA = {
    "s_laptop": ST + "a-man-working-on-a-laptop-at-the-office-9085.mp4", "s_desk": ST + "sitting-down-at-a-desk-3532.mp4",
    "s_office": ST + "sitting-down-in-the-office-72.mp4", "s_tired": ST + "a-girl-working-at-her-office-desk-feeling-tired-2989.mp4",
    "s_night": ST + "a-woman-working-on-her-computer-late-at-night-3699.mp4", "s_watch": ST + "a-man-checking-the-time-on-his-watch-3435.mp4",
    "s_walk": ST + "walking-around-the-office-4440.mp4", "s_squat": ST + "man-starting-his-squatting-workout-4958.mp4",
    "s_type": ST + "young-man-typing-on-a-laptop-1550.mp4", "s_bench": ST + "weight-lifting-in-the-gym-7769.mp4",
    "o_2253": "source/IMG_2253.mov", "o_2258": "source/IMG_2258.MOV", "o_photo": "work/photo_3324.mp4",
    **{f"m_{n}": f"work/motion/{n}.mp4" for n in ("posture", "research", "hours", "next", "timer", "strength", "cta")},
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
        {"type": "kineticTitle", "at": 10.3, "dur": 1.05, "lines": [{"text": "THE REAL", "size": 104}, {"text": "QUESTION", "accent": True, "size": 118}],
         "top": 0.13, "motion": "smooth", "depth": True},
        {"type": "lowerLabel", "at": 28.7, "dur": 1.6, "title": "الحل على المدى الطويل", "eyebrow": "THE REAL FIX", "top": 0.52, "plate": True},
    ]
    ov.append(dict(end_card(T), image=END_IMAGE, sub="Sources: Swain 2019 · Slater 2019 · Shiri 2018"))
    cues = [cue(0.0, "impact", -9), cue(0.02, "boom", -12), cue(0.05, "whoosh_in", -18)]
    for a, b, key, sin, kw in SHOTS[1:]:
        t = kw.get("tin", {}).get("type")
        cues.append(cue(a, "whip" if t == "whip" else "whoosh_in", -15 if t == "whip" else -16))
    cues += [cue(0.75, "swell", -20), cue(1.05, "impact", -12), cue(0.85, "whoosh_out", -22), cue(1.6, "whoosh_out", -22)]   # strike / DOESN'T EXIST / morphs
    R = 2.55
    cues += [cue(R + 0.3 + i * 0.12, "blip", -24) for i in range(7)] + [cue(R + 1.35, "whoosh_in", -20), cue(R + 2.0, "impact", -11),
             cue(R + 2.35, "boom", -13), cue(R + 3.1, "click", -20)]                                                  # 41 / ✗ / NO CONSENSUS
    cues += [cue(10.3, "boom", -12)]                                                                                 # THE REAL QUESTION
    H = 15.05
    cues += [cue(H + 0.3 + i * 0.3, "key", -26) for i in range(8)] + [cue(H + 1.5, "swell", -22)]                   # clock ticks, spine stiffens
    N = 19.55
    cues += [cue(N + 0.15 + i * 0.575, "whoosh_out", -21) for i in range(4)] + [cue(N + 0.3, "accent", -17)]         # posture changes
    M = 24.0
    cues += [cue(M + 0.15 + i * 0.22, "click", -24) for i in range(8)] + [cue(M + 1.85, "impact", -11)]              # timer / قوم واتحرك
    cues += [cue(28.7, "accent", -17)]
    G = 32.0
    cues += [cue(G + 0.45, "impact", -10), cue(G + 1.2, "whoosh_in", -20)] + [cue(G + 1.6 + i * 0.22, "blip", -20) for i in range(3)]  # -33% / 3 days
    cues += [cue(37.22 + 0.42, "blip", -16), cue(37.22 + 0.5, "chime", -19), cue(38.45, "swell", -20)]               # DM bubble
    cues += end_card_sfx(T)
    wf = P / "work" / "vo.words.json"
    wf.write_text(json.dumps({"segments": [{"words": words()}]}, ensure_ascii=False))
    mus = make_music(P, {"bpm": 120, "key": "D", "mode": "minor", "style": "trap", "seed": 23, "duration": round(T + END_DUR, 3),
                         "sections": [{"type": "intro", "until": 2.55}, {"type": "groove", "until": 28.6}, {"type": "build", "until": 30.38, "stop": True},
                                      {"type": "drop", "until": round(T, 3)}, {"type": "outro", "until": round(T + END_DUR, 3)}]}, gain_db=-11)
    edit = {"title": "No perfect posture (research reel)", "fps": 30, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": ov,
            "shakes": [], "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
            "voiceTrack": "work/vo.wav", "dialogueLufs": -16.0,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "plateColor": "#56A0FB", "keywordColor": "#FFFFFF",
                         "keywords": ["مثالية", "دليل", "وجع", "ضهرك", "الحركة", "جاية", "45", "حقيقي", "مختص", "مكتب"],
                         "zones": [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.74}]}}
    write_edit(P, edit)
    tot = sum((c["out"] - c["in"]) / c.get("speed", 1) for c in clips)
    print(f"clips cover {tot:.3f}s (VO {VO_DUR}s); unsure words: {UNSURE}")


if __name__ == "__main__":
    main()
