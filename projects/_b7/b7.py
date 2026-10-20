"""Batch 7 (2026-10-17, Coach Osama: 7 videos from one Drive folder) on the approved, locked OSM system.

  - 5 raw iPhone exercise demos (IMG_3006/3017/3018/3019/3022): projects/_tips/common4.py (Tip) with the tips colour
    grade he approved on 2026-10-16 (richer, clearer, skin kept), the exercise name as a smooth 3D title, his cues as
    icon tiles / badges / labels on the words he says them, punch-ins with an SFX hit, original music, OSM end card;
  - V2 (landscape app walkthrough with his phone screen beside him): projects/2026-10-17_b7-6/build.py;
  - 1011_2 (car selfie, old one-word blue plates ERASED with tools/erase_plates.py): projects/2026-10-17_b7-7/build.py.
LOCKED BRAND RULE (2026-10-16): caption bar #56A0FB, all caption text white, brand font. Nothing on or above his head.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_tips"))
from common4 import DECODE, Tip  # noqa: E402,F401

CAPTION_BAR = "#56A0FB"
TIP_GRADE = "format=yuv420p"  # 2026-10-20: natural camera colours (the old warm grade below read yellow)
OLD_WARM_GRADE = ("format=yuv420p,eq=contrast=1.12:saturation=1.20:gamma=0.97,"
             "colorbalance=rs=-0.015:bs=0.02:rm=-0.01:bm=0.005:rh=0.012:gh=0.004:bh=-0.012,"
             "curves=master='0/0 0.06/0.035 0.25/0.21 0.5/0.5 0.75/0.79 0.94/0.965 1/1',vignette=angle=PI/7")


def lock(P, blue_shirt=False):
    """LOCKED BRAND RULE (Coach Osama 2026-10-16): caption bar #56A0FB, all caption text white, brand font;
    exercise / cue labels and step badges on the solid brand plate. blue_shirt: his shirt is close to Core Blue, so
    titles over the footage are white (3D depth kept) instead of blue accent lines that would vanish into the shirt."""
    p = Path(P) / "edit.json"
    e = json.loads(p.read_text())
    e["textPlate"] = CAPTION_BAR
    if "captions" in e:
        e["captions"].update({"style": "plate", "plateColor": CAPTION_BAR, "keywordColor": "#FFFFFF"})
        e["captions"].pop("light", None)
    for o in e["overlays"]:
        if o["type"] in ("lowerLabel", "stepBadge"):
            o["plate"] = True
        if blue_shirt and o["type"] == "kineticTitle" and not o.get("backdrop"):
            for ln in o["lines"]:
                ln.pop("accent", None)
            o.pop("eyebrow", None)  # the small blue eyebrow vanishes into the shirt
    p.write_text(json.dumps(e, ensure_ascii=False, indent=1))


def demo(P, **kw):
    S = Tip(P, **kw)
    S.grade = TIP_GRADE
    return S


B7_ASSETS = Path(__file__).resolve().parent / "assets"


def image(S, name, at, dur, mode="full", **kw):
    """Openly licensed photo from projects/_b7/assets (manifest) as a visualCard, CC BY credit on screen."""
    from common3 import cue
    dst = S.P / "work/visuals" / f"{name}.jpg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes((B7_ASSETS / f"{name}.jpg").read_bytes())
    S.media[f"v_{name}"] = f"work/visuals/{name}.jpg"
    rec = {m["file"]: m for m in json.loads((B7_ASSETS / "manifest.json").read_text())}[f"{name}.jpg"]
    S.overlays.append({"type": "visualCard", "src": f"v_{name}", "at": round(at, 3), "dur": round(dur, 3), "mode": mode,
                       "credit": f"Photo: {rec['creator']} · CC {rec['license']}", **kw})
    S.cues += [cue(at, "whoosh_in", -15), cue(at + dur - 0.1, "whoosh_out", -19)]
