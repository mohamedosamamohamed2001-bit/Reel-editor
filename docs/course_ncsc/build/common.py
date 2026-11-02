"""Shared OSM print style + HTML helpers for the NCSC summaries and the OSM assessment manual.
Brand: brand/tokens.json (Night #0A0F16, Core Blue #56A0FB, Deep Navy #12203C, Line #263244); Inter / Barlow Condensed.
Text on Core Blue is always Night (brand contrast rule). Pages are white for print."""
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FONTS = ROOT / "brand/fonts"
LOGO = ROOT / "brand/logo/osm-wordmark-780x264.jpg"
NS = "Not Specified in Course Material"

CSS = f"""
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter[opsz,wght].ttf'); font-weight: 100 900; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-Italic[opsz,wght].ttf'); font-weight: 100 900; font-style: italic; }}
@font-face {{ font-family: Barlow; src: url('file://{FONTS}/BarlowCondensed-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: Barlow; src: url('file://{FONTS}/BarlowCondensed-SemiBold.ttf'); font-weight: 600; }}
:root {{ --night:#0A0F16; --blue:#56A0FB; --navy:#12203C; --line:#263244; --rule:#C9D3E0; --soft:#F2F5F9; --muted:#4F5B6B; }}
@page {{ size: A4; margin: 16mm 14mm 18mm 14mm; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; font-family: Inter, sans-serif; font-size: 9.3pt; line-height: 1.45; color: var(--night); background:#fff; }}
h1 {{ font-style: italic; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em; font-size: 21pt; margin: 0 0 2mm; line-height: 1.1; }}
h1 + .bar, .bar {{ width: 18mm; height: 2.2mm; background: var(--blue); margin: 0 0 6mm; }}
.chapter {{ break-before: page; }}
.eyebrow {{ font-weight: 800; font-size: 7.6pt; letter-spacing: .2em; text-transform: uppercase; color: var(--navy); margin-bottom: 1.5mm; }}
h2 {{ font-weight: 800; font-size: 12.5pt; margin: 7mm 0 2.5mm; padding-left: 3mm; border-left: 1.4mm solid var(--blue); break-after: avoid; }}
h3 {{ font-weight: 700; font-size: 10.3pt; margin: 4.5mm 0 1.5mm; break-after: avoid; color: var(--navy); }}
p {{ margin: 0 0 2.2mm; }}
ul, ol {{ margin: 0 0 2.5mm; padding-left: 5.5mm; }}
li {{ margin-bottom: .8mm; }}
table {{ width: 100%; border-collapse: collapse; margin: 1.5mm 0 4mm; break-inside: auto; }}
tr {{ break-inside: avoid; }}
thead {{ display: table-header-group; }}
th {{ background: var(--night); color: #fff; font-weight: 700; font-size: 8pt; text-align: left; padding: 1.6mm 2mm; letter-spacing: .02em; }}
td {{ border-bottom: .25mm solid var(--rule); padding: 1.5mm 2mm; vertical-align: top; font-size: 8.6pt; }}
tbody tr:nth-child(even) td {{ background: var(--soft); }}
.num {{ font-family: Barlow; font-weight: 600; font-size: 10pt; }}
.src {{ display:inline-block; font-size: 6.9pt; font-weight: 700; color: var(--muted); letter-spacing:.03em; white-space: nowrap; }}
.src::before {{ content: '['; }} .src::after {{ content: ']'; }}
.note {{ border: .3mm solid var(--rule); border-left: 1.4mm solid var(--blue); background: var(--soft); padding: 2.5mm 3.5mm; margin: 2mm 0 4mm; break-inside: avoid; font-size: 8.6pt; }}
.flag {{ border-left-color: #F2B84B; }}
.flag b.t {{ color: #8A5A00; }}
.key {{ display:grid; grid-template-columns: 1fr 1fr; gap: 3mm; margin: 2mm 0 4mm; }}
.box {{ border: .3mm solid var(--rule); padding: 2.5mm 3mm; break-inside: avoid; }}
.box h4 {{ margin: 0 0 1.2mm; font-size: 8.4pt; text-transform: uppercase; letter-spacing: .08em; color: var(--navy); }}
.pill {{ display:inline-block; background: var(--blue); color: var(--night); font-weight: 800; font-size: 7.4pt; padding: .4mm 2mm; border-radius: 1mm; letter-spacing:.05em; }}
.pill.ext {{ background:#F6D96B; }} .pill.int {{ background: var(--blue); }}
.toc td {{ border-bottom: .25mm dotted var(--rule); font-size: 9pt; }}
.small {{ font-size: 7.8pt; color: var(--muted); }}
.avoid {{ break-inside: avoid; }}
svg text {{ font-family: Inter; }}
/* cover */
.cover {{ width: 210mm; height: 297mm; background: var(--night); color: #fff; position: relative; overflow: hidden; }}
.cover .logo {{ position:absolute; left: 22mm; top: 30mm; width: 120mm; mix-blend-mode: lighten; }}
.cover .t {{ position:absolute; left: 22mm; right: 22mm; top: 125mm; }}
.cover .t .ey {{ color:#7DD2EC; font-weight:800; letter-spacing:.24em; font-size:9pt; }}
.cover .t h1 {{ font-size: 34pt; color:#fff; margin: 4mm 0 4mm; }}
.cover .t .sub {{ color:#C7D0DC; font-size: 11pt; max-width: 150mm; }}
.cover .meta {{ position:absolute; left: 22mm; right: 22mm; bottom: 24mm; color:#8C98AA; font-size: 8.4pt; border-top: .3mm solid #263244; padding-top: 4mm; }}
.cover .fields {{ position:absolute; left:22mm; right:22mm; bottom: 52mm; display:grid; grid-template-columns: 1fr 1fr; gap: 8mm; }}
.cover .fields div {{ border-bottom: .4mm solid #56A0FB; padding-bottom: 1.5mm; color:#8C98AA; font-size: 8pt; letter-spacing:.14em; font-weight:700; height: 14mm; display:flex; align-items:flex-end; }}
/* forms */
.form td {{ height: 9mm; background: #fff !important; }}
.form td.l {{ width: 36%; font-weight: 600; color: var(--navy); }}
.lines div {{ border-bottom: .25mm solid #9AA6B5; height: 8mm; }}
.rec th {{ font-size: 7.2pt; padding: 1.3mm 1.4mm; }}
.rec td {{ height: 11mm; font-size: 7.8pt; padding: 1.2mm 1.4mm; background:#fff !important; border: .25mm solid #B9C4D2; }}
.rec td.n {{ font-weight: 700; width: 24%; }}
.rec td.r {{ width: 15%; font-size: 7pt; color: var(--muted); }}
.card {{ border: .35mm solid #B9C4D2; margin: 0 0 6mm; break-inside: avoid; }}
.card .hd {{ background: var(--night); color:#fff; padding: 2.4mm 3.5mm; display:flex; justify-content: space-between; align-items: baseline; break-after: avoid; }}
.card .hd b {{ font-size: 10.5pt; }}
.card .hd span {{ color:#7DD2EC; font-size: 7.2pt; letter-spacing:.14em; font-weight:800; text-transform: uppercase; }}
.card table {{ margin: 0; }}
.card td.f {{ width: 27%; font-weight: 700; color: var(--navy); font-size: 8pt; background: var(--soft) !important; }}
.card td {{ background:#fff !important; }}
.ns {{ color: var(--muted); font-style: italic; }}
"""


