"""Lose fat and build muscle at the same time? (batch 3, video 7).

Hook (the myth) -> is it true? -> no, you can do both -> it depends on training and nutrition: training = more
intensity, nutrition = more calories, mostly protein -> keep the cardio -> muscle up, fat down -> description -> "Start".
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=33.3, focusY=0.35)
w = S.w

S.title(0.05, w("كتير") - 0.1, [{"text": "دهون ↓"}, {"text": "عضلات ↑", "accent": True}], eyebrow="في نفس الوقت؟", top=0.04)
S.icons(w("هل"), w("الكلام", near=6.3) - w("هل"), [{"icon": "CircleHelp", "label": "صح ولا لا؟"}], top=0.40, size=150)
S.badge(w("الكلام", near=6.3), w("انت", near=7.0) - w("الكلام", near=6.3), "✗", "Myth", top=0.14)
S.title(w("انت", near=7.0), w("متوقف") - w("انت", near=7.0), [{"text": "الاتنين", "accent": True, "size": 160}], eyebrow="ممكن تعمل", top=0.03, occlude=True)
S.icons(w("متوقف"), w("نظام", near=11.5) - w("متوقف"), [{"icon": "Dumbbell", "label": "التمرين"}, {"icon": "Utensils", "label": "التغذية"}], top=0.40, size=150)
S.label(w("نظام", near=11.5), w("انما") - w("نظام", near=11.5), "INTENSITY ↑", eyebrow="التمرين", top=0.13)
S.image("lifting", w("الشدة"), w("جسمك", near=13.9) - w("الشدة") + 0.2, mode="full", push=[1.04, 1.0])
S.label(w("انما"), w("ويبقى") - w("انما"), "CALORIES ↑", eyebrow="التغذية", top=0.13)
S.image("eggs", w("ويبقى"), w("عشان", near=20.0) - w("ويبقى") + 0.2, mode="full", push=[1.0, 1.05])
S.icons(w("البروتين"), w("وبالتالي") - w("البروتين"), [{"icon": "Egg", "label": "Protein"}, {"icon": "BicepsFlexed", "mark": "up"}], top=0.40, size=150)
S.image("treadmill", w("نستمر"), w("ده", near=23.8) - w("نستمر") + 0.1, mode="full", push=[1.05, 1.0])
S.icons(w("ده", near=23.8), w("عشان", near=25.3) - w("ده", near=23.8), [{"icon": "HeartPulse", "mark": "check", "label": "Cardio"}], top=0.40, size=150)
S.icons(w("هتزيد"), w("هتلاقيني") - w("هتزيد"), [{"icon": "BicepsFlexed", "mark": "up", "label": "عضلات"}, {"icon": "Flame", "mark": "down", "label": "دهون"}], top=0.40, size=150)
S.icons(w("هتلاقيني"), w("إكتب") - w("هتلاقيني"), [{"icon": "FileText", "label": "Description"}], top=0.40, size=150)
S.title(w("إكتب"), S.T - w("إكتب"), [{"text": "START", "accent": True, "size": 170}], eyebrow="اكتب كلمة", top=0.03, occlude=True)

S.finish("OSM: lose fat and build muscle together", keywords=["الاتنين", "التمرين", "التغذية", "الشدة", "calories", "البروتين", "الكارديو", "start"],
         cap_top=0.63, music={"style": "trap", "key": "F", "seed": 37})
