"""Batch 7 / 6 (V2, 88 s landscape, studio): "how my gym clients use the OSM app". His phone screen is already beside
him in the take; for 9:16 each beat is either HIM (face-centred crop) or the PHONE SCREEN (the panel of the same take,
as a phone card on the brand background), always in sync with his voice.

Cut from the take (source untouched):
  - 63.6-76.3 s: the Payment / "Work With Me" part (payment steps in app-facing video are not allowed, and the screen
    shows the coach admin panel, package prices and his e-mail); 16.2-21.1 s and two shorter pauses: dead air.
  - 4.15-6.0 s of the panel (home screen with an account name) is never shown.
Approved OSM system: #56A0FB caption bars, white text, smooth 3D titles, labels and icon tiles below his chin, transitions
with SFX on the cuts, original music, OSM end card."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "_mkt"))
sys.path.insert(0, str(HERE.parents[0] / "_b7"))
import promo  # noqa: E402
from promo import BG, FPS, PJ, Promo, cue  # noqa: E402
from b7 import lock  # noqa: E402

SRC = "2026-10-17_b7-6/source/original.mp4"
promo.VOICE["v2"] = (SRC, SRC, "2026-10-17_b7-6/work/tx/aligned.words.json", None)
GRADE = "eq=contrast=1.05:saturation=1.08:gamma=0.99"
KEEP = [(0.0, 16.2), (21.1, 29.9), (31.1, 53.9), (54.6, 63.6), (76.3, 88.35)]
PANEL = {"x": 192 / 1920, "y": 59 / 1080, "w": 502 / 1920, "h": 961 / 1080}  # his phone screen inside the take
CARD_W, CARD_TOP = 680, 120
CARD_BOTTOM = (CARD_TOP + CARD_W * 961 / 502) / 1920
WL, WR, Z = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "zoom", "flash": True}


def out(t):
    """Output time of source time t (inside a kept range)."""
    o = 0.0
    for a, b in KEEP:
        if t <= b + 1e-6:
            return round(o + max(0.0, t - a), 3)
        o += b - a
    raise ValueError(t)


class Walk(Promo):
    def __init__(self):
        super().__init__(HERE, cap_top=0.74)
        self.src_t = 0.0
        for a, b in KEEP:
            self.say("v2", a, b, at=out(a), pad=0.0)

    def shot(self, kind, until, focusX=0.65, zoom=(1.0, 1.03), tin=None):
        """From the current source time to `until`; split (with a whip) where a pause / cut is removed."""
        first = True
        for a, b in KEEP:
            x, y = max(a, self.src_t), min(b, until)
            if y - x < 1e-6:
                continue
            jump = not first or x > self.src_t + 1e-3  # a removed pause / cut: whip over it
            t_in = (tin or (WL if len(self.clips) % 2 else WR)) if jump else tin
            if kind == "me":
                self._add(f"../{SRC}", x, round(out(y) - out(x), 4), tin=t_in, zoom=list(zoom), focusX=focusX, focusY=0.32, grade=GRADE)
            else:
                self.panel(x, y, tin=t_in)
            first = False
        self.src_t = until

    def panel(self, a, b, tin=None):
        dur = round(out(b) - out(a), 4)
        t0 = self._add(f"../{BG.relative_to(PJ).as_posix()}", 0.0, dur, tin=tin, freeze=True, zoom=1.0)
        key = self._key(f"../{SRC}")
        self.overlays.append({"type": "screenCard", "at": round(t0, 4), "dur": dur, "src": key, "plate": True, "backdrop": "none",
                              "entrance": "tilt", "width": CARD_W, "top": CARD_TOP, "region": PANEL,
                              "segments": [{"in": a, "rate": 1, "dur": dur}], "taps": [], "highlights": []})
        self.zones.append({"at": round(t0 - 0.05, 3), "dur": round(dur + 0.05, 3), "top": round(CARD_BOTTOM + 0.012, 3)})
        if not tin:
            self.cues.append(cue(t0, "whoosh_in", -15))


S = Walk()
S.shot("me", 4.13, focusX=0.48)
S.shot("me", 6.0, tin=Z)
S.shot("panel", 8.3)                    # "ببعتلك التمرينة بتاعتك على الـApplication": today's workout + his demo video
S.shot("me", 11.2, zoom=(1.05, 1.08))   # "بحيث نتراك الوزن والعدات"
S.shot("panel", 23.6)                   # "لعبت 12 عدة ووزن 50" ... "كل تمرينة هتلعبها هتسجل وزنك وعداتك"
S.shot("me", 29.9)                      # "وأنا طبعًا هبقى معاك في الجيم ... كل أسبوع هنزود في الأوزان"
S.shot("me", 34.9, zoom=(1.05, 1.08))   # "الجزئية بتاعت الـCalories Calculator"
S.shot("panel", 39.4)                   # the calculator
S.shot("me", 43.8)                      # "الـSteps ... عايزك كل يوم تسجل الـSteps بتاعتك"
S.shot("panel", 53.9)                   # 10,000 steps -> 400 kcal
S.shot("me", 57.0, zoom=(1.05, 1.08))   # "الـProgress بتاعك برضو ده مهم"
S.shot("panel", 59.3)                   # progress: weight
S.shot("me", 63.6)                      # "عايزك كل يوم تسجل وزنك ... خسيت زدت"
S.shot("me", 78.0, zoom=(1.05, 1.08))   # "وحاجة كمان في الـNutrition Plan"
S.shot("panel", 81.70)                  # the diet plan: 2000 cal balanced
S.shot("me", 88.35, focusX=0.50, tin=Z)

ws = [w for w in S.words]


def w(text, near):
    return min((x for x in ws if x["w"] == text), key=lambda x: abs(x["start"] - out(near)))["start"]


S.title(0.1, w("هتستفيد", 2.2) - 0.1, [{"text": "OSM APP", "size": 120}, {"text": "لعملاء الجيم", "accent": True, "size": 80}], top=0.56)
S.title(w("هتستفيد", 2.2), w("أنا", 4.9) - w("هتستفيد", 2.2) - 0.1, [{"text": "هتستفيد إزاي", "size": 110}, {"text": "بالـApp؟", "accent": True, "size": 140}],
        eyebrow="COACH OSAMA", backdrop=True, top=0.36, sfx="whoosh_in")
S.icons(w("هتلاقيني", 5.6), out(6.0) - w("هتلاقيني", 5.6) - 0.05, [{"icon": "CalendarCheck", "label": "كل يوم"}], top=0.50, size=210)
S.icons(w("نتراك", 8.7), out(11.2) - w("نتراك", 8.7) - 0.1, [{"icon": "Dumbbell", "label": "الوزن"}, {"icon": "Repeat", "label": "العدات"}], top=0.50, size=210)
S.icons(w("وأنا", 23.7), w("بحيث", 25.5) - w("وأنا", 23.7) - 0.1, [{"icon": "Users", "label": "معاك في الجيم"}], top=0.50, size=210)
S.icons(w("كل", 28.0), out(29.9) - w("كل", 28.0) - 0.05, [{"icon": "TrendingUp", "label": "كل أسبوع"}], top=0.50, size=210)
S.label(w("الجزئية", 33.0), out(34.9) - w("الجزئية", 33.0) - 0.05, "CALORIES CALCULATOR", eyebrow="في الـApp", top=0.56)
S.icons(w("الـSteps", 39.5), out(43.8) - w("الـSteps", 39.5) - 0.1, [{"icon": "Footprints", "label": "سجل الـSteps"}], top=0.50, size=210)
S.label(w("الـProgress", 55.9), out(57.0) - w("الـProgress", 55.9) - 0.05, "PROGRESS", eyebrow="ده مهم", top=0.56)
S.icons(w("بحيث", 59.4), out(63.6) - w("بحيث", 59.4) - 0.1, [{"icon": "Scale", "label": "تراك للوزن"}], top=0.50, size=210)
S.icons(w("برا", 81.6), w("إنما", 82.6) - w("برا", 81.6) - 0.05, [{"icon": "Salad", "label": "Online بس"}], top=0.50, size=210)
S.icons(w("إنما", 82.6), S.t() - w("إنما", 82.6) - 0.1, [{"icon": "Dumbbell", "mark": "check", "label": "التمارين فقط"}], top=0.50, size=210)

S.finish("OSM app for gym clients", keywords=["App", "Application", "12", "50", "Calories", "Steps", "10,000", "400", "Progress", "Nutrition", "التمارين"],
         music={"style": "drive", "key": "E", "seed": 706, "gain": -10})
lock(HERE)
