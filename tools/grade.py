#!/usr/bin/env python3
"""Premium cinematic grade, shot by shot (docs/COLOR_GRADING.md): measured, not guessed.

    .venv/bin/python tools/grade.py SRC [--in A --out B] [--json]               print the FFmpeg grade chain + before/after metrics
    .venv/bin/python tools/grade.py SRC --in A --out B --compare DIR            before/after stills + scopes for 3 frames of the shot
    .venv/bin/python tools/grade.py SRC --in A --out B --sample DIR             synced before/after video (split + side by side) of A..B
In an edit: "plates": {"grade": "auto", "sharpen": ...}  -> render_edit grades every clip with auto_grade() (per-clip "grade" still wins).

Passes (each measured on 5 frames of the shot after the previous step):
 0 INPUT  HLG / PQ sources (iPhone HDR, Dolby Vision 8.4) -> BT.709 by zscale + mobius tone map at 203-nit reference white.
          (The old plain `format=yuv420p` read HLG/BT.2020 code values as BT.709: flat, desaturated, yellow-biased.)
 1 TECH   white balance + tint from near-neutral pixels (70 % of the measured cast, gains capped +-10 %), levels: grey blacks
          pulled down, dim highlights lifted toward 242 without new clipping.
 2 CONTRAST  filmic S-curve, strength from the shot's measured L* contrast.
 3 SATURATION  vibrance (lifts weak colours, protects saturated ones) iterated toward a colourfulness target; skin chroma capped.
 4 SEPARATION  yellows pulled back (no yellow contamination in neutrals), blues/cyans enriched, reds held.
 5 VERIFY  re-measure: neutral |b*|,|a*| small, no new clipping / crushing, colourfulness up, skin in its natural range.
Graphics are never graded: this runs on the footage plates only; Remotion composites captions/overlays afterwards.
"""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from scopes import metrics  # noqa: E402

VERSION = "g9"   # g9: curves interp=pchip (natural spline overshot/wrapped on steep black points, 2026-11-01)
TONEMAP = ("zscale=tin={tin}:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=mobius:param=0.3:desat=0,zscale=t=bt709,format=gbrp16le")
TARGET = {"neutral_ab": 2.0, "colour_gain": 1.25, "chroma_max": 30.0, "skin_chroma": (14.0, 31.0), "skin_hue": (30.0, 65.0), "p99": 242.0, "black": 7.0}


def probe(src):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,color_transfer,color_primaries,color_space:format=duration", "-of", "json", str(src)],
                                  capture_output=True, text=True, check=True).stdout)
    s = j["streams"][0]
    return s, float(j["format"].get("duration", 0))


def input_chain(src):
    s, _ = probe(src)
    trc = s.get("color_transfer", "")
    if trc == "arib-std-b67":
        return TONEMAP.format(tin="arib-std-b67"), "HLG BT.2020 -> BT.709 (mobius, 203 nit)"
    if trc == "smpte2084":
        return TONEMAP.format(tin="smpte2084"), "PQ BT.2020 -> BT.709 (mobius, 203 nit)"
    mtx = "bt709" if (s.get("color_space") in ("bt709", None, "unknown") and int(s["width"]) >= 1280) or s.get("color_space") == "bt709" else "bt601"
    return f"scale=in_color_matrix={mtx}:in_range=tv,format=gbrp16le", f"SDR ({s.get('color_transfer', 'untagged')}), matrix {mtx}"


def frames(src, chain, times, width=960):
    out = []
    for t in times:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", "-vf",
                              f"{chain},scale={width}:-2:flags=area,format=rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
        h = len(raw) // (width * 3)
        out.append(np.frombuffer(raw, np.uint8).reshape(h, width, 3))
    return out


def agg(ms):
    keys = [k for k in ms[0] if isinstance(ms[0][k], (int, float))]
    r = {k: round(float(np.mean([m[k] for m in ms if m.get(k) is not None])), 2) for k in keys if any(m.get(k) is not None for m in ms)}
    sk = [m for m in ms if "skin_chroma" in m]
    if sk:
        r["skin_hue"] = round(float(np.mean([m["skin_hue"] for m in sk])), 1)
        r["skin_chroma"] = round(float(np.mean([m["skin_chroma"] for m in sk])), 1)
    return r


def neutral_rgb(imgs):
    """mean R, G, B of near-neutral, mid-to-high luminance pixels (the white-balance reference)"""
    acc = []
    for im in imgs:
        f = im.reshape(-1, 3).astype(np.float32)
        mx, mn = f.max(1), f.min(1)
        y = f @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        k = (y > 70) & (y < 235) & ((mx - mn) < 0.12 * mx + 4)
        if k.sum() > 200:
            acc.append(f[k].mean(0))
    return np.mean(acc, 0) if acc else None


