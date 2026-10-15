"""Marketing Reel 2 — "Every exercise has a demo". His full osm-reel line (his own voice), cut against the app's own
exercise demo videos (filmed in the real app) and his gym footage."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_mkt"))
from promo import Promo  # noqa: E402

M = Promo(Path(__file__).resolve().parent, cap_top=0.70)
W, WR, Z = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "zoom", "flash": True}

# "أكتر حاجة بتقلقك من الأونلاين كوتشنج إنك تعمل التمرين غلط" — his face, in sync (the hook)
a, b = M.span("osm", "أكتر", "غلط")
M.talk("osm", a, b, focusY=0.40, zoom=(1.06, 1.12))
M.icons(M.t() - 1.5, 1.4, [{"icon": "Dumbbell", "mark": "x", "label": "غلط"}], top=0.56, size=170)
# "وعشان كده كل تمرين في OSM هتلاقي عليه التمرين مشروح بالفيديو" — the app's demo videos
a, b = M.span("osm", "وعشان", "بالفيديو")
t = M.t()
end = M.say("osm", a, b, at=t + 0.1)
M.app("workout", [(3.6, round(end - t + 0.15, 3))], tin=Z, highlights=[(2.6, 2.4, (0.05, 0.32, 0.9, 0.62))])
# "مش بس وانا بتمرن هتلاقيني بشرحك كل التبس اللي في التمرينة بصوتي" — him training
a, b = M.span("osm", "مش", "بصوتي")
t = M.t()
end = M.say("osm", a, b, at=t)
d = end - t
M.gym(1, "IMG_8381.MOV", 0.0, d * 0.34, zoom=(1.0, 1.06), tin=W, focusY=0.40)
M.gym(2, "IMG_7531.MOV", 1.2, d * 0.33, zoom=(1.02, 1.08), tin=WR, focusY=0.40)
t3 = M.gym(3, "CCA8ED09.mp4", 7.0, end - M.t(), zoom=(1.0, 1.06), tin=W, focusY=0.45)
M.icons(t3 + 0.1, end - t3 - 0.2, [{"icon": "Mic", "label": "بصوتي"}], top=0.62, size=170)
# "يعني مش هتكون بتتمرن لوحدك ومش عارف بتعمل إيه" — next exercise in the app
a, b = M.span("osm", "يعني", "إيه")
t = M.t()
end = M.say("osm", a, b, at=t + 0.1)
M.app("workout", [(19.9, round(end - t + 0.1, 3))], tin=Z, entrance="flat")
# close: him, title
t = M.gym(1, "IMG_8385.MOV", 0.3, 1.9, zoom=(1.04, 1.1), focusY=0.38, tin=WR)
M.title(t + 0.1, 1.75, [{"text": "كل تمرين", "size": 110}, {"text": "مشروح بالفيديو", "accent": True, "size": 88}], top=0.64)

M.finish("OSM promo 2: every exercise has a demo", keywords=["غلط", "OSM", "بالفيديو", "بصوتي", "لوحدك"],
         music={"style": "trap", "key": "F", "seed": 202, "gain": -9, "bpm": 128})
