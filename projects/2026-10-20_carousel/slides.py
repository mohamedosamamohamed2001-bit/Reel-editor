"""OSM 5-slide carousel (Coach Osama 2026-10-20): his 5 original photos (sRGB conversion of the iPhone P3 HEICs, 4:5 crop,
no colour change), OSM brand type (IBM Plex Sans Arabic Bold, Barlow Condensed numbers), headline white with a hard Night
3D extrusion (no soft shadow / glow / blur), supporting text on the locked #56A0FB caption bars with white text, logo and
numbering on small Night plates. Selective depth: a headline layered behind his arm (MODNet matte), never over his face."""
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = ROOT / "brand" / "fonts"
BAR = "#56A0FB"
NIGHT = "#0A0F16"
WHITE = "#FFFFFF"

SLIDES = json.loads((P / "slides.json").read_text())


def css():
    return f"""
@font-face {{ font-family: Plex; src: url('file://{F}/IBMPlexSansArabic-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: Plex; src: url('file://{F}/IBMPlexSansArabic-SemiBold.ttf'); font-weight: 600; }}
@font-face {{ font-family: Barlow; src: url('file://{F}/BarlowCondensed-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: Barlow; src: url('file://{F}/BarlowCondensed-SemiBold.ttf'); font-weight: 600; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1350px; overflow: hidden; background: {NIGHT}; }}
.slide {{ position: relative; width: 1080px; height: 1350px; overflow: hidden; }}
.layer {{ position: absolute; inset: 0; width: 1080px; height: 1350px; }}
.head {{ position: absolute; font-family: Plex; font-weight: 700; color: {WHITE}; direction: rtl; letter-spacing: 0;
        line-height: 1.22; white-space: nowrap; }}
.head .l {{ display: block; }}
.head .k {{ color: {BAR}; }}
.head.light {{ text-shadow: 0 3px 0 {NIGHT}, 0 6px 0 {NIGHT}, 0 9px 0 rgba(10,15,22,.85); }}
.head.dark {{ color: {NIGHT}; }}
.sub {{ position: absolute; direction: rtl; font-family: Plex; font-weight: 700; font-size: 37px; line-height: 1.72; }}
.sub span {{ background: {BAR}; color: {WHITE}; padding: 4px 22px 9px; border-radius: 18px;
            -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
.chip {{ position: absolute; top: 46px; height: 60px; background: {NIGHT}; border-radius: 16px; display: flex; align-items: center; }}
.logo {{ left: 46px; padding: 0 18px; }}
.logo img {{ height: 40px; display: block; mix-blend-mode: lighten; }}
.num {{ right: 46px; padding: 0 18px; font-family: Barlow; font-weight: 600; font-size: 34px; color: {WHITE}; letter-spacing: 1px; }}
.num b {{ color: {BAR}; font-weight: 700; }}
"""


def html(s):
    n = s["n"]
    head = "".join(f'<span class="l">{ln}</span>' for ln in s["head"]["lines"])
    hs = s["head"]
    hstyle = (f"top:{hs['top']}px; {hs['side']}:{hs['x']}px; font-size:{hs['size']}px; text-align:{hs.get('align','right')};"
              + (f" width:{hs['maxw']}px;" if hs.get('maxw') else ""))
    sub = s["sub"]
    sstyle = f"top:{sub['top']}px; {sub['side']}:{sub['x']}px; width:{sub['w']}px; text-align:{sub.get('align','right')};"
    sub_html = "<br>".join(f"<span>{ln}</span>" for ln in sub["lines"])
    behind = hs.get("behind", False)
    head_el = f'<div class="head {hs.get("ink","light")}" data-maxw="{hs.get("maxw", 0)}" style="{hstyle}">{head}</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body><div class="slide">
<img class="layer" src="file://{P}/work/bg_{n}.png">
{head_el if behind else ''}
{f'<img class="layer" src="file://{P}/work/person_{n}.png">' if behind else ''}
{'' if behind else head_el}
<div class="sub" style="{sstyle}">{sub_html}</div>
<div class="chip logo"><img src="file://{ROOT}/brand/logo/osm-wordmark-780x264.jpg"></div>
<div class="chip num"><b>{n}</b>/05</div>
</div><script>
// fit the headline into the free space measured from his silhouette (only a small, intentional overlap)
document.fonts.ready.then(() => {{ for (const h of document.querySelectorAll('.head')) {{
  const mw = +h.dataset.maxw; if (!mw) continue; let fs = parseFloat(getComputedStyle(h).fontSize);
  const widest = () => Math.max(...[...h.querySelectorAll('.l')].map(l => {{ const r = document.createRange(); r.selectNodeContents(l); return r.getBoundingClientRect().width; }}));
  while (widest() > mw && fs > 40) {{ fs -= 2; h.style.fontSize = fs + 'px'; }}
  document.body.dataset.fit = (document.body.dataset.fit || '') + fs + ' ';
}} document.body.dataset.ready = 1; }});
</script></body></html>"""


out = P / "work" / "html"
out.mkdir(parents=True, exist_ok=True)
for s in SLIDES:
    (out / f"slide_{s['n']}.html").write_text(html(s), encoding="utf-8")
print("html:", [s["n"] for s in SLIDES])
