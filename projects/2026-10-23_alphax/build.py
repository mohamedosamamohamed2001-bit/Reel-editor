"""AlphaX edits for Coach Osama (2026-10-23): 3 teasers + 1 full race video from his 17 race clips.
Cuts sit on a beat grid at the tempo of the song chosen for each video (the song itself is added in Instagram/TikTok:
commercial tracks can't be embedded here). Original camera audio is removed; the sound is the in-house SFX kit only.
120 fps clips give true slow motion. OSM: #56A0FB bars with white Inter Black Italic caps, OSM chip, OSM end card.

    .venv/bin/python -I build.py t1|t2|t3|full
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = ROOT / "brand" / "fonts"
W, H, FPS = 1080, 1920, 30
BAR, NIGHT, WHITE = "#56A0FB", "#0A0F16", "#FFFFFF"
LOOK = "eq=contrast=1.06:saturation=1.05"  # light, neutral: natural skin, no colour cast
SFX = {"air": .252, "whoosh_in": .527, "whoosh_out": .09, "swell": .55, "thump": 0, "impact": 0, "click": 0, "boom": 0,
       "whip": .165, "riser": 1.0, "slam": 0, "bass_drop": 0, "reverse_hit": .7}


def run(c):
    subprocess.run(c, check=True)


def card_html(text, y, size):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: InterI; src: url('file://{F}/Inter-Italic[opsz,wght].ttf'); font-weight: 100 900; font-style: italic; }}
html,body {{ margin:0; width:{W}px; height:{H}px; background:transparent; overflow:hidden; }}
.t {{ position:absolute; left:0; width:{W}px; top:{int(y * H)}px; transform:translateY(-50%); text-align:center;
      font-family:InterI; font-style:italic; font-weight:900; font-size:{size}px; letter-spacing:-0.02em; line-height:1.5; }}
.t span {{ background:{BAR}; color:{WHITE}; padding:6px 30px 10px; border-radius:18px; white-space:nowrap;
          -webkit-box-decoration-break:clone; box-decoration-break:clone; }}
</style></head><body><div class="t">{'<br>'.join(f'<span>{l}</span>' for l in text)}</div>
<script>document.fonts.ready.then(()=>document.body.dataset.ready=1)</script></body></html>"""


