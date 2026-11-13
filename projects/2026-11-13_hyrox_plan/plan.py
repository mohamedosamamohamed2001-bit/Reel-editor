"""OSM - 8-week HYROX preparation for Coach Osama (race: Friday 8 January 2027). Builds plan.html -> PDF (A4).

Programming basis: his EPI NCSC notes (docs/course_ncsc/study_notes.md): EPI training system (test -> profile -> periodize),
extensive (volume) vs intensive (intensity) themes, CONJUGATE model for trained athletes (several qualities in parallel, wave-like
loading, 3 weeks overload + 1 week de-load), MAS-based HIIT (long intervals 95-100 % MAS, short 15:15 at 110-120 % MAS, MLSS ~90 %
vVO2max), lactate power / capacity and PCr variables, program variables table (hypertrophy / max strength / explosive), contrast
training in Intensive 2. No paces or loads are invented: everything is anchored to his week-1 tests.

    python3 projects/2026-11-13_hyrox_plan/plan.py && node projects/2026-11-13_hyrox_plan/pdf.js
"""
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = ROOT / "brand" / "fonts"

# ---------------------------------------------------------------- content
WEEKS = [
    # (no, dates, phase, theme, focus, days[Mon..Sun])
    (1, "16–22 Nov", "Phase 1 · Foundation", "EXTENSIVE", "Aerobic base · running technique · hypertrophy + correctives · baseline tests",
     ["<b>TEST</b> AM: 1.5 km time trial (→ MAS) · PM (6 h+ later): <b>Gym A</b>, working up to a 5RM in trap-bar deadlift and back squat, then the rest of Gym A",
      "<b>Run · Long intervals</b> 5 × 3 min @ 95 % MAS, 2 min jog · drills 15 min before",
      "<b>Gym B</b> (upper body + posterior chain): work up to a 5RM in bench press and pull-up (weighted if &gt; 10 reps)",
      "<b>HYROX technique</b> at race weight, RPE 6: 4 rounds · SkiErg 250 m · sled push 12.5 m · sled pull 12.5 m · 10 burpee broad jumps · row 250 m · 20 m farmers · 10 lunges · 15 wall balls",
      "<b>Easy run</b> 40 min Z2 + 6 × 15 s strides",
      "<b>Long aerobic</b> 60 min Z2 (run, or 40 min run + 20 min row)",
      "Rest"]),
    (2, "23–29 Nov", "Phase 1 · Foundation", "EXTENSIVE", "Same layout, more volume (EPI progression)",
     ["<b>Gym A</b> (sets 3 → 4) + 20 min Z2 bike",
      "<b>Run · Long intervals</b> 2 × (3 × 3 min @ 95 % MAS), 2 min jog, 4 min between sets",
      "<b>Gym B</b> (sets 3 → 4)",
      "<b>HYROX technique</b> 5 rounds of the week-1 circuit, RPE 6–7",
      "<b>Easy run</b> 45 min Z2 + 6 × 15 s strides",
      "<b>Long aerobic</b> 70 min Z2",
      "Rest"]),
    (3, "30 Nov–6 Dec", "Phase 2 · Threshold + strength", "INTENSIVE", "Running performance · threshold · max strength (hypertrophy kept as assistance)",
     ["<b>Gym A</b> max strength (lower body)",
      "<b>Run · Threshold</b> 4 × 1 km @ 88–90 % MAS, 90 s jog",
      "<b>Gym B</b> max strength (upper body) + hypertrophy assistance",
      "<b>Run · Short intervals</b> 2 × 5 min of 15 s on / 15 s off @ 110 % MAS, 3 min between · then 4 × 25 m sled push at race weight",
      "<b>Easy run</b> 45 min Z2 + strides",
      "<b>Long run</b> 75 min Z2, last 10 min @ 88 % MAS",
      "Rest"]),
    (4, "7–13 Dec", "Phase 2 · Threshold + strength", "DE-LOAD", "EPI de-load: volume −30–40 %, intensity kept · retest",
     ["<b>Gym A</b> same loads as week 3, one set fewer per exercise",
      "<b>Run · Threshold</b> 3 × 1 km @ 88–90 % MAS, 90 s jog",
      "<b>Gym B</b> same loads, one set fewer",
      "<b>RETEST</b> 1.5 km time trial → update MAS and every pace from here on",
      "<b>Easy run</b> 35 min Z2 + strides",
      "<b>Long run</b> 60 min Z2",
      "Rest"]),
    (5, "14–20 Dec", "Phase 3 · HYROX-specific", "INTENSIVE", "Compromised running · lactate capacity · strength-speed (contrast) · power",
     ["<b>Gym A</b> strength-speed + power (contrast)",
      "<b>Compromised run</b> 4 × [1 km @ race pace → station] , 2 min between rounds · stations in order: SkiErg 500 m · sled push 2 × 12.5 m · row 500 m · 30 wall balls",
      "<b>Gym B</b> upper-body strength + hypertrophy · 20 min easy bike",
      "<b>Run · Short intervals</b> 3 × 5 min of 15:15 @ 110–115 % MAS, 3 min between",
      "<b>Easy run</b> 40 min Z2 + strides · mobility",
      "<b>HALF SIMULATION</b> runs 5–8 + stations 5–8 (row, farmers carry, sandbag lunges, wall balls) at race weight and race effort",
      "Rest"]),
    (6, "21–27 Dec", "Phase 3 · HYROX-specific", "INTENSIVE", "Peak specific load · full simulation 13 days out",
     ["<b>Gym A</b> strength-speed + power (contrast)",
      "<b>Compromised run</b> 5 × [1 km @ race pace → station] , 90 s between · stations: sled pull 2 × 12.5 m · 20 burpee broad jumps · 50 m farmers · 25 m lunges · 30 wall balls",
      "<b>Gym B</b> upper-body strength + hypertrophy",
      "<b>Run · Threshold</b> 5 × 1 km @ 90 % MAS, 60 s jog",
      "<b>Easy run</b> 35 min Z2 + strides",
      "<b>FULL SIMULATION</b> (26 Dec) · 8 × 1 km + all 8 stations at race weight · practise pacing, transitions, fuelling, kit",
      "Rest"]),
    (7, "28 Dec–3 Jan", "Phase 4 · Competition-specific", "SHARPEN", "Race-specific quality, volume −30 %, no new stress",
     ["<b>Gym</b> maintenance (full body, heavy, low volume)",
      "<b>Race-pace rehearsal</b> 4 × [1 km @ race pace → half-volume station + Roxzone transition], 2 min between",
      "<b>Easy run</b> 35 min Z2 · mobility",
      "<b>Sharpening</b> 6 × 400 m @ ~95 % MAS, 90 s jog · then 3 × 20 unbroken wall balls",
      "Rest",
      "<b>Station rehearsal</b> race weight, low volume: sled push 25 m · sled pull 25 m · 20 m burpee broad jumps · 25 m lunges · 30 wall balls · 20 min easy run",
      "Rest or 30 min easy"]),
    (8, "4–8 Jan", "Phase 5 · Taper + race", "TAPER", "Freshness: volume −50–60 %, keep a little intensity · RACE FRIDAY 8 JAN",
     ["<b>Gym</b> short primer: trap-bar DL 2 × 3 @ 75 %, 2 × 3 box jumps, push-ups 2 × 10 · 20 min easy run",
      "<b>Openers</b> 15 min easy + 2 × 1 km @ race pace (2 min jog) + 4 × 20 s strides",
      "Rest · 20 min mobility · check race kit and start time",
      "<b>Activation</b> 15 min easy + 3 × 20 s strides + 30 s SkiErg + 10 wall balls · higher-carb meals · early night",
      "<b>RACE DAY</b> · warm up 25–30 min before your wave (RAMP: raise, activate, mobilize, potentiate)",
      "Recovery walk + easy mobility",
      "Rest"]),
]

