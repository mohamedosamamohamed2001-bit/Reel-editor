"""No decline press machine? Two alternatives (batch 3, video 6).

Hook (no machine decline press / decline bench) -> save it -> alternative 1 on the cable (his demo) -> why not the
decline bench: lying like that, no support, no safety -> the safer alternative -> alternative 2 (his demo), focus on
his form -> that's the start -> save + more videos coming.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=26.95, focusY=0.35)
w = S.w

S.title(0.1, w("بس", near=2.5) - 0.1, [{"text": "DECLINE"}, {"text": "PRESS", "accent": True}], eyebrow="مفيش مكنة؟", top=0.03, occlude=True)
S.icons(w("Save", near=3.3), w("في", near=5.0) - w("Save", near=3.3), [{"icon": "Bookmark", "label": "Save"}], top=0.40, size=150)
S.label(w("بديل", near=6.1), w("مش", near=9.3) - w("بديل", near=6.1), "CABLE", eyebrow="البديل 01", top=0.13)
S.image("decline_bench", w("مش", near=9.3), w("انت", near=10.1) - w("مش", near=9.3) + 0.3, mode="full", push=[1.0, 1.06])
S.badge(w("مش", near=9.3), w("نايم") - w("مش", near=9.3), "✗", "Decline Bench", top=0.14)
S.icons(w("وما"), w("الامن") - w("وما"), [{"icon": "ShieldOff", "mark": "x", "label": "Support"}, {"icon": "TriangleAlert", "label": "امان"}], top=0.14, size=150)
S.badge(w("الامن"), w("وده", near=15.3) - w("الامن"), "✓", "الامن ليك", top=0.14)
S.label(w("تاني", near=15.6), w("دي", near=20.7) - w("تاني", near=15.6), "CHEST DIPS", eyebrow="البديل 02", top=0.13)
S.icons(w("ركز"), w("دي", near=20.7) - w("ركز"), [{"icon": "Eye", "label": "ركز على الاداء"}], top=0.40, size=140)
S.title(w("دي", near=20.7), w("اعمل", near=23.9) - w("دي", near=20.7), [{"text": "MACHINE"}, {"text": "DECLINE PRESS", "accent": True, "size": 110}],
        eyebrow="دي كده البداية", top=0.03, occlude=True)
S.icons(w("اعمل", near=23.9), S.T - w("اعمل", near=23.9), [{"icon": "Bookmark", "label": "Save"}, {"icon": "Play", "label": "الفيديوز الجاية"}], top=0.40, size=140)

S.finish("OSM: decline press alternatives", keywords=["decline", "press", "save", "support", "امان", "الاداء"],
         cap_top=0.68, music={"style": "trap", "key": "C", "seed": 36})
