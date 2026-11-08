"""HDR-preserving edit engine for the 8 KM run videos (Coach Osama 2026-11-08).

Coach Osama: "keep the original footage colours EXACTLY; no grading / correction / filters". His iPhone footage is HLG (BT.2020,
10-bit), so the footage is cut, transitioned and encoded in its own 10-bit HLG YUV with NO colour processing (measured: a plain
re-encode differs by 1.75/1023 on average = codec noise). Only resizing (punch-ins) and FFmpeg's built-in transitions touch it.
OSM graphics (overlay.html, rendered RGBA by render_overlay.js) are converted sRGB -> HLG/BT.2020 at 203-nit graphics white
(BT.2408), colour and alpha separately (alpha kept full range), then overlaid. Dialogue = each clip's own AAC track (the APAC
spatial track of IMG_4920 is skipped), light clean-up only. SFX = tools/sfx.py via render_edit.build_mix. NO music.
Output: HEVC Main10 HLG (hvc1) 1080x1920 30 fps, AAC 48 kHz, -14 LUFS / -1 dBTP.
"""
import json, math, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_edit as R  # noqa: E402  (build_mix, master_audio, measure)

FPS = 30
SRC = {k: P / f"source/IMG_{k}.MOV" for k in ("4915", "4919", "4920", "4922", "4923", "4924", "4925", "4926")}
AIDX = {k: (2 if k == "4920" else 1) for k in SRC}          # AAC stream index (4920: stream 1 is Apple APAC)
GFX = ("format=rgba,split[c{n}][a{n}];[c{n}]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=tv:npl=203,"
       "format=yuv420p10le[cy{n}];[a{n}]alphaextract,format=gray10le[al{n}];[cy{n}][al{n}]alphamerge")
HDR_TAGS = ["-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv"]
X265 = "crf=12:preset=medium:pools=2:frame-threads=2:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error"
DIALOGUE_FX = "highpass=f=85,afftdn=nf=-32:nr=8:tn=1,equalizer=f=3000:t=q:w=1.2:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1.5"
fr = lambda x: round(x * FPS)                                  # seconds -> frames


def ff(args, **kw):
    return subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], check=True, **kw)


def plan(shots, tail):
    """Frame-exact timeline. shot: dict(src, a, b, speed=1, rev=False, z=(1,1), fx=.5, fy=.5, tin=None|(type, sec), mute=False, cap=True)."""
    out, L = [], 0
    for i, s in enumerate(shots):
        sp = s.get("speed", 1.0)
        n = fr((s["b"] - s["a"]) / sp)
        d = fr(s["tin"][1]) if (i and s.get("tin")) else 0
        st = L - d
        out.append(dict(s, n=n, d=d, start=st, len=n / FPS))
        L = st + n
    return out, L, L + fr(tail)


def shot_filter(s, inp="0:v"):
    sp, n = s.get("speed", 1.0), s["n"]
    f = [f"[{inp}]trim=start={s['a']:.4f}:end={s['a'] + n * sp / FPS + 0.2:.4f},setpts=PTS-STARTPTS"]
    if sp != 1:
        f.append(f"setpts=PTS/{sp}")
    f.append(f"fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS")
    if s.get("rev"):
        f.append("reverse,setpts=PTS-STARTPTS")          # after fps: only n frames are buffered
    z0, z1 = s.get("z", (1.0, 1.0))
    if z0 != 1 or z1 != 1:
        Z = f"({z0}+({z1}-{z0})*t/{max(s['len'], 1e-3):.4f})"
        f.append(f"scale=w='2*trunc(540*{Z})':h='2*trunc(960*{Z})':eval=frame:flags=lanczos,"
                 f"crop=1080:1920:x='(iw-1080)*{s.get('fx', .5)}':y='(ih-1920)*{s.get('fy', .5)}'")
    f.append("format=yuv420p10le,setsar=1")
    return ",".join(f)


def render_segments(tl, W):
    """Pass 1: every shot alone -> visually lossless 10-bit HEVC (CRF 6, HLG tags, no colour conversion), low memory. Cached."""
    import hashlib
    seg = W / "seg"
    seg.mkdir(exist_ok=True)
    files = []
    for i, s in enumerate(tl):
        key = hashlib.sha1(json.dumps({k: s[k] for k in ("src", "a", "b", "n") if k in s} | {k: s.get(k) for k in ("speed", "rev", "z", "fx", "fy")},
                                      sort_keys=True, default=str).encode()).hexdigest()[:12]
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


