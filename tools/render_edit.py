#!/usr/bin/env python3
"""Render a project's edit.json with the OSM Remotion studio, master the audio, and run QA.

Usage:
    python3 tools/render_edit.py projects/<name> [--preview] [--frames A-B] [--no-master] [--lufs -14] [--tp -1]

projects/<name>/edit.json uses media KEYS instead of paths:
    "media":    {"main": "source/talk.mp4", "broll1": "source/set.mp4"}   (relative to the project folder)
    "clips":    [{"src": "main", "in": 0.4, "out": 12.8}, ...]
    "captions": {"wordsFile": "work/talk.words.json", "keywords": ["خطة"]}
    "overlays": [{"type": "insetCard", "src": "broll1", "in": 3, "at": 5, "dur": 4}, ...]
Media files are hard-linked (or copied) into studio/public/media/<name>/ (git-ignored); sources are never modified.

Optional "plates" (recommended for footage): {"grade": "<ffmpeg filters>", "sharpen": "cas=strength=0.4"}.
Each clip is then pre-framed by FFmpeg (crop at its zoom/focus -> grade -> Lanczos scale to the frame size ->
sharpen) into projects/<name>/work/plates/, so Remotion shows footage 1:1 instead of resampling 4K in the
browser (measured 2x softer). screenCard overlays with "plate": true are Lanczos-scaled to the card width.

Outputs (git-ignored): projects/<name>/renders/<name>[_preview].mp4 plus a _qa folder.
"""
import hashlib
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "studio"


def dims(path):
    """Display width/height of the first video stream (rotation-aware)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data=rotation", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    st = json.loads(r.stdout)["streams"][0]
    w, h = st["width"], st["height"]
    rot = next((abs(int(sd.get("rotation", 0))) for sd in st.get("side_data_list", [])), 0)
    return (h, w) if rot in (90, 270) else (w, h)


def jsround(x):
    """Math.round (halves up), to match the studio's frame maths exactly (Python's round() rounds halves to even)."""
    import math
    return int(math.floor(x + 0.5))


def first_frame(c, fps):
    """Source frame a clip starts on: round(in * fps). Contiguous clips telescope (next first = this first + frames)."""
    return jsround(c["in"] * fps)


def plate_frames(c, fps):
    """Output frames of a clip, as the studio plays it: round(out*fps) - round(in*fps) at speed 1 (and frozen/held),
    round((out - in) / speed * fps) for speed ramps. make_plates writes the plate's out so edit.ts clipFrames agrees."""
    sp = c.get("speed", 1)
    if sp == 1 or c.get("freeze"):
        return jsround(c["out"] * fps) - jsround(c["in"] * fps)
    return jsround((c["out"] - c["in"]) / sp * fps)


def _even(x):
    return max(2, int(round(x / 2)) * 2)


def _plate(src, dst_dir, vf, extra_in, extra_out, fps, complex_=False, more_inputs=()):
    """Write one plate as a JPEG image sequence (cached by a hash of source + filters + trim + fps).

    Image frames, not video: Remotion's <OffthreadVideo> frame extraction softened footage ~7x
    (face Laplacian variance 311 -> 44 on the same frame) while <Img> keeps it (JPEG q1 4:4:4).
    """
    key = hashlib.sha1(json.dumps([str(src), os.path.getmtime(src), vf, extra_in, extra_out, fps, "jpg-q1-444", complex_,
                                      [str(m) for m in more_inputs], [os.path.getmtime(m[-1]) for m in more_inputs]]).encode()).hexdigest()[:12]
    dst = dst_dir / f"{Path(src).stem}_{key}"
    done = dst / ".done"
    if not done.exists():
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        flt = ["-filter_complex", f"{vf},fps={fps},format=yuvj444p"] if complex_ else ["-vf", f"{vf},fps={fps},format=yuvj444p"]
        mi = [x for m in more_inputs for x in m]
        subprocess.run(["ffmpeg", "-y", "-v", "error", *extra_in, "-i", str(src), *mi, *extra_out, "-an",
                        *flt, "-q:v", "1", "-qmin", "1",
                        str(dst / "%05d.jpg")], check=True)
        done.write_text("ok")
    return dst


def _count(d):
    return len(list(Path(d).glob("*.jpg")))


