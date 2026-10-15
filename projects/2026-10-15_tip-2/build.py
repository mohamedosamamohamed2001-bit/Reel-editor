"""Tip 2: Goblet Squat, and the easier version (heels on a plate for more range when ankle mobility is limited). 21 s.
Full-body shot, he stands in the middle: captions on the floor (0.80), the title over his legs, graphics BESIDE him at
mid height (never above his head), punch-ins on the two key lines."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_tips"))
from common4 import Tip  # noqa: E402

S = Tip(Path(__file__).resolve().parent, focusY=0.42, zooms=((1.12, 1.16),))
w = S.w
S.punch(6.4, 9.6, zoom=(1.32, 1.36), focusY=0.30)
S.punch(15.2, 18.4, zoom=(1.32, 1.36), focusY=0.55)

S.title(0.1, w("بنزل") - 0.2, [{"text": "GOBLET", "size": 120}, {"text": "SQUAT", "accent": True, "size": 130}], eyebrow="OSM · LEGS", top=0.55)
S.icons(w("بنزل"), w("ولو") - w("بنزل"), [{"icon": "ArrowDown", "label": "للآخر"}], top=0.40, size=150, align="right")
S.badge(w("ولو"), w("ممكن") - w("ولو"), "?", "مش بتنزل للآخر", top=0.50, side="right")
S.badge(w("ممكن"), w("نخلي") - w("ممكن"), "✓", "الحل أسهل", top=0.50, side="right")
S.image("weight_plate", w("نخلي") + 0.4, w("هتساعدنا") - w("نخلي") - 0.4, mode="full", push=[1.0, 1.08])
S.label(w("هتساعدنا"), w("عشان") - w("هتساعدنا"), "MORE RANGE", eyebrow="Range أكتر", top=0.42)
S.icons(w("الـAnkle"), w("فده") - w("الـAnkle"), [{"icon": "Footprints", "label": "Ankle Mobility"}], top=0.36, size=150, align="right")
S.icons(w("فده"), S.T - w("فده"), [{"icon": "Check", "label": "بيحلها"}], top=0.42, size=150, align="right")

S.finish("OSM tip: Goblet Squat + heels on a plate", keywords=["goblet", "squat", "للآخر", "نسهل", "plate", "range", "mobility"],
         cap_top=0.80, music={"style": "drive", "key": "A", "seed": 42, "gain": -9})
