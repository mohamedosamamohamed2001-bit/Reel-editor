"""Batch 7 / 5 (IMG_3022, 14.4 s): Triceps Overhead (seated, one dumbbell). Hold the dumbbell like this, go back; the key
point: all the way down and all the way up. The silent reps after his last word stay in. Approved OSM system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b7"))
from b7 import demo, lock  # noqa: E402

HERE = Path(__file__).resolve().parent
S = demo(HERE, end=14.3, focusY=0.45)
S.punch(5.7, 9.2)     # "تنزل للآخر وتطلع للآخر"
S.punch(11.6, 14.3, zoom=(1.12, 1.15))
w = S.w

S.title(0.1, w("بمسك") - 0.1, [{"text": "TRICEPS", "size": 140}, {"text": "OVERHEAD", "accent": True, "size": 110}],
        eyebrow="OSM · TECHNIQUE", top=0.52)
S.label(w("بمسك"), w("أهم") - w("بمسك") - 0.1, "GRIP", eyebrow="امسك الدمبل من هنا", top=0.58)
S.title(w("أهم"), w("تنزل") - w("أهم") - 0.05, [{"text": "أهم حاجة", "accent": True, "size": 150}], backdrop=True, top=0.40, sfx="whoosh_in")
S.icons(w("تنزل"), w("وتطلع") - w("تنزل") - 0.05, [{"icon": "ArrowDown", "label": "للآخر"}], top=0.55, size=160)
S.icons(w("وتطلع"), w("للآخر", nth=1, end=True) + 0.3 - w("وتطلع"), [{"icon": "ArrowUp", "label": "للآخر"}], top=0.55, size=160)
t = w("للآخر", nth=1, end=True) + 0.5
# the last reps play clean: no room between his chin and the captions for a label

S.finish("OSM technique: Triceps Overhead", keywords=["Triceps", "Overhead", "أهم", "للآخر"], cap_top=0.76,
         music={"style": "drive", "key": "E", "seed": 705, "gain": -9}, replace={"الـTriceps": "Triceps"})
lock(HERE, blue_shirt=True)