def _cover_chain(covers, sw, sh, seek, idx):
    """FFmpeg filter steps that bake cover plates over burned-in text (source pixel space, before the crop).

    Each cover is a rounded Night plate over a heavily blurred copy of that region (frosted glass), so old text is
    gone in every frame of the plate, including frames that later move through a whip/zoom transition.
    kind "plate": rounded rect, Night 86 %. kind "fade": full-width band whose opacity ramps in from its top edge.
    """
    if not covers:
        return "", ""
    pre = f"[{idx}:v]split={len(covers) + 1}[cb0]" + "".join(f"[cp{i}]" for i in range(len(covers))) + ";"
    steps = []
    last = "cb0"
    for i, cv in enumerate(covers):
        x0, y0, x1, y1 = cv["box"]
        X, Y = _even(x0 * sw), _even(y0 * sh)
        Wd, Hd = _even((x1 - x0) * sw), _even((y1 - y0) * sh)
        a, b = cv["at"] - seek, cv["at"] + cv["dur"] - seek
        sigma = max(6, round(Hd * 0.18))
        if cv.get("kind") == "blur":
            # frosted blur only (no tint): the old text melts into the footage; feathered edges so there is no box
            f = max(4, round(min(Hd, Wd) * 0.3))
            alpha = f"255*clip(min(min(X,W-1-X),min(Y,H-1-Y))/{f},0,1)"
            sigma = max(8, round(Hd * 0.32))
            tint = 0.0
        elif cv.get("kind") == "fade":
            alpha = f"255*clip(Y/(H*0.45),0,1)"
            tint = 0.9
        else:
            r = max(6, round(min(Hd, Wd) * 0.28))
            alpha = (f"255*clip({r}+0.5-hypot(max(max({r}-X,X-(W-1-{r})),0),max(max({r}-Y,Y-(H-1-{r})),0)),0,1)")
            tint = cv.get("tint", 0.86)
        tint_f = f"drawbox=x=0:y=0:w=iw:h=ih:color=0x0A0F16@{tint}:t=fill," if tint > 0 else ""
        steps.append(f"[cp{i}]crop={Wd}:{Hd}:{X}:{Y},gblur=sigma={sigma}:steps=3,"
                     f"{tint_f}format=yuva444p,"
                     f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{alpha}'[cv{i}];"
                     f"[{last}][cv{i}]overlay={X}:{Y}:enable='between(t,{a:.3f},{b:.3f})'[co{i}]")
        last = f"co{i}"
    return pre + ";".join(steps), last


def _cover_chain_out(covers, crop, sw, sh, W, H, color, timing):
    """Cover plates drawn AFTER crop / grade / scale / sharpen, in output pixels, in an exact solid colour (edit
    "textPlate", e.g. the brand blue #56A0FB): drawn last so the grade can't shift the colour. Same rounded shapes,
    positions and timings as the Night plates (_cover_chain); opaque, so the old text under them stays hidden.
    timing(t_src) maps source seconds to the plate's own timestamps (None = always on, for held/frozen frames)."""
    x, y, cw, ch = crop
    sx, sy = W / cw, H / ch
    steps, last = [], "pb"
    hexc = color.lstrip("#")
    for i, cv in enumerate(covers):
        x0, y0, x1, y1 = cv["box"]
        X0, Y0 = max(0, (x0 * sw - x) * sx), max(0, (y0 * sh - y) * sy)
        X1, Y1 = min(W, (x1 * sw - x) * sx), min(H, (y1 * sh - y) * sy)
        X, Y, Wd, Hd = _even(X0), _even(Y0), _even(X1 - X0), _even(Y1 - Y0)
        if Wd < 4 or Hd < 4:
            continue
        if cv.get("kind") == "fade":
            alpha = "255*clip(Y/(H*0.45),0,1)"
        else:
            # radius as before: 28 % of the plate's short side (measured in source px), scaled to output px
            r = max(6, round(min((y1 - y0) * sh, (x1 - x0) * sw) * 0.28 * sx))
            alpha = (f"255*clip({r}+0.5-hypot(max(max({r}-X,X-(W-1-{r})),0),max(max({r}-Y,Y-(H-1-{r})),0)),0,1)")
        en = "" if timing is None else \
            f":enable='between(t,{timing(cv['at']):.3f},{timing(cv['at'] + cv['dur']):.3f})'"
        steps.append(f"color=c=0x{hexc}:s={Wd}x{Hd}:r=30,format=yuva444p,"
                     f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{alpha}'[pc{i}];"
                     f"[{last}][pc{i}]overlay={X}:{Y}:shortest=0:repeatlast=1{en}[po{i}]")
        last = f"po{i}"
    return steps, last


