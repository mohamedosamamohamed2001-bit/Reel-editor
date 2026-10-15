"""Gym edit 2 (folder 2, black tank, daylight industrial gym): 'BUILT NOT BORN'. 150 bpm phonk, 35.2 s + end card.

intro (8 beats): silhouettes against the window -> hands on hips   | build (8): 30 kg dumbbells off the rack, fast cuts, stop
drop 1 (32): rows, EZ curls, incline press, cable rows - ramps     | break (8): backlit silhouette in slow motion
build (8): fast cuts, flex, stop                                  | drop 2 (24): heavy finish -> double biceps -> end card
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_gym"))
from montage import Montage  # noqa: E402

M = Montage(Path(__file__).resolve().parent, look="grit")
W, WR, WU = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "whip", "dir": "up"}
Z, ZP = {"type": "zoom", "flash": True}, {"type": "zoom"}

# ---- intro
M.drop(at=0.0, big=True)
M.shot("IMG_7550.MOV", 4, start=0.2, zoom=[1.0, 1.12], sfx=None)
M.shot("IMG_7551.MOV", 2, start=3.2, zoom=[1.04, 1.1], tin=W)
M.shot("IMG_7549.MOV", 2, start=2.8, zoom=[1.02, 1.08], tin=ZP)
# ---- build
b0 = M.t()
M.shot("IMG_7545.MOV", 2, zoom=[1.0, 1.06], tin=WR)
M.shot("IMG_7558.MOV", 2, zoom=[1.0, 1.06])
M.shot("IMG_7534.MOV", 1, start=1.4, zoom=[1.04, 1.08])
M.shot("IMG_7552.MOV", 1, start=2.4, zoom=[1.06, 1.1])
M.shot("IMG_7548.MOV", 1, start=6.0, zoom=[1.06, 1.1])
M.hold("IMG_7549.MOV", 3.9, 1, zoom=1.14)
M.title(b0 + 5 * 0.4, 3, [{"text": "BUILT", "size": 180}, {"text": "NOT BORN", "accent": True, "size": 130}], top=0.70)
# ---- drop 1
d1 = M.t()
M.drop()
M.shot("IMG_7539.MOV", 4, kind="ramp", start=6.0, tin=Z, zoom=[1.0, 1.08])
M.shot("IMG_7531.MOV", 4, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_7560.MOV", 4, kind="ramp", zoom=[1.02, 1.1], tin=WR)
M.shot("IMG_7563.MOV", 4, zoom=[1.04, 1.1], tin=ZP)
M.shot("IMG_7538.MOV", 4, kind="ramp", zoom=[1.0, 1.08], tin=WU)
M.shot("IMG_7543.MOV", 4, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_7561.MOV", 4, kind="ramp", start=8.0, zoom=[1.02, 1.1], tin=WR)
M.shot("IMG_7532.MOV", 4, zoom=[1.0, 1.06], tin=ZP)
M.beat_pulses(d1, 32)
# ---- break: backlit silhouette, slow motion
br = M.t()
M.shot("IMG_7547.MOV", 8, kind="slow", speed=0.5, start=8.6, zoom=[1.0, 1.1], tin={"type": "zoom", "flash": True},
       sfx=[{"sound": "boom", "gain_db": -12}, {"sound": "swell", "gain_db": -16}])
M.title(br + 1.2, 5, [{"text": "NO", "size": 150}, {"text": "SHORTCUTS", "accent": True, "size": 140}], top=0.70)
# ---- build 2
M.shot("IMG_7559.MOV", 2, start=7.4, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_7536.MOV", 2, zoom=[1.04, 1.1], tin=WR)
M.shot("IMG_7564.MOV", 1, zoom=[1.05, 1.08])
M.shot("IMG_7533.MOV", 1, zoom=[1.05, 1.08])
M.shot("IMG_7544.MOV", 1, zoom=[1.1, 1.14])
M.hold("IMG_7542.MOV", 4.0, 1, zoom=1.12)
# ---- drop 2
d2 = M.t()
M.drop()
M.shot("IMG_7537.MOV", 4, kind="ramp", tin=Z, zoom=[1.0, 1.08])
M.shot("IMG_7560.MOV", 4, zoom=[1.0, 1.08], tin=W)
M.shot("IMG_7562.MOV", 4, kind="ramp", start=3.0, zoom=[1.02, 1.08], tin=WR)
M.shot("IMG_7546.MOV", 4, start=2.6, zoom=[1.0, 1.06], tin=ZP)
M.shot("IMG_7565.MOV", 4, start=11.0, zoom=[1.0, 1.1], tin=WU)
M.shot("IMG_7539.MOV", 4, start=13.4, zoom=[1.0, 1.1], tin=W)
M.beat_pulses(d2, 24)

M.finish("OSM gym edit 2: BUILT NOT BORN", {"bpm": 150, "key": "D", "mode": "minor", "style": "phonk", "seed": 9, "gain": -3,
                                           "riff": [0, 0, 7, 0, 5, 0, 3, 2, 0, 0, 7, 0, 10, 7, 5, 3],
                                           "sections": [{"type": "intro", "bars": 2}, {"type": "build", "bars": 2, "stop": True},
                                                        {"type": "drop", "bars": 8}, {"type": "break", "bars": 2},
                                                        {"type": "build", "bars": 2, "stop": True}, {"type": "drop", "bars": 6},
                                                        {"type": "outro", "bars": 2}]})
