"""Gym edit 3 (folder 3, black tee, dark neon gym): 'NO LIMITS'. 150 bpm phonk, 35.2 s + end card.

intro (8 beats): symmetric wide at the press -> the dip station stare -> close face  | build (8): cables, fast cuts, stop
drop 1 (32): dips, shoulder press, lateral raises, pushdowns - ramps on the best reps | break (8): deep dip in slow motion
build (8): fast cuts, stop                                                           | drop 2 (24): finish -> hero -> end card
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_gym"))
from montage import Montage  # noqa: E402

M = Montage(Path(__file__).resolve().parent, look="neon")
W, WR, WU = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "whip", "dir": "up"}
Z, ZP = {"type": "zoom", "flash": True}, {"type": "zoom"}

# ---- intro
M.drop(at=0.0, big=True)
M.shot("IMG_8158b.mov", 4, start=0.0, zoom=[1.0, 1.14], sfx=None)
M.shot("IMG_8157.MOV", 2, start=3.0, zoom=[1.02, 1.08], tin=W)
M.shot("IMG_8147.MOV", 2, start=26.3, zoom=[1.0, 1.06], tin=ZP)
# ---- build
b0 = M.t()
M.shot("IMG_8152.MOV", 2, zoom=[1.0, 1.06], tin=WR)
M.shot("IMG_8155.MOV", 2, zoom=[1.0, 1.06])
M.shot("IMG_8154.MOV", 1, zoom=[1.04, 1.08])
M.shot("IMG_8156.MOV", 1, zoom=[1.06, 1.1])
M.shot("IMG_8149.MOV", 1, zoom=[1.06, 1.1])
M.hold("IMG_8157.MOV", 4.8, 1, zoom=1.14)
M.title(b0 + 5 * 0.4, 3, [{"text": "NO", "size": 170}, {"text": "LIMITS", "accent": True, "size": 170}], top=0.72)
# ---- drop 1
d1 = M.t()
M.drop()
M.shot("IMG_8147.MOV", 4, kind="ramp", start=15.0, tin=Z, zoom=[1.0, 1.08])
M.shot("CCA8ED09.mp4", 4, start=10.0, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_8147.MOV", 4, kind="ramp", start=8.0, zoom=[1.02, 1.1], tin=WR)  # 9E93C5B9.mp4 = same take with burned-in text
M.shot("IMG_8153.MOV", 4, zoom=[1.04, 1.1], tin=ZP)
M.shot("7DD371A0.mp4", 4, kind="ramp", zoom=[1.0, 1.08], tin=WU)
M.shot("IMG_8152.MOV", 4, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_8151.MOV", 4, zoom=[1.02, 1.1], tin=WR)
M.shot("IMG_8148.MOV", 4, kind="ramp", zoom=[1.0, 1.06], tin=ZP)
M.beat_pulses(d1, 32)
# ---- break: a deep dip in slow motion
br = M.t()
M.shot("IMG_8147.MOV", 8, kind="slow", speed=0.5, start=20.0, zoom=[1.0, 1.1], tin={"type": "zoom", "flash": True},
       sfx=[{"sound": "boom", "gain_db": -12}, {"sound": "swell", "gain_db": -16}])
M.title(br + 1.2, 5, [{"text": "DISCIPLINE", "accent": True, "size": 120}], eyebrow="COACH OSAMA", top=0.72)
# ---- build 2
M.shot("IMG_8159.MOV", 2, start=9.0, zoom=[1.0, 1.08], tin=W)
M.shot("IMG_8156.MOV", 2, zoom=[1.04, 1.1], tin=WR)
M.shot("IMG_8154.MOV", 1, zoom=[1.05, 1.08])
M.shot("IMG_8155.MOV", 1, zoom=[1.05, 1.08])
M.shot("IMG_8149.MOV", 1, zoom=[1.1, 1.14])
M.hold("IMG_8152.MOV", 1.2, 1, zoom=1.12)
# ---- drop 2
d2 = M.t()
M.drop()
M.shot("IMG_8147.MOV", 4, kind="ramp", start=23.0, tin=Z, zoom=[1.0, 1.08])
M.shot("CCA8ED09.mp4", 4, zoom=[1.0, 1.08], tin=W)
M.shot("IMG_8153.MOV", 4, kind="ramp", zoom=[1.02, 1.08], tin=WR)
M.shot("7DD371A0.mp4", 4, zoom=[1.0, 1.06], tin=ZP)
M.shot("IMG_8157.MOV", 4, start=6.4, zoom=[1.0, 1.1], tin=WU)
M.shot("IMG_8158a.mov", 4, start=0.0, zoom=[1.0, 1.12], tin=W)
M.beat_pulses(d2, 24)

M.finish("OSM gym edit 3: NO LIMITS", {"bpm": 150, "key": "G", "mode": "minor", "style": "phonk", "seed": 13, "gain": -3,
                                      "riff": [0, 3, 0, 7, 0, 3, 8, 7, 0, 3, 0, 7, 12, 10, 8, 7],
                                      "sections": [{"type": "intro", "bars": 2}, {"type": "build", "bars": 2, "stop": True},
                                                   {"type": "drop", "bars": 8}, {"type": "break", "bars": 2},
                                                   {"type": "build", "bars": 2, "stop": True}, {"type": "drop", "bars": 6},
                                                   {"type": "outro", "bars": 2}]})
