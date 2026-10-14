"""Gym cardio isn't the only cardio (batch 3, video 10).

Hook (ping pong): gym cardio isn't a must -> you don't have to walk the treadmill, ride the bike, climb the
stairmaster -> ping pong, padel or football with friends = your daily cardio -> it doesn't mean skip gym cardio:
do cardio any way you like -> tell me in the comments what's next.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=19.6, start=1.1, focusY=0.35)
w = S.w

S.title(0.05, w("يعني", near=3.1) - 0.1, [{"text": "CARDIO"}, {"text": "في الجيم؟", "accent": True, "size": 120}], eyebrow="ما لوش لازمة", top=0.04)
S.badge(w("treadmill") - 0.3, w("مش", near=5.4) - w("treadmill") + 0.3, "✗", "Treadmill", top=0.14)
S.badge(w("Bike"), w("مش", near=6.6) - w("Bike"), "✗", "Bike", top=0.14)
S.badge(w("stairmaster"), w("لو", near=8.9) - w("stairmaster"), "✗", "Stairmaster", top=0.14)
S.image("pingpong", w("ping"), w("Padel") - w("ping") + 0.05, mode="full", push=[1.0, 1.06])
S.image("padel", w("Padel"), w("كورة") - w("Padel"), mode="full", push=[1.05, 1.0])
S.icons(w("كورة"), w("فانت", near=11.3) - w("كورة"), [{"icon": "Volleyball", "label": "كورة مع اصحابك"}], top=0.14, size=150)
S.icons(w("فانت", near=11.3), w("وده", near=12.8) - w("فانت", near=11.3), [{"icon": "HeartPulse", "mark": "check", "label": "الكارديو اليومي"}], top=0.14, size=150)
S.title(w("انت", near=15.0), w("اكتبولي") - w("انت", near=15.0), [{"text": "باي شكل", "accent": True, "size": 140}, {"text": "انت بتحب", "size": 90}], eyebrow="الكارديو", top=0.04, occlude=True)
S.icons(w("اكتبولي"), S.T - w("اكتبولي"), [{"icon": "MessageCircle", "label": "الكومنتس"}], top=0.14, size=150)

S.finish("OSM: cardio doesn't have to be in the gym", keywords=["الكارديو", "treadmill", "bike", "stairmaster", "ping", "padel", "كورة", "الكومنتس"],
         cap_top=0.76, music={"style": "trap", "key": "D", "seed": 40})
