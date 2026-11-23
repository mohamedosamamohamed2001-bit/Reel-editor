"""iFit Reel, version 2 = the FUN concept (Coach Osama 2026-11-23): his handheld unboxing with a friend (source/fun.MOV), its own
sound and energy kept. Cut: 12.8-26.2 s continuous ("iFit عامل شغل عالي أوي أوي أوي" -> "OSAMA10 ... Black Friday" -> the offer),
jump-cut punch-ins on each phrase | "بصوا يا جماعة من الآخر امشوا ورا الراجل ده" | the behind-the-scenes punchline "والمخرج" (the
cameraman revealed) | OSAMA10 code card (same as version 1). Same OSM graphics as version 1 (5,000 EGP, GOLD DRAW in Method Copper).
Captions only on his clearly audible lines (several people talk over each other in this clip), locked #56A0FB bar.

    .venv/bin/python -I projects/2026-11-23_ifit_fun/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-23_ifit_fun
"""
import json, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "projects/_c5"))
from common import cue, write_edit  # noqa: E402

FPS = 30
fr = lambda t: round(t * FPS) / FPS
# (source in, out, zoom, focusY)
CUTS = [(12.80, 15.96, [1.0, 1.04], .45), (15.96, 17.20, [1.12, 1.16], .5), (17.20, 20.06, [1.0, 1.05], .42),
        (20.06, 22.00, [1.14, 1.18], .4), (22.00, 24.24, [1.0, 1.04], .42), (24.24, 26.20, [1.12, 1.16], .42),
        (26.45, 29.40, [1.0, 1.06], .45), (31.55, 33.40, [1.0, 1.08], .45), (33.40, 35.20, [1.0, 1.0], .5)]
# captions: his clearly audible lines, SOURCE times (Whisper large-v3 word times), his words
LINES = [
    (12.88, 15.96, "iFit عامل شغل عالي، عالي أوي أوي أوي", [12.88, 13.44, 13.76, 14.08, 14.78, 15.12, 15.42, 15.7], 15.96),
    (20.06, 21.08, "وعاملين بقى حاجة تانية أجمل", [20.06, 20.3, 20.42, 20.62, 20.82], 21.08),
    (22.00, 24.24, "لو انت اشتريت أي حاجة فوق الـ5000 جنيه،", [22.0, 22.14, 22.28, 22.56, 22.72, 23.12, 23.3, 23.9], 24.24),
    (24.24, 26.12, "بتدخل سحب على نص دهب", [24.24, 25.08, 25.38, 25.48, 25.68], 26.12),
    (26.52, 29.20, "بصوا يا جماعة، من الآخر، امشوا ورا الراجل ده", [26.52, 26.92, 26.98, 27.38, 27.54, 27.96, 28.28, 28.48, 28.64], 28.86),
    (31.74, 32.38, "والمخرج", [31.74], 32.38),
]


def main():
    (P / "work").mkdir(exist_ok=True)
    words = []
    for _, _, text, starts, end in LINES:
        tok = text.split()
        assert len(tok) == len(starts), (text, len(tok), len(starts))
        for k, w in enumerate(tok):
            words.append({"w": w, "start": starts[k], "end": starts[k + 1] if k + 1 < len(starts) else end})
    (P / "work/fun.words.json").write_text(json.dumps({"segments": [{"words": words}]}, ensure_ascii=False))
    clips, cues, t, out_at = [], [], 0.0, {}
    for k, (a, b, z, fy) in enumerate(CUTS):
        c = {"src": "fun", "in": a, "out": b, "zoom": z, "focusY": fy}
        if k and abs(CUTS[k - 1][1] - a) > 0.01:          # a real cut (not a punch-in on continuous sound)
            c["tin"] = {"type": "whip", "dir": "left" if k % 2 else "right", "frames": 4}
            cues.append(cue(t, "whoosh_in", -15))
        elif k:
            cues.append(cue(t, "click", -22))
        out_at[k] = (t, a)
        clips.append(c)
        t = fr(t + (b - a))
    o = lambda src_t: next(ot + (src_t - a) for k, (ot, a) in out_at.items() if CUTS[k][0] <= src_t < CUTS[k][1])
    T = t
    # handheld framing puts his face mid-frame: the numbers sit low, on the box (top 0.76), never on his face
    ov = [{"type": "kineticTitle", "at": round(o(23.48), 3), "dur": 0.8, "lines": [{"text": "5,000 EGP", "size": 120}],
           "top": 0.76, "motion": "smooth", "depth": True},
          {"type": "kineticTitle", "at": round(o(24.30), 3), "dur": 1.8, "eyebrow": "iFit", "lines": [{"text": "GOLD DRAW", "accent": True, "size": 120}],
           "top": 0.76, "motion": "smooth", "depth": True}]
    cues += [cue(o(23.48), "impact", -13), cue(o(24.30), "chime", -15)]
    tc = o(33.40)
    ov.append({"type": "kineticTitle", "at": round(tc, 3), "dur": round(T - tc, 3), "eyebrow": "iFit DISCOUNT CODE",
               "lines": [{"text": "OSAMA10", "accent": True, "size": 200}], "top": 0.36, "backdrop": True, "motion": "smooth", "depth": True})
    cues += [cue(tc - 0.3, "swell", -16, dur=0.4), cue(tc, "slam", -12)]
    cues.append(cue(o(31.74), "blip", -14))                # the "director" reveal
    edit = {"title": "iFit fun", "fps": FPS, "width": 1080, "height": 1920, "media": {"fun": "source/fun.MOV"},
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.2"}, "clips": clips, "overlays": ov,
            "captions": {"wordsFile": "work/fun.words.json", "style": "plate", "plateColor": "#56A0FB", "keywordColor": "#FFFFFF",
                         "karaoke": True, "maxWords": 3, "maxChars": 22, "keywords": ["سحب", "دهب"],
                         "zones": [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.64}]},
            "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "tail": 0,
            "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5", "dialogueLufs": -16.0}
    write_edit(P, edit)
    print(f"T={T:.2f}s, {len(clips)} clips, {len(words)} caption words")


if __name__ == "__main__":
    main()
