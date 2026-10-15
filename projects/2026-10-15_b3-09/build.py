"""Biceps curl vs hammer curl (batch 3, video 9).

Hook: this is different from this -> the biceps does 2 actions: supination + elbow flexion -> supinated grip = biceps
-> mid-prone grip = brachioradialis (the "hammer" muscle) -> now you know the difference. His own demos carry it;
anatomy plate: Bourgery & Jacob pl. 103 (public domain), labelled without markers (no mislabelled muscle heads).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=25.0, focusY=0.35)
w = S.w

S.title(0.05, w("ال", near=2.0) - 0.1, [{"text": "BICEPS"}, {"text": "VS HAMMER", "accent": True, "size": 120}], eyebrow="مختلفة؟", top=0.03, occlude=True)
S.image("arm103", w("Biceps", near=2.2) - 0.1, w("بتعمل", near=3.9) - w("Biceps", near=2.2) + 0.1, mode="full", label="BICEPS", push=[1.05, 1.0])
S.icons(w("2"), w("بتعمل", near=3.9) - w("2"), [{"icon": "Repeat", "value": "2", "label": "actions"}], top=0.40, size=150)
S.checklist(w("بتعمل", near=3.9), w("فالوضع") - w("بتعمل", near=3.9),
            [{"at": 0.0, "text": "SUPINATION"}, {"at": w("وبتعمل") - w("بتعمل", near=3.9), "text": "ELBOW FLEXION"}], top=0.13)
S.label(w("فالوضع"), w("فانا", near=10.8) - w("فالوضع"), "SUPINATION", eyebrow="الوضع ده", top=0.13)
S.badge(w("فانا", near=10.8), w("الوضع", near=13.0) - w("فانا", near=10.8), "✓", "Biceps", top=0.14)
S.label(w("الوضع", near=13.0), w("فانا", near=14.7) - w("الوضع", near=13.0), "MID PRONE", eyebrow="الوضع ده", top=0.13)
# full cutaway: also hides the old edit's picture sticker (15.9-17.5 s), emptied by the caption eraser
S.image("arm103", w("عضلة", near=15.4) - 0.1, w("يعني", near=17.1) - w("عضلة", near=15.4) + 0.55, mode="full", label="BRACHIORADIALIS", push=[1.0, 1.05])
S.title(w("Hammer"), w("كده", near=22.0) - w("Hammer"), [{"text": "HAMMER", "accent": True, "size": 150}], eyebrow="عضلة ال", top=0.03, occlude=True)
S.title(w("كده", near=22.0), S.T - w("كده", near=22.0), [{"text": "الفرق", "accent": True, "size": 160}], eyebrow="كده انت عرفت", top=0.03, occlude=True)

S.finish("OSM: biceps vs hammer curl", keywords=["biceps", "actions", "supination", "flexion", "prone", "brachioradialis", "hammer", "الفرق"],
         cap_top=0.70, music={"style": "drive", "key": "B", "seed": 39})
