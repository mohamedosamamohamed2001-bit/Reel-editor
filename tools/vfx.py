#!/usr/bin/env python3
"""Claude Video Effects pack (vendor/claude-video-effects, MIT) wired into the OSM studio.

The pack's 42 effects are per-frame image effects that need the speaker's face position and a person matte.
In the studio they run on a clip's PLATE (the JPEG frame sequence render_edit.py makes), before Remotion
composites captions and overlays on top, so they are part of the normal render, not a separate tool.

    python3 tools/vfx.py list [--all] [--json]       effects usable under the OSM rules (--all: every effect + status)
    python3 tools/vfx.py describe NAME               options, needs, OSM status and the rule behind it
    python3 tools/vfx.py validate EDIT_OR_PLAN.json  check an edit.json (clips[].vfx) or a plan {"effects": [...]}
    python3 tools/vfx.py selftest                    synthetic checks only (no footage, no render)

In edit.json (needs top-level "plates"), per clip, times in clip-local OUTPUT seconds:
    "vfx": [{"fx": "lean-in", "start": 1.2, "end": 2.4, "zoom": 1.3}]
A blocked effect is refused unless the entry carries "osmOverride": "<why Coach Osama approved it>".

Adapter changes vs. upstream (the vendored fx.py itself only has its exec() hook disabled):
- Tracking uses the studio's MODNet matte (onnxruntime, ~/.cache/osm-models/modnet.onnx) + YuNet instead of MediaPipe,
  so no new dependency (MediaPipe has no wheels in our Python 3.13 venv).
- Sans/display fonts map to the OSM brand fonts (Inter, Barlow Condensed). Serif / hand / mono looks keep the pack's
  OFL fonts (flagged off-brand in the registry). Arabic text is refused: the pack draws one font per string.
- Frames are read and written at the plate's own size (8-bit SDR RGB, like every plate); HDR is not handled here.
"""
import argparse, hashlib, importlib.util, json, os, re, shutil, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "claude-video-effects"
REGISTRY = Path(__file__).resolve().with_name("vfx_effects.json")
MODELS = Path.home() / ".cache" / "osm-models"
BRAND_FONTS = ROOT / "brand" / "fonts"
ARABIC = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
TRACK_SHORT = 540        # tracking resolution (short side), as upstream
PAD = 0.5                # seconds tracked around each window, as upstream
_fx = None


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def load(brand_fonts=True):
    """Import the vendored fx.py once (module name osm_vendor_fx) with the OSM tracker and font map."""
    global _fx
    if _fx is not None:
        return _fx
    spec = importlib.util.spec_from_file_location("osm_vendor_fx", VENDOR / "scripts" / "fx.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if brand_fonts:
        inter = str(BRAND_FONTS / "Inter[opsz,wght].ttf")
        for k, w in {"bold": (32, 900), "ui": (24, 640), "uim": (24, 540), "uib": (32, 860),
                     "mont": (32, 700), "monts": (32, 600), "montb": (32, 800)}.items():
            m.FONT[k] = inter
            m.WGHT[k] = w
        m.FONT["anton"] = str(BRAND_FONTS / "BarlowCondensed-Bold.ttf")
        m.WGHT.pop("anton", None)
        m._fc.clear()
    m.Tracker = OsmTracker
    _fx = m
    return m


class OsmTracker:
    """Drop-in for fx.Tracker: same call signature and outputs (uint8 matte, (cx, cy, face_w) or None)."""

    def __init__(self, aw, ah):
        import cv2
        import onnxruntime as ort
        modnet = MODELS / "modnet.onnx"
        yunet = MODELS / "yunet.onnx"
        if not yunet.exists():
            yunet = VENDOR / "models" / "yunet.onnx"
        if not modnet.exists():
            raise RuntimeError(f"person matte model missing: {modnet} (see CLAUDE.md Dependencies: MODNet ONNX)")
        self.cv2 = cv2
        self.sess = ort.InferenceSession(str(modnet), providers=["CPUExecutionProvider"])
        self.fd = cv2.FaceDetectorYN.create(str(yunet), "", (aw, ah), 0.6, 0.3, 20)
        self.prev = None

    def _matte(self, rgb):
        cv2 = self.cv2
        h, w = rgb.shape[:2]
        ih = 512
        iw = max(32, int(round(ih * w / h / 32) * 32))
        x = (cv2.resize(rgb, (iw, ih), interpolation=cv2.INTER_AREA).astype(np.float32) / 127.5 - 1).transpose(2, 0, 1)[None]
        m = self.sess.run(None, {"input": x})[0][0, 0]
        return cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32)

    def __call__(self, rgb, ms):
        cv2, fx = self.cv2, _fx
        m = self._matte(rgb)
        m = fx.guided(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255, m)
        m = np.clip((m - 0.5) * 1.6 + 0.5, 0, 1)
        if self.prev is not None and self.prev.shape == m.shape:
            m = 0.65 * m + 0.35 * self.prev
        self.prev = m
        _, f = self.fd.detect(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        face = None
        if f is not None and len(f):
            r = max(f, key=lambda r: r[2] * r[3] * r[-1])
            face = (r[0] + r[2] / 2, r[1] + r[3] / 2, r[2])
        else:
            rows = np.where((m > 0.5).sum(1) > m.shape[1] * 0.01)[0]
            if len(rows):
                top = rows[0]
                band = m[top:top + max(4, int(m.shape[0] * 0.06))] > 0.5
                xs = np.where(band.any(0))[0]
                if len(xs):
                    fw = max(8.0, (xs.max() - xs.min()) * 0.8)
                    face = (float(xs.mean()), top + fw * 0.7, fw)
        return (m * 255).astype(np.uint8), face


def resolve(name):
    """'glitter' -> ('spotlight', 'sparkle'); aliases -> canonical name. Returns (effect, look|None, registry key)."""
    fx = load()
    n = str(name).lower().lstrip("/")
    reg = registry()
    if n in reg["looks"]:
        lk = reg["looks"][n]
        return lk["effect"], lk["look"], n
    n = fx.ALIASES.get(n, n)
    return n, None, n


def validate(plan, duration=None):
    """-> (errors, warnings) for a list of effect entries. duration: clip length in seconds (optional)."""
    fx, reg = load(), registry()
    errors, warns = [], []
    camera = {k for k, v in reg["effects"].items() if v["category"] == "camera"} | {"spotlight"}
    seen = []
    for i, d in enumerate(plan):
        tag = f"vfx[{i}]"
        if not isinstance(d, dict) or "fx" not in d:
            errors.append(f"{tag}: needs an 'fx' name"); continue
        name, look, key = resolve(d["fx"])
        tag = f"vfx[{i}] {d['fx']}"
        if name not in fx.EFFECTS or name not in reg["effects"]:
            errors.append(f"{tag}: unknown effect (python3 tools/vfx.py list --all)"); continue
        info = reg["effects"][name]
        look = d.get("look", look)
        status, rules, note = info["osm"], info["rules"], info["note"]
        if key in reg["looks"]:
            status, rules, note = reg["looks"][key]["osm"], reg["looks"][key]["rules"], reg["looks"][key]["note"]
        try:
            s, e = float(d.get("start", 0)), float(d.get("end", 0))
        except (TypeError, ValueError):
            errors.append(f"{tag}: start/end must be numbers"); continue
        if not e > s >= 0:
            errors.append(f"{tag}: needs 0 <= start < end (got {s}..{e})")
        if duration is not None and e > duration + 1e-6:
            errors.append(f"{tag}: ends at {e:.2f}s, after the clip ({duration:.2f}s)")
        if e - s > 0 and not 1.0 <= e - s <= 6.0:
            warns.append(f"{tag}: {e - s:.2f}s window (the pack is tuned for ~1.5-4 s)")
        # options: types and ranges from the registry; unknown keys are ignored by the pack, so flag them
        for k, v in d.items():
            if k in ("fx", "start", "end", "osmOverride", "look"):
                continue
            spec = info["options"].get(k)
            if spec is None:
                warns.append(f"{tag}: option '{k}' is not used by this effect")
                continue
            if isinstance(spec, list) and len(spec) == 2 and all(isinstance(x, (int, float)) for x in spec):
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    errors.append(f"{tag}: '{k}' must be a number in {spec}"); continue
                if not spec[0] <= fv <= spec[1]:
                    errors.append(f"{tag}: '{k}'={fv} outside {spec}")
            elif isinstance(spec, list) and v not in spec:
                errors.append(f"{tag}: '{k}' must be one of {spec}")
            elif spec in ("number", "int"):
                try:
                    float(v)
                except (TypeError, ValueError):
                    errors.append(f"{tag}: '{k}' must be a number")
            elif spec == "hex" and not re.fullmatch(r"#?[0-9A-Fa-f]{6}", str(v)):
                errors.append(f"{tag}: '{k}' must be a hex colour like #56A0FB")
            elif spec == "string" and ARABIC.search(str(v)):
                errors.append(f"{tag}: Arabic text in '{k}' is not supported by the pack's renderer (one font per string, "
                              "no Arabic glyphs); put Arabic text in the Remotion captions/titles instead")
        if "look" in d and isinstance(info["options"].get("look"), list) and d["look"] not in info["options"]["look"]:
            errors.append(f"{tag}: look must be one of {info['options']['look']}")
        # OSM policy
        conds = []
        if name == "apple-toggles" and d.get("pos") != "below":
            conds.append("apple-toggles needs pos=below (the default sits behind his head)")
        if name == "spotlight" and (d.get("text") or look == "sparkle"):
            conds.append("spotlight with text or look=sparkle puts a glowing word/rays behind his head")
        if name in ("locked-on",) and d.get("text"):
            conds.append("locked-on with a text tag puts text by his face")
        own = {"tier-list": ("item",), "checklist": ("text", "title")}.get(name)
        if "claude" in json.dumps(d, ensure_ascii=False).lower() or (own and not all(d.get(k) for k in own)):
            conds.append("third-party branding (the pack's default content says 'Claude'): give his own "
                         + ", ".join(own or ("text",)))
        if status == "blocked" or conds:
            why = "; ".join([reg["rules"][r] for r in rules] if status == "blocked" else conds)
            if d.get("osmOverride"):
                warns.append(f"{tag}: OSM rule overridden ({d['osmOverride']}): {why}")
            else:
                errors.append(f"{tag}: refused by OSM rules: {why}. Add \"osmOverride\": \"<his approval>\" only if Coach Osama asked for it.")
        elif status == "restricted":
            warns.append(f"{tag}: restricted: {note}")
        if name in camera:
            if any(o[1] < e and s < o[2] and o[0] not in camera for o in seen):
                warns.append(f"{tag}: camera effects should be listed before the effects they overlap (the pack applies in order)")
        seen.append((name, s, e))
    return errors, warns


def _hash(*parts):
    return hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:12]