def make_plates(edit, proj):
    """Pre-frame every clip (and opted-in screen cards) with FFmpeg into image sequences. Mutates edit.

    Per clip (all optional): "speed" (2 = twice as fast; >1 blends source frames = natural motion blur, <1 blends
    neighbours, never motion-interpolates, so nobody's body is warped), "freeze": true (hold the frame at `in`
    for out-in seconds). Top-level "covers": [{"src", "at", "dur", "box": [x0,y0,x1,y1], "kind"}] in SOURCE time and
    source-frame fractions are baked into the plates; captions.anchors (output time + output-frame box) are derived
    so the new captions sit on the cover plates.
    """
    cfg = edit.get("plates")
    if not cfg:
        return
    W, H = edit["width"], edit["height"]
    media = edit["media"]
    out_dir = proj / "work" / "plates"
    grade = cfg.get("grade")
    sharpen = cfg.get("sharpen")
    scale = f"scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int"
    fps = edit["fps"]
    covers = edit.pop("covers", [])
    anchors = []
    out_frame = 0
    for i, c in enumerate(edit["clips"]):
        src = (proj / media[c["src"]]).resolve()
        sw, sh = dims(src)
        z = c.get("zoom", 1)
        z0, z1 = (z if isinstance(z, list) else (z, z))
        # same framing maths as studio/src/components/FramedVideo.tsx, evaluated at the clip's first zoom
        s = max(W / sw, H / sh) * z0
        cw, ch = _even(W / s), _even(H / s)
        x = min(max(c.get("focusX", 0.5) * sw - cw / 2, 0), sw - cw)
        y = min(max(c.get("focusY", 0.5) * sh - ch / 2, 0), sh - ch)
        speed = c.get("speed", 1)
        freeze = c.get("freeze", False)
        span = c["out"] - c["in"]
        n_out = plate_frames(c, fps)
        # frame-exact trim: start ON the frame the timeline shows at `in` (floor), not the next one
        # (a plain -ss picks the first frame AFTER `in`: measured 1 frame late after the cut)
        hold = c.get("hold")  # show the still frame at `hold` (source s) for this clip while its dialogue plays on
        first = jsround(hold * fps) if hold is not None else first_frame(c, fps)
        seek = (first - 0.25) / fps if first else 0
        if hold is not None:
            mine = [cv for cv in covers if cv["src"] == c["src"] and cv["at"] <= hold < cv["at"] + cv["dur"]]
        else:
            mine = [cv for cv in covers if cv["src"] == c["src"] and cv["at"] < c["out"] and cv["at"] + cv["dur"] > c["in"]]
        text_plate = edit.get("textPlate")  # exact solid colour for the plates, drawn after the grade
        # kind "anchor": position-only covers (caption placement), nothing is drawn or blurred
        drawn = [cv for cv in mine if cv.get("kind") != "anchor"]
        solid = [cv for cv in drawn if cv.get("kind") != "blur"] if text_plate else []
        bm = edit.get("blurMask")
        more = []
        if bm and c["src"] == bm.get("src", "main"):
            # one blur of the caption band, merged through the precomputed feathered mask (any number of phrases)
            y0b, bh = bm["band"]
            sig = bm.get("sigma", 16)
            dark = bm.get("darken", 0.12)
            more = [["-ss", f"{seek:.5f}", "-i", str((proj / bm["file"]).resolve())]] if first else [["-i", str((proj / bm["file"]).resolve())]]
            pre = (f"[0:v]split=2[bm0][bm1];[bm1]crop={sw}:{bh}:0:{y0b},gblur=sigma={sig}:steps=3,"
                   f"colorchannelmixer=rr={1-dark}:gg={1-dark}:bb={1-dark},format=yuva444p[bmb];"
                   f"[1:v]format=gray,scale={sw}:{bh}[bmm];[bmb][bmm]alphamerge[bma];"
                   f"[bm0][bma]overlay=0:{y0b}:shortest=0:eof_action=pass[bmo]")
            rest = [cv for cv in drawn if cv not in solid and cv.get("kind") != "blur"]
            if rest:
                p2, l2 = _cover_chain(rest, sw, sh, seek, 0)
                pre = pre + ";" + p2.replace("[0:v]", "[bmo]", 1)
                last = l2
            else:
                last = "bmo"
        else:
            pre, last = _cover_chain([cv for cv in drawn if cv not in solid], sw, sh, seek, 0)
        motion = []
        if freeze or hold is not None:
            motion = ["trim=end_frame=1", f"loop=loop={n_out + 1}:size=1:start=0", f"setpts=N/{fps}/TB"]
        elif speed > 1:
            k = max(2, min(6, round(speed)))
            motion = [f"tmix=frames={k}", f"setpts=(PTS-STARTPTS)/{speed}"]
        elif speed < 1:
            motion = [f"setpts=(PTS-STARTPTS)/{speed}", f"framerate=fps={fps}:interp_start=0:interp_end=255:scene=100"]
        chain = ",".join(f for f in [f"crop={cw}:{ch}:{_even(x)}:{_even(y)}", grade, *motion, f"fps={fps}", scale, sharpen] if f)
        vf = (pre + f";[{last}]" + chain) if pre else chain
        if text_plate and solid:
            if freeze or hold is not None:
                timing = None
            elif speed != 1:
                timing = lambda t: (t - seek) / speed
            else:
                timing = lambda t: t - seek
            steps, plast = _cover_chain_out(solid, (_even(x), _even(y), cw, ch), sw, sh, W, H, text_plate, timing)
            if steps:
                vf = (f"[0:v]{chain}[pb];" if not pre else pre + f";[{last}]" + chain + "[pb];") + ";".join(steps) + f";[{plast}]null"
                pre = "post"  # forces filter_complex below
        plate = _plate(src, out_dir, vf, ["-ss", f"{seek:.5f}"] if first else [], ["-frames:v", str(n_out + 1)], fps, more_inputs=more,
                       complex_=bool(pre))
        key = f"plate{i}"
        media[key] = str(plate.relative_to(proj))
        # caption anchors: cover boxes mapped into the output frame (zoom ramp taken at the clip's midpoint)
        zm = (1 + z1 / z0) / 2 if z1 != z0 else 1
        for cv in mine:
            if not cv.get("anchor", True):  # a plate over something other than old captions: captions don't sit on it
                continue
            bx = [((cv["box"][0] * sw - x) / cw - 0.5) * zm + 0.5, ((cv["box"][1] * sh - y) / ch - 0.5) * zm + 0.5,
                  ((cv["box"][2] * sw - x) / cw - 0.5) * zm + 0.5, ((cv["box"][3] * sh - y) / ch - 0.5) * zm + 0.5]
            t0 = 0 if hold is not None else max(cv["at"], c["in"]) - c["in"]
            t1 = span if hold is not None else min(cv["at"] + cv["dur"], c["out"]) - c["in"]
            if speed != 1 and not freeze:
                t0, t1 = t0 / speed, t1 / speed
            anchors.append({"at": round(out_frame / fps + t0, 4), "dur": round(t1 - t0, 4), "box": [round(v, 4) for v in bx]})
        out_frame += n_out
        # caption timing maps through orig: the same start frame and frame-exact length as picture and audio
        o_in = first_frame(c, fps) / fps
        c.update({"orig": {"in": o_in, "out": o_in + n_out / fps} if not freeze and speed == 1 else {"in": c["in"], "out": c["out"]},
                  # out chosen so edit.ts clipFrames gives exactly n_out frames
                  "src": key, "in": 0, "out": round(n_out / fps if (speed == 1 or freeze) else n_out * speed / fps, 6),
                  "focusX": 0.5, "focusY": 0.5,
                  "zoom": [1, round(z1 / z0, 4)] if z1 != z0 else 1})
        if freeze:
            c["speed"] = 1
        c.pop("hold", None)
    if anchors and edit.get("captions") is not None:
        edit["captions"]["anchors"] = anchors
    for j, o in enumerate(edit.get("overlays", [])):
        if o.get("type") == "screenCard" and o.get("plate"):
            src = (proj / media[o["src"]]).resolve()
            width = o.get("width", 920)
            plate = _plate(src, out_dir, f"scale={_even(width / o.get('region', {}).get('w', 1))}:-2:"
                                         "flags=lanczos+accurate_rnd+full_chroma_int", [], [], 60)
            media[f"screenplate{j}"] = str(plate.relative_to(proj))
            o["src"] = f"screenplate{j}"


