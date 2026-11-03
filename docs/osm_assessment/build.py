"""OSM Assessment System: build both assessment documents (PDF + editable DOCX).

    python3 docs/osm_assessment/build.py OUTDIR

Layout is table-based so the same HTML renders in Chromium (PDF) and converts cleanly with LibreOffice (DOCX).
Brand (brand/tokens.json): Night #0A0F16, Core Blue #56A0FB (text on it = Night), Deep Navy #12203C, Signal Cyan #7DD2EC (dark only).
"""
import html, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import content as C
sys.path.insert(0, str(ROOT / "docs/course_ncsc/build"))
from phase1 import SKIN, VBT  # reference tables (values only)

FONTS, LOGO = ROOT / "brand/fonts", ROOT / "brand/logo/osm-wordmark-780x264.jpg"
NIGHT, BLUE, NAVY, CYAN, TINT, TINT2, RULE, MUTED = "#0A0F16", "#56A0FB", "#12203C", "#7DD2EC", "#EAF2FE", "#CFE2FD", "#C9D3E0", "#4F5B6B"
e = html.escape

CHIP = {"Good": (BLUE, NIGHT), "Excellent": (BLUE, NIGHT), "World class": (NAVY, "#FFFFFF"), "Average": (TINT2, NIGHT), "Moderate": (TINT2, NIGHT),
        "Poor": (NAVY, "#FFFFFF"), "Low": (NAVY, "#FFFFFF")}


