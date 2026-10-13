#!/usr/bin/env python3
"""QA sweep of one horizontal band of a render, every Nth frame, tiled into sheets (to prove nothing old leaks).

    python3 tools/band_sweep.py VIDEO OUT_PREFIX [--band 0.5 0.95] [--every 5] [--cols 8]

Used on the collection re-edits to check that no burned-in caption from the old edit shows around the cover plates.
Each tile is labelled with its frame number; writes OUT_PREFIX_1.jpg, _2.jpg, ...
"""
import argparse
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("out")
ap.add_argument("--band", type=float, nargs=2, default=[0.5, 0.95])
ap.add_argument("--every", type=int, default=5)
ap.add_argument("--cols", type=int, default=8)
ap.add_argument("--rows", type=int, default=12)
ap.add_argument("--width", type=int, default=240)
a = ap.parse_args()
y0, y1 = a.band
vf = (f"select='not(mod(n\\,{a.every}))',crop=iw:ih*{y1 - y0:.3f}:0:ih*{y0:.3f},scale={a.width}:-2,"
      f"drawtext=text='%{{n}}':x=3:y=3:fontsize=12:fontcolor=yellow:box=1:boxcolor=black,"
      f"tile={a.cols}x{a.rows}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", vf, "-vsync", "vfr", f"{a.out}_%d.jpg"], check=True)
print("written", a.out + "_*.jpg")
