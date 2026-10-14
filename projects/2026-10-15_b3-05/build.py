"""How I lost weight, Part 2 (batch 3, video 5): resistance training + cardio.

Hook (Part 2) -> 3 months -> focus on resistance training: 5 days a week, Push Pull Legs Upper -> cardio every day,
30 min = 150 min a week -> other factors: wait for Part 3.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=20.4, focusY=0.38)
w = S.w

S.title(0.1, w("انا") - 0.15, [{"text": "PART 2", "accent": True, "size": 150}, {"text": "ازاي تخس"}], eyebrow="OSM · FAT LOSS", top=0.04, occlude=True)
S.icons(w("تلات"), w("وبعلمك") - w("تلات"), [{"icon": "CalendarDays", "value": "3", "label": "شهور بس"}], top=0.42, size=150)
S.badge(w("لازم"), w("انا", near=7.5) - w("لازم"), "1", "تمرين المقاومة", top=0.42)
S.image("gym_weights", w("تمرين"), w("انا", near=7.5) - w("تمرين") + 0.1, mode="full", push=[1.0, 1.06])
S.icons(w("خمس"), w("Push") - w("خمس"), [{"icon": "CalendarDays", "value": "5", "label": "ايام في الاسبوع"}], top=0.42, size=150)
S.checklist(w("Push"), w("وطبعا") - w("Push"), [{"at": 0.0, "text": "PUSH"}, {"at": w("Pull") - w("Push"), "text": "PULL"},
            {"at": w("Legs") - w("Push"), "text": "LEGS"}, {"at": w("upper") - w("Push"), "text": "UPPER"}], top=0.13)
S.badge(w("بالكارديو"), w("كل", near=14.7) - w("بالكارديو"), "2", "الكارديو", top=0.42)
S.image("treadmill", w("بالكارديو") + 0.2, w("كل", near=14.7) - w("بالكارديو") - 0.2, mode="full", push=[1.05, 1.0])
S.icons(w("كل", near=14.7), w("150") - w("كل", near=14.7), [{"icon": "Timer", "value": "30", "label": "دقيقة كل يوم"}], top=0.42, size=150)
S.title(w("150"), w("في", near=17.9) - w("150") + 0.05, [{"text": "150", "accent": True, "size": 200}, {"text": "دقيقة في الاسبوع", "size": 80}],
        top=0.03, occlude=True)
S.icons(w("في", near=17.9), S.T - w("في", near=17.9), [{"icon": "Hourglass", "label": "Part 3"}], top=0.42, size=150)

S.finish("OSM: how I lost weight, part 2", keywords=["تخس", "المقاومة", "push", "pull", "legs", "upper", "بالكارديو", "30", "150"],
         cap_top=0.67, music={"style": "drive", "key": "G", "seed": 35})