def css(title):
    return f"""
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter[opsz,wght].ttf'); font-weight: 100 900; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-Italic[opsz,wght].ttf'); font-weight: 100 900; font-style: italic; }}
@font-face {{ font-family: Barlow; src: url('file://{FONTS}/BarlowCondensed-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: Barlow; src: url('file://{FONTS}/BarlowCondensed-SemiBold.ttf'); font-weight: 600; }}
@page {{ size: A4; margin: 15mm 15mm 17mm 15mm;
  @bottom-left {{ content: "OSM · Osama Strength Method  —  {title}"; font: 600 8pt Inter, Arial; color: {MUTED}; }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font: 600 8pt Inter, Arial; color: {NAVY}; }} }}
@page cover {{ margin: 0; @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #fff; color: {NIGHT}; font-family: Inter, Arial, sans-serif; font-size: 11pt; line-height: 1.42; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ vertical-align: top; text-align: left; }}
ol {{ margin: 0; padding-left: 5.5mm; }} ol li {{ margin: 0 0 1.2mm; padding-left: .5mm; }} ol li:last-child {{ margin-bottom: 0; }}
.cover {{ page: cover; width: 210mm; height: 297mm; background: {NIGHT}; color: #fff; position: relative; overflow: hidden; }}
.cover .logo {{ position: absolute; left: 20mm; top: 26mm; width: 112mm; mix-blend-mode: lighten; }}
.cover .stripe {{ position: absolute; right: 0; top: 0; width: 9mm; height: 297mm; background: {BLUE}; }}
.cover .t {{ position: absolute; left: 20mm; right: 26mm; top: 118mm; }}
.cover .ey {{ font: 700 13pt Barlow; letter-spacing: .26em; color: {CYAN}; }}
.cover h1 {{ font: italic 900 38pt/1.02 Inter; text-transform: uppercase; letter-spacing: -.02em; margin: 4mm 0 5mm; color: #fff; }}
.cover .bar {{ width: 26mm; height: 2.6mm; background: {BLUE}; margin-bottom: 6mm; }}
.cover .sub {{ font-size: 12.5pt; color: #C7D0DC; }}
.cover .fields {{ position: absolute; left: 20mm; width: 160mm; bottom: 46mm; table-layout: fixed; }}
.cover .fields td {{ padding: 0 6mm 0 0; }}
.cover .fields div {{ border-bottom: .5mm solid {BLUE}; height: 15mm; display: flex; align-items: flex-end; padding-bottom: 1.5mm; font: 700 10pt Barlow; letter-spacing: .18em; color: #8C98AA; }}
.cover .foot {{ position: absolute; left: 20mm; right: 26mm; bottom: 20mm; border-top: .3mm solid #263244; padding-top: 4mm; font: 700 10pt Barlow; letter-spacing: .3em; color: #8C98AA; }}
.page {{ break-before: page; }}
.ptitle td {{ padding: 0; }}
.ptitle .ey {{ font: 700 10.5pt Barlow; letter-spacing: .24em; color: {BLUE}; text-transform: uppercase; }}
h2 {{ font: italic 900 22pt/1.1 Inter; text-transform: uppercase; letter-spacing: -.01em; margin: 1mm 0 2mm; color: {NIGHT}; }}
.rule {{ height: 2.2mm; width: 22mm; background: {BLUE}; margin: 0 0 6mm; }}
.lead {{ font-size: 11pt; color: {MUTED}; margin: -2mm 0 5mm; }}
.form td {{ border-bottom: .35mm solid {RULE}; padding: 0 3mm; height: 13mm; vertical-align: bottom; padding-bottom: 2mm; }}
.form td.k {{ width: 62mm; font: 700 11pt Barlow; letter-spacing: .06em; text-transform: uppercase; color: {NAVY}; background: {TINT}; border-bottom: .35mm solid #fff; vertical-align: middle; padding-bottom: 0; }}
.box {{ border-left: 1.6mm solid {BLUE}; background: {TINT}; padding: 3.5mm 4.5mm; margin: 0 0 5mm; break-inside: avoid; }}
.box b.h {{ display: block; font: 700 11pt Barlow; letter-spacing: .14em; text-transform: uppercase; color: {NAVY}; margin-bottom: 1.5mm; }}
.box ul {{ margin: 0; padding-left: 5mm; }} .box li {{ margin-bottom: 1mm; }}
.toc td {{ padding: 2.2mm 3mm; border-bottom: .3mm solid {RULE}; font-size: 11pt; }}
.toc td.n {{ width: 14mm; font: 700 13pt Barlow; color: {BLUE}; }}
.toc tr.s td {{ background: {NIGHT}; color: #fff; font: 700 11pt Barlow; letter-spacing: .16em; text-transform: uppercase; border-bottom: 0; }}
.sec {{ margin-bottom: 4mm; }}
.sec td {{ background: {NIGHT}; color: #fff; padding: 2.4mm 5mm; vertical-align: middle; }}
.sec td.no {{ width: 30mm; background: {BLUE}; color: {NIGHT}; font: 700 12pt Barlow; letter-spacing: .14em; vertical-align: middle; }}
.sec .nm {{ font: italic 900 15pt/1.1 Inter; text-transform: uppercase; }}
.sec .ct {{ font: 600 10.5pt Barlow; letter-spacing: .18em; color: {CYAN}; text-transform: uppercase; text-align: right; }}
.test {{ break-before: page; height: 262mm; display: flex; flex-direction: column; overflow: hidden; }}
.cbox {{ flex: 1; min-height: 27mm; background: repeating-linear-gradient(to bottom, #fff 0, #fff 8.7mm, {RULE} 8.7mm, {RULE} 9mm); }}
.over {{ outline: 3px solid red; }}
.test .hd td {{ padding: 2.6mm 4mm; vertical-align: middle; }}
.test .hd td.no {{ width: 16mm; background: {BLUE}; color: {NIGHT}; font: 700 17pt Barlow; text-align: center; }}
.test .hd td.nm {{ background: {NIGHT}; color: #fff; font: 800 14pt Inter; letter-spacing: -.01em; }}
.test .hd td.ct {{ background: {NIGHT}; color: {CYAN}; font: 600 9.5pt Barlow; letter-spacing: .18em; text-transform: uppercase; text-align: right; width: 48mm; }}
.info td {{ padding: 2.3mm 3.5mm; border-bottom: .3mm solid {RULE}; font-size: 11pt; }}
.info td.k {{ width: 33mm; background: {TINT}; font: 700 10pt/1.25 Barlow; letter-spacing: .1em; text-transform: uppercase; color: {NAVY}; border-bottom: .3mm solid #fff; }}
.ref {{ margin-top: 2mm; width: auto; }}
.ref td {{ padding: 1.2mm 3mm; font-size: 10.5pt; border: 0; vertical-align: middle; }}
.ref td.chip {{ font: 700 10pt Barlow; letter-spacing: .1em; text-transform: uppercase; text-align: center; width: 30mm; border-bottom: .6mm solid #fff; }}
.std {{ margin-top: 1.5mm; font-style: italic; color: {NAVY}; }}
.note {{ margin-top: 1.5mm; font-size: 10pt; color: {MUTED}; }}
.lab {{ font: 700 10.5pt Barlow; letter-spacing: .2em; color: {NAVY}; text-transform: uppercase; margin: 4mm 0 1.5mm; padding-left: 2.5mm; border-left: 1.2mm solid {BLUE}; }}
.res th {{ background: {NAVY}; color: #fff; font: 600 10pt Barlow; letter-spacing: .08em; text-transform: uppercase; padding: 1.8mm 2.5mm; border: .3mm solid {NAVY}; }}
.res td {{ border: .3mm solid {RULE}; height: 10.5mm; padding: 1.5mm 2.5mm; font-size: 10.5pt; vertical-align: middle; }}
.res td.r {{ font-weight: 700; color: {NAVY}; background: {TINT}; }}
.res.chk td {{ height: 7.6mm; font-size: 10pt; padding: 1mm 2mm; }} .res.chk th {{ padding: 1.5mm 2mm; }}
.two td {{ padding: 0; vertical-align: top; }}
.res td.x {{ color: {MUTED}; font-style: italic; font-size: 9.5pt; }}
.lines td {{ height: 9mm; border-bottom: .3mm solid {RULE}; }}
.calc td, .calc th {{ border: .3mm solid {RULE}; padding: 2.2mm 3mm; font-size: 10.5pt; vertical-align: middle; }}
.calc th {{ background: {NAVY}; color: #fff; font: 600 10pt Barlow; letter-spacing: .08em; text-transform: uppercase; }}
.calc td.k {{ font-weight: 700; color: {NAVY}; background: {TINT}; width: 42mm; }}
.calc td.v {{ width: 30mm; }}
.rt td, .rt th {{ border: .3mm solid {RULE}; padding: 1mm 2.5mm; font-size: 10pt; text-align: center; }}
.rt th {{ background: {NAVY}; color: #fff; font: 600 9.5pt Barlow; letter-spacing: .08em; text-transform: uppercase; }}
.rt td.s {{ background: {TINT}; font-weight: 700; color: {NAVY}; }}
.avoid {{ break-inside: avoid; }}
"""