def video_graph(tl, total_frames, ov_input, files):
    """Pass 2: join the lossless shots with transitions, then the OSM overlay (converted into HLG)."""
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
    # renumber timestamps continuously: xfade leaves gaps in the PTS, and the overlay syncs by time (that cut 2.2 s off the end)
    g.append(f"[{acc}]tpad=stop_mode=clone:stop={total_frames - end},trim=end_frame={total_frames},setpts=N/({FPS}*TB)[base]")
    oi = len(files)
    inputs += ["-thread_queue_size", "64", "-framerate", str(FPS), "-i", str(ov_input)]
    g.append(f"[{oi}:v]setpts=N/({FPS}*TB)," + GFX.format(n="o") + "[ov]")
    g.append("[base][ov]overlay=format=yuv420p10:shortest=1,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[vout]")
    return inputs, ";".join(g)


def dialogue(tl, total_frames, dst):
    inputs, g, labels, idx = [], [], [], {}
    for k in sorted({s["src"] for s in tl}):
        idx[k] = len(inputs) // 2; inputs += ["-i", str(SRC[k])]
    for i, s in enumerate(tl):
        if s.get("mute") or s.get("rev") or s.get("speed", 1.0) != 1:
            continue
        ln = s["n"] / FPS
        fi = max(0.012, s["d"] / FPS)
        nxt = tl[i + 1]["d"] / FPS if i + 1 < len(tl) else 0
        fo = max(0.012, nxt)
        gain = s.get("gain_db", 0)
        g.append(f"[{idx[s['src']]}:{AIDX[s['src']]}]atrim=start={s['a']:.4f}:end={s['a'] + ln:.4f},asetpts=PTS-STARTPTS,aresample=48000,"
                 f"aformat=channel_layouts=mono,volume={gain}dB,afade=t=in:d={fi:.3f},afade=t=out:st={max(0, ln - fo):.3f}:d={fo:.3f},"
                 f"adelay={round(s['start'] / FPS * 1000)}:all=1[a{i}]")
        labels.append(f"[a{i}]")
    tot = total_frames / FPS
    g.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad=whole_dur={tot:.4f},atrim=end={tot:.4f},{DIALOGUE_FX},"
             "aformat=channel_layouts=stereo[aout]")
    raw = dst.with_suffix(".raw.wav")
    ff([*inputs, "-filter_complex", ";".join(g), "-map", "[aout]", "-ar", "48000", "-c:a", "pcm_s24le", str(raw)])
    i, _ = R.measure(raw)
    ff(["-i", str(raw), "-af", f"volume={-16 - i:.2f}dB", "-c:a", "pcm_s24le", str(dst)])
    raw.unlink()


def captions(tl, words, keywords, max_words=3, max_chars=22, breaks=None):
    """Words of each un-muted, real-speed shot mapped to output time, grouped into 1-3 word phrases (break at gaps and cuts)."""
    groups = []
    for s in tl:
        if s.get("mute") or s.get("rev") or s.get("speed", 1.0) != 1 or not s.get("cap", True):
            continue
        ws = [(w, t) for w, t in words.get(s["src"], []) if s["a"] - 0.05 <= t < s["a"] + s["len"] - 0.12]
        allw = words.get(s["src"], [])
        cur = []
        for j, (w, t) in enumerate(ws):
            nx = next((t2 for w2, t2 in allw if t2 > t + 1e-6), t + 0.5)
            st = s["start"] / FPS + (t - s["a"])
            spoken = 0.2 + 0.075 * len(w)                       # estimated spoken length: lets real pauses break phrases
            en = min(s["start"] / FPS + s["len"], s["start"] / FPS + (min(nx, t + spoken) - s["a"]))
            item = {"w": w, "start": round(st, 3), "end": round(en, 3), "kw": w in keywords}
            forced = breaks and any(abs(t - bt) < 0.02 for bt in breaks.get(s["src"], ()))
            if cur and (forced or len(cur) >= max_words or sum(len(x["w"]) + 1 for x in cur) + len(w) > max_chars or st - cur[-1]["end"] > 0.35):
                groups.append(cur); cur = []
            cur.append(item)
        if cur:
            groups.append(cur)
    out = []
    for i, g in enumerate(groups):
        st, en = g[0]["start"], g[-1]["end"]
        if i + 1 < len(groups):
            en = min(max(en, st + 0.45), groups[i + 1][0]["start"])
        out.append({"start": st, "end": round(en, 3), "words": g})
    return out


