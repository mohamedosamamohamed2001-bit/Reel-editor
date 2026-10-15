"""How I lost weight, Part 1 (batch 3, video 8): calorie deficit.

Hook (how to lose weight; I went from this to this in 3 months) -> step 1: a calorie deficit -> know your daily
calories with a Calorie Calculator app (his screen recording stays) -> the key element -> everyone loves food,
but deficit = real fat loss -> other factors: wait for Part 2.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=23.0, focusY=0.38)
w = S.w

S.title(0.1, w("انا") - 0.15, [{"text": "PART 1", "accent": True, "size": 150}, {"text": "ازاي تخس"}], eyebrow="OSM · FAT LOSS", top=0.04, occlude=True)
S.icons(w("تلات"), w("وبعلمك") - w("تلات"), [{"icon": "CalendarDays", "value": "3", "label": "شهور بس"}], top=0.42, size=150)
S.badge(w("اول"), w("ولازم") - w("اول"), "1", "عجز في السعرات", top=0.42)
S.icons(w("Calories", near=8.8), w("عن") - w("Calories", near=8.8), [{"icon": "Flame", "label": "Calories / اليوم"}], top=0.42, size=150)
# old caption + blue box baked into his screen recording (10.6-13.0 s): the calculator cutaway covers it
S.image("calculator", w("عن") - 0.05, w("انا", near=15.7) - w("عن") + 0.05, mode="full", push=[1.0, 1.06])
S.title(w("ده", near=14.1), w("انا", near=15.7) - w("ده", near=14.1), [{"text": "العنصر الاساسي", "accent": True, "size": 110}], top=0.05, occlude=True)
S.image("pizza", w("بحب"), w("بس", near=18.1) - w("بحب"), mode="full", push=[1.05, 1.0])
S.title(w("بس", near=18.1), w("في", near=20.4) - w("بس", near=18.1), [{"text": "عجز", "accent": True, "size": 170}, {"text": "في السعرات", "size": 90}],
        top=0.04, occlude=True)
S.icons(w("في", near=20.4), S.T - w("في", near=20.4), [{"icon": "Hourglass", "label": "Part 2"}], top=0.42, size=150)

S.finish("OSM: how I lost weight, part 1", keywords=["تخس", "عجز", "السعرات", "calories", "calculator", "الاساسي"],
         cap_top=0.67, music={"style": "trap", "key": "G", "seed": 38})
