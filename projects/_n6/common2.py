"""Batch 2 (the next six OSM videos, 2026-10-14): the approved collection style (projects/_c5/common.py) plus
  - narrow #56A0FB caption bars: each caption keeps its own tight plate (anchorPlate) instead of a wide cover bar,
  - old burned-in captions: ERASED from a cleaned copy of the source (tools/erase_text.py -> CLEAN_SOURCE); no blur,
    no box. Covers stay as caption positions only (kind "anchor"),
  - end card = Coach Osama's end artwork (END_IMAGE) + the "OSM Coach Osama" pill,
  - supporting visuals (visualCard) from openly licensed sources, credited in projects/_n6/assets/manifest.json.
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
from common import blur_covers as _blur_covers  # noqa: E402
from common import (DIALOGUE_FX, END_DUR, FPS, GRADE, SHARPEN, TEXT_PLATE, Timeline, blur_covers, cue, end_card,  # noqa: F401
                    end_card_sfx, load_words, make_blur_mask, make_music, word_time, write_edit)

ASSETS = Path(__file__).resolve().parent / "assets"
NO_BLUR = True  # Coach Osama 2026-10-14: remove the blurred background behind text in every video
CLEAN_SOURCE = "work/clean/original.clean.mp4"  # Coach Osama 2026-10-14: old captions ERASED (tools/erase_text.py), not covered
END_IMAGE = "brand/end/osm-end-photo.jpg"  # Coach Osama 2026-10-14: his end artwork, replaces the wordmark on the end card
MANIFEST = json.loads((ASSETS / "manifest.json").read_text()) if (ASSETS / "manifest.json").exists() else []


def credit(name):
    """On-screen credit for licences that require attribution (CC BY / BY-SA); None for CC0 / public domain."""
    rec = next((m for m in MANIFEST if m["file"] == name), None)
    if not rec or rec["license"].startswith(("CC0", "PDM")):
        return None
    return f"Photo: {rec['creator']} / {rec['source'].capitalize()} · CC {rec['license']}"


def asset(proj, name):
    """Copy a licensed asset into the project (media must live under the project) and return its media path."""
    dst = Path(proj) / "work" / "visuals" / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    src = ASSETS / name if (ASSETS / name).exists() else ASSETS / "cand" / name
    shutil.copy2(src, dst)
    return f"work/visuals/{name}"


def visual(proj, media, key, name, at, dur, mode="full", **kw):
    """Register an image as media `key` and return a visualCard overlay for it."""
    media[key] = asset(proj, name)
    ov = {"type": "visualCard", "src": key, "at": round(at, 3), "dur": round(dur, 3), "mode": mode}
    c = credit(name)
    if c:
        ov["credit"] = c
    ov.update(kw)
    return ov


def captions_block(words_file, keywords):
    return {"wordsFile": words_file, "style": "plate", "anchorPlate": True, "karaoke": True, "maxWords": 3, "maxChars": 22,
            "keywords": keywords}


def finish(P, tl, edit, covers, blur_band=(0.40, 1.0)):
    """Covers (for caption anchors) + the blur mask, then write edit.json."""
    pinned = Path(P) / "covers.pinned.json"
    if pinned.exists():  # the covers of the delivered render: caption positions stay exactly as approved
        covers = json.loads(pinned.read_text())
    if NO_BLUR:
        # approved 2026-10-14: no blur / frosted background behind text. Covers stay only as caption positions.
        edit["covers"] = [dict(c, kind="anchor") for c in covers]
    else:
        bm = make_blur_mask(P, covers, band=blur_band, fps=60)
        bm.update({"sigma": 16, "darken": 0.12})
        edit["covers"] = covers
        edit["blurMask"] = bm
    if CLEAN_SOURCE:
        if not (Path(P) / CLEAN_SOURCE).exists():
            sys.exit(f"{P}: run `.venv/bin/python tools/erase_text.py {P}` first (it writes {CLEAN_SOURCE})")
        edit["media"]["main"] = CLEAN_SOURCE  # same frames and timing as source/original.mp4, old captions erased
    for ov in edit["overlays"]:
        if ov["type"] == "endCard" and END_IMAGE:
            ov["image"] = END_IMAGE
    edit.setdefault("textPlate", TEXT_PLATE)
    write_edit(P, edit)


def covers_for(P, words, band=(0.45, 0.86), center_tol=0.2, full_width=False, grow_y=0.0):
    """Per-phrase blur covers: detections, plus held boxes wherever he speaks but detection missed the old text.
    Boxes above 0.5 (scene text) are ignored by the band."""
    cv = _blur_covers(Path(P) / "work/text/original.text.json", band=band, center_tol=center_tol, words=words, hold=1.5)
    if full_width:  # a soft blur across the whole width: old text that slides in from the edges can't escape it
        for c in cv:
            c["box"] = [0.0, round(c["box"][1] - grow_y, 4), 1.0, round(min(1.0, c["box"][3] + grow_y), 4)]
    if cv and cv[0]["at"] < 1.2:  # the first caption is usually on from frame 1
        cv[0]["dur"] = round(cv[0]["dur"] + cv[0]["at"], 3)
        cv[0]["at"] = 0.0
    return cv