def apply_frames(read, write, n, fps, plan, thumbs_from=None, images_root=None, log=print):
    """Run plan (validated entries, times in seconds from frame 0) over n frames.
    read(i) -> HxWx3 uint8 RGB, write(i, rgb) called only for frames an effect touches. Returns touched indices."""
    import cv2
    from PIL import Image
    fx = load()
    errors, _ = validate(plan, n / fps)
    if errors:
        raise ValueError("vfx plan invalid:\n  " + "\n  ".join(errors))
    entries = []
    for d in plan:
        name, look, _ = resolve(d["fx"])
        dd = {k: v for k, v in d.items() if k != "osmOverride"}
        dd["fx"] = name
        if look and "look" not in dd:
            dd["look"] = look
        if images_root and dd.get("images"):
            dd["images"] = str((Path(images_root) / dd["images"]).resolve())
        entries.append(dd)
    fxs = [fx.Fx(d, fps) for d in entries]
    h, w = read(0).shape[:2]
    if w <= h:
        aw = TRACK_SHORT; ah = int(round(aw * h / w / 2)) * 2
    else:
        ah = TRACK_SHORT; aw = int(round(ah * w / h / 2)) * 2
    inwin = lambda t: any(f.start - PAD <= t < f.end + PAD for f in fxs)
    trk, masks, faces = fx.Tracker(aw, ah), {}, []
    thumbs = []
    for j in range(10):
        i = int(n * (j + 0.5) / 10)
        thumbs.append(Image.fromarray(cv2.resize(read(i), (aw, ah), interpolation=cv2.INTER_AREA)))
    for i in range(n):
        t = i / fps
        if inwin(t):
            small = cv2.resize(read(i), (aw, ah), interpolation=cv2.INTER_AREA)
            m, f = trk(small, int(t * 1000))
            masks[i] = m
            faces.append(f)
        else:
            faces.append(None)
            trk.prev = None
    sm = fx.smooth(faces, fps)
    if sm is None:
        sm = np.tile([aw / 2, ah * 0.33, aw * 0.15], (n, 1))
    for f in fxs:
        if f.name in fx.CARD_FX:
            f.cards = fx.load_cards(f.o.get("images"), thumbs_from or thumbs)
    sc, touched = w / aw, []
    for i in range(n):
        t = i / fps
        act = [f for f in fxs if f.start <= t < f.end]
        if not act:
            continue
        c = fx.Ctx()
        c.W, c.H, c.t, c.fps = w, h, t, fps
        c.img = read(i).astype(np.float32) / 255.0
        m = masks.get(i)
        c.m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0 if m is not None else np.zeros((h, w), np.float32)
        fx_, fy_, fw_ = sm[min(i, len(sm) - 1)]
        c.fx, c.fy, c.fw = fx_ * sc, fy_ * sc, max(fw_ * sc, w * 0.05)
        for f in act:
            c.lt = t - f.start
            fx.EFFECTS[f.name][0](c, f)
        write(i, (np.clip(c.img, 0, 1) * 255 + 0.5).astype(np.uint8))
        touched.append(i)
    log(f"vfx: {len(fxs)} effect(s), {len(touched)} of {n} frames changed")
    return touched


