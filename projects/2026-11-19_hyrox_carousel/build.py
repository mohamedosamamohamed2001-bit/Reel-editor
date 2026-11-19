"""HYROX Cairo race carousel (Coach Osama 2026-11-19): 8 slides, 1080 x 1350 (4:5), his exact copy, his 8 photos.

Design: editorial frame. Each photo sits at the top inside a thin black margin; the copy lives in a solid black panel underneath,
so no text ever touches him or the race details. One electric-blue (OSM Core Blue #56A0FB) line runs edge to edge through every
panel at the same height, so the swipe reads as one continuous strip; one blue keyword per slide; slide counter 01/08.
English: Barlow Condensed Bold caps (brand display face). Arabic: IBM Plex Sans Arabic, right-to-left, Egyptian copy as given.
Photos: iPhone originals, Display P3 -> sRGB through their own ICC profiles, EXIF orientation applied, crop + Lanczos downscale,
then one gentle grade for all 8 (soft S-curve + light vibrance). No retouching, nothing generated.

    .venv/bin/python -I projects/2026-11-19_hyrox_carousel/build.py
"""
import html, io, json, subprocess, zipfile
from pathlib import Path
from PIL import Image, ImageOps, ImageCms
import pillow_heif

pillow_heif.register_heif_opener()
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
W, H = 1080, 1350
M = 40                                       # outer margin
BLUE = "#56A0FB"
GRADE = "curves=master='0/0 0.25/0.235 0.5/0.5 0.75/0.765 1/1':interp=pchip,vibrance=intensity=0.08"

# photo, crop top (fraction of the photo height at frame width), frame height, English headline (keyword in [ ]), Arabic
SLIDES = [
    ("IMG_5099.HEIC", 0.172, 940, "MORE THAN A [RACE].", ["أكتر من مجرد سباق."]),
    ("IMG_1908.heic", 0.240, 940, "THE [START].", ["بداية تحدي مختلف، حماس وتركيز وهدف واحد."]),
    ("IMG_1910.HEIC", 0.060, 940, "NO TURNING [BACK].", ["من اللحظة دي مفيش رجوع، لازم تكمل."]),
    ("IMG_2100.HEIC", 0.170, 940, "EVERY STATION IS A NEW [CHALLENGE].", ["كل محطة ليها تحديها، وكل خطوة بتختبر قوتك."]),
    ("IMG_5044.JPG", 0.300, 940, "[MIND] OVER BODY.", ["لما جسمك يقولك كفاية، عقلك بيقولك كمّل."]),
    ("IMG_2085.JPG", 0.110, 940, "ONE MORE RUN.|ONE MORE [PUSH].", ["كل كيلو، وكل محطة، محتاجين منك مجهود أكتر."]),
    ("FullSizeRender.heic", 0.110, 940, "THE [FINISH] LINE.", ["لحظة بتنسيك كل التعب اللي فات."]),
    ("IMG_5036.JPG", 0.300, 640, None, None),   # final slide: its own copy block (below)
]
FINAL = {"head": "FIRST HYROX EXPERIENCE.", "ar1": "أول تجربة <span class=lat>HYROX</span>.", "time": "1:27:00",
         "line": "5 MINUTES FASTER THAN MY PREVIOUS TARGET.", "ar2": "مش النهاية، دي مجرد البداية.", "end": "MORE TO COME."}
LINE_Y = 1000                                # the continuous blue line (same y on every slide)
# headline size: the cover is the largest; two-line headlines a step smaller so the Arabic keeps its bottom margin
HEAD_SIZE = {1: 118, 2: 96, 3: 96, 4: 80, 5: 96, 6: 80, 7: 96}


def load(name):
    im = ImageOps.exif_transpose(Image.open(P / "source" / name))
    icc = im.info.get("icc_profile")
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), ImageCms.createProfile("sRGB"),
                                       renderingIntent=0, outputMode="RGB")
    return im.convert("RGB")


def photo(name, top, fh, out):
    im = load(name)
    fw = W - 2 * M
    s = fw / im.width
    ch = round(fh / s)                       # crop height in source px
    y0 = min(max(0, round(top * im.height)), im.height - ch)
    crop = im.crop((0, y0, im.width, y0 + ch)).resize((fw, fh), Image.LANCZOS)
    raw = out.with_suffix(".raw.png"); crop.save(raw)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", GRADE, str(out)], check=True)
    raw.unlink()
    return {"y0": y0, "ch": ch, "src": list(im.size)}


def head_html(t):
    e = html.escape(t)
    return e.replace("[", f'<span style="color:{BLUE}">').replace("]", "</span>").replace("|", "<br>")