def chip_html():
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;width:{W}px;height:{H}px;background:transparent}}
.c{{position:absolute;top:120px;left:54px;height:64px;padding:0 18px;background:{NIGHT};border-radius:16px;display:flex;align-items:center}}
.c img{{height:42px;mix-blend-mode:lighten}}</style></head><body><div class="c"><img src="file://{ROOT}/brand/logo/osm-wordmark-780x264.jpg"></div>
<script>document.body.dataset.ready=1</script></body></html>"""


RENDER_JS = """const { chromium } = require(process.env.PW); const fs = require('fs'); const path = require('path');
(async () => { const dir = process.argv[2]; const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html'))) { await p.goto('file://' + path.join(dir, f));
    await p.waitForFunction(() => document.body.dataset.ready == 1);
    await p.screenshot({ path: path.join(dir, f.replace('.html', '.png')), omitBackground: true }); } await b.close(); })();"""


def build(key):
    c = json.loads((P / "edits.json").read_text())[key]
    beat = 60.0 / c["bpm"]
    out = P / "work" / key; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"):
        f.unlink()
    # ---- picture
    ins, fl, t, cuts = [], [], 0.0, []
    for i, s in enumerate(c["shots"]):
        d = round(round(s["beats"] * beat * FPS) / FPS, 4)
        sp = s.get("speed", 1.0)
        z, fx, fy = s.get("zoom", 1.0), s.get("fx", 0.5), s.get("fy", 0.5)
        ins += ["-i", str(P / "source" / f"IMG_{s['clip']}.MOV")]
        f = (f"[{i}:v]trim=start={s['in']}:duration={d * sp + 0.05},setpts=(PTS-STARTPTS)/{sp},fps={FPS},trim=duration={d},"
             f"setpts=PTS-STARTPTS,format=yuv420p,{LOOK},scale={W}*{z}:{H}*{z}:force_original_aspect_ratio=increase:flags=lanczos,"
             f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy},setsar=1")
        if s.get("flash"):  # white flash on the cut (a hit), 3 frames
            f += f",fade=t=in:st=0:d=0.1:color=white"
        fl.append(f + f"[v{i}]")
        cuts.append((round(t, 4), s))
        t += d
    T_main = t
    n = len(c["shots"])
    # end card: OSM end artwork (1080 wide, centred on Night), 1.6 s
    endd = 1.6
    ins += ["-loop", "1", "-t", str(endd), "-i", str(ROOT / "brand/end/osm-end-photo.jpg")]
    fl.append(f"[{n}:v]scale={W}:-2,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0A0F16,format=yuv420p,setsar=1,fps={FPS},"
              f"fade=t=in:st=0:d=0.25[v{n}]")
    fl.append("".join(f"[v{i}]" for i in range(n + 1)) + f"concat=n={n + 1}:v=1:a=0[cat]")
    T = T_main + endd
    # ---- text cards + OSM chip
    k0 = n + 1
    for j, tx in enumerate(c.get("texts", [])):
        (out / f"t{j:02d}.html").write_text(card_html(tx["text"], tx.get("y", 0.72), tx.get("size", 76)), encoding="utf-8")
    (out / "chip.html").write_text(chip_html())
    (out / "render.js").write_text(RENDER_JS)
    run(["node", str(out / "render.js"), str(out)])
    base = "cat"
    for j, tx in enumerate(c.get("texts", [])):
        t0 = cuts[tx["shot"]][0] if "shot" in tx else tx["t0"]
        t1 = t0 + tx["beats"] * beat
        ins += ["-loop", "1", "-t", f"{T}", "-i", str(out / f"t{j:02d}.png")]
        fl.append(f"[{k0 + j}:v]format=rgba,fade=t=in:st={t0}:d=0.12:alpha=1,fade=t=out:st={t1 - 0.12}:d=0.12:alpha=1[o{j}]")
        fl.append(f"[{base}][o{j}]overlay=0:0:enable='between(t,{t0},{t1})'[b{j}]")
        base = f"b{j}"
    kc = k0 + len(c.get("texts", []))
    ins += ["-loop", "1", "-t", f"{T}", "-i", str(out / "chip.png")]
    fl.append(f"[{base}][{kc}:v]overlay=0:0:enable='lt(t,{T_main})',format=yuv420p[vout]")
    # ---- SFX only (cues by hit time)
    cues = []
    for tc, s in cuts:
        for snd in s.get("sfx", []):
            name, gain = (snd, -10) if isinstance(snd, str) else snd
            cues.append((tc, name, gain))
    cues.append((T_main, "boom", -8))
    for extra in c.get("sfx", []):
        cues.append(tuple(extra))
    ai = kc + 1
    parts = []
    for q, (tc, name, gain) in enumerate(cues):
        ins += ["-i", str(P / "work/sfx" / f"{name}.wav")]
        start = max(0.0, tc - SFX[name])
        parts.append(f"[{ai + q}:a]volume={gain}dB,adelay={int(start * 1000)}|{int(start * 1000)}[s{q}]")
    fl += parts
    fl.append("".join(f"[s{q}]" for q in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad,atrim=duration={T}[aout]")
    raw = P / "work" / f"{key}_raw.mov"
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-r", str(FPS), "-c:a", "pcm_f32le", "-t", f"{T}", str(raw)])
    # SFX bus level: peaks to -3 dBFS (the song is added on top in the app)
    dst = P / "renders" / f"{c['name']}.mp4"; dst.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af",
         "volume=-6dB,aresample=192000,alimiter=limit=0.7:attack=1:release=60:level=false,aresample=48000",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(dst)])
    raw.unlink()
    print(f"{c['name']}: {T:.2f}s ({T_main:.2f}s + end card), {n} shots, beat {beat:.3f}s")


if __name__ == "__main__":
    build(sys.argv[1])
