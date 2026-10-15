"""Gym edit 1 (folder 1, arm day, light-blue top): 'DON'T QUIT'. 150 bpm phonk, 35.2 s + end card.

intro (8 beats): the DON'T QUIT sign -> wide gym -> walking in       | build (8): hero shots, accelerating cuts, stop
drop 1 (32): curls, cable, rope, pulldown - ramps on the best reps    | break (8): 120 fps slow-motion pushdown
build (8): fast cuts, stop                                            | drop 2 (24): heavy finish -> hero -> end card
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_gym"))
from montage import Montage  # noqa: E402

M = Montage(Path(__file__).resolve().parent, look="steel")
W = {"type": "whip", "dir": "left"}
WR = {"type": "whip", "dir": "right"}
WU = {"type": "whip", "dir": "up"}
Z = {"type": "zoom", "flash": True}
ZP = {"type": "zoom"}

# ---- intro: grab in the first frame
M.drop(at=0.0, big=True)
M.shot("IMG_8404.MOV", 4, zoom=[1.0, 1.18], sfx=None)
M.shot("IMG_8388.MOV", 2, zoom=[1.05, 1.12], tin=W)
M.shot("IMG_8394.MOV", 2, start=0.0, zoom=[1.0, 1.08], tin=ZP)
# ---- build: hero shots, cuts accelerate into the stop
b0 = M.t()
M.shot("IMG_8386.MOV", 2, start=3.0, zoom=[1.0, 1.06], tin=WR)
M.shot("IMG_8387.MOV", 2, start=3.6, zoom=[1.04, 1.1])
M.shot("IMG_8384.MOV", 1, start=3.5, zoom=[1.08, 1.12])
M.shot("IMG_8385.MOV", 1, start=1.6, zoom=[1.1, 1.14])
M.shot("IMG_8381.MOV", 1, zoom=[1.0, 1.04])
M.hold("IMG_8385.MOV", 2.6, 1, zoom=1.16)  # the stop beat: freeze on the look up
M.title(b0 + 6 * 0.4, 2, [{"text": "ARM", "size": 190}, {"text": "DAY", "accent": True, "size": 190}], top=0.70)
# ---- drop 1
d1 = M.t()
M.drop()
M.shot("IMG_8398.MOV", 4, kind="ramp", tin=Z, zoom=[1.0, 1.08])
M.shot("IMG_8382.MOV", 4, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_8392.MOV", 4, kind="ramp", zoom=[1.02, 1.1], tin=WR)
M.shot("IMG_8397.MOV", 4, zoom=[1.04, 1.1], tin=ZP)
M.shot("IMG_8395.MOV", 4, kind="ramp", zoom=[1.0, 1.08], tin=WU)
M.shot("IMG_8399.MOV", 4, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_8390.MOV", 4, kind="ramp", zoom=[1.02, 1.1], tin=WR)
M.shot("IMG_8403.MOV", 4, zoom=[1.0, 1.06], tin=ZP)
M.beat_pulses(d1, 32)
# ---- break: real 120 fps slow motion
br = M.t()
M.shot("IMG_8396.MOV", 8, kind="slow", speed=0.25, zoom=[1.0, 1.1], tin={"type": "zoom", "flash": True},
       sfx=[{"sound": "boom", "gain_db": -12}, {"sound": "swell", "gain_db": -16}])
M.title(br + 1.2, 5, [{"text": "NO DAYS", "size": 130}, {"text": "OFF", "accent": True, "size": 170}], top=0.70)
# ---- build 2
M.shot("IMG_8400.MOV", 2, zoom=[1.0, 1.06], tin=W)
M.shot("IMG_8393.MOV", 2, zoom=[1.04, 1.1], tin=WR)
M.shot("IMG_8391.MOV", 1, zoom=[1.05, 1.08])
M.shot("IMG_8383.MOV", 1, zoom=[1.05, 1.08])
M.shot("IMG_8401.MOV", 1, zoom=[1.1, 1.14])
M.hold("IMG_8398.MOV", 1.3, 1, zoom=1.12)
# ---- drop 2
d2 = M.t()
M.drop()
M.shot("IMG_8381.MOV", 4, kind="ramp", tin=Z, zoom=[1.0, 1.08])
M.shot("IMG_8397.MOV", 4, kind="ramp", zoom=[1.0, 1.08], tin=W)
M.shot("IMG_8398.MOV", 4, kind="fast", speed=1.5, zoom=[1.02, 1.08], tin=WR)
M.shot("IMG_8390.MOV", 4, zoom=[1.0, 1.06], tin=ZP)
M.shot("IMG_8384.MOV", 4, start=0.8, zoom=[1.0, 1.1], tin=WU)
M.shot("IMG_8394.MOV", 4, start=2.0, zoom=[1.0, 1.1], tin=W)
M.beat_pulses(d2, 24)

M.finish("OSM gym edit 1: DON'T QUIT", {"bpm": 150, "key": "F", "mode": "minor", "style": "phonk", "seed": 5, "gain": -3,
                                       "sections": [{"type": "intro", "bars": 2}, {"type": "build", "bars": 2, "stop": True},
                                                    {"type": "drop", "bars": 8}, {"type": "break", "bars": 2},
                                                    {"type": "build", "bars": 2, "stop": True}, {"type": "drop", "bars": 6},
                                                    {"type": "outro", "bars": 2}]})
