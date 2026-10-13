"""Shared builder for the 5-video OSM collection upgrade (projects/2026-10-13_c5-*).

Every video uses the same grade, caption system, cover plates, transition vocabulary, sound kit, music engine and
end card, so the five read as one collection. Each video's build.py only describes its own story beats.
"""
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FPS = 30
W, H = 1080, 1920

# Collection grade (one look for all five): gentle contrast, cool shadows / neutral highlights, a touch less
# saturation (the sources range from warm to neon), soft vignette. Applied after the cover plates, before scaling.
GRADE = ("eq=contrast=1.05:saturation=0.95:gamma=0.99,"
         "colorbalance=rs=-0.015:bs=0.02:rm=-0.01:bm=0.005:rh=0.012:gh=0.004:bh=-0.012,"
         "curves=master='0/0 0.22/0.2 0.78/0.8 1/1',"
         "vignette=angle=PI/7")
# 720p sources upscaled 1.5x: light CAS only (strong sharpening on an upscale shows halos)
SHARPEN = "cas=strength=0.22"

END_CTA = "OSM Coach Osama"
DIALOGUE_FX = "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5"
DIALOGUE_LUFS = -16.0
END_DUR = 2.4


def fr(t):
    return round(t * FPS)


class Timeline:
    """Clips in order; knows each clip's output frames exactly as the studio computes them (clipFrames)."""

    def __init__(self):
        self.clips = []
        self.starts = []  # output frame where each clip starts

    @staticmethod
    def frames(c):
        sp = c.get("speed", 1)
        if c.get("freeze") or sp == 1:
            return fr(c["out"]) - fr(c["in"])
        return round((c["out"] - c["in"]) / sp * FPS)

    def add(self, src, a, b, **kw):
        c = {"src": src, "in": a, "out": b, **kw}
        self.starts.append(self.total_frames())
        self.clips.append(c)
        return self.starts[-1] / FPS  # output start (s)

    def total_frames(self):
        return sum(self.frames(c) for c in self.clips)

    def total(self):
        return self.total_frames() / FPS

    def start_of(self, i):
        return self.starts[i] / FPS

    def out(self, t, src="main"):
        """Source time -> output time (first non-silent clip containing it)."""
        for c, s in zip(self.clips, self.starts):
            if c["src"] != src or c.get("freeze") or c.get("speed", 1) != 1:
                continue
            if c["in"] <= t < c["out"]:
                return s / FPS + (t - c["in"])
        raise ValueError(f"source time {t} is not on the timeline")


def load_words(path):
    d = json.load(open(path))
    return [w for s in d["segments"] for w in s["words"]]


def word_time(words, text, near=None, nth=0):
    """Start time of a reference word (optionally the one nearest `near` seconds)."""
    hits = [w for w in words if w["w"].strip(".,،؟!:") == text]
    if not hits:
        raise SystemExit(f"word not found: {text}")
    if near is not None:
        return min(hits, key=lambda w: abs(w["start"] - near))["start"]
    return hits[nth]["start"]


def covers_from_detection(text_json, band=(0.45, 0.86), min_w=0.70, pad_x=0.035, hold=0.12, gap=0.35,
                          skip=(), line_h=0.064, two_line_h=0.112, center_tol=None):
    """Cover plates over the old burned-in captions, from tools/burned_text.py detections (10 fps).

    One cover per contiguous run of detected text at one position; boxes are normalised so the plates read as one
    consistent caption bar: centred on the old text, at least `min_w` wide, and snapped to a 1-line or 2-line height.
    `hold` widens each cover in time (detection runs at 10 fps; text pops in between samples).
    """
    d = json.load(open(text_json))
    runs = []
    for f in d["frames"]:
        t = f["t"]
        if any(a <= t <= b for a, b in skip):
            continue
        bs = [b for b in f["boxes"] if band[0] <= b[1] and b[3] <= band[1] and b[3] - b[1] <= 0.14 and b[2] - b[0] >= 0.05
              and (center_tol is None or abs((b[0] + b[2]) / 2 - 0.5) <= center_tol)]
        if not bs:
            continue
        u = [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]
        last = runs[-1] if runs else None
        # same caption block while it keeps its place and size (a new line count = a new plate size)
        if last and t - last["t1"] <= gap and abs(u[1] - last["u"][1]) < 0.03 and abs(u[3] - last["u"][3]) < 0.03:
            last["t1"] = t
            last["u"] = [min(last["u"][0], u[0]), min(last["u"][1], u[1]), max(last["u"][2], u[2]), max(last["u"][3], u[3])]
        else:
            runs.append({"t0": t, "t1": t, "u": u})
    for r in runs:  # line count from the block's full extent, not its first frame
        r["two"] = (r["u"][3] - r["u"][1]) > 0.048
    covers = []
    for r in runs:
        if r["t1"] - r["t0"] < 0.15:  # a single stray detection is noise
            continue
        u = r["u"]
        cx = (u[0] + u[2]) / 2
        w = min(0.96, max(min_w, u[2] - u[0] + 2 * pad_x))
        h = max(two_line_h if r["two"] else line_h, u[3] - u[1] + 0.02)
        cy = (u[1] + u[3]) / 2
        x0 = min(max(0.02, cx - w / 2), 0.98 - w)
        covers.append({"src": "main", "at": round(max(0, r["t0"] - hold), 3), "dur": round(r["t1"] - r["t0"] + 2 * hold, 3),
                       "box": [round(x0, 4), round(cy - h / 2, 4), round(x0 + w, 4), round(cy + h / 2, 4)]})
    # bridge short gaps so the bar doesn't blink between phrases: the earlier plate holds until the next one starts
    # (sizes are not merged: one tall 3-line moment must not make every plate tall)
    for p, c in zip(covers, covers[1:]):
        if 0 < c["at"] - (p["at"] + p["dur"]) < 0.3:
            p["dur"] = round(c["at"] - p["at"], 3)
    return covers


def cue(at, sound, gain_db, **kw):
    return {"at": round(at, 4), "sound": sound, "gain_db": gain_db, **kw}


def end_card(at):
    return {"type": "endCard", "at": round(at, 4), "dur": END_DUR, "cta": END_CTA, "reveal": "wipe"}


def end_card_sfx(at):
    # the collection's signature ending: reversed suck into the logo, deep boom on the reveal, CTA click
    return [cue(at, "reverse_hit", -12, dur=0.7), cue(at, "boom", -7), cue(at + 0.5, "click", -17)]


def make_music(proj, spec, gain_db):
    """Render the video's original track with tools/music.py; returns the edit's "music" block."""
    out = proj / "work" / "music"
    out.mkdir(parents=True, exist_ok=True)
    (out / "spec.json").write_text(json.dumps(spec, indent=1))
    subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "tools/music.py"), str(out / "spec.json"), str(out / "music.wav")], check=True)
    return {"src": "work/music/music.wav", "gain_db": gain_db}


def write_edit(proj, edit):
    (proj / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1))
    print(f"wrote {proj / 'edit.json'}: {len(edit['clips'])} clips, {len(edit['overlays'])} overlays, "
          f"{len(edit.get('covers', []))} covers, {len(edit.get('sfx', {}).get('cues', []))} sfx cues")
