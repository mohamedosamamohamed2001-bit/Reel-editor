"""Batch 7 / 3 (IMG_3018, 47.7 s): Seated Dumbbell Shoulder Press. Most people press with an Arch: not wrong in itself,
but with back or shoulder pain: brace the abs, kill the Arch, press. Why the Arch hurts: with a heavy weight the load goes
onto the Lower Back (plus the shoulder), and the Arch adds range / compensation at the shoulder. Approved OSM system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b7"))
from b7 import demo, lock  # noqa: E402

HERE = Path(__file__).resolve().parent
S = demo(HERE, pauses=[(21.0, 24.9)], end=47.4, focusY=0.42)
S.punch(14.1, 17.2)   # "شد بطنك، الغي الـArch ده خالص"
S.punch(29.8, 31.5)   # "فالحمل كله بيبقى على الـLower Back"
S.punch(36.3, 41.6, zoom=(1.1, 1.13))  # range / compensation
S.punch(45.9, 47.4)   # "وطبعًا ده مش صح"
w = S.w

S.title(0.1, w("معظم") - 0.15, [{"text": "SHOULDER", "size": 130}, {"text": "PRESS", "accent": True, "size": 140}],
        eyebrow="OSM · TECHNIQUE", top=0.52)
S.label(w("معظم"), w("أنا", near=7.3) - w("معظم") - 0.1, "COMMON WAY", eyebrow="معظم الناس بتلعبها كده", top=0.58)
S.badge(w("أنا", near=7.3), w("بس", near=8.4) - w("أنا", near=7.3) - 0.02, "✓", "مش غلط", top=0.56, side="right")
S.image("back_pain", w("بوجع"), w("انت", near=11.7) - w("بوجع") - 0.05, mode="full", push=[1.0, 1.06])
S.title(w("انت", near=11.7), w("شد") - w("انت", near=11.7) - 0.1, [{"text": "لازم", "size": 110}, {"text": "تعمل كده", "accent": True, "size": 100}],
        top=0.54, sfx="whoosh_in")
S.icons(w("شد"), w("الغي") - w("شد") - 0.05, [{"icon": "Shield", "label": "شد بطنك"}], top=0.52, size=160)
S.badge(w("الغي"), w("واطلع") - w("الغي") - 0.1, "✗", "Arch", top=0.56, side="right")
S.icons(w("واطلع"), w("ليه") - w("واطلع") - 0.15, [{"icon": "ArrowUp", "label": "اطلع"}, {"icon": "ArrowDown", "label": "انزل"}], top=0.52, size=150)
S.title(w("ليه"), w("أنا", near=27.7) - w("ليه") - 0.05, [{"text": "ليه الـArch", "size": 120}, {"text": "بيوجع ظهرك؟", "accent": True, "size": 110}],
        eyebrow="OSM · WHY", backdrop=True, top=0.34)  # full-screen card: no room between his chin and the captions
S.icons(w("شايل"), w("فالحمل") - w("شايل") - 0.05, [{"icon": "Dumbbell", "label": "وزن تقيل"}], top=0.52, size=160)
S.label(w("فالحمل"), w("بلس") - w("فالحمل") - 0.05, "LOWER BACK", eyebrow="الحمل كله على", top=0.58)
S.icons(w("بلس"), w("بس", near=33.5) - w("بلس") - 0.05, [{"icon": "TriangleAlert", "label": "حمل على الكتف"}], top=0.52, size=160)
S.icons(w("بس", near=33.5), w("وكمان") - w("بس", near=33.5) - 0.1, [{"icon": "TriangleAlert", "value": "+", "label": "الـLower Back"}], top=0.52, size=160)
S.image("shoulder_anatomy", w("الـRange"), w("فمفروض") - w("الـRange") - 0.05, mode="full", push=[1.0, 1.06])
S.badge(w("لو", near=44.2), w("وطبعًا") - w("لو", near=44.2) - 0.05, "!", "عامل Arch", top=0.56, side="right")
S.badge(w("وطبعًا"), S.T - w("وطبعًا") - 0.1, "✗", "مش صح", top=0.56, side="right")

S.finish("OSM technique: Shoulder Press without the Arch", keywords=["Shoulder", "Press", "ظهرك", "كتفك", "بطنك", "Arch", "Lower", "Range", "صح"],
         cap_top=0.74, music={"style": "drive", "key": "D", "seed": 703, "gain": -9})
lock(HERE, blue_shirt=True)
