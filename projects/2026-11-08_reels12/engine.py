"""HDR-preserving, voice-spine edit engine for the RAMP warm-up and speed Reels (Coach Osama 2026-11-08).

Built on projects/2026-11-08_run8k/engine.py (same colour contract: his iPhone HLG footage is cut, scaled and encoded in its own
10-bit HLG YUV, no grade / correction / filter; only the OSM graphics are converted sRGB -> HLG at 203-nit graphics white).
New here, for fast editing:
  * VOICE SPINE: his lines are a list of source ranges played back to back (dead air removed). Output times come from the spine.
  * PICTURE: a separate list of shots that tile the timeline by `until` times. A shot is either `sync` (his talking picture, kept in
    lip sync with the spine and split automatically at every spine cut, alternating punch-ins hide the jump cuts) or B-roll
    (any source, any speed: 120 fps footage gives real slow motion; `ramp` steps the speed, e.g. 1.4x into 0.3x).
  * MUSIC: an original track from tools/music.py (no licences), ducked under his voice by render_edit.build_mix.
Output: HEVC Main10 HLG (hvc1) 1080x1920 30 fps, AAC 48 kHz, -14 LUFS / -1 dBTP.
"""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_edit as R  # noqa: E402

FPS = 30
SRC = {k: P / f"source/{k}.mov" for k in ("1_a", "1_b", "1_c", "1_d", "1_e", "1_f", "1_g", "1_h", "2_a", "2_b", "2_c", "2_d", "2_e", "wu")}
SRC["box"] = ROOT / "library/broll/files/IMG_2257.MOV"          # his 120 fps box-jump clip (permanent B-roll library)
GFX = ("format=rgba,split[c{n}][a{n}];[c{n}]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,"
       "format=yuv420p10le[cy{n}];[a{n}]alphaextract,format=gray10le[al{n}];[cy{n}][al{n}]alphamerge")
HDR_TAGS = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
X265 = "crf=12:preset=medium:pools=2:frame-threads=2:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error"
DIALOGUE_FX = "highpass=f=85,afftdn=nf=-30:nr=10:tn=1,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-22dB:ratio=3:attack=6:release=100:makeup=2"
fr = lambda x: round(x * FPS)


def ff(args, **kw):
    return subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], check=True, **kw)


# ---------------------------------------------------------------- timeline
def spine_times(spine):
    """Output start (frame-exact) of each voice segment, played back to back."""
    out, T = [], 0
    for v in spine:
        n = fr(v["b"] - v["a"])
        st = max(T, fr(v["at"])) if v.get("at") is not None else T      # `at`: start this line on a beat (a short breath before it)
        out.append(dict(v, start=st, n=n))
        T = st + n
    return out, T


def voice_at(sp, t_out):
    """(src, source time) of the voice at output time t_out."""
    f = t_out * FPS
    for v in sp:
        if v["start"] <= f < v["start"] + v["n"]:
            return v, v["a"] + (f - v["start"]) / FPS
    nxt = [v for v in sp if v["start"] > f]
    if nxt:                                   # in a breath between lines: the next take, just before he speaks
        v = nxt[0]
        return v, max(0.0, v["a"] - (v["start"] - f) / FPS)
    v = sp[-1]
    return v, v["a"] + (f - v["start"]) / FPS


