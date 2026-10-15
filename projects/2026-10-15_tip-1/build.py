"""Tip 1: band exercise steps (55 s, one take). Steps: band set-up -> elbow position, hand out -> no Arch, brace the abs
(the opposite of an Arch) -> full range up/down, always pushing the hand out -> 10 reps -> straight to the same arm from
the side -> elbow over it -> key rule: elbow never opens on the way down, same line, full range.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_tips"))
from common4 import Tip  # noqa: E402

S = Tip(Path(__file__).resolve().parent, pauses=[(26.24, 29.41)], focusY=0.40)
w = S.w
S.punch(11.5, 16.2)  # "مش عايزك عامل Arch ... هشد بطني" punch-in
S.punch(45.0, 50.3)  # "أهم حاجة ... ما ينفعش كوعي يفتح"

S.title(0.1, w("أول") - 0.2, [{"text": "STEPS", "size": 150}, {"text": "خطوة بخطوة", "accent": True, "size": 90}],
        eyebrow="OSM · BAND", top=0.47)
S.label(w("بشد"), w("كوعي") - w("بشد") - 0.1, "RESISTANCE BAND", eyebrow="الـBand", top=0.56)
S.badge(w("كوعي"), w("ومش") - w("كوعي") - 0.05, "1", "الكوع والإيد لبرا", top=0.55, side="right")
S.badge(w("ومش"), w("هشد") - w("ومش"), "✗", "Arch", top=0.55, side="right")
S.icons(w("هشد"), w("وهطلع") - w("هشد") - 0.1, [{"icon": "Flame", "label": "شد بطنك"}, {"icon": "Shield", "label": "Core"}], top=0.55, size=130)
S.icons(w("وهطلع"), w("ودايما") - w("وهطلع"), [{"icon": "ArrowUp", "label": "للآخر"}, {"icon": "ArrowDown", "label": "للآخر"}], top=0.55, size=130)
S.label(w("ودايما"), w("هنا") - w("ودايما"), "PUSH OUT", eyebrow="ادفع إيدك لبرا", top=0.56)
S.icons(w("هعمل"), w("نفس", near=32.5) - w("هعمل"), [{"icon": "Repeat", "value": "10", "label": "عدات"}], top=0.55, size=140)
S.icons(w("نفس", near=32.5), w("نفس", near=35.0) - w("نفس", near=32.5), [{"icon": "TimerOff", "label": "من غير راحة"}], top=0.55, size=140)
S.badge(w("نفس", near=35.0), w("هطلع", near=41.2) - w("نفس", near=35.0), "2", "من الجنب", top=0.55, side="right")
S.image("shoulder_anatomy", w("هطلع", near=41.2), w("أهم") - w("هطلع", near=41.2) - 0.1, mode="full", push=[1.0, 1.06])
S.title(w("أهم"), w("ما", near=48.2) - w("أهم"), [{"text": "أهم حاجة", "accent": True, "size": 120}], top=0.6)
S.icons(w("ما", near=48.2), w("لازم") - w("ما", near=48.2), [{"icon": "BicepsFlexed", "mark": "x", "label": "الكوع ما يفتحش"}], top=0.55, size=140)
S.label(w("لازم"), w("هطلع", near=51.8) - w("لازم"), "SAME LINE", eyebrow="نفس الخط", top=0.56)
S.icons(w("هطلع", near=51.8), S.T - w("هطلع", near=51.8), [{"icon": "ArrowUp"}, {"icon": "Check", "label": "Full Range"}, {"icon": "ArrowDown"}], top=0.55, size=120)

S.finish("OSM tip: band exercise steps", keywords=["steps", "band", "arch", "بطني", "لبرا", "10", "أهم", "line"],
         cap_top=0.72, music={"style": "drive", "key": "E", "seed": 41, "gain": -9})
