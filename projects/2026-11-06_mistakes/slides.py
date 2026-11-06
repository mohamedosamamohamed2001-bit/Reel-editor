"""OSM carousel: Common Gym Mistakes (Coach Osama 2026-11-06). 8 slides, 1080x1350, his 8 original photos (sRGB conversion via
each photo's ICC profile, 4:5 crop, no colour change, nothing generated).

The OSM carousel system (projects/2026-10-20_carousel, 2026-10-30_lifestyle): logo + NN/08 chips on Night, English title in
Inter Black Italic CAPS, Arabic in IBM Plex Sans Arabic Bold, hard Night 3D extrusion (no soft shadow / glow / blur), body on the
locked #56A0FB bars with white text, OSM TIP on a solid Night plate. English training terms: Core Blue in headlines and tips,
Night on the blue bars (text on Core Blue = Night). Text never on, above or behind his head: every headline line is fitted to the
free width measured ROW BY ROW from his MODNet silhouette (dilated), so nothing touches him.

    .venv/bin/python projects/2026-11-06_mistakes/slides.py && node projects/2026-11-06_mistakes/render.js
"""
import json, re
from pathlib import Path
import numpy as np
import cv2

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = ROOT / "brand" / "fonts"
BAR, NIGHT, WHITE = "#56A0FB", "#0A0F16", "#FFFFFF"
EXTRUDE = f"0 3px 0 {NIGHT}, 0 6px 0 {NIGHT}, 0 9px 0 rgba(10,15,22,.85)"
N = 8
MARGIN, GAP = 54, 44

# Copy = the brief's wording. [[term]] = English training term (highlighted). {{...}} = one left-to-right run inside Arabic.
SLIDES = [
    dict(side="right", title=["EGO", "LIFTING"], q=["بتشيل وزن", "أكبر من", "قدرتك؟"],
         bars=["استخدام وزن تقيل على حساب الـ [[Form]]", "مش معناه إنك بتتمرن أقوى."],
         tip=["Focus on [[technique]]", "before increasing the weight."]),
    dict(side="right", title=["NO TRAINING", "PROGRESSION"], title_at="bottom", q=["بتتمرن بنفس", "الأوزان ونفس", "العدات كل مرة؟"],
         bars=["جسمك محتاج [[Stimulus]] جديد عشان يتطور."],
         tip=["{{Apply [[Progressive Overload]]}}", "تدريجياً وبشكل محسوب."], tip_rtl=True),
    dict(side="right", title=["RUSHING", "REPS"], q=["بتخلص العدات", "بسرعة لمجرد", "إنك تخلص؟"],
         bars=["التحكم في الحركة مهم،", "خصوصاً أثناء الـ [[Eccentric Phase]]."],
         tip=["[[Control the movement.]]", "Don’t just move the weight."]),
    dict(side="right", title=["IGNORING", "RECOVERY"], q=["فاكر إن كل", "ما تتمرن أكتر", "النتيجة", "هتبقى أسرع؟"], q_plate=True,
         bars=["[[Overtraining]] without enough recovery", "can affect your performance."], bars_ltr=True,
         tip=["Train smart. [[Recover better.]]", "Progress consistently."]),
    dict(side="right", title=["TRAINING", "WITHOUT", "ENOUGH", "VOLUME"], q=["بتتمرن العضلة", "بمجموعات", "قليلة جداً؟"],
         bars=["مش مجرد إنك تتمرن العضلة معناه", "إنك بتديها [[Stimulus]] كافي للنمو."],
         tip=["Adjust your [[weekly training volume]] based on", "your goals, recovery, and training level."]),
    dict(side="left", title=["POOR REST", "PERIODS"], title_at="bottom", q=["بتستعجل تبدأ", "الـ [[Next Set]]؟"], q_plate=True,
         bars=["الراحة القصيرة مش دايماً أفضل."],
         tip=["[[Rest enough]] to maintain performance", "and exercise quality."]),
    dict(side="right", title=["NO", "TRAINING", "PLAN"], q=["بتروح الجيم", "وتختار التمارين", "عشوائي؟"],
         bars=["التدريب من غير خطة واضحة", "بيصعّب عليك متابعة تطورك."],
         tip=["Have a [[structured program]]", "and track your progress."]),
    dict(side="cta", title=["WHICH MISTAKE", "ARE [[YOU]] MAKING? 👀"], q=[],
         bars=["كلنا بنقع في أخطاء،", "المهم إننا نتعلم ونطور من نفسنا."],
         tip=["Save this post & share it", "with your [[gym partner]]!"]),
]


