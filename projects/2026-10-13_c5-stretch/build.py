"""Stretching done right: Concentric / Eccentric, and the stretch is the opposite of the movement.

Story: hook "you're stretching wrong" -> title card (replaces the old light leak) -> Concentric / Eccentric ->
example 01 Chest (train -> stretch) -> example 02 Triceps (train -> stretch) -> the question for the viewer -> end card.
The old edit's viewfinder intro and colour-bar glitch (0-2.27 s) are dropped: his first word starts at 2.30 s
(measured on the separated voice), right where the clean picture begins.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
from common import (FPS, GRADE, SHARPEN, Timeline, covers_from_detection, cue, end_card, end_card_sfx, load_words,
                    make_music, word_time, write_edit, END_DUR)

P = Path(__file__).resolve().parent
# timing fixes measured on the voice stem (RMS in 50 ms steps): silence 1.85-2.25, speech from 2.30
al = json.load(open(P / "work/tx/aligned.words.json"))
ws = al["segments"][0]["words"]
assert ws[0]["w"] == "طب" and ws[1]["w"] == "بقولك"
ws[0].update(start=2.30, end=2.44)
ws[1].update(start=2.44)
(P / "work/tx/aligned.fixed.words.json").write_text(json.dumps(al, ensure_ascii=False, indent=1))
words = load_words(P / "work/tx/aligned.fixed.words.json")

tl = Timeline()
tl.add("main", 2.27, 4.00, zoom=[1.04, 1.1], focusY=0.4)                    # hook on the bike
iCard = len(tl.clips); tl.add("main", 4.00, 4.57, zoom=1.0)                  # under the title card (old leak)
iS = len(tl.clips); tl.add("main", 4.57, 6.25, zoom=1.0, settle=1.08)       # lands from the card
tl.add("main", 6.25, 6.42, zoom=1.0, hold=6.20)                             # 5 leak frames -> clean still
tl.add("main", 6.42, 10.55, zoom=[1.0, 1.05])                               # Concentric / Eccentric
iChest = len(tl.clips); tl.add("main", 10.55, 16.45, zoom=[1.08, 1.12], focusY=0.42, tin={"type": "zoom", "flash": True})
iTri = len(tl.clips); tl.add("main", 16.45, 21.00, zoom=[1.0, 1.04], tin={"type": "whip", "dir": "left"})
iDown = len(tl.clips); tl.add("main", 21.00, 22.93, zoom=1.12, focusY=0.36, tin={"type": "zoom", "flash": True})
iQ = len(tl.clips); tl.add("main", 22.93, 23.12, zoom=1.04, hold=23.15, tin={"type": "whip", "dir": "up"})
tl.add("main", 23.12, 26.65, zoom=[1.04, 1.1], focusY=0.42)
T = tl.total()
o = tl.out
tCard, tS, tChest, tTri, tDown, tQ = (tl.start_of(i) for i in (iCard, iS, iChest, iTri, iDown, iQ))

overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": tCard - 0.05, "eyebrow": "OSM · STRETCH", "lines": [{"text": "YOU'RE STRETCHING"}, {"text": "WRONG", "accent": True}], "top": 0.33, "tilt": True},
    {"type": "kineticTitle", "at": tCard, "dur": tS - tCard, "backdrop": True, "eyebrow": "OSM · TECHNIQUE", "lines": [{"text": "HOW TO"}, {"text": "STRETCH", "accent": True, "size": 190}], "top": 0.3},
    {"type": "kineticTitle", "at": o(word_time(words, "Concentric")) - 0.05, "dur": o(10.2) - o(7.07), "eyebrow": "انقباض · انبساط",
     "lines": [{"text": "CONCENTRIC", "size": 116}, {"text": "ECCENTRIC", "accent": True, "size": 116}], "top": 0.33},
    {"type": "lowerLabel", "at": o(word_time(words, "Chest")) - 0.1, "dur": tTri - o(word_time(words, "Chest")) + 0.1, "eyebrow": "EXAMPLE 01", "title": "CHEST", "top": 0.14},
    {"type": "stepBadge", "at": o(word_time(words, "بالشكل", near=13.7)), "dur": 1.5, "mark": "1", "label": "TRAIN", "top": 0.3, "side": "left"},
    {"type": "stepBadge", "at": o(word_time(words, "بالشكل", near=15.4)) - 0.2, "dur": tTri - o(15.2), "mark": "2", "label": "STRETCH", "top": 0.3, "side": "left"},
    {"type": "lowerLabel", "at": o(word_time(words, "Triceps")) - 0.1, "dur": tQ - o(word_time(words, "Triceps")) + 0.1, "eyebrow": "EXAMPLE 02", "title": "TRICEPS", "top": 0.14},
    {"type": "stepBadge", "at": o(word_time(words, "بالشكل", near=18.5)), "dur": 1.6, "mark": "1", "label": "TRAIN", "top": 0.3, "side": "left"},
    {"type": "stepBadge", "at": o(word_time(words, "بالشكل", near=20.3)) - 0.2, "dur": tQ - o(20.1), "mark": "2", "label": "STRETCH", "top": 0.3, "side": "left"},
    {"type": "stepBadge", "at": tQ + 0.1, "dur": T - tQ - 0.1, "mark": "?", "label": "السؤال ده ليك", "top": 0.15},
    end_card(T),
]

covers = covers_from_detection(P / "work/text/original.text.json")

cues = [
    cue(0.0, "boom", -9), cue(0.1, "slam", -15),
    cue(tCard, "boom", -9), cue(tCard, "slam", -13), cue(tS, "whip", -13, dir=1.0),            # into / out of the title card
    cue(o(word_time(words, "Concentric")), "mech", -18), cue(o(word_time(words, "Eccentric")), "mech", -18),
    cue(tChest - 0.6, "riser", -19, dur=0.6), cue(tChest, "boom", -10),
    cue(tTri, "whip", -11, dir=-1.0), cue(tTri, "bass_drop", -18),
    cue(tDown - 0.5, "reverse_hit", -16, dur=0.5), cue(tDown, "boom", -11),
    cue(tQ, "whip", -12, dir=1.0, bright=7500), cue(tQ + 0.12, "slam", -16),
    *end_card_sfx(T),
]
for ov in overlays:  # every badge / label lands with a mechanical lock
    if ov["type"] in ("stepBadge", "lowerLabel"):
        cues.append(cue(ov["at"] + 0.22, "click", -22))

music = make_music(P, {
    "bpm": 120, "key": "E", "mode": "minor", "style": "drive", "seed": 5,
    "sections": [
        {"type": "intro", "until": tCard}, {"type": "drop", "until": tS}, {"type": "groove", "until": tChest},
        {"type": "groove", "until": tTri}, {"type": "groove", "until": tDown}, {"type": "groove", "until": tQ},
        {"type": "break", "until": T}, {"type": "outro", "until": T + END_DUR},
    ],
    "duration": T + END_DUR,
}, gain_db=-8)

write_edit(P, {
    "title": "OSM: stretching done right", "fps": FPS, "width": 1080, "height": 1920,
    "media": {"main": "source/original.mp4"},
    "audio": {"main": "work/stems/original.vocals.wav"},
    "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5",
    "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN},
    "covers": covers,
    "clips": tl.clips,
    "captions": {
        "wordsFile": "work/tx/aligned.fixed.words.json", "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
        "keywords": ["غلط", "concentric", "eccentric", "chest", "triceps", "لتحت", "الامامية"],
    },
    "overlays": overlays,
    "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tCard, "amp": 0.8}, {"at": tChest, "amp": 0.6}, {"at": tDown, "amp": 0.6}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues},
    "music": music,
    "tail": END_DUR,
})
