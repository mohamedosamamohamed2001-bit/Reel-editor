"""OSM Reels 2026-10-16 (Coach Osama: 3 landscape 4K talking-head takes -> 9:16 Reels, with B-roll and app visuals).

The take's own sound is the voice track, unbroken and in real time (nothing he says is cut), so output time = source time.
The picture is a sequence of shots, each lasting until a source time:
  - `me(until)`: his take, reframed to 9:16 (face-centred crop from the 4K frame, slow push / punch-ins);
  - `app(...)`, `gym(...)`, `stock(...)`: cutaways (the real app screen recordings, his own gym footage, free non-AI stock),
    placed while he keeps talking.
Graphics come from the OSM studio components (projects/_mkt/promo.py). Captions sit on WHITE bars (Coach Osama
2026-10-16): Night text, the one keyword in Core Blue, no blur or haze anywhere, nothing on or above his head.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "_mkt"))
import promo  # noqa: E402
from promo import CAL_GRADE, PJ, Promo, cue  # noqa: E402

ASSETS = HERE / "assets"
W, WR, WU = {"type": "whip", "dir": "left"}, {"type": "whip", "dir": "right"}, {"type": "whip", "dir": "up"}
Z, ZP = {"type": "zoom", "flash": True}, {"type": "zoom"}


class Reel(Promo):
    def __init__(self, P, cap_top=0.72):
        super().__init__(P, cap_top=cap_top)
        name = Path(P).name
        src = next((Path(P) / "source").glob("original.*"))
        self.key = name
        # his take: picture + sound from the same file, transcript = the checked caption text aligned to the take
        promo.VOICE[name] = (str(src.relative_to(PJ)), str(src.relative_to(PJ)),
                             str((Path(P) / "work/tx/aligned.words.json").relative_to(PJ)), CAL_GRADE)
        ws = self.wordlist(name)
        self.end = round(ws[-1]["end"] + 0.35, 3)
        self.say(name, 0.0, self.end, at=0.0, pad=0.0)

    def w(self, text, nth=0, end=False):
        hits = [x for x in self.wordlist(self.key) if x["w"].strip("،.؟?!,") == text]
        x = hits[nth]
        return x["end"] if end else x["start"]

    def dur_to(self, until):
        return round(until - self.t(), 3)

    def me(self, until, zoom=(1.0, 1.05), focusY=0.40, focusX=0.5, tin=None):
        pic = promo.VOICE[self.key][0]
        return self._add(f"../{pic}", self.t(), self.dur_to(until), tin=tin, zoom=list(zoom), focusY=focusY, focusX=focusX,
                         grade=CAL_GRADE)

    def gym2(self, folder, name, a, until, **kw):
        return self.gym(folder, name, a, self.dur_to(until), **kw)

    def stock2(self, name, a, until, **kw):
        return self.stock(name, a, self.dur_to(until), **kw)

    def app2(self, flow, a, until, **kw):
        return self.app(flow, [(a, self.dur_to(until))], **kw)

    def photo(self, at, dur, name, mode="full", label=None, sub=None, **kw):
        """Openly licensed photo (projects/_r16/assets, manifest) as a visualCard; CC BY credit on screen."""
        dst = self.P / "work/visuals" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ASSETS / name, dst)
        key = "v_" + Path(name).stem
        self.media[key] = f"work/visuals/{name}"
        rec = {m["file"]: m for m in json.loads((ASSETS / "manifest.json").read_text())}[name]
        ov = {"type": "visualCard", "src": key, "at": round(at, 3), "dur": round(dur, 3), "mode": mode,
              "credit": f"Photo: {rec['creator']} · CC {rec['license']}", **kw}
        if label:
            ov["label"] = label
        if sub:
            ov["sub"] = sub
        self.overlays.append(ov)
        self.cues += [cue(at, "whoosh_in", -15), cue(at + dur - 0.1, "whoosh_out", -19)]
        return ov

    def finish(self, title, keywords, music, replace=None):
        T = super().finish(title, keywords, music)
        p = self.P / "edit.json"
        e = json.loads(p.read_text())
        cap = e.get("captions")
        if cap:  # white caption bars (Coach Osama 2026-10-16), Night text, keyword in Core Blue
            cap.update({"plateColor": "#FFFFFF", "light": True})
            if replace:
                cap.setdefault("replace", {}).update(replace)
        p.write_text(json.dumps(e, ensure_ascii=False, indent=1))
        return T