def free_profile(n, side):
    """Free width per row (px) on `side`, keeping GAP px from his silhouette (largest matte component) and MARGIN from the edge."""
    m = cv2.imread(str(P / "work" / f"person_{n}.png"), cv2.IMREAD_UNCHANGED)[:, :, 3] > 128
    _, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    m = cv2.dilate((lab == big).astype(np.uint8), np.ones((GAP * 2 + 1, GAP * 2 + 1), np.uint8)) > 0
    top = int(np.where(m.any(axis=1))[0].min())             # the top of his head: nothing may sit in the column above it
    out = []
    for y in range(1350):
        r = m[y]
        if side == "right":
            edge = int(np.where(r)[0].max()) if r.any() else 0
            out.append(max(0, 1080 - MARGIN - edge))
        else:
            edge = int(np.where(r)[0].min()) if r.any() else 1080
            out.append(max(0, edge - MARGIN))
    return out, top


def mark(s, cls):
    s = re.sub(r"\{\{(.+?)\}\}", lambda m: f'<bdi dir="ltr" class="run">{m.group(1)}</bdi>', s)
    return re.sub(r"\[\[(.+?)\]\]", lambda m: f'<span class="{cls}" dir="ltr">{m.group(1)}</span>', s)


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
.fit {{ position: absolute; white-space: nowrap; }}
.fit.r {{ right: {MARGIN}px; text-align: right; }} .fit.l {{ left: {MARGIN}px; text-align: left; }}
.title {{ font-family: InterI; font-style: italic; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em; color: {WHITE};
         line-height: 0.98; text-shadow: {EXTRUDE}; direction: ltr; }}
