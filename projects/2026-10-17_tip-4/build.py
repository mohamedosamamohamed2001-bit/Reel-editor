"""Tip 4 (2026-10-17): "Why am I so slow on the pitch?" -> 3 speed drills (pogos, A skip, switches) -> "these alone
aren't enough: they're part of a full plan". Re-edit of a finished export in the approved OSM system
(projects/_b3/common3.py, as batch 3 / the tips): old burned-in blue plates ERASED (tools/erase_plates.py), separated
voice + our own music, a transition + SFX on each original cut, exercise cards rebuilt as OSM labels, icon tiles on the
key points, captions on #56A0FB bars with white text (locked brand rule). Nothing on or above anyone's head."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

HERE = Path(__file__).resolve().parent
S = Story(HERE, end=20.30, zoom_cycle=(1.0, 1.04), focusY=0.45)
w = S.w

# hook (no speech yet): what this video is about
S.title(0.1, w("وأنا") - 0.15, [{"text": "SPEED", "size": 150}, {"text": "في الملعب", "accent": True, "size": 96}],
        eyebrow="OSM · TIPS", top=0.50)
# the drills (no speech: the old exercise cards, rebuilt in the OSM style)
S.title(S.o(5.40), 0.95, [{"text": "3 تمارين", "size": 120}, {"text": "للـ Speed", "accent": True, "size": 96}], top=0.48, sfx="whoosh_in")
S.label(S.o(6.40), S.o(7.45) - S.o(6.40), "POGOS", eyebrow="01 · rest 2–3 min", top=0.72, sets="3×5")
S.label(S.o(7.62), S.o(10.25) - S.o(7.62), "A SKIP", eyebrow="02 · rest 2–3 min", top=0.72, sets="3×5")
S.label(S.o(10.42), S.o(12.32) - S.o(10.42), "SWITCHES", eyebrow="03 · rest 2–3 min", top=0.72, sets="3×5")
# "وهتلاقي سرعتك اختلفت تماماً في الملعب"
S.icons(w("سرعتك"), w("بس") - w("سرعتك") - 0.1, [{"icon": "Zap", "label": "Speed"}], top=0.55, size=170)
# "التمارين دي لوحدها مش كفاية"
S.icons(w("لوحدها"), w("ده") - w("لوحدها") - 0.05, [{"icon": "Dumbbell", "mark": "x", "label": "لوحدها مش كفاية"}], top=0.55, size=170)
# "ده جزء من Plan كاملة هنشرحهالكم الفترة اللي جاية"
S.icons(w("جزء"), S.T - w("جزء") - 0.05, [{"icon": "ClipboardList", "label": "Plan كاملة"}], top=0.55, size=170)

S.finish("OSM tip 4: speed on the pitch", keywords=["بطيء", "Speed", "سرعتك", "كفاية", "Plan"], cap_top=0.745,
         music={"style": "drive", "key": "E", "seed": 1704, "gain": -9, "bpm": 120}, replace={"الـSpeed": "Speed"})

# LOCKED BRAND RULE (Coach Osama 2026-10-16): caption bar #56A0FB, all caption text white, brand font
p = HERE / "edit.json"
e = json.loads(p.read_text())
e["textPlate"] = "#56A0FB"
e["captions"].update({"style": "plate", "plateColor": "#56A0FB", "keywordColor": "#FFFFFF"})
e["captions"].pop("light", None)
# educational tone: exercise labels on the solid brand plate; no white flash frame on the cut (a plain zoom)
for o in e["overlays"]:
    if o["type"] == "lowerLabel":
        o["plate"] = True
for c in e["clips"]:
    if c.get("tin", {}).get("flash"):
        c["tin"] = {"type": "zoom"}
p.write_text(json.dumps(e, ensure_ascii=False, indent=1))
