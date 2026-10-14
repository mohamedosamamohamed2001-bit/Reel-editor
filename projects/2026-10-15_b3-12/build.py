"""Rest day may matter more than training day (batch 3, video 12).

Hook -> your body doesn't grow during training -> real progress happens while you rest -> muscles recover, energy
rebalances -> push every day = stress instead of progress -> before blaming yourself for a rest day: you're
protecting your body from injury -> how many rest days do you take?
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=21.75, focusY=0.35)
w = S.w

S.title(0.05, w("جسمك", near=2.6) - 0.1, [{"text": "REST DAY", "accent": True}, {"text": "اهم من التمرين؟", "size": 90}], top=0.03, occlude=True)
S.badge(w("مش", near=3.2), w("التطور") - w("مش", near=3.2), "✗", "اثناء التمرين", top=0.14)
S.image("sleep_bed", w("التطور"), w("الراحة", near=7.0) - w("التطور"), mode="full", push=[1.0, 1.05])
S.icons(w("عضلاتك"), w("ولو") - w("عضلاتك"), [{"icon": "BicepsFlexed", "mark": "check", "label": "بتتعافى"}, {"icon": "BatteryFull", "label": "الطاقة"}], top=0.14, size=150)
S.icons(w("ولو"), w("انت", near=13.0) - w("ولو"), [{"icon": "CalendarDays", "value": "7/7", "label": "كل يوم"}], top=0.14, size=150)
S.title(w("للإجهاد"), w("فقبل") - w("للإجهاد"), [{"text": "إجهاد", "accent": True, "size": 160}], eyebrow="بدل التطور", top=0.03, occlude=True)
S.image("knee_injury", w("بتحمي"), w("اكتبلي") - w("بتحمي"), mode="card", width=560, top=0.10)
S.icons(w("اكتبلي"), S.T - w("اكتبلي"), [{"icon": "MessageCircle", "label": "كم يوم راحة؟"}], top=0.14, size=150)

S.finish("OSM: rest day", keywords=["الراحة", "بيكبر", "بترتاح", "عضلاتك", "للإجهاد", "الاصابات", "راحة"],
         cap_top=0.70, music={"style": "drive", "key": "E", "seed": 42})