GYM = [
    ("Phase 1 · Weeks 1–2 · HYPERTROPHY + CORRECTIVES (extensive)",
     "EPI hypertrophy variables: 3–4 sets · 6–12 reps · 70–85 % 1RM · 60 s–2 min rest. Stop 2–3 reps short of failure (RIR 2–3).",
     [("Gym A · lower-body emphasis", [
         ("Back squat", "3×8 @ 70–75 % (week 2: 4×8)", "2 min"),
         ("DB Romanian deadlift", "3×10", "90 s"),
         ("DB walking lunge", "3×10 / leg", "90 s"),
         ("Hip thrust", "3×10", "90 s"),
         ("Seated cable row", "3×10", "60 s"),
         ("DB shoulder press", "3×10", "60 s"),
         ("Correctives (your MCS)", "90/90 hip IR 2×8/side · couch stretch 2×45 s/side · SL glute bridge 2×12", "—"),
         ("Core", "Copenhagen side plank 3×20 s/side", "45 s")]),
      ("Gym B · upper-body emphasis", [
         ("Bench press", "3×8 @ 70–75 % (week 2: 4×8)", "2 min"),
         ("Pull-up", "4×6–10", "90 s"),
         ("Incline DB press", "3×10", "90 s"),
         ("Chest-supported row", "3×10", "90 s"),
         ("Lateral raise", "3×12–15", "60 s"),
         ("Biceps curl + triceps pushdown", "3×12 superset", "60 s"),
         ("Nordic curl (eccentric)", "3×5", "90 s"),
         ("Soleus / calf raise", "3×15", "60 s"),
         ("Core", "Pallof press 3×10/side", "45 s")])]),
    ("Phase 2 · Weeks 3–4 · MAX STRENGTH (intensive) + hypertrophy assistance",
     "EPI max strength: 3–5 sets · 1–5 reps · 85 %+ · 3 min rest. Two main lifts per quality; the rest is assistance (keeps muscle). Week 4: same loads, one set fewer.",
     [("Gym A · lower body", [
         ("Trap-bar deadlift", "4×5 @ 80–85 % (wk 4: 3×5)", "3 min"),
         ("Front squat", "3×5 @ 75–80 %", "3 min"),
         ("Bulgarian split squat", "3×8 / leg", "90 s"),
         ("Nordic curl", "3×5", "90 s"),
         ("Weighted pull-up", "3×6", "2 min"),
         ("Core", "Hanging leg raise 3×10", "60 s")]),
      ("Gym B · upper body", [
         ("Bench press", "4×5 @ 80–85 % (wk 4: 3×5)", "3 min"),
         ("Weighted pull-up", "4×5", "3 min"),
         ("DB shoulder press", "3×8", "90 s"),
         ("Lat pulldown or row", "3×10", "60 s"),
         ("Lateral raise", "3×15", "60 s"),
         ("Arms superset", "2×12", "60 s"),
         ("Heavy soleus raise", "3×12", "60 s")])]),
    ("Phase 3 · Weeks 5–6 · STRENGTH-SPEED + POWER (contrast) · upper-body hypertrophy kept",
     "EPI Intensive 2 / contrast: heavy set, then an explosive movement of the same pattern. PCr power: efforts of 6–8 s, rest 5–10× the work.",
     [("Gym A · lower body + power", [
         ("Trap-bar deadlift → CMJ", "4 × (3 @ 85 % → 4 jumps)", "2–3 min"),
         ("Heavy sled sprint (push)", "4 × 10 m, max intent", "90 s"),
         ("Bulgarian split squat", "3×6 / leg, heavy", "2 min"),
         ("Single-leg RDL", "3×8 / leg", "90 s"),
         ("Core", "Pallof press 3×10/side", "45 s")]),
      ("Gym B · upper body", [
         ("Push press → MB chest throw", "4 × (3 @ 75–80 % → 4 throws)", "2–3 min"),
         ("Bench press", "3×5 @ 80 %", "2–3 min"),
         ("Weighted pull-up", "3×5", "2–3 min"),
         ("Row", "3×10", "60 s"),
         ("Lateral raise", "3×15", "60 s"),
         ("Arms superset", "2×12", "60 s")])]),
    ("Phase 4–5 · Weeks 7–8 · MAINTENANCE → PRIMER",
     "Keep the intensity, cut the volume: this keeps strength and muscle while fatigue drops for race day. Nothing to failure.",
     [("Week 7 · full body (1 session)", [
         ("Trap-bar deadlift", "3×3 @ 80 %", "2–3 min"),
         ("Bench press", "3×4 @ 80 %", "2–3 min"),
         ("Pull-up", "3×6", "2 min"),
         ("Box jump", "3×3", "90 s"),
         ("Row + arms", "2×10 each", "60 s")]),
      ("Week 8 · Monday primer", [
         ("Trap-bar deadlift", "2×3 @ 75 %", "2 min"),
         ("Box jump", "2×3", "90 s"),
         ("Push-up", "2×10", "60 s")])]),
]