def build(tech, curve, vib, sat, skin=(0.0, 0.0), sep=True, blue=0.08, cool=0.0):
    """passes 1-4 as an FFmpeg chain on gbrp16le (display-referred BT.709)"""
    g = tech["gains"]
    c = [f"colorchannelmixer=rr={g[0]:.4f}:gg={g[1]:.4f}:bb={g[2]:.4f}"]
    b, w = tech["black_in"] / 255, min(1.0, tech["white_in"] / 255)
    lo = TARGET["black"] / 255 if b > 0 else 0.0
    hi = 0.955 if w < 0.995 else 1.0          # dim highlights lift to ~242; already-bright whites are left alone (no compression)
    s = curve
    X = lambda f: b + (w - b) * f
    Y = lambda f: lo + (hi - lo) * f
    # levels + filmic S with a highlight shoulder (identity again at 92 %, so the top end keeps its roll-off and detail)
    pts = [(0, 0)] if b > 0 else []
    pts += [(b, lo), (X(0.25), Y(0.25 - s)), (X(0.5), Y(0.5)), (X(0.75), Y(0.75 + s * 0.6)), (X(0.92), Y(0.92)), (w, hi)]
    if w < 0.995:
        pts.append((1, 1))
    c.append("curves=master='" + " ".join(f"{x:.4f}/{y:.4f}" for x, y in pts) + "':interp=pchip")
    if vib > 0:
        c.append(f"vibrance=intensity={vib:.3f}")
    if abs(sat - 1) > 1e-3:                 # global saturation in RGB (eq would drop the chain to 8-bit YUV)
        c.append(f"huesaturation=saturation={sat - 1:.3f}:colors=a:strength=1")
    if sep:
        c += ["huesaturation=saturation=-0.12:colors=y:strength=2", "huesaturation=saturation=-0.03:colors=r:strength=2"]
        if blue > 0:
            c.append(f"huesaturation=saturation={blue:.3f}:colors=b+c:strength=2")
    if cool > 0:                            # richness outside the skin hues (greens, cyans, blues, magentas)
        c.append(f"huesaturation=saturation={cool:.3f}:colors=g+c+b+m:strength=1.5")
    if skin[0] > 0 or skin[1] > 0:          # measured skin protection: reds/oranges nudged toward natural skin hue, trimmed
        c.append(f"huesaturation=hue={skin[0]:.2f}:saturation={-skin[1]:.3f}:colors=r+y:strength=1.5")
    return ",".join(c)