def render(name, shots, words, keywords, titles, hud, lower_third, cues, tail=2.4, caps_off=(), breaks=None):
    W = P / "work" / name
    W.mkdir(parents=True, exist_ok=True)
    tl, end_f, total_f = plan(shots, tail)
    caps = captions(tl, words, keywords, breaks=breaks)
    spec = {"dur": total_f / FPS, "captions": caps, "capTop": 1420, "capLow": [[t["at"], t["at"] + t["dur"]] for t in titles], "titles": titles, "hud": hud, "lowerThird": lower_third,
            "end": {"at": end_f / FPS}, "capsOff": list(caps_off) + [[end_f / FPS, 999]]}
    (W / "overlay_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    (W / "timeline.json").write_text(json.dumps({"total": total_f / FPS, "end_card": end_f / FPS,
                                                 "shots": [{k: v for k, v in s.items()} for s in tl]}, indent=1, default=str))
    print(f"{name}: {len(tl)} shots, picture {end_f / FPS:.2f}s + end card = {total_f / FPS:.2f}s, {len(caps)} caption phrases", flush=True)
    return W, tl, end_f, total_f, spec


def encode(name, W, tl, end_f, total_f, cues, preview=False):
    ov = W / "ov"
    import hashlib
    h = hashlib.sha256((W / "overlay_spec.json").read_bytes() + (P / "overlay.html").read_bytes()).hexdigest()
    stamp = ov / "_spec.sha256"
    if not (stamp.exists() and stamp.read_text() == h and (ov / f"f_{total_f - 1:05d}.png").exists()):
        subprocess.run(["node", str(P / "render_overlay.js"), str(W / "overlay_spec.json"), str(ov)], check=True)
        stamp.write_text(h)
    files = render_segments(tl, W)
    inputs, graph = video_graph(tl, total_f, ov / "f_%05d.png", files)
    # pass 2a: shots + transitions + end-card padding -> one visually lossless 10-bit file (exactly total_f frames)
    base = W / "base.mkv"
    gb = ";".join(x for x in graph.split(";") if not any(k in x for k in ("[ov]", "[co]", "[ao]", "alphamerge", "alphaextract", "zscale", "[vout]")))
    ff([*inputs[:4 * len(files)], "-filter_complex", gb, "-map", "[base]", "-frames:v", str(total_f), "-c:v", "libx265", "-pix_fmt", "yuv420p10le",
        "-x265-params", "crf=6:preset=fast:pools=2:frame-threads=1:log-level=error", "-tag:v", "hvc1", *HDR_TAGS, str(base)])
    nb = count_frames(base)
    assert nb == total_f, f"base has {nb} frames, expected {total_f}"
    # pass 2b: OSM overlay (sRGB -> HLG/BT.2020, alpha kept full range) on the base, final HEVC Main10 HLG
    raw = W / f"{name}_video.mp4"
    x265 = X265.replace("crf=12", "crf=20").replace("preset=medium", "preset=faster") if preview else X265
    g2 = (f"[0:v]setpts=N/({FPS}*TB),tpad=stop_mode=clone:stop=3[b];[1:v]setpts=N/({FPS}*TB)," + GFX.format(n="o") + "[ov];"
          "[b][ov]overlay=format=yuv420p10:eof_action=repeat,setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv[vout]")
    ff(["-i", str(base), "-thread_queue_size", "64", "-framerate", str(FPS), "-i", str(ov / "f_%05d.png"), "-filter_complex", g2, "-map", "[vout]",
        "-frames:v", str(total_f), "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params", x265, "-tag:v", "hvc1", *HDR_TAGS, str(raw)])
    nr = count_frames(raw)
    assert nr == total_f, f"video has {nr} frames, expected {total_f}"
    base.unlink()
    dlg = W / "dialogue.wav"
    dialogue(tl, total_f, dlg)
    mix = W / "mix.wav"
    placed = R.build_mix(dlg, cues, total_f / FPS, FPS, mix)
    final = P / "renders" / f"{name}.mp4"
    final.parent.mkdir(exist_ok=True)
    R.master_audio(mix, final, -14.0, -1.0, video=raw)
    raw.unlink()
    print(f"{name}: {len(placed)} sfx cues; output {final}", flush=True)
    return final