CSS = f"""
@font-face {{ font-family: Barlow; src: url('file://{ROOT}/brand/fonts/BarlowCondensed-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: BarlowS; src: url('file://{ROOT}/brand/fonts/BarlowCondensed-SemiBold.ttf'); font-weight: 600; }}
@font-face {{ font-family: Plex; src: url('file://{ROOT}/brand/fonts/IBMPlexSansArabic-SemiBold.ttf'); font-weight: 600; }}
@font-face {{ font-family: Inter; src: url('file://{ROOT}/brand/fonts/Inter[opsz,wght].ttf'); font-weight: 100 900; }}
html,body{{margin:0;width:{W}px;height:{H}px;background:#050608;overflow:hidden}}
.ph{{position:absolute;left:{M}px;top:{M}px}}
.line{{position:absolute;left:0;width:{W}px;height:4px;background:{BLUE}}}
.cnt{{position:absolute;right:{M}px;font:600 26px/1 BarlowS;letter-spacing:.18em;color:#9AA4B2}}
.cnt b{{color:#fff;font-weight:600}}
.tag{{position:absolute;left:{M}px;font:600 26px/1 BarlowS;letter-spacing:.32em;color:#9AA4B2}}
.h{{position:absolute;left:{M}px;right:{M}px;text-align:center;font:700 92px/0.98 Barlow;color:#fff;letter-spacing:.01em}}
.ar{{position:absolute;left:{M}px;right:{M}px;text-align:center;direction:rtl;font:600 40px/1.6 Plex;color:#E5EBF1}}
.lat{{direction:ltr;unicode-bidi:isolate;font-family:Inter;font-weight:700;font-size:.9em}}
"""


def slide_html(i, img, fh, head, ar):
    n = f"<b>{i:02d}</b> / 08"
    if head is not None:
        body = (f'<img class=ph src="file://{img}">'
                f'<div class=line style="top:{LINE_Y}px"></div>'
                f'<div class=tag style="top:{LINE_Y + 24}px">HYROX CAIRO</div><div class=cnt style="top:{LINE_Y + 24}px">{n}</div>'
                f'<div class=h id=h style="top:{LINE_Y + 66}px;font-size:{HEAD_SIZE[i]}px">{head_html(head)}</div>'
                f'<div class=ar id=ar>{"<br>".join(html.escape(a) for a in ar)}</div>')
    else:   # final slide
        f = FINAL
        body = (f'<img class=ph src="file://{img}">'
                f'<div class=line style="top:{LINE_Y}px"></div>'
                f'<div class=tag style="top:{M + fh + 26}px">HYROX CAIRO</div><div class=cnt style="top:{M + fh + 26}px">{n}</div>'
                f'<div class=h style="top:{M + fh + 74}px;font-size:76px">{html.escape(f["head"])}</div>'
                f'<div class=ar style="top:{M + fh + 152}px;font-size:38px">{f["ar1"]}</div>'
                f'<div class=h style="top:{LINE_Y + 20}px;font-size:140px;color:{BLUE}">{f["time"]}</div>'
                f'<div class=h style="top:{LINE_Y + 168}px;font:600 34px/1 BarlowS;letter-spacing:.06em">{html.escape(f["line"])}</div>'
                f'<div class=ar style="top:{LINE_Y + 206}px;font-size:36px">{html.escape(f["ar2"])}</div>'
                f'<div class=h style="top:{LINE_Y + 272}px;font-size:40px;letter-spacing:.32em;padding-left:.32em">{html.escape(f["end"])}</div>')
    # the Arabic line follows the real headline height (one or two lines)
    js = ("document.fonts.ready.then(()=>{const h=document.getElementById('h'),a=document.getElementById('ar');"
          "if(h&&a){a.style.top=(h.getBoundingClientRect().bottom+14)+'px'};"
          "window.boxes=[...document.querySelectorAll('.h,.ar,.tag,.cnt')].map(e=>{const r=e.getBoundingClientRect();"
          "return [e.className,Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom),e.scrollWidth>e.clientWidth]});"
          "window.done=true})")
    return f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}<script>{js}</script></body></html>"


def main():
    W_ = P / "work"; W_.mkdir(exist_ok=True)
    out = P / "output"; out.mkdir(exist_ok=True)
    pages, meta = [], []
    for i, (name, top, fh, head, ar) in enumerate(SLIDES, 1):
        img = W_ / f"photo_{i:02d}.png"
        meta.append({"slide": i, "photo": name, **photo(name, top, fh, img)})
        page = W_ / f"slide_{i:02d}.html"
        page.write_text(slide_html(i, img, fh, head, ar))
        pages.append(str(page))
    subprocess.run(["node", str(P / "shoot.js"), str(out), *pages], check=True)
    files = []
    for i in range(1, 9):
        png = out / f"Slide {i:02d}.png"
        im = Image.open(png).convert("RGB")
        assert im.size == (W, H)
        im.save(out / f"Slide {i:02d}.jpg", quality=95, subsampling=0)
        files.append(png.name)
    with zipfile.ZipFile(out / "HYROX_Carousel.zip", "w", zipfile.ZIP_STORED) as z:
        for i in range(1, 9):
            z.write(out / f"Slide {i:02d}.jpg", f"Slide {i:02d}.jpg")
            z.write(out / f"Slide {i:02d}.png", f"PNG/Slide {i:02d}.png")
    (W_ / "meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
