""""Client is 10 minutes late..." trend (Coach Osama 2026-11-19): his two clips recut to the reference (ref/Trend.mp4, a screen
recording; reference only, never in the output).

Reference, measured: the Reel runs 0.283-15.535 s of the recording (15.252 s, then it loops). ONE clip (trainer tosses a towel and
walks up to the lens) repeated 7 times; hard cuts at 2.200, 4.367, 6.534, 8.684, 10.852, 13.019 s (Reel time); each repeat starts
from the same source frame; one caption per repeat, changing exactly on the cut. The sound repeats every 2.167 s in step with the
cuts (a strong hit ~1.05 s into every repeat), so the segment lengths are kept to the frame: 66, 65, 65, 65, 65, 65, 67 frames at 30.
Caption: Instagram classic text look = bold white sans, black outline, one line, same size for all 7 (the reference's longest line
runs past both edges: here a line only shrinks if it would not fit), ascender top at 247 px / baseline 322 px of 1920 (measured on
the recording: Reel fitted to the 1320 px screen width, top at y 227).
V1 = IMG_8401 (from 0.2 s; his head sits mid-frame, the caption keeps the reference's top position).
V2 = IMG_9205 (1.73 s: slowed to fit 2.233 s with motion interpolation; his face fills the frame down to 77 % of the height, so the
caption sits under his chin at 0.79 instead of across his face).
Sound: the trend's own sound from the recording (0.283-15.535 s, his request: use the original audio); a silent copy of each version
is also written for adding the sound in Instagram ("Use audio").

    .venv/bin/python projects/2026-11-19_trend_two/build.py
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
FPS = 30
SEG = [66, 65, 65, 65, 65, 65, 67]                       # 458 frames = 15.267 s (reference 15.252 s)
LINES = ["Client is 10 minutes late", "Client is 10 minutes early", "Client is on time", "Client cancels", "Client shows up",
         "Zero clients", "Fully booked"]
REF_IN, REF_OUT = 0.283, 15.535
HLG = "zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709,format=gbrp16le"
SAT = "huesaturation=saturation=-0.12:colors=y:strength=2,huesaturation=saturation=-0.03:colors=r:strength=2"
VERSIONS = {
    # tools/grade.py's measured chain (PASS) for V1
    "v1": dict(src="IMG_8401.MOV", start=0.2, speed=1.0, cap_top=None,
               grade=f"{HLG},colorchannelmixer=rr=0.9421:gg=0.9693:bb=1.0000,curves=master='0/0 0.0017/0.0275 0.2513/0.2511 0.5009/0.5137 0.7504/0.7685 0.9201/0.9222 1/1':interp=pchip,{SAT}"),
    # V2: grade.py's curve, but its white-balance pull (red x0.85) turned his skin red -> left out, his camera's own balance kept
    "v2": dict(src="IMG_9205.mov", start=0.0, speed=1.727 / (67 / FPS), cap_top=0.79,
               grade=f"{HLG},curves=master='0/0 0.0814/0.0275 0.3111/0.2511 0.5407/0.5137 0.7704/0.7685 0.9265/0.9222 1/1':interp=pchip,{SAT}"),
}


def ff(a):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *a], check=True)


def clip(name, v, W):
    """The repeated clip, graded, 1080x1920, 67 frames (the longest segment); segments use its first N frames."""
    out = W / f"{name}_clip.mkv"
    sp = v["speed"]
    chain = f"trim=start={v['start']},setpts=PTS-STARTPTS"
    if sp < 1:   # real motion-interpolated frames, not duplicates
        chain += f",setpts=PTS/{sp:.5f},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    chain += f",fps={FPS},{v['grade']},scale=1080:1920:flags=lanczos,format=yuv420p"
    ff(["-i", str(P / "source" / v["src"]), "-vf", chain, "-frames:v", "67", "-an", "-c:v", "libx264", "-crf", "10", "-preset", "medium", str(out)])
    return out


FONT = str(P.parents[1] / "brand/fonts/Inter[opsz,wght].ttf")
ASC_TOP, BASE = 247, 322               # reference: ascender top / baseline (px of 1920)
REF_W = 1031                           # reference: "Client is 10 minutes late" incl. outline, px of 1080
STROKE = 4


def font(size):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([32, 700])            # opsz, wght: bold
    except Exception:
        f.set_variation_by_name("Bold")
    return f


def text_pngs(out, cap_top):
    """One transparent 1080x1920 PNG per line: bold white, black outline, centred; the size is fitted ONCE on the reference line."""
    from PIL import Image, ImageDraw
    out.mkdir(parents=True, exist_ok=True)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    size = 40
    while d0.textbbox((0, 0), LINES[0], font=font(size + 1), stroke_width=STROKE)[2] <= REF_W:
        size += 1
    for i, line in enumerate(LINES):
        s = size
        while d0.textbbox((0, 0), line, font=font(s), stroke_width=STROKE)[2] > 1040:   # only a line that would be cut off shrinks
            s -= 1
        f = font(s)
        im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        asc = f.getmetrics()[0]
        base = BASE if cap_top is None else round(cap_top * 1920) + (BASE - ASC_TOP)
        x0, y0, x1, y1 = d.textbbox((0, 0), line, font=f, stroke_width=STROKE)
        d.text(((1080 - (x1 - x0)) / 2 - x0, base - asc), line, font=f, fill=(255, 255, 255, 255), stroke_width=STROKE,
               stroke_fill=(0, 0, 0, 255))
        im.save(out / f"line_{i}.png")
    return size


def main():
    W = P / "work"; W.mkdir(exist_ok=True); (P / "renders").mkdir(exist_ok=True)
    audio = W / "trend_audio.wav"          # the recording's sound peaks above 0 dBFS: mastered like every Reel (-14 LUFS, -1 dBTP)
    ff(["-ss", str(REF_IN), "-to", str(REF_OUT), "-i", str(P / "ref/Trend.mp4"), "-vn", "-ar", "48000", "-c:a", "pcm_s24le", str(audio)])
    sys.path.insert(0, str(P.parents[1] / "tools"))
    import render_edit as R
    for name, v in VERSIONS.items():
        c = clip(name, v, W)
        spec = {"lines": LINES, "seg": SEG, "fps": FPS, "capTop": v["cap_top"]}
        (W / f"{name}_spec.json").write_text(json.dumps(spec))
        text_pngs(W / f"{name}_text", v["cap_top"])
        # 7 repeats of the clip, each cut to its segment length, one caption PNG per repeat
        ins, g, labs = ["-i", str(c)], [f"[0:v]split={len(SEG)}" + "".join(f"[r{i}]" for i in range(len(SEG)))], []
        for i, n in enumerate(SEG):
            ins += ["-i", str(W / f"{name}_text" / f"line_{i}.png")]
            g.append(f"[r{i}]trim=end_frame={n},setpts=PTS-STARTPTS[c{i}];[c{i}][{i + 1}:v]overlay=0:0[s{i}]")
            labs.append(f"[s{i}]")
        g.append("".join(labs) + f"concat=n={len(SEG)}:v=1:a=0,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]")
        silent = P / "renders" / f"trend_{name}_silent.mp4"
        ff([*ins, "-filter_complex", ";".join(g), "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-crf", "14", "-preset", "slow",
            "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-movflags", "+faststart", str(silent)])
        R.master_audio(audio, P / "renders" / f"trend_{name}.mp4", -14.0, -1.0, video=silent)
        print("output", name)


if __name__ == "__main__":
    main()