def make_cutouts(edit, proj):
    """Behind-the-head titles (kineticTitle "occlude": true): person cut-outs (tools/cutout.py, MODNet) of exactly the
    plate frames under each such title, so the studio can draw him above the title and below the captions."""
    fps = edit["fps"]
    wins = [(jsround(o["at"] * fps), jsround(o["at"] * fps) + max(1, jsround(o["dur"] * fps)))
            for o in edit.get("overlays", []) if o.get("type") == "kineticTitle" and o.get("occlude")]
    if not wins:
        return
    start = 0
    for c in edit["clips"]:
        sp = c.get("speed", 1)
        n = jsround(c["out"] * fps) - jsround(c["in"] * fps) if sp == 1 else jsround((c["out"] - c["in"]) / sp * fps)
        parts = []
        for a, b in wins:
            lo, hi = max(a, start), min(b, start + n)
            if hi > lo:  # plate index of local frame k = round(in*fps) + k + 1 (FramedVideo)
                base = jsround(c["in"] * fps) + 1
                parts.append(f"{base + lo - start}-{base + hi - start - 1}")
        if parts:
            plate = (proj / edit["media"][c["src"]]).resolve()
            out = plate.parent / f"{plate.name}_fg"
            subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "tools/cutout.py"), str(plate), str(out),
                            "--frames", ",".join(parts)], check=True)
            c["fg_dir"] = str(out)
        start += n


