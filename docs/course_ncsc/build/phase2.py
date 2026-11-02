"""OSM – Phase 2 Summary (EPI NCSC Phase 2 manual, Jan 2026). References [P2 p.xx] = the manual's printed page numbers."""
from common import *

R = lambda p: src(f"P2 p.{p}")


def zones_svg():
    z = [("Max strength", "< 0.5 m/s"), ("Strength-speed", "0.5–0.75 m/s"), ("Max power", "0.75–1.0 m/s"), ("Speed-strength", "1.0–1.3 m/s"),
         ("Starting strength / reactive power", "> 1.3 m/s")]
    return fv_svg([(0.05 + i * 0.2, f"{a} ({b})") for i, (a, b) in enumerate(z)], "Force–velocity zones, intensive work", "Velocity (m/s)", "Force (N)", 620, 260)


def asr_svg():
    rows = [("MSS", "100% MSS", ""), ("180% vVO₂max", "95% MSS", "ST"), ("160% vVO₂max", "85% MSS", "RST"), ("140% vVO₂max", "75% MSS", "MAS short intervals"),
            ("120% vVO₂max", "", "MAS short intervals"), ("vVO₂max = MAS", "", "MAS long intervals"), ("90% vVO₂max", "MLSS", "MAS long intervals")]
    h = 26 * len(rows) + 30
    out = [f'<svg viewBox="0 0 620 {h}" width="100%" style="max-width:160mm;display:block;margin:2mm 0 4mm">',
           f'<rect x="150" y="10" width="14" height="{26 * len(rows)}" fill="url(#g)"/><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#56A0FB"/><stop offset="1" stop-color="#F6D96B"/></linearGradient></defs>']
    for i, (a, b, c) in enumerate(rows):
        y = 26 + i * 26
        out.append(f'<line x1="140" y1="{y}" x2="400" y2="{y}" stroke="#C9D3E0"/><text x="132" y="{y + 4}" text-anchor="end" font-size="11" font-weight="700">{esc(a)}</text>'
                   f'<text x="180" y="{y + 4}" font-size="11">{esc(b)}</text><text x="300" y="{y + 4}" font-size="10.5" fill="#12203C" font-weight="700">{esc(c)}</text>')
    out.append(f'<text x="420" y="40" font-size="10.5" font-weight="700">ASR = MSS − MAS</text><text x="420" y="56" font-size="9.5" fill="#4F5B6B">(the span from MAS up to MSS)</text></svg>')
    return "".join(out)


