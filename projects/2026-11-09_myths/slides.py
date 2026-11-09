"""OSM carousel: 5 Training Myths You Need to Stop Believing (Coach Osama 2026-11-09). 5 slides, 1080x1350 (4:5).

His 5 original photos (HEIC -> sRGB through each photo's own ICC profile, 4:5 crop, Lanczos resize; no colour change, nothing
generated). OSM carousel system (projects/2026-11-06_mistakes): OSM logo + NN/05 chips on Night, English headlines in Inter Black
Italic CAPS with the hard Night extrusion (no soft shadow / glow / blur), Arabic in IBM Plex Sans Arabic Bold, Arabic body on the
locked #56A0FB bar with white text, Core Blue for the accent words, text on Core Blue = Night.
Layout: his photo full-bleed; the copy sits on a solid Night card on the lower part of the frame. Every card is auto-fitted so its
top stays below his chin (YuNet face box from prep.py) - never on or above his head. English left-aligned, Arabic right-aligned.
The copy is the brief's wording, unchanged (structural labels only: MYTH #N, THE SCIENCE).

    .venv/bin/python projects/2026-11-09_myths/slides.py && node projects/2026-11-09_myths/render.js
"""
import json, re
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = ROOT / "brand" / "fonts"
BAR, NIGHT, WHITE, SKY = "#56A0FB", "#0A0F16", "#FFFFFF", "#7DD2EC"
EXTRUDE = f"0 3px 0 {NIGHT}, 0 6px 0 {NIGHT}, 0 9px 0 rgba(10,15,22,.85)"
N, MARGIN = 5, 54

# [[...]] = Core Blue accent in English headlines; {{...}} = an English run inside Arabic (one isolated LTR run)
SLIDES = [
    dict(kind="cover",
         en=["TRAINING MYTHS", "YOU NEED TO", "[[STOP BELIEVING]]"],
         ar="5 مفاهيم غلط لازم تبطل تصدقها في التمرين"),
    dict(kind="myth", no=1, q="MORE WEIGHT = [[MORE MUSCLE?]]",
         ar="مش كل ما الوزن يزيد العضلات تكبر أسرع!",
         fact_en="Muscle growth depends on effective training, not just lifting heavier weights.",
         fact_ar="نمو العضلات بيعتمد على جودة وحجم التدريب، مش الوزن بس."),
    dict(kind="myth", no=2, q="MORE SWEAT = [[MORE FAT LOSS?]]",
         ar="العرق مش مقياس لحرق الدهون!",
         fact_en="Sweating mainly helps regulate body temperature.",
         fact_ar="العرق وظيفته الأساسية تنظيم درجة حرارة الجسم، مش قياس الدهون اللي بتحرقها."),
    dict(kind="myth", no=3, q="CAN YOU BURN [[BELLY FAT]] WITH ABS EXERCISES?",
         ar="تمارين البطن مش بتحرق دهون البطن بشكل موضعي!",
         fact_en="Fat loss happens through an overall energy deficit.",
         fact_ar="خسارة الدهون بتحصل من الجسم بشكل عام، مش من منطقة معينة."),
    dict(kind="double", myths=[
        dict(no=4, q="REST DAYS ARE A [[WASTE OF TIME?]]",
             ar="أيام الراحة جزء من خطة التطور!",
             fact_en="Recovery allows your body to adapt to training.",
             fact_ar="الاستشفاء بيساعد جسمك يتأقلم مع الحمل التدريبي ويتطور."),
        dict(no=5, q="YOU MUST TRAIN UNTIL [[FAILURE]] EVERY SET?",
             ar="مش لازم توصل للفشل العضلي في كل {{Set}}!",
             fact_en="You can build muscle effectively while leaving some reps in reserve.",
             fact_ar="تقدر تبني عضلات بكفاءة من غير ما توصل للفشل العضلي في كل مجموعة."),
    ], final_en="DON’T FOLLOW MYTHS.<br>[[FOLLOW SCIENCE.]]", final_ar="متتبعش الخرافات.. اتبع العلم."),
]


