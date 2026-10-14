"""Your weight isn't moving (batch 3, video 3).

Hook: diet and training on point, weight stuck -> reason 1: more calories than your body needs to lose ->
reason 2: resistance + cardio = fat down, muscle up, same weight (you ARE progressing) -> reason 3: bad sleep,
work pressure, stress -> cortisol up -> water retention -> slows progress -> more in the description -> "جاهز" CTA.
His head fills the top third in the close shot: titles sit BEHIND his head (occlude), icons on the hoodie,
pictures as full-screen cutaways (a card would cover his face).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=35.05, focusY=0.35)
w = S.w

S.title(0.1, w("تعالى") - 0.15, [{"text": "وزنك ثابت؟", "accent": True, "size": 130}], eyebrow="OSM · FAT LOSS", top=0.05)
S.icons(w("ضابط"), w("تعالى") - 0.1, [{"icon": "Utensils", "mark": "check"}, {"icon": "Dumbbell", "mark": "check"},
                                         {"icon": "Weight", "label": "ثابت"}], top=0.36, size=130)
S.title(w("تعالى"), w("لو", near=3.2) - w("تعالى"), [{"text": "3 اسباب", "accent": True, "size": 140}], top=0.03, occlude=True)
S.badge(w("لو", near=3.2), w("سعرات") - w("لو", near=3.2), "1", "سعرات زيادة", top=0.38)
S.image("fast_food", w("سعرات") - 0.05, w("فانت", near=7.5) - w("سعرات"), mode="full", push=[1.0, 1.06])
S.icons(w("بالتالي", near=8.0), w("تاني") - w("بالتالي", near=8.0), [{"icon": "Weight", "label": "ثابت"}], top=0.38, size=150)
S.badge(w("تاني"), w("تمارين") - w("تاني"), "2", "مقاومة + كارديو", top=0.38)
S.image("lifting", w("تمارين"), w("مع", near=11.5) - w("تمارين") + 0.05, mode="full", push=[1.04, 1.0])
S.image("cardio_run", w("مع", near=11.5) + 0.05, w("فانت", near=12.0) - w("مع", near=11.5) + 0.2, mode="full", push=[1.0, 1.05])
S.icons(w("عشان", near=13.6), w("ده", near=16.0) - w("عشان", near=13.6),
        [{"icon": "Flame", "mark": "down", "label": "دهون"}, {"icon": "BicepsFlexed", "mark": "up", "label": "عضلات"}], top=0.36, size=150)
S.title(w("لا", near=17.8), w("تالت") - w("لا", near=17.8), [{"text": "بتتطور", "accent": True, "size": 150}],
        eyebrow="انت كده", top=0.03, occlude=True)
S.badge(w("تالت"), w("نومك") - w("تالت"), "3", "النوم والاسترس", top=0.38)
S.icons(w("نومك"), w("طاقة") - w("نومك"), [{"icon": "Moon", "mark": "x", "label": "نومك بايظ"}], top=0.38, size=150)
S.image("tired_desk", w("طاقة"), w("بيعلي") - w("طاقة"), mode="full", push=[1.0, 1.05])
S.label(w("بيعلي"), w("فده", near=25.2) - w("بيعلي"), "CORTISOL ↑", eyebrow="هرمون", top=0.38)
S.icons(w("احتباس"), w("وده", near=27.4) - w("احتباس"), [{"icon": "Droplets", "label": "احتباس السوايل"}], top=0.38, size=150)
S.icons(w("هياخر"), w("وفي") - w("هياخر"), [{"icon": "Hourglass", "label": "التقدم"}], top=0.38, size=150)
S.icons(w("هاكتبهالكو"), w("ولو", near=31.1) - w("هاكتبهالكو"), [{"icon": "FileText", "label": "Description"}], top=0.38, size=150)
S.title(w("ابعتلي"), S.T - w("ابعتلي"), [{"text": "جاهز", "accent": True, "size": 170}], eyebrow="ابعتلي كلمة", top=0.03, occlude=True)

S.finish("OSM: your weight isn't moving", keywords=["ثابت", "سعرات", "مقاومة", "الدهون", "العضلات", "بتتطور", "الكورتيزون", "description", "جاهز"],
         cap_top=0.64, music={"style": "drive", "key": "A", "seed": 33})