def resolve(edit, proj, name):
    media = edit.pop("media", {})
    edit.pop("plates", None)
    link_dir = STUDIO / "public" / "media" / name
    link_dir.mkdir(parents=True, exist_ok=True)
    paths, sizes, seqs = {}, {}, {}
    if link_dir.exists():
        shutil.rmtree(link_dir)  # stale plates from earlier renders
    link_dir.mkdir(parents=True)
    for key, rel in media.items():
        src = (proj / rel).resolve()
        if not src.exists():
            raise SystemExit(f"media '{key}' not found: {src}")
        if src.is_dir():  # image-sequence plate
            link = link_dir / key
            if link.exists():
                shutil.rmtree(link)
            link.mkdir()
            for f in sorted(src.glob("*.jpg")):
                try:
                    os.link(f, link / f.name)
                except OSError:
                    shutil.copy2(f, link / f.name)
            first = sorted(src.glob("*.jpg"))[0]
            paths[key] = f"media/{name}/{key}"
            sizes[key] = dims(first)
            seqs[key] = _count(src)
            continue
        link = link_dir / f"{key}{src.suffix.lower()}"
        if link.is_symlink() or link.exists():
            link.unlink()
        # Remotion copies public/ when bundling and does not follow file symlinks:
        # hard-link (no extra disk, source untouched), or copy across filesystems.
        try:
            os.link(src, link)
        except OSError:
            shutil.copy2(src, link)
        paths[key] = f"media/{name}/{link.name}"
        sizes[key] = dims(src)

    def p(key):
        if key not in paths:
            raise SystemExit(f"unknown media key '{key}' (define it under \"media\")")
        return paths[key]

    for c in edit["clips"]:
        fg = c.pop("fg_dir", None)
        if fg:  # behind-the-head cut-outs: hard-link the PNGs next to the plate frames
            fl = link_dir / Path(fg).name
            fl.mkdir(exist_ok=True)
            for f in Path(fg).glob("*.png"):
                if not (fl / f.name).exists():
                    try:
                        os.link(f, fl / f.name)
                    except OSError:
                        shutil.copy2(f, fl / f.name)
            c["fg"] = f"media/{name}/{fl.name}"
        c["srcW"], c["srcH"] = sizes.get(c["src"], (None, None))
        if c["src"] in seqs:
            c["frames"] = {"count": seqs[c["src"]], "fps": edit["fps"]}
        c["src"] = p(c["src"])
    for o in edit.get("overlays", []):
        if "src" in o:
            o["srcW"], o["srcH"] = sizes.get(o["src"], (None, None))
            if o["src"] in seqs:
                o["frames"] = {"count": seqs[o["src"]], "fps": 60}
            o["src"] = p(o["src"])
        if o.get("type") == "split":
            for side in ("top", "bottom"):
                o[side]["src"] = p(o[side]["src"])
    cap = edit.get("captions")
    if cap and "wordsFile" in cap:
        data = json.loads((proj / cap.pop("wordsFile")).read_text())
        rep = cap.pop("replace", {})
        seqs = cap.pop("replaceSeq", [])  # [{"from": ["الويب", "سايت"], "to": "Website"}]: merges consecutive words
        words = [{"w": w["w"], "start": w["start"], "end": w["end"]} for s in data["segments"] for w in s["words"]]
        for sq in sorted(seqs, key=lambda q: -len(q["from"])):  # longest first
            n, out, i, hits = len(sq["from"]), [], 0, 0
            while i < len(words):
                if [w["w"] for w in words[i:i + n]] == sq["from"]:
                    out.append({"w": sq["to"], "start": words[i]["start"], "end": words[i + n - 1]["end"]})
                    i += n
                    hits += 1
                else:
                    out.append(words[i])
                    i += 1
            if not hits:
                raise SystemExit(f"captions.replaceSeq not found in transcript: {sq['from']}")
            words = out
        # replaceAt: fix ONE occurrence, found by its transcript start time (±0.06 s): new text and/or a corrected
        # start measured from the audio (transcript word edges can be off by 0.3–0.6 s around pauses)
        for fix in cap.pop("replaceAt", []):
            hit = [w for w in words if abs(w["start"] - fix["at"]) <= 0.06]
            if len(hit) != 1:
                raise SystemExit(f"captions.replaceAt matched {len(hit)} words at {fix['at']}s (need exactly 1)")
            if "to" in fix:
                hit[0]["w"] = fix["to"]
                hit[0]["fixed"] = True
            if "start" in fix:
                hit[0]["start"] = fix["start"]
        cap["words"] = [{"w": w["w"] if w.pop("fixed", False) else rep.get(w["w"], w["w"]), "start": w["start"], "end": w["end"]}
                        for w in words]
        hits = {k: sum(w["w"] == k for s in data["segments"] for w in s["words"]) for k in rep}
        missing = [k for k, n in hits.items() if n == 0]
        if missing:
            raise SystemExit(f"captions.replace keys not found in transcript: {missing}")
    return edit


