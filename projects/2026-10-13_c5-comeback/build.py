"""Comeback after injury / time off: 3 rules. Builds edit.json + the original music track.

Story: hook question -> "3 things" -> 01 light weights, progress gradually -> 02 Stretch before & after ->
03 controlled reps, full Range of Motion -> demo set (music drop) -> comment CTA -> end card.
Source: the finished 720x1280 edit; its burned-in captions are covered and replaced, its flashes/light leaks
are replaced by new transitions, its music is replaced by an original track (voice separated with tools/separate.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
from common import (FPS, GRADE, SHARPEN, Timeline, covers_from_detection, cue, end_card, end_card_sfx, load_words,
                    make_music, word_time, write_edit, END_DUR)

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")

tl = Timeline()
# A: hook, same take split at "تعال" for a punch-in
tl.add("main", 0.0, 1.84, zoom=[1.0, 1.04], focusY=0.42)
tl.add("main", 1.84, 4.33, zoom=1.12, focusY=0.36, settle=1.06)
# B: point 1 (gym with mural), whip in
# (its first 4 frames are the old edit's warm flash: a clean held frame rides the whip instead)
iB = len(tl.clips); tl.add("main", 4.33, 4.47, zoom=1.0, hold=4.50, tin={"type": "whip", "dir": "left"})
tl.add("main", 4.47, 7.40, zoom=[1.0, 1.05])
# C: point 2 (arm circles), vertical whip
iC = len(tl.clips); tl.add("main", 7.40, 10.87, zoom=[1.02, 1.0], tin={"type": "whip", "dir": "up"})
# D: point 3 on the bench, zoom punch through a flash
iD = len(tl.clips); tl.add("main", 10.87, 15.86, zoom=[1.0, 1.06], tin={"type": "zoom", "flash": True})
# demo set: real speed -> 2x ramp (frame-blended motion blur) -> real speed on the lockout
iD2 = len(tl.clips); tl.add("main", 15.86, 16.40, zoom=1.04)
iR = len(tl.clips); tl.add("main", 16.40, 17.90, zoom=1.04, speed=2)
iR2 = len(tl.clips); tl.add("main", 17.90, 18.93, zoom=[1.04, 1.08])
# E: CTA, zoom + flash (replaces the old flash on this cut)
iE = len(tl.clips); tl.add("main", 18.93, 21.43, zoom=[1.0, 1.05], focusY=0.42, tin={"type": "zoom", "flash": True})
T = tl.total()

tB, tC, tD, tDrop, tR, tR2, tE = (tl.start_of(i) for i in (iB, iC, iD, iD2, iR, iR2, iE))
t3 = word_time(words, "3")
overlays = [
    {"type": "kineticTitle", "at": 0.1, "dur": 1.75, "eyebrow": "OSM · COMEBACK", "lines": [{"text": "BACK TO"}, {"text": "TRAINING", "accent": True}], "top": 0.33, "tilt": True},
    {"type": "stepBadge", "at": t3 - 0.05, "dur": tB - t3 + 0.05, "mark": "3", "label": "حاجات", "sub": "لازم تركز عليهم", "top": 0.15},
    {"type": "stepBadge", "at": tB, "dur": tC - tB, "mark": "01", "label": "أوزان خفيفة", "sub": "ونعلى بالتدريج", "top": 0.15},
    {"type": "stepBadge", "at": tC, "dur": tD - tC, "mark": "02", "label": "Stretch", "sub": "قبل وبعد التمرين", "top": 0.15},
    {"type": "stepBadge", "at": tD, "dur": tDrop - tD, "mark": "03", "label": "أداء مضبوط", "sub": "FULL RANGE OF MOTION", "top": 0.15},
    {"type": "kineticTitle", "at": tDrop, "dur": tE - tDrop - 0.1, "eyebrow": "03", "lines": [{"text": "FULL RANGE"}, {"text": "OF MOTION", "accent": True}], "top": 0.15},
    end_card(T),
]

covers = covers_from_detection(P / "work/text/original.text.json")
covers[0]["dur"] = round(covers[0]["dur"] + covers[0]["at"], 3); covers[0]["at"] = 0.0  # "كا" typing in on frame 1

cues = [
    cue(0.0, "boom", -9), cue(0.12, "slam", -15),                       # cold open: weight on frame 1 + title slam
    cue(1.84, "air", -24),                                                # punch-in
    cue(t3, "slam", -17), cue(t3, "bass_drop", -19),                      # "3"
    cue(tB, "whip", -11, dir=-1.0), cue(tB, "bass_drop", -18),            # whip into 01
    cue(tC, "whip", -11, dir=1.0, bright=7500),                           # whip up into 02
    cue(tD - 0.6, "riser", -19, dur=0.6), cue(tD, "boom", -10), cue(tD + 0.05, "slam", -16),   # zoom + flash into 03
    cue(tDrop, "boom", -8), cue(tDrop + 0.08, "slam", -13),              # the drop: demo set + title
    cue(tR, "whip", -14, dur=0.45, dir=1.0), cue(tR2, "slam", -14),      # ramp up / land the lockout
    cue(tE, "reverse_hit", -15, dur=0.5), cue(tE, "boom", -11),     # zoom + flash into the CTA
    *end_card_sfx(T),
]
for i, t in enumerate((tB, tC, tD)):                                      # step badges lock in with a mechanical click
    cues.append(cue(t + 0.23, "mech", -21))

music = make_music(P, {
    "bpm": 120, "key": "D", "mode": "minor", "style": "trap", "seed": 3,
    "sections": [
        {"type": "intro", "until": tB}, {"type": "groove", "until": tC}, {"type": "groove", "until": tD},
        {"type": "groove", "until": tDrop - 2.0}, {"type": "build", "until": tDrop, "stop": True},
        {"type": "drop", "until": tl.out(18.69) - 0.1}, {"type": "groove", "until": T}, {"type": "outro", "until": T + END_DUR},
    ],
    "duration": T + END_DUR,
}, gain_db=-9)

write_edit(P, {
    "title": "OSM: back to training (3 rules)", "fps": FPS, "width": 1080, "height": 1920,
    "media": {"main": "source/original.mp4"},
    "audio": {"main": "work/stems/original.vocals.wav"},
    "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5",
    "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN},
    "covers": covers,
    "clips": tl.clips,
    "captions": {
        "wordsFile": "work/tx/aligned.words.json", "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
        "keywords": ["إصابة", "3", "خفيفة", "stretch", "مضبوط", "كامل", "الكومنت"],
    },
    "overlays": overlays,
    "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tD, "amp": 0.7}, {"at": tDrop, "amp": 1.0}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues},
    "music": music,
    "tail": END_DUR,
})
