"""CrossFit or gym (to lose weight)? What CrossFit is, how it's trained, its pros and its cons.

Story: hook question -> "what is CrossFit?" -> resistance / bodyweight / Cardio (chips) -> title card "how it works"
(replaces the old light-leak dissolve) -> exercises in a circle, back to back; equipment / weights / sets ->
pros (+): Calories, whole body -> cons (-): heavy weight + bad technique = joints -> wrap-up -> follow CTA -> end card.
The 1.3 s pause at 21.1-22.4 s (two old light leaks, no speech) is cut out.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
from common import (FPS, GRADE, SHARPEN, Timeline, covers_from_detection, cue, end_card, end_card_sfx, load_words,
                    make_music, word_time, write_edit, END_DUR)

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")

tl = Timeline()
tl.add("main", 0.00, 3.00, zoom=[1.0, 1.06], focusY=0.35)                                  # hook
iW = len(tl.clips); tl.add("main", 3.00, 4.87, zoom=1.0, tin={"type": "whip", "dir": "right"})   # "what is it?"
iDef = len(tl.clips); tl.add("main", 4.87, 12.20, zoom=[1.0, 1.05], tin={"type": "zoom", "flash": True})
iHow = len(tl.clips); tl.add("main", 12.20, 12.47, zoom=1.04, hold=12.50, tin={"type": "whip", "dir": "left"})  # 5 leak frames -> still
tl.add("main", 12.47, 13.43, zoom=[1.04, 1.08])
iCard = len(tl.clips); tl.add("main", 13.43, 13.80, zoom=1.0)                                # under the title card (leak dissolve)
iCirc = len(tl.clips); tl.add("main", 13.80, 21.10, zoom=[1.0, 1.06], settle=1.08)
iPC = len(tl.clips); tl.add("main", 22.40, 22.63, zoom=1.0, hold=22.66, tin={"type": "whip", "dir": "up"})  # pause cut; leak -> still
tl.add("main", 22.63, 25.47, zoom=[1.0, 1.05])
iPro = len(tl.clips); tl.add("main", 25.47, 29.33, zoom=[1.04, 1.08], tin={"type": "zoom"})
iCon = len(tl.clips); tl.add("main", 29.33, 35.07, zoom=[1.0, 1.05], tin={"type": "whip", "dir": "left"})
iEnd = len(tl.clips); tl.add("main", 35.07, 38.70, zoom=[1.0, 1.06], tin={"type": "zoom", "flash": True})
tl.add("main", 38.70, 38.95, zoom=1.06, hold=38.68)                                          # "جديد" finishes on a still (old end flash)
T = tl.total()
o = tl.out
tW, tDef, tHow, tCard, tCirc, tPC, tPro, tCon, tEnd = (tl.start_of(i) for i in (iW, iDef, iHow, iCard, iCirc, iPC, iPro, iCon, iEnd))


def chips(at, end, items, top=0.36, row=False):
    return {"type": "checklist", "at": round(at, 3), "dur": round(end - at, 3), "top": top, "row": row,
            "items": [{"at": round(t - at, 3), "text": x} for t, x in items]}


overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": tW - 0.05, "eyebrow": "OSM · TRAINING", "lines": [{"text": "CROSSFIT"}, {"text": "OR GYM?", "accent": True}], "top": 0.36, "tilt": True},
    chips(o(6.4), tHow, [(o(word_time(words, "بمقاومة")), "تمارين بمقاومة"), (o(word_time(words, "بوزن", near=8.3)), "بوزن الجسم"),
                         (o(word_time(words, "Cardio")), "Cardio")]),
    {"type": "kineticTitle", "at": tCard, "dur": tCirc - tCard, "backdrop": True, "eyebrow": "OSM · CROSSFIT", "lines": [{"text": "HOW IT"}, {"text": "WORKS", "accent": True, "size": 190}], "top": 0.3},
    chips(o(19.6), tPC, [(o(word_time(words, "بالعدات")), "العدات"), (o(word_time(words, "والاوزان")), "الأوزان"),
                         (o(word_time(words, "والمجموعات")), "المجموعات")], top=0.4, row=True),
    {"type": "stepBadge", "at": tPro, "dur": tCon - tPro, "mark": "+", "label": "مميزات", "top": 0.27},  # fisheye: his head fills the top-centre
    chips(o(26.3), tCon, [(o(word_time(words, "Calories")), "بتحرق Calories"), (o(word_time(words, "بيقوي")), "بيقوي الجسم كله")], top=0.42),
    {"type": "stepBadge", "at": tCon, "dur": tEnd - tCon, "mark": "–", "label": "عيوب", "top": 0.27},
    chips(o(31.9), tEnd, [(o(word_time(words, "تقيل")), "وزن تقيل"), (o(word_time(words, "وبتكنيك")), "تكنيك غلط"),
                          (o(word_time(words, "هيدمرلك")), "هيدمرلك مفاصلك")], top=0.42),
    end_card(T),
]

covers = covers_from_detection(P / "work/text/original.text.json", band=(0.57, 0.79), center_tol=0.15, cuts=tl.cuts())  # the white PVC stick reads as text: centred captions only

cues = [
    cue(0.0, "boom", -9), cue(0.1, "slam", -15),
    cue(tW, "whip", -11, dir=1.0),
    cue(tDef - 0.6, "riser", -19, dur=0.6), cue(tDef, "boom", -10),
    cue(tHow, "whip", -11, dir=-1.0),
    cue(tCard, "boom", -9), cue(tCard, "slam", -13), cue(tCirc, "whip", -13, dir=1.0),
    cue(tPC, "whip", -11, dir=1.0, bright=7500), cue(tPC, "bass_drop", -17),
    cue(tPro - 0.5, "reverse_hit", -17, dur=0.5), cue(tPro, "slam", -13), cue(tPro + 0.22, "mech", -20),
    cue(tCon, "whip", -11, dir=-1.0), cue(tCon, "bass_drop", -16), cue(tCon + 0.22, "mech", -20),
    cue(o(word_time(words, "هيدمرلك")), "slam", -17),
    cue(tEnd - 0.6, "riser", -19, dur=0.6), cue(tEnd, "boom", -10),
    *end_card_sfx(T),
]
for ov in overlays:  # each chip ticks in with a soft click
    if ov["type"] == "checklist":
        cues += [cue(ov["at"] + it["at"], "click", -21) for it in ov["items"]]

music = make_music(P, {
    "bpm": 120, "key": "G", "mode": "minor", "style": "drive", "seed": 9,
    "sections": [
        {"type": "intro", "until": tW}, {"type": "groove", "until": tDef}, {"type": "groove", "until": tHow},
        {"type": "groove", "until": tCard}, {"type": "drop", "until": tCirc}, {"type": "groove", "until": tPC - 1.0},
        {"type": "build", "until": tPC, "stop": True}, {"type": "drop", "until": tPro}, {"type": "groove", "until": tCon},
        {"type": "groove", "until": tEnd}, {"type": "break", "until": T}, {"type": "outro", "until": T + END_DUR},
    ],
    "duration": T + END_DUR,
}, gain_db=-10)

write_edit(P, {
    "title": "OSM: CrossFit or gym?", "fps": FPS, "width": 1080, "height": 1920,
    "media": {"main": "source/original.mp4"},
    "audio": {"main": "work/stems/original.vocals.wav"},
    "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5",
    "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN},
    "covers": covers,
    "clips": tl.clips,
    "captions": {
        "wordsFile": "work/tx/aligned.words.json", "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
        "keywords": ["تخس", "crossfit", "سيركل", "مميزات", "عيوب", "calories", "مفاصلك"],
    },
    "overlays": overlays,
    "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tDef, "amp": 0.6}, {"at": tCard, "amp": 0.8}, {"at": tPro, "amp": 0.6},
               {"at": o(word_time(words, "هيدمرلك")), "amp": 0.5}, {"at": tEnd, "amp": 0.6}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues},
    "music": music,
    "tail": END_DUR,
})
