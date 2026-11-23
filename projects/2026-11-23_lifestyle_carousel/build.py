"""OSM lifestyle carousel (Coach Osama 2026-11-23): 4 photos, 1080x1350, one phrase each on the locked OSM caption bar.

Photos: iPhone HEIC -> sRGB through each photo's own ICC profile (Display P3), EXIF orientation applied. 9:16 -> 4:5 crop keeps
70 % of the height: photos 1-2 keep him to his shoes (window at the bottom), photos 3-4 keep more of the ceiling light lines (their
bottom is the machine). Lanczos to 1080x1350, then ONE identical gentle grade for all four (soft S-curve, slight shadow lift,
light vibrance, mild CAS sharpening): no skin smoothing, no HDR look, no warm/yellow shift, nothing generated.
Text: the locked caption bar (#56A0FB, white Inter 700, radius 20, padding 14/30), same size and height on all four, in the dark
ceiling band, on the side AWAY from his head (never on or above it): left on 1-2, right on 3-4.

    .venv/bin/python -I projects/2026-11-23_lifestyle_carousel/build.py
"""
import json, subprocess, zipfile
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
W, H = 1080, 1350
# (photo, crop top as fraction of the photo height, phrase, side)
SLIDES = [("IMG_5686", 0.297, "Beyond the gym.", "left"), ("IMG_5689", 0.297, "It’s a lifestyle.", "left"),
          ("IMG_5690", 0.200, "Built on discipline.", "right"), ("IMG_5694", 0.200, "Enjoy the process.", "right")]
GRADE = "curves=master='0/0 0.06/0.07 0.25/0.245 0.5/0.505 0.75/0.765 1/1':interp=pchip,vibrance=intensity=0.06,cas=strength=0.35"
BAR_TOP, MARGIN = 92, 40


def main():
    out = P / "output"; out.mkdir(exist_ok=True); work = P / "work"
    pages = []
    for i, (n, top, text, side) in enumerate(SLIDES, 1):
        im = Image.open(work / f"{n}.png").convert("RGB")
        ch = round(im.width * H / W)
        y0 = min(round(top * im.height), im.height - ch)
        crop = im.crop((0, y0, im.width, y0 + ch)).resize((W, H), Image.LANCZOS)
        raw = work / f"crop_{i}.png"; crop.save(raw)
        graded = work / f"graded_{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", GRADE, "-update", "1", str(graded)], check=True)
        pos = f"left:{MARGIN}px" if side == "left" else f"right:{MARGIN}px"
        html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Inter;src:url('file://{ROOT}/brand/fonts/Inter[opsz,wght].ttf');font-weight:100 900}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:#000}}
img{{position:absolute;inset:0;width:{W}px;height:{H}px}}
.bar{{position:absolute;top:{BAR_TOP}px;{pos};font:700 46px/1.25 Inter;color:#fff;background:#56A0FB;padding:14px 30px;border-radius:20px;white-space:nowrap}}
</style></head><body><img src="file://{graded}"><div class="bar" id="b">{text}</div>
<script>document.fonts.ready.then(()=>{{const r=document.getElementById('b').getBoundingClientRect();window.box=[r.left,r.top,r.right,r.bottom].map(Math.round);window.done=true}})</script></body></html>"""
        page = work / f"slide_{i}.html"; page.write_text(html); pages.append(str(page))
    js = f"""const {{chromium}}=require('/opt/node-tools/node_modules/playwright');
(async()=>{{const b=await chromium.launch({{args:['--allow-file-access-from-files']}});const p=await b.newPage({{viewport:{{width:{W},height:{H}}}}});
const pages={json.dumps(pages)};for(const [i,f] of pages.entries()){{await p.goto('file://'+f);await p.waitForFunction(()=>window.done===true);
await p.evaluate(()=>Promise.all([...document.images].map(im=>im.decode())));console.log(i+1,JSON.stringify(await p.evaluate(()=>window.box)));
await p.screenshot({{path:'{out}/Slide '+String(i+1).padStart(2,'0')+'.png'}});}}await b.close()}})()"""
    (work / "shoot.js").write_text(js)
    subprocess.run(["node", str(work / "shoot.js")], check=True)
    with zipfile.ZipFile(out / "OSM_Lifestyle_Carousel.zip", "w", zipfile.ZIP_STORED) as z:
        for i in range(1, 5):
            png = out / f"Slide {i:02d}.png"
            Image.open(png).convert("RGB").save(out / f"Slide {i:02d}.jpg", quality=95, subsampling=0)
            z.write(out / f"Slide {i:02d}.jpg", f"Slide {i:02d}.jpg"); z.write(png, f"PNG/Slide {i:02d}.png")


if __name__ == "__main__":
    main()
