"""Batch 7 / 2 (IMG_3017, 19.8 s): Lateral Raises with dumbbells. Key rule: the ELBOW leads up, not the hand; the
elbow never stays under the hand; raise in one exact line, not to the side or too far forward. Approved OSM system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b7"))
from b7 import demo, lock  # noqa: E402

HERE = Path(__file__).resolve().parent
S = demo(HERE, end=19.75, focusY=0.42)
S.punch(4.5, 7.0)     # "عايز كوعي هو اللي بيطلع لفوق مش إيدي"
S.punch(11.3, 13.7, zoom=(1.12, 1.15))  # "وبطلع في الـLine ده كده بالظبط"
S.punch(17.1, 19.75)  # the rule again
w = S.w

S.title(0.1, w("أهم") - 0.15, [{"text": "LATERAL", "size": 130}, {"text": "RAISES", "accent": True, "size": 130}],
        eyebrow="OSM · TECHNIQUE", top=0.50)
S.title(w("أهم"), w("أنا", near=4.6) - w("أهم") - 0.05, [{"text": "أهم حاجة", "accent": True, "size": 120}], top=0.52, sfx="whoosh_in")
S.icons(w("كوعي", near=5.0), w("يعني") - w("كوعي", near=5.0) - 0.1,
        [{"icon": "BicepsFlexed", "mark": "up", "label": "الكوع لفوق"}, {"icon": "Hand", "mark": "x", "label": "مش الإيد"}], top=0.50, size=150)
S.badge(w("يعني"), w("لا") - w("يعني") - 0.05, "✗", "الكوع تحت الإيد", top=0.54, side="right")
S.badge(w("لا"), w("وبطلع", near=11.3) - w("لا") - 0.05, "✓", "العكس", top=0.54, side="right")
S.label(w("وبطلع", near=11.3), w("ومبطلعش") - w("وبطلع", near=11.3) - 0.05, "ONE LINE", eyebrow="في الـLine ده بالظبط", top=0.56)
S.icons(w("ومبطلعش"), w("أنا", near=17.1) - w("ومبطلعش") - 0.1,
        [{"icon": "ArrowLeftRight", "mark": "x", "label": "مش جنبك"}, {"icon": "MoveDiagonal2", "mark": "x", "label": "مش لقدام قوي"}], top=0.50, size=150)
S.icons(w("أنا", near=17.1), S.T - w("أنا", near=17.1) - 0.1, [{"icon": "Check", "label": "نفس الـLine"}], top=0.52, size=160)

S.finish("OSM technique: Lateral Raises", keywords=["Lateral", "Raises", "كوعي", "العكس", "Line", "بالظبط"], cap_top=0.74,
         music={"style": "drive", "key": "F", "seed": 702, "gain": -9}, replace={"الـLateral": "Lateral"})
lock(HERE, blue_shirt=True)
