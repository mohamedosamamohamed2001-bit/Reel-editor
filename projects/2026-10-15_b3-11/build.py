"""Why do I feel my calves on the seated leg curl? (batch 3, video 11).

Seated leg curl -> calves working -> the movement = knee flexion -> the calf (gastrocnemius) also does knee flexion,
responsible for the first 0-15 degrees -> so sometimes you feel the calves -> that's normal -> comment what's next.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=24.5, focusY=0.45)
w = S.w

S.label(0.05, w("السمانة", near=1.9) - 0.05, "SEATED LEG CURL", eyebrow="ليه وانا بلعب", top=0.13)
S.icons(w("السمانة", near=1.9), w("وانا", near=2.6) - w("السمانة", near=1.9), [{"icon": "CircleHelp", "label": "السمانة اشتغلت؟"}], top=0.14, size=150)
S.label(w("لل"), w("السمانة", near=7.0) - w("لل"), "KNEE FLEXION", eyebrow="الحركة اسمها", top=0.13)
S.image("calf", w("السمانة", near=7.0), w("بس", near=10.1) - w("السمانة", near=7.0), mode="card", width=560, top=0.10, label="GASTROCNEMIUS")
S.title(w("من", near=11.2), w("فساعات") - w("من", near=11.2), [{"text": "0° → 15°", "accent": True, "size": 150}], eyebrow="المسؤوله عن", top=0.05)
S.icons(w("فساعات"), w("وده", near=18.2) - w("فساعات"), [{"icon": "Zap", "label": "السمانة شغاله"}], top=0.14, size=150)
S.badge(w("وده", near=18.2), w("اكتبلي") - w("وده", near=18.2), "✓", "ده عادي", top=0.14)
S.icons(w("اكتبلي"), S.T - w("اكتبلي"), [{"icon": "MessageCircle", "label": "الكومنت"}], top=0.14, size=150)

S.finish("OSM: calves on the seated leg curl", keywords=["السمانة", "knee", "flexion", "gastrocnemius", "15", "عادي"],
         cap_top=0.74, music={"style": "drive", "key": "A", "seed": 41})