def auto_grade(src, t_in=0.0, t_out=None, cache=None, log=lambda *a: print(*a, file=sys.stderr)):
    """-> {"grade": ffmpeg chain from the source's own pixels to graded BT.709, "report": {...}}"""
    src = Path(src)
    _, dur = probe(src)
    t_out = min(t_out if t_out is not None else dur, dur - 0.05)
    key = hashlib.sha1(f"{VERSION}|{src.resolve()}|{src.stat().st_mtime}|{t_in:.3f}|{t_out:.3f}".encode()).hexdigest()[:16]
    if cache:
        cache = Path(cache); store = json.loads(cache.read_text()) if cache.exists() else {}
        if key in store:
            return store[key]
    times = [t_in + (t_out - t_in) * f for f in (0.1, 0.3, 0.5, 0.7, 0.9)]
    inp, what = input_chain(src)
    old = agg([metrics(f) for f in frames(src, "format=yuv420p", times)])        # the previous studio default, for the report
    base_imgs = frames(src, inp, times)
    base = agg([metrics(f) for f in base_imgs])
    # PASS 1: white balance / tint from neutrals (70 % of the measured cast, 85 % when it is strong; gains capped +-12 %), levels
    n = neutral_rgb(base_imgs)
    gains = [1.0, 1.0, 1.0]
    if n is not None:
        tgt = n.mean()
        strong = abs(base.get("neutral_b") or 0) > 4 or abs(base.get("neutral_a") or 0) > 4
        k = 0.85 if strong else 0.7
        gains = [float(np.clip(1 + k * (tgt / max(v, 1) - 1), 0.88, 1.12)) for v in n]
        gm = float(max(gains)); gains = [g / gm for g in gains]      # no channel pushed up: correction never adds clipping
    black_in = float(min(base["luma_p0_5"], 30.0)) if base["luma_p0_5"] > 10 else max(0.0, base["luma_p0_5"] - 3)
    white_in = float(np.clip(base["luma_p99_5"] + 6, 200, 255)) if base["luma_p99_5"] < 236 else 255.0
    tech = {"gains": gains, "black_in": black_in, "white_in": white_in}
    # PASS 2: contrast from measured L* RMS
    curve = float(np.clip(0.02 + (24 - base["contrast_rms"]) * 0.006, 0.02, 0.07))
    # PASS 3/4: the strongest vibrance (with separation) that stays gamut-safe: no new channel clipping (saturated colours that
    # hit 255 lose texture), chroma under the cap, skin in range. Correctly decoded HDR often needs little or none.
    ref = agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, 0.0, 1.0, sep=False), times)])
    lim_clip = ref["clipped_pct"] + 0.8
    tries, best = [], None
    blue = 0.08
    for vib in (0.0, 0.1, 0.2, 0.3, 0.42):
        res = agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, vib, 1.0, blue=blue), times)])
        if vib == 0.0 and res["clipped_pct"] > lim_clip:      # saturated blues already at the limit: no blue enrichment
            blue = 0.0
            res = agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, vib, 1.0, blue=blue), times)])
        tries.append({"vibrance": vib, "blue": blue, "colourfulness": res["colourfulness"], "chroma": res["chroma_mean"], "clipped": res["clipped_pct"],
                      "skin_hue": res.get("skin_hue"), "skin_chroma": res.get("skin_chroma")})
        sc = res.get("skin_chroma")
        if res["clipped_pct"] > lim_clip or res["chroma_mean"] > TARGET["chroma_max"] or (sc is not None and sc > TARGET["skin_chroma"][1] + 4):
            break
        best = (vib, res)
        if res["colourfulness"] >= old["colourfulness"] * TARGET["colour_gain"] * 1.15 and vib >= 0.1:
            break
    if best is None:
        best = (0.0, agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, 0.0, 1.0, blue=blue), times)]))
    vib, res = best
    sat, skin = 1.0, [0.0, 0.0]
    # WB refinement: re-measure neutrals on the graded frames and correct what is left (up to two iterations)
    for _ in range(2):
        if not (abs(res.get("neutral_b") or 0) > TARGET["neutral_ab"] or abs(res.get("neutral_a") or 0) > TARGET["neutral_ab"]):
            break
        n2 = neutral_rgb(frames(src, inp + "," + build(tech, curve, vib, sat, blue=blue), times))
        if n2 is not None:
            g2 = [float(np.clip(1 + 0.9 * (n2.mean() / max(v, 1) - 1), 0.92, 1.08)) for v in n2]
            g = [a * b for a, b in zip(tech["gains"], g2)]
            tech["gains"] = [float(np.clip(v / max(g), 0.85, 1.0)) for v in g]
            gains = tech["gains"]
            res = agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, vib, sat, blue=blue), times)])
            tries.append({"wb_refine": [round(v, 4) for v in gains], "neutral_a": res.get("neutral_a"), "neutral_b": res.get("neutral_b")})
    # skin protection: measured hue / chroma brought into the natural range (reds/oranges only)
    sh, sc = res.get("skin_hue"), res.get("skin_chroma")
    if sc is not None and (sc > TARGET["skin_chroma"][1] or sh < TARGET["skin_hue"][0] + 5):
        skin = [float(np.clip((TARGET["skin_hue"][0] + 7 - sh) * 0.5, 0, 8)), float(np.clip((sc - TARGET["skin_chroma"][1] + 2) / 40, 0, 0.3))]
        res = agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, vib, sat, tuple(skin), blue=blue), times)])
        if res.get("skin_chroma") and res["skin_chroma"] > TARGET["skin_chroma"][1] + 1:      # one more measured step
            skin[1] = float(np.clip(skin[1] + (res["skin_chroma"] - TARGET["skin_chroma"][1] + 1) / 30, 0, 0.4))
            res = agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, vib, sat, tuple(skin), blue=blue), times)])
        tries.append({"skin_fix": [round(v, 3) for v in skin], "skin_hue": res.get("skin_hue"), "skin_chroma": res.get("skin_chroma")})
    # richness top-up away from skin, when skin protection held the global gain back (measured, clip-safe)
    cool = 0.0
    need = old["colourfulness"] * TARGET["colour_gain"] * 1.03
    if res["colourfulness"] < need:
        for cv in (0.12, 0.24, 0.36):
            r2 = agg([metrics(f) for f in frames(src, inp + "," + build(tech, curve, vib, sat, tuple(skin), blue=blue, cool=cv), times)])
            if r2["clipped_pct"] > lim_clip or r2["chroma_mean"] > TARGET["chroma_max"]:
                break
            cool, res = cv, r2
            tries.append({"cool": cv, "colourfulness": r2["colourfulness"], "clipped": r2["clipped_pct"]})
            if r2["colourfulness"] >= need:
                break
    # PASS 5: verify
    checks = {
        "neutral_cast_ok": res.get("neutral_b") is None or (abs(res["neutral_b"]) <= TARGET["neutral_ab"] + 0.5 and abs(res.get("neutral_a") or 0) <= TARGET["neutral_ab"] + 0.5),
        "no_new_luma_clipping": res["luma_clipped_pct"] <= base["luma_clipped_pct"] + 0.3,
        "colour_channels_not_clipping": res["clipped_pct"] <= lim_clip + 0.3,
        "no_crushed_blacks": res["crushed_pct"] <= max(1.5, base["crushed_pct"] * 1.5 + 0.5),
        # a strong cast inflates colourfulness; removing it legitimately lowers that part, so require less gain there
        "richer_than_old_pipeline": res["colourfulness"] >= old["colourfulness"] * (1.1 if max(abs(old.get("neutral_b") or 0), abs(old.get("neutral_a") or 0)) > 3 else TARGET["colour_gain"]),
        "not_oversaturated": res["chroma_mean"] <= TARGET["chroma_max"] + 2,
        "skin_natural": "skin_chroma" not in res or (TARGET["skin_chroma"][0] - 2 <= res["skin_chroma"] <= TARGET["skin_chroma"][1] + 2
                                                     and TARGET["skin_hue"][0] - 3 <= res["skin_hue"] <= TARGET["skin_hue"][1] + 3),
    }
    out = {"grade": inp + "," + build(tech, curve, vib, sat, skin, blue=blue, cool=cool), "report": {
        "source": str(src), "range": [round(t_in, 3), round(t_out, 3)], "input": what, "old_pipeline": old, "input_converted": base, "graded": res,
        "params": {"gains": [round(g, 4) for g in gains], "black_in": round(black_in, 1), "white_in": round(white_in, 1), "s_curve": round(curve, 3),
                   "vibrance": round(vib, 3), "saturation": round(sat, 3), "skin_fix": [round(v, 3) for v in skin], "blue": blue, "cool": cool}, "iterations": tries, "checks": checks, "pass": all(checks.values())}}
    if cache:
        store[key] = out; cache.parent.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(store, indent=1))
    r = out["report"]
    log(f"grade {src.name} [{t_in:.2f}-{t_out:.2f}] {what}: colourfulness {old['colourfulness']} -> {res['colourfulness']}, "
        f"neutral b* {old.get('neutral_b')} -> {res.get('neutral_b')}, {'PASS' if r['pass'] else 'CHECK ' + str([k for k, v in checks.items() if not v])}")
    return out