def apply_to_plate(plate_dir, fps, plan, out_root, images_root=None, log=print):
    """Derived plate: <out_root>/<plate>_vfx<hash>/ with the same 00001.jpg.. numbering. Untouched frames are hard links
    to the original plate (pixel-identical); touched ones are re-encoded JPEG q100 4:4:4. Cached by plate + plan + engine."""
    import cv2
    plate_dir = Path(plate_dir)
    files = sorted(plate_dir.glob("*.jpg"))
    if not files:
        raise ValueError(f"vfx: no plate frames in {plate_dir}")
    engine = hashlib.sha1((VENDOR / "scripts" / "fx.py").read_bytes() + Path(__file__).read_bytes() + REGISTRY.read_bytes()).hexdigest()[:8]
    dst = Path(out_root) / f"{plate_dir.name}_vfx{_hash(str(plate_dir.resolve()), plan, engine, len(files))}"
    if (dst / ".done").exists():
        return dst
    tmp = dst.with_name(dst.name + ".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    read = lambda i: cv2.cvtColor(cv2.imread(str(files[i])), cv2.COLOR_BGR2RGB)
    params = [cv2.IMWRITE_JPEG_QUALITY, 100]
    if hasattr(cv2, "IMWRITE_JPEG_SAMPLING_FACTOR"):
        params += [cv2.IMWRITE_JPEG_SAMPLING_FACTOR, cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444]
    write = lambda i, rgb: cv2.imwrite(str(tmp / files[i].name), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), params)
    touched = set(apply_frames(read, write, len(files), fps, plan, images_root=images_root, log=log))
    for i, f in enumerate(files):
        if i not in touched:
            os.link(f, tmp / f.name)
    (tmp / ".done").write_text(json.dumps({"plate": str(plate_dir), "plan": plan, "touched": sorted(touched)}))
    tmp.rename(dst)
    return dst