def mark(s, cls="k"):
    s = re.sub(r"\{\{(.+?)\}\}", lambda m: f'<bdi dir="ltr" class="run">{m.group(1)}</bdi>', s)
    return re.sub(r"\[\[(.+?)\]\]", lambda m: f'<span class="{cls}">{m.group(1)}</span>', s)


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
.bg {{ position: absolute; inset: 0; width: 1080px; height: 1350px; }}
.chip {{ position: absolute; top: 46px; height: 60px; background: {NIGHT}; border-radius: 16px; display: flex; align-items: center; }}
.logo {{ left: 46px; padding: 0 18px; }}
.logo img {{ height: 40px; display: block; mix-blend-mode: lighten; }}
.num {{ right: 46px; padding: 0 18px; font-family: Barlow; font-weight: 600; font-size: 34px; color: {WHITE}; letter-spacing: 1px; }}
.num b {{ color: {BAR}; font-weight: 700; }}
.H {{ font-family: InterI; font-style: italic; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em; color: {WHITE}; line-height: .98; direction: ltr; }}
.H .k {{ color: {BAR}; }}
.AR {{ font-family: Plex; font-weight: 700; color: {WHITE}; direction: rtl; text-align: right; line-height: 1.45; }}
.AR .run {{ font-family: Inter; font-weight: 800; }}
.card {{ position: absolute; left: {MARGIN}px; right: {MARGIN}px; background: {NIGHT}; border-radius: 30px; padding: 40px 44px 44px; }}
.pill {{ display: inline-block; background: {BAR}; color: {NIGHT}; font-family: Barlow; font-weight: 700; letter-spacing: .14em;
        padding: 4px 18px 2px; border-radius: 10px; }}
