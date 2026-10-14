"""Copying workouts from the internet won't give you results (batch 2, video 2).

Hook -> internet workouts (phone card) -> not matched to your goal & level (chips) -> everyone has his own plan ->
"right training isn't copying" -> a plan made for you (checklist card) -> CTA: send "تدريب" -> end card.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common2 import *  # noqa: F401,F403

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")
media = {"main": "source/original.mp4"}

tl = Timeline()
tl.add("main", 0.00, 2.30, zoom=[1.0, 1.06], focusY=0.4)
iA = len(tl.clips); tl.add("main", 2.30, 2.66, zoom=1.0, hold=2.70, tin={"type": "whip", "dir": "left"})   # leak -> still
tl.add("main", 2.66, 5.55, zoom=[1.0, 1.04])
iB = len(tl.clips); tl.add("main", 5.55, 5.95, zoom=1.1, focusY=0.4, hold=5.98, tin={"type": "zoom", "flash": True})
tl.add("main", 5.95, 11.58, zoom=[1.1, 1.14], focusY=0.4)
iC = len(tl.clips); tl.add("main", 11.58, 11.82, zoom=1.0, hold=11.85, tin={"type": "whip", "dir": "up"})
tl.add("main", 11.82, 15.12, zoom=[1.0, 1.05])
iD = len(tl.clips); tl.add("main", 15.12, 15.36, zoom=1.0, hold=15.40, tin={"type": "zoom", "flash": True})
tl.add("main", 15.36, 21.70, zoom=[1.0, 1.05])
T = tl.total()
o = tl.out
tA, tB, tC, tD = (tl.start_of(i) for i in (iA, iB, iC, iD))
t_net, t_goal, t_lvl = o(word_time(words, "النت")), o(word_time(words, "لهدفك")), o(word_time(words, "ومستواك"))
t_copy, t_plan, t_word = o(word_time(words, "تقليد")), o(word_time(words, "خطة", near=13.9)), o(word_time(words, "كلمة"))

overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": tA - 0.05, "eyebrow": "OSM · TRAINING", "lines": [{"text": "متستناش نتيجة", "accent": True, "size": 110}], "top": 0.16, "tilt": True},
    visual(P, media, "v_phone", "phone1.jpg", t_net - 0.35, tB - (t_net - 0.35), mode="card", label="تمارين من على النت", push=[1.0, 1.08]),
    {"type": "checklist", "at": t_goal - 0.1, "dur": tC - t_goal + 0.1 - 0.05, "top": 0.17, "row": True,
     "items": [{"at": 0.1, "text": "هدفك"}, {"at": t_lvl - t_goal + 0.1, "text": "مستواك"}]},
    {"type": "kineticTitle", "at": t_copy - 0.15, "dur": o(13.0) - t_copy + 0.15, "eyebrow": "التدريب الصح", "lines": [{"text": "مش تقليد", "accent": True, "size": 130}], "top": 0.16},
    visual(P, media, "v_plan", "checklist.jpg", t_plan - 0.2, tD - (t_plan - 0.2), mode="card", label="خطة معمولة ليك", push=[1.0, 1.08]),
    {"type": "stepBadge", "at": t_word - 0.1, "dur": T - t_word + 0.1 - 0.05, "mark": "✓", "label": "ابعتلي: تدريب", "top": 0.15},
    end_card(T),
]
cues = [
    cue(0.0, "boom", -9), cue(0.12, "slam", -15),
    cue(tA, "whip", -11, dir=-1.0), cue(t_net - 0.35, "slam", -15), cue(t_net - 0.35, "bass_drop", -18),
    cue(tB - 0.6, "riser", -19, dur=0.6), cue(tB, "boom", -10),
    cue(t_goal, "click", -19), cue(t_lvl, "click", -19),
    cue(tC, "whip", -11, dir=1.0, bright=7500), cue(t_copy - 0.15, "slam", -14),
    cue(t_plan - 0.2, "whip", -13, dir=1.0), cue(t_plan, "mech", -18),
    cue(tD - 0.5, "reverse_hit", -16, dur=0.5), cue(tD, "boom", -10), cue(t_word, "mech", -18),
    *end_card_sfx(T),
]
music = make_music(P, {
    "bpm": 120, "key": "E", "mode": "minor", "style": "drive", "seed": 22,
    "sections": [{"type": "intro", "until": tA}, {"type": "groove", "until": tB}, {"type": "groove", "until": tC - 1.0},
                 {"type": "build", "until": tC, "stop": True}, {"type": "drop", "until": tD}, {"type": "groove", "until": T},
                 {"type": "outro", "until": T + END_DUR}],
    "duration": T + END_DUR}, gain_db=-9)

finish(P, tl, {
    "title": "OSM: copying workouts", "fps": FPS, "width": 1080, "height": 1920, "media": media,
    "audio": {"main": "work/stems/original.vocals.wav"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN}, "clips": tl.clips,
    "captions": captions_block("work/tx/aligned.words.json", ["نتيجة", "النت", "لهدفك", "تقليد", "خطة", "تدريب"]),
    "overlays": overlays, "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tB, "amp": 0.6}, {"at": t_copy, "amp": 0.6}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues}, "music": music, "tail": END_DUR,
}, covers_for(P, words, band=(0.52, 0.86)))
