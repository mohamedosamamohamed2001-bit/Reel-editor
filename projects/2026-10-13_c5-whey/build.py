"""Whey protein: worth your money or not?

Story: hook question -> title card (replaces the old light leak) -> what whey does (tracked label on the tub) ->
protein = muscle mass + recovery -> food sources (eggs / meat / fish chips replace the old stock food photos) ->
"or swap it for a supplement like this" -> "so, buy it or not?" -> case 1: food covers it, don't buy ->
case 2: no time for meals, it helps -> comment CTA -> end card.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
from common import (FPS, GRADE, SHARPEN, Timeline, covers_from_detection, cue, end_card, end_card_sfx, load_words,
                    make_music, word_time, write_edit, END_DUR)

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")
track = json.load(open(P / "analysis/track_tub.json"))  # tools/track.py, tub centre in source fractions (static camera)

tl = Timeline()
tl.add("main", 0.0, 2.97, zoom=[1.0, 1.06], focusY=0.4)                          # standing intro, the question
iCard = len(tl.clips); tl.add("main", 2.97, 3.55, zoom=1.0)                       # under the title card (old leak)
iA = len(tl.clips); tl.add("main", 3.55, 10.20, zoom=[1.0, 1.04], settle=1.08)    # what whey does, protein basics
iB = len(tl.clips); tl.add("main", 10.20, 18.17, zoom=[1.1, 1.14], focusY=1.0, tin={"type": "whip", "dir": "right"})  # bottom-anchored: the tub stays in frame
iQ = len(tl.clips); tl.add("main", 18.17, 19.50, zoom=1.2, focusY=0.36, tin={"type": "zoom", "flash": True})
i1 = len(tl.clips); tl.add("main", 19.50, 23.18, zoom=[1.0, 1.04], settle=1.06)   # case 1
i2 = len(tl.clips); tl.add("main", 23.18, 27.30, zoom=[1.12, 1.16], focusY=0.42, settle=1.06)  # case 2
iE = len(tl.clips); tl.add("main", 27.30, 30.95, zoom=[1.0, 1.06], tin={"type": "zoom", "flash": True})  # CTA
T = tl.total()
o = tl.out
tCard, tA, tB, tQ, t1, t2, tE = (tl.start_of(i) for i in (iCard, iA, iB, iQ, i1, i2, iE))


def to_out(sx, sy, z, fx=0.5, fy=0.5):
    """Source-frame point -> output-frame point for a clip framed at zoom z / focus (same maths as FramedVideo)."""
    c = 1 / z
    x0 = min(max(fx - c / 2, 0), 1 - c)
    y0 = min(max(fy - c / 2, 0), 1 - c)
    return (sx - x0) / c, (sy - y0) / c


def tracked(t0, t1_, text, sub=None, z=1.02, fy=0.5):
    """Label pinned to the tub (ring on the logo), tracked keys mapped into the clip's output frame."""
    ks = [k for k in track if t0 <= o(k["t"]) <= t1_] or [track[-1]]  # static camera: hold the last tracked spot
    keys = []
    for k in ks:
        x, y = to_out(k["x"], k["y"] - 0.035, z, 0.5, fy)
        keys.append({"t": round(max(0.0, o(k["t"]) - t0) if len(ks) > 1 else 0.0, 3), "x": round(x, 4), "y": round(y, 4)})
    if len(keys) == 1:
        keys.append({**keys[0], "t": round(t1_ - t0, 3)})
    return {"type": "trackedLabel", "at": round(t0, 3), "dur": round(t1_ - t0, 3), "text": text, "sub": sub, "keys": keys, "side": "right"}