def check_edit(edit, fps=None):
    """Validate every clips[].vfx of an edit dict. -> (errors, warnings)."""
    errs, warns = [], []
    fps = fps or edit.get("fps", 30)
    for ci, c in enumerate(edit.get("clips", [])):
        if not c.get("vfx"):
            continue
        if not edit.get("plates"):
            errs.append(f"clips[{ci}].vfx needs top-level \"plates\" (effects run on the clip's plate frames)")
        dur = (c["out"] - c["in"]) / (1 if c.get("freeze") else c.get("speed", 1))
        e, w = validate(c["vfx"], dur)
        errs += [f"clips[{ci}] {x}" for x in e]
        warns += [f"clips[{ci}] {x}" for x in w]
    return errs, warns


# ---------- CLI ----------
def _list(show_all, as_json):
    reg, fx = registry(), load()
    rows = [(k, v) for k, v in reg["effects"].items() if show_all or v["osm"] != "blocked"]
    if as_json:
        print(json.dumps({k: v for k, v in rows}, ensure_ascii=False, indent=1)); return
    for k, v in rows:
        print(f"{k:19s} {v['osm']:10s} {v['category']:11s} {fx.EFFECTS[k][1]}")
    if show_all:
        for k, v in reg["looks"].items():
            print(f"{k:19s} {v['osm']:10s} {'look':11s} = {v['effect']} look={v['look']}")
    print(f"\n{len(rows)} effect(s). approved = as is; restricted = see `describe`; blocked = breaks a locked OSM rule.")


