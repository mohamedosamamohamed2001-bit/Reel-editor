"""Batch 7 / 1 (IMG_3006, 14.8 s): One Hand Row on the cable machine. He names it, leans slightly, pulls down and
goes back up; the silent reps after his last word stay in (a demo people watch). Approved OSM system (projects/_b7/b7.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b7"))
from b7 import demo, lock  # noqa: E402

HERE = Path(__file__).resolve().parent
S = demo(HERE, end=14.5, focusY=0.45)
S.punch(5.9, 8.9)     # "وبنزل وبطلع تاني لفوق": the movement itself
S.punch(11.4, 14.5, zoom=(1.12, 1.15))  # last reps
w = S.w

S.title(0.1, w("أنا") - 0.15, [{"text": "ONE HAND ROW", "accent": True, "size": 112}], eyebrow="OSM · TECHNIQUE", top=0.57)
S.label(w("بميل"), w("وبنزل") - w("بميل") - 0.1, "LEAN SLIGHTLY", eyebrow="ميل بجسمك حاجة بسيطة", top=0.56)
S.icons(w("وبنزل"), w("وبطلع") - w("وبنزل") - 0.05, [{"icon": "ArrowDown", "label": "انزل"}], top=0.52, size=160)
S.icons(w("وبطلع"), w("لفوق", end=True) + 0.3 - w("وبطلع"), [{"icon": "ArrowUp", "label": "اطلع لفوق"}], top=0.52, size=160)
t = w("لفوق", end=True) + 0.5
S.icons(t, S.T - t - 0.1, [{"icon": "MoveDiagonal2", "label": "ميل بسيط"}, {"icon": "ArrowDown", "label": "انزل"},
                           {"icon": "ArrowUp", "label": "اطلع لفوق"}], top=0.52, size=140)

S.finish("OSM technique: One Hand Row", keywords=["One", "Hand", "Row", "بميل", "وبنزل", "لفوق"], cap_top=0.74,
         music={"style": "drive", "key": "E", "seed": 701, "gain": -9}, replace={"الـOne": "One"})
lock(HERE, blue_shirt=True)
