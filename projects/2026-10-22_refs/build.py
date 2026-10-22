"""OSM recreations of 3 Instagram reference Reels (Coach Osama 2026-10-22).
The references' on-screen text, order and timing are kept (read frame by frame from the screen recordings); the pictures
are his own: video 1 = his training clips (one clip per reference shot), video 2 = Photo 2, video 3 = Photo 3.
No Instagram UI, no third-party footage or audio: an original OSM music bed (tools/music.py) replaces the source sound.
OSM look: IBM Plex Sans Arabic Bold / Inter, white text on the locked #56A0FB bars, OSM wordmark chip, natural colours.

    .venv/bin/python -I build.py 1|2|3 [--preview]
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = ROOT / "brand" / "fonts"
BAR, NIGHT, WHITE = "#56A0FB", "#0A0F16", "#FFFFFF"
FPS, W, H = 30, 1080, 1920
CFG = json.loads((P / "videos.json").read_text())


def run(cmd):
    subprocess.run(cmd, check=True)


def css():
    return f"""
@font-face {{ font-family: Plex; src: url('file://{F}/IBMPlexSansArabic-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: Inter; src: url('file://{F}/Inter[opsz,wght].ttf'); font-weight: 100 900; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; background: transparent; overflow: hidden; }}
.t {{ position: absolute; left: 0; width: {W}px; }}
.ar {{ font-family: Plex; font-weight: 700; direction: rtl; line-height: 1.68; }}
.en {{ font-family: Inter; font-weight: 700; direction: ltr; line-height: 1.5; }}
.t span {{ background: {BAR}; color: {WHITE}; padding: 3px 26px 9px; border-radius: 20px; white-space: nowrap;
          -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
.en span {{ padding: 6px 24px 8px; }}
.chip {{ position: absolute; top: 120px; left: 54px; height: 64px; padding: 0 18px; background: {NIGHT}; border-radius: 16px;
        display: flex; align-items: center; }}
.chip img {{ height: 42px; mix-blend-mode: lighten; }}
"""


def text_html(ev):
    """One text event: Arabic lines (stacked bars) and/or an English line, block centred on (x, y) fractions."""
    al = ev.get("align", "center")
    out = ""
    if ev.get("ar"):
        out += f'<div class="ar" style="font-size:{ev.get("size", 70)}px; text-align:{al}">' + "<br>".join(
            f"<span>{l}</span>" for l in ev["ar"]) + "</div>"
    if ev.get("en"):
        out += f'<div class="en" style="font-size:{ev.get("en_size", 40)}px; text-align:{al}; margin-top:12px">' + "<br>".join(
            f"<span>{l}</span>" for l in ev["en"]) + "</div>"
    x = ev.get("x", 0.5)
    pad = 60
    if al == "center":
        bw = ev.get("bw", 1000); box = f"left:{int(x * W - bw / 2)}px; width:{bw}px;"
    elif al == "right":
        box = f"right:{int(W - x * W)}px; width:{int(x * W - pad)}px;"
    else:
        box = f"left:{int(x * W)}px; width:{int(W - x * W - pad)}px;"
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body>'
            f'<div class="t" id="b" style="{box}">{out}</div><script>document.fonts.ready.then(() => {{'
            f'const b = document.getElementById("b"); b.style.top = ({ev.get("y", 0.5)} * {H} - b.offsetHeight / 2) + "px";'
            f'document.body.dataset.ready = 1; }})</script></body></html>')


def logo_html():
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body>'
            f'<div class="chip"><img src="file://{ROOT}/brand/logo/osm-wordmark-780x264.jpg"></div>'
            f'<script>document.fonts.ready.then(() => document.body.dataset.ready = 1)</script></body></html>')


RENDER_JS = """
const { chromium } = require(process.env.PW); const fs = require('fs'); const path = require('path');
(async () => { const [dir] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html'))) {
    await p.goto('file://' + path.join(dir, f)); await p.waitForFunction(() => document.body.dataset.ready == 1);
    await p.screenshot({ path: path.join(dir, f.replace('.html', '.png')), omitBackground: true }); }
  await b.close(); })();
"""


def shot_filter(s, i):
    """One shot -> [v{i}] 1080x1920 @30: his own footage / photo, natural colours (plain decode), no stretch."""
    zoom = s.get("zoom", 1.0)
    fx, fy = s.get("fx", 0.5), s.get("fy", 0.5)
    d = s["dur"]
    if s.get("photo"):
        z0, z1 = s.get("push", [1.0, 1.06])
        n = int(round(d * FPS))
        # Ken Burns on a 2x canvas (no jitter): zoom z0->z1 around the focus point
        return (f"[{i}:v]scale={2 * W}:{2 * H}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={2 * W}:{2 * H}:(iw-{2 * W})*{fx}:(ih-{2 * H})*{fy},"
                f"zoompan=z='{z0}+({z1}-{z0})*on/{max(1, n - 1)}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d={n}:s={W}x{H}:fps={FPS},"
                f"setsar=1,format=yuv420p[v{i}]")
    cw, ch = f"{W}*{zoom}", f"{H}*{zoom}"
    f = (f"[{i}:v]trim=start={s['in']}:duration={d},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p,"
         f"scale={cw}:{ch}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy},setsar=1")
    if s.get("fade_in"):
        f += f",fade=t=in:st=0:d={s['fade_in']}"
    if s.get("fade_out"):
        f += f",fade=t=out:st={d - s['fade_out']}:d={s['fade_out']}"
    return f + f"[v{i}]"


def build(key, preview=False):
    c = CFG[key]
    out = P / "work" / f"v{key}"; out.mkdir(parents=True, exist_ok=True)
    T = c["duration"]
    # 1) text + logo PNGs
    for f in out.glob("t_*"):
        f.unlink()
    for k, ev in enumerate(c["texts"]):
        (out / f"t_{k:02d}.html").write_text(text_html(ev), encoding="utf-8")
    (out / "t_logo.html").write_text(logo_html(), encoding="utf-8")
    (out / "render.js").write_text(RENDER_JS)
    run(["node", str(out / "render.js"), str(out)])
    # 2) music bed (original, tools/music.py)
    spec = dict(c["music"], duration=T)
    (out / "music.json").write_text(json.dumps(spec))
    run([str(ROOT / ".venv/bin/python"), str(ROOT / "tools/music.py"), str(out / "music.json"), str(out / "music.wav")])
    # 3) picture: shots (+ dissolves) -> text overlays with short fades -> logo
    inputs, fl = [], []
    for i, s in enumerate(c["shots"]):
        src = str(P / s["src"])
        inputs += (["-loop", "1", "-t", str(s["dur"] + 1), "-i", src] if s.get("photo") else ["-i", src])
        fl.append(shot_filter(s, i))
    n = len(c["shots"])
    if c.get("dissolve"):  # photo videos: crossfade between shots
        acc, t_acc = "v0", c["shots"][0]["dur"]
        for i in range(1, n):
            d = c["dissolve"]
            fl.append(f"[{acc}][v{i}]xfade=transition=fade:duration={d}:offset={t_acc - d}[x{i}]")
            acc, t_acc = f"x{i}", t_acc + c["shots"][i]["dur"] - d
        base = acc
    else:
        fl.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cat]")
        base = "cat"
    k0 = n
    for k, ev in enumerate(c["texts"]):
        inputs += ["-loop", "1", "-t", f"{T}", "-i", str(out / f"t_{k:02d}.png")]
        fi = ev.get("fade", 0.12)
        dur = ev["t1"] - ev["t0"]
        fl.append(f"[{k0 + k}:v]format=rgba,fade=t=in:st={ev['t0']}:d={fi}:alpha=1,"
                  f"fade=t=out:st={ev['t1'] - fi}:d={fi}:alpha=1[o{k}]")
        nxt = f"b{k}"
        fl.append(f"[{base}][o{k}]overlay=0:0:enable='between(t,{ev['t0']},{ev['t1']})'[{nxt}]")
        base = nxt
    inputs += ["-loop", "1", "-t", f"{T}", "-i", str(out / "t_logo.png")]
    fl.append(f"[{base}][{k0 + len(c['texts'])}:v]overlay=0:0,trim=duration={T},format=yuv420p[vout]")
    inputs += ["-i", str(out / "music.wav")]
    ai = k0 + len(c["texts"]) + 1
    fl.append(f"[{ai}:a]atrim=duration={T},afade=t=out:st={T - 0.8}:d=0.8,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    name = c["name"] + ("_preview" if preview else "")
    dst = P / "renders" / f"{name}.mp4"; dst.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fl), "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "veryfast" if preview else "slow", "-crf", "26" if preview else "16",
         "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", f"{T}", str(dst)])
    print("wrote", dst)


if __name__ == "__main__":
    build(sys.argv[1], preview="--preview" in sys.argv)