def _describe(name):
    reg = registry()
    eff, look, key = resolve(name)
    if eff not in reg["effects"]:
        sys.exit(f"unknown effect '{name}'")
    info = dict(reg["effects"][eff])
    if key in reg["looks"]:
        info = {**info, **reg["looks"][key], "look": look}
    info["rulesText"] = {r: reg["rules"][r] for r in info.get("rules", [])}
    print(json.dumps({"effect": eff, **info}, ensure_ascii=False, indent=1))


def _validate(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if "clips" in d:
        e, w = check_edit(d)
    else:
        e, w = validate(d.get("effects", d) if isinstance(d, dict) else d)
    for x in w:
        print("WARN ", x)
    for x in e:
        print("ERROR", x)
    print("OK" if not e else f"{len(e)} error(s)")
    sys.exit(1 if e else 0)


def selftest():
    """Synthetic checks only: registry <-> engine, validation, tracker, every effect on synthetic frames, plate wiring."""
    import tempfile, cv2
    from PIL import Image
    fx, reg = load(), registry()
    ok, bad = [], []
    def check(name, cond, info=""):
        (ok if cond else bad).append(f"{name} {info}".strip())

    check("registry covers every engine effect", set(fx.EFFECTS) == set(reg["effects"]), str(set(fx.EFFECTS) ^ set(reg["effects"])))
    check("every registry rule is defined", all(r in reg["rules"] for v in reg["effects"].values() for r in v["rules"]))
    check("aliases resolve to real effects", all(fx.ALIASES[a] in fx.EFFECTS for a in fx.ALIASES))
    check("private exec hook disabled", "exec(open(_PRIV)" not in "".join(l for l in (VENDOR / "scripts/fx.py").read_text().splitlines() if not l.lstrip().startswith("#")))
    check("brand fonts mapped", fx.FONT["bold"].endswith("Inter[opsz,wght].ttf") and Path(fx.FONT["bold"]).exists() and Path(fx.FONT["anton"]).exists())
    check("all font files present", all(Path(p).exists() for p in fx.FONT.values()))
    # validation
    e, _ = validate([{"fx": "lean-in", "start": 1, "end": 2.5, "zoom": 1.3}], 5); check("valid plan passes", not e, str(e))
    e, _ = validate([{"fx": "nope", "start": 0, "end": 1}]); check("unknown effect refused", bool(e))
    e, _ = validate([{"fx": "backdrop-word", "start": 0, "end": 2, "text": "GO"}]); check("blocked effect refused", bool(e))
    e, w = validate([{"fx": "backdrop-word", "start": 0, "end": 2, "text": "GO", "osmOverride": "test"}]); check("override accepted with warning", not e and any("overridden" in x for x in w))
    e, _ = validate([{"fx": "lean-in", "start": 0, "end": 2, "zoom": 3}]); check("zoom > 2 refused", bool(e))
    e, _ = validate([{"fx": "reject-stamp", "start": 0, "end": 2, "text": "لا"}]); check("Arabic effect text refused", bool(e))
    e, _ = validate([{"fx": "lean-in", "start": 2, "end": 1}]); check("start >= end refused", bool(e))
    e, _ = validate([{"fx": "lean-in", "start": 0, "end": 9}], 5); check("window past clip refused", bool(e))
    e, _ = validate([{"fx": "apple-toggles", "start": 0, "end": 2, "text": "Sleep|Steps", "pos": "below"}]); check("apple-toggles pos=below allowed", not e, str(e))
    e, _ = validate([{"fx": "apple-toggles", "start": 0, "end": 2, "text": "Sleep|Steps"}]); check("apple-toggles default refused", bool(e))
    e, _ = validate([{"fx": "glitter", "start": 0, "end": 2}]); check("glitter look refused", bool(e))
    e, _ = validate([{"fx": "spotlight", "start": 0, "end": 2}]); check("spotlight without text allowed", not e, str(e))
    e, _ = validate([{"fx": "moody", "start": 0, "end": 2, "grade": "sepia"}]); check("bad enum refused", bool(e))
    # tracker on a synthetic image (a drawn figure: no person footage)
    img = np.full((960, 540, 3), 40, np.uint8)
    cv2.ellipse(img, (270, 300), (70, 90), 0, 0, 360, (200, 160, 140), -1)
    cv2.rectangle(img, (170, 390), (370, 900), (230, 120, 40), -1)
    try:
        trk = fx.Tracker(540, 960); m, f = trk(img, 0)
        check("OSM tracker runs (MODNet + YuNet)", m.shape == (960, 540) and m.dtype == np.uint8)
    except Exception as ex:
        check("OSM tracker runs (MODNet + YuNet)", False, repr(ex))
    # every effect on synthetic frames at 3 local times (in memory)
    W, H = 540, 960
    base = np.dstack([np.tile(np.linspace(0.15, 0.6, W, dtype=np.float32), (H, 1))] * 3)
    mask = np.zeros((H, W), np.float32); cv2.ellipse(mask, (270, 520), (150, 430), 0, 0, 360, 1, -1)
    thumbs = [Image.new("RGB", (270, 480), (60 + 15 * k, 90, 140)) for k in range(6)]
    texts = {"text": "ONE|TWO|THREE", "ticks": "0.3|0.8|1.2", "lines": "A|B|C", "images": None}
    failed = []
    for name, (fn, _) in fx.EFFECTS.items():
        looks = [None] + list(reg["effects"][name]["options"].get("look", []) if isinstance(reg["effects"][name]["options"].get("look"), list) else [])
        for lk in looks:
            d = {"fx": name, "start": 0.0, "end": 2.0}
            for k in ("text", "ticks", "lines"):
                if k in reg["effects"][name]["options"]:
                    d[k] = texts[k]
            if lk:
                d["look"] = lk
            e = fx.Fx(d, 30); e.cards = thumbs
            try:
                for lt in (0.05, 1.0, 1.9):
                    c = fx.Ctx(); c.W, c.H, c.fps, c.t, c.lt = W, H, 30.0, lt, lt
                    c.img = base.copy(); c.m = mask.copy(); c.fx, c.fy, c.fw = 270.0, 300.0, 140.0
                    fn(c, e)
                    assert c.img.shape == (H, W, 3) and np.isfinite(c.img).all()
            except Exception as ex:
                failed.append(f"{name}{'/' + lk if lk else ''}: {type(ex).__name__}: {ex}")
    check(f"all {len(fx.EFFECTS)} effects (+ looks) run on synthetic frames", not failed, "; ".join(failed[:5]))
    # plate wiring: synthetic JPEG frames (generated arrays, not footage)
    with tempfile.TemporaryDirectory() as td:
        pd = Path(td) / "plate_test"; pd.mkdir()
        for i in range(1, 31):
            fr = (base * 255).astype(np.uint8).copy(); cv2.circle(fr, (100 + 10 * i, 600), 30, (255, 255, 255), -1)
            cv2.imwrite(str(pd / f"{i:05d}.jpg"), fr)
        plan = [{"fx": "lean-in", "start": 0.3, "end": 0.7, "zoom": 1.3}]
        out = apply_to_plate(pd, 30, plan, Path(td), log=lambda *a: None)
        files = sorted(out.glob("*.jpg"))
        same = [i for i, f in enumerate(files) if os.path.samefile(f, pd / f.name)]
        check("derived plate keeps frame count", len(files) == 30)
        check("untouched frames are hard links (pixel-identical)", same and all(not 9 <= i < 21 for i in same) and len(same) == 18, f"{len(same)} linked")
        check("derived plate cached", apply_to_plate(pd, 30, plan, Path(td), log=lambda *a: None) == out)
        check("original plate untouched", len(list(pd.glob("*.jpg"))) == 30 and not any(pd.glob("*vfx*")))
    # render_edit wiring without FFmpeg: make_plates is fed a fake plate maker
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import render_edit as re_
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td); (proj / "src.mov").write_bytes(b"")
            pd = proj / "work" / "plates" / "p0"; pd.mkdir(parents=True)
            for i in range(1, 62):
                cv2.imwrite(str(pd / f"{i:05d}.jpg"), (base * 255).astype(np.uint8))
            saved = (re_._plate, re_.dims)
            re_._plate = lambda *a, **k: pd
            re_.dims = lambda p: (1080, 1920)
            try:
                edit = {"width": 540, "height": 960, "fps": 30, "media": {"main": "src.mov"}, "plates": {"grade": "format=yuv420p"},
                        "clips": [{"src": "main", "in": 0, "out": 2.0, "vfx": [{"fx": "lean-in", "start": 0.5, "end": 1.5, "zoom": 1.2}]}]}
                re_.make_plates(edit, proj)
                c0 = edit["clips"][0]
                check("render_edit applies clip vfx to the plate", "_vfx" in edit["media"][c0["src"]] and "vfx" not in c0, edit["media"][c0["src"]])
                bad_edit = {"width": 540, "height": 960, "fps": 30, "media": {"main": "src.mov"},
                            "clips": [{"src": "main", "in": 0, "out": 2.0, "vfx": [{"fx": "lean-in", "start": 0.5, "end": 1.5}]}]}
                e, _ = check_edit(bad_edit); check("vfx without plates refused", bool(e))
            finally:
                re_._plate, re_.dims = saved
    except Exception as ex:
        check("render_edit wiring", False, repr(ex))
    for x in ok:
        print("PASS", x)
    for x in bad:
        print("FAIL", x)
    print(f"\n{len(ok)} passed, {len(bad)} failed")
    return not bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--all", action="store_true"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("describe"); p.add_argument("name")
    p = sub.add_parser("validate"); p.add_argument("path")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "list":
        _list(a.all, a.json)
    elif a.cmd == "describe":
        _describe(a.name)
    elif a.cmd == "validate":
        _validate(a.path)
    else:
        sys.exit(0 if selftest() else 1)


if __name__ == "__main__":
    main()
