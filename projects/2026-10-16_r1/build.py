"""Reel r1 (v1.mov): "The app doesn't do everything — I build your plan myself." His whole take, unbroken.
Cutaways: the coach chat (connection), icons for routine / needs / goal, the workout plan, his own training,
the progress screen (plan updates), the home screen (the app makes follow-up easy)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_r16"))
from reel import W, WR, Z, ZP, Reel  # noqa: E402

R = Reel(Path(__file__).resolve().parent)
w = R.w

R.me(w("الحقيقة"), zoom=(1.0, 1.07))
t = R.me(w("انت"), zoom=(1.22, 1.26), focusY=0.38, tin=ZP)
R.title(w("لأ"), w("انت") - w("لأ") - 0.05, [{"text": "لأ", "size": 170}], top=0.64)
R.me(w("ساعتها"), zoom=(1.04, 1.1), tin=W)
R.icons(w("تقرر"), w("ساعتها") - w("تقرر") - 0.1, [{"icon": "UserCheck", "label": "تشترك معايا"}], top=0.58, size=170)
# "ساعتها بيكون في اتصال بيني وبينك" — the coach chat (text or a voice note)
R.app2("messages", 3.0, w("بفهم"), region=(0.0, 0.03, 1.0, 0.84), width=700, tin=WR, entrance="flat",
       highlights=[(0.3, 1.2, (0.0, 0.058, 1.0, 0.062))])
# "بفهم أكتر عن روتينك واحتياجك وهدفك"
R.me(w("وبعدها", 1), zoom=(1.08, 1.12), tin=W)
R.icons(w("روتينك"), w("وبعدها", 1) - w("روتينك") - 0.1,
        [{"icon": "Clock", "label": "روتينك"}, {"icon": "Utensils", "label": "احتياجك"}, {"icon": "Target", "label": "هدفك"}],
        top=0.58, size=150)
# "وبعدها بنحدد الـPlan المناسبة ليك" — the real workout plan
R.app2("workout", 3.6, w("وأنا"), tin=Z)
# "وأنا اللي بحط لك الـPlan بتاعتك بنفسي" — him, in the gym
t = R.gym2(1, "IMG_8384.MOV", 2.6, w("بتاعتك", 1), zoom=(1.04, 1.1), focusY=0.40, tin=WR)
R.gym2(1, "IMG_8381.MOV", 0.3, w("وكل"), zoom=(1.0, 1.06), focusY=0.40, tin=W)
R.label(t + 0.15, w("وكل") - t - 0.3, "COACH OSAMA", eyebrow="بنفسي", top=0.66)
# "وكل فترة طبعاً بيكون فيها تجديد على حسب التطور بتاعك" — progress
R.app("progress", [(3.0, 1.6), (7.6, round(w("الـApp", 1) - R.t() - 1.6, 3))], tin=Z,
      highlights=[(0.5, 1.4, (0.02, 0.535, 0.96, 0.45))])
# "الـApp بيسهل المتابعة" — the home screen (today's workout, meals, challenge)
R.app2("home", 2.6, w("بس"), region=(0.0, 0.13, 1.0, 0.72), tin=W, entrance="flat")
# "بس أنا اللي بوجهك في الآخر"
t = R.me(R.end, zoom=(1.16, 1.22), focusY=0.38, tin=Z)
R.title(t + 0.15, R.end - t - 0.2, [{"text": "Coach Osama", "size": 96}, {"text": "OSM", "accent": True, "size": 120}], top=0.64,
        sfx="slam")

R.finish("OSM r1: the coach builds your plan", keywords=["لأ", "بيني", "هدفك", "بنفسي", "التطور", "بوجهك"],
         music={"style": "drive", "key": "E", "seed": 1601, "gain": -9, "bpm": 124},
         replace={})
