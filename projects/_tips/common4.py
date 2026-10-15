"""Fitness-tip videos (2026-10-15, 3 raw iPhone takes): the approved OSM system from batch 3 (projects/_b3/common3.py:
narrow #56A0FB caption bar + karaoke, iconPop tiles, smooth 3D titles, step badges, labels, licensed images on the
spoken words, transitions with SFX, energetic original music, OSM end card) with the 2026-10-15 corrections:
no blur / haze anywhere, no text on or above his head (tools/head_check.py + projects/_b3/head_fix.py).

Raw single takes (no old captions to erase): the source is the camera file itself. HLG is decoded as-is (the exact
BT.2020 -> 709 conversion turned the light-blue band cyan). Long pauses are shortened with jump cuts; every jump cut gets
a transition + SFX hit, and the shots between cuts alternate framing (slow push-ins) so the take never looks static.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_b3"))
from common3 import GRADE, Story, Timeline, cue  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
DECODE = "format=yuv420p"


class Tip(Story):
    def __init__(self, P, pauses=(), max_pause=0.9, zooms=((1.0, 1.04), (1.08, 1.11)), focusY=0.42, focusX=0.5):
        """pauses: source gaps (a, b) to shorten to max_pause (jump cuts). Everything else plays in real time."""
        self.P = Path(P)
        d = json.load(open(self.P / "work/tx/aligned.words.json"))
        self.words = [w for s in d["segments"] for w in s["words"]]
        self.media = {"main": "source/original.mov"}
        self.overlays, self.cues, self.shakes = [], [], []
        self.grade = DECODE + "," + GRADE
        end = round(self.words[-1]["end"] + 0.45, 3)
        keep, t0 = [], 0.0
        for a, b in sorted(pauses):
            if b - a > max_pause:
                cut_a = a + max_pause / 2
                cut_b = b - max_pause / 2
                keep.append((t0, round(cut_a, 3)))
                t0 = round(cut_b, 3)
        keep.append((t0, end))
        self.tl = Timeline()
        kinds = ["whip_left", "zoom", "whip_right", "flash", "whip_up"]
        self.transitions = []
        for i, (a, b) in enumerate(keep):
            z = zooms[i % len(zooms)]
            kw = {"tin": self._tin(kinds[(i - 1) % len(kinds)])} if i else {}
            self.tl.add("main", a, b, zoom=list(z), focusY=focusY, focusX=focusX, **kw)
        self.T = self.tl.total()

    def _transition_cues(self):
        """Transitions = clip starts with a tin (jump cuts and punch-ins); each gets its SFX hit (+ jolt on zooms)."""
        self.transitions = [(self.tl.start_of(i), c["tin"]["type"]) for i, c in enumerate(self.tl.clips) if c.get("tin")]
        for t, kind in self.transitions:
            if kind == "whip":
                self.cues += [cue(t, "whip", -11, dir=1.0), cue(t + 0.02, "air", -20)]
            else:
                self.cues += [cue(t, "reverse_hit", -16, dur=0.45), cue(t, "boom", -12)]
                self.shakes.append({"at": round(t, 3), "amp": 0.4})

    def punch(self, a, b, zoom=(1.1, 1.13), focusY=None):
        """A punch-in on the same take between source times a and b (emphasis on a key phrase), no transition."""
        out = []
        for c in self.tl.clips:
            if c["out"] <= a or c["in"] >= b:
                out.append(c)
                continue
            parts = [(c["in"], a, c.get("zoom")), (a, b, list(zoom)), (b, c["out"], c.get("zoom"))]
            first = True
            for x, y, z in parts:
                x, y = max(x, c["in"]), min(y, c["out"])
                if y - x < 0.05:
                    continue
                n = {k: v for k, v in c.items() if k not in ("in", "out", "zoom", "tin")}
                n.update({"in": round(x, 3), "out": round(y, 3), "zoom": z})
                if focusY is not None and z == list(zoom):
                    n["focusY"] = focusY
                if first and c.get("tin"):
                    n["tin"] = c["tin"]
                elif not first or x == a:  # punch in / back out: a zoom punch on the cut
                    n["tin"] = {"type": "zoom"}
                first = False
                out.append(n)
        tl = Timeline()
        for c in out:
            tl.add(c.pop("src"), c.pop("in"), c.pop("out"), **c)
        self.tl = tl
        self.T = tl.total()

    def image(self, name, at, dur, mode="card", sfx=True, **kw):
        # the tips assets live next to this preset; batch-3 assets (projects/_b3/assets) are reused when present
        src = ASSETS / f"{name}.jpg"
        if not src.exists():
            return super().image(name, at, dur, mode=mode, sfx=sfx, **kw)
        dst = self.P / "work/visuals" / f"{name}.jpg"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        key = f"v_{name}"
        self.media[key] = f"work/visuals/{name}.jpg"
        ov = {"type": "visualCard", "src": key, "at": round(at, 3), "dur": round(dur, 3), "mode": mode, **kw}
        man = {m["file"]: m for m in json.loads((ASSETS / "manifest.json").read_text())}
        rec = man.get(f"{name}.jpg")
        if rec and not rec["license"].upper().startswith(("CC0", "PDM")):
            ov["credit"] = f"Photo: {rec['creator']} · CC {rec['license']}"
        self.overlays.append(ov)
        if sfx:
            self.cues += [cue(at, "whoosh_in", -15), cue(at + dur - 0.1, "whoosh_out", -19)]
        return ov

    def finish(self, title, keywords, cap_top=0.62, zones=(), music=None, replace=None, extra=None):
        self._transition_cues()
        super().finish(title, keywords, cap_top=cap_top, zones=zones, music=music, replace=replace, extra=extra)
        p = self.P / "edit.json"
        e = json.loads(p.read_text())
        e.pop("audio", None)  # raw take: the dialogue is the camera's own sound
        p.write_text(json.dumps(e, ensure_ascii=False, indent=1))
