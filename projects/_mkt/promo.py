"""OSM marketing Reels (2026-10-15, Coach Osama: "full autonomous execution" of the 6-Reel marketing plan).

Real material only, no AI voice, no AI people, no AI visuals:
  - voice  = Coach Osama's OWN recorded voice, cut from his earlier talking-head videos (exact words, captions are
             what he says); when a line plays over B-roll it is a voice-over, when his face is on screen it is in sync;
  - picture = his own gym footage (Drive folders, 2026-10-15), his talking-head takes, the real OSM app filmed with
             tools/app_record.js (demo account, read-only), and free non-AI Coverr stock (projects/_mkt/stock/manifest.json);
  - graphics = the studio's OSM components (narrow #56A0FB bars, smooth 3D titles, labels, icon tiles), no blur or
             haze anywhere, nothing on or above his head (tools/head_check.py), the OSM end card.
A Promo is a cursor timeline: shots are appended in order; voice lines and overlays are placed in output time.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "_c5"))
sys.path.insert(0, str(HERE.parents[0] / "_n6"))
sys.path.insert(0, str(HERE.parents[0] / "_gym"))
from common import END_DUR, FPS, GRADE, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402
from common2 import END_IMAGE, TEXT_PLATE  # noqa: E402
from montage import HLG_TO_709, LOOKS  # noqa: E402

ROOT = HERE.parents[1]
PJ = ROOT / "projects"
CAL_GRADE = ("colorbalance=rs=-0.02:bs=0.025:rm=-0.05:bm=0.015:rh=0.02:gh=0.005:bh=-0.025,"
             "curves=all='0/0 0.25/0.235 0.5/0.5 0.75/0.765 1/1'")
GYM = {  # folder -> (project, grade) as approved in the gym edits (projects/_gym/montage.py)
    1: ("2026-10-15_gym-1", "format=yuv420p," + LOOKS["steel"]),
    2: ("2026-10-15_gym-2", HLG_TO_709 + "," + LOOKS["grit"]),
    3: ("2026-10-15_gym-3", HLG_TO_709 + "," + LOOKS["neon"]),
}
# his recorded voice: (picture, sound, word-timed transcript, grade of the picture)
VOICE = {
    "n2": ("2026-10-14_n2-training/work/clean/original.clean.mp4", "2026-10-14_n2-training/work/stems/original.vocals.wav",
           "2026-10-14_n2-training/work/tx/aligned.words.json", None),
    "n3": ("2026-10-14_n3-scale/work/clean/original.clean.mp4", "2026-10-14_n3-scale/work/stems/original.vocals.wav",
           "2026-10-14_n3-scale/work/tx/aligned.words.json", None),
    "osm": ("2026-10-14_osm-reel/source/main.mp4", "2026-10-14_osm-reel/source/main.mp4",
            "2026-10-14_osm-reel/work/tx/main.words.json", None),
    "cal": ("2026-10-12_calorie-calculator/source/main.mp4", "2026-10-12_calorie-calculator/source/main.mp4",
            "2026-10-12_calorie-calculator/work/large/main.words.json", CAL_GRADE),
}
REPLACE = {"الأونلاين": "Online", "كوتشنج": "Coaching", "التبس": "Tips", "تتحافظ": "تحافظ"}
APP = HERE / "app"
STOCK = HERE / "stock"
BG = HERE / "bg_night.mp4"
APP_W, APP_TOP = 800, 150  # phone card in px; its bottom edge sits above the caption bar


def ensure_bg():
    """Static brand background for app moments: Deep Navy at the top easing into Night (no haze, no motion)."""
    if not BG.exists():
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=0x0A0F16:s=1080x1920:r=30:d=4",
                        "-vf", "geq=r='10+8*pow(1-Y/H\\,2)':g='15+17*pow(1-Y/H\\,2)':b='22+38*pow(1-Y/H\\,2)',format=yuv420p",
                        "-c:v", "libx264", "-crf", "8", str(BG)], check=True)


def rel(path, P):
    return str(Path("..") / Path(path).relative_to(PJ)) if Path(path).is_absolute() else str(Path("..") / path)


class Promo:
    def __init__(self, P, cap_top=0.70):
        self.P = Path(P)
        self.media, self.clips, self.overlays, self.cues = {}, [], [], []
        self.shakes, self.pulses, self.flashes, self.zones = [], [], [], []
        self.voice, self.words = [], []  # voice: (file, a, b, at); words in output time
        self.frame = 0
        self.cap_top = cap_top
        self._words = {}
        ensure_bg()

    # ---------------------------------------------------------------- time
    def t(self):
        return self.frame / FPS

    def _key(self, path):
        k = "m_" + Path(path).stem.replace("-", "_").replace(".", "_")[-40:]
        n, base = 1, k
        while k in self.media and self.media[k] != path:
            n += 1
            k = f"{base}_{n}"
        self.media[k] = path
        return k

    def _add(self, path, a, dur, tin=None, sfx=True, **kw):
        frames = round(dur * FPS)
        a = round(a * FPS) / FPS
        c = {"src": self._key(path), "in": round(a, 5), "out": round(a + frames / FPS, 5), **kw}
        if tin:
            c["tin"] = tin
        t0 = self.t()
        self.clips.append(c)
        self.frame += frames
        if tin and sfx:
            if tin["type"] == "whip":
                self.cues += [cue(t0, "whip", -12, dir=1.0), cue(t0 + 0.02, "air", -21)]
            else:
                self.cues += [cue(t0, "reverse_hit", -17, dur=0.4), cue(t0, "boom", -13)]
                self.shakes.append({"at": round(t0, 3), "amp": 0.4})
        return t0

    # ---------------------------------------------------------------- shots
    def gym(self, folder, name, a, dur, zoom=(1.0, 1.06), focusY=0.45, focusX=0.5, tin=None, speed=None, sfx=True):
        proj, grade = GYM[folder]
        kw = {"zoom": list(zoom), "focusX": focusX, "focusY": focusY, "grade": grade}
        if speed:
            kw["speed"] = speed
            t0 = self.t()
            frames = round(dur * FPS)
            c = {"src": self._key(f"../{proj}/source/{name}"), "in": round(a, 5), "out": round(a + frames * speed / FPS, 5), **kw}
            if tin:
                c["tin"] = tin
            self.clips.append(c)
            self.frame += frames
            if tin and sfx:
                self.cues += [cue(t0, "whip", -12, dir=1.0)] if tin["type"] == "whip" else [cue(t0, "boom", -13)]
            return t0
        return self._add(f"../{proj}/source/{name}", a, dur, tin=tin, sfx=sfx, **kw)

    def stock(self, name, a, dur, zoom=(1.0, 1.08), focusX=0.5, focusY=0.5, tin=None, sfx=True):
        """Free non-AI Coverr clip (landscape 1080p, cropped to 9:16)."""
        assert any(m["file"] == f"{name}.mp4" for m in json.loads((STOCK / "manifest.json").read_text())), name
        return self._add(f"../_mkt/stock/{name}.mp4", a, dur, tin=tin, sfx=sfx, zoom=list(zoom), focusX=focusX, focusY=focusY,
                         grade=GRADE)

    def talk(self, v, a, b, zoom=(1.0, 1.04), focusY=0.42, tin=None, lead=0.06, tail=0.1):
        """His face on screen, in sync with his own voice (source a..b, word edges padded)."""
        pic, snd, _, grade = VOICE[v]
        a0, b0 = a - lead, b + tail
        t0 = self._add(f"../{pic}", a0, b0 - a0, tin=tin, zoom=list(zoom), focusY=focusY, **({"grade": grade} if grade else {}))
        # the clip starts on a frame: take the sound from that same frame so lips and voice stay together
        c = self.clips[-1]
        self.say(v, c["in"], c["out"], at=t0, pad=0.0)
        return t0

    def app(self, flow, segs, region=(0.0, 0.035, 1.0, 0.72), taps=True, tin=None, highlights=(), width=APP_W,
            entrance="tilt", sfx=True, top=APP_TOP):
        """A real app recording (tools/app_record.js) as a phone card on the brand background.
        segs = [(recording_in, dur), ...] played back to back (real time); highlights = [(at, dur, (x, y, w, h))]."""
        x, y, w, h = region
        dur = round(sum(d for _, d in segs), 3)
        t0 = self._add(f"../{BG.relative_to(PJ).as_posix()}", 0.0, dur, tin=tin, sfx=sfx, freeze=True, zoom=1.0)
        key = self._key(f"../_mkt/app/{flow}.mp4")
        info = json.loads((APP / f"{flow}.json").read_text())
        tp, off = [], 0.0
        for a, d in segs:
            for k in info["taps"] if taps else []:
                ts = off + k["t"] - a
                if off + 0.2 <= ts <= off + d - 0.1 and x <= k["x"] <= x + w and y <= k["y"] <= y + h:
                    tp.append({"at": round(ts - 0.12, 3), "x": round((k["x"] - x) / w, 4), "y": round((k["y"] - y) / h, 4)})
                    self.cues.append(cue(t0 + ts - 0.12, "click", -18))
            off += d
        ov = {"type": "screenCard", "at": round(t0, 4), "dur": dur, "src": key, "plate": True, "backdrop": "none",
              "entrance": entrance, "width": width, "top": top, "region": {"x": x, "y": y, "w": w, "h": h},
              "segments": [{"in": a, "rate": 1, "dur": d} for a, d in segs], "taps": tp,
              "highlights": [{"at": round(hl[0], 3), "dur": round(hl[1], 3), "box": dict(zip("xywh", hl[2]))} for hl in highlights]}
        self.overlays.append(ov)
        card_bottom = (top + width * (h * 2532) / (w * 1170)) / 1920
        self.zones.append({"at": round(t0 - 0.05, 3), "dur": round(dur + 0.05, 3), "top": round(min(0.79, card_bottom + 0.012), 3)})
        if entrance == "tilt" and sfx and not tin:
            self.cues += [cue(t0, "whoosh_in", -15)]
        return t0

    # ---------------------------------------------------------------- voice
    def wordlist(self, v):
        if v not in self._words:
            d = json.loads((PJ / VOICE[v][2]).read_text())
            self._words[v] = [w for s in d["segments"] for w in s["words"]]
        return self._words[v]

    def span(self, v, first, last, nth_first=0, nth_last=0):
        """Source (start, end) of the words first..last (exact word text, nth occurrence)."""
        ws = self.wordlist(v)
        f = [w for w in ws if w["w"].strip("،.؟?!,") == first][nth_first]
        l_ = [w for w in ws if w["w"].strip("،.؟?!,") == last and w["start"] >= f["start"]][nth_last]
        return f["start"], l_["end"]

    def say(self, v, a, b, at=None, pad=0.06):
        """His voice from source a..b, placed at output time `at` (default: now). Captions follow the words."""
        at = self.t() if at is None else at
        a0, b0 = max(0.0, a - pad), b + pad
        self.voice.append((str((PJ / VOICE[v][1]).resolve()), a0, b0, at))
        for w in self.wordlist(v):
            mid = (w["start"] + w["end"]) / 2
            if a0 <= mid < b0:
                self.words.append({"w": w["w"], "start": round(at + max(w["start"], a0) - a0, 3),
                                   "end": round(at + min(w["end"], b0) - a0, 3)})
        return at + (b0 - a0)

    # ---------------------------------------------------------------- graphics
    def title(self, at, dur, lines, eyebrow=None, top=0.66, ink=None, sfx="boom", **kw):
        ov = {"type": "kineticTitle", "at": round(at, 3), "dur": round(dur, 3), "lines": lines, "top": top,
              "motion": "smooth", "depth": ink != "dark", **kw}
        if eyebrow:
            ov["eyebrow"] = eyebrow
        if ink:
            ov["ink"] = ink
        self.overlays.append(ov)
        if sfx == "boom":
            self.cues += [cue(at, "boom", -13), cue(at + 0.05, "impact", -20)]
        elif sfx:
            self.cues.append(cue(at, sfx, -16))

    def label(self, at, dur, title, eyebrow=None, top=0.6, plate=True, **kw):
        ov = {"type": "lowerLabel", "at": round(at, 3), "dur": round(dur, 3), "title": title, "top": top, "plate": plate, **kw}
        if eyebrow:
            ov["eyebrow"] = eyebrow
        self.overlays.append(ov)
        self.cues.append(cue(at, "click", -18))

    def icons(self, at, dur, items, top=0.55, size=200, sfx=True, **kw):
        self.overlays.append({"type": "iconPop", "at": round(at, 3), "dur": round(dur, 3), "items": items, "top": top, "size": size, **kw})
        if sfx:
            self.cues += [cue(at + 0.08 + 0.17 * i, "blip", -20, freq=700 + 120 * i) for i in range(len(items))]

    def badge(self, at, dur, mark, label, top=0.6, side="right", sub=None):
        ov = {"type": "stepBadge", "at": round(at, 3), "dur": round(dur, 3), "mark": mark, "label": label, "top": top,
              "side": side, "plate": True}
        if sub:
            ov["sub"] = sub
        self.overlays.append(ov)
        self.cues.append(cue(at, "slam", -16))

    # ---------------------------------------------------------------- output
    def _voice_track(self, T):
        """All voice lines on one track at their output times (15 ms fades at every edit)."""
        out = self.P / "work" / "vo.wav"
        out.parent.mkdir(parents=True, exist_ok=True)
        if not self.voice:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
                            "-t", f"{T:.3f}", "-c:a", "pcm_s24le", str(out)], check=True)
            return out
        inputs, parts = [], []
        for i, (f, a, b, at) in enumerate(self.voice):
            inputs += ["-i", f]
            d = b - a
            parts.append(f"[{i}:a:0]atrim=start={a:.4f}:duration={d:.4f},asetpts=PTS-STARTPTS,aresample=48000,"
                         f"aformat=channel_layouts=stereo,afade=t=in:d=0.015,afade=t=out:st={max(0, d - 0.015):.4f}:d=0.015,"
                         f"adelay={int(round(at * 1000))}:all=1[v{i}]")
        graph = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(self.voice))) + \
            f"amix=inputs={len(self.voice)}:normalize=0:duration=longest,apad[out]"
        # -t on the output (apad/atrim inside the graph did not stop after amix: the file grew without end)
        subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]", "-t", f"{T:.3f}",
                        "-c:a", "pcm_s24le", str(out)], check=True)
        return out

    def finish(self, title, keywords, music, voice_led=True):
        T = self.t()
        self.overlays.append(dict(end_card(T), image=END_IMAGE))
        self.cues += end_card_sfx(T)
        self.shakes.append({"at": round(T, 3), "amp": 0.6})
        self._voice_track(T + END_DUR)
        wf = self.P / "work" / "vo.words.json"
        wf.write_text(json.dumps({"segments": [{"words": self.words}]}, ensure_ascii=False))
        cap = {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "karaoke": True, "maxWords": 3,
               "maxChars": 22, "keywords": keywords, "replace": {k: v for k, v in REPLACE.items() if any(w["w"] == k for w in self.words)},
               "zones": sorted(self.zones, key=lambda z: z["at"]) + [{"at": 0, "dur": round(T + 0.01, 3), "top": self.cap_top}]}
        secs = music.get("sections") or [
            {"type": "intro", "until": round(min(1.6, T / 5), 3)}, {"type": "groove", "until": round(T * 0.5, 3)},
            {"type": "build", "until": round(T * 0.58, 3), "stop": True}, {"type": "drop", "until": round(T, 3)},
            {"type": "outro", "until": round(T + END_DUR, 3)}]
        mus = make_music(self.P, {"bpm": music.get("bpm", 124), "key": music.get("key", "E"), "mode": "minor",
                                  "style": music.get("style", "trap"), "seed": music.get("seed", 7), "sections": secs,
                                  "duration": round(T + END_DUR, 3)}, gain_db=music.get("gain", -9))
        if not voice_led:
            mus.update({"duck_ratio": 1, "voice_dip_db": 0})
        edit = {"title": title, "fps": FPS, "width": 1080, "height": 1920, "media": self.media,
                "plates": {"grade": None, "sharpen": "cas=strength=0.3"}, "clips": self.clips,
                "overlays": self.overlays, "shakes": self.shakes, "pulses": self.pulses, "flashes": self.flashes,
                "sfx": {"cues": sorted(self.cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
                "textPlate": TEXT_PLATE, "voiceTrack": "work/vo.wav", "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5",
                "dialogueLufs": -16.0}
        if self.words:
            edit["captions"] = cap
        fix_p = self.P / "headfix.json"  # no text on / above his head (projects/_b3/head_fix.py), re-applied on rebuild
        if fix_p.exists():
            sys.path.insert(0, str(PJ / "_b3"))
            from head_fix import apply, apply_captions
            fix = json.loads(fix_p.read_text())
            edit["overlays"] = apply(edit["overlays"], fix["fixes"])
            if self.words:
                apply_captions(edit["captions"], fix.get("captions", []), fix.get("caption_extra"))
        write_edit(self.P, edit)
        print(f"{self.P.name}: T={T:.2f}s (+{END_DUR} end card), {len(self.clips)} clips, {len(self.overlays)} overlays, "
              f"{len(self.voice)} voice lines, {len(self.words)} caption words")
        return T
