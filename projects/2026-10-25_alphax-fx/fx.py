"""AlphaX recap (Coach Osama's own edit, 2026-10-25): add transitions + SFX ONLY.

Every frame outside a transition window is passed through bit-identical as decoded (10-bit 4:2:0, HLG/BT.2020,
no colour conversion). Frame count, timing and cut points are unchanged. Transitions live only around the
19 existing cuts: a whip pan (mirrored edges, motion blur along the move) or an impact punch-in (scale settle).
The original audio track is digital silence (-91 dB); the SFX bed is the only sound.

    .venv/bin/python fx.py [--frames A-B]   (A-B = test range)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
import cv2

P = Path(__file__).resolve().parent
SRC = P / "source" / "original.mov"
W, H, N = 1080, 1920, 2047
FS = W * H * 3 // 2 * 2  # bytes per yuv420p10le frame
SFXDIR = P.parents[0] / "2026-10-23_alphax" / "work" / "sfx"
HIT = {"whip": .165, "whoosh_in": .527, "impact": 0, "boom": 0, "swell": .55, "air": .252, "thump": 0}
PLAN = json.loads((P / "plan.json").read_text())


def planes(buf):
    a = np.frombuffer(buf, np.uint16)
    y = a[:W * H].reshape(H, W)
    u = a[W * H:W * H * 5 // 4].reshape(H // 2, W // 2)
    v = a[W * H * 5 // 4:].reshape(H // 2, W // 2)
    return y, u, v


def shift_blur(p, axis, s0, s1, n=12):
    """Shift plane p along axis by s0..s1 (fraction of its size), mirrored edges, averaged = motion blur."""
    L = p.shape[axis]
    ext = np.concatenate([np.flip(p, axis), p, np.flip(p, axis)], axis=axis).astype(np.float32)
    acc = np.zeros(p.shape, np.float32)
    ss = np.linspace(s0, s1, n) if abs(s1 - s0) * L > 1 else [s1]
    for s in ss:
        o = int(round(L - s * L))
        o = min(max(o, 0), 2 * L)
        acc += np.take(ext, range(o, o + L), axis=axis)
    return np.clip(np.rint(acc / len(ss)), 0, 1023).astype(np.uint16)


def zoom(p, z):
    if z <= 1.0001:
        return p
    h, w = p.shape
    big = cv2.resize(p, (int(round(w * z)), int(round(h * z))), interpolation=cv2.INTER_CUBIC)
    y0, x0 = (big.shape[0] - h) // 2, (big.shape[1] - w) // 2
    return np.clip(big[y0:y0 + h, x0:x0 + w], 0, 1023).astype(np.uint16)


def effects():
    """frame index -> function(planes) for every frame inside a transition window."""
    fx = {}
    for t in PLAN["transitions"]:
        c, kind = t["cut"], t["kind"]
        if kind == "whip":
            k, D = t.get("k", 4), t.get("d", 0.35)
            axis = 1 if t["dir"] in "LR" else 0
            sg = 1 if t["dir"] in "RD" else -1
            for m in range(1, k + 1):          # outgoing shot accelerates away
                s0, s1 = sg * D * ((m - 1) / k) ** 2, sg * D * (m / k) ** 2
                fx[c - k - 1 + m] = ("whip", axis, s0, s1)
            for m in range(k):                 # incoming shot arrives from the other side and settles
                s0, s1 = -sg * D * ((k - m) / k) ** 2, -sg * D * ((k - m - 1) / k) ** 2
                fx[c + m] = ("whip", axis, s0, s1)
        else:                                  # punch: slight push into the cut, incoming shot settles from z
            z, k = t.get("z", 1.10), t.get("k", 6)
            for m, zz in enumerate([1.02, 1.045]):
                fx[c - 2 + m] = ("zoom", zz)
            for m in range(k):
                fx[c + m] = ("zoom", 1 + (z - 1) * (1 - m / k) ** 2)
    return fx


def apply(buf, e):
    y, u, v = planes(buf)
    if e[0] == "whip":
        _, axis, s0, s1 = e
        out = [shift_blur(y, axis, s0, s1), shift_blur(u, axis, s0, s1), shift_blur(v, axis, s0, s1)]
    else:
        out = [zoom(y, e[1]), zoom(u, e[1]), zoom(v, e[1])]
    return b"".join(o.tobytes() for o in out)


def video(a, b, dst):
    fx = effects()
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(SRC), "-vf", f"select='between(n,{a},{b})'", "-vsync", "0",
                            "-f", "rawvideo", "-pix_fmt", "yuv420p10le", "-"], stdout=subprocess.PIPE)
    x265 = ("crf=10:preset=slow:keyint=30:min-keyint=30:no-scenecut=1:colorprim=bt2020:transfer=arib-std-b67:"
            "colormatrix=bt2020nc:range=limited:repeat-headers=1:aud=1:hrd=0:log-level=error")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p10le", "-s", f"{W}x{H}",
                            "-r", "30", "-i", "-", "-c:v", "libx265", "-preset", "slow", "-x265-params", x265,
                            "-pix_fmt", "yuv420p10le", "-color_primaries", "bt2020", "-color_trc", "arib-std-b67",
                            "-colorspace", "bt2020nc", "-color_range", "tv", "-tag:v", "hvc1", str(dst)],
                           stdin=subprocess.PIPE)
    n, touched = a, 0
    while True:
        buf = dec.stdout.read(FS)
        if len(buf) < FS:
            break
        if n in fx:
            buf = apply(buf, fx[n]); touched += 1
        enc.stdin.write(buf)
        n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(f"frames {a}-{n - 1}: {n - a} written, {touched} inside transition windows")
    return sorted(fx)


def audio(dst, dur):
    cues = []
    for t in PLAN["transitions"]:
        tc = t["cut"] / 30.0
        for name, g in t["sfx"]:
            cues.append((tc, name, g))
    ins, fl = [], []
    for q, (tc, name, g) in enumerate(cues):
        ins += ["-i", str(SFXDIR / f"{name}.wav")]
        st = max(0.0, tc - HIT[name])
        fl.append(f"[{q}:a]aresample=44100,volume={g}dB,adelay={int(round(st * 1000))}|{int(round(st * 1000))}[s{q}]")
    fl.append("".join(f"[s{q}]" for q in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad,atrim=duration={dur}[a]")
    raw = P / "work" / "sfx_raw.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[a]", "-c:a", "pcm_f32le",
                    str(raw)], check=True)
    vd = subprocess.run(["ffmpeg", "-i", str(raw), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    peak = float(vd.split("max_volume: ")[1].split(" dB")[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    f"volume={PLAN['peak_db'] - peak:.2f}dB,aresample=176400,alimiter=limit={10 ** (PLAN['peak_db'] / 20):.3f}:"
                    "attack=1:release=50:level=false,aresample=44100", "-c:a", "aac", "-b:a", "256k", str(dst)], check=True)
    raw.unlink()


if __name__ == "__main__":
    (P / "work").mkdir(exist_ok=True)
    if "--frames" in sys.argv:
        a, b = map(int, sys.argv[sys.argv.index("--frames") + 1].split("-"))
        video(a, b, P / "work" / f"test_{a}_{b}.mov")
        sys.exit()
    v, au = P / "work" / "video.mov", P / "work" / "sfx.m4a"
    touched = video(0, N - 1, v)
    (P / "work" / "touched_frames.json").write_text(json.dumps(touched))
    audio(au, 68.241995)
    out = P / "renders" / "AlphaX_Recap_FX.mov"; out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-i", str(au), "-map", "0:v", "-map", "1:a", "-c", "copy",
                    "-tag:v", "hvc1", "-movflags", "+faststart", str(out)], check=True)
    print(out)