def word_html(body):
    """Editable (DOCX) variant: no CSS. Every visual is carried by HTML attributes that LibreOffice/Word keep."""
    import re
    body = re.sub(r'<div class="box"><b class="h">(.*?)</b>(.*?)</div>',
                  lambda m: f'<table border="1" cellpadding="8" cellspacing="0" width="100%"><tr><td bgcolor="{TINT}"><b><font color="{NAVY}">{m.group(1).upper()}</font></b><br>{m.group(2)}</td></tr></table><p></p>', body, flags=re.S)
    body = re.sub(r'<div class="lab">(.*?)</div>', lambda m: f'<p><b><font color="{NAVY}">{m.group(1).upper()}</font></b></p>', body)
    body = re.sub(r'<div class="ey">(.*?)</div>', lambda m: f'<p><b><font color="{BLUE}">{m.group(1).upper()}</font></b></p>', body)
    body = body.replace('<div class="rule"></div>', "")
    body = re.sub(r'<div class="(page|test)">', '<p style="page-break-before: always; margin:0; font-size:2pt">&nbsp;</p><div>', body)
    body = re.sub(r'<table(?![^>]*border=)', '<table border="1"', body)
    body = re.sub(r'<table([^>]*)>', lambda m: m.group(0) if "width=" in m.group(1) else f'<table{m.group(1)} width="100%" cellpadding="5">', body)
    body = body.replace('<td class="cbox"></td>', "")
    return body


def head_tag(title, body, editable):
    if editable:
        style = "body { font-family: Arial, sans-serif; font-size: 11pt; } td, th { font-size: 10.5pt; } h2 { font-size: 18pt; font-style: italic; }"
        body = word_html(body)
    else:
        style = css(title)
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>OSM – {e(title)}</title><style>{style}</style></head><body>{body}</body></html>'


def td(text, cls="", bg=None, fg=None, raw=False, attrs=""):
    a = f' class="{cls}"' if cls else ""
    if bg: a += f' bgcolor="{bg}"'
    t = text if raw else e(text)
    if fg: t = f'<font color="{fg}">{t}</font>'
    return f"<td{a}{attrs}>{t}</td>"


def rows_table(headers, rows, cls="res", label_first=True):
    h = "<tr>" + "".join(f'<th bgcolor="{NAVY}"><font color="#FFFFFF">{e(x)}</font></th>' for x in headers) + "</tr>" if headers else ""
    b = ""
    for r in rows:
        b += "<tr>" + "".join(td(c, "r" if (i == 0 and label_first and c) else "", TINT if (i == 0 and label_first and c) else None) for i, c in enumerate(r)) + "</tr>"
    return f'<table class="{cls}" border="1" cellspacing="0" cellpadding="5">{h}{b}</table>'


