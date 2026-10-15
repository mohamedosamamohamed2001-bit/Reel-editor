"""Batch 3 (12 videos, 2026-10-15): the approved OSM system (projects/_n6/common2.py: narrow #56A0FB caption bars,
no blur, old captions ERASED, end artwork) + Coach Osama's batch-3 asks:
  - heavy motion graphics: iconPop illustration tiles, kinetic titles (smooth motion, 3D depth), step badges, labels;
  - more external visuals (openly licensed, projects/_b3/assets/manifest.json) on the words they illustrate;
  - a transition with an SFX hit on every real cut of the source (old flash/light-leak frames hidden by held frames);
  - energetic original music (tools/music.py), voice always on top;
  - behind-the-head titles where his head is in frame (kineticTitle occlude, tools/cutout.py).
Each video's build.py lists its story beats; this module turns them into an edit.
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common import DIALOGUE_FX, END_DUR, FPS, GRADE, SHARPEN, Timeline, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402,F401
from common2 import END_IMAGE, TEXT_PLATE  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
MANIFEST = {m["file"]: m for m in json.loads((ASSETS / "manifest.json").read_text())}
CLEAN = "work/clean/original.clean.mp4"


def words_of(P):
    d = json.load(open(Path(P) / "work/tx/aligned.words.json"))
    return [w for s in d["segments"] for w in s["words"]]


class Story:
    """One video: timeline from the source's real cuts, overlays and SFX placed on spoken words (source time)."""

    def __init__(self, P, end, start=0.0, zoom_cycle=(1.0, 1.06), focusY=0.42, grade=GRADE, extra_holds=(), skip=()):
        self.P = Path(P)
        self.words = words_of(P)
        self.media = {"main": CLEAN}
        self.overlays, self.cues, self.shakes = [], [], []
        self.grade = grade
        # the old edit's cuts and flash / light-leak spans (projects/_b3/flashes.py): a span = several jumping frames
        spans = [tuple(map(float, x.split("-"))) for x in (self.P / "work/flashes.txt").read_text().split(":")[1].split()]
        groups = [[a, b] if b > a else [a] for a, b in spans if start + 0.3 < a and b < end - 0.3]
        for a, b in extra_holds:
            groups.append([a, b])
        groups = [g for g in sorted(groups, key=lambda g: (g[0], -len(g))) if not any(abs(g[0] - x) < 0.05 for x in skip)]
        merged = []  # a hold span swallows single cuts inside / at its edges
        for g in groups:
            if merged and len(merged[-1]) > 1 and g[0] <= merged[-1][-1] + 0.05:
                merged[-1][-1] = max(merged[-1][-1], g[-1])
                continue
            merged.append(list(g))
        groups = merged
        self.tl = Timeline()
        kinds = ["whip_left", "zoom", "whip_right", "flash", "whip_up"]
        t0, pending = start, None  # pending: transition kind owed to the next clip (after a single hard cut)
        for i, g in enumerate(groups):
            a, b = g[0], g[-1]
            if a - t0 < 0.25:  # too close to the previous cut: merge into it
                continue
            z = zoom_cycle[i % len(zoom_cycle)]
            kw = {"tin": self._tin(pending)} if pending else {}
            if len(g) > 1:  # old flash / leak: hold a clean frame after it while the dialogue plays on
                self.tl.add("main", t0, a - 0.02, zoom=[z, z + 0.03], focusY=focusY, **kw)
                self.tl.add("main", a - 0.02, b + 0.05, zoom=1.0, hold=round(b + 0.08, 3), focusY=focusY, tin=self._tin(kinds[i % len(kinds)]))
                t0, pending = b + 0.05, None
            else:
                self.tl.add("main", t0, a, zoom=[z, z + 0.03], focusY=focusY, **kw)
                t0, pending = a, kinds[i % len(kinds)]
        z = zoom_cycle[len(groups) % len(zoom_cycle)]
        self.tl.add("main", t0, end, zoom=[z, z + 0.03], focusY=focusY, **({"tin": self._tin(pending)} if pending else {}))
        # transition output times = starts of clips with a tin
        self.transitions = [(self.tl.start_of(i), c["tin"]["type"]) for i, c in enumerate(self.tl.clips) if c.get("tin")]
        self.T = self.tl.total()
        for t, kind in self.transitions:
            if kind == "whip":
                self.cues += [cue(t, "whip", -11, dir=1.0), cue(t + 0.02, "air", -20)]
            else:
                self.cues += [cue(t, "reverse_hit", -16, dur=0.45), cue(t, "boom", -12)]
                self.shakes.append({"at": round(t, 3), "amp": 0.5})

    @staticmethod
    def _tin(kind):
        return {"whip_left": {"type": "whip", "dir": "left"}, "whip_right": {"type": "whip", "dir": "right"},
                "whip_up": {"type": "whip", "dir": "up"}, "zoom": {"type": "zoom", "flash": True},
                "flash": {"type": "zoom"}}[kind]

    # --- timing -------------------------------------------------------------------------------------------------
    def o(self, t):
        return self.tl.out(t)

    def w(self, text, near=None, nth=0, end=False):
        """OUTPUT time of a spoken word (start, or end with end=True)."""
        hits = [x for x in self.words if x["w"].strip("،.؟?!") == text]
        if not hits:
            raise SystemExit(f"{self.P.name}: word not found: {text}")
        x = min(hits, key=lambda h: abs(h["start"] - near)) if near is not None else hits[nth]
        return round(self.o(x["end"] if end else x["start"]), 3)

    # --- overlays -----------------------------------------------------------------------------------------------
    def image(self, name, at, dur, mode="card", sfx=True, **kw):
        """Licensed image (projects/_b3/assets) as a visualCard; CC BY gets an on-screen credit."""
        dst = self.P / "work/visuals" / f"{name}.jpg"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ASSETS / f"{name}.jpg", dst)
        key = f"v_{name}"
        self.media[key] = f"work/visuals/{name}.jpg"
        ov = {"type": "visualCard", "src": key, "at": round(at, 3), "dur": round(dur, 3), "mode": mode, **kw}
        rec = MANIFEST.get(f"{name}.jpg")
        if rec and not rec["license"].upper().startswith(("CC0", "PDM")):
            ov["credit"] = f"Photo: {rec['creator']} · CC {rec['license']}"
        self.overlays.append(ov)
        if sfx:
            self.cues += [cue(at, "whoosh_in", -15), cue(at + dur - 0.1, "whoosh_out", -19)]
        return ov

    def icons(self, at, dur, items, top=0.15, size=170, sfx=True, **kw):
        size = int(size * 1.3)  # QA 2026-10-15: tiles read too small on a phone
        self.overlays.append({"type": "iconPop", "at": round(at, 3), "dur": round(dur, 3), "items": items, "top": top, "size": size, **kw})
        if sfx:
            self.cues += [cue(at + 0.08 + 0.17 * i, "blip", -20, freq=700 + 120 * i) for i in range(len(items))]

    def title(self, at, dur, lines, eyebrow=None, top=0.14, occlude=False, ink=None, sfx="boom", **kw):
        ov = {"type": "kineticTitle", "at": round(at, 3), "dur": round(dur, 3), "lines": lines, "top": top,
              "motion": "smooth", "depth": ink != "dark", **kw}
        if eyebrow:
            ov["eyebrow"] = eyebrow
        if occlude:
            ov["occlude"] = True
        if ink:
            ov["ink"] = ink
        self.overlays.append(ov)
        if sfx == "boom":
            self.cues += [cue(at, "boom", -13), cue(at + 0.05, "impact", -20)]
        elif sfx:
            self.cues.append(cue(at, sfx, -16))

    def badge(self, at, dur, mark, label, top=0.15, side="right", sub=None):
        ov = {"type": "stepBadge", "at": round(at, 3), "dur": round(dur, 3), "mark": mark, "label": label, "top": top, "side": side}
        if sub:
            ov["sub"] = sub
        self.overlays.append(ov)
        self.cues += [cue(at, "slam", -16)]

    def label(self, at, dur, title, eyebrow=None, top=0.14, sets=None):
        ov = {"type": "lowerLabel", "at": round(at, 3), "dur": round(dur, 3), "title": title, "top": top}
        if eyebrow:
            ov["eyebrow"] = eyebrow
        if sets:
            ov["sets"] = sets
        self.overlays.append(ov)
        self.cues += [cue(at, "click", -18)]

    def checklist(self, at, dur, items, top=0.15, row=False):
        self.overlays.append({"type": "checklist", "at": round(at, 3), "dur": round(dur, 3), "items": items, "top": top, "row": row})
        self.cues += [cue(at + it["at"], "key", -19) for it in items]

    # --- output -------------------------------------------------------------------------------------------------
    def finish(self, title, keywords, cap_top=0.62, zones=(), music=None, replace=None, extra=None):
        T = self.T
        self.overlays.append(dict(end_card(T), image=END_IMAGE))
        self.cues += end_card_sfx(T)
        self.shakes.append({"at": round(T, 3), "amp": 0.6})
        cap = {"wordsFile": "work/tx/aligned.words.json", "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
               "keywords": keywords, "zones": [{"at": 0, "dur": round(T + 0.01, 3), "top": cap_top}]}
        for z in zones:  # zones listed later win (Captions takes the first match): put specific ones first
            cap["zones"].insert(0, z)
        if replace:
            cap["replace"] = replace
        spec = music or {}
        drops = sorted(t for t, _ in self.transitions)
        secs, prev = [], 0.0
        for i, t in enumerate(drops):
            if t - prev < 1.2:
                continue
            if t - 1.0 > prev + 0.6:
                secs.append({"type": "groove" if i % 2 else "drive" if spec.get("style") == "drive" else "groove", "until": round(t - 1.0, 3)})
                secs.append({"type": "build", "until": round(t, 3), "stop": True})
            else:
                secs.append({"type": "groove", "until": round(t, 3)})
            prev = t
        secs = [{"type": "intro", "until": min(1.2, T / 4)}] + [s for s in secs if s["until"] > 1.3] + \
            [{"type": "drop", "until": round(T, 3)}, {"type": "outro", "until": round(T + END_DUR, 3)}]
        clean = []
        for s in secs:  # every section >= 1.1 s (shorter ones break tools/music.py): merge into the previous one
            if s["type"] == "drive":
                s["type"] = "groove"
            start = clean[-1]["until"] if clean else 0.0
            if clean and s["until"] - start < 1.1 and s["type"] not in ("drop", "outro"):
                clean[-1]["until"] = s["until"]
                clean[-1].pop("stop", None) if clean[-1]["type"] != "build" else None
            else:
                clean.append(s)
        secs = clean
        mus = make_music(self.P, {"bpm": spec.get("bpm", 124), "key": spec.get("key", "E"), "mode": "minor",
                                  "style": spec.get("style", "trap"), "seed": spec.get("seed", 7),
                                  "sections": secs, "duration": round(T + END_DUR, 3)}, gain_db=spec.get("gain", -9))
        edit = {"title": title, "fps": FPS, "width": 1080, "height": 1920, "media": self.media,
                "audio": {"main": "work/stems/original.vocals.wav"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
                "plates": {"grade": self.grade, "sharpen": SHARPEN}, "clips": self.tl.clips, "captions": cap,
                "overlays": self.overlays, "shakes": self.shakes, "sfx": {"cues": sorted(self.cues, key=lambda c: c["at"])},
                "music": mus, "tail": END_DUR, "textPlate": TEXT_PLATE}
        if extra:
            edit.update(extra)
        write_edit(self.P, edit)
        print(f"T={T:.2f}s, {len(self.transitions)} transitions, {len(self.overlays)} overlays")