def plan(spine, picture, tail):
    """Picture shots tile [0, voice end] by `until` (output seconds, snapped to frames). A shot's transition `tin` starts it
    d frames before its boundary (the previous shot runs to the boundary), so boundaries never move. Sync shots are split at
    spine cuts; `alt` alternates the punch-in at every split."""
    sp, VT = spine_times(spine)
    bounds, t = [], 0
    for i, s in enumerate(picture):
        u = VT if s.get("until") is None else fr(s["until"])
        assert u > t, f"picture shot {i} ends at {u} <= {t}"
        bounds.append((t, u)); t = u
    assert t == VT, f"picture ends at {t} frames, voice at {VT}"
    tl = []
    for (b0, b1), s in zip(bounds, picture):
        d = fr(s["tin"][1]) if (tl and s.get("tin")) else 0
        if s.get("sync"):
            # split at spine cuts inside [b0 - d, b1)
            cuts = sorted({v["start"] for v in sp if b0 < v["start"] < b1})
            # a breath before a line belongs to that line's take (voice_at), so splitting at line starts is enough
            edges = [b0] + cuts + [b1]
            for j in range(len(edges) - 1):
                e0, e1 = edges[j], edges[j + 1]
                dj = d if j == 0 else 0
                st = e0 - dj
                v, a = voice_at(sp, e0 / FPS)          # the take that speaks from the boundary on
                a -= dj / FPS                          # its transition frames come from just before (same take, stays in sync after)
                hold = 0
                if a < 0:                              # the take starts on its first word: freeze its first frame through the transition
                    hold = min(dj, round(-a * FPS)); a = 0.0
                z = s.get("z", (1.0, 1.0))
                if s.get("alt") and j % 2 == 1:
                    z = s["alt"]
                tl.append(dict(src=v["src"], a=round(a, 4), speed=1.0, z=z, fx=s.get("fx", .5), fy=s.get("fy", .3), sync=True, hold=hold,
                               tin=s.get("tin") if j == 0 else None, d=dj, start=st, n=e1 - st))
        elif s.get("ramp"):
            # speed steps inside one B-roll shot: [(seconds of OUTPUT, speed), ...]; the last step fills the rest
            a = s["a"]; st = b0 - d; first = True
            steps = s["ramp"]
            rem = b1 - st
            for k, (dur, spd) in enumerate(steps):
                n = rem if k == len(steps) - 1 else min(rem, fr(dur))
                if n <= 0:
                    break
                tl.append(dict(src=s["src"], a=round(a, 4), speed=spd, z=s.get("z", (1.0, 1.0)), fx=s.get("fx", .5), fy=s.get("fy", .5),
                               tin=s.get("tin") if first else None, d=d if first else 0, start=st, n=n, rev=False))
                a += n * spd / FPS; st += n; rem -= n; first = False
        else:
            tl.append(dict(src=s["src"], a=s["a"], speed=s.get("speed", 1.0), z=s.get("z", (1.0, 1.0)), fx=s.get("fx", .5),
                           fy=s.get("fy", .5), tin=s.get("tin"), d=d, start=b0 - d, n=b1 - (b0 - d), rev=s.get("rev", False)))
    for s in tl:
        s["len"] = s["n"] / FPS
        s["b"] = round(s["a"] + (s["n"] - s.get("hold", 0)) * s["speed"] / FPS, 4)
    return tl, sp, VT, VT + fr(tail)


def shot_filter(s, inp="0:v"):
    sp, hold = s.get("speed", 1.0), s.get("hold", 0)
    n = s["n"] - hold
    f = [f"[{inp}]trim=start={s['a']:.4f}:end={s['a'] + n * sp / FPS + 0.2:.4f},setpts=PTS-STARTPTS"]
    if sp != 1:
        f.append(f"setpts=PTS/{sp}")
    f.append(f"fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS")
    if hold:
        f.append(f"tpad=start_mode=clone:start={hold},setpts=PTS-STARTPTS")
    if s.get("rev"):
        f.append("reverse,setpts=PTS-STARTPTS")
    z0, z1 = s.get("z", (1.0, 1.0))
    if z0 != 1 or z1 != 1:
        Z = f"({z0}+({z1}-{z0})*t/{max(s['len'], 1e-3):.4f})"
        f.append(f"scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,"
                 f"crop=1080:1920:x='(iw-1080)*{s.get('fx', .5)}':y='(ih-1920)*{s.get('fy', .5)}'")
    f.append("format=yuv420p10le,setsar=1")
    return ",".join(f)


def render_segments(tl, W):
    seg = W / "seg"
    seg.mkdir(exist_ok=True)
    files = []
    for i, s in enumerate(tl):
        key = hashlib.sha1(json.dumps({k: s.get(k) for k in ("src", "a", "n", "speed", "rev", "z", "fx", "fy", "hold")}, sort_keys=True, default=str).encode()).hexdigest()[:12]
        f = seg / f"s{i:02d}_{key}.mkv"
        if not f.exists():
            ff(["-threads", "2", "-i", str(SRC[s["src"]]), "-filter_complex", shot_filter(s) + "[v]", "-map", "[v]", "-an",
                "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", "crf=6:preset=fast:pools=2:frame-threads=1:log-level=error",
                "-tag:v", "hvc1", *HDR_TAGS, "-r", str(FPS), str(f)])
        files.append(f)
    for old in seg.glob("*.mkv"):
        if old not in files:
            old.unlink()
    return files


