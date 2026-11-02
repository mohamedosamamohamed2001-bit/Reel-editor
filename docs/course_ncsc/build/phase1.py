"""OSM – Phase 1 Summary (EPI NCSC Phase 1 manual, Jan 2026). Every point is referenced to the manual's printed page
numbers as [P1 p.xx]. Paraphrased study notes for Coach Osama's personal use; values are reproduced exactly."""
from common import *

R = lambda p: src(f"P1 p.{p}")

SKIN = [(5, -7.23, -2.69), (10, 0.41, 5.72), (15, 5.00, 10.78), (20, 8.32, 14.44), (25, 10.92, 17.33), (30, 13.07, 19.71),
        (35, 14.91, 21.74), (40, 16.51, 23.51), (45, 17.93, 25.09), (50, 19.21, 26.51), (55, 20.37, 27.80), (60, 21.44, 28.98),
        (65, 22.42, 30.08), (70, 23.34, 31.10), (75, 24.20, 32.05), (80, 25.00, 32.94), (85, 25.76, 33.78), (90, 26.47, 34.58),
        (95, 27.15, 35.34), (100, 27.80, 36.06), (105, 28.42, 36.74), (110, 29.00, 37.40), (115, 29.57, 38.03), (120, 30.11, 38.63),
        (125, 30.63, 39.21), (130, 31.13, 39.77), (135, 31.62, 40.31), (140, 32.08, 40.83), (145, 32.53, 41.34), (150, 32.97, 41.82),
        (155, 33.39, 42.29), (160, 33.80, 42.75), (165, 34.20, 43.20), (170, 34.59, 43.63), (175, 34.97, 44.05), (180, 35.33, 44.46),
        (185, 35.69, 44.86), (190, 36.04, 45.25), (195, 36.38, 45.63), (200, 36.71, 46.00)]
VBT = [(30, 1.33), (35, 1.21), (40, 1.15), (45, 1.06), (50, 0.97), (55, 0.89), (60, 0.80), (65, 0.72), (70, 0.64), (75, 0.56),
       (80, 0.48), (85, 0.41), (90, 0.33), (95, 0.26), (100, 0.19)]
ROM = [("Straight leg raise (SLR)", "Biceps femoris, semimembranosus, semitendinosus (hamstrings)", "90°"),
       ("Knee to chest", "Hip mobility", "110–120°"),
       ("Prone hip extension", "Psoas, iliacus, rectus femoris, TFL", "30–45°"),
       ("Prone internal rotation", "Piriformis", "30–45°"),
       ("Prone external rotation", "Adductors, glute medius, glute minimus", "60°"),
       ("Prone knee flexion (passive)", "Rectus femoris, vastus medialis / lateralis / intermedius", "160°"),
       ("Prone ankle dorsiflexion", "Soleus, gastrocnemius", "15–25°")]


def skin_table():
    half = len(SKIN) // 2
    rows = [[a[0], f"{a[1]:.2f}", f"{a[2]:.2f}", b[0], f"{b[1]:.2f}", f"{b[2]:.2f}"] for a, b in zip(SKIN[:half], SKIN[half:])]
    return table(["Sum of 4 folds (mm)", "Males (% fat)", "Females (% fat)", "Sum of 4 folds (mm)", "Males (% fat)", "Females (% fat)"], rows)


