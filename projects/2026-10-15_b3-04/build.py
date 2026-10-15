"""How to read your InBody (batch 3, video 4, 96 s).

Hook (InBody is useless if you can't read it) -> in order: Total Body Water (muscle is 70% water) -> protein,
minerals -> Body Fat Mass (kg) -> Weight -> SMM -> Body Fat Mass -> PBF (%) -> the two segmental charts
(each arm, abs, each leg; fix a weak side) -> InBody Score, Weight Target / Control -> BMR 1383 is NOT your burn:
add the activity level -> don't eat at BMR. His InBody-sheet shots stay (his own content); labels name each value.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=95.75, focusY=0.4)
w = S.w
L = lambda word, near, until, title, eyebrow=None: S.label(w(word, near=near), until - w(word, near=near), title, eyebrow=eyebrow, top=0.13)

# the old edit's hook title sits on his face (can't be erased without touching it): full-frame OSM title card
# until the first cut (2.93 s) while he speaks; captions stay on top
S.title(0.0, S.o(2.93), [{"text": "INBODY", "size": 190}, {"text": "مالوش لازمة؟", "accent": True, "size": 120}],
        eyebrow="OSM · INBODY", top=0.30, backdrop=True)
S.icons(w("تعال"), w("اول") - w("تعال"), [{"icon": "ListOrdered", "label": "بالترتيب"}], top=0.14, size=150)
L("Total", 5.8, w("وملحوظة"), "TOTAL BODY WATER", "01")
S.icons(w("ممكن", near=9.3), w("بعد", near=14.2) - w("ممكن", near=9.3),
        [{"icon": "Droplets", "label": "مايه"}, {"icon": "BicepsFlexed", "value": "70%", "label": "العضلات"}], top=0.13, size=150)
L("البروتين", 14.7, w("في", near=15.2), "PROTEIN", "02")
L("Minerals", 15.4, w("في", near=16.7), "MINERALS", "المعادن")
L("Body", 16.7, w("بعد", near=20.4), "BODY FAT MASS", "وزن الدهون · KG")
L("Weight", 20.8, w("ال", near=24.1), "WEIGHT", "وزنك")
L("SMM", 24.3, w("وبعدها"), "SMM", "كتلة العضلات")
L("Body", 26.8, w("بعد", near=29.8), "BODY FAT MASS", "كتلة الدهون · KG")
S.icons(w("PBF"), w("بيكون", near=35.9) - w("PBF"), [{"icon": "Percent", "label": "PBF · نسبة الدهون"}], top=0.13, size=150)
S.title(w("رسمتين"), w("بيشرحوا") - w("رسمتين") + 0.05, [{"text": "رسمتين مهمين", "accent": True, "size": 110}], top=0.05, occlude=True)
S.icons(w("بيشرحوا"), w("يعني", near=41.1) - w("بيشرحوا"),
        [{"icon": "BicepsFlexed", "label": "العضلات"}, {"icon": "Flame", "label": "الدهون"}], top=0.13, size=150)
S.badge(w("نفس", near=51.7), w("بس", near=53.3) - w("نفس", near=51.7), "=", "نفس الفكرة في الدهون", top=0.14)
S.icons(w("مختلفة"), w("ابدا") - w("مختلفة"), [{"icon": "Scale", "mark": "x", "label": "يمين ≠ شمال"}], top=0.13, size=150)
S.icons(w("ابدا"), w("بعد", near=61.1) - w("ابدا"), [{"icon": "Scale", "mark": "check", "label": "يمين = شمال"}], top=0.13, size=150)
L("InBody", 63.2, w("تحتها"), "INBODY SCORE", "03")
S.icons(w("Target"), w("فاخر") - w("Target"),
        [{"icon": "Target", "label": "Weight Target"}, {"icon": "Flame", "mark": "down", "label": "الدهون"}], top=0.13, size=140)
S.title(w("BMR"), w("ده", near=80.8) - w("BMR"), [{"text": "BMR"}, {"text": "1383", "accent": True, "size": 150}], top=0.05, occlude=True)
S.badge(w("مش", near=81.1), w("ده", near=82.3) - w("مش", near=81.1), "✗", "مش معدل الحرق", top=0.14)
S.icons(w("لو", near=83.6), w("فالرقم") - w("لو", near=83.6), [{"icon": "BedDouble", "label": "من غير مجهود"}], top=0.13, size=150)
S.icons(w("بنزود"), w("فمش") - w("بنزود"),
        [{"icon": "Calculator", "value": "BMR"}, {"icon": "Plus"}, {"icon": "Activity", "label": "Activity Level"}], top=0.13, size=130)
S.badge(w("ينفعش"), S.T - w("ينفعش"), "✗", "مش سعراتك الاساسية", top=0.14)

S.finish("OSM: how to read your InBody",
         keywords=["inbody", "water", "70%", "mass", "smm", "pbf", "رسمتين", "score", "bmr", "1383", "activity"],
         cap_top=0.66, music={"style": "drive", "key": "D", "seed": 34, "gain": -10})