def base_graph(tl, total_frames, files):
    g, inputs = [], []
    for i, f in enumerate(files):
        inputs += ["-threads", "1", "-i", str(f)]
        g.append(f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
    acc = "v0"
    for i in range(1, len(tl)):
        s = tl[i]
        if s["d"] > 0:
            g.append(f"[{acc}][v{i}]xfade=transition={s['tin'][0]}:duration={s['d'] / FPS:.4f}:offset={s['start'] / FPS:.4f}[x{i}]")
        else:
            g.append(f"[{acc}][v{i}]concat=n=2:v=1:a=0[x{i}]")
        acc = f"x{i}"
    end = tl[-1]["start"] + tl[-1]["n"]
    g.append(f"[{acc}]tpad=stop_mode=clone:stop={total_frames - end},trim=end_frame={total_frames},setpts=N/({FPS}*TB)[base]")
    return inputs, ";".join(g)


# ---------------------------------------------------------------- audio
def dialogue(sp, total_frames, dst):
    """His voice: spine segments back to back, 8 ms fades only at real cuts, light clean-up, -16 LUFS."""
    inputs, g, labels, idx = [], [], [], {}
    for k in sorted({v["src"] for v in sp}):
        idx[k] = len(inputs) // 2; inputs += ["-i", str(SRC[k])]
    for i, v in enumerate(sp):
        ln = v["n"] / FPS
        g.append(f"[{idx[v['src']]}:1]atrim=start={v['a']:.4f}:end={v['a'] + ln:.4f},asetpts=PTS-STARTPTS,aresample=48000,"
                 f"aformat=channel_layouts=mono,volume={v.get('gain_db', 0)}dB,afade=t=in:d=0.008,afade=t=out:st={max(0, ln - 0.008):.4f}:d=0.008,"
                 f"adelay={round(v['start'] / FPS * 1000)}:all=1[a{i}]")
        labels.append(f"[a{i}]")
    tot = total_frames / FPS
    g.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad=whole_dur={tot:.4f},atrim=end={tot:.4f},{DIALOGUE_FX},"
             "aformat=channel_layouts=stereo[aout]")
    raw = dst.with_suffix(".raw.wav")
    ff([*inputs, "-filter_complex", ";".join(g), "-map", "[aout]", "-ar", "48000", "-c:a", "pcm_s24le", str(raw)])
    i, _ = R.measure(raw)
    ff(["-i", str(raw), "-af", f"volume={-16 - i:.2f}dB", "-c:a", "pcm_s24le", str(dst)])
    raw.unlink()


# ---------------------------------------------------------------- captions
def captions(sp, words, keywords, max_words=3, max_chars=22, breaks=None):
    groups = []
    for v in sp:
        if v.get("cap") is False:
            continue
        allw = words.get(v["src"], [])
        ws = [(w, t) for w, t in allw if v["a"] - 0.05 <= t < v["a"] + v["n"] / FPS - 0.1]
        cur = []
        for w, t in ws:
            nx = next((t2 for w2, t2 in allw if t2 > t + 1e-6), t + 0.5)
            st = max(v["start"] / FPS, v["start"] / FPS + (t - v["a"]))
            spoken = 0.2 + 0.075 * len(w)
            en = min((v["start"] + v["n"]) / FPS, v["start"] / FPS + (min(nx, t + spoken) - v["a"]))
            item = {"w": w, "start": round(st, 3), "end": round(en, 3), "kw": w in keywords}
            forced = breaks and any(abs(t - bt) < 0.02 for bt in breaks.get(v["src"], ()))
            if cur and (forced or len(cur) >= max_words or sum(len(x["w"]) + 1 for x in cur) + len(w) > max_chars or st - cur[-1]["end"] > 0.3):
                groups.append(cur); cur = []
            cur.append(item)
        if cur:
            groups.append(cur)
    out = []
    for i, g in enumerate(groups):
        st, en = g[0]["start"], g[-1]["end"]
        if i + 1 < len(groups):
            en = min(max(en, st + 0.4), groups[i + 1][0]["start"])
        out.append({"start": st, "end": round(en, 3), "words": g})
    return out


def out_time(sp, src, t):
    """Output time of source time t in the voice spine."""
    for v in sp:
        if v["src"] == src and v["a"] - 1e-6 <= t < v["a"] + v["n"] / FPS:
            return round(v["start"] / FPS + (t - v["a"]), 3)
    raise KeyError((src, t))


# ---------------------------------------------------------------- face-aware layout
_FACE = {}