def ref_html(t):
    r, out = t["ref"], ""
    if isinstance(r, str):
        out = f'<div class="std">{e(r)}</div>'
    else:
        rows = ""
        for k, v in r:
            bg, fg = CHIP.get(k, (TINT, NAVY))
            rows += f'<tr><td class="chip" bgcolor="{bg}" style="background:{bg};color:{fg}"><font color="{fg}">{e(k)}</font></td><td>{e(v)}</td></tr>'
        out = f'<table class="ref" cellspacing="0">{rows}</table>'
    if t.get("refnote"):
        out += f'<div class="note">{e(t["refnote"])}</div>'
    return f'<div>{e(t["measure"])}</div>{out}'


def results_html(t):
    kind = t["results"][0]
    if kind == "lr":
        cols = t["results"][1]
        return rows_table(["Side"] + cols, [["Left"] + [""] * len(cols), ["Right"] + [""] * len(cols)])
    if kind == "trials":
        _, unit, n, measures = t["results"]
        return rows_table(["Measure"] + [f"Trial {i}" for i in range(1, n + 1)] + ["Best"], [[m] + [""] * (n + 1) for m in measures])
    if kind == "table":
        _, hdr, rows = t["results"]
        return rows_table(hdr, rows)
    if kind == "check":
        items = t["results"][1]
        def half(its, total=False):
            r = ""
            for g, it, scored in its:
                r += f'<tr>{td(g, "r", TINT)}{td(it)}<td></td>{td("" if scored else "observe", "x" if not scored else "")}</tr>'
            if total:
                r += f'<tr>{td("", "r", TINT)}<td><b>Total score (max 12)</b></td><td></td><td></td></tr>'
            h = "".join(f'<th bgcolor="{NAVY}"><font color="#FFFFFF">{x}</font></th>' for x in ["View", "Fault", "✓ / L / R", "Pts"])
            return f'<table class="res chk" border="1" cellspacing="0" cellpadding="4"><tr>{h}</tr>{r}</table>'
        front = [x for x in items if x[0] != "Side"]
        side = [x for x in items if x[0] == "Side"]
        return f'<table class="two" cellspacing="0"><tr><td style="padding-right:2mm;width:50%">{half(front, True)}</td><td style="padding-left:2mm">{half(side)}</td></tr></table>'
    raise ValueError(kind)


def lines(n):
    return '<table class="lines" cellspacing="0">' + "<tr><td>&nbsp;</td></tr>" * n + "</table>"


def test_html(no, t, section, band='', editable=False):
    info = [("Purpose", e(t["purpose"])), ("Equipment", e(t["equip"])),
            ("Protocol", "<ol>" + "".join(f"<li>{e(s)}</li>" for s in t["protocol"]) + "</ol>"),
            ("Measurement &amp; reference", ref_html(t))]
    rows = "".join(f'<tr><td class="k" width="22%" bgcolor="{TINT}">{k}</td><td width="78%">{v}</td></tr>' for k, v in info)
    return (f'<div class="test">{band}<table class="hd" cellspacing="0"><tr>'
            f'<td class="no" bgcolor="{BLUE}">{no:02d}</td><td class="nm" bgcolor="{NIGHT}"><font color="#FFFFFF">{e(t["name"])}</font></td>'
            f'<td class="ct" bgcolor="{NIGHT}"><font color="{CYAN}">{e(section)}</font></td></tr></table>'
            f'<table class="info" cellspacing="0">{rows}</table>'
            f'<div class="lab">Client results</div>{results_html(t)}'
            f'<div class="lab">Coach comments</div>' + (lines(t.get("lines", 5)) if editable else '<div class="cbox"></div>') + '</div>')


def ptitle(eyebrow, title, lead=None, page=True):
    return (f'<div class="{"page" if page else ""}"><div class="ptitle"><div class="ey">{e(eyebrow)}</div><h2>{e(title)}</h2><div class="rule"></div>'
            + (f'<p class="lead">{e(lead)}</p>' if lead else "") + "</div>")