.hr {{ height: 3px; background: #263244; border-radius: 2px; }}
.lab {{ font-family: Barlow; font-weight: 700; letter-spacing: .22em; color: {BAR}; }}
.fen {{ font-family: Inter; font-weight: 600; color: #DCE3EC; line-height: 1.32; direction: ltr; }}
.far {{ direction: rtl; text-align: right; font-family: Plex; font-weight: 700; line-height: 1.78; }}
.far span {{ background: {BAR}; color: {WHITE}; padding: 3px 20px 8px; border-radius: 16px;
            -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
.cols {{ display: flex; gap: 26px; margin-top: 16px; align-items: flex-start; }}
.col {{ flex: 1 1 0; min-width: 0; }}
.vr {{ width: 3px; align-self: stretch; background: #263244; border-radius: 2px; }}
.final {{ position: absolute; left: {MARGIN}px; right: {MARGIN}px; background: {BAR}; border-radius: 30px; padding: 30px 44px 34px; }}
.final .H {{ color: {NIGHT}; }} .final .H .k {{ color: {WHITE}; text-shadow: 0 3px 0 {NIGHT}; }}
.final .AR {{ color: {NIGHT}; }}
.cover {{ position: absolute; left: {MARGIN}px; right: {MARGIN}px; }}
.cover .row {{ display: flex; align-items: flex-start; gap: 26px; }}
.cover .five {{ font-family: InterI; font-style: italic; font-weight: 900; color: {BAR}; line-height: .78; text-shadow: {EXTRUDE}; letter-spacing: -0.04em; }}
.cover .H {{ text-shadow: {EXTRUDE}; }}
.cover .ar {{ margin-top: 30px; text-align: right; direction: rtl; }}
.cover .ar span {{ display: inline; background: {NIGHT}; color: {WHITE}; font-family: Plex; font-weight: 700; padding: 6px 24px 12px;
                  border-radius: 18px; line-height: 1.8; -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
"""


def myth_card(m, s=1.0, cls="card"):
    """One myth on a Night card. s scales all type (the fitter lowers it until the card clears his chin)."""
    return (f'<div class="{cls}" data-s="{s}">'
            f'<div><span class="pill" data-fs="30">MYTH #{m["no"]}</span></div>'
            f'<div class="H" data-fs="76" style="margin-top:22px">{mark(m["q"])}</div>'
            f'<div class="AR" data-fs="44" style="margin-top:18px">{mark(m["ar"])}</div>'
            f'<div class="hr" style="margin:26px 0 22px"></div>'
            f'<div class="lab" data-fs="26">THE SCIENCE</div>'
            f'<div class="fen" data-fs="32" style="margin-top:8px">{m["fact_en"]}</div>'
            f'<div class="far" data-fs="33" style="margin-top:16px"><span>{mark(m["fact_ar"])}</span></div>'
            f'</div>')


def myth_card2(m):
    """Compact two-column myth card (slide 5 carries two myths + the final message): English left, Arabic right."""
    return (f'<div class="card c2" style="position:relative;left:auto;right:auto;margin:0 54px;padding:28px 36px 32px">'
            f'<div><span class="pill" data-fs="26">MYTH #{m["no"]}</span></div>'
            f'<div class="cols">'
            f'<div class="col en"><div class="H" data-fs="46">{mark(m["q"])}</div>'
            f'<div class="lab" data-fs="21" style="margin-top:16px">THE SCIENCE</div>'
            f'<div class="fen" data-fs="26" style="margin-top:4px">{m["fact_en"]}</div></div>'
            f'<div class="vr"></div>'
            f'<div class="col ar"><div class="AR" data-fs="34">{mark(m["ar"])}</div>'
            f'<div class="far" data-fs="27" style="margin-top:14px"><span>{mark(m["fact_ar"])}</span></div></div>'
            f'</div></div>')


def page(i, s, face):
    n = f"{i:02d}"
    chin = face[1] + face[3] * 1.22
    if s["kind"] == "cover":
        body = (f'<div class="cover" id="stack" style="bottom:{MARGIN + 10}px">'
                f'<div class="row"><div class="five" data-fs="330">5</div>'
                f'<div class="H" data-fs="98">{"<br>".join(mark(l) for l in s["en"])}</div></div>'
                f'<div class="ar"><span data-fs="50">{s["ar"]}</span></div></div>')
    elif s["kind"] == "myth":
        body = myth_card(s).replace('class="card"', f'class="card" id="stack" style="bottom:{MARGIN}px"', 1)
    else:
        a, b = s["myths"]
        body = (f'<div id="stack" style="position:absolute;left:0;right:0;bottom:{MARGIN}px">'
                + myth_card2(a)
                + '<div style="height:18px"></div>'
                + myth_card2(b)
                + '<div style="height:18px"></div>'
                + f'<div class="final" style="position:relative"><div class="H" data-fs="58">{mark(s["final_en"])}</div>'
                  f'<div class="AR" data-fs="44" style="margin-top:12px">{s["final_ar"]}</div></div>'
                + '</div>')
        body = body.replace('<div class="final" style="position:relative">', '<div class="final" style="position:relative;left:auto;right:auto;margin:0 54px">')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body><div class="slide">
<img class="bg" src="file://{P}/work/bg_{n}.png">
{body}
<div class="chip logo"><img src="file://{ROOT}/brand/logo/osm-wordmark-780x264.jpg"></div>
<div class="chip num"><b>{n}</b>/{N:02d}</div>
</div><script>
const MIN_TOP = {round(chin + 46)};          // the copy stays below his chin (+46 px)
document.fonts.ready.then(() => {{
  const els = [...document.querySelectorAll('[data-fs]')];
  const stack = document.getElementById('stack');
  let k = 1, it = 0;
  const apply = () => els.forEach(e => e.style.fontSize = (+e.dataset.fs * k) + 'px');
  apply();
  while (stack.getBoundingClientRect().top < MIN_TOP && k > 0.55 && it++ < 100) {{ k -= 0.01; apply(); }}
  // no line may run outside the safe margins
  const over = [...document.querySelectorAll('.H,.AR,.fen,.far,.cover .ar')].some(e => {{ const r = e.getBoundingClientRect(); return r.left < 40 || r.right > 1040; }});
  const r = stack.getBoundingClientRect();
  document.body.dataset.fit = JSON.stringify({{ scale: +k.toFixed(2), top: Math.round(r.top), min_top: MIN_TOP, bottom: Math.round(r.bottom), ok: r.top >= MIN_TOP && !over }});
  document.body.dataset.ready = 1;
}});
</script></body></html>"""


def main():
    info = json.loads((P / "work" / "layout_info.json").read_text())
    out = P / "work" / "html"
    out.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(SLIDES, 1):
        n = f"{i:02d}"
        (out / f"slide_{n}.html").write_text(page(i, s, info[n]["face"]), encoding="utf-8")
    print(f"html: {len(SLIDES)} slides")


if __name__ == "__main__":
    main()