STATIONS = [("SkiErg", "1,000 m", "—"), ("Sled push", "50 m", "152 kg incl. sled / Pro 202 kg"), ("Sled pull", "50 m", "103 kg incl. sled / Pro 153 kg"),
            ("Burpee broad jumps", "80 m", "—"), ("Row", "1,000 m", "—"), ("Farmers carry", "200 m", "2 × 24 kg / Pro 2 × 32 kg"),
            ("Sandbag lunges", "100 m", "20 kg / Pro 30 kg"), ("Wall balls", "100 reps", "6 kg to 3 m / Pro 9 kg to 3 m")]


def li(xs):
    return "".join(f"<li>{x}</li>" for x in xs)


def build():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    theme_col = {"EXTENSIVE": "#F4C542", "INTENSIVE": "#56A0FB", "DE-LOAD": "#9AA6B6", "SHARPEN": "#7DD2EC", "TAPER": "#FFFFFF"}
    week_html = ""
    for no, dates, phase, theme, focus, dd in WEEKS:
        rows = "".join(f'<tr><td class="d">{days[i]}</td><td>{x}</td></tr>' for i, x in enumerate(dd))
        week_html += (f'<section class="wk"><div class="wkh"><div class="no">WEEK {no}</div><div class="dt">{dates}</div>'
                      f'<div class="ph">{phase}</div><div class="th" style="background:{theme_col[theme]}">{theme}</div></div>'
                      f'<div class="fo">{focus}</div><table class="days">{rows}</table></section>')
    gym_html = ""
    for title, note, sessions in GYM:
        blocks = ""
        for sname, ex in sessions:
            rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td class='r'>{c}</td></tr>" for a, b, c in ex)
            blocks += f'<div class="gs"><div class="gsh">{sname}</div><table class="ex"><tr><th>Exercise</th><th>Sets × reps · load</th><th class="r">Rest</th></tr>{rows}</table></div>'
        gym_html += f'<section class="gp"><h3>{title}</h3><p class="note">{note}</p>{blocks}</section>'
    st = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in STATIONS)
    pace_rows = ""
    for mas in (4.0, 4.25, 4.5, 4.75, 5.0):
        t15 = 1500 / mas
        def pace(p):
            s = 1000 / (mas * p); return f"{int(s // 60)}:{int(round(s % 60)):02d}"
        pace_rows += (f"<tr><td>{int(t15 // 60)}:{int(round(t15 % 60)):02d}</td><td>{mas:.2f} m/s · {mas * 3.6:.1f} km/h</td>"
                      f"<td>{pace(0.70)}</td><td>{pace(0.88)}–{pace(0.90)}</td><td>{pace(0.95)}</td><td>{pace(1.10)}</td></tr>")
    html = (P / "template.html").read_text(encoding="utf-8")
    html = (html.replace("{{F}}", str(F)).replace("{{ROOT}}", str(ROOT)).replace("{{WEEKS}}", week_html)
            .replace("{{GYM}}", gym_html).replace("{{STATIONS}}", st).replace("{{PACES}}", pace_rows))
    (P / "plan.html").write_text(html, encoding="utf-8")
    print("plan.html written")


if __name__ == "__main__":
    build()
