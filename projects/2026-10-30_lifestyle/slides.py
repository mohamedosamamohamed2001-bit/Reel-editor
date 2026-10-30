"""OSM lifestyle carousel (Coach Osama 2026-10-30): the beach carousel system (projects/2026-10-20_beach) unchanged, 6 slides,
English-only copy (bars set in Inter Bold, the brand English face). Beach notes: the same OSM carousel system as projects/2026-10-20_carousel (logo + number
chips on Night, white headline with the hard Night 3D extrusion, tip text on the locked #56A0FB bars with white text,
IBM Plex Sans Arabic Bold) + an English headline in Inter Black Italic CAPS (brand title style). His photos unchanged
(sRGB conversion, 4:5 crop). Text never on, above or behind his head; each block placed in that photo's open space."""
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = ROOT / "brand" / "fonts"
BAR, NIGHT, WHITE = "#56A0FB", "#0A0F16", "#FFFFFF"
EXTRUDE = f"0 3px 0 {NIGHT}, 0 6px 0 {NIGHT}, 0 9px 0 rgba(10,15,22,.85)"  # same hard 3D edge as the gym carousel


def css():
    return f"""
@font-face {{ font-family: Plex; src: url('file://{F}/IBMPlexSansArabic-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: Barlow; src: url('file://{F}/BarlowCondensed-SemiBold.ttf'); font-weight: 600; }}
@font-face {{ font-family: Barlow; src: url('file://{F}/BarlowCondensed-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: Inter; src: url('file://{F}/Inter[opsz,wght].ttf'); font-weight: 100 900; }}
@font-face {{ font-family: InterI; src: url('file://{F}/Inter-Italic[opsz,wght].ttf'); font-weight: 100 900; font-style: italic; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1350px; overflow: hidden; background: {NIGHT}; }}
.slide {{ position: relative; width: 1080px; height: 1350px; overflow: hidden; }}
.layer {{ position: absolute; inset: 0; width: 1080px; height: 1350px; }}
.block {{ position: absolute; }}
.en {{ font-family: InterI; font-style: italic; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em;
       color: {WHITE}; line-height: 1.0; text-shadow: {EXTRUDE}; direction: ltr; }}
.ar {{ white-space: nowrap; font-family: Plex; font-weight: 700; color: {WHITE}; direction: rtl; line-height: 1.45; text-shadow: {EXTRUDE};
       margin-top: 18px; }}
.sub {{ direction: rtl; font-family: Plex; font-weight: 700; font-size: 37px; line-height: 1.72; }}
.sub span {{ white-space: nowrap; background: {BAR}; color: {WHITE}; padding: 4px 22px 9px; border-radius: 18px;
            -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
.sub.ltr {{ direction: ltr; font-family: Inter; font-weight: 700; line-height: 1.78; }}
.sub.ltr span {{ padding: 5px 22px 9px; }}
.chip {{ position: absolute; top: 46px; height: 60px; background: {NIGHT}; border-radius: 16px; display: flex; align-items: center; }}
.logo {{ left: 46px; padding: 0 18px; }}
.logo img {{ height: 40px; display: block; mix-blend-mode: lighten; }}
.num {{ right: 46px; padding: 0 18px; font-family: Barlow; font-weight: 600; font-size: 34px; color: {WHITE}; letter-spacing: 1px; }}
.num b {{ color: {BAR}; font-weight: 700; }}
"""


def block(b, en=None, ar=None, sub=None):
    pos = f"top:{b['top']}px; {b['side']}:{b['x']}px; width:{b['w']}px; text-align:{b.get('align', 'right')};"
    h = f'<div class="block" id="b{b.get("id", 0)}" style="{pos}">'
    if en:
        h += f'<div class="en" style="font-size:{b["en"]}px">' + "<br>".join(en) + "</div>"
    if ar:
        h += f'<div class="ar" style="font-size:{b["ar"]}px">' + "<br>".join(ar) + "</div>"
    if sub:
        h += f'<div class="sub{" ltr" if b.get("ltr") else ""}" style="margin-top:{b.get("gap", 26)}px; font-size:{b.get("subsize", 37)}px">' + "<br>".join(f"<span>{s}</span>" for s in sub) + "</div>"
    return h + "</div>"


def html(s):
    n = s["n"]
    body = ""
    for b in s["blocks"]:
        body += block(b, s["en"] if "en" in b else None, s["ar"] if "ar" in b else None, s["tip"] if b.get("tip") else None)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body><div class="slide">
<img class="layer" src="file://{P}/work/bg_{n}.png">{body}
<div class="chip logo"><img src="file://{ROOT}/brand/logo/osm-wordmark-780x264.jpg"></div>
<div class="chip num"><b>{n}</b>/06</div></div>
<script>document.fonts.ready.then(() => document.body.dataset.ready = 1)</script></body></html>"""


out = P / "work" / "html"; out.mkdir(parents=True, exist_ok=True)
for s in json.loads((P / "slides.json").read_text()):
    (out / f"slide_{s['n']}.html").write_text(html(s), encoding="utf-8")
print("html written")
