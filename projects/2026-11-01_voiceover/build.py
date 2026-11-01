"""Creatine & hair loss: his voice-over (main.mov audio, untouched) as the spine; the static image is gone.
Visuals: real stock footage (Coverr, non-AI, non-premium, manifest in source/stock), OSM science/research motion scenes
(motion/pieces/creatine_science, facts from PubMed-verified papers), and his own clips/photo only where they add value.
Output time = voice-over time. Captions = his words (large-v3, cross-checked with medium; corrections listed in WORD_FIX).

    .venv/bin/python projects/2026-11-01_voiceover/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-01_voiceover
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(P.parents[0] / "_c5"))
sys.path.insert(0, str(P.parents[0] / "_n6"))
from common import END_DUR, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402
from common2 import END_IMAGE  # noqa: E402

VO_DUR = 53.8
GFX = "format=yuv420p"            # motion graphics are SDR brand pixels: never graded

# spoken words, corrected spelling of clear mishearings (both models agree on the sound): large-v3 start time -> text
WORD_FIX = {0.00: "الكرياتين", 4.18: "لاعب", 4.52: "رجبي", 7.02: "هرمون", 9.14: "لاعيبة", 9.48: "الرجبي", 10.74: "كرياتين",
            17.38: "اتعملت", 18.32: "دراسة", 21.94: "كرياتين", 25.58: "ولقوا", 29.50: "الكرياتين", 30.80: "مش", 30.84: "سحر",
            32.64: "شغل", 35.34: "والعضل", 41.06: "كرياتين", 42.50: "إنك", 44.00: "وزنك", 50.12: "الكرياتين", 51.96: "الكلى"}
UNSURE = {25.58: "ولقوا (heard 'ولو'/'ولوه')", 32.64: "شغل (heard 'شغلة')", 44.00: "وزنك (heard 'وزدك')"}

# timeline: (start, end, media key, source in, kwargs). Output time = VO time; the clips tile 0 -> VO_DUR exactly.
SHOTS = [
    (0.00, 1.26, "s_comb", 2.2, dict(zoom=[1.12, 1.22], focusX=0.5, focusY=0.42)),
    (1.26, 4.90, "m_rugby", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (4.90, 8.44, "m_study2009", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (8.44, 13.98, "m_dht", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "left"})),
    (13.98, 15.06, "s_insta", 6.0, dict(zoom=[1.0, 1.08], focusX=0.42, tin={"type": "whip", "dir": "right"})),
    (15.06, 16.16, "s_type", 2.0, dict(zoom=[1.0, 1.08], focusX=0.55, tin={"type": "zoom"})),
    (16.16, 20.74, "m_rct2025", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (20.74, 22.82, "o_2253", 16.4, dict(zoom=[1.0, 1.06], focusY=0.6, tin={"type": "whip", "dir": "left"})),
    (22.82, 24.10, "s_calendar", 1.5, dict(zoom=[1.0, 1.06], focusX=0.4, grade="format=yuv420p", tin={"type": "zoom"})),
    (24.10, 27.38, "m_hair", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (27.38, 30.02, "s_vitamins", 3.5, dict(zoom=[1.02, 1.1], focusX=0.5, tin={"type": "whip", "dir": "right"})),
    (30.02, 31.28, "s_science", 4.0, dict(zoom=[1.1, 1.2], focusX=0.42, tin={"type": "zoom"})),
    (31.28, 33.86, "o_2253", 11.0, dict(zoom=[1.0, 1.06], focusY=0.55, tin={"type": "whip", "dir": "left"})),
    (33.86, 36.30, "m_atp", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (36.30, 37.70, "s_equip", 2.0, dict(zoom=[1.0, 1.08], focusX=0.5, tin={"type": "whip", "dir": "right"})),
    (37.70, 39.62, "o_2258", 1.2, dict(zoom=[1.0, 1.05], focusY=0.45, speed=0.5, tin={"type": "zoom"})),
    (39.62, 43.30, "m_dose", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),
    (43.30, 45.54, "s_scale", 2.0, dict(zoom=[1.05, 1.12], focusX=0.5, tin={"type": "whip", "dir": "left"})),
    (45.54, 46.14, "s_water", 4.0, dict(zoom=[1.1, 1.18], focusX=0.5, tin={"type": "zoom"})),
    (46.14, 48.22, "m_water", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (48.22, 49.86, "o_photo", 0.0, dict(zoom=[1.0, 1.07], focusY=0.36, tin={"type": "whip", "dir": "right"})),
    (49.86, 50.72, "s_fist", 3.5, dict(zoom=[1.05, 1.12], focusX=0.45, tin={"type": "whip", "dir": "left"})),
    (50.72, VO_DUR, "s_gloves", 2.0, dict(zoom=[1.0, 1.06], focusX=0.4, tin={"type": "zoom"})),
]
MEDIA = {
    "s_comb": "source/stock/coverr-combing-a-man-s-hair-2623.mp4", "s_insta": "source/stock/coverr-man-scrolling-through-his-instagram-feed-4477.mp4",
    "s_type": "source/stock/coverr-man-types-on-iphone-15.mp4",
    "s_calendar": "source/stock/coverr-july-calendar-5192.mp4", "s_vitamins": "source/stock/coverr-taking-vitamins-230.mp4",
    "s_science": "source/stock/coverr-science-experiment-6978.mp4", "s_equip": "source/stock/coverr-sports-equipment-in-a-gym-7635.mp4",
    "s_scale": "source/stock/coverr-pouring-flour-on-the-scales-2968.mp4", "s_water": "source/stock/coverr-pouring-water-into-a-glass-749.mp4",
    "s_fist": "source/stock/coverr-friends-giving-each-other-a-fist-bump-5866.mp4", "s_gloves": "source/stock/coverr-putting-medical-gloves-on-5311.mp4",
    "o_2253": "source/IMG_2253.mov", "o_2258": "source/IMG_2258.MOV", "o_photo": "work/photo_3324.mp4",
    **{f"m_{n}": f"work/motion/{n}.mp4" for n in ("rugby", "study2009", "dht", "rct2025", "hair", "atp", "dose", "water")},
}


def photo_clip():
    """IMG_3324.HEIC -> sRGB PNG (pillow-heif, P3 -> sRGB via its ICC) -> 3 s still clip (no other change)."""
    out = P / "work" / "photo_3324.mp4"
    if out.exists():
        return
    import io
    from PIL import Image, ImageCms, ImageOps
    import pillow_heif
    pillow_heif.register_heif_opener()
    im = ImageOps.exif_transpose(Image.open(P / "source" / "IMG_3324.HEIC"))
    icc = im.info.get("icc_profile")
    im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), ImageCms.createProfile("sRGB"), outputMode="RGB") if icc else im.convert("RGB")
    png = P / "work" / "photo_3324.png"
    im.save(png)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-t", "3", "-i", str(png), "-vf",
                    "scale=1440:-2:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "12", "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709", str(out)], check=True)


def words():
    d = json.loads((P / "work/tx/main.words.json").read_text())
    out = []
    for s in d["segments"]:
        for w in s["words"]:
            k = round(w["start"], 2)
            t = WORD_FIX.get(k, w["w"].strip())
            out.append({"w": t, "start": w["start"], "end": w["end"]})
    return out


def main():
    photo_clip()
    vo = P / "work" / "vo.wav"     # his voice-over, sample-exact, untouched (only resampled for the mixer)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / "source/main.mov"), "-map", "0:a:0", "-ar", "48000", "-ac", "2",
                    "-t", f"{VO_DUR + END_DUR:.3f}", "-af", f"apad=whole_dur={VO_DUR + END_DUR:.3f}", "-c:a", "pcm_s24le", str(vo)], check=True)
    clips = []
    for a, b, key, sin, kw in SHOTS:
        sp = kw.get("speed", 1)
        c = {"src": key, "in": round(sin, 4), "out": round(sin + (b - a) * sp, 4)}
        c.update(kw)
        clips.append(c)
    T = SHOTS[-1][1]
    ov = [
        {"type": "kineticTitle", "at": 0.05, "dur": 1.2, "lines": [{"text": "CREATINE", "size": 118}, {"text": "= HAIR LOSS?", "accent": True, "size": 92}],
         "top": 0.12, "motion": "smooth", "depth": True},
        {"type": "lowerLabel", "at": 21.45, "dur": 1.32, "title": "5 جرام كرياتين يوميًا", "eyebrow": "THE DOSE", "top": 0.16, "plate": True},
        {"type": "lowerLabel", "at": 23.2, "dur": 0.88, "title": "لمدة 12 أسبوع", "eyebrow": "DURATION", "top": 0.16, "plate": True},
        {"type": "kineticTitle", "at": 30.6, "dur": 0.68, "lines": [{"text": "NOT MAGIC", "size": 120}], "top": 0.14, "motion": "smooth", "depth": True},
        {"type": "kineticTitle", "at": 36.35, "dur": 1.3, "lines": [{"text": "NO TRAINING", "size": 104}, {"text": "= NO RESULTS", "accent": True, "size": 92}],
         "top": 0.14, "motion": "smooth", "depth": True},
        {"type": "lowerLabel", "at": 43.45, "dur": 2.55, "title": "ميّه، مش دهون", "eyebrow": "WATER WEIGHT", "top": 0.16, "plate": True},
        {"type": "lowerLabel", "at": 50.85, "dur": 2.9, "title": "مشكلة في الكلى؟ اسأل دكتورك", "eyebrow": "SAFETY FIRST", "top": 0.16, "plate": True},
    ]
    endc = dict(end_card(T), image=END_IMAGE, sub="Sources: van der Merwe 2009 · Lak et al. 2025 · ISSN 2017")
    ov.append(endc)
    cues = [cue(0.0, "impact", -9), cue(0.02, "boom", -12), cue(0.05, "whoosh_in", -18)]
    for a, b, key, sin, kw in SHOTS[1:]:
        t = kw.get("tin", {}).get("type")
        cues.append(cue(a, "whip" if t == "whip" else "whoosh_in", -15 if t == "whip" else -16))
    # science / data beats (graphics land on these)
    cues += [cue(1.26 + 0.55 + i * 0.07 * 4, "blip", -24) for i in range(5)]                      # rugby players pop in
    cues += [cue(4.90 + 1.1, "swell", -20)]                                                        # DHT molecule draws
    cues += [cue(8.44 + 0.2 + i * 0.55, "thump", -15) for i in range(3)]                           # DHT bars
    cues += [cue(8.44 + 3.85 + i * 0.28, "click", -16) for i in range(2)] + [cue(8.44 + 4.41, "impact", -11)]   # checklist, hair ✗
    cues += [cue(16.16 + 3.0, "impact", -12), cue(21.45, "accent", -16), cue(23.2, "accent", -16)]  # 45 / 5 g / 12 weeks
    cues += [cue(24.10 + 1.48, "whoosh_in", -16), cue(24.10 + 2.3, "impact", -10)]                 # NO DIFFERENCE
    cues += [cue(30.6, "boom", -12)]                                                              # NOT MAGIC
    cues += [cue(33.86 + 0.05 + i * 0.4, "blip", -22) for i in range(5)]                           # ATP chain
    cues += [cue(36.35, "impact", -12), cue(39.62, "boom", -12)]
    cues += [cue(39.62 + 2.5 + i * 0.12, "click", -22) for i in range(7)]                          # 7 days ✓
    cues += [cue(43.45, "accent", -17), cue(46.14 + 0.3, "swell", -20), cue(48.22, "chime", -18), cue(50.85, "accent", -17)]
    cues += end_card_sfx(T)
    wf = P / "work" / "vo.words.json"
    ws = words()
    wf.write_text(json.dumps({"segments": [{"words": ws}]}, ensure_ascii=False))
    mus = make_music(P, {"bpm": 120, "key": "E", "mode": "minor", "style": "trap", "seed": 11, "duration": round(T + END_DUR, 3),
                         "sections": [{"type": "intro", "until": 1.26}, {"type": "groove", "until": 27.38}, {"type": "build", "until": 31.28, "stop": True},
                                      {"type": "drop", "until": round(T, 3)}, {"type": "outro", "until": round(T + END_DUR, 3)}]}, gain_db=-11)
    edit = {"title": "Creatine & hair loss (research reel)", "fps": 30, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": ov,
            "shakes": [], "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
            "voiceTrack": "work/vo.wav", "dialogueLufs": -16.0,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "plateColor": "#56A0FB", "keywordColor": "#FFFFFF",
                         "keywords": ["DHT", "2009", "2025", "الشعر", "سحر", "منتظم", "المياه", "دكتورك", "رجبي", "فرق"],
                         "zones": [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.74}]}}
    write_edit(P, edit)
    tot = sum((c["out"] - c["in"]) / c.get("speed", 1) for c in clips)
    print(f"clips cover {tot:.3f}s (VO {VO_DUR}s); unsure words: {UNSURE}")


if __name__ == "__main__":
    main()
