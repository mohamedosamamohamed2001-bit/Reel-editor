"""Creatine: worth your money? (batch 2, video 1)

Hook (close-up with the tub) -> what it does: strength (weights cutaway) and muscle mass -> it's in food (salmon,
steak cutaways replace the old stock photos) but not enough -> athletes should take it -> myth (water under the skin)
vs fact (water stored in the muscle) -> comment CTA -> end card.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common2 import *  # noqa: F401,F403

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")
media = {"main": "source/original.mp4"}

tl = Timeline()
tl.add("main", 0.00, 1.83, zoom=[1.0, 1.06], focusY=0.45)                                         # hook close-up
iW = len(tl.clips); tl.add("main", 1.83, 1.97, zoom=1.0, hold=2.00, tin={"type": "whip", "dir": "left"})  # flash -> still
tl.add("main", 1.97, 10.63, zoom=[1.0, 1.05])
iZ = len(tl.clips); tl.add("main", 10.63, 10.83, zoom=1.08, hold=10.86, tin={"type": "zoom", "flash": True})
tl.add("main", 10.83, 20.40, zoom=[1.08, 1.12], focusY=0.42)
iE = len(tl.clips); tl.add("main", 20.40, 20.55, zoom=1.0, hold=20.58, tin={"type": "zoom", "flash": True})
tl.add("main", 20.55, 23.95, zoom=[1.0, 1.05])
T = tl.total()
o = tl.out
tW, tZ, tE = tl.start_of(iW), tl.start_of(iZ), tl.start_of(iE)

t_str, t_kot = o(word_time(words, "القوة")), o(word_time(words, "الكتلة"))
t_fish, t_meat = o(word_time(words, "السمك")), o(word_time(words, "اللحمة"))
t_ath, t_myth, t_fact = o(word_time(words, "رياضي")), o(word_time(words, "مغلوطة")), o(word_time(words, "صح"))
overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": tW - 0.05, "eyebrow": "OSM · SUPPLEMENTS", "lines": [{"text": "CREATINE"}, {"text": "WORTH IT?", "accent": True}], "top": 0.16, "tilt": True},
    {"type": "stepBadge", "at": t_str - 0.05, "dur": o(3.5) - t_str + 0.05, "mark": "+", "label": "القوة", "top": 0.15},
    # old strength icons 3.5-5.1 s -> lifting cutaway on "ترفع اوزان"
    visual(P, media, "v_lift", "w3.jpg", o(3.47), o(5.12) - o(3.47), mode="full", push=[1.04, 1.12], focusY=0.5),
    {"type": "stepBadge", "at": t_kot - 0.1, "dur": o(8.2) - t_kot + 0.1, "mark": "+", "label": "الكتلة العضلية", "top": 0.15},
    # old food photos 8.85-10.7 s -> salmon / steak cutaways on his words
    visual(P, media, "v_fish", "salmon.jpg", o(8.85), t_meat - o(8.85), mode="full", push=[1.0, 1.06]),
    visual(P, media, "v_meat", "steak.jpg", t_meat, tZ - t_meat, mode="full", push=[1.06, 1.0]),
    {"type": "stepBadge", "at": t_ath - 0.1, "dur": o(13.0) - t_ath + 0.1, "mark": "✓", "label": "لو انت رياضي", "top": 0.15},
    {"type": "stepBadge", "at": t_myth - 0.1, "dur": t_fact - t_myth - 0.2, "mark": "✗", "label": "معلومة مغلوطة", "top": 0.15},
    {"type": "kineticTitle", "at": t_fact, "dur": tE - t_fact - 0.1, "eyebrow": "FACT", "lines": [{"text": "مايه في العضلات", "accent": True, "size": 100}], "top": 0.15},
    end_card(T),
]
cues = [
    cue(0.0, "boom", -9), cue(0.12, "slam", -15),
    cue(tW, "whip", -11, dir=-1.0), cue(t_str, "slam", -16),
    cue(o(3.47), "whip", -12, dir=1.0), cue(o(3.47), "bass_drop", -17), cue(o(5.12), "whip", -14, dir=-1.0),
    cue(t_kot, "slam", -16),
    cue(o(8.85), "whip", -12, dir=1.0), cue(t_meat, "whip", -13, dir=-1.0), cue(t_meat, "slam", -18),
    cue(tZ - 0.6, "riser", -19, dur=0.6), cue(tZ, "boom", -10),
    cue(t_ath, "mech", -18), cue(t_myth - 0.1, "slam", -15), cue(t_fact - 0.5, "reverse_hit", -16, dur=0.5), cue(t_fact, "boom", -10),
    cue(tE - 0.5, "reverse_hit", -16, dur=0.5), cue(tE, "boom", -11),
    *end_card_sfx(T),
]
music = make_music(P, {
    "bpm": 120, "key": "D", "mode": "minor", "style": "trap", "seed": 21,
    "sections": [{"type": "intro", "until": tW}, {"type": "groove", "until": o(8.85)}, {"type": "drop", "until": tZ},
                 {"type": "groove", "until": t_fact - 1.0}, {"type": "build", "until": t_fact, "stop": True},
                 {"type": "drop", "until": tE}, {"type": "break", "until": T}, {"type": "outro", "until": T + END_DUR}],
    "duration": T + END_DUR}, gain_db=-9)

covers = covers_for(P, words, band=(0.52, 0.86))
finish(P, tl, {
    "title": "OSM: creatine, worth it?", "fps": FPS, "width": 1080, "height": 1920, "media": media,
    "audio": {"main": "work/stems/original.vocals.wav"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN}, "clips": tl.clips,
    "captions": captions_block("work/tx/aligned.words.json", ["الكرياتين", "القوة", "العضلية", "رياضي", "مغلوطة", "العضلات", "الكومنتس"]),
    "overlays": overlays, "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tZ, "amp": 0.6}, {"at": t_fact, "amp": 0.7}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues}, "music": music, "tail": END_DUR,
}, covers)
