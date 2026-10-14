"""One machine, two muscles: Glutes and Lower back (batch 2, video 5).

Hook -> move 1: Glutes (+ Hamstring) - anatomy card -> setup: pad just under the Hip -> reps (+2 Dumbbells to make
it harder) -> move 2: Lower back - Erector spinae anatomy card -> setup: pad above Hip level so the hip stays out ->
wrong way (✗, his demo) vs right way (✓, his demo) -> recap -> end card.
Anatomy: Bourgery & Jacob, Traité complet de l'anatomie de l'homme (1831-1854), public domain.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common2 import *  # noqa: F401,F403

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")
media = {"main": "source/original.mp4"}

tl = Timeline()
tl.add("main", 0.00, 2.05, zoom=[1.0, 1.06], focusY=0.4)
iA = len(tl.clips); tl.add("main", 2.05, 2.46, zoom=1.0, hold=2.50, tin={"type": "whip", "dir": "left"})
tl.add("main", 2.46, 4.81, zoom=[1.0, 1.04])
iB = len(tl.clips); tl.add("main", 4.81, 5.30, zoom=1.0, hold=5.34, tin={"type": "zoom", "flash": True})
tl.add("main", 5.30, 22.40, zoom=[1.0, 1.05])
iC = len(tl.clips); tl.add("main", 22.40, 22.56, zoom=1.0, hold=22.60, tin={"type": "zoom", "flash": True})
tl.add("main", 22.56, 24.81, zoom=[1.0, 1.05])
iD = len(tl.clips); tl.add("main", 24.81, 25.00, zoom=1.0, hold=25.03, tin={"type": "whip", "dir": "up"})
tl.add("main", 25.00, 54.18, zoom=[1.0, 1.04])
iE = len(tl.clips); tl.add("main", 54.18, 54.52, zoom=1.0, hold=54.60, tin={"type": "zoom", "flash": True})
tl.add("main", 54.52, 58.80, zoom=[1.0, 1.04])
T = tl.total()
o = tl.out
tA, tB, tC, tD, tE = (tl.start_of(i) for i in (iA, iB, iC, iD, iE))
t_g1, t_ham = o(word_time(words, "Glutes", near=3.9)), o(word_time(words, "Hamstring"))
t_hip1, t_down = o(word_time(words, "Hip", near=7.4)), o(word_time(words, "بنزل", near=11.8))
t_db = o(word_time(words, "Dumbbells"))
t_lb, t_es = o(word_time(words, "Lower")), o(word_time(words, "Erector", near=27.0))
t_hip2, t_wrong, t_right = o(word_time(words, "مستوى")), o(word_time(words, "ينفعش", near=41.8)), o(word_time(words, "لازم", near=45.0))

overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": tA - 0.1, "eyebrow": "OSM · ONE MACHINE", "lines": [{"text": "GLUTES"}, {"text": "& LOWER BACK", "accent": True, "size": 120}], "top": 0.16, "tilt": True},
    visual(P, media, "v_glutes", "glutes_hams.jpg", t_g1 - 0.3, tB - (t_g1 - 0.3) - 0.05, mode="card", label="Glutes · Hamstring",
           markers=[{"at": 0.2, "x": 0.68, "y": 0.24, "label": "GLUTES", "r": 0.16}, {"at": t_ham - t_g1 + 0.3, "x": 0.66, "y": 0.6, "label": "HAMSTRING", "r": 0.14}]),
    {"type": "lowerLabel", "at": tB + 0.1, "dur": t_down - tB - 0.2, "eyebrow": "MOVE 01 · SETUP", "title": "تحت Hip بحاجة بسيطة", "top": 0.14},
    {"type": "lowerLabel", "at": t_down - 0.1, "dur": t_db - t_down - 0.2, "eyebrow": "MOVE 01", "title": "GLUTES", "top": 0.14},
    {"type": "stepBadge", "at": t_db - 0.15, "dur": tC - t_db + 0.1, "mark": "+", "label": "2 Dumbbells", "top": 0.15},
    {"type": "kineticTitle", "at": t_lb - 0.1, "dur": tD - t_lb + 0.05, "eyebrow": "MOVE 02", "lines": [{"text": "LOWER BACK", "accent": True, "size": 150}], "top": 0.16},
    visual(P, media, "v_es", "a_deep_back.jpg", t_es - 0.2, 2.6, mode="card", label="Erector spinae",
           markers=[{"at": 0.25, "x": 0.58, "y": 0.5, "label": "ERECTOR SPINAE", "r": 0.13}]),
    {"type": "stepBadge", "at": t_hip2 - 0.1, "dur": o(37.4) - t_hip2 + 0.1, "mark": "↑", "label": "فوق مستوى Hip", "top": 0.15},
    {"type": "stepBadge", "at": t_wrong - 0.3, "dur": t_right - t_wrong - 0.1, "mark": "✗", "label": "ما ينفعش كده", "top": 0.15},
    {"type": "stepBadge", "at": t_right - 0.2, "dur": o(54.0) - t_right + 0.2, "mark": "✓", "label": "بالشكل ده", "top": 0.15},
    end_card(T),
]
cues = [
    cue(0.0, "boom", -9), cue(0.12, "slam", -15),
    cue(tA, "whip", -11, dir=-1.0), cue(t_g1 - 0.3, "whip", -13, dir=1.0), cue(t_g1, "mech", -17), cue(t_ham + 0.3, "mech", -18),
    cue(tB - 0.5, "reverse_hit", -16, dur=0.5), cue(tB, "boom", -10), cue(tB + 0.3, "click", -19),
    cue(t_down, "slam", -16), cue(t_db, "slam", -15),
    cue(tC - 0.5, "reverse_hit", -16, dur=0.5), cue(tC, "boom", -10), cue(t_lb, "slam", -14),
    cue(tD, "whip", -11, dir=1.0, bright=7500), cue(t_es - 0.2, "whip", -13, dir=-1.0), cue(t_es + 0.05, "mech", -17),
    cue(t_hip2, "click", -18), cue(t_wrong - 0.3, "slam", -14), cue(t_right - 0.2, "boom", -13), cue(t_right - 0.1, "slam", -16),
    cue(tE - 0.5, "reverse_hit", -16, dur=0.5), cue(tE, "boom", -10),
    *end_card_sfx(T),
]
music = make_music(P, {
    "bpm": 120, "key": "A", "mode": "minor", "style": "drive", "seed": 25,
    "sections": [{"type": "intro", "until": tA}, {"type": "groove", "until": tB}, {"type": "groove", "until": t_down},
                 {"type": "drop", "until": tC - 1.0}, {"type": "build", "until": tC, "stop": True}, {"type": "drop", "until": tD},
                 {"type": "groove", "until": t_wrong - 0.3}, {"type": "break", "until": t_right - 1.0},
                 {"type": "build", "until": t_right - 0.2, "stop": True}, {"type": "drop", "until": tE},
                 {"type": "groove", "until": T}, {"type": "outro", "until": T + END_DUR}],
    "duration": T + END_DUR}, gain_db=-9)

finish(P, tl, {
    "title": "OSM: glutes & lower back, one machine", "fps": FPS, "width": 1080, "height": 1920, "media": media,
    "audio": {"main": "work/stems/original.vocals.wav"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN}, "clips": tl.clips,
    "captions": captions_block("work/tx/aligned.words.json", ["glutes", "hip", "dumbbells", "lower", "erector", "انقباض", "ينفعش"]),
    "overlays": overlays, "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tB, "amp": 0.6}, {"at": tC, "amp": 0.6}, {"at": t_right - 0.2, "amp": 0.6}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues}, "music": music, "tail": END_DUR,
}, covers_for(P, words, band=(0.48, 0.86)))
