"""Tip 2: Goblet Squat, and the easier version (heels on a plate for more range when ankle mobility is limited). 21 s."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_tips"))
from common4 import Tip  # noqa: E402

S = Tip(Path(__file__).resolve().parent, focusY=0.45, zooms=((1.0, 1.05),))
w = S.w
S.punch(6.4, 9.6, zoom=(1.12, 1.15), focusY=0.35)
S.punch(15.2, 18.4, zoom=(1.12, 1.15), focusY=0.45)

S.title(0.1, w("بنزل") - 0.2, [{"text": "GOBLET", "size": 160}, {"text": "SQUAT", "accent": True, "size": 170}], eyebrow="OSM · LEGS", top=0.70)
S.icons(w("بنزل"), w("ولو") - w("بنزل"), [{"icon": "ArrowDown", "label": "للآخر"}, {"icon": "ArrowUp", "label": "وبطلع"}], top=0.74, size=120)
S.badge(w("ولو"), w("ممكن") - w("ولو"), "?", "مش عارف تنزل للآخر", top=0.72, side="right")
S.badge(w("ممكن"), w("إن", near=11.0) - w("ممكن"), "✓", "الحل أسهل", top=0.72, side="right")
S.image("weight_plate", w("نخلي"), w("هتساعدنا") - w("نخلي"), mode="card", width=560, top=0.52)
S.label(w("هتساعدنا"), w("عشان") - w("هتساعدنا"), "MORE RANGE", eyebrow="Range أكتر", top=0.72)
S.image("ankle", w("عشان"), w("فده") - w("عشان"), mode="full", push=[1.0, 1.06])
S.icons(w("فده"), S.T - w("فده"), [{"icon": "Footprints", "label": "Ankle Mobility"}, {"icon": "Check"}], top=0.72, size=120)

S.finish("OSM tip: Goblet Squat + heels on a plate", keywords=["goblet", "squat", "للآخر", "نسهل", "plate", "range", "mobility"],
         cap_top=0.80, music={"style": "drive", "key": "A", "seed": 42, "gain": -9})
