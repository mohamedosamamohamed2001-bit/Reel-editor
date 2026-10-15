"""Marketing Reel 5 — "The scale isn't the whole story". His n3 take (his own voice): the scale alone doesn't tell the
truth -> you can lose fat and gain muscle at the same weight -> real progress = measurements and Before & After photos
(the app's Progress screen) -> his CTA, in sync."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_mkt"))
from promo import Promo  # noqa: E402

M = Promo(Path(__file__).resolve().parent, cap_top=0.70)
W, WR, Z = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "zoom", "flash": True}

a, b = M.span("n3", "متابعش", "بالميزان")  # the old export has a flash + scale tile baked in from 1.95 s: face only before it
M.talk("n3", a, b, focusY=0.40, zoom=(1.04, 1.1), tail=0.04)
a, b = 1.94, 3.86  # "بس. الميزان مش دايما بيحكي الحقيقة."
end = M.say("n3", a, b, at=M.t(), pad=0.0)
M.gym(1, "IMG_8386.MOV", 2.6, end - M.t(), zoom=(1.0, 1.08), focusY=0.40, tin={"type": "whip", "dir": "left"})
a, b = M.span("n3", "انت", "بتتطور")
t = M.t()
end = M.say("n3", a, b, at=t)
d = end - t
t1 = M.gym(2, "IMG_7537.MOV", 0.4, d * 0.36, zoom=(1.0, 1.06), tin=W, focusY=0.45)
t2 = M.gym(1, "IMG_8382.MOV", 0.3, d * 0.32, zoom=(1.0, 1.06), tin=WR, focusY=0.40)
M.gym(3, "IMG_8149.MOV", 2.0, end - M.t(), zoom=(1.0, 1.06), tin=W, focusY=0.42)
a, b = M.span("n3", "التطور", "After", nth_first=1)
t = M.t()
end = M.say("n3", a, b, at=t + 0.1)
M.app("progress", [(3.0, 2.2), (7.6, round(end - t + 0.1 - 2.2, 3))], tin=Z,
      highlights=[(0.6, 1.6, (0.02, 0.535, 0.96, 0.45))])
a, b = M.span("n3", "ولو", "بعض")
M.talk("n3", a, b, focusY=0.40, zoom=(1.0, 1.05), tin=WR)

M.finish("OSM promo 5: the scale isn't the whole story", keywords=["الميزان", "الحقيقة", "العضلات", "مقاسات", "Before", "After"],
         music={"style": "drive", "key": "A", "seed": 505, "gain": -9, "bpm": 120})
