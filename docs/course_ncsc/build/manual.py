"""OSM – Complete Client Assessment Manual (PDF + editable DOCX source)."""
from common import *
from tests import TESTS, CATS, CMS_LIST, CMS_MAP, COURSE_MAP
from phase1 import SKIN, VBT

BY_ID = {t["id"]: t for t in TESTS}
B = "&nbsp;"


def refs_html(t):
    return "<br>".join(f"{esc(v)} {src(s)}" for v, s in t["refs"]) if t["refs"] else f'<span class="ns">{NS}</span>'


def v(x):
    if x == NS or (isinstance(x, str) and x.startswith(NS)):
        return f'<span class="ns">{esc(x)}</span>'
    return esc(x)


def card(t):
    proto = "<ol style='margin:0;padding-left:4.5mm'>" + "".join(f"<li>{v(p)}</li>" for p in t["protocol"]) + "</ol>"
    rows = [("1 Assessment name", esc(t["name"])), ("2 Category", esc(t["cat"])), ("3 Purpose", v(t["purpose"])), ("4 Physical quality", v(t["quality"])),
            ("5 Required equipment", v(t["equip"])), ("6 Starting position", v(t["start"])), ("7 Testing protocol", proto),
            ("8 Instructions to the client", v(t["instruct"])), ("9 Number of trials", v(t["trials"])), ("10 Rest period", v(t["rest"])),
            ("11 What to measure", v(t["measure"]) + (" — <b>left and right</b>" if t["sides"] else "")), ("12 Scoring method", v(t["scoring"])),
            ("13 Reference values / norms", refs_html(t)), ("14 Interpretation", v(t["interp"])), ("15 Common mistakes", v(t["mistakes"])),
            ("16 Coaching considerations", v(t["coach"]))]
    merged = f'<tr><td class="f">Duplicate merge</td><td>{esc(t["merged"])}</td></tr>' if t["merged"] else ""
    srcs = " · ".join(t["sources"])
    body = "".join(f'<tr><td class="f">{a}</td><td>{b}</td></tr>' for a, b in rows)
    return (f'<div class="card"><div class="hd"><b>{esc(t["id"])} · {esc(t["name"])}</b><span>{esc(srcs)}</span></div>'
            f'<table><colgroup><col style="width:27%"><col style="width:73%"></colgroup><tbody>{merged}{body}</tbody></table></div>')


def short_ref(t):
    return "; ".join(f"{v_} [{s}]" for v_, s in t["refs"])[:260] if t["refs"] else NS


def sheet_head(title, extra=""):
    return (f'<div class="avoid"><h2>{esc(title)}</h2>' + table(["Client", "Assessment date", "Coach", "Session"], [[B, B, B, "Initial / Re 1 / Re 2 / Re 3"]], cls="form rec", raw=True)
            + extra + "</div>")


def rec_table(headers, rows, widths):
    return table(headers, rows, cls="rec", raw=True, widths=widths)