def cover(doc, editable):
    if editable:
        return (f'<table bgcolor="{NIGHT}" cellpadding="18" width="100%"><tr><td bgcolor="{NIGHT}"><img src="file://{LOGO}" width="300"><br><br>'
                f'<font color="{CYAN}"><b>OSM ASSESSMENT SYSTEM</b></font><br><font color="#FFFFFF" size="6"><b><i>{e(doc["title"].upper())}</i></b></font><br>'
                f'<font color="#C7D0DC">{e(doc["sub"])}</font><br><br><font color="#8C98AA">CLIENT NAME: ____________________________<br><br>'
                f'ASSESSMENT DATE: ______________<br><br>COACH: ____________________</font><br><br><font color="#8C98AA">OSAMA STRENGTH METHOD</font></td></tr></table>')
    return (f'<div class="cover"><div class="stripe"></div><img class="logo" src="file://{LOGO}"><div class="t"><div class="ey">OSM ASSESSMENT SYSTEM</div>'
            f'<h1>{e(doc["title"])}</h1><div class="bar"></div><div class="sub">{e(doc["sub"])}</div></div>'
            f'<table class="fields"><tr><td><div>CLIENT NAME</div></td><td><div>ASSESSMENT DATE</div></td><td style="width:42mm"><div>COACH</div></td></tr></table>'
            f'<div class="foot">OSAMA STRENGTH METHOD</div></div>')


def profile():
    rows = ""
    for label, h in C.PROFILE:
        rows += f'<tr><td class="k" width="34%" bgcolor="{TINT}">{e(label)}</td><td width="66%" style="height:{13 * h}mm">&nbsp;' + "<br>&nbsp;" * (h - 1) + '</td></tr>'
    return ptitle("Section 1", "Client profile", "Complete with the client before testing.", page=False) + f'<table class="form" cellspacing="0">{rows}</table>'


def contents(doc):
    rows, n = "", 1
    for i, (sec, tests) in enumerate(doc["sections"], 2):
        rows += f'<tr class="s"><td colspan="2" bgcolor="{NIGHT}"><font color="#FFFFFF">Section {i} · {e(sec)}</font></td></tr>'
        for t in tests:
            rows += f'<tr><td class="n">{n:02d}</td><td>{e(t["name"])}</td></tr>'
            n += 1
    extra = ["Calculations", "Reference tables", "Assessment summary"] if "calcs" in doc else ["Assessment summary"]
    rows += f'<tr class="s"><td colspan="2" bgcolor="{NIGHT}"><font color="#FFFFFF">Final pages</font></td></tr>' + "".join(f'<tr><td class="n">·</td><td>{x}</td></tr>' for x in extra)
    box = ('<div class="box"><b class="h">Before you start</b><ul>' + "".join(f"<li>{e(x)}</li>" for x in doc["intro"]) + "</ul></div>"
           + f'<div class="box"><b class="h">Equipment checklist</b>{e(doc["kit"])}</div>')
    return ptitle("How to use", "Assessment overview") + box + f'<table class="toc" cellspacing="0">{rows}</table>'


def calcs(doc):
    rows = ""
    for name, f, use, items in doc["calcs"]:
        rows += f'<tr>{td(name, "k", TINT)}{td(f)}{td(use)}<td class="v">' + "<br>".join(f'<span style="font-size:9pt;color:{MUTED}">{e(x)}:</span> ______' for x in items) + "</td></tr>"
    h = "".join(f'<th bgcolor="{NAVY}"><font color="#FFFFFF">{x}</font></th>' for x in ["Calculation", "Formula", "Reference / use", "Client value"])
    return ptitle("Calculations", "Derived values", "Work these out after testing. Each uses results recorded in this document.") + f'<table class="calc" cellspacing="0" border="1">{h}{rows}</table>'


