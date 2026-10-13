"""Leg day vlog: 8 exercises, cut to the music.

No dialogue in the source (its soundtrack was a commercial rap track, replaced by an original OSM track), so this one
is a music-driven montage: each exercise ~3.3 s, cuts on the beat grid, speed ramps on the machine work, one freeze
frame on the deadlift lockout. The old exercise labels (bottom 12 %, in the Reels UI zone) sit under a cinematic
bottom fade; new labels (name + the original's prescription, 3 x 15) animate in above it, inside the safe area.
The original's "Sated calf raises" typo is corrected to SEATED.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
from common import FPS, GRADE, SHARPEN, Timeline, cue, end_card, end_card_sfx, make_music, write_edit, END_DUR

P = Path(__file__).resolve().parent
tl = Timeline()
ex = []  # (name, first clip index, last clip index)


def exercise(name, parts):
    first = len(tl.clips)
    for a, b, kw in parts:
        tl.add("main", a, b, **kw)
    ex.append((name, first, len(tl.clips) - 1))


tl.add("main", 3.05, 5.55, zoom=[1.0, 1.1], focusY=0.45)                                         # intro (title)
exercise("BULGARIAN SQUAT", [(5.62, 7.10, {"zoom": 1.0, "tin": {"type": "whip", "dir": "left"}}),
                             (7.15, 8.90, {"zoom": [1.0, 1.04], "settle": 1.06})])
exercise("DEADLIFT", [(10.42, 11.84, {"zoom": [1.0, 1.04], "tin": {"type": "zoom", "flash": True}}),
                      (13.55, 14.75, {"zoom": 1.0, "settle": 1.05})])
iFreeze = len(tl.clips); tl.add("main", 14.75, 15.55, freeze=True, zoom=[1.0, 1.08])              # lockout freeze
exercise("SQUAT", [(17.05, 18.85, {"zoom": [1.0, 1.04], "tin": {"type": "whip", "dir": "up"}}),
                   (20.85, 22.25, {"zoom": 1.02, "settle": 1.05})])
exercise("LEG EXTENSION", [(22.45, 23.70, {"zoom": 1.0, "tin": {"type": "zoom", "flash": True}}),
                           (23.70, 25.70, {"zoom": 1.0, "speed": 2}),
                           (25.70, 26.80, {"zoom": [1.0, 1.04]})])
exercise("LEG CURL", [(26.86, 28.40, {"zoom": 1.0, "tin": {"type": "whip", "dir": "right"}}),
                      (28.40, 30.40, {"zoom": 1.0, "speed": 2}),
                      (30.40, 31.30, {"zoom": [1.0, 1.04]})])
exercise("ADDUCTION", [(31.86, 33.40, {"zoom": 1.0, "tin": {"type": "whip", "dir": "down"}}),
                       (33.40, 35.40, {"zoom": 1.0, "speed": 2}),
                       (35.40, 36.40, {"zoom": [1.0, 1.04]})])
exercise("SEATED CALF RAISES", [(37.45, 39.95, {"zoom": [1.0, 1.05], "tin": {"type": "zoom", "flash": True}}),
                                (40.00, 40.95, {"zoom": 1.0, "settle": 1.05})])
exercise("MACHINE CALF RAISES", [(41.05, 44.60, {"zoom": [1.0, 1.06], "tin": {"type": "whip", "dir": "left"}})])
T = tl.total()

starts = [tl.start_of(f) for _, f, _ in ex]
ends = [tl.start_of(l) + tl.frames(tl.clips[l]) / FPS for _, _, l in ex]
tFreeze = tl.start_of(iFreeze)
overlays = [
    {"type": "kineticTitle", "at": 0.05, "dur": 1.5, "eyebrow": "OSM · GYM VLOG", "lines": [{"text": "LEG"}, {"text": "DAY", "accent": True, "size": 220}], "top": 0.3, "tilt": True},
    {"type": "stepBadge", "at": 1.55, "dur": starts[0] - 1.55, "mark": "8", "label": "EXERCISES", "sub": "3 × 15", "top": 0.3, "side": "left"},
]
for k, ((name, _, _), a, b) in enumerate(zip(ex, starts, ends)):
    if name == "DEADLIFT":
        b = tFreeze  # the freeze has its own title
    overlays.append({"type": "lowerLabel", "at": round(a + 0.12, 3), "dur": round(b - a - 0.2, 3), "eyebrow": f"EXERCISE {k + 1:02d}", "title": name, "sets": "3 × 15"})
overlays.append({"type": "kineticTitle", "at": tFreeze, "dur": tl.frames(tl.clips[iFreeze]) / FPS, "eyebrow": "EXERCISE 02 · 3 × 15",
                 "lines": [{"text": "DEADLIFT", "accent": True, "size": 190}], "top": 0.58})
overlays.append(end_card(T))

cues = [cue(0.0, "boom", -8), cue(0.1, "slam", -12), cue(1.55, "slam", -15), cue(1.75, "mech", -16)]
for k, ((name, f, l), a) in enumerate(zip(ex, starts)):
    t = tl.clips[f].get("tin", {})
    if t.get("type") == "whip":
        d = {"left": -1.0, "right": 1.0}.get(t.get("dir"), 1.0)
        cues += [cue(a, "whip", -9, dir=d), cue(a, "bass_drop", -14)]
    elif t.get("type") == "zoom":
        cues += [cue(a - 0.6, "riser", -15, dur=0.6), cue(a, "boom", -9)]
    cues.append(cue(a + 0.3, "click", -17))  # label lock-in
    for i in range(f + 1, l + 1):  # inside an exercise: speed ramps whoosh in, hard angle cuts get a slam
        c, s = tl.clips[i], tl.start_of(i)
        if c.get("speed", 1) != 1:
            cues += [cue(s, "whip", -14, dur=0.45, dir=1.0), cue(s + tl.frames(c) / FPS, "slam", -15)]
        elif c.get("settle"):
            cues.append(cue(s, "slam", -16))
cues += [cue(tFreeze - 0.5, "reverse_hit", -13, dur=0.5), cue(tFreeze, "boom", -7), cue(tFreeze + 0.05, "slam", -11), cue(tFreeze + 0.2, "mech", -15)]
cues += end_card_sfx(T)

music = make_music(P, {
    "bpm": 120, "key": "A", "mode": "minor", "style": "drive", "seed": 11,
    "sections": [
        {"type": "intro", "until": starts[0] - 1.0}, {"type": "build", "until": starts[0], "stop": True},
        {"type": "drop", "until": tFreeze}, {"type": "break", "until": starts[2]},
        {"type": "groove", "until": starts[3] - 1.0}, {"type": "build", "until": starts[3], "stop": True},
        {"type": "drop", "until": starts[6]}, {"type": "groove", "until": starts[7]},
        {"type": "drop", "until": T}, {"type": "outro", "until": T + END_DUR},
    ],
    "duration": T + END_DUR,
}, gain_db=-3)

write_edit(P, {
    "title": "OSM: leg day", "fps": FPS, "width": 1080, "height": 1920,
    "media": {"main": "source/original.mp4"},
    # no dialogue: the source track was music only; the edit is music + sound design
    "audio": {"main": "work/stems/original.silence.wav"},
    "plates": {"grade": GRADE, "sharpen": SHARPEN},
    # the old labels live in the bottom 12 %: a cinematic bottom fade, opaque from y 0.88 down
    "covers": [{"src": "main", "at": 5.4, "dur": 40.6, "box": [0.0, 0.78, 1.0, 1.0], "kind": "fade"}],
    "clips": tl.clips,
    "overlays": overlays,
    "shakes": [{"at": 0.0, "amp": 0.6}, {"at": starts[0], "amp": 0.6}, {"at": tFreeze, "amp": 1.0}, {"at": starts[3], "amp": 0.7},
               {"at": starts[7], "amp": 0.5}, {"at": T, "amp": 0.6}],
    "sfx": {"cues": cues},
    "music": music,
    "tail": END_DUR,
})
