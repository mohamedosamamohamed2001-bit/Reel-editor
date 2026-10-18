"""Batch 7 / 7 (1011_2, 95 s car selfie): gym etiquette, a sensitive topic: if someone tells you that you smell, don't
be upset, be glad: it may be the clothes / the T-shirt; everyone in the gym has the right not to smell anything bad, so
we tell people tactfully; accept it. His old one-word blue captions are ERASED (tools/erase_plates.py --matched,
work/clean/original.clean.mp4, 30 fps). Cut: the 2 s off-topic aside "لا حلوة دي على بعض" and two long pauses.
Selfie framing: his face fills the top 60 %, so the key lines are full-screen brand title cards (his voice goes on) and
the chest under his chin has no room for tiles (head_fix shrank or removed them), so there are none. Approved OSM system (projects/_b7/b7.py)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b7"))
from b7 import TIP_GRADE, demo, image, lock  # noqa: E402

HERE = Path(__file__).resolve().parent
S = demo(HERE, pauses=[(4.0, 7.15), (40.26, 41.62), (46.48, 47.62)], focusY=0.40, zooms=((1.0, 1.03), (1.05, 1.08)))
S.media["main"] = "work/clean/original.clean.mp4"
S.punch(19.6, 21.4)   # "فانت ليه بتتضايق"
S.punch(47.6, 49.3)   # "بالعكس انت تتبسط"
S.punch(84.4, 88.0)   # "يا جدعان بجد إحنا بقى مخنوقين"
w = S.w
CARD = dict(backdrop=True, top=0.34)

S.title(w("موضوع"), w("المهم") - w("موضوع") - 0.05, [{"text": "موضوع حساس", "size": 120}, {"text": "في الجيم", "accent": True, "size": 110}],
        eyebrow="OSM · GYM TALK", **CARD)
S.title(w("فانت", near=20.4), w("عايز", near=22.4) - w("فانت", near=20.4) - 0.05, [{"text": "ليه", "size": 120}, {"text": "بتتضايق؟", "accent": True, "size": 130}], **CARD)
S.title(w("الموضوع", near=45.1), w("بالعكس") - w("الموضوع", near=45.1) - 0.05, [{"text": "الموضوع", "size": 110}, {"text": "مايضايقكش", "accent": True, "size": 120}], **CARD)
S.title(w("فأتمنى"), w("عشان", near=58.2) - w("فأتمنى") - 0.05, [{"text": "أتمنى الناس", "size": 110}, {"text": "تتقبل ده", "accent": True, "size": 120}], **CARD)
S.image("gym_weights", w("حقنا"), w("فلازم") - w("حقنا") - 0.05, mode="full", push=[1.0, 1.06])
image(S, "washing_machine", w("الهدوم", near=77.2), w("فتقبلوا") - w("الهدوم", near=77.2) - 0.05, push=[1.0, 1.06])
S.title(w("فتقبلوا"), w("عشان", near=84.5) - w("فتقبلوا") - 0.05, [{"text": "اتقبلوا", "size": 120}, {"text": "الموضوع ده", "accent": True, "size": 110}], **CARD)

S.finish("OSM gym talk: a sensitive topic", keywords=["حساس", "ريحته", "ريحتك", "الهدوم", "T-shirt", "تتبسط", "حقنا", "بشياكة", "تقبلوا"],
         cap_top=0.745, music={"style": "drive", "key": "D", "seed": 707, "gain": -11})
lock(HERE)
p = HERE / "edit.json"
e = json.loads(p.read_text())
e["audio"] = {"main": "work/stems/original.vocals.wav"}  # the clean picture has no sound: his separated voice (no music in the take; car hum removed)
p.write_text(json.dumps(e, ensure_ascii=False, indent=1))