def sheet(video, dst, every=2.0, cols=10, w=216):
    tm = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
    font = "/tmp/claude-0/-home-user-Reel-editor/412088e3-e25e-56de-89cf-cf38f3a05bbc/scratchpad/inter.ttf"
    ff(["-i", str(video), "-vf", f"fps=1/{every},{tm},scale={w}:-2,drawtext=fontfile={font}:text='%{{pts\\:hms}}':x=4:y=4:fontsize=15:fontcolor=yellow:box=1:boxcolor=black,"
        f"tile={cols}x8", "-frames:v", "1", str(dst)])


_ENV = {}


def snap(src, t, win=0.15, side="out"):
    """Move a cut point to the quietest 10 ms (voice band) near t, so cuts fall between words. side="in": only earlier
    (t-win .. t+0.02), never into the first word; side="out": t-0.04 .. t+0.08, never into the next word."""
    import numpy as np
    if src not in _ENV:
        a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC[src]), "-map", f"0:{AIDX[src]}", "-af", "highpass=f=200,lowpass=f=3500",
                            "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(a, np.int16).astype(float) / 32768
        _ENV[src] = np.array([np.sqrt(np.mean(x[i:i + 160] ** 2)) for i in range(0, len(x) - 160, 160)])
    e = _ENV[src]
    lo, hi = (t - win, t + 0.02) if side == "in" else (t - 0.04, t + 0.08)
    i0, i1 = max(0, int(lo * 100)), min(len(e) - 1, int(hi * 100))
    if i1 <= i0:
        return t
    return round((i0 + int(e[i0:i1 + 1].argmin())) / 100 + 0.005, 3)


def out_time(tl, src, t):
    """Output time of source time t (first shot that contains it at real speed)."""
    for s in tl:
        if s["src"] == src and not s.get("rev") and s["a"] <= t < s["a"] + s["len"] * s.get("speed", 1):
            return round(s["start"] / FPS + (t - s["a"]) / s.get("speed", 1), 3)
    raise KeyError((src, t))


def chin_y(tl, t_out, samples=3, dur=0.6):
    """Lowest chin (output px) of his face over [t_out, t_out+dur]: YuNet on the source frame, mapped through the shot's zoom/crop.
    Used to keep every title clear of his face. Returns 0 when no face is found (e.g. the watch close-up)."""
    import cv2, numpy as np
    det = cv2.FaceDetectorYN.create(str(Path.home() / ".cache/osm-models/yunet.onnx"), "", (540, 960), 0.6, 0.3, 50)
    worst = 0
    for k in range(samples):
        t = t_out + dur * k / max(1, samples - 1)
        s = next((s for s in reversed(tl) if s["start"] / FPS <= t), tl[0])
        lt = min(max(0.0, t - s["start"] / FPS), s["len"] - 0.01)
        sp = s.get("speed", 1.0)
        src_t = (s["a"] + (s["len"] - lt) * sp) if s.get("rev") else (s["a"] + lt * sp)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{src_t:.3f}", "-i", str(SRC[s["src"]]), "-frames:v", "1", "-vf",
                              "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,"
                              "format=bgr24,scale=540:960", "-f", "rawvideo", "-"], capture_output=True).stdout
        if len(raw) != 540 * 960 * 3:
            continue
        img = np.frombuffer(raw, np.uint8).reshape(960, 540, 3)
        _, faces = det.detect(img)
        if faces is None:
            continue
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])[:4] * 2          # source px (1080x1920)
        chin = y + h * 1.12                                                   # YuNet box ends near the lips/chin: add beard
        z0, z1 = s.get("z", (1.0, 1.0)); Z = z0 + (z1 - z0) * lt / max(s["len"], 1e-3)
        fy = s.get("fy", .5)
        out = chin * Z - (1920 * Z - 1920) * fy
        worst = max(worst, out)
    return round(worst)


def place_titles(tl, titles, cap_top=1545, gap=36):
    """Fit each title between his chin (+gap) and the caption bar; shrink the type when the space is short."""
    for ti in titles:
        chin = chin_y(tl, ti["at"] + 0.05, dur=min(ti["dur"], 1.5))
        n = len(ti["lines"]); eb = 50 if ti.get("eyebrow") else 0
        bottom = cap_top - 24
        top_min = max(chin + gap, 300)
        avail = bottom - top_min
        size = ti.get("size", 120)
        need = lambda sz: n * sz * 0.98 + eb + (12 if ti.get("hit") else 0)
        while need(size) > avail and size > 60:
            size -= 4
        ti["size"] = size
        ti["top"] = round(bottom - need(size))
        ti["chin"] = chin
    return titles


def count_frames(path):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets",
                               "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip())
