"""Marketing Reel 1 — "Coach, not an app" (hero). His own voice (n2 + osm-reel takes), his gym footage, the real app.
Story: hook title over a hero shot -> "every person has his own training" (his face, in sync) -> "the right training is a
plan made for you" over training + the app's workout -> "every exercise in OSM is explained on video" over the app's
demo videos -> food in grams with swaps (diet screen) -> "you won't be training alone" over the coach chat -> hero -> end card.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_mkt"))
from promo import Promo  # noqa: E402

M = Promo(Path(__file__).resolve().parent, cap_top=0.70)
W = {"type": "whip", "dir": "left"}
WR = {"type": "whip", "dir": "right"}
Z = {"type": "zoom", "flash": True}

# 0 — hook (music only): the coach himself, walking in
M.gym(1, "IMG_8387.MOV", 1.6, 2.2, zoom=(1.0, 1.08), focusY=0.42)
M.title(0.15, 1.95, [{"text": "كوتش حقيقي", "size": 120}, {"text": "مش مجرد App", "accent": True, "size": 92}],
        eyebrow="OSM · COACH OSAMA", top=0.62)
# 1 — "كل واحد وليه تمرينه على حسب هدفه ومستواه." (his face, in sync)
a, b = M.span("n2", "كل", "ومستواه")
t = M.talk("n2", a, b, tin=Z, focusY=0.40)
# 2 — "التدريب الصح مش تقليد." over his training
a, b = M.span("n2", "التدريب", "تقليد")
t = M.t()
M.say("n2", a, b)
M.gym(2, "IMG_7537.MOV", 2.0, 0.75, zoom=(1.02, 1.08), tin=W)
M.gym(3, "CCA8ED09.mp4", 10.0, (b - a) + 0.12 - 0.75, zoom=(1.0, 1.06), tin=WR)
# 3 — "التدريب الصح ان يكون خطة معمولة ليك انت." -> 4 — "كل تمرين في OSM هتلاقي عليه التمرين مشروح بالفيديو"
a, b = M.span("n2", "التدريب", "انت", nth_first=1)
t3 = M.t()
end3 = M.say("n2", a, b)
a2, b2 = M.span("osm", "كل", "بالفيديو")
end4 = M.say("osm", a2, b2, at=end3 + 0.15)
M.app("workout", [(3.6, 3.4), (14.7, 1.6), (19.9, round(end4 + 0.25 - t3 - 5.0, 3))], tin=Z,
      highlights=[(0.5, 1.6, (0.03, 0.23, 0.94, 0.08))])
# 5 — food in grams, with swaps (diet screen; music)
t5 = M.app("diet", [(10.6, 2.3)], region=(0.0, 0.16, 1.0, 0.72), tin=W, entrance="flat")
M.label(t5 + 0.15, 2.1, "بدائل لكل أكلة", eyebrow="DIET · بالجرام", top=0.785)
# 6 — "يعني مش هتكون بتتمرن لوحدك ومش عارف بتعمل إيه" over the coach chat
a, b = M.span("osm", "يعني", "إيه")
t6 = M.t()
end6 = M.say("osm", a, b, at=t6 + 0.1)
M.app("messages", [(3.0, round(end6 - t6 + 0.1, 3))], region=(0.0, 0.03, 1.0, 0.84), width=700, tin=WR,
      entrance="flat", highlights=[(0.3, 1.4, (0.0, 0.058, 1.0, 0.062)), (1.8, 1.3, (0.72, 0.9, 0.12, 0.075))])
# 7 — hero close
t7 = M.gym(1, "IMG_8384.MOV", 2.6, 1.8, zoom=(1.04, 1.12), focusY=0.40, tin=Z)
M.title(t7 + 0.1, 1.65, [{"text": "OSM", "size": 150}, {"text": "Osama Strength Method", "accent": True, "size": 60}], top=0.64)

M.finish("OSM promo 1: coach, not an app", keywords=["تمرينه", "تقليد", "ليك", "OSM", "بالفيديو", "لوحدك"],
         music={"style": "drive", "key": "E", "seed": 101, "gain": -9, "bpm": 124})