tFoodEggs, tMeat, tFish = (o(word_time(words, w)) for w in ("البيض", "اللحمة", "السمك"))
overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": tCard - 0.05, "eyebrow": "OSM · SUPPLEMENTS", "lines": [{"text": "WORTH YOUR"}, {"text": "MONEY?", "accent": True}], "top": 0.33, "tilt": True},
    {"type": "kineticTitle", "at": tCard, "dur": tA - tCard, "backdrop": True, "eyebrow": "OSM · NUTRITION", "lines": [{"text": "WHEY"}, {"text": "PROTEIN", "accent": True, "size": 180}], "top": 0.3},
    tracked(o(4.0), o(6.6), "WHEY PROTEIN", "SUPPLEMENT"),
    {"type": "checklist", "at": o(8.0), "dur": tB - o(8.0), "top": 0.2,
     "items": [{"at": o(word_time(words, "كتلة")) - o(8.0), "text": "كتلة العضلات"}, {"at": o(word_time(words, "الاستشفاء")) - o(8.0), "text": "الاستشفاء"}]},
    {"type": "checklist", "at": tFoodEggs - 0.1, "dur": o(15.62) - tFoodEggs + 0.1, "top": 0.755, "row": True,
     "items": [{"at": 0.1, "text": "البيض"}, {"at": tMeat - tFoodEggs + 0.1, "text": "اللحمة"}, {"at": tFish - tFoodEggs + 0.1, "text": "السمك"}]},
    {"type": "kineticTitle", "at": tQ, "dur": t1 - tQ, "eyebrow": "من الآخر", "lines": [{"text": "BUY IT"}, {"text": "OR NOT?", "accent": True}], "top": 0.14},
    {"type": "stepBadge", "at": t1 + 0.05, "dur": t2 - t1 - 0.05, "mark": "1", "label": "من الأكل؟", "sub": "ما تشتريهوش", "top": 0.15},
    {"type": "stepBadge", "at": t2 + 0.05, "dur": tE - t2 - 0.05, "mark": "2", "label": "وقتك ضيق؟", "sub": "فده هيفيدك", "top": 0.15},
    end_card(T),
]
tSwap = o(word_time(words, "Supplement", near=17.0))
overlays.insert(5, tracked(tSwap - 0.2, o(18.1), "SUPPLEMENT", z=1.135, fy=1.0))

# old burned-in captions + the old stock food photos (eggs / meat / fish, 13.15-15.57 s) under one wide plate
# captions are always centred at y 0.62-0.76 here; the window frame by his arm and the tub label are not text
covers = [c for c in covers_from_detection(P / "work/text/original.text.json", band=(0.6, 0.77), center_tol=0.12) if c["at"] < 3.3]
# seated (3.55 s on): the jacket's white stripes sit in the caption band and defeat the text detector, but the old
# caption there is always ONE centred line at y 0.69-0.72 shown while he speaks -> fixed plates on the speech spans
spans = []
for w in words:
    if w["start"] < 3.4:
        continue
    if spans and w["start"] - spans[-1][1] < 1.0:
        spans[-1][1] = w["end"]
    else:
        spans.append([w["start"], w["end"]])
for a, b in spans:
    covers.append({"src": "main", "at": round(a - 0.25, 3), "dur": round(b - a + 0.6, 3), "box": [0.07, 0.668, 0.93, 0.744]})
covers.append({"src": "main", "at": 13.08, "dur": 2.56, "box": [0.02, 0.728, 0.98, 0.878]})

cues = [
    cue(0.0, "boom", -9), cue(0.1, "slam", -15),
    cue(tCard, "boom", -9), cue(tCard, "slam", -13), cue(tA, "whip", -13, dir=-1.0),
    cue(o(4.0) + 0.05, "mech", -18),                                              # tracked label locks on
    cue(tB, "whip", -11, dir=1.0), cue(tB, "bass_drop", -18),
    cue(tFoodEggs, "click", -19), cue(tMeat, "click", -19), cue(tFish, "click", -19),
    cue(tSwap - 0.15, "mech", -18),
    cue(tQ - 0.6, "riser", -18, dur=0.6), cue(tQ, "boom", -9), cue(tQ + 0.08, "slam", -14),
    cue(t1, "slam", -16), cue(t2, "slam", -16),
    cue(tE - 0.5, "reverse_hit", -16, dur=0.5), cue(tE, "boom", -11),
    *end_card_sfx(T),
]

music = make_music(P, {
    "bpm": 120, "key": "F", "mode": "minor", "style": "trap", "seed": 7,
    "sections": [
        {"type": "intro", "until": tCard}, {"type": "drop", "until": tA}, {"type": "groove", "until": tB},
        {"type": "groove", "until": tQ - 1.0}, {"type": "build", "until": tQ, "stop": True},
        {"type": "drop", "until": t1}, {"type": "groove", "until": t2}, {"type": "groove", "until": tE},
        {"type": "break", "until": T}, {"type": "outro", "until": T + END_DUR},
    ],
    "duration": T + END_DUR,
}, gain_db=-7)

write_edit(P, {
    "title": "OSM: whey protein, worth it?", "fps": FPS, "width": 1080, "height": 1920,
    "media": {"main": "source/original.mp4"},
    "audio": {"main": "work/stems/original.vocals.wav"},
    "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5",
    "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN},
    "covers": covers,
    "clips": tl.clips,
    "captions": {
        "wordsFile": "work/tx/aligned.words.json", "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
        "keywords": ["فلوسك", "البروتين", "العضلات", "supplement", "ضيق", "الكومنت"],
    },
    "overlays": overlays,
    "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tCard, "amp": 0.8}, {"at": tQ, "amp": 0.9}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues},
    "music": music,
    "tail": END_DUR,
})