def build():
    b = []
    b.append('<section><div class="eyebrow">How to use this summary</div><h1>Phase 1 Summary</h1><div class="bar"></div>')
    b.append(f"""<p>A structured revision resource for the <b>EPI National Certificate in Strength &amp; Conditioning (NCSC), Phase 1</b>
course manual (Elite Performance Institute, author Karl Gilligan, published January 2026). It follows the order of the manual. Every fact carries
its source page as {src('P1 p.xx')} (the manual's printed page number), so you can check it against the original.</p>""")
    b.append(note("Content is paraphrased from the course manual; numbers, tables and protocols are reproduced exactly. Anything that is "
                  "<b>not</b> from the manual is marked <b>Additional note (not course material)</b>. Items the manual leaves unclear are listed in "
                  "the final chapter instead of being guessed.", "Source rule"))
    toc = [("1", "Course overview, aims and exam"), ("2", "The EPI coaching system: pillars, framework, training system"),
           ("3", "Fitness testing (Section 1)"), ("4", "Movement screening: MCS and ROM (Section 2)"),
           ("5", "Acceleration speed (Lecture 2, Sections 3–4)"), ("6", "Olympic weightlifting: the Clean & Jerk (Lecture 3, Section 5)"),
           ("7", "Program design (Lecture 4)"), ("8", "Slow SSC plyometrics (Section 6)"), ("9", "ATP-CP energy system (Section 7)"),
           ("10", "Linear periodization (Lecture 5)"), ("11", "References, recommended reading and unclear points")]
    b.append(table(["#", "Chapter"], toc, cls="toc", widths=["10%", "90%"]) + "</section>")

    # 1
    b.append(chapter("Chapter 1", "Course overview"))
    b.append(f"<h2>Phase 1 learning aims {R(3)}</h2>" + ul(["Movement screen an athlete", "Fitness assess an athlete", "Coach acceleration speed",
             "Coach the Clean &amp; Jerk", "Develop slow stretch-shortening-cycle (SSC) plyometrics", "Develop the ATP-CP energy system",
             "Create strength &amp; power programs following the EPI system", "Plan the year with a linear periodized approach"]))
    b.append(f"<h2>Three-day structure {R(7)}</h2>" + table(["Day", "Lectures", "Practicals"], [
        ["1 – Fitness testing &amp; Movement Compensation Screen (MCS)", "Course introduction &amp; EPI training system", "Fitness testing &amp; profiling; movement screening; corrective exercises"],
        ["2 – Acceleration speed &amp; Olympic weightlifting", "Acceleration; Olympic weightlifting", "RAMP warm-up, speed testing, acceleration; Clean &amp; Jerk"],
        ["3 – Program design &amp; energy system development (ESD)", "Program design fundamentals; linear periodization", "Slow SSC plyometrics; ATP-CP ESD"]], raw=True))
    b.append(f"<h2>NCSC exam {R(11)}</h2>" + table(["Part", "Format", "Duration", "Content", "Pass"], [
        ["Written", "Multiple-choice questionnaire (MCQ)", "60 min", "Phase 1 and Phase 2 course manuals", "70%"],
        ["Practical", "Olympic weightlifting", "30 min", "Demonstration skills, technical and coaching models", "70%"]]))
    b.append(f"<p>Phase 2 adds: strength &amp; power and advanced program design (snatch, upper-body strength &amp; power), max-velocity speed and ESD, "
             f"conjugate periodization, an athlete case study, fast SSC plyometrics and ESD testing &amp; training {R(11)}.</p></section>")

    # 2
    b.append(chapter("Chapter 2", "The EPI coaching system"))
    b.append(f"<h2>Two areas of S&amp;C coaching {R('13–14')}</h2>" + table(["Gym-based coaching skills", "Pitch-based coaching skills"],
             [["Strength, power, hypertrophy training, prehabilitation", "Warm-ups, linear speed, agility, energy system development (ESD)"]]))
    b.append(f"<h2>The four pillars of effective S&amp;C coaching {R(14)}</h2>" + table(["Pillar", "Meaning"], [
        ["1 Philosophy", "A clear S&C philosophy: the set of beliefs and guiding principles that determine how you coach"],
        ["2 Methodology", "How you coach new movement skills (technical model + coaching model)"],
        ["3 Framework", "A step-by-step process for enhancing athleticism"],
        ["4 System", "The roadmap for your S&C coaching"]]))
    b.append(f"""<h3>Pillar 1 – Philosophy {R(15)}</h3><p><b>Technical ability first, then physical ability.</b> First ask whether the athlete has the
mobility and stability for the movement and the coordination to perform it; only then whether they have the strength and power qualities it requires.</p>
<h3>Pillar 2 – Methodology {R('15–17')}</h3>""")
    b.append(table(["Tool", "Definition", "Back squat example"], [
        ["Technical model (T-model)", "A series of key points that define perfect form", "Feet shoulder/hip width and turned out; knees track in line with feet; torso stays upright; back remains flat; hips move towards ankles after 90°"],
        ["Coaching model (C-model)", "Breaking a complex skill into a series of simpler movements", "Air squat → goblet squat → box squat → back squat"]]))
    b.append(f"<p>T- and C-models exist for GYM skills (squat pattern: back, front, overhead squat; hinge: RDL, deadlift; Olympic lifts: clean, jerk, snatch; "
             f"plyometrics: slow and fast SSC) and PITCH skills (linear speed: acceleration, max velocity; agility: deceleration, turning, evasion/side-step) {R(17)}.</p>")
    b.append(f"<h3>Pillar 3 – Coaching framework (5 steps) {R('17–19')}</h3>" + ol([
        "<b>Athletic objectives</b>", "<b>Physical quality(s)</b> – strength, power, speed, agility, endurance, mobility, hypertrophy (7 qualities)",
        "<b>Training methods</b> – a specific way of training that targets one physical quality (e.g. powerlifting is a sport and a method for max strength)",
        "<b>Exercise selection</b>", "<b>Program variables</b> – sets &amp; reps, intensity, volume (= training dosage), rest: managed to elicit the desired adaptation"]))
    b.append(f"<h3>Pillar 4 – The EPI training system (8 steps) {R(19)}</h3>" + ol([
        "Athlete / head-coach consultation", "Needs analysis", "Movement screening", "Fitness testing", "Profile results",
        "Periodization plan &amp; program design", "Develop the FV curve (strength–power)", "Develop the VI curve (ESD–speed)"]))
    b.append(f"<h2>Worked example: semi-professional football team {R('20–21')}</h2>")
    b.append(table(["Step", "Content in the manual"], [
        ["Consultation", "Average age 22; semi-professional; training age 2 years; 3rd division; hard-working; off-season; goals speed, power, fitness; previous hamstring strains and ankle sprains; 3 pitch + 1 gym session per week; 90 min pitch / 60 min gym"],
        ["Needs analysis – primary", "Linear speed (acceleration), agility, speed endurance (ATP-CP fitness)"],
        ["Needs analysis – secondary", "Power (reactive strength), aerobic fitness"],
        ["Injury profile", "Muscle strains = 41% of all injuries; hamstring strains = 16% of all injuries and 39.5% of strains (Jones et al., 2021)"],
        ["Considerations", "Semi-pro; training age 2; movement skill unknown; 1 gym + 3 football sessions per week; 6-week pre-season"],
        ["Movement screening", "MCS: overhead squat test + range-of-motion (ROM) testing"],
        ["Fitness testing order", "1 bodyweight → 2 body composition → 3 leg power → 4 speed → 5 strength → 6 energy system test"]]))
    b.append(f"<h3>Profile results – traffic-light bands used in the example {R(21)}</h3>" + table(["Test", "Poor", "Average", "Good"], [
        ["CMJ (leg power)", "&lt; 35 cm", "35–40 cm", "&gt; 40 cm"], ["Bronco (aerobic fitness)", "&gt; 4:45 min", "4:30–4:45 min", "&lt; 4:30 min"]], raw=True))
    b.append(note("These bands are the example team's profile. Phase 2 gives different Bronco bands (see the Phase 2 summary). Quote the source when you use them.", "Context", flag=True))
    b.append(f"<h2>Periodization plans {R(22)}</h2>" + table(["Model", "Gym sequence", "Pitch sequence"], [
        ["Linear", "Hypertrophy → max strength → power", "Aerobic fitness → ATP-CP fitness → speed &amp; agility"],
        ["Conjugate", "Strength endurance &amp; hypertrophy → max strength &amp; slow-SSC power → speed-strength &amp; fast-SSC power",
         "Aerobic &amp; anaerobic fitness → ATP-CP fitness &amp; acceleration speed → max-velocity speed &amp; agility"]], raw=True))
    b.append(f"<h2>The FV curve and the VI curve {R('22–23')}</h2><div class='key'><div class='box'><h4>Force–velocity (FV) curve – gym</h4>"
             "<p><span class='pill ext'>EXTENSIVE</span> movement skill training, strength endurance, hypertrophy, prehabilitation.</p>"
             "<p><span class='pill int'>INTENSIVE</span> along the curve from high force / low velocity to low force / high velocity: "
             "max strength → explosive strength → reactive strength.</p></div><div class='box'><h4>Volume–intensity (VI) curve – pitch</h4>"
             "<p><span class='pill ext'>EXTENSIVE</span> aerobic system, anaerobic glycolysis system.</p><p><span class='pill int'>INTENSIVE</span> "
             "from high volume / low intensity to low volume / high intensity: ATP-CP system → agility → acceleration speed → max velocity speed.</p></div></div>")
    b.append(fv_svg([(0.08, "Max strength"), (0.35, "Explosive strength"), (0.75, "Reactive strength")], "Intensive FV qualities (Phase 1 labels)"))
    b.append(fv_svg([(0.06, "ATP-CP"), (0.3, "Agility"), (0.55, "Acceleration"), (0.85, "Max velocity")], "Intensive VI qualities", "Intensity", "Volume"))
    b.append('<p class="small">Diagrams redrawn schematically from the manual (positions illustrative, not measured values).</p>')
    b.append(f"<p><b>Motto:</b> “Keep it simple.” {R(23)}</p></section>")

    # 3 fitness testing
    b.append(chapter("Chapter 3", "Fitness testing"))
    b.append(f"<p>Purpose: objective monitoring of fitness qualities over time with EPI's standardized test battery {R(24)}.</p>")
    b.append(f"<h2>Planning a testing session {R(25)}</h2>" + ol(["Time of season", "Facilities (gym vs pitch)", "Equipment", "Qualities to assess",
             "Order of tests", "Group management (squad size)"]))
    b.append(f"<h2>Test battery summary {R(26)}</h2>" + table(["Component", "Tests", "Equipment"], [
        ["Anthropometrics &amp; body composition", "Height, weight, skinfolds", "Stadiometer, digital scales, Harpenden calipers"],
        ["Leg power", "Countermovement jump (CMJ); standing long jump (SLJ)", "Electronic jump mat; long jump mat"],
        ["Speed", "0–10 m acceleration; 0–30 m max velocity", "Electronic timing gates (stopwatch alternative)"],
        ["Strength", "Bench press; back squat; chin up", "Bench; squat rack; chin bar"],
        ["Energy systems", "Bronco (aerobic); 150 m shuttle (anaerobic glycolysis); phosphate decrement test (ATP-CP)", "Cones + stopwatch; cones + stopwatch; timing gates"]], raw=True))
    b.append(f"<h2>Skinfold measurement (4 sites) {R('27–29')}</h2><h3>Technique</h3>" + ol([
        "Measure on dry skin, before exercise.", "Pinch skin and subcutaneous fat between thumb and index finger.",
        "Place the caliper prongs perpendicular to the fold, 1–2 cm from the fingers; release the caliper grip.",
        "Read 1–2 s later, to the nearest 0.5 mm.", "Take one measurement per site, then repeat all sites.",
        "If two readings differ by ≤ 10%, average them; otherwise keep measuring until two readings are within 10%."]))
    b.append(table(["Site", "Fold", "Location"], [["Biceps", "Vertical", "Front of arm, midway between acromion and cubital fossa"],
             ["Triceps", "Vertical", "Back of arm, midway between acromion and olecranon"], ["Subscapular", "Diagonal", "2 cm below the inferior angle of the scapula"],
             ["Suprailiac", "Diagonal", "1 cm above the iliac crest"]]))
    b.append(f"<h3>Table 1 – Sum of 4 skinfolds → body fat % {R(29)}</h3>" + skin_table())
    b.append(f"<h2>Leg power – countermovement jump (CMJ) {R(30)}</h2>" + ol([
        "Stand on the electronic jump mat (Skyhook), feet hip/shoulder width.", "Hands on hips, kept there throughout.",
        "Squat down and immediately jump as high as possible.", "Keep legs straight in the air.", "Land on the balls of the feet, then heels.",
        "Reset the feet before the next jump.", "3 jumps; the best counts.", "Score: jump height in centimetres (cm)."]))
    b.append(f"<h2>Speed – 0–10 m and 0–30 m sprint {R(31)}</h2>" + ol([
        "Timing gates at the start, 10 m and 30 m.", "Athlete starts 0.7 m behind the start gate, between two cones.", "Two-point start.",
        "At least 1 min between sprints.", "3 sprints; the fastest counts.", "Score: seconds (s)."]))
    b.append(f"<h2>Strength – isometric mid-thigh pull (IMTP) {R(32)}</h2>" + ol([
        "Equipment: MAT IMTP platform + Muscle Meter dynamometer connected by Bluetooth (Measurz app).",
        "Stand on the platform holding the bar with straight arms; slight flexion at ankle, knee and hip.", "Remove the slack in the chain.",
        "On the cue, pull with maximal effort for 3 s.", "Score: isometric strength in kg."]))
    b.append(f"<h2>Strength – estimated 1RM with velocity-based training (VBT) {R(33)}</h2>" + ol([
        "Equipment: Vitruve linear encoder; exercise: back squat.", "Progressive loads: 3 reps at ~40% estimated 1RM, then ~60%, then ~80%.",
        "Record bar speed (m/s) and read the estimated %1RM from the load–velocity table."]))
    b.append(table(["% 1RM", "Mean velocity (m/s)"], [[f"{p}%", f"{v:.2f}"] for p, v in VBT], widths=["30%", "70%"]))
    b.append(f'<p class="small">Mean velocities from the manual\'s table (Medina 2010, T1 column); the manual shows test–retest differences of about 0.01 m/s and spreads of roughly ±0.04–0.08 m/s {R(33)}.</p>')
    b.append(f"<h2>1RM tests {R('34–36')}</h2>" + table(["Test", "Set-up and execution", "Attempts / unit"], [
        ["Back squat", "Closed pronated grip, slightly wider than shoulders; bar above the posterior deltoids at the base of the neck; extend hips and knees to unrack; 1–2 steps back; feet shoulder width or wider, toes slightly out; controlled descent to 90° or deeper", "3 attempts; kg"],
        ["Bench press", "Supine, feet on floor, hips on bench; pronated grip slightly wider than shoulders; spotter at the head end; lift off together, athlete says “my bar”; controlled lowering to touch the chest; press to full elbow extension", "3 attempts; kg"],
        ["Chin up (weighted)", "Weighted dip belt (e.g. +10 kg); closed supinated grip; start from a full hang; chin over the bar and back to full hang. <b>No rep</b> if: chin not over the bar; arms not fully extended at the bottom; kipping with the legs; knees rise above the hips", "3 attempts; kg (added load)"]], raw=True))
    b.append("</section>")

    # 4 MCS
    b.append(chapter("Chapter 4", "Movement screening"))
    b.append(f"<p>The <b>Movement Compensation Screen (MCS)</b> is a concise tool to identify problems in the musculoskeletal system and flag individuals "
             f"possibly at risk of <b>non-contact injury</b> {R(37)}.</p>")
    b.append(f"<h2>MCS 1 – Overhead squat (OHS) set-up {R(38)}</h2>" + ul([
        "Feet hip/shoulder width, pointing straight. If the feet rotate during a squat, reset them before the next rep.",
        "Dowel grip wide enough to make a right angle between upper and lower arm. Athletes widen the grip to hide mobility issues; the coach must enforce it."]))
    b.append(f"<h2>OHS scoresheet – 10 checkpoints {R(39)}</h2>" + table(["View", "#", "Compensation", "Scored"], [
        ["Front", "1", "Feet turn out", "Left / Right"], ["Front", "2", "Knees buckle in", "Left / Right"], ["Side", "3", "Heels off floor", "Yes / No"],
        ["Side", "4", "Tibial angle &lt; 15°", "Yes / No"], ["Side", "5", "Knee-dominant squat", "Yes / No"], ["Side", "6", "Lumbar spine rounds", "Yes / No"],
        ["Side", "7", "Excessive forward lean", "Yes / No"], ["Side", "8", "Arms fall forward", "Yes / No"], ["Side", "9", "Squat depth &lt; 90°", "Yes / No"],
        ["Rear", "10", "Hip weight shift", "Left / Right"]], raw=True))
    b.append(table(["Test score", "Classification"], [["0–2", "Good"], ["3–5", "Average"], ["6–12", "Poor"]], widths=["40%", "60%"]))
    b.append(note("Maximum score is 12 because checkpoints 1, 2 and 10 are scored separately for left and right. The manual shows photos for each "
                  f"compensation (feet straight vs turned out, knees aligned vs buckling, heels on/off, tibial angle 15° vs &lt; 15°, neutral vs knee-dominant, "
                  f"neutral spine vs lumbar rounding, neutral torso vs forward lean, arms aligned vs falling forward, depth 90° vs &lt; 90°, neutral hips vs weight shift) {R('40–44')}.", "Scoring"))
    b.append(f"<h2>Range of motion (ROM) – normative targets {R('45–46')}</h2>" + table(["Test", "Muscles listed in the manual", "Target ROM"], [[a, m, f"<span class='num'>{v}</span>"] for a, m, v in ROM], raw=True))
    b.append(note("The manual gives one target value or range per test with no poor/average/good bands, and no written ROM measuring protocol "
                  "(no goniometer instructions). The corrective-exercise practical on the Day 1 timetable has no written section.", "What is not in the manual", flag=True))
    b.append("</section>")

    # 5 acceleration
    b.append(chapter("Chapter 5", "Acceleration speed"))
    b.append(f"<p>Sprinting is “a movement skill involving switching on and off of almost every muscle in the body” {R(49)}.</p>")
    b.append(f"<div class='note'><b>Acceleration goal {R(50)}:</b> generate as much <b>horizontal</b> force as possible in the least amount of time while maximizing technique.</div>")
    b.append(f"<h2>Acceleration metrics {R(50)}</h2>" + table(["Metric", "Value"], [["Forward lean (body angle)", "45°"], ["First-step stride length", "1.5 m"],
             ["Foot height at first step", "15–30 cm"], ["Velocity at 10 m", "&gt; 8 m/s (29 km/h)"], ["Ground contact time (GCT)", "0.12–0.20 s"]], raw=True, widths=["50%", "50%"]))
    b.append(f"<h2>Determinants {R('50–51')}</h2>" + table(["Simplified determinant", "Meaning"], [["Technique", "Limbs: arms, legs, posture"],
             ["Force production", "Explosive force from stationary"], ["Direction of force", "Horizontal"], ["Contact time", "Short GCT &lt; 0.15 s"]], raw=True))
    b.append(table(["Mechanical factor", "Physical determinant"], [["Triple extension", "Leg extension strength"], ["45° lean", "Trunk stiffness and control"],
             ["Ankle dorsiflexed", "Leg stiffness (ankle)"], ["Short GCT", "SSC / rate of force development (RFD) and leg stiffness"],
             ["Explosive piston leg drive", "Speed-strength"], ["Explosive arm drive", "Upper-body power"]]))
    b.append(f"<h3>GPS demands in elite football (Toulouse FC, Rave et al., 2020) {R(51)}</h3>" + table(
        ["Position", "Total distance (m)", "HSR (m)", "SPR (m)", "Acc (n)", "Dec (n)", "Max speed (km/h)"], [
        ["Centre back", 9962, 493, 217, 29, 22, 34], ["Midfielder", 12045, 928, 353, 39, 62, 34], ["Wide midfielder", 10340, 756, 378, 47, 55, 34],
        ["Attacker", 10415, 643, 348, 59, 59, 35]]))
    b.append('<p class="small">Acc = accelerating efforts up to 3 m/s²; Dec = decelerating efforts up to −3 m/s². HSR / SPR abbreviations are not expanded in the manual.</p>')
    b.append(f"<h2>Technical model {R('52, 62')}</h2>" + table(["#", "Key point"], [["1", "<b>Foot</b> 15–30 cm off the ground"], ["2", "<b>Ankle</b> dorsiflexed (toe pointing forward)"],
             ["3", "<b>Shin</b> parallel with torso (positive shin angle)"], ["4", "<b>Knee</b> drive (knee pointing forward)"], ["5", "<b>Hand</b> to eye level"],
             ["6", "<b>Body angle</b> 45–60°"], ["7", "<b>Triple extension</b> from the push leg"]], raw=True, widths=["8%", "92%"]))
    b.append(table(["Backside mechanics", "Frontside mechanics"], [["Triple extension; 45–60° forward lean", "Arm drive past eye level; shin and torso parallel; no heel drop on ground contact"]]))
    b.append(f"<p>Error example in the manual: excessive forward lean; the foot “lands” instead of striking backwards {R(52)}.</p>")
    b.append(f"<h3>Speed mechanics profiling {R('63–64')}</h3>" + table(["Side", "Marker", "Efficient when…"], [["Frontside", "Hand", "Lead hand gets past eye level"],
             ["Frontside", "Shin", "Shin and torso are parallel"], ["Frontside", "Heel", "Heel stays off the ground during contact"], ["Backside", "Leg", "Push-off leg triple extends"]]))
    b.append(f"<h2>Coaching model {R('53–54')}</h2>" + ol(["Sprint technique (wall drills)", "Acceleration sprints", "Develop the FV curve (get stronger)",
             "Improve contact time: frequent sprint exposure; plyometric training", "Improve mobility"]))
    b.append(f"<p>The manual cites a systematic review (“Sprinting performance and resistance-based training interventions”): strength training, including general strength, "
             f"dynamic and unilateral exercises, increases speed. There are no magic exercises; the magic is putting all the pieces together {R(54)}.</p>")
    b.append(f"<h3>Wall drill series {R(65)}</h3>" + table(["Drill", "Key points"], [
        ["Set-up", "Body lean 45–60°; power line from ankle to shoulders; weight on the ball of the foot; abs tight; neutral spine; arms parallel with the floor"],
        ["Marches", "Pull the left leg through low to high; foot finishes 15–30 cm from the floor; ankle dorsiflexed; shin parallel with torso; knee forward; power line maintained"],
        ["Switches", "Start with the left foot forward 15–30 cm off the ground; in one fast motion switch limbs so the left becomes the support and the right foot finishes 15–30 cm off the ground"]]))
    b.append(f"<h2>Session design and speed rules {R('54–55')}</h2>" + ol(["Dynamic warm-up (RAMP)", "Speed technique (acceleration wall drills)",
             "High-intensity sprints (5–30 m)", "Overload training (resisted sprinting, hill sprints, etc.)"]))
    b.append(note("<b>Rule #1:</b> don't sprint when tired, sore or mentally stressed. <b>Rule #2:</b> don't put sprints at the end of a session.", "Speed rules"))
    b.append(f"<h2>Program design variables – acceleration {R(56)}</h2>" + table(["Variable", "Acceleration"], [["Intensity", "95–100%"], ["Distances", "5–30 m"],
             ["Rest", "60 s per 10 m"], ["Session volume", "150–250 m"], ["Methods", "Flat, uphill, resisted sprinting (sleds, Flexvit bands)"],
             ["Key cue", "“Push the ground away”"], ["Strength focus", "Develop the FV curve; prioritize plyometrics and hamstring strength"]], widths=["35%", "65%"]))
    b.append(f"<h3>Sample acceleration session {R(56)}</h3>" + table(["Block", "Prescription", "Volume"], [["Warm-up", "RAMP; wall march progression", "–"],
             ["Sprints A", "1 × (5 × 10 m), 30–60 s rest", "50 m"], ["Sprints B", "1 × (5 × 30 m), 90 s–3 min rest; 5 min between sets", "150 m"],
             ["Resisted", "Sled sprints 1 × (3 × 15 m) @ 10% bodyweight", "45 m"]]))
    b.append(f"<p><b>Final thoughts {R(57)}:</b> do the basics well; test and re-test speed; sprinting below 90% of max speed does not improve speed "
             f"(Haugen et al., “Not quite so fast”). Know your technical model, apply the coaching model consistently, and “keep the goal the goal” {R(58)}.</p>")
    b.append(f"<h2>RAMP warm-up {R('59–60')}</h2>" + table(["Phase", "Duration", "Content"], [
        ["Raise", "3–4 min", "General movement skills over 20 m and back: linear running, lateral shuffles, carioca, carioca with high knee, low skip to high skip (ladders optional). Linear session → linear drills; agility session → add multi-directional drills"],
        ["Activate", "2–3 min", "Glutes, core, VMO, hamstrings: single-leg hip lifts, side-plank lifts with leg abduction, single-leg quarter squat, single-leg T-stance (each 1 × 5–6 per side)"],
        ["Mobilize", "5–6 min", "Dynamic stretching of the lower extremity, lower back and hips"],
        ["Potentiate", "3–4 min", "Sub-maximal sprints 3 × 20 m at 70 / 80 / 90%"]]))
    b.append("</section>")

    # 6 OL
    b.append(chapter("Chapter 6", "Olympic weightlifting – Clean & Jerk"))
    b.append(f"<h2>Phases {R('67–68')}</h2>" + table(["Lift", "Phases"], [["Clean", "1 start position → 2 first pull → 3 transition → 4 second pull → 5 catch → 6 recovery"],
             ["Jerk", "1 dip → 2 drive → 3 catch → 4 recovery"]]))
    b.append(f"<p>Teaching fundamentals: technical model, coaching model, clarity in program design, demonstration skills, coaching eye {R(69)}.</p>")
    b.append(f"<h2>Clean technical model {R('69–70')}</h2>" + table(["Phase", "Key points"], [
        ["Start position", "Feet shoulder width; bar over the 1st MTP joint (big toe); pronated hook grip; knees in front of the bar; hips higher than knees; shoulders in front of the bar; back flat; scapulae retracted; elbows straight, pointing outwards; neck in slight extension; weight mid- to forefoot"],
        ["First pull", "Bar pulled slightly in towards the body; hips and shoulders rise at the same rate; posterior knee drive; back and arms straight; scapulae retracted; finishes just above the knees; weight shifts from midfoot to rear foot"],
        ["Second pull", "Torso to upright; bar contacts the upper thigh; triple extension of ankle, knee, hip; heels lift; aggressive shrug; elbows bend slightly; bar close to the body; weight from midfoot to forefoot"],
        ["Catch", "At the highest point of the second pull, flex the elbows; loosen the grip and rotate the elbows quickly under the bar; transfer weight down; land in a front-squat position with the bar on the anterior deltoids and a wider stance; weight shifts to the rear foot"]]))
    b.append(note("The manual lists transition and recovery as phases but gives no separate key points for them, and gives no written technical model for the jerk.", "Not in the manual", flag=True))
    b.append(f"<h2>Coaching model – three-phase top-down approach {R('71, 76–78')}</h2><p>Establish shoulder, T-spine, hip and ankle mobility first, and teach the front "
             f"squat before Olympic lifting. Start novices with Phase 1, bar only (an empty-bar system), 3–4 sessions per phase. Set-up: hook grip 2–3 inches outside hip width; "
             f"feet hip/shoulder width pointing straight; good posture; “sit position” (slight flexion of ankle, knee, hip).</p>")
    b.append(table(["Phase", "Drill", "Start position"], [["1 Sit position", "Shrug &amp; triple extend", "Sit"], ["1", "Front squat", "Rack"], ["1", "Clean land", "Rack"],
             ["1", "Clean drop (full squat)", "Rack"], ["1", "Receiving the bar: high-high and low-low (rib cage and belly button)", "Rack"], ["1", "Jump &amp; catch", "Sit"],
             ["2 Hang", "Hang slides; hang shrug &amp; triple extend; hang clean", "Hang"], ["3 Floor", "Clean pull; power clean; squat clean", "Floor"]], raw=True))
    b.append('<p class="small">The lecture calls Phase 1 the “crease of hip” position and the practical calls it the “sit position”: same drills.</p>')
    b.append(f"<h2>Program design for the clean {R('72–74')}</h2>" + table(["Quality", "Load", "Exercises"], [
        ["Max strength", "85%+ 1RM", "Back squat, front squat, clean deadlift"],
        ["Strength-speed", "80%+ 1RM", "Squat clean (80–100%), clean pull (100–120%)"],
        ["Speed-strength", "60–80% 1RM", "Hang cleans (60–70%), power cleans (70–80%), high pulls (60–80%), loaded plyometrics"],
        ["Reactive strength", "0–0.5 s GCT", "Box jumps (0.25–0.5 s), broad jumps (0.25–0.5 s), depth jumps (0–0.25 s)"]]))
    b.append(table(["Variable", "Guideline"], [["Sets", "3–4"], ["Reps", "1–4 (5–6 with an empty bar while learning)"],
             ["Rest", "2–3 min novice–intermediate; 3–4 min intermediate–advanced"], ["Intensity", "Strength-speed 80%+; speed-strength 60–80%"],
             ["Frequency", "Typically 1–2 Olympic lifting sessions per week"]], widths=["30%", "70%"]))
    b.append(f"<h3>Sample lower-body sessions {R('74–75')}</h3>" + table(["Strength-speed session", "Speed-strength session"], [
        ["Squat clean 3 × 2 @ 90%, 3 min", "Hang clean 3 × 4 @ 70%, 2–3 min"], ["Trap-bar jumps 3 × 4 @ 50%, 3 min", "Trap-bar jumps 3 × 4 @ 30%, 2–3 min"],
        ["BB step-ups 3 × 10, 90 s", "DB Bulgarian squats 3 × 10, 90 s"], ["SL DB RDL 3 × 10, 60 s", "SL Swiss-ball hamstring rolls 3 × 10, 60 s"],
        ["SL calf raises 3 × 10, 60 s", "SL calf switches 3 × 10, 60 s"], ["Core: plate V-ups 3 × 15; seated Russian twists 3 × 10 each side", "Core: hanging toes-to-bar 3 × 10; Swiss-ball Russian twists 3 × 10 each side"]]))
    b.append("</section>")

    # 7 program design
    b.append(chapter("Chapter 7", "Program design"))
    b.append(f"<h2>8 key variables {R(81)}</h2>" + ol(["Sports needs analysis (primary vs secondary needs: movement, strength, speed/ESD, injuries)",
             "Training age (and movement ability)", "Periodization model and period (e.g. pre-season / in-season)", "Program goal (which physical quality)",
             "Training frequency (sessions per week)", "Session design (training methods, exercise selection, exercise order)",
             "Intensity &amp; volume (% 1RM; dosage: maximum vs minimum effective dose)", "Rest periods appropriate for each strength quality"]))
    b.append(f"<h2>Physical-quality program variables {R(82)}</h2>" + table(["Session goal", "Exercises", "Sets", "Reps", "Intensity", "Rest", "Type"], [
        ["Strength endurance", "6–8", "2–3", "15+", "50–70%", "45–60 s", "Extensive"], ["Hypertrophy", "5–6", "3–4", "6–12", "70–85%", "60 s–2 min", "Extensive"],
        ["Max strength", "4–5", "3–5", "1–5", "85%+", "3 min", "Intensive"], ["Explosive strength", "4–5", "3–5", "1–4", "30–100%", "3 min", "Intensive"],
        ["Reactive strength", "4–5", "3–5", "4–5", "0–30%", "2–3 min", "Intensive"]]))
    b.append(note("For each FV-curve strength quality, choose only <b>two</b> exercises that develop it; the remaining exercises are assistance strength. "
                  f"The repetition-maximum continuum on the same page places strength/power at low reps, hypertrophy around 6–12 and muscular endurance at higher reps, with overlap {R(82)}.", "Dosage"))
    b.append(f"<h2>Session structure {R('83–85')}</h2>" + table(["Session", "Order"], [["Warm-up (always)", "Mobility → activation → movement preparation; extras: core / prehab"],
             ["Lower body", "Power → bilateral strength → assistance (unilateral strength, posterior chain)"],
             ["Upper body", "Power → bilateral strength → assistance (vertical push/pull, horizontal push/pull, accessory)"],
             ["Full body", "LB power, LB bilateral, LB assistance, UB power, UB bilateral, UB assistance"],
             ["Linear periodization types (LB)", "Hypertrophy = bilateral + assistance; strength = bilateral + assistance; power = power + assistance"]]))
    b.append(f"<h2>Exercise classification {R('86–88')}</h2>" + table(["Category", "Examples"], [
        ["LB power", "Power clean, hang snatch; hex-bar jumps, BB squat jumps; prowler/sled sprint; speed squat, speed deadlift; box jump, depth jump"],
        ["LB bilateral", "Back squat, deadlift, front squat, RDL, hip thrust"], ["LB unilateral", "Lunge, step-up, split squat, Bulgarian squat, single-leg squat"],
        ["Posterior chain", "Nordic curl, SL RDL, glute-ham bridge, Swiss-ball hamstring roll, calf raise"],
        ["UB power", "Push press, split jerk; MB chest throw; Smith bench throw; clap push-up, depth push-up"],
        ["UB bilateral", "Bench press, military press, seal row, bent-over row, chin/pull up, T-bar/Pendlay row"],
        ["UB assistance", "DB shoulder press (vertical push), DB bench (horizontal push), chin up (vertical pull), DB gorilla row (horizontal pull), DB curls (accessory)"]]))
    b.append(f"<h2>Sample sessions {R('89–92')}</h2>" + table(["Session", "Exercises"], [
        ["Full-body hypertrophy", "BB back squat 3×8 @80% 2 min; DB step-ups 3×10 60 s; DB SL RDL 3×10 60 s; BB bench 3×8 @80% 2 min; DB bent-over rows 3×10 60 s; DB 3-way raises 3×10 60 s; hanging leg raises 3×10 60 s"],
        ["Full-body max strength", "Hex-bar deadlift 4×5 @85% 3 min; DB Bulgarian 3×10 60 s; SB hamstring roll 3×10 60 s; weighted chin ups 4×5 @85% 3 min; DB shoulder press 3×10 60 s; Copenhagen holds 3×5×10 s"],
        ["Strength endurance (rower)", "BB back squat 3×45 s @50%; DB walking lunge 3×15; DB SL RDL 3×15; BB bench 3×45 s @50%; DB SA bent-over row 3×15; EZ curls 3×15; EZ triceps dips 3×15; all 60 s rest"],
        ["Explosive strength (rugby)", "Hang cleans 4×4 @70% 2–3 min; hex-bar jumps 4×4 @30% 2–3 min; DB step-ups 3×8 90 s; Nordic falls 3×5 s eccentric 90 s; foot prehab: standing forward lean 3×15 s, “Michael Jackson raises” 3×10"],
        ["Reactive strength (soccer)", "CMJ 4×4 2–3 min; broad jumps 4×4 2–3 min; DB Bulgarian 3×8 90 s; SL hamstring rolls 3×10 60 s; Swiss-ball circle rolls 3×15; hanging leg raises 3×10"]]))
    b.append(f"<p>Weeks 1–4: increase intensity (%) and decrease volume (reps); weeks 1–2 use the same layout; weeks 3–4 use fewer reps, higher intensity and more rest "
             f"(assistance exercises can change) {R(90)}.</p></section>")

    # 8 plyo
    b.append(chapter("Chapter 8", "Slow SSC plyometrics"))
    b.append(f"<p>Develop reactive strength safely and systematically with EPI's three-phase model {R(93)}.</p>" + table(["Phase", "Drills", "Progressions / targets"], [
        ["1 Fundamentals (coordination for basic jumping; start in session 1)", "CMJ; rebound CMJ; tuck jump",
         "CMJ and rebound CMJ: hands on hips → hands on hips &amp; toe up → with hands &amp; toe up. Tuck jump: with hands → with hands &amp; step"],
        ["2 Slow SSC jumps (coach in this order)", "Hurdle jump; standing long jump; box jump",
         "Hurdle height knee → mid-thigh → waist, landing stick → bounce. SLJ target: guys 2.5 m, girls 2 m. Box height target: guys 75 cm, girls 60 cm"],
        ["3 Slow SSC hops", "Standing long hop; hurdle hop", "Long hop target: guys 2.25 m, girls 1.75 m. Hurdle hop height shin → knee → mid-thigh, landing stick → bounce"]], raw=True))
    b.append(note(f"Phase 1 does not define slow vs fast SSC. Its program-design chapter places reactive-strength jumps at 0.25–0.5 s GCT (box and broad jumps) "
                  f"vs 0–0.25 s (depth jumps) {R(73)}; Phase 2 defines slow SSC as GCT 0.25–0.5 s and fast SSC as 0–0.25 s.", "Definition"))
    b.append("</section>")

    # 9 ATP-CP
    b.append(chapter("Chapter 9", "ATP-CP energy system"))
    b.append(f"<h2>Session planning in 3 steps {R(98)}</h2>" + ol(["Training method: repeated sprint training (RST) on the pitch, or a power-endurance session in the gym",
             "Power vs capacity adaptation (or both)", "A 4-week progressive overload plan"]))
    b.append(f"<h2>Session variables {R(99)}</h2><p>Adaptation: <b>neurological</b>. Theme: blue (intensive) physical quality. Primary focus: <b>intensity</b>. Method: RST.</p>"
             + table(["Variable", "ATP-CP power", "ATP-CP capacity"], [["Intensity", "95%", "85–95%"], ["Work duration", "6–8 s", "9–15 s"], ["Reps per set", "4–8", "3–6"],
             ["Sets per session", "3–4", "2–3"], ["Rep recovery (rest:work)", "5–10:1", "4–6:1"], ["Set recovery", "5 min", "5 min"], ["Session recovery", "48 h", "48 h"],
             ["Sessions per week", "1–2", "1–2"]]))
    b.append("</section>")

    # 10 linear periodization
    b.append(chapter("Chapter 10", "Linear periodization"))
    b.append(f"<p><b>Periodization</b> is the planned manipulation of training variables (load, sets, reps) to maximize adaptations; the key considerations are intensity, "
             f"volume and recovery. Why: to win; clear goals for coach and athlete; maximize athletic potential; reduce boredom and injury risk {R(101)}.</p>")
    b.append(f"<h2>Linear model – key points {R(102)}</h2>" + ul(["“X-factor” manipulation of volume and intensity",
             "Volume starts high and intensity low at the start of pre-season; as volume decreases, intensity increases",
             "Targets only <b>one</b> strength and <b>one</b> fitness quality per phase", "Target athlete: young / developmental, low training age"]))
    b.append(table(["Term group", "Items"], [["Terminology", "Macrocycle, mesocycle, microcycle, training unit"], ["Periods", "Preparatory, competition, transition"],
             ["Themes", "Extensive = yellow; intensive = blue"]]))
    b.append(f"<h2>Classification of qualities {R(103)}</h2>" + table(["", "Intensive (blue)", "Extensive (yellow)"], [
        ["Strength", "Max strength, explosive strength, reactive strength", "Corrective exercises, prehabilitation, strength endurance, hypertrophy"],
        ["Speed &amp; ESD", "Linear speed, agility, ATP-CP system", "Anaerobic glycolysis system, aerobic system"]], raw=True))
    b.append(f"<p>One main quality per phase. <b>4 steps to effective planning</b> {R(103)}: 1 arrange training themes (yellow vs blue); 2 choose physical qualities; "
             f"3 organize the weekly schedule; 4 create programs.</p>")
    b.append(f"<h2>Option 1 – less pre-season time {R('104–106')}</h2><p>Annual plan: preparatory (GPP, SPP) → competition (pre-competition, competition) → transition. "
             "Blocks: Extensive 1 (GPP) → Intensive 1 (SPP) → Intensive 2 (pre-competition).</p>")
    b.append(table(["Block", "Strength phase", "ESD &amp; speed phase"], [
        ["Extensive 1", "Hypertrophy &amp; correctives: muscle mass, movement quality (build phase)", "Aerobic: VO₂max, speed of recovery (endurance phase)"],
        ["Intensive 1", "Max strength &amp; core: 1RM, peak force (strength phase)", "ATP-CP: repeated sprint ability, RSA (speed-endurance phase)"],
        ["Intensive 2", "Reactive power &amp; prehab: rate of force development, muscular power (power phase)", "Speed &amp; agility: linear and multidirectional (speed phase)"]], raw=True))
    b.append(table(["Block (weeks 1–3)", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], [
        ["Extensive 1", "Hypertrophy (FB gym)", "Aerobic (pitch)", "MCS corrective session", "Aerobic (pitch)", "Hypertrophy (FB gym)", "Rest", "Rest"],
        ["Intensive 1", "Max strength (FB gym)", "ATP-CP (pitch)", "Core &amp; stretch", "ATP-CP (pitch)", "Max strength (FB gym)", "Rest", "Rest"],
        ["Intensive 2", "Reactive power (LB gym)", "Speed (pitch)", "Reactive power (UB gym)", "Agility (pitch)", "Prehab &amp; stretch", "Game", "Rest"]], raw=True))
    b.append(f"<h2>Option 2 – more pre-season time {R('106–108')}</h2>" + table(["Phase", "Strength", "ESD &amp; speed"], [
        ["1", "Strength endurance &amp; correctives: work capacity, movement quality (build)", "Aerobic (endurance)"],
        ["2", "Hypertrophy &amp; core: muscle mass, injury prevention (growth)", "Anaerobic glycolysis: higher work intensity, buffer lactate (lactate phase)"],
        ["3", "Max strength &amp; prehab (strength)", "ATP-CP (speed endurance)"], ["4", "Reactive power &amp; prehab (power)", "Speed &amp; agility (speed)"]], raw=True))
    b.append(f"<p>The manual shows weekly tables only for Extensive 1 of option 2 (strength endurance FB gym Mon/Fri, aerobic Tue/Thu, MCS Wed) and Intensive 2 {R(107)}.</p>")
    b.append(f"<p><b>Summary {R(108)}:</b> periodization is planning the training process; balance progressive overload, recovery and adaptation; create a plan and keep the goal the goal.</p></section>")

    # 11 refs
    b.append(chapter("Chapter 11", "References & unclear points"))
    b.append("<h2>Research cited in the Phase 1 manual</h2>" + table(["Citation as given in the manual", "Used for"], [
        ["Jones et al. (2021)", f"Injury profile in football: strains 41%, hamstring 16% / 39.5% {R(20)}"],
        ["Rave et al. (2020), Toulouse FC", f"GPS match demands by position {R(51)}"],
        ["Systematic review: “Sprinting performance and resistance-based training interventions”", f"Strength training improves sprint speed {R(54)}"],
        ["Haugen et al., “Not quite so fast”", f"Sprinting below 90% of max speed does not improve speed {R(57)}"],
        ["Medina (2010)", f"Load–velocity table for estimating 1RM {R(33)}"]], raw=True))
    b.append('<p class="small">The manual cites these by author and year only; full bibliographic details are not printed.</p>')
    b.append(f"<h2>Recommended reading {R(109)}</h2>" + ol(["Block Periodisation (Issurin)", "Clinical Sports Medicine (Brukner &amp; Khan)",
             "Designing Resistance Training Programs (Fleck &amp; Kraemer)", "Essentials of Strength and Conditioning, 4th ed. (Haff &amp; Triplett)",
             "Exercise Physiology: Human Bioenergetics and its Application (Brooks &amp; Fahey)", "Explosive Lifting for Sports (Newton)",
             "High Performance Sports Conditioning (Foran)", "High Powered Plyometrics (Radcliffe &amp; Farentinos)",
             "Muscles Testing and Function with Posture &amp; Pain, 5th ed. (Kendall et al.)", "Periodization – Theory &amp; Methodology of Training, 5th ed. (Bompa)",
             "Principles and Practice of Resistance Training (Stone)", "Science and Practice of Strength Training (Zatsiorsky &amp; Kraemer)",
             "Special Strength Training: Manual for Coaches (Verkhoshansky)", "Strength &amp; Power in Sport (Komi)",
             "Supertraining, 3rd ed. (Siff &amp; Verkhoshansky)", "Training for Speed, Agility and Quickness (Brown &amp; Ferrigno)",
             "Ultimate Back Fitness and Performance, 2nd ed. (McGill)"]))
    b.append("<h2>Points the manual leaves unclear or does not cover</h2>" + ul([
        f"Bronco bands here (good &lt; 4:30) differ from both sets in Phase 2 {R(21)}.",
        f"ATP-CP variables differ slightly from Phase 2 (capacity 9–15 s and 85–95% here; 10–15 s and 85–90% in Phase 2) {R(99)}.",
        f"High pulls 60–80% here vs 70–80% in Phase 2 {R(73)}.",
        "No ROM measuring protocol, no corrective-exercise content, no jerk technical model, and no tables for option-2 Extensive 2 / Intensive 1.",
        f"The 8th system step is written as “Develop VI curve (ESD–speed)”; its slide calls it the volume–intensity curve {R('19, 23')}."]))
    b.append("</section>")
    return page("OSM – Phase 1 Summary", "".join(b))


def build_cover():
    return cover("EPI NCSC · STUDY & REVISION RESOURCE", "Phase 1<br>Summary",
                 "Fitness testing · movement screening · acceleration · Clean &amp; Jerk · program design · slow SSC plyometrics · ATP-CP · linear periodization",
                 "Prepared for Coach Osama · OSM – Osama Strength Method · Source: EPI NCSC Phase 1 course manual (Elite Performance Institute, January 2026). "
                 "Page references [P1 p.xx] point to the manual's printed page numbers. For personal study use.")
