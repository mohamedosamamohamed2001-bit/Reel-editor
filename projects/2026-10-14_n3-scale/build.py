"""Don't track your progress with the scale alone (batch 2, video 3).

Hook -> scale cutaway (replaces the old scale icon) -> fat down + muscle up = same weight (chips) -> scale-only
tracking = frustration, rushing -> real progress: measurements (tape card), body shape, Before & After -> CTA -> end.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common2 import *  # noqa: F401,F403

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")
media = {"main": "source/original.mp4"}

tl = Timeline()
tl.add("main", 0.00, 1.93, zoom=[1.0, 1.06], focusY=0.4)
iA = len(tl.clips); tl.add("main", 1.93, 2.42, zoom=1.0, hold=2.46, tin={"type": "whip", "dir": "left"})
tl.add("main", 2.42, 9.36, zoom=[1.0, 1.05])
iB = len(tl.clips); tl.add("main", 9.36, 9.48, zoom=1.08, focusY=0.4, hold=9.50, tin={"type": "zoom", "flash": True})
tl.add("main", 9.48, 12.76, zoom=[1.08, 1.12], focusY=0.4)
iC = len(tl.clips); tl.add("main", 12.76, 12.86, zoom=1.0, hold=12.90, tin={"type": "whip", "dir": "up"})
tl.add("main", 12.86, 17.98, zoom=[1.0, 1.05])
iD = len(tl.clips); tl.add("main", 17.98, 22.95, zoom=[1.0, 1.05], tin={"type": "zoom", "flash": True})
T = tl.total()
o = tl.out
tA, tB, tC, tD = (tl.start_of(i) for i in (iA, iB, iC, iD))
t_fat, t_mus, t_same = o(word_time(words, "الدهون")), o(word_time(words, "العضلات")), o(word_time(words, "فميزانك"))
t_frus, t_rush = o(word_time(words, "احباط")), o(word_time(words, "استعجال"))
t_meas, t_shape, t_ba = o(word_time(words, "مقاسات")), o(word_time(words, "شكل")), o(word_time(words, "Before"))
t_word = o(word_time(words, "كلمة"))

overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": o(1.45) - 0.05, "eyebrow": "OSM · PROGRESS", "lines": [{"text": "الميزان", "size": 120}, {"text": "بس؟", "accent": True, "size": 120}], "top": 0.16, "tilt": True},
    # old scale icon 1.5-4.1 s -> real scale cutaway on "الميزان مش دايما بيحكي"
    visual(P, media, "v_scale", "scale.jpg", o(1.45), o(4.5) - o(1.45), mode="full", push=[1.08, 1.0], focusY=0.45),
    {"type": "checklist", "at": t_fat - 0.1, "dur": tB - t_fat + 0.05, "top": 0.15,
     "items": [{"at": 0.1, "text": "بتنزل في الدهون"}, {"at": t_mus - t_fat + 0.1, "text": "بتزيد في العضلات"}, {"at": t_same - t_fat + 0.1, "text": "ميزانك ثابت"}]},
    {"type": "stepBadge", "at": t_frus - 0.1, "dur": tC - t_frus + 0.05, "mark": "✗", "label": "احباط", "sub": "واحيانا استعجال", "top": 0.15},
    visual(P, media, "v_tape", "tape.jpg", t_meas - 0.2, t_ba - (t_meas - 0.2), mode="card", label="مقاسات", push=[1.0, 1.1]),
    {"type": "kineticTitle", "at": t_ba - 0.1, "dur": tD - t_ba + 0.05, "eyebrow": "الصور بتاعتك", "lines": [{"text": "BEFORE"}, {"text": "& AFTER", "accent": True}], "top": 0.16},
    {"type": "stepBadge", "at": t_word - 0.1, "dur": T - t_word + 0.05, "mark": "✓", "label": "ابعتلي: تدريب", "top": 0.15},
    end_card(T),
]
cues = [
    cue(0.0, "boom", -9), cue(0.12, "slam", -15),
    cue(o(1.45), "whip", -11, dir=1.0), cue(o(1.45), "bass_drop", -17), cue(tA, "whip", -14, dir=-1.0), cue(o(4.5), "whip", -13, dir=-1.0),
    cue(t_fat, "click", -19), cue(t_mus, "click", -19), cue(t_same, "slam", -16),
    cue(tB - 0.6, "riser", -19, dur=0.6), cue(tB, "boom", -10), cue(t_frus, "slam", -15),
    cue(tC, "whip", -11, dir=1.0, bright=7500), cue(t_meas - 0.2, "whip", -13, dir=-1.0), cue(t_ba - 0.1, "slam", -14), cue(t_ba, "bass_drop", -17),
    cue(tD - 0.5, "reverse_hit", -16, dur=0.5), cue(tD, "boom", -10), cue(t_word, "mech", -18),
    *end_card_sfx(T),
]
music = make_music(P, {
    "bpm": 120, "key": "F", "mode": "minor", "style": "trap", "seed": 23,
    "sections": [{"type": "intro", "until": o(1.45)}, {"type": "drop", "until": o(4.5)}, {"type": "groove", "until": tB},
                 {"type": "groove", "until": tC - 1.0}, {"type": "build", "until": tC, "stop": True}, {"type": "drop", "until": tD},
                 {"type": "groove", "until": T}, {"type": "outro", "until": T + END_DUR}],
    "duration": T + END_DUR}, gain_db=-9)

finish(P, tl, {
    "title": "OSM: the scale isn't everything", "fps": FPS, "width": 1080, "height": 1920, "media": media,
    "audio": {"main": "work/stems/original.vocals.wav"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN}, "clips": tl.clips,
    "captions": captions_block("work/tx/aligned.words.json", ["بالميزان", "الحقيقة", "العضلات", "احباط", "مقاسات", "before", "تدريب"]),
    "overlays": overlays, "shakes": [{"at": 0.0, "amp": 0.5}, {"at": o(1.45), "amp": 0.6}, {"at": tB, "amp": 0.6}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues}, "music": music, "tail": END_DUR,
}, covers_for(P, words, band=(0.50, 0.93), full_width=True, grow_y=0.025))
