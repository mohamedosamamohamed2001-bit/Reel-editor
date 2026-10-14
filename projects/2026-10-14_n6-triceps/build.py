"""Triceps on the cable: the grip doesn't matter, the two movements do (batch 2, video 6).

Hook (3 attachments) -> two movements -> move 1 (top to bottom): Lateral & Medial head attach to the Humerus (anatomy
card) -> move 2 (bottom to top): Long head attaches to the Scapula (anatomy card) -> full range down / up ->
"the grips don't change it" -> every angle covered -> end card.
Anatomy: Bourgery & Jacob, Traité complet de l'anatomie de l'homme (1831-1854), plate 103, public domain.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common2 import *  # noqa: F401,F403

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")
media = {"main": "source/original.mp4"}

tl = Timeline()
tl.add("main", 0.00, 8.82, zoom=[1.0, 1.05], focusY=0.4)
iA = len(tl.clips); tl.add("main", 8.82, 8.98, zoom=1.0, hold=9.02, tin={"type": "whip", "dir": "left"})
tl.add("main", 8.98, 24.26, zoom=[1.0, 1.05])
iB = len(tl.clips); tl.add("main", 24.26, 24.70, zoom=1.0, hold=24.74, tin={"type": "zoom", "flash": True})
tl.add("main", 24.70, 49.20, zoom=[1.0, 1.04])
T = tl.total()
o = tl.out
tA, tB = tl.start_of(iA), tl.start_of(iB)
ds = [w["start"] for w in words if w["w"].strip("،.") in ("بدي", "دي")][:3]
t_two, t_m1 = o(word_time(words, "لحركتين")), o(word_time(words, "الحركة"))
t_lat, t_hum = o(word_time(words, "Lateral")), o(word_time(words, "Humerus"))
t_long, t_scap = o(word_time(words, "Long")), o(word_time(words, "Scapula"))
t_down, t_up = o(word_time(words, "بنزل")), o(word_time(words, "وبطلع"))
t_grips, t_all = o(word_time(words, "المسكات")), o(word_time(words, "الزوايا"))

overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": o(ds[0]) - 0.15, "eyebrow": "OSM · ARMS", "lines": [{"text": "TRICEPS"}, {"text": "WHICH GRIP?", "accent": True}], "top": 0.16, "tilt": True},
    *[{"type": "stepBadge", "at": round(o(t) - 0.05, 3), "dur": round((o(ds[k + 1]) if k < 2 else o(7.4)) - o(t), 3), "mark": str(k + 1), "label": "Grip", "top": 0.15}
      for k, t in enumerate(ds)],
    {"type": "kineticTitle", "at": t_two - 0.3, "dur": t_m1 - t_two + 0.1, "eyebrow": "TRICEPS", "lines": [{"text": "2 MOVES", "accent": True, "size": 170}], "top": 0.16},
    {"type": "lowerLabel", "at": t_m1 - 0.1, "dur": t_lat - t_m1 - 0.3, "eyebrow": "MOVE 01", "title": "PUSHDOWN", "sets": None, "top": 0.14},
    visual(P, media, "v_hum", "arm103.jpg", t_lat - 0.2, tB - (t_lat - 0.2) - 0.05, mode="card", label="Lateral head · Medial head",
           markers=[{"at": 0.25, "x": 0.13, "y": 0.5, "label": "TRICEPS", "r": 0.07}, {"at": t_hum - t_lat + 0.2, "x": 0.5, "y": 0.3, "label": "HUMERUS", "r": 0.06}]),
    {"type": "lowerLabel", "at": tB + 0.15, "dur": t_long - tB - 0.5, "eyebrow": "MOVE 02 · من تحت لفوق", "title": "OVERHEAD EXTENSION", "top": 0.14},
    visual(P, media, "v_scap", "arm103.jpg", t_long - 0.2, o(31.0) - t_long + 0.2, mode="card", label="Long head", push=[1.06, 1.0],
           markers=[{"at": 0.25, "x": 0.83, "y": 0.55, "label": "LONG HEAD", "r": 0.06}, {"at": t_scap - t_long + 0.2, "x": 0.9, "y": 0.25, "label": "SCAPULA", "r": 0.06}]),
    {"type": "stepBadge", "at": t_down - 0.1, "dur": t_up - t_down, "mark": "↓", "label": "للاخر خالص", "top": 0.15},
    {"type": "stepBadge", "at": t_up - 0.1, "dur": o(38.6) - t_up + 0.1, "mark": "↑", "label": "للاخر خالص", "top": 0.15},
    {"type": "kineticTitle", "at": t_grips - 0.2, "dur": o(42.3) - t_grips + 0.2, "eyebrow": "Grip", "lines": [{"text": "مش هتفرق", "accent": True, "size": 130}], "top": 0.16},
    {"type": "kineticTitle", "at": t_all - 0.3, "dur": T - t_all + 0.25, "eyebrow": "TRICEPS", "lines": [{"text": "كل الزوايا", "accent": True, "size": 130}], "top": 0.16},
    end_card(T),
]
for ov in overlays:
    if ov.get("sets", 1) is None:
        ov.pop("sets")
cues = [
    cue(0.0, "boom", -9), cue(0.12, "slam", -15),
    *[cue(o(t), "slam", -17) for t in ds],
    cue(tA, "whip", -11, dir=-1.0), cue(t_two - 0.3, "boom", -11), cue(t_m1, "click", -18),
    cue(t_lat - 0.2, "whip", -13, dir=1.0), cue(t_lat + 0.05, "mech", -17), cue(t_hum + 0.2, "mech", -18),
    cue(tB - 0.5, "reverse_hit", -16, dur=0.5), cue(tB, "boom", -10), cue(tB + 0.4, "click", -18),
    cue(t_long - 0.2, "whip", -13, dir=-1.0), cue(t_long + 0.05, "mech", -17), cue(t_scap + 0.2, "mech", -18),
    cue(t_down, "slam", -16), cue(t_up, "slam", -16), cue(t_grips - 0.2, "boom", -12), cue(t_all - 0.3, "slam", -14),
    *end_card_sfx(T),
]
music = make_music(P, {
    "bpm": 120, "key": "C", "mode": "minor", "style": "trap", "seed": 26,
    "sections": [{"type": "intro", "until": tA}, {"type": "groove", "until": t_two - 0.3}, {"type": "drop", "until": t_lat},
                 {"type": "groove", "until": tB - 1.0}, {"type": "build", "until": tB, "stop": True}, {"type": "drop", "until": t_down},
                 {"type": "groove", "until": t_grips - 1.2}, {"type": "build", "until": t_grips - 0.2, "stop": True},
                 {"type": "drop", "until": T}, {"type": "outro", "until": T + END_DUR}],
    "duration": T + END_DUR}, gain_db=-9)

finish(P, tl, {
    "title": "OSM: triceps on the cable", "fps": FPS, "width": 1080, "height": 1920, "media": media,
    "audio": {"main": "work/stems/original.vocals.wav"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN}, "clips": tl.clips,
    "captions": captions_block("work/tx/aligned.words.json", ["triceps", "لحركتين", "lateral", "humerus", "long", "scapula", "هتفرق", "الزوايا"]),
    "overlays": overlays, "shakes": [{"at": 0.0, "amp": 0.5}, {"at": t_two - 0.3, "amp": 0.6}, {"at": tB, "amp": 0.6}, {"at": t_grips - 0.2, "amp": 0.6}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues}, "music": music, "tail": END_DUR,
}, covers_for(P, words, band=(0.48, 0.86)))
