"""Tip 3: Dead Bug, the common mistakes (58 s). The Arch is the mistake (compensating, not training the core); keep the
lower back flat on the floor, start one arm at a time, harder version later. He lies on the floor from 6.5 s: graphics
go in the empty upper half on the right, captions on the floor under him."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_tips"))
from common4 import Tip  # noqa: E402

S = Tip(Path(__file__).resolve().parent, pauses=[(4.0, 6.53), (13.83, 15.57), (49.49, 50.73)], focusY=0.5)
w = S.w
S.punch(18.8, 23.0, zoom=(1.1, 1.13), focusY=0.55)
S.punch(52.4, 58.5, zoom=(1.1, 1.13), focusY=0.55)
S.punch(30.9, 34.9, zoom=(1.1, 1.13), focusY=0.55)  # "أول ما تحس إن بطنك شغالة"
S.punch(39.6, 44.6, zoom=(1.1, 1.13), focusY=0.55)  # "وأهم حاجة ... ما يبقاش فيه أي Arch"

S.title(0.1, w("ده", near=6.5) - 0.15, [{"text": "غلط", "accent": True, "size": 170}, {"text": "شائع", "size": 110}],
        eyebrow="OSM · CORE", top=0.70)
S.title(w("Dead"), w("ده", near=8.7) - w("Dead"), [{"text": "DEAD", "size": 150}, {"text": "BUG", "accent": True, "size": 160}], top=0.14)
S.icons(w("إيدي"), w("وطبعا") - w("إيدي"), [{"icon": "Hand", "mark": "up", "label": "إيدك لفوق"}, {"icon": "Footprints", "label": "رجلك"}], top=0.14, size=150, align="right")
S.badge(w("الأخطاء", near=17.6), w("أول", near=18.8) - w("الأخطاء", near=17.6), "!", "الأخطاء", top=0.15, side="right")
S.badge(w("أول", near=19.6), w("الـArch") - w("أول", near=19.6), "1", "Arch", top=0.15, side="right")
S.image("back_pain", w("الـArch"), w("انت", near=23.2) - w("الـArch"), mode="full", push=[1.0, 1.06])
S.icons(w("انت", near=23.2), w("أهم", near=26.5) - w("انت", near=23.2), [{"icon": "Shuffle", "label": "Compensation"}, {"icon": "X", "label": "Core"}], top=0.14, size=150, align="right")
S.badge(w("أهم", near=26.5), w("فانت", near=30.9) - w("أهم", near=26.5), "✓", "No Arch = Core", top=0.15, side="right")
S.icons(w("فانت", near=30.9), w("ونبدأ") - w("فانت", near=30.9), [{"icon": "Flame", "label": "بطنك شغالة"}, {"icon": "Check"}], top=0.14, size=150, align="right")
S.label(w("ونبدأ"), w("وأهم") - w("ونبدأ"), "ONE BY ONE", eyebrow="واحدة واحدة", top=0.15)
S.badge(w("وأهم"), w("ونرجع") - w("وأهم"), "✗", "No Arch", top=0.15, side="right")
S.icons(w("لو", near=46.1), w("أهم", near=52.4) - w("لو", near=46.1), [{"icon": "TrendingUp", "label": "صعّبها"}], top=0.14, size=160, align="right")
S.title(w("أهم", near=52.4), w("وضهرك") - w("أهم", near=52.4), [{"text": "NO ARCH", "accent": True, "size": 150}], top=0.14)
S.icons(w("وضهرك"), S.T - w("وضهرك"), [{"icon": "Minus", "label": "ضهرك Flat"}, {"icon": "Check"}], top=0.14, size=150, align="right")

S.finish("OSM tip: Dead Bug mistakes", keywords=["غلط", "dead", "arch", "core", "تمام", "واحدة", "flat"],
         cap_top=0.80, zones=[{"at": 0, "dur": 6.0, "top": 0.74}], music={"style": "drive", "key": "D", "seed": 43, "gain": -9},
         replace={"بتكومبنسيت": "بتكومبنسيت"})