def chin_y(tl, t_out, dur=0.6, step=0.1, cap=30):
    """Lowest chin (output px, beard included = 1.22 x face box) of his face over [t_out, t_out+dur]; 0 if no face."""
    import cv2, numpy as np
    det = _FACE.get("det") or cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (540, 960), 0.6, 0.3, 50)
    _FACE["det"] = det
    worst = 0
    samples = max(2, min(cap, int(dur / step) + 1))
    for k in range(samples):
        t = t_out + dur * k / max(1, samples - 1)
        f = t * FPS
        s = next((s for s in reversed(tl) if s["start"] <= f), tl[0])
        lt = min(max(0.0, (f - s["start"]) / FPS), s["len"] - 0.01)
        src_t = s["a"] + lt * s.get("speed", 1.0)
        key = (s["src"], round(src_t, 2))
        if key not in _FACE:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{src_t:.3f}", "-i", str(SRC[s["src"]]), "-frames:v", "1", "-vf",
                                  "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,"
                                  "format=bgr24,scale=540:960", "-f", "rawvideo", "-"], capture_output=True).stdout
            box = None
            if len(raw) == 540 * 960 * 3:
                _, faces = det.detect(np.frombuffer(raw, np.uint8).reshape(960, 540, 3))
                if faces is not None:
                    box = (max(faces, key=lambda q: q[2] * q[3])[:4] * 2).tolist()
            _FACE[key] = box
        box = _FACE[key]
        if not box:
            continue
        x, y, w, h = box
        z0, z1 = s.get("z", (1.0, 1.0)); Z = z0 + (z1 - z0) * lt / max(s["len"], 1e-3)
        out = (y + h * 1.22) * Z - (1920 * Z - 1920) * s.get("fy", .5)
        worst = max(worst, out)
    return round(worst)


def place_titles(tl, titles, cap_top=1420, gap=24):     # titles end above the caption bar (captions never move)
    for ti in titles:
        if ti.get("free"):            # full-frame card or a graphic placed by hand away from his face
            ti["skip"] = False; continue
        chin = chin_y(tl, ti["at"] + 0.03, dur=max(0.1, ti["dur"] - 0.06), step=0.067, cap=45)
        n = len(ti["lines"]); eb = 50 if ti.get("eyebrow") else 0
        bottom = ti.get("bottom", cap_top - 24)
        top_min = max(chin + gap, 300)
        size = ti.get("size", 120)
        need = lambda sz: n * sz * 0.98 + eb + (12 if ti.get("hit") else 0)
        while need(size) > bottom - top_min and size > 60:
            size -= 4
        ti["size"] = size
        ti["top"] = round(bottom - need(size))
        ti["chin"] = chin
        ti["skip"] = ti["top"] < chin + gap or size < 100
        if ti["skip"]:
            print(f"title skipped (no room under his face): {ti['lines']} at {ti['at']:.2f}s, chin {chin}", flush=True)
    return [t for t in titles if not t["skip"]]


def place_captions(tl, caps, top=1420, gap=30, low_max=1552):
    for g in caps:
        chin = chin_y(tl, g["start"] + 0.02, dur=max(0.1, g["end"] - g["start"] - 0.04))
        g["top"] = top if chin + gap <= top else min(low_max, chin + gap)
        g["chin"] = chin
    return caps