.title .l, .q .l {{ display: block; }}
.q {{ font-family: Plex; font-weight: 700; color: {WHITE}; direction: rtl; line-height: 1.36; text-shadow: {EXTRUDE}; }}
.k {{ color: {BAR}; font-family: Inter; font-weight: 800; }}
.q.plate {{ text-shadow: none; line-height: 1.78; }}
.q.plate .l {{ display: inline; background: {NIGHT}; padding: 4px 22px 10px; border-radius: 18px; white-space: nowrap;
                -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
.title .k {{ font-family: InterI; font-weight: 900; }}
.rule {{ position: absolute; width: 84px; height: 9px; border-radius: 5px; background: {BAR}; }}
.bot {{ position: absolute; left: {MARGIN}px; right: {MARGIN}px; bottom: 54px; }}
.bot .title {{ margin-bottom: 26px; }}
.bars {{ direction: rtl; font-family: Plex; font-weight: 700; font-size: 37px; line-height: 1.74; }}
.bars span.b {{ white-space: nowrap; background: {BAR}; color: {WHITE}; padding: 4px 22px 9px; border-radius: 18px;
               -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
.bars.ltr {{ direction: ltr; font-family: Inter; font-weight: 700; font-size: 35px; line-height: 1.8; }}
.bars.ltr span.b {{ padding: 5px 22px 9px; }}
.bars .t {{ color: {NIGHT}; font-family: Inter; font-weight: 800; }}
.tip {{ display: inline-block; margin-top: 20px; background: {NIGHT}; border-radius: 18px; padding: 16px 26px 18px;
       font-family: Inter; font-weight: 700; font-size: 33px; line-height: 1.38; color: {WHITE}; direction: ltr; white-space: nowrap; }}
.tip.rtl {{ direction: rtl; font-family: Plex; }}
.tip .run {{ font-family: Inter; }}
.tip .k {{ font-weight: 800; }}
.tip .lab {{ display: block; font-family: Barlow; font-weight: 700; font-size: 25px; letter-spacing: .2em; color: {BAR}; margin-bottom: 4px; }}
.tip.rtl .lab {{ direction: ltr; text-align: right; }}
.chip {{ position: absolute; top: 46px; height: 60px; background: {NIGHT}; border-radius: 16px; display: flex; align-items: center; }}
.logo {{ left: 46px; padding: 0 18px; }}
.logo img {{ height: 40px; display: block; mix-blend-mode: lighten; }}
.num {{ right: 46px; padding: 0 18px; font-family: Barlow; font-weight: 600; font-size: 34px; color: {WHITE}; letter-spacing: 1px; }}
.num b {{ color: {BAR}; font-weight: 700; }}
.emo {{ font-family: 'Noto Color Emoji'; font-style: normal; text-shadow: none; }}
.cta {{ text-align: center; }}
.cta .title {{ font-size: 90px; }}
.cta .bars {{ text-align: center; }}
.sign {{ display: flex; align-items: center; justify-content: center; gap: 14px; margin-top: 24px; }}
.sign .ico {{ margin-right: 8px; }}
.sign .w {{ font-family: InterI; font-style: italic; font-weight: 900; font-size: 36px; text-transform: uppercase; letter-spacing: -0.01em;
           color: {WHITE}; text-shadow: {EXTRUDE}; }}
.sign .w.k {{ font-family: InterI; font-weight: 900; color: #56A0FB; }}
.ico {{ display: flex; gap: 12px; }}
.ico div {{ width: 66px; height: 66px; border-radius: 18px; background: {BAR}; display: flex; align-items: center; justify-content: center; }}
"""


ICONS = {  # lucide (ISC): bookmark + send, Night strokes on Core Blue
    "save": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#0A0F16" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>',
    "share": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#0A0F16" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>',
}


def lines(ls, cls):
    return "".join(f'<span class="l">{mark(l, cls).replace("👀", "<span class=emo>👀</span>")}</span>' for l in ls)


def html(i, s, prof, head_top, face):
    n = f"{i:02d}"
    side = "r" if s["side"] == "right" else "l"
    bars = "<br>".join(f'<span class="b">{mark(l, "t")}</span>' for l in s["bars"])
    tip = "<br>".join(mark(l, "k") for l in s["tip"])
    tipc = "tip rtl" if s.get("tip_rtl") else "tip"
    bal = "right" if side == "r" else "left"
    if s["side"] == "cta":
        body = (f'<div class="bot cta"><div class="title">{lines(s["title"], "k")}</div>'
                f'<div class="bars">{bars}</div><div><div class="{tipc}" style="text-align:center">{tip}</div></div>'
                f'<div class="sign"><div class="ico"><div>{ICONS["save"]}</div><div>{ICONS["share"]}</div></div>'
                f'<span class="w">OSM –</span><span class="w k">Train Smart.</span><span class="w">Progress Better.</span></div></div>')
        top = ""
    else:
        t_html = f'<div class="title" style="font-size:118px">{lines(s["title"], "k")}</div>'
        top = ((f'<div class="fit {side} t" data-max="118" data-min="60">{t_html}</div>' if s.get("title_at") != "bottom" else "")
               + ('<div class="rule"></div>' if s.get("title_at") != "bottom" else "")
               + (f'<div class="fit {side} q" data-max="52" data-min="36"><div class="q plate" style="font-size:52px">{"<br>".join(f'<span class="l">{mark(l, "k")}</span>' for l in s["q"])}</div></div>' if s.get("q_plate")
                  else f'<div class="fit {side} q" data-max="72" data-min="44"><div class="q" style="font-size:72px">{lines(s["q"], "k")}</div></div>'))
        body = (f'<div class="bot" style="text-align:{bal}">'
                + (f'<div class="title bt" style="font-size:96px">{lines(s["title"], "k")}</div>' if s.get("title_at") == "bottom" else "")
                + f'<div class="bars{" ltr" if s.get("bars_ltr") else ""}" style="text-align:{bal}">{bars}</div>'
                f'<div class="{tipc}" style="text-align:{"right" if s.get("tip_rtl") else "left"}"><span class="lab">OSM TIP</span>{tip}</div></div>')
    y0 = max(140, face[1] - 10) if s.get("title_at") != "bottom" else max(300, face[1] + face[3] + 60)          # first headline row: level with his face at most (never in the column above his head)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body><div class="slide">
<img class="layer" src="file://{P}/work/bg_{n}.png">
{top}{body}
<div class="chip logo"><img src="file://{ROOT}/brand/logo/osm-wordmark-780x264.jpg"></div>
<div class="chip num"><b>{n}</b>/{N:02d}</div>
</div><script>
const FREE = {json.dumps(prof)}, Y0 = {y0}, SIDE = "{side}";
document.fonts.ready.then(() => {{
  const wid = (el) => Math.max(0, ...[...el.querySelectorAll('.l')].map(l => {{ const r = document.createRange(); r.selectNodeContents(l); return r.getBoundingClientRect().width; }}));
  const freeAt = (a, b) => Math.min(...FREE.slice(Math.max(0, Math.floor(a)), Math.ceil(b)));
  const bot = document.querySelector('.bot');
  // bottom title: fit the full width
  const bt = document.querySelector('.bot .title.bt');
  if (bt) {{ let f = 96; while (wid(bt) > 972 && f > 50) {{ f -= 2; bt.style.fontSize = f + 'px'; }} }}
  const limit = bot.getBoundingClientRect().top - 40;
  let y = Y0; const rep = {{}};
  for (const box of document.querySelectorAll('.fit')) {{
    const inner = box.firstElementChild; let f = +box.dataset.max; const fmin = +box.dataset.min;
    box.style.top = y + 'px';
    const pad = inner.classList.contains('plate') ? 46 : 0;
    const ok = () => {{ const r = box.getBoundingClientRect(); return wid(inner) + pad <= freeAt(r.top, r.bottom) && r.bottom <= limit; }};
    let it = 0; while (!ok() && f > fmin && it++ < 200) {{ f -= 1; inner.style.fontSize = f + 'px'; }}
    const r = box.getBoundingClientRect();
    rep[box.classList.contains('t') ? 'title' : 'q'] = {{ size: f, w: Math.round(wid(inner)), free: freeAt(r.top, r.bottom), top: Math.round(r.top), bottom: Math.round(r.bottom), ok: ok() }};
    if (box.classList.contains('t')) {{             // accent rule under the title, then the question
      const rule = document.querySelector('.rule'); rule.style.top = (r.bottom + 22) + 'px';
      rule.style[SIDE === 'r' ? 'right' : 'left'] = '{MARGIN}px'; y = r.bottom + 22 + 9 + 30;
    }}
  }}
  rep.bottom_top = Math.round(bot.getBoundingClientRect().top);
  document.body.dataset.fit = JSON.stringify(rep);
  document.body.dataset.ready = 1;
}});
</script></body></html>"""


def main():
    info = json.loads((P / "work" / "layout_info.json").read_text())
    out = P / "work" / "html"
    out.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(SLIDES, 1):
        n = f"{i:02d}"
        prof, head_top = free_profile(n, "right" if s["side"] != "left" else "left")
        (out / f"slide_{n}.html").write_text(html(i, s, prof, head_top, info[n]["face"]), encoding="utf-8")
    print("html: 8 slides")


if __name__ == "__main__":
    main()
