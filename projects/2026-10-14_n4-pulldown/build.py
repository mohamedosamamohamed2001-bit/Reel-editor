"""Seated row: close grip vs wide grip (batch 2, video 4).

Question (which grip?) -> close grip: prime mover = Lats (anatomy cutaway), Shoulder extension -> the whole back
works in proportions -> wide grip: elbows higher = Horizontal abduction -> mid back: Middle trapezius & Rhomboids
(anatomy cutaway, replaces the old images) -> recap: wide vs close (split from his own footage) -> end card.
Anatomy: Bourgery & Jacob, Traité complet de l'anatomie de l'homme (1831-1854), public domain.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common2 import *  # noqa: F401,F403

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/aligned.words.json")
media = {"main": "source/original.mp4", "v_split": "work/visuals/split_wide_close.jpg"}

tl = Timeline()
tl.add("main", 0.00, 5.05, zoom=[1.0, 1.05], focusY=0.4)
iA = len(tl.clips); tl.add("main", 5.05, 5.18, zoom=1.0, hold=5.20, tin={"type": "zoom", "flash": True})
tl.add("main", 5.18, 16.92, zoom=[1.0, 1.05])
iB = len(tl.clips); tl.add("main", 16.92, 19.96, zoom=[1.0, 1.04], tin={"type": "whip", "dir": "right"})
iC = len(tl.clips); tl.add("main", 19.96, 22.08, zoom=1.04, settle=1.06)
iD = len(tl.clips); tl.add("main", 22.08, 22.27, zoom=1.0, hold=22.30, tin={"type": "whip", "dir": "left"})
tl.add("main", 22.27, 26.96, zoom=[1.0, 1.05])
iE = len(tl.clips); tl.add("main", 26.96, 27.06, zoom=1.0, hold=27.09, tin={"type": "zoom", "flash": True})
tl.add("main", 27.06, 30.79, zoom=[1.0, 1.04])
iF = len(tl.clips); tl.add("main", 30.79, 36.56, zoom=[1.0, 1.05], tin={"type": "whip", "dir": "up"})
iG = len(tl.clips); tl.add("main", 36.56, 36.76, zoom=1.0, hold=36.79, tin={"type": "zoom", "flash": True})
tl.add("main", 36.76, 42.78, zoom=[1.0, 1.05])
T = tl.total()
o = tl.out
tA, tB, tC, tD, tE, tF, tG = (tl.start_of(i) for i in (iA, iB, iC, iD, iE, iF, iG))
t_lats = o(word_time(words, "Lats", near=8.9))
t_shx = o(word_time(words, "Shoulder"))
t_hab = o(word_time(words, "Horizontal"))
t_mid, t_trap, t_rh = o(word_time(words, "Mid")), o(word_time(words, "Middle")), o(word_time(words, "Rhomboids"))
t_recap = o(word_time(words, "الفرق"))

overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": tA - 0.1, "eyebrow": "OSM · BACK", "lines": [{"text": "SEATED ROW"}, {"text": "WIDE VS CLOSE", "accent": True, "size": 120}], "top": 0.16, "tilt": True},
    {"type": "lowerLabel", "at": tA + 0.1, "dur": o(8.6) - tA - 0.1, "eyebrow": "GRIP 01", "title": "CLOSE GRIP", "top": 0.14},
    visual(P, media, "v_lats", "a_back50.jpg", t_lats - 0.15, 1.9, mode="full", push=[1.0, 1.06],
           markers=[{"at": 0.25, "x": 0.72, "y": 0.52, "label": "LATS", "r": 0.11}]),
    {"type": "lowerLabel", "at": t_shx - 0.1, "dur": o(13.2) - t_shx + 0.1, "eyebrow": "PRIME MOVER: LATS", "title": "SHOULDER EXTENSION", "top": 0.14},
    {"type": "lowerLabel", "at": tD + 0.1, "dur": o(27.6) - tD - 0.1, "eyebrow": "GRIP 02", "title": "WIDE GRIP", "top": 0.14},
    {"type": "lowerLabel", "at": t_hab - 0.1, "dur": t_mid - t_hab, "eyebrow": "ELBOWS UP", "title": "HORIZONTAL ABDUCTION", "top": 0.14},
    # old anatomy images 34.1-36.1 s -> plate with the two muscles he names
    visual(P, media, "v_midback", "a_back50.jpg", t_mid - 0.1, tG - t_mid + 0.1, mode="full", push=[1.05, 1.0], focusY=0.3,
           markers=[{"at": t_trap - t_mid + 0.1, "x": 0.6, "y": 0.25, "label": "MIDDLE TRAPEZIUS", "r": 0.08},
                    {"at": t_rh - t_mid + 0.1, "x": 0.37, "y": 0.31, "label": "RHOMBOIDS", "r": 0.07}]),
    # old row icons 38.7-40.6 s -> his own wide / close frames
    {"type": "visualCard", "src": "v_split", "at": round(o(38.05), 3), "dur": round(o(40.75) - o(38.05), 3), "mode": "full", "push": [1.0, 1.04],
     "markers": [{"at": 0.15, "x": 0.5, "y": 0.06, "label": "WIDE", "r": 0.01}, {"at": 0.9, "x": 0.5, "y": 0.56, "label": "CLOSE", "r": 0.01}]},
    end_card(T),
]
cues = [
    cue(0.0, "boom", -9), cue(0.12, "slam", -15),
    cue(tA - 0.5, "reverse_hit", -16, dur=0.5), cue(tA, "boom", -10), cue(tA + 0.3, "click", -19),
    cue(t_lats - 0.15, "whip", -12, dir=1.0), cue(t_lats + 0.1, "mech", -17), cue(t_lats + 1.75, "whip", -14, dir=-1.0),
    cue(t_shx, "slam", -16),
    cue(tB, "whip", -11, dir=1.0), cue(tC, "slam", -15),
    cue(tD, "whip", -11, dir=-1.0), cue(tD + 0.3, "click", -19),
    cue(tE - 0.5, "reverse_hit", -16, dur=0.5), cue(tE, "boom", -10),
    cue(tF, "whip", -11, dir=1.0, bright=7500), cue(t_hab, "slam", -16),
    cue(t_mid - 0.1, "whip", -12, dir=-1.0), cue(t_mid - 0.1, "bass_drop", -17), cue(t_trap + 0.1, "mech", -17), cue(t_rh + 0.1, "mech", -17),
    cue(tG - 0.5, "reverse_hit", -16, dur=0.5), cue(tG, "boom", -10),
    cue(o(38.05), "whip", -12, dir=1.0), cue(o(38.25), "slam", -16), cue(o(40.75), "whip", -14, dir=-1.0),
    *end_card_sfx(T),
]
music = make_music(P, {
    "bpm": 120, "key": "G", "mode": "minor", "style": "drive", "seed": 24,
    "sections": [{"type": "intro", "until": tA}, {"type": "groove", "until": tB}, {"type": "groove", "until": tD - 1.0},
                 {"type": "build", "until": tD, "stop": True}, {"type": "drop", "until": tF}, {"type": "groove", "until": t_mid},
                 {"type": "drop", "until": tG}, {"type": "groove", "until": T}, {"type": "outro", "until": T + END_DUR}],
    "duration": T + END_DUR}, gain_db=-9)

finish(P, tl, {
    "title": "OSM: seated row wide vs close", "fps": FPS, "width": 1080, "height": 1920, "media": media,
    "audio": {"main": "work/stems/original.vocals.wav"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
    "plates": {"grade": GRADE, "sharpen": SHARPEN}, "clips": tl.clips,
    "captions": captions_block("work/tx/aligned.words.json", ["grip", "lats", "shoulder", "wide", "horizontal", "middle", "الفرق"]),
    "overlays": overlays, "shakes": [{"at": 0.0, "amp": 0.5}, {"at": tA, "amp": 0.6}, {"at": tE, "amp": 0.6}, {"at": tG, "amp": 0.6}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues}, "music": music, "tail": END_DUR,
}, covers_for(P, words, band=(0.50, 0.93), full_width=True, grow_y=0.025)
   # back shot 26.96-30.79: a 2-line old caption, the upper line (white on his light-blue shirt) isn't detected
   + [{"src": "main", "at": 26.96, "dur": 3.83, "box": [0.0, 0.70, 1.0, 0.95], "kind": "blur"}])