def build():
    b = []
    b.append('<section><div class="eyebrow">How to use this summary</div><h1>Phase 2 Summary</h1><div class="bar"></div>')
    b.append(f"""<p>A structured revision resource for the <b>EPI NCSC Phase 2</b> course manual (Elite Performance Institute, author Karl Gilligan, January 2026).
Same structure and conventions as the Phase 1 summary: every fact carries its page reference {src('P2 p.xx')}; numbers and protocols are reproduced exactly;
material not from the manual is labelled <b>Additional note (not course material)</b>.</p>""")
    b.append(table(["#", "Chapter"], [("1", "Course overview and Phase 1 recap"), ("2", "Strength & power: F–t / F–v, DSI, % method, VBT"),
             ("3", "The Snatch – coaching model"), ("4", "Advanced program design: performance model, complex & contrast training"),
             ("5", "Strength & power practical sessions"), ("6", "Max velocity speed"), ("7", "Energy system development (ESD)"),
             ("8", "Energy system testing"), ("9", "Conjugate periodization"), ("10", "Fast SSC plyometrics and RSI"), ("11", "Agility training"),
             ("12", "Anaerobic glycolysis (lactate) sessions"), ("13", "Athlete case study"), ("14", "References, reading and unclear points")], cls="toc", widths=["10%", "90%"]) + "</section>")

    b.append(chapter("Chapter 1", "Course overview"))
    b.append(f"<p>Phase 2 advances coaching skills for more elite athletes; ideally participants have at least 50 hours of coaching experience {R(3)}. Aims: develop strength &amp; power "
             f"with more advanced methods; coach the snatch; coach max-velocity speed; coach agility; develop fast SSC plyometrics; develop the aerobic and anaerobic glycolysis "
             f"systems; plan the year with a conjugate periodized approach {R(3)}.</p>")
    b.append(table(["Day", "Lectures", "Practicals"], [["1 – Olympic weightlifting &amp; advanced program design", "Strength &amp; power development; advanced program design", "Snatch coaching model; strength &amp; power development"],
             ["2 – Max velocity speed &amp; ESD", "Max velocity speed; ESD", "Max velocity speed; energy system testing"],
             ["3 – Advanced periodization &amp; agility", "Conjugate periodization; athlete case study", "Fast SSC plyometrics; agility training; anaerobic glycolysis ESD"]], raw=True))
    b.append(f"<p>Exam identical to Phase 1: MCQ 60 min on both manuals (pass 70%); Olympic weightlifting practical 30 min (pass 70%) {R(9)}.</p>")
    b.append(f"<h2>Phase 1 recap {R('10–12')}</h2>" + ul(["Pillars: philosophy (beliefs and understanding of what works), methodology (strategy for coaching new skills), framework (step-by-step approach to athleticism), system (roadmap).",
             "Philosophy: 01 technical ability (competence in movement skills) → 02 physical ability (qualities important for the sport).",
             "Methodology: technical model = key points describing how a skill is performed; coaching model = key exercises that develop the skill.",
             "Framework: physical qualities → training methods → exercise selection → program variables. Training system: the same 8 steps as Phase 1.",
             "FV curve: for each intensive point choose 1 physical quality, 2 training method, 3 exercise. VI curve: 1 physical quality, 2 training method, 3 drill."]) + "</section>")

    b.append(chapter("Chapter 2", "Strength & power"))
    b.append(f"<p>Outcomes: link the force–time (F–t) curve with the force–velocity (F–v) curve; develop strength &amp; power with the traditional % method; introduce VBT {R(13)}.</p>")
    b.append(f"<h2>Key physical quality: force under a time constraint {R('14–16')}</h2><p>Sprint, jump, endurance and games-based athletes all move and express force under a time "
             f"constraint: these sporting movements express force in <b>&lt; 0.3 s</b>. Sprinting, jumping and throwing actions sit within about 0.3 s on the F–t curve, while heavy "
             f"lifts reach peak force later (about 0.8 s). Training methods are therefore split into those that improve <b>RFD</b> (the early window) and those that improve <b>peak force</b>. "
             f"Group task in the manual: athlete A has the higher peak force (about 0.8 s), athlete B the higher early force (&lt; 0.3 s).</p>")
    b.append(f"<h2>Max power – three contributors {R(17)}</h2>" + table(["Contributor", "Definition", "Training methods"], [
        ["1 Max strength", "Develop max strength (relative to bodyweight?)", "Powerlifting, isometric training, eccentric training"],
        ["2 Power output", "Ability to express high forces as the velocity of shortening increases (concentric power)", "Olympic weightlifting, de-loaded powerlifting, loaded plyometrics, resisted sprinting"],
        ["3 RFD", "Ability to express high forces in very short periods of time (eccentric–concentric power)", "Plyometrics, medicine-ball throws"]]))
    b.append(f"<h2>Dynamic Strength Index (DSI) {R('17–18')}</h2><div class='note'><b>Formula:</b> DSI = ballistic peak force ÷ dynamic or isometric peak force = "
             f"<b>CMJ peak force (N) ÷ IMTP peak force (N)</b>.</div>")
    b.append(table(["Athlete", "CMJ peak force (N)", "IMTP peak force (N)", "DSI"], [["A", 1200, 2650, "0.45"], ["B", 1500, 2150, "0.70"], ["C", 1800, 2000, "0.9"]]))
    b.append(table(["DSI score", "Classification", "Training priority"], [["&lt; 0.60", "Low", "Ballistic training"], ["0.60–0.80", "Moderate", "Concurrent training"],
             ["&gt; 0.80", "High", "Max strength training"]], raw=True))
    b.append(note("DSI reflects the share of maximal strength “potential” not used during a ballistic exercise such as the CMJ. A higher DSI means the athlete uses "
                  "more of their force potential in the jump, so spend more time on maximal strength. A lower DSI means more time on RFD with ballistic methods.", "Interpretation"))
    b.append(f"<h2>Traditional strength &amp; power – % method {R('19–21')}</h2><p>Fundamentals: % based; primarily load based; 1RM for the main lifts. Benefits: easy to track, "
             f"no technology needed, works well for strength. Limitation: more problematic for power training.</p>")
    b.append(table(["Quality", "Traditional method", "Exercises", "Alternatives"], [
        ["Max strength", "Powerlifting", "Bilateral strength (back squat, deadlift, front squat)", "Strongman, heavy eccentrics, isometric training &amp; PROM"],
        ["Explosive power", "Olympic weightlifting", "Cleans, snatches and derivatives", "Loaded plyometrics, de-loaded powerlifting, resisted sprinting"]], raw=True))
    b.append(table(["Quality", "Exercises (dosage)", "Sets", "Reps / TUT", "Intensity", "Rest"], [
        ["Max strength", "x2 / 4–5", "3–5", "1–5 / &lt; 20 s", "85–100%", "3 min+"], ["Explosive power", "x2 / 4–5", "3–5", "1–4 / N/A", "30–80%", "3 min"],
        ["Reactive strength", "x2 / 4–5", "3–5", "Slow SSC 1–5; fast SSC 3–6", "0–30%", "2–3 min"]], raw=True))
    b.append('<p class="small">“x2 / 4–5”: two exercises for the target quality within 4–5 exercises per session. “PROM” is not expanded in the manual.</p>')
    b.append(f"<h3>Explosive power – optimal load {R(21)}</h3>" + table(["Training method", "Strength-speed (%1RM)", "Speed-strength (%1RM)"], [
        ["Olympic weightlifting", "Clean pull 100%+; mid-thigh pulls 80%+; squat clean 80%+", "Hang clean 60–70%; power clean 70–80%; high pulls 70–80%"],
        ["De-loaded powerlifting", "Speed squats 60–70%; speed deadlifts 60–70%", "Speed squats 50–60%; speed deadlifts 50–60%"],
        ["Loaded plyometrics", "Squat jumps 40–50%; trap-bar jumps 40–50%", "Squat jumps 30–40%; trap-bar jumps 30–40%"]]))
    b.append(note(f"On the same page the Olympic-lifting FV diagram lists mid-thigh pull at 100%+ while the table says 80%+ {R(21)}.", "Inconsistency in the manual", flag=True))
    b.append(f"<h3>Reactive power – slow vs fast SSC {R('22–23')}</h3>" + table(["", "Slow SSC plyometrics", "Fast SSC plyometrics"], [
        ["Type", "Single jumps", "Rebound jumps"], ["Dominance", "Concentric dominant", "Eccentric dominant"], ["Focus", "Force production", "Force absorption"],
        ["Adaptation", "Improves muscular power", "Improves tendon stiffness"], ["GCT", "0.25–0.5 s", "0.00–0.25 s"],
        ["Examples", "Hurdle jump, standing long jump, accentuated eccentric training (AET)", "Drop jumps, pogos, rebound hurdle jumps"]]))
    b.append(f"<h2>Velocity-based training (VBT) {R('23–25')}</h2><p>VBT is a method that “uses velocity to inform or enhance training practice”. Device: Vitruve (linear encoder). "
             f"It adds two intensity metrics: <b>power</b> (peak and mean, watts) and <b>velocity</b> (peak and mean, m/s). Benefits: workout tracking, athlete feedback, motivation "
             f"and monitoring, auto-regulation. Limitation: expensive equipment.</p>")
    b.append(table(["Variable", "Definition", "Use for"], [["Mean velocity (MV)", "Average velocity across the entire concentric phase", "Traditional strength exercises (e.g. squats)"],
             ["Peak velocity (PV)", "Maximum velocity reached during the concentric phase", "Ballistic exercises (Olympic lifts, loaded plyometrics)"]]))
    b.append(zones_svg())
    b.append(table(["Training effect", "Upper body VBT zone", "Upper body %1RM", "Lower body VBT zone", "Lower body %1RM"], [
        ["Light power", "0.8–1.0 m/s", "30–50%", "1.1–1.5 m/s", "40–60%"], ["Heavy power", "0.6–0.8 m/s", "50–70%", "0.7–1.1 m/s", "60–80%"],
        ["General strength", "0.4–0.55 m/s", "75–85%", "0.5–0.7 m/s", "75–85%"], ["Maximal strength", "0.2–0.4 m/s", "85%+", "0.3–0.5 m/s", "85%+"]]))
    b.append(f"<h3>Concurrent training – 4 options {R(25)}</h3>" + ol(["Separate sessions: strength (heavy) and power (light) on separate days",
             "Same session: power exercises first, then strength", "Same session: alternate strength and power exercises (<b>complex training</b>)",
             "Same session: all strength exercises first, then power (<b>contrast training</b>)"]) + "</section>")

    b.append(chapter("Chapter 3", "The Snatch – coaching model"))
    b.append(f"<p>Same three-phase top-down approach as the clean: start novices with Phase 1, bar only, an empty-bar learning system, 3–4 sessions per phase {R(28)}.</p>"
             "<h3>Set-up</h3>" + ol(["Hook grip on the bar", "Grip wide enough for the bar to sit in the “crease of the hip” position (below the ASIS, above the pubic symphysis)",
             "Feet hip/shoulder width, pointing straight", "Good posture", "“Sit position”: slight flexion of ankle, knee and hip"]))
    b.append(table(["Phase", "Drills (in order)", "Start position"], [["1 Sit position", "Shrug &amp; triple extend; elbows high; muscle snatch", "Sit"],
             ["1", "Overhead squat; snatch land; snatch drop (full squat)", "Overhead"], ["1", "Jump &amp; catch", "Sit"],
             ["2 Hang", "Hang slides; hang snatch pull; hang muscle snatch; hang snatch", "Hang"],
             ["3 Floor", "Snatch pull; muscle snatch; power snatch; squat snatch", "Floor"]], raw=True))
    b.append(note("The Phase 2 manual gives the snatch coaching model only; there is no written snatch technical model.", "Not in the manual", flag=True) + "</section>")

    b.append(chapter("Chapter 4", "Advanced program design"))
    b.append(f"<h2>Performance model roadmap – goal: speed {R(31)}</h2>" + ol(["Training goal: acceleration and max velocity development",
             "Fitness-test the player: max strength and RFD qualities; 0–10 m and 0–30 m (the slide reads “0–3m”)", "Create the S&amp;C program (gym and pitch)",
             "Coach speed: identify and correct sprint-technique errors", "Re-test: max strength and RFD; 0–10 m and 0–30 m"]))
    b.append(f"<p><b>Gym-based plan</b> {R(31)}: max strength (peak dynamic and/or isometric force); explosive power (max power output); reactive power (RFD); limb symmetry "
             f"(left vs right leg and agonist vs antagonist); trunk control (trunk stiffness and control).</p>")
    b.append(f"<h2>EPI performance model {R(32)}</h2>" + table(["Physical quality", "Performance tests", "Main exercises"], [
        ["Max strength", "1RM back squat; 1RM bench press; 1RM chin up", "Back squat, front squat, trap-bar deadlift, bench press, chin up"],
        ["Explosive power", "Power clean (watts); squat jump (m/s)", "Clean &amp; derivatives, loaded squat jumps, loaded trap-bar jumps"],
        ["Reactive power (slow &amp; fast SSC)", "CMJ; drop jump (RSI)", "SLJ, hurdle jump, box jump, drop jump, pogos, SL hops"],
        ["Limb symmetry", "SL CMJ; SL hops", "Split squats, step ups, Nordics, SL plyos"],
        ["Trunk control", "Trunk extensor endurance test", "Prone extension hold, bracing, hanging leg raises, anti-rotation"]], raw=True))
    b.append(f"<h2>Complex (CPX) vs contrast (CNT) training {R('32–34')}</h2>" + table(["", "Complex training (CPX)", "Contrast training (CNT)"], [
        ["What", "Alternates biomechanically similar high-load weight exercises with lighter-load power exercises, set for set (e.g. back squat then CMJ) (Bauer et al., 2019)",
         "Contrasting heavy and light loads: all high-load strength exercises at the start of the session, all lighter power exercises at the end (Dobbs et al., 2015)"],
        ["Why", "Post-activation potentiation (PAP)", "Targets the force and velocity components of power in the same session"]]))
    b.append(ul(["<b>Primer</b> = a max-strength exercise (e.g. squat) or an explosive-strength exercise (e.g. loaded squat jump).",
                 "<b>Plyometric</b> = slow or fast SSC, but mechanically similar to the primer: same direction of force, same joint angles, same muscle groups.",
                 "<b>Intra-set recovery:</b> find the interval at which the muscle has partly recovered from fatigue but is still potentiated (Docherty &amp; Hodgson, 2007). "
                 "Stronger, more experienced athletes are more fatigue-resistant and reach peak PAP earlier (Chiu &amp; Barnes, 2003). 3–4 min intra-complex rest appears optimal (Seitz &amp; Haff, 2016)."]))
    b.append(f"<h3>Practical application {R(34)}</h3>" + table(["Item", "Guideline"], [["Training status", "Moderately to highly trained"], ["Training age", "2 years+"],
             ["Periodization model", "Conjugate"], ["Strength standards", "Back squat 1.5 × BW and bench press 1.2 × BW"],
             ["Intra-complex recovery (CPX)", "Printed as “3–4 mins vs 1–2mins”"], ["CNT training", "Manage heavy-lifting dosage to avoid neural fatigue before ballistic exercises"]]))
    b.append(note("Handwritten notes on this page of your copy (near the strength standards and the recovery line) are not part of the printed text, and the meaning of “3–4 mins vs 1–2mins” is not explained.", "Unclear", flag=True))
    b.append(table(["Role", "Lower-body options", "Upper-body options", "Sets", "Reps", "Intensity", "Rest"], [
        ["Max strength primer", "Back squat, box squat, trap-bar deadlift, front squat", "Bench press, strict press, weighted pull-up", "3–4", "2–5", "85%+", "Intra-set 1–2 min"],
        ["Explosive power primer", "Trap-bar jumps, squat jumps, high pulls / mid-thigh pulls, hang cleans, speed squats / deadlifts", "Banded bench press, bench throws, push press", "3–4", "2–4", "30–80%", "Intra-set 1–2 min"],
        ["Reactive power (plyometric)", "CMJ, SLJ, depth jumps, pogos, rebound hurdle jumps, hops", "MB throws, muscle up, clap push-up", "3–4", "2–6", "0–30%", "Inter-set 2–3 min"]]))
    b.append(f"<p>Complex options: max strength primer + reactive power, or explosive power primer + reactive power {R(34)}.</p>")
    b.append(f"<h3>Sample sessions {R('37–38')}</h3>" + table(["Session", "Prescription"], [
        ["LB CPX (pre-season)", "1a trap-bar DL 3×4 @90% 1–2 min; 1b CMJ (slow SSC) 3×3 2–3 min; 2a box squat 3×4 @90% 1–2 min; 2b pogos (fast SSC) 3×6 2–3 min; 3 step-ups 3×8 90 s; 4 SL SB hamstring curls 3×10 60–90 s; core/prehab"],
        ["LB CPX (in-season)", "1a trap-bar DL 3×4 @90% 1–2 min; 1b drop jumps (fast SSC) 3×5, 45 cm box, &lt; 0.25 s, 2–3 min; 2 SL RDL 3×10; 3 SL calf switches 3×10 (60–90 s); core/prehab"],
        ["UB CNT (pre-season)", "Bench 3×5 @85% 3 min; seal row 3×5 @85% 3 min; MB chest throw 3×5 2 min; MB rotational hip toss 3×5 each side 2 min; DB bent-over row 3×10 60 s"],
        ["UB CNT (in-season)", "Push press 3×5 @85% 3 min; MB slams 3×5 2 min; MB single-arm rotational chest throw 3×5 2 min; 4a DB half-kneeling shoulder press 3×10 each side; 4b pull ups 3×10 90 s"]], raw=True))
    b.append(note("“Sport-specificity is less about <i>what</i> and more about <i>how much</i>”: the ingredients (strength, power, speed, agility, mobility) are the same. "
                  "“Focus on the physical qualities needed, not the movement”: kinetic and physiological adaptations outweigh kinematic ones. CPX and CNT are effective but not for every athlete; "
                  f"athletes must be physically capable of benefiting {R('38–39')}.", "Take-home messages") + "</section>")

    b.append(chapter("Chapter 5", "Strength & power – practical sessions"))
    rows = [["Traditional", "LB max strength &amp; slow SSC", "AET CMJ 3×4 @10 kg 2 min; SLJ 3×4 2.5 m+ 2 min; back squat 3×4 @90% 3 min; Nordic falls 3×5×5 s 90 s; SL calf raises 3×10 @2 RIR 60 s"],
            ["Traditional", "LB max strength &amp; fast SSC", "Pogos 3×5 m 2 min; drop jump 3×5, 45 cm, &lt; 0.25 s, 2 min; trap-bar DL 3×4 @90% 3 min; OH plate step ups 3×10 90 s; SL RDL 3×10 @2 RIR 60 s"],
            ["Traditional", "LB explosive power &amp; slow SSC", "Hurdle jump 3×4 2 min; hang cleans 3×4 @70% 2–3 min; clean pull 3×4 @90% 3 min; SL Swiss-ball hamstring rolls 3×10 60 s; SL calf switches 3×10 @2 RIR 60 s"],
            ["Traditional", "LB explosive power &amp; fast SSC", "Rebound hurdle jumps 3×5 2 min; SL pogos 3×10 m 2 min; power snatch 3×4 @75% 3 min; Nordic curls 3×5 90 s; Bulgarian squats 3×10 @2 RIR 60 s"],
            ["Complex", "LB max strength &amp; slow SSC (pre-season)", "1a back squat 3×3 @90%+ 1–2 min; 1b CMJ 3×3 40 cm+ 2 min; 2a trap-bar squat 3×3 @90% 1–2 min; 2b SLJ 3×3 2.50 m+ 2 min; 3 plate lateral lunges 3×10 @2 RIR 60 s"],
            ["Complex", "LB max strength &amp; fast SSC (in-season)", "1a partial squat 3×3 @120% 1–2 min; 1b drop jump 3×5, 45 cm, &lt; 0.25 s, 2 min; Nordic falls 3×5×5 s 90 s; OH plate walking lunges 3×10 90 s"],
            ["VBT", "LB max strength &amp; speed-strength", "Loaded squat jumps 3×4 @40%, 1.10–1.20 m/s, 2–3 min; hang clean 3×4 @70%, 1.10–1.20 m/s, 2 min; back squat 3×4 &lt; 0.5 m/s 3 min; lateral step ups 3×10 90 s; SL foot-elevated glute bridge 3×10 60 s"],
            ["VBT", "LB strength-speed &amp; fast SSC", "Pogos 3×5 m 2 min; drop jump 3×5, 45 cm, &lt; 0.25 s, 2 min; clean pull 3×4 @110%, 0.6–0.8 m/s, 3 min; SL pistol squats 3×10 90 s"]]
    b.append(f"<p>Traditional methods vs advanced methods (complex training and VBT) {R('40–44')}. RIR = reps in reserve.</p>" + table(["Method", "Session", "Prescription"], rows, raw=True) + "</section>")

    b.append(chapter("Chapter 6", "Max velocity speed"))
    b.append(f"<p>Is max-velocity training important for games-based players? Consider pitch size, player position and the tactics/formation used {R(48)}.</p>")
    b.append(f"<h2>Physiological benefits {R(48)}</h2>" + table(["Area", "Benefit"], [["Neuromuscular", "Better recruitment of higher-order motor units; activation of type IIX fibres"],
             ["Structural", "Longer hamstring fascicles; greater tendon stiffness"], ["Kinematics", "Better movement efficiency on the pitch/track"],
             ["Metabolic", "Improved anaerobic capacity"], ["Injury prevention", "Prophylactic: prepares tissues for high-force demands"]]))
    b.append(f"<h2>Mechanical factors and determinants {R(49)}</h2>" + table(["Mechanical factor", "Max velocity value"], [["Body angle", "Upright"], ["Stride length", "2.25–2.7 m"],
             ["Velocity", "12.5 m/s (45 km/h)"], ["Ground contact time", "0.08–0.10 s"], ["Contacts", "4–5 per second"]], widths=["45%", "55%"]))
    b.append(table(["Determinant", "Max velocity requirement"], [["Technique", "Move limbs with correct technique (arms, legs, posture)"],
             ["Force production", "Produce force under high eccentric demands"], ["Direction of force", "Vertical"], ["Contact time", "Very short ground contacts (&lt; 0.10 s)"]], raw=True))
    b.append(table(["", "Steps 1–3", "→ 20 m → 40 m →", "60 m"], [["GCT", "0.2 s", "decreasing", "0.08 s"], ["Force direction", "Horizontal", "→", "Vertical"]]))
    b.append("<p>As speed increases: ground contact time ↓, concentric demand ↓, eccentric demand ↑, stiffness requirement ↑.</p>")
    b.append(f"<h2>Technical model {R('50, 56')}</h2>" + table(["#", "Key point"], [["1", "<b>Foot</b> strike close to under the centre of mass (COM)"],
             ["2", "<b>Ankle</b> dorsiflexed (toe pointing forward)"], ["3", "<b>Shin</b> parallel with torso (positive shin angle)"], ["4", "<b>Knee</b> drive (knee pointing forward)"],
             ["5", "<b>Hand</b> to eye level"], ["6", "<b>Body angle</b> 80–90°"], ["7", "<b>Triple extension</b> from the push leg"]], raw=True, widths=["8%", "92%"]))
    b.append(table(["Backside mechanics", "Frontside mechanics"], [["Active heel recovery", "Arm drive past eye level; thigh parallel with the ground; no heel drop on ground contact"]]))
    b.append(f"<h3>Speed mechanics profiling {R('57–58')}</h3>" + table(["Side", "Marker", "Efficient when…"], [["Frontside", "Hand", "Lead hand gets to eye level"],
             ["Frontside", "Thigh", "Thigh and torso are perpendicular"], ["Frontside", "Heel", "Heel stays off the ground during contact"], ["Backside", "Leg", "Active heel recovery"]]))
    b.append(f"<h2>Coaching model {R(51)}</h2>" + ol(["Sprinting technique (wall drills, A series, dribble series)", "Max velocity sprints",
             "Develop the FV curve (eccentric and elastic focus)", "Muscle focus: hamstrings and glutes", "Improve contact time: frequent sprint exposure; plyometric training"]))
    b.append(f"<h3>Drills {R('59–62')}</h3>" + table(["Drill", "Key points"], [
        ["Wall set-up", "Upright torso; weight on the ball of the foot; abdominals tight; neutral spine; power line from ankle to shoulders"],
        ["Wall pull", "From set-up, actively dorsiflex; “pull” the heel under the butt while the thigh comes forward into flexion; dynamic"],
        ["Wall step", "Dorsiflex; pull the heel under the butt; “step” over the standing knee; thigh finishes parallel to the ground, shin at right angles to the thigh"],
        ["Wall punch", "From the end of the step (thigh parallel), “punch” the foot down keeping dorsiflexion; contact under the COM with a sweeping motion; pull the heel under the butt; step over the knee; cyclical action; finish in the start position"],
        ["A-walk", "Stand on one leg switching arms and legs; standing foot flat; opposite arm to leg; finish thigh parallel, ankle dorsiflexed"],
        ["A-march", "Switch arms and legs; actively punch down when lowering the thigh; land on the forefoot as you switch; opposite arm to leg"],
        ["A-skip", "1-2-1 rhythm (one foot, two feet, one foot); switch limbs on the one-foot contact before the two-foot contact"],
        ["A-run", "Switch limbs dynamically; bounce off the ground on contact; opposite arm to leg; pull the heel under the butt, step over the knee, punch the foot into the ground under the COM; fast contacts, knees high"]]))
    b.append('<p class="small">The dribble series is named in the coaching model but has no drill card in the manual.</p>')
    b.append(f"<h2>Session design and program variables {R('52–53')}</h2>" + ol(["Dynamic warm-up (RAMP)", "Speed technique (max-velocity wall drills, A series)",
             "High-intensity sprints: max velocity 30–60 m; dosage is very important, less is more"]))
    b.append(note("<b>Rule #1:</b> max velocity sprinting is neurologically very demanding. <b>Rule #2:</b> sprinting is a skill: it needs rhythm and feel to stay relaxed.", "Speed rules"))
    b.append(table(["Variable", "Max velocity (Phase 2)", "Acceleration (Phase 1, for comparison)"], [["Intensity", "95–100%", "95–100%"], ["Distances", "30–60 m", "5–30 m"],
             ["Rest", "60 s per 10 m", "60 s per 10 m"], ["Session volume", "300–500 m", "150–250 m"], ["Methods", "Flat, assisted and downhill", "Flat, uphill, resisted"],
             ["Strength focus", "FV curve, eccentric strength and fast SSC", "FV curve, plyometrics and hamstring strength"]]))
    b.append(f"<h2>Speed framework – general to specific {R(54)}</h2>" + table(["Layer", "Content"], [["Strength", "Functional hypertrophy, max strength, max isometric strength"],
             ["Power", "Explosive power, slow SSC plyometrics, MB throws"], ["Stiffness", "Max eccentric strength, fast SSC plyometrics, resisted &amp; assisted sprints"],
             ["Speed", "Acceleration sprints, max velocity sprints, curved sprints, multi-directional sprints, repeated sprint ability (RSA)"]], raw=True))
    b.append(f"<h2>Speed classification {R(63)}</h2>" + table(["Speed quality", "Key points", "Energy system", "Intensity", "Distance / time"], [
        ["Acceleration", "Forward lean in the initial drive phase before moving into an upright posture", "ATP-PC", "100%", "0–30 m"],
        ["Max velocity", "Upright; top speed held for only 2–3 s", "ATP-PC", "100%", "30–60 m"],
        ["Multi-directional", "Change(s) of direction, e.g. deceleration, lateral movement", "ATP-PC", "100%", "Up to 8 s of work"],
        ["Speed endurance", "Reach near-maximal velocity and hold it as long as possible", "ATP-PC (PCr power) / ATP-PC (PCr capacity)", "95% / 85%", "6–8 s / 9–15 s"]]) + "</section>")

    b.append(chapter("Chapter 7", "Energy system development (ESD)"))
    b.append(f"<p>Energy-system comparison: ATP-CP = 100 m sprint (Noah Lyles; “Ferrari”), anaerobic glycolysis = 400 m (Wayde van Niekerk; “BMW”), aerobic = 3,000–5,000 m "
             f"(Jakob Ingebrigtsen; “Toyota”) {R(65)}. Every movement needs muscle contractions, which need energy; the energy currency is <b>ATP</b>. Once ATP is used up the body "
             f"<b>resynthesises</b> it from other sources, and the method depends on the volume and intensity of exercise {R(66)}.</p>")
    b.append(f"<h2>Simple strategy – traditional ESD {R('67–70')}</h2>" + table(["", "ATP-CP (intensive)", "Anaerobic glycolysis (extensive)", "Aerobic (extensive)"], [
        ["Training stress", "Neurological high / metabolic low", "Neurological moderate / metabolic high", "Neurological low / metabolic high"],
        ["Classification", "PCr power (6–8 s) &amp; PCr capacity (10–15 s)", "Lactic power (15–30 s) &amp; lactic capacity (30–90 s)", "Aerobic power (90 s–3 min) &amp; aerobic capacity (3 min+)"],
        ["Intensity", "90–95% (power) / 85–90% (capacity)", "90%+ HRmax / 8+/10 on the Borg scale", "HR 70–80% (power) / 60–70% (capacity)"],
        ["Methods", "Repeated sprint training (RST)", "Intensive intervals &amp; small-sided games (SSG)", "Extensive intervals &amp; SSG"],
        ["Themes", "Linear &amp; multi-directional", "Linear &amp; multi-directional", "Linear &amp; multi-directional"],
        ["Work:rest", "1:5–1:10 (power) / 1:3–1:6 (capacity)", "1:1–1:3 (linear vs multi-directional)", "1:0.5–1:1"],
        ["Fitness test", "Phosphate decrement test (PDT)", "150 m shuttle test", "– (Bronco, see Chapter 8)"]], raw=True))
    b.append(note("Weeks 1 &amp; 2: keep the same session but increase the target distance of the runs. Weeks 3 &amp; 4: increase work duration (time) and again raise the target distance. "
                  "Goals: ATP-CP, hold speed for longer with quicker recoveries (e.g. 6 s → 8 s @ 95%); anaerobic, work longer (e.g. 30 s → 45 s @ 80%) while buffering lactate; "
                  "aerobic, work longer (e.g. 90 s → 3 min) using oxygen more efficiently.", "4-week progressive overload"))
    b.append(table(["Session", "Week 1", "Week 2", "Week 3", "Week 4"], [
        ["PCr power", "6 s sprint, 40 m, 3×6 @90–95%, rest 30 s / 5 min", "45 m, 3×6 @95%", "8 s sprint, 55 m, 3×4 @90–95%, 40 s / 5 min", "60 m, 3×4 @95%"],
        ["Anaerobic power", "30 s sprint, 190 m, 2×4 @85%, 90 s / 5 min (1,520 m)", "200 m (1,600 m)", "45 s sprint, 280 m, 2×3 @80%, 2 min / 6 min (1,680 m)", "290 m (1,740 m)"],
        ["Aerobic power", "90 s runs, 400 m, 2×3 @80% MHR, 90 s / 5 min (2,400 m)", "2×4 (3,200 m)", "3 min runs, 700 m, 2×3 @70% MHR, 2 min / 6 min (4,200 m)", "2×4 (5,600 m)"]]))
    b.append(f"<h2>Advanced strategy – the physical-preparation puzzle {R('71–80')}</h2><p>Five pieces: 1 HIIT fundamentals; 2 key markers &amp; profiling; 3 training methods; "
             "4 program goals; 5 planning &amp; periodization.</p>")
    b.append(f"<p><b>HIIT</b>: repeated bouts of high-intensity work above the lactate threshold, separated by low-intensity exercise or complete rest. Four sub-categories: long "
             f"(extensive) intervals, short (intensive) intervals, repeated sprint training (RST), small-sided games (SSG) {R(72)}.</p>")
    b.append(f"<p><b>Maximal lactate steady state (MLSS)</b>: the highest intensity that can be sustained without a continuous build-up of blood lactate (aka anaerobic threshold); "
             f"as % VO₂max: untrained 70–80%, trained 80–90% {R(74)}.</p>")
    b.append(asr_svg())
    b.append(f'<p class="small">Intensity continuum redrawn from the manual {R("73, 79")}. ST = sprint training; RST = repeated sprint training; MAS = maximal aerobic speed; MSS = maximal sprint speed; ASR = anaerobic speed reserve.</p>')
    b.append(f"<h3>Key markers {R('74–77')}</h3>" + table(["Marker", "Definition", "Assessment", "Formula / example"], [
        ["1 MAS", "Lowest speed at which VO₂max occurs (= vVO₂max)", "Bronco (multi-directional) or 1.5 km time trial (linear)", "MAS = distance ÷ time; Bronco 1,200 m in 4:25 (265 s) → 4.5 m/s × 3.6 = 16.2 km/h"],
        ["2 MSS", "Maximal speed over a 30–60 m sprint", "10–30 m flying sprint", "20 m flying in 2.1 s → 9.5 m/s × 3.6 = 34.2 km/h"],
        ["3 ASR", "Capacity difference between vVO₂max (MAS) and MSS", "Derived", "ASR = MSS (km/h) − MAS (km/h)"]]))
    b.append(table(["Class", "Bronco time", "MAS", "20 m flying time", "MSS"], [["Good", "&lt; 4:35", "Av. 4.5 m/s (16.2 km/h)", "&lt; 2.1 s", "Av. 9.5 m/s (35 km/h)"],
             ["Average", "4:35–4:50", "Av. 4.25 m/s (15.3 km/h)", "2.1–2.3 s", "Av. 9.1 m/s (33.5 km/h)"], ["Poor", "&gt; 4:50", "Av. 4 m/s (14.4 km/h)", "&gt; 2.3 s", "Av. 8.7 m/s (31.2 km/h)"]], raw=True))
    b.append(note("Athlete A: MAS 16 km/h, MSS 30 km/h, ASR 14 km/h. Athlete B: MAS 16, MSS 34, ASR 18. At 120% MAS (19 km/h, Eurofit 15:15) both run the same speed, which is "
                  "21.5% of A's ASR but only 16.5% of B's, so A works relatively harder. <b>Solution:</b> prescribe from the ASR, e.g. 15 s @ 100% MAS + 20% ASR → A 18.8 km/h, B 19.6 km/h "
                  f"{R('76–77')}.", "Why ASR matters"))
    b.append(f"<h3>Training methods {R('78–79')}</h3>" + table(["Method", "Prescription", "Worked example"], [
        ["Short interval – grouping (extensive)", "Eurofit 1:1 (15 s:15 s for 5–10 min) @ 110–120% MAS; session 3 × 5 min, 3 min rest; distance = MAS (m/s) × intensity × work (s)",
         "4.45 × 1.2 × 15 = 80 m. Groups at 120%: good 81 m, average 77 m, poor 72 m"],
        ["Short interval – individualized", "15:15 for 5–10 min @ 100% MAS + 15–20% ASR; 3 × 5 min, 3 min rest", "A: 4.5 + 0.75 = 5.25 m/s → 78 m; B: 4.5 + 1 = 5.5 m/s → 82 m"],
        ["RST (intensive)", "PCr power 6–8 s @ 90–95% MSS; 3 × 5 for 6 s @ 95%; work:rest 1:5 (30 s); distance = speed × 6 s − 5 m for acceleration",
         "A: MSS 8.3 m/s, 95% = 7.6 m/s → 45 − 5 = 40 m; B: 9.4 m/s, 95% = 8.9 m/s → 53 − 5 = 48 m"]]))
    b.append(f"<h3>Program goals – 4-week phases {R(80)}</h3>" + table(["Week", "Phase 1 long intervals", "Phase 2 short intervals (15:15)", "Phase 3 RST (PCr power)"], [
        ["1", "5 × 3 min @ 95% MAS", "2 × 5 min @ 110% MAS", "3 × 4 for 6 s @ 95%"], ["2", "2 × (3 × 3 min @ 95%)", "3 × 5 min @ 110%", "3 × 6 for 6 s @ 95%"],
        ["3", "2 × (3 × 3 min @ 100%)", "3 × 5 min @ 120%", "3 × 4 for 8 s @ 95%"], ["4", "2 × (4 × 3 min @ 100%)", "3 × 6 min @ 120%", "3 × 6 for 8 s @ 95%"]]))
    b.append('<p class="small">Phases 1 and 2 develop training volume and intensity; Phase 3 develops intensity.</p>')
    b.append(f"<h3>Planning {R('81–82')}</h3><p>Conjugate themes: preparatory (GPP, SPP) → competition (pre-competition, competition) → transition, with Extensive 1–3 and Intensive 1–3 running "
             "in parallel. ESD phases: aerobic (long intervals) → anaerobic (short intervals) → anaerobic (short intervals), alongside PCr capacity (RST) → PCr power (RST) → speed &amp; agility (ST).</p>")
    b.append(table(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], [["Strength (FB gym)", "Aerobic, long intervals (pitch)", "Active recovery", "PCr capacity RST (pitch)",
             "Hypertrophy (FB gym)", "Aerobic, long intervals (pitch)", "Rest &amp; recover"]], raw=True))
    b.append(table(["Game day", "GD+1", "GD+2", "GD−4", "GD−3", "GD−2", "GD−1"], [["Game", "Recovery", "Off", "HIIT (SSG)", "HIIT (short intervals)", "Speed", "Activation"]]))
    b.append('<p class="small">The game-week slide is labelled “pre-season” in the manual even though it shows a match week.</p>')
    b.append(f"<p><b>Summary {R(83)}:</b> plan conditioning by time of season; prioritize the energy system(s); apply the right method(s) and balance volume and intensity.</p></section>")

    b.append(chapter("Chapter 8", "Energy system testing"))
    b.append(table(["Test", "System", "Protocol", "Score", "Classification"], [
        [f"Phosphate decrement test (PDT) {R(85)}", "ATP-CP", "40 m linear sprints; 2 timing gates (start + finish; handheld digital timing is an alternative); 8 maximal sprints; 30 s passive recovery",
         "Fatigue index = % difference between fastest and slowest time (lower is better)", "0–6% good; 7–10% average; &gt; 10% poor"],
        [f"150 m shuttle test {R(86)}", "Anaerobic glycolysis", "6 × 30 s maximal runs, 30 s passive recovery; cones at 5, 10, 15, 20, 25 m; sprint to 5 m and back, 10 m and back … 25 m, continuing within 30 s; one marker per athlete; run as far as possible",
         "Total distance over 6 runs", "&gt; 740 m good; 700–740 m average; &lt; 700 m poor"],
        [f"Bronco test {R(87)}", "Aerobic", "5 continuous laps (1.2 km); 1 lap = 20 m and back, 40 m and back, 60 m and back (240 m); no break",
         "Total time (fastest possible)", "&lt; 4:45 good; 4:45–5:00 average; &gt; 5:00 poor"]], raw=True))
    b.append(note(f"Three Bronco band sets exist in the course: Phase 1 profile (good &lt; 4:30, average 4:30–4:45, poor &gt; 4:45) {src('P1 p.21')}; Phase 2 MAS classification "
                  f"(&lt; 4:35 / 4:35–4:50 / &gt; 4:50) {R(75)}; Phase 2 test page (&lt; 4:45 / 4:45–5:00 / &gt; 5:00) {R(87)}. Always state which one you use.", "Bronco bands differ", flag=True) + "</section>")

    b.append(chapter("Chapter 9", "Conjugate periodization"))
    b.append(table(["", "Linear model", "Conjugate model"], [["Athlete", "Novice", "Elite"], ["Qualities", "Prioritize 1 strength + 1 ESD quality", "Develop multiple physical qualities"],
             ["Load pattern", "“X-factor” manipulation of volume &amp; intensity", "Wave-like manipulation of volume &amp; intensity"]], raw=True))
    b.append(f"<p>Review: terminology (macro-, meso-, microcycle, training unit); periods (preparatory, competition, transition); themes extensive = volume (yellow), intensive = intensity (blue) {R(90)}.</p>")
    b.append(f"<h2>Westside Barbell methods {R('91–92')}</h2>" + table(["Method", "Definition", "Typical prescription"], [
        ["Maximal effort", "Lifting maximal or near-maximal loads", "1–3 reps at 90–100% 1RM"], ["Dynamic effort", "A non-maximal load at the highest attainable speed", "4–5 reps at 50–75% 1RM"],
        ["Repeated effort", "A non-maximal load for the desired reps or to failure", "5–20 reps, or more if to failure"]]))
    b.append("<p>Sessions: maximal-effort bench day and maximal-effort squat &amp; deadlift day (maximal + repetition method, heavy days); dynamic-effort bench day and dynamic-effort "
             "squat &amp; deadlift day (dynamic + repetition method, fast days). The training-week diagram puts the maximal-effort squat/deadlift on Monday and the dynamic-effort bench on "
             "Wednesday; it does not label the days of the other two.</p>")
    b.append(f"<h2>Training menu {R(93)}</h2>" + table(["", "Extensive (yellow)", "Intensive (blue)"], [
        ["Strength", "Corrective exercises (based on the MCS); prehabilitation (key areas of injury concern); strength endurance (work capacity); hypertrophy (myofibrillar vs sarcoplasmic)",
         "Max strength (peak dynamic vs peak isometric force); explosive power (strength-speed vs speed-strength); reactive power (slow vs fast SSC)"],
        ["Speed &amp; ESD", "Aerobic system (power vs capacity); anaerobic glycolysis (power vs capacity)",
         "ATP-CP (PCr power vs capacity); agility (change of direction vs evasion skills); acceleration (speed off the mark); max velocity (top-end speed)"]], raw=True))
    b.append(f"<h2>Phases {R(94)}</h2>" + table(["", "Phase A", "Phase B", "Phase C"], [
        ["Strength", "Hypertrophy &amp; correctives: work capacity, muscle mass, movement quality", "Max strength &amp; slow SSC: peak force, RFD", "Strength-speed &amp; fast SSC: maintain strength, power output, tendon stiffness"],
        ["ESD &amp; speed", "Aerobic &amp; glycolytic: VO₂max, lactate threshold, lactate buffering", "PCr power &amp; capacity: repeated sprint ability, linear &amp; multi-directional", "Speed &amp; agility: linear speed, multi-directional speed"]], raw=True))
    b.append(f"<h3>Weekly plans – weeks 1–3 progressive overload, week 4 de-load {R('94–95')}</h3>" + table(["Block", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], [
        ["Extensive 1", "Hypertrophy (full body)", "Anaerobic power &amp; capacity (pitch)", "MCS correctives &amp; core", "Aerobic power &amp; capacity (pitch)", "Hypertrophy (full body)", "Active recovery &amp; core", "Rest"],
        ["Intensive 1", "LB max strength &amp; slow SSC (complex)", "PCr power (pitch)", "Core &amp; stretch", "PCr capacity (pitch)", "UB max strength &amp; slow SSC (complex)", "Active recovery &amp; core", "Rest"],
        ["Intensive 2", "LB strength-speed &amp; fast SSC (contrast)", "Linear speed (pitch)", "Core &amp; stretch", "Agility (pitch)", "UB strength-speed &amp; fast SSC (contrast)", "Active recovery &amp; core", "Rest"]], raw=True))
    b.append(f"<p>Summary {R(96)}: understand the needs analysis and key physical qualities; apply conjugate periodization to better-trained athletes; create a plan and keep the goal the goal.</p></section>")

    b.append(chapter("Chapter 10", "Fast SSC plyometrics & RSI"))
    b.append(table(["Phase", "Drill", "Progressions / targets"], [
        [f"1 Fundamentals {R(98)}", "SL pogos (supported)", "Fully supported → fully supported &amp; toe up → half supported &amp; toe up"], ["1", "Pogos (5 m)", "Forward &amp; toe up → lateral (L &amp; R) &amp; toe up → backward &amp; toe up"],
        [f"2 Fast SSC jumps {R(99)}", "Drop jumps (guys 45 cm / girls 30 cm)", "GCT initial &lt; 0.25 s, progression &lt; 0.20 s; jump height (CMJ score); RSI initial &gt; 2.5, progression &gt; 3.0"],
        ["2", "Rebound hurdle jump (5–6 hurdles)", "Height: knee → mid-thigh → waist"], ["2", "Rebound standing long jump (10 m)", "Guys 3–4 jumps; girls 4–5"],
        [f"3 Fast SSC hops {R(100)}", "Single-leg hops", "SL pogos → alternate SL pogo &amp; tuck hop → rebound tuck hop → 10 m target (hop speed, hop distance)"]], raw=True))
    b.append(f"<h2>Reactive Strength Index (RSI) testing {R(101)}</h2><p>2–3 depth jumps at several heights (e.g. 15, 30, 45, 60 cm), recording jump height, contact time and RSI at each, "
             "builds a fast-SSC profile. If RSI is maintained or improves with drop height and contact times stay below 0.25 s, reactive strength is sufficient for that height. A drop in "
             "RSI or contact times above 0.25 s suggests a sub-optimal stimulus or excessive stress on the muscle–tendon system.</p>")
    b.append(table(["RSI", "Level", "Guidance"], [["&lt; 1.5", "Low", "Unprepared for moderate-intensity plyometrics; focus on max strength and slow SSC"],
             ["1.5–2.0", "Moderate", "Prepared for moderate-intensity plyometrics; begin with pogos and rebound jumps"], ["2.0–2.5", "Good", "Intensive plyometrics can be developed; progress to depth jumps"],
             ["2.5–3.0", "Excellent", "Progress to SL hopping and bounding"], ["&gt; 3.0", "World class", "Maintain elastic strength bilaterally and unilaterally"]], raw=True))
    b.append(note("The manual does not print the RSI formula. It is commonly calculated as jump height ÷ ground contact time (Flanagan &amp; Comyns, 2008, <i>Strength and Conditioning Journal</i> 30(5):32–38).", "Additional note (not course material)", flag=True) + "</section>")

    b.append(chapter("Chapter 11", "Agility training"))
    b.append(f"<h2>Agility framework {R(103)}</h2>" + table(["Branch", "Skill group", "Components"], [["Change of direction (COD)", "Physical skills", "Strength, power, speed, tendon stiffness"],
             ["Change of direction (COD)", "Technical skills", "Acceleration, deceleration, turning, lateral movement"], ["Cognitive response", "Perceptual skills", "Visual scanning, auditory scanning"],
             ["Cognitive response", "Decision-making skills", "Choosing from the movement skills acquired; speed of decision making"]]))
    b.append(f"<p><b>Coaching model {R(104)}:</b> COD technical skills linked with perceptual and decision-making skills, progressed through 1 <b>closed drills</b> → 2 <b>open drills</b> → 3 <b>game-simulation drills</b>.</p>")
    b.append(note("No agility technical model, drill descriptions or session variables are printed in the manual.", "Not in the manual", flag=True) + "</section>")

    b.append(chapter("Chapter 12", "Anaerobic glycolysis – lactate sessions"))
    b.append(f"<p>Planning in 3 steps {R(106)}: 1 training method (an intensive interval session on the pitch, or an off-feet lactate session in the gym); 2 power vs capacity adaptation (or both); "
             f"3 a 4-week progressive overload plan. Adaptation: <b>metabolic</b>; theme: yellow; primary focus: volume &amp; intensity; method: intensive intervals {R(107)}.</p>")
    b.append(table(["Variable", "Lactate power", "Lactate capacity"], [["Intensity", "80–85%", "70–80%"], ["Duration of work", "15–30 s", "30–90 s"], ["Reps per set", "3–6", "3–4"],
             ["Sets per session", "2–3", "2–3"], ["Rep recovery (rest:work)", "1–5:1", "1–3:1"], ["Set recovery", "5 min", "5 min"], ["Session recovery", "48 h", "48 h"], ["Sessions per week", "1–2", "1–2"]]))
    b.append(note(f"The ESD lecture gives intensity as 90%+ HRmax / RPE 8+ and work:rest 1:1–1:3 {R(68)}, while this page gives 80–85% / 70–80% (unit not stated) {R(107)}.", "Different values in the manual", flag=True) + "</section>")

    b.append(chapter("Chapter 13", "Athlete case study"))
    b.append(table(["Step", "Data"], [["Profile", "20-year-old male; semi-professional; training age 2 years; right wing; 180 cm; 75 kg; hard-working and motivated"],
             ["Program profile", "Goals: improve speed, power and fitness; repetitive hamstring strains; off-season; 4 weeks; 4–5 sessions/week; 75–90 min/day"],
             ["Needs analysis", "Primary: linear speed (acceleration), agility, speed endurance (ATP-CP). Secondary: power (reactive strength), aerobic fitness. Injury: hamstring strains, mainly right leg"],
             ["Movement screen", "MCS overhead squat 4/12 (average); ROM: tight hamstring, tight piriformis, reduced ankle mobility"],
             ["Fitness tests", "Weight 75 kg (good); skinfold sum of 4 = 28 mm (good); CMJ 35 cm (average); 0–10 m 1.78 s (poor); back squat 1.2 × BW (average); bench press 0.9 × BW (average); chin ups 9 (average); Bronco 4:45 (average); PDT 12% (poor)"]]))
    b.append(f"<p>Group tasks {R(111)}: choose the training theme (yellow vs blue); choose the physical qualities; write a weekly schedule; write a week-1 gym session and a week-1 pitch session. "
             "The manual gives no model answer.</p>")
    b.append(note("These good / average / poor labels describe the case-study player; the manual does not present them as general norms (except PDT, which matches the test page).", "Context", flag=True) + "</section>")

    b.append(chapter("Chapter 14", "References & unclear points"))
    b.append("<h2>Research cited in the Phase 2 manual</h2>" + table(["Citation as given", "Used for"], [["Bauer et al. (2019)", f"Definition of complex training {R(32)}"],
             ["Dobbs et al. (2015)", f"Definition of contrast training {R(33)}"], ["Docherty &amp; Hodgson (2007)", f"Optimal intra-set recovery in a potentiated state {R(33)}"],
             ["Chiu &amp; Barnes (2003)", f"Stronger athletes reach PAP earlier {R(33)}"], ["Seitz &amp; Haff (2016)", f"3–4 min intra-complex rest appears optimal {R(33)}"]], raw=True))
    b.append(f"<p>Recommended reading: the same 17 titles as Phase 1 {R(113)} (see the Phase 1 summary).</p>")
    b.append("<h2>Unclear points and inconsistencies</h2>" + ul([
        "Bronco bands: three different sets across the course (Chapter 8).", f"Mid-thigh pull 80%+ (table) vs 100%+ (diagram) {R(21)}; high pulls 70–80% here vs 60–80% in Phase 1.",
        f"ATP-CP: 10–15 s, 85–90% capacity, work:rest 1:5–1:10 / 1:3–1:6 {R(67)} vs Phase 1's 9–15 s, 85–95%, 5–10:1 / 4–6:1.",
        f"Lactate intensity and work:rest differ between {R(68)} and {R(107)}.", f"“3–4 mins vs 1–2mins” and the handwritten notes on {R(34)}.",
        f"“PROM” not expanded {R(19)}; “0–3m” on {R(31)} is presumably 0–30 m.",
        "Not printed: snatch technical model, agility technical model and drills, dribble-series drill card, protocols for power clean (watts), squat jump (m/s), SL CMJ, SL hops and the trunk extensor endurance test, the Extensive 2/3 and Intensive 3 weeks, and the RSI formula."]))
    b.append("</section>")
    return page("OSM – Phase 2 Summary", "".join(b))


def build_cover():
    return cover("EPI NCSC · STUDY & REVISION RESOURCE", "Phase 2<br>Summary",
                 "Strength &amp; power · VBT · snatch · complex &amp; contrast training · max velocity · ESD &amp; HIIT · energy system testing · conjugate periodization · fast SSC · agility · case study",
                 "Prepared for Coach Osama · OSM – Osama Strength Method · Source: EPI NCSC Phase 2 course manual (Elite Performance Institute, January 2026). "
                 "Page references [P2 p.xx] point to the manual's printed page numbers. For personal study use.")
