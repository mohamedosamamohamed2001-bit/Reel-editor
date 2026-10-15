"""Gym hype edits (2026-10-15, Coach Osama: 3 folders of raw training footage -> 3 high-energy Reels, 30-40 s).

A Montage is a list of shots placed on a beat grid (tools/music.py, 150 bpm = one beat every 12 frames at 30 fps,
so every cut lands exactly on a beat). Each shot picks its source window automatically from the clip's motion curve
(tools/footage_review.py: the most explosive stretch of the rep) unless an explicit start is given.

Shot kinds:
  cut   - real time, a slow push-in (zoom) on the beat
  ramp  - speed ramp: real time -> slow motion around the rep's peak -> fast out (each part is its own plate)
  slow  - slow motion for the whole shot (frame-blended at 30 fps; true slow motion from 120 fps sources)
  fast  - 1.5-2x with natural motion blur (tmix)
Every shot change gets a beat-synced transition or hard cut, an SFX hit, and drops get flash + shake + punch-in.
Footage is iPhone HLG HDR: BT.2020 -> BT.709 primaries (HLG curve kept as the display gamma, which looked the
most natural of the tested tonemaps) before the grade. Nobody's body is warped: no motion interpolation.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_c5"))
from common import END_DUR, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FPS = 30
END_IMAGE = "brand/end/osm-end-photo.jpg"
HLG_TO_709 = "zscale=pin=bt2020:p=bt709:min=bt2020nc:m=bt709:tin=arib-std-b67:t=arib-std-b67:rin=tv:r=tv,format=yuv420p"
LOOKS = {
    # bright gym, light-blue top: crisp, cool steel highlights, warm skin, strong contrast
    "steel": "eq=contrast=1.12:saturation=1.0:gamma=0.97,colorbalance=rm=0.02:bm=-0.02:rh=0.02:bh=-0.02,"
             "curves=master='0/0 0.12/0.08 0.5/0.5 0.88/0.93 1/1',vignette=angle=PI/6",
    # daylight industrial, black tank: gritty, slightly desaturated, deep blacks, warm skin
    "grit": "eq=contrast=1.16:saturation=0.9:gamma=0.96,colorbalance=rs=-0.02:bs=0.03:rm=0.02:gm=0.0:bm=-0.02:rh=0.02:bh=-0.02,"
            "curves=master='0/0 0.1/0.06 0.5/0.48 0.9/0.94 1/1',vignette=angle=PI/5",
    # dark neon gym: deep blacks but readable shadows, cool blue light, natural skin
    "neon": "eq=contrast=1.1:saturation=1.06:gamma=1.04,colorbalance=rs=-0.03:bs=0.05:rm=0.01:bm=0.0:rh=0.02:bh=-0.01,"
            "curves=master='0/0 0.06/0.05 0.3/0.32 0.7/0.74 1/1',vignette=angle=PI/5",
}
SHARPEN = "cas=strength=0.45"
# Folder 1 (light-blue top under cool LEDs): the exact BT.2020 -> 709 conversion turned the shirt a saturated cyan it
# never looks like; decoding the HLG signal as-is (what most players do) kept the shirt and the skin natural.
DECODE = {"steel": "format=yuv420p"}


class Montage:
    def __init__(self, P, look, bpm=150):
        self.P = Path(P)
        self.bpm = bpm
        self.bf = round(FPS * 60 / bpm)  # frames per beat (12 at 150 bpm)
        assert abs(self.bf - FPS * 60 / bpm) < 1e-9, "bpm must give a whole number of frames per beat"
        self.look = look
        self.review = {r["name"]: r for r in json.load(open(self.P / "work/review/review.json"))}
        self.media, self.clips, self.overlays, self.cues = {}, [], [], []
        self.shakes, self.pulses, self.flashes = [], [], []
        self.frame = 0  # output cursor (frames)
        self.used = {}  # clip -> list of used source windows (avoid showing the same rep twice)

    # ---------------------------------------------------------------- helpers
    def t(self, beats=0.0):
        """Output time (s) of the cursor + beats."""
        return (self.frame + beats * self.bf) / FPS

    def key(self, name):
        k = "c_" + Path(name).stem.replace("-", "_")
        self.media[k] = f"source/{name}"
        return k

    def window(self, name, src_len, peak_at=0.5, start=None):
        """Source start for a window of src_len s: the most explosive stretch (mean motion), avoiding reuse, with the
        motion peak at `peak_at` of the window when possible."""
        r = self.review[name]
        dur = r["dur"] - 0.05
        if start is not None:
            return max(0.0, min(start, dur - src_len))
        mot = r["motion"]
        best, best_s = -1, 0.0
        steps = max(1, int((dur - src_len) * 10))
        for i in range(steps + 1):
            s = i / 10
            if any(not (s + src_len <= a or s >= b) for a, b in self.used.get(name, [])):
                continue
            seg = mot[int(s * 10): int((s + src_len) * 10) + 1] or [0]
            score = sum(seg) / len(seg)
            # a peak (rep top / drop of the weight) near the wanted position scores extra
            k = int((s + src_len * peak_at) * 10)
            score += 0.5 * max(mot[max(0, k - 2): k + 3] or [0])
            if score > best:
                best, best_s = score, s
        return best_s

    def _add(self, name, a, frames, speed=1.0, **kw):
        """One clip of exactly `frames` output frames from source time a."""
        a = round(a * FPS) / FPS  # start on a source frame (the studio's frame maths)
        b = a + frames * speed / FPS
        c = {"src": self.key(name), "in": round(a, 5), "out": round(b, 5)}
        if speed != 1:
            c["speed"] = speed
        c.update(kw)
        self.clips.append(c)
        self.frame += frames
        return a, b

    # ---------------------------------------------------------------- shots
    def shot(self, name, beats, kind="cut", start=None, zoom=None, focusX=0.5, focusY=0.45, tin=None, sfx="hit",
             speed=None, parts=None, volume=0.0):
        """Place a shot of `beats` beats. Returns the output start time."""
        t0 = self.t()
        frames = round(beats * self.bf)
        z = zoom or [1.0, 1.05]
        base = {"focusX": focusX, "focusY": focusY, "volume": volume}
        if kind in ("cut", "fast", "slow") and not parts:
            sp = speed or {"cut": 1.0, "fast": 1.6, "slow": 0.5}[kind]
            src_len = frames * sp / FPS
            a = self.window(name, src_len, start=start)
            kw = dict(base, zoom=z)
            if tin:
                kw["tin"] = tin
            kw["volume"] = volume  # 0: the clips' audio carries the gym's own (copyrighted) music
            self._add(name, a, frames, sp, **kw)
            self.used.setdefault(name, []).append((a, a + src_len))
        else:  # ramp: parts = [(beats, speed), ...] (default: 1x -> 0.35x -> 1.8x)
            parts = parts or [(beats * 0.375, 1.0), (beats * 0.375, 0.35), (beats * 0.25, 1.8)]
            fr = [round(pb * self.bf) for pb, _ in parts]
            fr[-1] = frames - sum(fr[:-1])
            # each part consumes a whole number of source frames (no repeated / skipped frame at the joins)
            parts = [(pb, max(1, round(f * sp)) / f if f else sp) for f, (pb, sp) in zip(fr, parts)]
            lens = [f * sp / FPS for f, (_, sp) in zip(fr, parts)]
            total = sum(lens)
            slow_i = min(range(len(parts)), key=lambda i: parts[i][1])
            peak_at = (sum(lens[:slow_i]) + lens[slow_i] / 2) / total
            a = self.window(name, total, peak_at=peak_at, start=start)
            zs = z[0]
            for i, (f, (_, sp)) in enumerate(zip(fr, parts)):
                z1 = zs + (z[1] - z[0]) * f / frames
                kw = dict(base, zoom=[round(zs, 4), round(z1, 4)])
                if i == 0 and tin:
                    kw["tin"] = tin
                ts = self.t()
                a, _ = self._add(name, a, f, sp, **kw)
                a = a + f * sp / FPS
                zs = z1
                if i and sp < 1:
                    self.cues.append(cue(ts, "whoosh_in", -16))  # into slow motion
                elif i and sp > 1:
                    self.cues.append(cue(ts, "whip", -15, dir=-1.0))  # snap back to speed
            self.used.setdefault(name, []).append((a - total, a))
        if sfx == "hit":
            self.cues.append(cue(t0, "whip", -14, dir=1.0) if tin and tin.get("type") == "whip" else cue(t0, "slam", -17))
        elif sfx:
            for s in (sfx if isinstance(sfx, list) else [sfx]):
                self.cues.append(dict(s, at=round(t0 + s.get("at", 0), 4)))
        return t0

    def hold(self, name, at, beats, zoom=1.08, **kw):
        """A frozen frame (impact frame / hero still)."""
        frames = round(beats * self.bf)
        a = round(at * FPS) / FPS
        c = {"src": self.key(name), "in": a, "out": round(a + frames / FPS, 5), "freeze": True, "zoom": zoom}
        c.update(kw)
        t0 = self.t()
        self.clips.append(c)
        self.frame += frames
        return t0

    # ---------------------------------------------------------------- energy
    def drop(self, at=None, big=True):
        """The drop: white flash frame, camera jolt, punch-in, deep boom + impact."""
        t = self.t() if at is None else at
        self.flashes.append(round(t, 4))
        self.shakes.append({"at": round(t, 4), "amp": 1.0 if big else 0.6})
        self.pulses.append({"at": round(t, 4), "amp": 0.09 if big else 0.06})
        self.cues += [cue(t, "boom", -8 if big else -11), cue(t + 0.02, "impact", -13), cue(t - 0.7, "reverse_hit", -14, dur=0.7)]

    def beat_pulses(self, t0, beats, pattern=(0, 2), amp=0.035):
        """Punch-ins on the music's kick/snare beats between t0 and t0 + beats."""
        for b in range(int(beats)):
            if b % 4 in pattern:
                self.pulses.append({"at": round(t0 + b * self.bf / FPS, 4), "amp": amp})

    def title(self, at, beats, lines, eyebrow=None, top=0.72, backdrop=False):
        self.overlays.append({"type": "kineticTitle", "at": round(at, 4), "dur": round(beats * self.bf / FPS, 4),
                              "lines": lines, "top": top, "motion": "smooth", "depth": True,
                              **({"eyebrow": eyebrow} if eyebrow else {}), **({"backdrop": True} if backdrop else {})})
        self.cues.append(cue(at, "slam", -14))

    # ---------------------------------------------------------------- output
    def finish(self, title, music_spec, gym_gain=-26.0):
        T = self.frame / FPS
        self.overlays.append(dict(end_card(T), image=END_IMAGE))
        self.cues += end_card_sfx(T)
        self.shakes.append({"at": round(T, 3), "amp": 0.6})
        spec = dict(music_spec, duration=round(T + END_DUR, 3))
        mus = make_music(self.P, spec, gain_db=music_spec.get("gain", -4))
        mus.update({"duck_ratio": 1, "voice_dip_db": 0})  # music-led: no ducking under the gym sound
        grade = DECODE.get(self.look, HLG_TO_709) + "," + LOOKS[self.look]
        edit = {"title": title, "fps": FPS, "width": 1080, "height": 1920, "media": self.media,
                "plates": {"grade": grade, "sharpen": SHARPEN}, "clips": self.clips, "overlays": self.overlays,
                "shakes": self.shakes, "pulses": self.pulses, "flashes": self.flashes,
                "sfx": {"cues": sorted(self.cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
                "dialogueFx": "highpass=f=60"}
        write_edit(self.P, edit)
        print(f"T={T:.2f}s (+{END_DUR} end card = {T + END_DUR:.2f}s), {len(self.clips)} clips")
        return T