# ---------------------------------------------------------------- render
def render(name, spine, picture, words, keywords, spec_extra, tail=2.4, caps_off=(), breaks=None):
    W = P / "work" / name
    W.mkdir(parents=True, exist_ok=True)
    tl, sp, end_f, total_f = plan(spine, picture, tail)
    caps = place_captions(tl, captions(sp, words, keywords, breaks=breaks))
    titles = place_titles(tl, spec_extra.pop("titles", []))
    spec = {"dur": total_f / FPS, "captions": caps, "capTop": 1420, "titles": titles,
            "end": {"at": end_f / FPS}, "capsOff": list(caps_off) + [[end_f / FPS, 999]], **spec_extra}
    (W / "overlay_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    (W / "timeline.json").write_text(json.dumps({"total": total_f / FPS, "end_card": end_f / FPS, "shots": tl, "spine": sp}, indent=1, default=str))
    print(f"{name}: {len(tl)} shots, {len(sp)} voice cuts, picture {end_f / FPS:.2f}s + end card = {total_f / FPS:.2f}s, {len(caps)} caption phrases", flush=True)
    return W, tl, sp, end_f, total_f


def overlay_frames(W, total_f):
    ov = W / "ov"
    h = hashlib.sha256((W / "overlay_spec.json").read_bytes() + (P / "overlay.html").read_bytes()).hexdigest()
    stamp = ov / "_spec.sha256"
    if not (stamp.exists() and stamp.read_text() == h and (ov / f"f_{total_f - 1:05d}.png").exists()):
        subprocess.run(["node", str(P / "render_overlay.js"), str(W / "overlay_spec.json"), str(ov)], check=True)
        stamp.write_text(h)
    from PIL import Image
    for f in sorted(ov.glob("f_*.png")):          # opaque frames come out RGB: a format change resets the filter graph mid-stream
        with Image.open(f) as im:
            if im.mode == "RGBA":
                continue
            tmp = f.with_suffix(".tmp.png"); im.convert("RGBA").save(tmp)
        os.replace(tmp, f)
    return ov


def encode(name, W, tl, sp, end_f, total_f, cues, music=None, preview=False):
    ov = overlay_frames(W, total_f)
    base, stamp_b = W / "base.mkv", W / "base.plan"
    plan_key = json.dumps([[s.get(k) for k in ("src", "a", "n", "d", "start", "speed", "rev", "z", "fx", "fy", "tin", "hold")] for s in tl], default=str) + str(total_f)
    if not (base.exists() and stamp_b.exists() and stamp_b.read_text() == plan_key and count_frames(base) == total_f):
        files = render_segments(tl, W)
        inputs, gb = base_graph(tl, total_f, files)
        ff([*inputs, "-filter_complex", gb, "-map", "[base]", "-frames:v", str(total_f), "-c:v", "libx265", "-pix_fmt", "yuv420p10le",
            "-x265-params", "crf=6:preset=fast:pools=2:frame-threads=1:log-level=error", "-tag:v", "hvc1", *HDR_TAGS, str(base)])
        nb = count_frames(base)
        assert nb == total_f, f"base has {nb} frames, expected {total_f}"
        stamp_b.write_text(plan_key)
        shutil.rmtree(W / "seg", ignore_errors=True)
    raw = W / f"{name}_video.mp4"
    x265 = X265.replace("crf=12", "crf=20").replace("preset=medium", "preset=faster") if preview else X265
    g2 = (f"[0:v]settb=1/{FPS},setpts=N[b];[1:v]settb=1/{FPS},setpts=N," + GFX.format(n="o") + "[ov];"
          "[b][ov]overlay=format=yuv420p10:eof_action=repeat,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[vout]")
    ff(["-i", str(base), "-reinit_filter", "0", "-framerate", str(FPS), "-i", str(ov / "f_%05d.png"), "-filter_complex", g2, "-map", "[vout]",
        "-frames:v", str(total_f), "-r", str(FPS), "-fps_mode", "cfr", "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", x265, "-tag:v", "hvc1",
        *HDR_TAGS, str(raw)])
    nr = count_frames(raw)
    assert nr == total_f, f"video has {nr} frames, expected {total_f}"
    dlg = W / "dialogue.wav"
    dialogue(sp, total_f, dlg)
    mix = W / "mix.wav"
    placed = R.build_mix(dlg, cues, total_f / FPS, FPS, mix, music)
    final = P / "renders" / f"{name}{'_preview' if preview else ''}.mp4"
    final.parent.mkdir(exist_ok=True)
    R.master_audio(mix, final, -14.0, -1.0, video=raw)
    raw.unlink()
    print(f"{name}: {len(placed)} sfx cues; output {final}", flush=True)
    return final


def count_frames(path):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets",
                               "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip())


_ENV = {}


def snap(src, t, win=0.12, side="out"):
    """Move a voice cut to the quietest 10 ms (voice band) near t. side="in": t-win .. t+0.02; "out": t-0.04 .. t+0.08."""
    import numpy as np
    if src not in _ENV:
        a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC[src]), "-map", "0:1", "-af", "highpass=f=200,lowpass=f=3500",
                            "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(a, np.int16).astype(float) / 32768
        _ENV[src] = np.array([np.sqrt(np.mean(x[i:i + 160] ** 2)) for i in range(0, len(x) - 160, 160)])
    e = _ENV[src]
    lo, hi = (t - win, t + 0.02) if side == "in" else (t - 0.04, t + 0.08)
    i0, i1 = max(0, int(lo * 100)), min(len(e) - 1, int(hi * 100))
    if i1 <= i0:
        return t
    return round((i0 + int(e[i0:i1 + 1].argmin())) / 100 + 0.005, 3)


def sheet(video, dst, every=1.0, cols=10, w=180):
    tm = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
    font = str(ROOT / "brand/fonts/BarlowCondensed-Bold.ttf")
    ff(["-i", str(video), "-vf", f"fps=1/{every},{tm},scale={w}:-2,drawtext=fontfile={font}:text='%{{pts\\:hms}}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black,"
        f"tile={cols}x8", "-frames:v", "1", str(dst)])