def compare(src, t_in, t_out, chain, dst):
    import cv2
    from scopes import scope_sheet
    dst = Path(dst); dst.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, t in enumerate([t_in + (t_out - t_in) * f for f in (0.2, 0.5, 0.8)]):
        a = frames(src, "format=yuv420p", [t], 1080)[0]; b = frames(src, chain, [t], 1080)[0]
        for tag, im in (("before", a), ("after", b)):
            cv2.imwrite(str(dst / f"{i}_{tag}.png"), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
            scope_sheet(dst / f"{i}_{tag}.png", dst / f"{i}_{tag}_scopes.png")
        rows.append((i, t))
    return rows


def sample(src, t_in, t_out, chain, dst):
    """synced before/after: a split-screen (wipe at the centre) and a side-by-side, same frames, no audio change"""
    dst = Path(dst); dst.mkdir(parents=True, exist_ok=True)
    d = t_out - t_in
    common = ["-ss", f"{t_in:.3f}", "-t", f"{d:.3f}", "-i", str(src)]
    g = (f"[0:v]split=2[a][b];[a]format=yuv420p,format=rgb24,scale=1080:-2:flags=lanczos[A];[b]{chain},scale=1080:-2:flags=lanczos,format=rgb24[B];"
         "[A]split=2[A1][A2];[B]split=2[B1][B2];[A1][B1]hstack[sbs];"
         "[A2]crop=iw/2:ih:0:0[L];[B2]crop=iw/2:ih:iw/2:0[R];[L][R]hstack,drawbox=x=iw/2-2:y=0:w=4:h=ih:color=white@1:t=fill[split]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *common, "-filter_complex", g, "-map", "[sbs]", "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-an", str(dst / "before_after_side_by_side.mp4"),
                    "-map", "[split]", "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-an", str(dst / "before_after_split.mp4")], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src"); ap.add_argument("--in", dest="t_in", type=float, default=0.0); ap.add_argument("--out", dest="t_out", type=float)
    ap.add_argument("--compare"); ap.add_argument("--sample"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    g = auto_grade(a.src, a.t_in, a.t_out)
    print(json.dumps(g, indent=1) if a.json else g["grade"])
    t_out = g["report"]["range"][1]
    if a.compare:
        compare(a.src, a.t_in, t_out, g["grade"], a.compare)
        (Path(a.compare) / "report.json").write_text(json.dumps(g, indent=1))
    if a.sample:
        sample(a.src, a.t_in, t_out, g["grade"], a.sample)
        (Path(a.sample) / "report.json").write_text(json.dumps(g, indent=1))


if __name__ == "__main__":
    main()