def ref_tables():
    s = [r for r in SKIN if r[0] >= 15]
    half = (len(s) + 1) // 2
    L, R = s[:half], s[half:]
    rows = ""
    for i in range(half):
        a = L[i]
        b = R[i] if i < len(R) else None
        rows += (f'<tr><td class="s" bgcolor="{TINT}">{a[0]}</td><td>{a[1]:.1f}</td><td>{a[2]:.1f}</td>'
                 + (f'<td class="s" bgcolor="{TINT}">{b[0]}</td><td>{b[1]:.1f}</td><td>{b[2]:.1f}</td>' if b else "<td></td><td></td><td></td>") + "</tr>")
    h = "".join(f'<th bgcolor="{NAVY}"><font color="#FFFFFF">{x}</font></th>' for x in ["Sum of 4 (mm)", "Male %", "Female %"] * 2)
    skin = f'<table class="rt" cellspacing="0" border="1">{h}{rows}</table>'
    half = (len(VBT) + 1) // 2
    vr = ""
    for i in range(half):
        a = VBT[i]; b = VBT[i + half] if i + half < len(VBT) else None
        vr += f'<tr><td class="s" bgcolor="{TINT}">{a[0]}%</td><td>{a[1]:.2f}</td>' + (f'<td class="s" bgcolor="{TINT}">{b[0]}%</td><td>{b[1]:.2f}</td>' if b else "<td></td><td></td>") + "</tr>"
    vh = "".join(f'<th bgcolor="{NAVY}"><font color="#FFFFFF">{x}</font></th>' for x in ["%1RM", "Mean velocity (m/s)"] * 2)
    zones = rows_table(["Training zone (lower body)", "Velocity", "%1RM"], [["Maximal strength", "0.3–0.5 m/s", "85%+"], ["General strength", "0.5–0.7 m/s", "75–85%"],
                                                                          ["Heavy power", "0.7–1.1 m/s", "60–80%"], ["Light power", "1.1–1.5 m/s", "40–60%"]], cls="rt")
    return (ptitle("Reference tables", "Skinfolds → body fat %", "Find the client's sum of 4 skinfolds (mm) and read body fat % for their sex. Use the nearest value.") + skin
            + ptitle("Reference tables", "Load–velocity (back squat)", "Mean concentric velocity at each %1RM. Use with the Estimated 1RM – Velocity Method test.")
            + f'<table class="rt" cellspacing="0" border="1">{vh}{vr}</table><div style="height:7mm"></div>' + zones)


def summary():
    pr = rows_table(["Priority", "Finding", "Planned action"], [["High", "", ""], ["High", "", ""], ["Medium", "", ""], ["Medium", "", ""], ["Low", "", ""]])
    return (ptitle("Final page", "Assessment summary", "Complete after testing. Priorities guide the next training block.")
            + '<div class="lab">Key strengths</div>' + lines(3) + '<div class="lab">Priorities</div>' + pr
            + '<div class="lab">Referral to a healthcare professional needed?</div>' + rows_table(["Yes / No", "Reason / to whom"], [["", ""]])
            + '<div class="lab">Plan &amp; next assessment</div>' + rows_table(["Next assessment date", "Tests to repeat"], [["", ""]]) + lines(2))


def build_doc(doc, editable=False):
    b = [cover(doc, editable), '<div class="page">' + profile() + "</div>", contents(doc)]
    n = 1
    for i, (sec, tests) in enumerate(doc["sections"], 2):
        band = (f'<table class="sec" cellspacing="0"><tr><td class="no" bgcolor="{BLUE}">SECTION {i}</td><td bgcolor="{NIGHT}"><div class="nm"><font color="#FFFFFF">{e(sec)}</font></div></td>'
                f'<td bgcolor="{NIGHT}" class="ct"><font color="{CYAN}">{len(tests)} assessment{"s" if len(tests) > 1 else ""}</font></td></tr></table>')
        for j, t in enumerate(tests):
            b.append(test_html(n, t, sec, band if j == 0 else "", editable)); n += 1
    if "calcs" in doc:
        b += [calcs(doc), ref_tables()]
    b.append(summary())
    return head_tag(doc["title"], "".join(b), editable)


def main():
    out = Path(sys.argv[1]).resolve(); tmp = out / "_build"; tmp.mkdir(parents=True, exist_ok=True)
    for doc in (C.MOBILITY, C.PERFORMANCE):
        name = f"OSM – {doc['title']}"
        h = tmp / f"{name}.html"; h.write_text(build_doc(doc), encoding="utf-8")
        subprocess.run(["node", str(HERE / "render.js"), str(h), str(out / f"{name}.pdf")], check=True)
        ed = tmp / f"{name} (Editable).html"; ed.write_text(build_doc(doc, editable=True), encoding="utf-8")
        subprocess.run(["soffice", "--headless", "--convert-to", "docx:MS Word 2007 XML", "--outdir", str(tmp), str(ed)], check=True, capture_output=True)
        shutil.copy(tmp / f"{ed.stem}.docx", out / f"{ed.stem}.docx")
        print("wrote", name)


if __name__ == "__main__":
    main()