def build_dialogue(clips, total, dst, fx=None, lufs=None):
    """Cut the dialogue straight from the sources with FFmpeg (sample-accurate, honours the AAC edit list).

    Remotion's audio path ignores the source's AAC priming edit list, which put the dialogue ~42 ms behind the
    picture on the first real edit (measured by cross-correlation). Video is rendered muted; this is the audio.
    Each clip gets 8 ms fades so cuts don't click.
    """
    # Clips that only change framing (same source, out == next in) are one continuous take: merge them,
    # otherwise the per-clip fades dip the audio mid-word at every punch-in.
    merged = []
    for c in clips:
        m = merged[-1] if merged else None
        if (m and m["path"] == c["path"] and abs(m["out"] - c["in"]) < 1e-6 and m["volume"] == c["volume"]
                and m.get("silent") == c.get("silent") and not c.get("silent")):
            m["out"] = c["out"]
            m["len"] = m["len"] + c["len"]
        else:
            merged.append(dict(c))
    clips = merged
    inputs, parts = [], []
    paths = sorted({c["path"] for c in clips})
    for p in paths:
        inputs += ["-i", p]
    for i, c in enumerate(clips):
        d = c["out"] - c["in"]
        if c.get("silent"):  # speed-ramped or frozen picture: no dialogue there (music + SFX carry it)
            parts.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={c['len']:.5f}[a{i}]")
            continue
        # start on the same source frame as the picture, and last exactly the clip's frame count, so sub-frame
        # differences can't accumulate into A/V drift across jump cuts
        d = c["len"]
        parts.append(f"[{paths.index(c['path'])}:a:0]atrim=start={c['start']:.6f}:duration={d:.6f},asetpts=PTS-STARTPTS,"
                     f"aresample=48000,aformat=channel_layouts=stereo,volume={c['volume']},"
                     f"afade=t=in:d=0.008,afade=t=out:st={max(0, d - 0.008):.3f}:d=0.008[a{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[a{i}]" for i in range(len(clips))) + \
        f"concat=n={len(clips)}:v=0:a=1{',' + fx if fx else ''},apad=whole_dur={total:.3f}[out]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-c:a", "pcm_s24le", str(dst)], check=True)
    if lufs is not None:
        # dialogue to a fixed loudness BEFORE the mix, so music/SFX gains mean the same thing in every video
        # (voice stems separated from different finished mixes came out between -10 and -17 LUFS)
        i, _ = measure(dst)
        if i > -50:
            tmp = Path(dst).with_suffix(".norm.wav")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(dst), "-af", f"volume={lufs - i:.2f}dB",
                            "-c:a", "pcm_s24le", str(tmp)], check=True)
            tmp.replace(dst)


