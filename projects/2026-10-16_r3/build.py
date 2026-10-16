"""Reel r3 (v7.mp4): "Imagine training and getting an Apple Watch for free." His whole take, unbroken.
Cutaways: his training, a real Apple Watch photo (CC BY), the real app (points balance, today's challenge and the upload,
points history, rewards), AirPods footage, his close."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_r16"))
from reel import W, WR, WU, Z, ZP, Reel  # noqa: E402

R = Reel(Path(__file__).resolve().parent)
w = R.w

# "تخيل تتمرن" — him training; "وتاخد Apple Watch ببلاش" — the watch
R.gym2(3, "IMG_8147.MOV", 15.0, w("وتاخد"), zoom=(1.0, 1.08), focusY=0.5)
t = R.me(w("في"), zoom=(1.0, 1.04))
R.photo(t, w("في") - t, "aw_f30499.jpg", mode="full", push=[1.0, 1.08])
R.title(t + 0.1, w("في") - t - 0.15, [{"text": "Apple Watch", "size": 110}, {"text": "ببلاش", "accent": True, "size": 130}], top=0.68)
# "في OSM كل ما بتلتزم أكتر بتجمع Points أكتر" — him, then the points balance
R.me(w("بتجمع"), zoom=(1.04, 1.1), tin=W)
R.app2("osm_real", 7.1, w("أنا"), region=(0.0, 0.045, 1.0, 0.72), tin=Z, highlights=[(0.2, 0.9, (0.0, 0.0, 1.0, 0.16))])
# "أنا بابعتلك Daily Challenges" — today's challenge; "انت بتعملها كل يوم" — him training; "وبترفعها على الـApp" — the upload
R.app2("osm_real", 2.0, w("انت"), region=(0.0, 0.045, 1.0, 0.72), tin=WR, entrance="flat",
       highlights=[(0.3, 1.0, (0.03, 0.08, 0.94, 0.28))])
R.gym2(2, "IMG_7537.MOV", 2.0, w("وبترفعها"), zoom=(1.02, 1.08), focusY=0.45, tin=W)
R.app2("osm_real", 3.4, w("كل", 2), region=(0.0, 0.045, 1.0, 0.72), tin=WR, entrance="flat",
       highlights=[(0.1, 0.8, (0.03, 0.40, 0.94, 0.17))])
# "كل ده بيزود الـPoints بتاعتك" — the points history
R.me(w("الـPoints"), zoom=(1.08, 1.12), tin=W)
R.app2("osm_real", 9.6, w("والـPoints"), region=(0.0, 0.045, 1.0, 0.72), tin=Z, entrance="flat",
       highlights=[(0.1, 0.9, (0.0, 0.13, 1.0, 0.2))])
# "والـPoints دي تقدر تستبدلها بجوايز" — rewards
R.app2("osm_real", 7.0, w("زي"), region=(0.0, 0.045, 1.0, 0.72), tin=WR, entrance="flat",
       highlights=[(0.5, 1.4, (0.0, 0.2, 1.0, 0.28))])
# "زي الـApple Watch، الـAirPods وحاجات تانية كتير"
t = R.me(w("الـAirPods"), zoom=(1.0, 1.04), tin=W)
R.photo(t, w("الـAirPods") - t, "aw_461a56.jpg", mode="full", push=[1.04, 1.1], label="Apple Watch")
R.stock2("coverr-taking-airpods-out-of-the-case-2007", 2.0, w("وحاجات"), zoom=(1.0, 1.08), focusX=0.42, tin=WR)
t0 = R.t()
R.label(t0 - (w("وحاجات") - w("الـAirPods")) + 0.05, w("وحاجات") - w("الـAirPods") - 0.1, "AirPods", eyebrow="جوايز", top=0.66)
R.me(w("التزم"), zoom=(1.06, 1.1), tin=W)
# "التزم أكتر، اكسب أكتر في OSM."
t = R.me(R.end, zoom=(1.16, 1.22), focusY=0.38, tin=Z)
R.title(t + 0.1, R.end - t - 0.15, [{"text": "التزم أكتر", "size": 110}, {"text": "اكسب أكتر", "accent": True, "size": 120}], top=0.62)

R.finish("OSM r3: train and win an Apple Watch", keywords=["Apple", "Points", "Daily", "بجوايز", "اكسب"],
         music={"style": "trap", "key": "G", "seed": 1603, "gain": -9, "bpm": 130})
