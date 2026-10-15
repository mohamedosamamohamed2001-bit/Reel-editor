"""Marketing Reel 6 — "Calorie Calculator". His calorie-calculator take (his own voice) + the real calculator in the
app: typing age / height / weight, then the three targets (Shred / Maintain / Lean bulk) lit as he says them."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_mkt"))
from promo import Promo  # noqa: E402

M = Promo(Path(__file__).resolve().parent, cap_top=0.70)
W, WR, Z = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "zoom", "flash": True}

t = M.gym(2, "IMG_7538.MOV", 1.0, 1.7, zoom=(1.0, 1.08), focusY=0.45)
M.title(t + 0.1, 1.55, [{"text": "جسمك محتاج", "size": 96}, {"text": "كام Calorie؟", "accent": True, "size": 110}], top=0.66)
a, b = M.span("cal", "وانا", "Calculator")
M.talk("cal", a, b, focusY=0.40, zoom=(1.0, 1.04), tin=Z)
a, b = M.span("cal", "ادخل", "بياناتك", nth_first=1)
t = M.t()
end = M.say("cal", a, b, at=t + 0.1)
M.app("calculator", [(3.1, round(end - t + 0.1, 3))], tin=WR)
a, b = M.span("cal", "وهتعرف", "وزنك")
t = M.t()
end = M.say("cal", a, b, at=t)
M.app("calculator", [(14.2, round(end - t + 0.25, 3))], tin=None, entrance="flat", sfx=False)
M.finish("OSM promo 6: calorie calculator", keywords=["Calories", "Calculator", "free", "جسمك"],
         music={"style": "drive", "key": "C", "seed": 606, "gain": -9, "bpm": 124})