def build_record_sheets():
    out = ['<section class="chapter"><div class="eyebrow">Section 3</div><h1>Client assessment record sheets</h1><div class="bar"></div>',
           "<p>Fill in during the session. Reference = course/CMS value with source (full detail on each test card in Section 2). "
           "Classification: use the course system where one exists (written on the sheet); otherwise the coach's own judgement. Never record a diagnosis.</p>"]
    # anthropometry
    out.append(sheet_head("3.1 Anthropometry & body composition"))
    out.append(rec_table(["Measure", "Trial 1", "Trial 2", "Trial 3", "Final (avg / best)", "Notes"],
                         [["Height (cm)", B, B, B, B, B], ["Body mass (kg)", B, B, B, B, B]], ["24%", "13%", "13%", "13%", "15%", "22%"]))
    out.append(rec_table(["Skinfold site (mm)", "Reading 1", "Reading 2", "Reading 3", "Average", "Within 10%?"],
                         [[s, B, B, B, B, "Y / N"] for s in ["Biceps (vertical)", "Triceps (vertical)", "Subscapular (diagonal)", "Suprailiac (diagonal)"]] +
                         [["<b>Sum of 4 (mm)</b>", B, B, B, B, "→ Body fat % (Table A1): ______"]], ["24%", "13%", "13%", "13%", "15%", "22%"]))
    # OHS
    out.append('<div class="avoid">' + sheet_head("3.2 Movement quality – squat screen (MCS overhead squat + CMS squat)"))
    ohs = [["Front", "1 Feet turn out", "L □  R □"], ["Front", "2 Knees buckle in", "L □  R □"], ["Side", "3 Heels off floor", "□"], ["Side", "4 Tibial angle &lt; 15°", "□"],
           ["Side", "5 Knee-dominant squat", "□"], ["Side", "6 Lumbar spine rounds", "□"], ["Side", "7 Excessive forward lean", "□"], ["Side", "8 Arms fall forward", "□"],
           ["Side", "9 Squat depth &lt; 90°", "□"], ["Rear", "10 Hip weight shift", "L □  R □"]]
    out.append(rec_table(["View", "MCS checkpoint [P1 p.39]", "Seen (1 pt each)", "Notes"], [r + [B] for r in ohs] +
                         [["", "<b>OHS score /12</b>", B, "Good 0–2 · Average 3–5 · Poor 6–12 [P1 p.39]"]], ["12%", "40%", "18%", "30%"]))
    out.append(rec_table(["CMS squat observation [CMS]", "Seen", "Side / notes"], [[o, "Y / N", B] for o in ["Feet turnout", "Foot arch collapse", "Knee cave-in",
                         "Asymmetrical weight shift", "APT (anterior pelvic tilt)", "Butt wink", "Excessive torso lean"]], ["45%", "15%", "40%"]))
    out.append(rec_table(["Test", "Reference", "Finding", "Pain / location", "Classification", "Notes"],
                         [["<b>Toe touch</b><br><span class='small'>Observe: hip flexion, lumbar flexion, posterior weight shift, T-spine flexion</span>", "Touch the ground [CMS]", B, B, B, B]],
                         ["26%", "14%", "16%", "14%", "13%", "17%"]) + "</div>")

    def rom_sheet(title, ids):
        rows = []
        for i in ids:
            t = BY_ID[i]
            ref = "<br>".join(f"{esc(a)} [{esc(s if s != 'CMS Assessment Sheet' else 'CMS')}]" for a, s in t["refs"] if not a.startswith("Case study"))
            if t["sheet"] == "rom2":
                for m in t["protocol"]:
                    lab = m.split(":")[0]
                    rows.append([f"<b>{esc(t['name'])}</b><br><span class='small'>{esc(lab)}</span>", ref if m == t["protocol"][0] else "″", B, B, B, B, B])
            elif t["sheet"] == "neck":
                rows.append([f"<b>{esc(t['name'])}</b> – flexion", esc(t["refs"][0][0]) + " [CMS]", B, "—", B, B, B])
                rows.append([f"<b>{esc(t['name'])}</b> – extension", esc(t["refs"][1][0]) + " [CMS]", B, "—", B, B, B])
            elif t["sides"]:
                rows.append([f"<b>{esc(t['name'])}</b> <span class='small'>({esc(t['unit'])})</span>", ref, B, B, B, B, B])
            else:
                rows.append([f"<b>{esc(t['name'])}</b>", ref, B, "—", B, B, B])
        return sheet_head(title) + rec_table(["Test", "Reference / normal range", "Left / finding", "Right", "Pain / location", "Classification", "Notes"], rows,
                                             ["22%", "22%", "10%", "10%", "12%", "11%", "13%"])

    out.append(rom_sheet("3.3 Lower-body mobility & range of motion", ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11", "L12"]))
    out.append(rom_sheet("3.4 Trunk & spine", ["S1", "S2", "S3", "S4", "S5", "S6"]))
    out.append(rec_table(["Test", "Reference", "Trial 1", "Trial 2", "Best", "Classification", "Notes"],
                         [["<b>Trunk extensor endurance test</b> [P2 p.32]", NS, B, B, B, B, B]], ["24%", "18%", "10%", "10%", "10%", "12%", "16%"]))
    out.append(rom_sheet("3.5 Upper-body mobility & range of motion", ["U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8"]))

    def perf_rows(ids):
        rows = []
        for i in ids:
            t = BY_ID[i]
            ref = "<br>".join(f"{esc(a)} [{esc(s)}]" for a, s in t["refs"])
            if t["sheet"] == "perfLR":
                for side in ("Left", "Right"):
                    rows.append([f"<b>{esc(t['name'])}</b> – {side} ({esc(t['unit'])})", ref if side == "Left" else "″", B, B, B, B, B])
            else:
                rows.append([f"<b>{esc(t['name'])}</b> ({esc(t['unit'])})", ref, B, B, B, B, B])
        return rows

    W7 = ["24%", "27%", "8%", "8%", "8%", "10%", "15%"]
    out.append(sheet_head("3.6 Strength") + rec_table(["Test", "Reference", "Trial / att. 1", "Att. 2", "Att. 3", "Best", "Classification / notes"],
                                                    perf_rows(["ST1", "ST3", "ST4", "ST5"]), W7))
    out.append(rec_table(["Est. 1RM (VBT) back squat [P1 p.33]", "Load (kg)", "Rep 1 (m/s)", "Rep 2 (m/s)", "Rep 3 (m/s)", "Mean (m/s)", "Est. %1RM (Table A2)"],
                         [[f"~{p}% est. 1RM", B, B, B, B, B, B] for p in (40, 60, 80)] + [["<b>Estimated 1RM (kg)</b>", B, B, B, B, B, B]],
                         ["24%", "12%", "12%", "12%", "12%", "12%", "16%"]))
    out.append(rec_table(["Relative strength", "Value", "Course guideline"], [["Back squat 1RM ÷ BW", B, "1.5 × BW standard for complex/contrast training [P2 p.34]"],
                         ["Bench 1RM ÷ BW", B, "1.2 × BW standard for complex/contrast training [P2 p.34]"]], ["35%", "20%", "45%"]))
    out.append(sheet_head("3.7 Power & reactive strength") + rec_table(["Test", "Reference", "Trial 1", "Trial 2", "Trial 3", "Best", "Classification / notes"],
                                                                     perf_rows(["P1", "P2", "P3", "P4", "P5", "P6"]), W7))
    out.append(rec_table(["RSI profile – drop height", "Trial", "Jump height", "GCT (s)", "RSI", "GCT &lt; 0.25 s?", "Notes"],
                         [[f"{h} cm", "1 / 2 / 3", B, B, B, "Y / N", B] for h in (15, 30, 45, 60)] + [["<b>Best RSI / band</b>", B, B, B, B, B, "&lt;1.5 Low · 1.5–2.0 Mod · 2.0–2.5 Good · 2.5–3.0 Exc · &gt;3.0 WC [P2 p.101]"]],
                         ["20%", "10%", "13%", "11%", "10%", "12%", "24%"]))
    out.append(rec_table(["DSI [P2 p.17–18]", "CMJ peak force (N)", "IMTP peak force (N)", "DSI = CMJ ÷ IMTP", "Classification → priority"],
                         [["Result", B, B, B, "&lt;0.60 Low → ballistic · 0.60–0.80 Moderate → concurrent · &gt;0.80 High → max strength"]], ["16%", "16%", "16%", "16%", "36%"]))
    out.append(sheet_head("3.8 Speed & sprint mechanics") + rec_table(["Sprint", "Trial 1 (s)", "Trial 2 (s)", "Trial 3 (s)", "Best (s)", "Notes"],
               [["0–10 m [P1 p.31]", B, B, B, B, B], ["0–30 m [P1 p.31]", B, B, B, B, B], ["Flying ____ m (MSS) [P2 p.75]", B, B, B, B, "MSS = ____ m/s × 3.6 = ____ km/h"]],
               ["26%", "13%", "13%", "13%", "13%", "22%"]))
    out.append(rec_table(["MSS band (20 m flying) [P2 p.76]", "Good", "Average", "Poor"], [["20 m flying time", "&lt; 2.1 s", "2.1–2.3 s", "&gt; 2.3 s"]], ["40%", "20%", "20%", "20%"]))
    out.append(rec_table(["Mechanics marker", "Acceleration [P1 p.63–64]", "Max velocity [P2 p.57–58]", "Notes"], [
        ["Frontside – hand", "Lead hand past eye level □", "Lead hand to eye level □", B], ["Frontside – shin / thigh", "Shin & torso parallel □", "Thigh & torso perpendicular □", B],
        ["Frontside – heel", "Heel off ground in contact □", "Heel off ground in contact □", B], ["Backside – leg", "Push leg triple extends □", "Active heel recovery □", B]],
        ["24%", "27%", "27%", "22%"]))
    out.append(sheet_head("3.9 Energy systems / fitness") + rec_table(["Test", "Result", "Derived value", "Band used (state source)", "Classification", "Notes"], [
        ["Bronco (min:s) [P2 p.87]", B, "MAS = 1200 ÷ ___ s = ___ m/s (×3.6 = ___ km/h)", "□ P2 p.87 □ P2 p.75 □ P1 p.21", B, B],
        ["1.5 km time trial (min:s) [P2 p.74]", B, "MAS = 1500 ÷ ___ s = ___ m/s", NS, B, B],
        ["ASR [P2 p.76]", "MSS ___ km/h", "ASR = MSS − MAS = ___ km/h", "—", "—", B]], ["20%", "12%", "24%", "18%", "12%", "14%"]))
    out.append(rec_table(["150 m shuttle [P2 p.86]"] + [f"Run {i}" for i in range(1, 7)] + ["Total (m)"], [["Distance (m)"] + [B] * 7],
                         ["20%"] + ["10%"] * 6 + ["20%"]))
    out.append('<p class="small">Bands: &gt; 740 m good · 700–740 m average · &lt; 700 m poor [P2 p.86].</p>')
    out.append(rec_table(["PDT 40 m [P2 p.85]"] + [f"S{i}" for i in range(1, 9)] + ["Fatigue index %"], [["Time (s)"] + [B] * 9],
                         ["16%"] + ["8%"] * 8 + ["20%"]))
    out.append('<p class="small">Fatigue index = % difference between fastest and slowest sprint · 0–6% good · 7–10% average · &gt; 10% poor [P2 p.85].</p>')
    # additional
    out.append('<div class="avoid"><h2>3.10 Additional assessments</h2><p>For tests added by the coach. State the reference source for every value.</p>'
               + rec_table(["Test name", "Finding / range (L | R)", "Pain / location", "Classification", "Reference / source"], [[B] * 5 for _ in range(6)],
                           ["24%", "22%", "18%", "16%", "20%"]) + "</div></section>")
    return "".join(out)


def lines(n):
    return '<div class="lines">' + "<div></div>" * n + "</div>"


def build_report():
    o = ['<section class="chapter"><div class="eyebrow">Section 4</div><h1>Final client assessment report</h1><div class="bar"></div>',
         table(["Client", "Assessment date", "Coach", "Next reassessment"], [[B, B, B, B]], cls="form rec", raw=True)]
    for h, n in [("Overall assessment findings / main findings", 4), ("Strengths", 3), ("Weaknesses", 3), ("Mobility limitations", 3), ("Stability limitations", 3),
                 ("Strength deficits", 3), ("Movement quality observations & compensations", 3), ("Asymmetries (left vs right)", 2), ("Performance limitations", 3),
                 ("Pain-related findings (record only – no diagnosis)", 2), ("Areas requiring further attention", 2)]:
        o.append(f'<div class="avoid"><h3>{h}</h3>{lines(n)}</div>')
    o.append('<h2>Priority areas</h2><p class="small">Classify only when supported by the assessment findings and your professional interpretation.</p>' +
             table(["Priority", "Finding", "Supporting test result(s)", "Planned action"], [["High", B, B, B], ["High", B, B, B], ["Medium", B, B, B], ["Medium", B, B, B],
                                                                                         ["Low", B, B, B], ["Low", B, B, B]], cls="rec", raw=True, widths=["12%", "30%", "28%", "30%"]))
    o.append("<h2>Coaching recommendations</h2>")
    for h in ["Recommended corrective exercises", "Mobility recommendations", "Stability exercises", "Strengthening priorities", "Movement technique improvements",
              "Recommended training focus / coaching priorities"]:
        o.append(f'<div class="avoid"><h3>{h}</h3>{lines(2)}</div>')
    o.append(note("Pain, suspected injury or medical concerns found during screening are outside the scope of a fitness assessment. Record them and refer the client to a qualified "
                  "healthcare professional before progressing the related training.", "Referral") + f'<div class="avoid"><h3>Areas requiring referral to a qualified healthcare professional</h3>{lines(2)}</div>')
    o.append("<h2>Action plan</h2>" + table(["Item", "Details"], [["Short-term goals (4–6 weeks)", B], ["Long-term goals", B], ["Training modifications", B],
             ["Reassessment recommendations (tests + date)", B]], cls="form rec", raw=True, widths=["32%", "68%"]))
    o.append(table(["Coach signature", "Date", "Client signature", "Date"], [[B, B, B, B]], cls="form rec", raw=True) + "</section>")
    return "".join(o)


def build_tracking():
    o = ['<section class="chapter"><div class="eyebrow">Section 5</div><h1>Reassessment &amp; progress tracking</h1><div class="bar"></div>',
         "<p>Write the date of each session in the header row. Use the same protocol, equipment and time of day for every re-test. In the progress column write ↑ improvement, "
         "↓ regression or = no change (remember: for times and the PDT fatigue index, lower is better).</p>"]
    W = ["24%", "8%", "11%", "11%", "11%", "11%", "10%", "14%"]
    H = ["Test", "Unit", "Initial<br>__/__/__", "Re 1<br>__/__/__", "Re 2<br>__/__/__", "Re 3 / latest<br>__/__/__", "Progress / regression", "Coach's notes"]
    for c in CATS:
        rows = []
        for t in [x for x in TESTS if x["cat"] == c]:
            if t["sides"] or t["sheet"] == "perfLR":
                for s in ("L", "R"):
                    rows.append([f"{esc(t['name'])} – {s}", esc(t["unit"])] + [B] * 6)
            elif t["id"] == "SP1":
                rows += [["Sprint 0–10 m", "s"] + [B] * 6, ["Sprint 0–30 m", "s"] + [B] * 6]
            elif t["id"] == "A1":
                rows += [["Height", "cm"] + [B] * 6, ["Body mass", "kg"] + [B] * 6]
            elif t["id"] == "M1":
                rows.append(["MCS overhead squat score", "/12"] + [B] * 6)
            else:
                rows.append([esc(t["name"]), esc(t["unit"])] + [B] * 6)
        o.append(f'<h2>{esc(c)}</h2>' + table(H, rows, cls="rec", raw=True, widths=W))
    o.append("</section>")
    return "".join(o)


def build_profile():
    def form(title, fields, n=None):
        return f'<div class="avoid"><h2>{title}</h2>' + table(["Field", "Client response"], [[f, B] for f in fields], cls="form", raw=True, widths=["36%", "64%"]) + "</div>"
    o = ['<section class="chapter"><div class="eyebrow">Section 1</div><h1>Client profile &amp; initial information</h1><div class="bar"></div>']
    o.append(form("Personal information", ["Full name", "Age", "Sex / gender (optional)", "Date of birth", "Phone number", "Assessment date", "Coach name", "Occupation",
                                            "Sport / physical activity"]))
    o.append(form("Anthropometric measurements", ["Height (cm)", "Body weight (kg)", "Body fat % (skinfold sum of 4 → Table A1, if measured)", "Muscle mass (if available)",
                                                   "Resting heart rate (optional)"]))
    o.append(form("Training background", ["Training age / training experience", "Previous sports experience", "Current training frequency (sessions/week)",
                                           "Previous training programs", "Current physical activity level"]))
    o.append(form("Client goals", ["Primary goal", "Secondary goals", "Short-term goals", "Long-term goals", "Specific performance goals", "Areas the client wants to improve"]))
    o.append(form("Health &amp; injury history", ["Previous injuries", "Current injuries", "Current pain or discomfort", "Pain location", "Previous surgeries",
                                                   "Medical history", "Medical considerations / restrictions", "Current physical limitations"]))
    o.append(form("Lifestyle &amp; recovery", ["Occupation / daily activity level", "Sleep quality", "Average sleeping hours", "Stress level", "Recovery habits"]))
    o.append(form("Additional coaching notes", ["Client expectations", "Movement limitations reported", "Areas of concern", "Other relevant information"]))
    o.append(note("If the client reports current pain, a recent injury or surgery, or a medical condition, consider referral and clearance from a qualified healthcare professional "
                  "before maximal or high-intensity tests. The course material does not provide a pre-test medical screening protocol.", "Before testing", flag=True))
    o.append("</section>")
    return "".join(o)


def build_appendix():
    o = ['<section class="chapter"><div class="eyebrow">Appendix A</div><h1>Reference tables</h1><div class="bar"></div>']
    half = len(SKIN) // 2
    o.append(f"<h2>A1 – Sum of 4 skinfolds → body fat % {src('P1 p.29')}</h2>" + table(["Sum (mm)", "Male %", "Female %", "Sum (mm)", "Male %", "Female %"],
             [[a[0], f"{a[1]:.2f}", f"{a[2]:.2f}", b[0], f"{b[1]:.2f}", f"{b[2]:.2f}"] for a, b in zip(SKIN[:half], SKIN[half:])]))
    o.append(f"<h2>A2 – Load–velocity table, back squat (Medina 2010, T1) {src('P1 p.33')}</h2>" + table(["%1RM", "Mean velocity (m/s)", "%1RM", "Mean velocity (m/s)"],
             [[f"{a[0]}%", f"{a[1]:.2f}", f"{b[0]}%" if b else "", f"{b[1]:.2f}" if b else ""] for a, b in zip(VBT[:8], VBT[8:] + [None])]))
    o.append(f"<h2>A3 – Velocity zones {src('P2 p.25')}</h2>" + table(["Training effect", "Upper body (m/s)", "UB %1RM", "Lower body (m/s)", "LB %1RM"], [
        ["Light power", "0.8–1.0", "30–50%", "1.1–1.5", "40–60%"], ["Heavy power", "0.6–0.8", "50–70%", "0.7–1.1", "60–80%"],
        ["General strength", "0.4–0.55", "75–85%", "0.5–0.7", "75–85%"], ["Maximal strength", "0.2–0.4", "85%+", "0.3–0.5", "85%+"]]))
    o.append(table(["FV zone (intensive)", "Velocity"], [["Max strength", "&lt; 0.5 m/s"], ["Strength-speed", "0.5–0.75 m/s"], ["Max power", "0.75–1.0 m/s"],
             ["Speed-strength", "1.0–1.3 m/s"], ["Starting strength / reactive power", "&gt; 1.3 m/s"]], raw=True))
    o.append(f"<h2>A4 – Lower-body ROM targets (MCS) {src('P1 p.45–46')}</h2>" + table(["Test", "Muscles (as listed)", "Target"], [
        ["Straight leg raise", "Hamstrings (biceps femoris, semimembranosus, semitendinosus)", "90°"], ["Knee to chest", "Hip mobility", "110–120°"],
        ["Prone hip extension", "Psoas, iliacus, rectus femoris, TFL", "30–45°"], ["Prone internal rotation", "Piriformis", "30–45°"],
        ["Prone external rotation", "Adductors, glute medius, glute minimus", "60°"], ["Prone knee flexion (passive)", "Rectus femoris, vasti", "160°"],
        ["Prone ankle dorsiflexion", "Soleus, gastrocnemius", "15–25°"]]))
    o.append(f"<h2>A5 – CMS Assessment Sheet references {src('CMS Assessment Sheet')}</h2>")
    rows = []
    for g, names in CMS_LIST:
        for n in names:
            t = BY_ID[CMS_MAP[n]]
            r = "; ".join(a for a, s in t["refs"] if s == "CMS Assessment Sheet") or "Observation list (see M1)"
            rows.append([esc(g.split(" (")[0]), esc(n), esc(r)])
    o.append(table(["Section", "Test", "Reference"], rows, raw=True, widths=["20%", "30%", "50%"]))
    o.append(note("These CMS values were taken from the text of your brief. The two CMS sheet images were not received in this session, so they could not be checked against the "
                  "original image. Please confirm them – especially neck flexion (“chin to head”).", "Verification status", flag=True))
    o.append(f"<h2>A6 – Bronco: three band sets in the course</h2>" + table(["Source", "Good", "Average", "Poor"], [
        ["Phase 2 test page [P2 p.87]", "&lt; 4:45", "4:45–5:00", "&gt; 5:00"], ["Phase 2 MAS classification [P2 p.75]", "&lt; 4:35", "4:35–4:50", "&gt; 4:50"],
        ["Phase 1 team profile [P1 p.21]", "&lt; 4:30", "4:30–4:45", "&gt; 4:45"]], raw=True) + "</section>")

    o.append('<section class="chapter"><div class="eyebrow">Appendix B</div><h1>Source map &amp; duplicate audit</h1><div class="bar"></div>')
    o.append("<p>Every assessment found in the Phase 1 and Phase 2 manuals and on the CMS sheet, mapped to the single entry where it now lives. "
             f"Result: <b>{len(TESTS)} unique assessments</b> (including 3 derived indices: DSI, ASR and the estimated 1RM calculation).</p>")
    o.append("<h2>B1 – CMS sheet: all 26 tests</h2>" + table(["#", "CMS test", "OSM entry", "Merged with course test?"],
             [[i + 1, esc(n), f"{CMS_MAP[n]} · {esc(BY_ID[CMS_MAP[n]]['name'])}", "Yes" if BY_ID[CMS_MAP[n]]["merged"] else "No (CMS only)"]
              for i, n in enumerate([n for _, ns in CMS_LIST for n in ns])], raw=True, widths=["6%", "28%", "46%", "20%"]))
    o.append("<h2>B2 – Course assessments</h2>" + table(["Course assessment", "Source", "OSM entry"], [[esc(a), esc(s), f"{e} · {esc(BY_ID[e]['name'])}"] for a, s, e in COURSE_MAP], raw=True,
             widths=["40%", "20%", "40%"]))
    o.append("<h2>B3 – Duplicates merged (one entry each)</h2>" + table(["Entry", "Merged sources", "Different values kept?"], [
        [f"{t['id']} · {esc(t['name'])}", esc(t["merged"]), "Yes – both shown with sources" if any(w in t["merged"] for w in ("differ", "DIFFERENT")) else "Values agree"]
        for t in TESTS if t["merged"]] + [
        ["E1 · Bronco", "Phase 1 battery [P1 p.26] + profile bands [P1 p.21] + Phase 2 MAS [P2 p.74–75] + test page [P2 p.87]", "Yes – three band sets shown"],
        ["E3 · 150 m shuttle / E4 · PDT", "Phase 1 battery [P1 p.26] + Phase 2 protocols [P2 p.85–86]", "No conflict"],
        ["P1 · CMJ / ST3–ST5 · 1RM tests", "Phase 1 protocols + Phase 2 performance model [P2 p.32]", "No conflict"]], raw=True, widths=["28%", "52%", "20%"]))
    o.append(note("No assessment appears twice in Sections 2, 3 or 5. Different references for the same joint action (hip IR, knee flexion, ankle dorsiflexion, hip extension) are kept "
                  "side by side with their sources instead of being averaged.", "Audit result") + "</section>")
    return "".join(o)


def build(editable=False):
    b = []
    if editable:
        b.append(f'<img src="file://{LOGO}" style="width:70mm"><div class="eyebrow">OSM – OSAMA STRENGTH METHOD</div><h1>Complete Client Assessment System</h1><div class="bar"></div>'
                 + table(["Client name", "Assessment date", "Coach"], [[B, B, "Coach Osama"]], cls="form rec", raw=True))
    b.append(f'<section class="{"chapter" if editable else ""}"><div class="eyebrow">How to use this manual</div><h1>Using the OSM assessment system</h1><div class="bar"></div>')
    b.append(ol(["<b>Section 1</b> – complete the client profile in the consultation.", "<b>Section 2</b> – the assessment library: one card per test with protocol, references and interpretation.",
                 "<b>Section 3</b> – record sheets: write results during testing.", "<b>Section 4</b> – the final report: findings, priorities and action plan.",
                 "<b>Section 5</b> – track every test across reassessments.", "<b>Appendices</b> – reference tables, and the source map / duplicate audit."]))
    b.append("<h2>Source rules</h2>" + table(["Tag", "Meaning"], [["[P1 p.xx]", "EPI NCSC Phase 1 manual (Jan 2026), printed page number"],
             ["[P2 p.xx]", "EPI NCSC Phase 2 manual (Jan 2026), printed page number"], ["[CMS]", "Coach Osama's CMS Assessment Sheet (values as provided in his brief)"],
             [NS, "The course and the CMS sheet give no value or protocol for this item. Nothing has been filled in from outside sources."],
             ["Additional note (not course material)", "External information, clearly separated and cited"]]))
    b.append(note("“Case-study label” values (e.g. CMJ 35 cm = Average) describe one example athlete in the course and are not general norms. Where the course gives different values "
                  "for the same test, all are shown with their sources. Classification is only pre-printed where the course provides a system; otherwise the coach decides. "
                  "This manual supports coaching decisions; it is not a medical assessment and must not be used to diagnose.", "Read before use"))
    b.append(table(["Recommended testing order (course) [P1 p.20]", ""], [["1 Bodyweight · 2 Body composition · 3 Leg power · 4 Speed · 5 Strength · 6 Energy system test",
             "Movement screen (MCS + mobility) before fitness testing [P1 p.19]. Sprint rule: don't sprint when tired, sore or mentally stressed [P1 p.55]."]], raw=True))
    b.append("</section>")
    b.append(build_profile())
    b.append('<section class="chapter"><div class="eyebrow">Section 2</div><h1>Complete assessment library</h1><div class="bar"></div>'
             + table(["Category", "Assessments"], [[esc(c), "; ".join(f"{t['id']} {esc(t['name'])}" for t in TESTS if t["cat"] == c)] for c in CATS], raw=True, widths=["28%", "72%"]))
    for c in CATS:
        b.append(f'<h2 style="break-before:page">{esc(c)}</h2>' + "".join(card(t) for t in TESTS if t["cat"] == c))
    b.append("</section>")
    b.append(build_record_sheets())
    b.append(build_report())
    b.append(build_tracking())
    b.append(build_appendix())
    return page("OSM – Complete Client Assessment Manual", "".join(b))


def build_cover():
    return cover("OSM – OSAMA STRENGTH METHOD", "Complete Client<br>Assessment System",
                 "Client profile · assessment library · record sheets · assessment report · reassessment tracking. Built from the EPI NCSC Phase 1 &amp; 2 course material and the OSM CMS Assessment Sheet.",
                 "Head Coach: Coach Osama · OSM – Osama Strength Method · Every value is traceable to its source: [P1]/[P2] = EPI NCSC Phase 1/2 manuals (2026), [CMS] = OSM CMS Assessment Sheet.",
                 fields=["CLIENT NAME", "ASSESSMENT DATE"])