def build_mix(dialogue, cues, total, fps, dst, music=None):
    """Dialogue + synthesised SFX bus (tools/sfx.py). The voice always wins:
    SFX bus is high-passed at 40 Hz, dipped -4 dB around 2.5 kHz (speech presence), and sidechain-ducked
    by the dialogue before the two are summed. Returns the cue placements (frame-snapped times)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import sfx as sfxkit
    bus, placed = sfxkit.render_cues(cues, total, fps)
    sfx_wav = Path(dst).with_suffix(".sfx.wav")
    sfxkit.write_wav(sfx_wav, bus)
    inputs = ["-i", str(dialogue), "-i", str(sfx_wav)]
    graph = ("[1:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=40,"
             "equalizer=f=2500:t=q:w=1.2:g=-4[s];")
    if music:
        # music bed (tools/music.py): voice-band dip, then ducked hard by the dialogue (4:1) so the voice always
        # wins; between lines it comes back up. Gain is the bed level relative to the -14 LUFS master.
        inputs += ["-i", str(music["path"])]
        graph += ("[0:a]asplit=3[d][dk][dk2];"
                  f"[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={total:.3f},apad=whole_dur={total:.3f},"
                  f"highpass=f=30,equalizer=f=2200:t=q:w=1.0:g={music.get('voice_dip_db', -4)},"
                  f"volume={music.get('gain_db', -8)}dB[m];"
                  f"[m][dk2]sidechaincompress=threshold={music.get('duck_threshold', 0.02)}:ratio={music.get('duck_ratio', 4)}:"
                  "attack=15:release=320:knee=4[md];"
                  "[s][dk]sidechaincompress=threshold=0.03:ratio=2:attack=10:release=180[sd];"
                  "[d][sd][md]amix=inputs=3:normalize=0:duration=first[out]")
    else:
        graph += ("[0:a]asplit=2[d][dk];"
                  "[s][dk]sidechaincompress=threshold=0.03:ratio=2:attack=10:release=180[sd];"
                  "[d][sd]amix=inputs=2:normalize=0:duration=first[out]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph,
                    "-map", "[out]", "-c:a", "pcm_s24le", str(dst)], check=True)
    sfx_wav.unlink()
    return placed


def measure(path):
    """Integrated loudness (LUFS) and true peak (dBTP) of the first audio stream, via ebur128."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a:0",
                          "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summ = err[err.rfind("Summary:"):]
    return (float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1)),
            float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1)))