def esc(s):
    return html.escape(str(s), quote=False)


def src(s):
    return f'<span class="src">{esc(s)}</span>'


def table(headers, rows, cls="", raw=False, widths=None):
    cg = "".join(f'<col style="width:{w}">' for w in widths) if widths else ""
    th = "".join(f"<th>{h if raw else esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c if raw else esc(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><colgroup>{cg}</colgroup><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def ul(items, raw=True):
    return "<ul>" + "".join(f"<li>{i if raw else esc(i)}</li>" for i in items) + "</ul>"


def ol(items):
    return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def note(html_, title="Coaching note", flag=False):
    return f'<div class="note{" flag" if flag else ""}"><b class="t">{title}:</b> {html_}</div>'


def chapter(eyebrow, title, first=False):
    return f'<section class="{"" if first else "chapter"}"><div class="eyebrow">{esc(eyebrow)}</div><h1>{esc(title)}</h1><div class="bar"></div>'


def page(title, body):
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title><style>{CSS}</style></head><body>{body}</body></html>'


def cover(eyebrow, title, sub, meta, fields=None):
    f = ""
    if fields:
        f = '<div class="fields">' + "".join(f"<div>{esc(x)}</div>" for x in fields) + "</div>"
    return page(title, f'''<div class="cover"><img class="logo" src="file://{LOGO}">
<div class="t"><div class="ey">{esc(eyebrow)}</div><h1>{title}</h1><div class="bar"></div><div class="sub">{sub}</div></div>
{f}<div class="meta">{meta}</div></div>''')


def fv_svg(points, title="", xlab="Velocity", ylab="Force", w=520, h=230):
    """Generic hyperbolic curve with labelled dots. points = [(t in 0..1, label)]."""
    import math
    x0, y0, x1, y1 = 60, 20, w - 20, h - 40
    def xy(t):
        x = x0 + 10 + t * (x1 - x0 - 20)
        y = y0 + (y1 - y0) * (1 - 1 / (1 + 6 * t)) * 1.05
        return x, min(y, y1 - 6)
    path = " ".join(("M" if i == 0 else "L") + "%.1f,%.1f" % xy(i / 60) for i in range(61))
    dots = "".join(f'<circle cx="{xy(t)[0]:.1f}" cy="{xy(t)[1]:.1f}" r="6" fill="#56A0FB" stroke="#0A0F16" stroke-width="1"/>'
                   f'<text x="{xy(t)[0] + 10:.1f}" y="{xy(t)[1] - 8:.1f}" font-size="10" font-weight="700" fill="#0A0F16">{esc(l)}</text>' for t, l in points)
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:150mm;display:block;margin:2mm 0 4mm">'
            f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#0A0F16" stroke-width="1.5"/><line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#0A0F16" stroke-width="1.5"/>'
            f'<path d="{path}" fill="none" stroke="#263244" stroke-width="2"/>{dots}'
            f'<text x="{x1}" y="{y1 + 22}" text-anchor="end" font-size="10" font-weight="700">{esc(xlab)} →</text>'
            f'<text x="{x0 - 8}" y="{y0 + 4}" text-anchor="end" font-size="10" font-weight="700">{esc(ylab)}</text>'
            f'<text x="{x0 + 8}" y="{y1 + 22}" font-size="9" fill="#4F5B6B">{esc(title)}</text></svg>')
