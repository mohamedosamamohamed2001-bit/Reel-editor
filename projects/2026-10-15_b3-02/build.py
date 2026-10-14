"""2021 throwback (batch 3, video 2): Coach Osama's 9.5 s gym clip from 13 Sep 2021, no speech.

Made into its own short Reel (his choice): two punch-in whips on the beats, smooth titles (no claims about who is
who or results: "OSM · 2021" / "كل رحلة ليها بداية"), energetic music over the gym ambience, OSM end card.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import Story  # noqa: E402

S = Story(Path(__file__).resolve().parent, end=9.45, focusY=0.4, zoom_cycle=(1.0, 1.08, 1.14))
S.title(0.2, 2.9, [{"text": "2021", "accent": True, "size": 220}], eyebrow="OSM · THROWBACK", top=0.06)
S.title(S.o(3.2) + 0.1, 3.0, [{"text": "كل رحلة"}, {"text": "ليها بداية", "accent": True, "size": 120}], top=0.06)
S.icons(S.o(6.4) + 0.1, S.T - S.o(6.4) - 0.1, [{"icon": "Dumbbell", "label": "OSM"}], top=0.08, size=150)
S.finish("OSM: 2021 throwback", keywords=[], music={"style": "trap", "key": "E", "seed": 32, "gain": -6},
         extra={"audio": {"main": "work/clean/original.clean.mp4"}, "dialogueLufs": -26.0})
