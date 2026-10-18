"""Batch 7 / 4 (IMG_3019, 11.2 s): Dumbbell Shrugs. Hands at the sides, up and down; lift with the SHOULDERS, not the
elbows. The silent reps after his last word stay in. Approved OSM system (projects/_b7/b7.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b7"))
from b7 import demo, lock  # noqa: E402

HERE = Path(__file__).resolve().parent
S = demo(HERE, end=11.1, focusY=0.40)
S.punch(4.25, 7.6)    # "مش عايز أطلع بكوعي، أنا بطلع بكتافي"
S.punch(8.6, 11.1, zoom=(1.12, 1.15))
w = S.w

S.title(0.1, w("إيدي") - 0.1, [{"text": "SHRUGS", "size": 150}, {"text": "بالدمبل", "accent": True, "size": 96}],
        eyebrow="OSM · TECHNIQUE", top=0.50)
S.icons(w("إيدي"), w("بطلع") - w("إيدي") - 0.05, [{"icon": "Hand", "label": "إيدك جنبك"}], top=0.50, size=160)
S.icons(w("بطلع"), w("مش") - w("بطلع") - 0.1, [{"icon": "ArrowUp", "label": "اطلع"}, {"icon": "ArrowDown", "label": "انزل"}], top=0.50, size=150)
S.badge(w("مش"), w("أنا") - w("مش") - 0.05, "✗", "بكوعك", top=0.54, side="right")
S.badge(w("أنا"), w("وبنزل", near=7.0, end=True) + 0.2 - w("أنا"), "✓", "بكتافك لفوق", top=0.54, side="right")
t = w("وبنزل", near=7.0, end=True) + 0.4
S.icons(t, S.T - t - 0.1, [{"icon": "Hand", "label": "إيدك جنبك"}, {"icon": "ArrowUp", "label": "بكتافك"},
                           {"icon": "BicepsFlexed", "mark": "x", "label": "مش بكوعك"}], top=0.50, size=140)

S.finish("OSM technique: Dumbbell Shrugs", keywords=["Shrugs", "جنبي", "بكوعي", "بكتافي"], cap_top=0.74,
         music={"style": "drive", "key": "G", "seed": 704, "gain": -9}, replace={"الـShrugs": "Shrugs"})
lock(HERE, blue_shirt=True)
