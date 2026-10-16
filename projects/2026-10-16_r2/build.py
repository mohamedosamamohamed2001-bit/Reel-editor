"""Reel r2 (v5.mp4): "Two months of commitment can win you these supplements for free." His whole take, unbroken.
Cutaways: punch-ins on the supplements on his table, the real app (today's challenge -> points history -> the rewards
it can be redeemed for: C4 preworkout, EAA, creatine), his gym footage for "one or two months", 3 winners."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_r16"))
from reel import W, WR, Z, ZP, Reel  # noqa: E402

R = Reel(Path(__file__).resolve().parent, cap_top=0.76)
w = R.w

R.me(w("المكملات"), zoom=(1.0, 1.06))
# "المكملات دي ببلاش؟" — the supplements on the table
t = R.me(w("في"), zoom=(1.7, 1.78), focusY=0.86, tin=ZP)
R.title(t + 0.1, w("في") - t - 0.15, [{"text": "ببلاش؟", "accent": True, "size": 150}], top=0.30)
R.me(w("بالـDaily"), zoom=(1.04, 1.08), tin=W)
# "بالـDaily Challenges بتاعتك بتكسب Points" — today's challenge, then the points it earned
R.app("osm_real", [(2.0, 1.5), (9.6, round(w("والـPoints") - R.t() - 1.5, 3))], region=(0.0, 0.045, 1.0, 0.72), tin=Z,
      highlights=[(0.3, 1.1, (0.03, 0.08, 0.94, 0.28)), (1.6, 0.9, (0.03, 0.13, 0.94, 0.2))])
# "والـPoints دي تقدر تستبدلها بجوايز" — the rewards
R.app2("osm_real", 7.0, w("والمكملات"), region=(0.0, 0.045, 1.0, 0.72), tin=WR, entrance="flat",
       highlights=[(0.6, 1.5, (0.0, 0.42, 1.0, 0.36))])
# "والمكملات دي حاجة من الحاجات اللي انت تقدر تستبدلها."
t = R.me(w("والأحلى"), zoom=(1.5, 1.56), focusY=0.82, tin=Z)
R.icons(t + 0.3, w("والأحلى") - t - 0.45, [{"icon": "Gift", "label": "جوايز"}], top=0.30, size=220)
# "والأحلى في كل ده إن انت مش محتاج Points كتير"
R.me(w("شهر"), zoom=(1.06, 1.1), tin=W)
# "شهر أو شهرين التزام بس ممكن يكونوا كفاية" — him training
R.gym2(2, "IMG_7531.MOV", 1.2, w("التزام", 1), zoom=(1.02, 1.08), focusY=0.40, tin=WR)
R.gym2(3, "CCA8ED09.mp4", 9.0, w("كفاية"), zoom=(1.0, 1.06), focusY=0.45, tin=W)
t = R.gym2(1, "IMG_8382.MOV", 2.2, w("بس", 2), zoom=(1.0, 1.06), focusY=0.40, tin=WR)
# "بس خليني أقولك برضو إن الفايزين هيكونوا 3 بس."
t = R.me(R.end, zoom=(1.12, 1.18), focusY=0.38, tin=Z)
R.icons(w("الفايزين"), R.end - w("الفايزين") - 0.05,
        [{"icon": "Trophy"}, {"icon": "Trophy", "label": "3 فايزين بس"}, {"icon": "Trophy"}], top=0.56, size=200)

R.finish("OSM r2: commit and win the supplements", keywords=["ببلاش", "Points", "بجوايز", "كفاية", "3"],
         music={"style": "trap", "key": "F", "seed": 1602, "gain": -9, "bpm": 128})
