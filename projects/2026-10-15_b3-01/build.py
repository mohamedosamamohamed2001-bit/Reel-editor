"""Pre-workout every day? (batch 3, video 1).

Hook (no speech, his close-up): PRE WORKOUT behind his head -> people who take it every day -> the body gets used to it,
you keep raising the dose (the worst mistake) -> caffeine very high -> bad for your heart -> why it exists: a heavy work
day / bad sleep -> real power -> max 3x a week -> follow -> end card.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=29.0, extra_holds=[(3.03, 3.66)])
w = S.w

S.title(0.15, w("الكلام") - 0.3, [{"text": "PRE"}, {"text": "WORKOUT", "accent": True}], eyebrow="كل يوم؟",
        top=0.04, occlude=True)
S.image("energy_drink", w("بتاخد"), w("كده") - w("بتاخد") + 0.1, mode="card", width=620, top=0.13)
S.icons(w("بيتعود"), w("فانت", near=7.8) - w("بيتعود"), [{"icon": "Repeat", "label": "بيتعود"}], top=0.16)
S.icons(w("تزود", near=9.1), w("ودي") - w("تزود", near=9.1), [{"icon": "Pill", "mark": "up", "label": "الجرعة"}], top=0.16)
S.badge(w("غلط", near=10.7) - 0.05, w("نسبة") - w("غلط", near=10.7), "✗", "غلط", top=0.15)
S.image("coffee_cup", w("نسبة") - 0.05, w("جدا") - w("نسبة") + 0.5, mode="card", width=560, top=0.12)
S.icons(w("عالية"), w("فانت", near=13.8) - w("عالية"), [{"icon": "Coffee", "mark": "up", "label": "Caffeine"}], top=0.36, size=140)
S.image("heart", w("بيكون", near=16.0) - 0.1, w("طب") - w("بيكون", near=16.0) + 0.1, mode="card", width=520, top=0.12,
        markers=[{"at": 0.35, "x": 0.5, "y": 0.45, "r": 0.12}])
S.title(w("طب"), w("بنستعمله") - w("طب"), [{"text": "ليه موجود؟", "accent": True, "size": 120}], eyebrow="PRE WORKOUT", top=0.12)
S.image("tired_desk", w("يوم", near=20.1) - 0.1, w("او", near=20.7) - w("يوم", near=20.1) + 0.1, mode="card", width=620, top=0.13)
S.icons(w("مش", near=21.1), w("فده") - w("مش", near=21.1), [{"icon": "Moon", "mark": "down", "label": "نوم"}], top=0.16)
S.icons(w("بيديك"), w("واخرك") - w("بيديك"), [{"icon": "Zap", "mark": "up", "label": "Power"}], top=0.16)
S.title(w("تلات"), w("اعملي") - w("تلات"), [{"text": "3×", "accent": True, "size": 200}, {"text": "في الاسبوع", "size": 90}],
        eyebrow="بس", top=0.10)
S.icons(w("اعملي"), w("واكبر") - w("اعملي"), [{"icon": "UserPlus", "label": "Follow"}], top=0.16)

S.finish("OSM: pre-workout every day?", keywords=["workout", "غلط", "الكافيين", "قلبك", "power", "تلات", "فولو"],
         cap_top=0.62, music={"style": "trap", "key": "E", "seed": 31})
