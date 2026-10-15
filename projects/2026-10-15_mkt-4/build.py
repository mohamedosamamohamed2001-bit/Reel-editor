"""Marketing Reel 4 — "Daily challenge" (music-led). His gym footage + the real app: today's challenge with its
points, upload your attempt, how points work (the app's own rules), badges earned automatically, redeeming points."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_mkt"))
from promo import Promo  # noqa: E402

M = Promo(Path(__file__).resolve().parent)
W, WR, Z = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "zoom", "flash": True}

t = M.gym(3, "IMG_8147.MOV", 15.0, 1.9, zoom=(1.0, 1.1), focusY=0.5)
M.title(t + 0.1, 1.75, [{"text": "كل يوم", "size": 110}, {"text": "تحدي جديد", "accent": True, "size": 110}],
        eyebrow="DAILY CHALLENGE", top=0.66)
t = M.app("challenges", [(3.5, 1.9), (6.5, 1.6)], tin=Z, highlights=[(0.5, 1.3, (0.03, 0.08, 0.94, 0.27)), (2.1, 1.3, (0.03, 0.42, 0.94, 0.1))])
M.label(t + 2.0, 1.4, "ارفع فيديو المحاولة", eyebrow="UPLOAD", top=0.80)
M.gym(2, "IMG_7531.MOV", 3.0, 0.8, zoom=(1.04, 1.1), tin=W, focusY=0.40)
M.gym(1, "IMG_8382.MOV", 2.2, 0.8, zoom=(1.0, 1.06), tin=WR, focusY=0.40)
# the app's own rules (How points work)
t = M.app("points", [(3.0, 1.6), (7.6, 1.6)], tin=Z, highlights=[(0.3, 1.2, (0.03, 0.06, 0.94, 0.25)), (1.9, 1.2, (0.03, 0.40, 0.94, 0.2))])
M.label(t + 0.2, 1.4, "نقط على يومك وتحدياتك", eyebrow="POINTS", top=0.80)
M.label(t + 1.8, 1.3, "استبدل نقطك", eyebrow="REDEEM", top=0.80)
t = M.app("badges", [(3.0, 1.2), (6.4, 1.0)], tin=W, entrance="flat")
M.label(t + 0.15, 2.0, "Badges بالتمرين بس", eyebrow="محدش بياخدها هدية", top=0.80)
t = M.gym(3, "CCA8ED09.mp4", 9.0, 2.0, zoom=(1.0, 1.08), tin=Z, focusY=0.45)
M.title(t + 0.1, 1.85, [{"text": "اتمرن", "size": 110}, {"text": "واكسب", "accent": True, "size": 120}], top=0.66)

M.finish("OSM promo 4: daily challenge", keywords=[], voice_led=False,
         music={"style": "phonk", "key": "D", "seed": 404, "gain": -5, "bpm": 150})
