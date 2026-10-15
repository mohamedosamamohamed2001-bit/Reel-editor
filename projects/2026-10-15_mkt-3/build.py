"""Marketing Reel 3 — "Swap it" (music-led, no voice-over). Real food footage (free non-AI Coverr clips) and the
real diet screen: chicken -> Swap (9) -> the app's own alternatives at the same 120 g (shrimps, tilapia, lean steak)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_mkt"))
from promo import Promo  # noqa: E402

M = Promo(Path(__file__).resolve().parent)
W, WR, Z = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "zoom", "flash": True}

t = M.stock("coverr-chicken-skewer-1416", 4.0, 2.0, zoom=(1.0, 1.1), focusX=0.62)
M.title(t + 0.1, 1.85, [{"text": "زهقت من", "size": 100}, {"text": "الفراخ؟", "accent": True, "size": 130}], top=0.60)
# the real diet plan: Chicken Breast (Cooked) · 120 Gram -> Swap (9)
t = M.app("diet", [(8.0, 3.5)], region=(0.0, 0.16, 1.0, 0.72), tin=Z,
          highlights=[(0.3, 1.3, (0.03, 0.42, 0.94, 0.10))])
M.title(t + 1.5, 1.9, [{"text": "بدّلها", "accent": True, "size": 120}], top=0.80, sfx="whoosh_in")
# the alternatives the app lists for it, same 120 g, cooked
for name, a, label, fx in [("coverr-shrimps-on-the-barbecue-2876", 6.0, "Shrimps · 120 Gram", 0.5),
                           ("coverr-squeezing-lemon-on-fish-1227", 3.0, "Fish · 120 Gram", 0.5),
                           ("coverr-grilled-steak-8580", 2.0, "Lean Steak · 120 Gram", 0.4)]:
    t = M.stock(name, a, 1.35, zoom=(1.05, 1.14), focusX=fx, tin=W if label[0] != "F" else WR)
    M.label(t + 0.1, 1.2, label, eyebrow="بديل · Cooked", top=0.66)
t = M.app("diet", [(10.6, 3.0)], region=(0.0, 0.16, 1.0, 0.72), tin=Z, entrance="flat")
M.label(t + 0.2, 2.7, "بدائل جاهزة في خطتك", eyebrow="DIET · SWAP", top=0.80)
t = M.stock("coverr-grilled-chicken-and-potatoes-1400", 3.0, 2.0, zoom=(1.0, 1.08), tin=WR)
M.title(t + 0.1, 1.85, [{"text": "بدّل", "size": 120}, {"text": "والخطة ماشية", "accent": True, "size": 92}], top=0.60)

M.finish("OSM promo 3: swap it", keywords=[], voice_led=False,
         music={"style": "trap", "key": "G", "seed": 303, "gain": -5, "bpm": 140})