def master_audio(src, dst, lufs, tp, video=None):
    """Gain to the loudness target + peak limiter, measured and corrected (max 3 rounds); video copied.

    Two-pass loudnorm in linear mode refuses gain it can't fit under the true-peak ceiling (first real
    edit: -15.2 LUFS). Here the gain is applied directly, a limiter 1 dB under the ceiling (alimiter is
    sample-peak, so the margin covers inter-sample peaks) holds the peaks, and the result is re-measured.
    """
    limit = 10 ** ((tp - 1.0) / 20)
    i0, _ = measure(src)  # src: any file with the dialogue as its first audio stream
    gain = lufs - i0
    tmp = Path(dst).with_suffix(".master.wav")  # stay uncompressed until the final mux (AAC delay handled once)
    for _ in range(3):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vn", "-af",
                        # 4x oversampling around the limiter = true-peak limiting (a 48 kHz sample-peak limiter let
                        # inter-sample overs through: -0.3 dBTP on the second video, which needed +8.9 dB of gain)
                        f"aresample=192000,volume={gain:.2f}dB,alimiter=limit={limit:.4f}:level=false:attack=2:release=60,"
                        "aresample=48000",
                        "-ar", "48000", "-c:a", "pcm_s24le", str(tmp)], check=True)
        i, peak = measure(tmp)
        if abs(i - lufs) <= 0.3 and peak <= tp:
            break
        gain += lufs - i
    print(f"audio master: {i0:.1f} -> {i:.1f} LUFS, true peak {peak:.1f} dBTP (gain {gain:+.1f} dB)", flush=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video or src), "-i", str(tmp), "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(dst)], check=True)
    tmp.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--preview", action="store_true", help="half resolution, faster")
    ap.add_argument("--frames", default=None, help="frame range, e.g. 0-150")
    ap.add_argument("--no-master", action="store_true")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--alt-nomusic", action="store_true", help="also write <name>_nomusic.mp4 (dialogue + SFX only)")
    a = ap.parse_args()

    proj = Path(a.project).resolve()
    name = proj.name
    edit = json.loads((proj / "edit.json").read_text())
    # dialogue always comes from the ORIGINAL sources and cut points, before any plate rewriting
    # "audio": {"main": "work/stems/x.vocals.wav"} swaps a media key's sound for another file (e.g. the dialogue
    # stem separated from a finished mix by tools/separate.py)
    amap = edit.pop("audio", {})
    fps = edit["fps"]
    audio_clips = []
    plated = bool(edit.get("plates"))
    for c in edit["clips"]:
        sp = c.get("speed", 1)
        silent = c.get("freeze", False) or sp != 1
        n = plate_frames(c, fps) if plated else jsround(c["out"] * fps) - jsround(c["in"] * fps)
        audio_clips.append({"path": str((proj / amap.get(c["src"], edit["media"][c["src"]])).resolve()), "in": c["in"],
                            "out": c["out"], "volume": c.get("volume", 1), "silent": silent,
                            # the picture starts on source frame round(in * fps): the audio starts there too
                            "start": first_frame(c, fps) / fps if plated else c["in"],
                            # exact timeline length in frames, so audio and picture can't drift apart
                            "len": n / fps})
    dialogue_fx = edit.pop("dialogueFx", None)
    dialogue_lufs = edit.pop("dialogueLufs", None)
    music = edit.pop("music", None)
    if music:
        music["path"] = str((proj / music["src"]).resolve())
    make_plates(edit, proj)
    make_cutouts(edit, proj)
    edit_sfx = edit.pop("sfx", None)
    edit = resolve(edit, proj, name)
    renders = proj / "renders"
    renders.mkdir(exist_ok=True)
    props = renders / "_props.json"
    props.write_text(json.dumps({"edit": edit}, ensure_ascii=False))

    suffix = "_preview" if a.preview else ""
    raw = renders / f"{name}{suffix}_raw.mp4"
    cmd = ["npx", "remotion", "render", "src/index.ts", "ReelEdit", str(raw), f"--props={props}",
           f"--concurrency={4}", "--log=error", "--muted"]
    if a.preview:
        cmd.append("--scale=0.5")
    if a.frames:
        cmd.append(f"--frames={a.frames}")
    print("rendering:", " ".join(cmd[2:5]), flush=True)
    subprocess.run(cmd, cwd=STUDIO, check=True)

    final = renders / f"{name}{suffix}.mp4"
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(raw)], capture_output=True, text=True, check=True).stdout)
    if a.frames:
        print("note: --frames renders a range; dialogue is built for the full cut list", flush=True)
    dialogue = renders / f"{name}{suffix}_dialogue.wav"
    build_dialogue(audio_clips, total, dialogue, dialogue_fx, dialogue_lufs)
    cues = (edit_sfx or {}).get("cues", [])
    alt = None
    if a.alt_nomusic and music:
        alt = renders / f"{name}{suffix}_nomusic_mix.wav"
        build_mix(dialogue, cues, total, edit["fps"], alt)
    if cues or music:
        mixed = renders / f"{name}{suffix}_mix.wav"
        placed = build_mix(dialogue, cues, total, edit["fps"], mixed, music)
        print(f"sfx: {len(placed)} cues placed on frame times" + (", music bed mixed" if music else ""), flush=True)
        (renders / "_sfx_placed.json").write_text(json.dumps(placed))
        dialogue.unlink()
        dialogue = mixed
    if alt:
        master_audio(alt, renders / f"{name}{suffix}_nomusic.mp4", a.lufs, a.tp, video=raw)
        alt.unlink()
    if a.no_master:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-i", str(dialogue), "-map", "0:v:0", "-map", "1:a:0",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(final)], check=True)
    else:
        master_audio(dialogue, final, a.lufs, a.tp, video=raw)
    raw.unlink()
    dialogue.unlink()
    print("output:", final, flush=True)

    w, h = (edit["width"] // 2, edit["height"] // 2) if a.preview else (edit["width"], edit["height"])
    qa = subprocess.run([sys.executable, str(ROOT / "tools" / "qa_render.py"), str(final), "--expect", f"{w}x{h}",
                         "--fps", str(edit["fps"]), "--lufs", str(a.lufs), "--tp", str(a.tp)])
    sys.exit(qa.returncode)


if __name__ == "__main__":
    main()
