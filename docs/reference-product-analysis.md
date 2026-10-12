# Reference Analysis — 5 fitness Reels (October 2026)

**What the references are:** five vertical social videos from other creators. They show an **editing style**,
not app screens, so there is no app UI or app business logic to reverse-engineer. The "product" here is
the **video production system**: how the videos are structured, captioned, titled and paced. These findings
are applied to the OSM video studio in this repo.

**How they were inspected:** I probed each file's technical specs. I made frame contact sheets every 1.5–3.8 s
and looked at full-resolution key frames. Cut points come from FFmpeg scene detection. Loudness was measured
with EBU R128. Speech was transcribed locally (faster-whisper `medium`). Transcripts are machine drafts: they
contain recognition errors and were used only to understand structure. Nothing below quotes them as exact.

Confidence tags: **Observed** (seen or measured directly) · **Inferred** (reasoned from evidence) · **Unknown**.

## 1. Inventory

| # | File (short id) | Length | Spec | Speech | Type |
|---|---|---|---|---|---|
| A | `81445a0c` | 53.1 s | 720×1280, 30 fps | Egyptian Arabic. **On-screen captions in English** | Sponsored equipment explainer (Intenza shoulder press) |
| B | `ef3ac602` "Sweat now.. shine later" | 47.1 s | 720×1280, 30 fps | None (music only) | Beach partner-workout montage |
| C | `a17bb6d4` | 57.1 s | 716×1278, 30 fps | Egyptian Arabic, no captions | Sponsored creatine explainer, mostly AI/3D-generated anatomy visuals |
| D | `3dbcd01f` (@mahmoudfoodaa, leg day) | 151.2 s | 720×1280, 30 fps | Egyptian Arabic with Arabic captions | "Train with me" full leg workout |
| E | `b84249e1` (@mahmoudfoodaa, reps) | 90.1 s | 720×1280, 30 fps | Egyptian Arabic with Arabic captions | Talking-head education (rep ranges / effort) |

All five are 9:16 at **720p**. Integrated loudness is **−14.1 to −14.6 LUFS** in all five (Observed). This confirms
−14 LUFS as the platform-appropriate target used by the studio.

## 2. Per-video breakdown (timestamps observed)

### A — Equipment explainer (53 s, cuts every ~2.5–3 s)
- **0:00–0:04 Hook:** a problem statement to camera ("your shoulder gets injured even with correct technique"), in a staged
  clinic set with arm sling props and a holographic shoulder graphic. English caption, 1–4 words.
- **0:04–0:12 Twist and demo setup:** "the problem is the machine". A coffee cup is placed on the machine as a stability test.
- **0:13–0:20 Product title:** a large stacked 3D title "INTENZA SHOULDER PRESS" in brand orange, composited behind the machine.
- **0:20–0:31 Mechanism visualisation:** a pulley close-up with a glow, a **battery-meter graphic** filling as resistance increases,
  **neon line tracing** over the machine's movement path, and a **two-angle split screen** (0:28–0:31).
- **0:31–0:34 Result headline:** two lines, "MORE TENSION ON THE MUSCLE / LESS STRESS ON THE JOINT", with one coloured keyword per line
  (green / red).
- **0:34–0:40 Proof callback:** the coffee didn't spill.
- **0:40–0:48 Range extension:** a sales pitch for the other machines, then the presenter in an "engineer" costume (hard hat, hi-vis) with a HUD graphic.
- **0:48–0:53 Close:** a one-line moral ("when the engineering is right, the muscle gets tired, not the joint").
- Captions are white, bold, geometric sans, 1–4 words, centred at about 62% of frame height, with no plate (Observed).

### B — Beach montage (47 s, about 40 cuts, median shot about 1–1.5 s)
- No dialogue. Music-driven cuts (Inferred: cuts land on musical beats; not measured).
- Varied angles: low-angle hero shots, close-ups of sweat and muscle, wide shots of drills, and a wipe through an agility pole at 0:30.
- Teal/orange natural grade. There are no captions, titles or graphics at all.
- It ends on partner camaraderie (hug and splash). An emotional close instead of a CTA.

### C — Creatine explainer (57 s)
- **0:00–0:03:** the presenter takes the product, then a hard transition into a **3D / AI-generated** anatomical journey
  (mouth → stomach → intestine → blood → muscle → mitochondria, with "ATP" labels).
- **0:30–0:33, 0:40–0:47:** real gym footage (preacher curl) as proof of the effect.
- **0:48–0:57:** the presenter in a locker room holds the product. **Sponsor URL and promo code** in a yellow glow.
- Voice-over only, with no captions. Scientific claims are spoken over generated imagery. It ends on "99% of people…".

### D — Leg-day walkthrough (151 s)
- **0:00–0:05 Hook:** "If you asked me for the best complete leg workout…", with a giant "LEG WORKOUT" title on the wall behind the presenter.
- **Repeated exercise blocks** (about 0:05–2:05): each opens with the presenter introducing the exercise, then a **large exercise-name title**
  (LEG EXTENSION, HACK SQUAT, LEG CURL, LUNGES, LEG PRESS, PLANK) in white caps with a **glow, set over the lower third, revealing
  letter by letter**. Then the movement is shown with spoken coaching (sets, weight choice, tempo, depth).
- **Small FX:** a dust puff on lunge steps, a light burst on a Smith-machine plate, studio practical lights in frame.
- **2:08–2:31 Close:** like and share, comment what you want next, **DM for coaching prices**.
- Arabic captions: white bold, 1–3 words, about 62% height, no plate. Low-key teal-blue grade with cool shadows.

### E — Rep-range education (90 s)
- A seated talking head across the whole video. Every 4–12 s it **cuts away to an inset B-roll card** (rounded corners, over a
  blurred, darkened backdrop) or a **full-screen kinetic number/keyword**: "12 عدة", "8 عدات", "15 عدة",
  "بتتعب في العدة 10", "العدة السلبية", "الفشل العضلي", "النوم الكويس".
- Graphic accents: a muscle-silhouette icon, chevron arrows behind the presenter, cyan light streaks.
- Arabic captions: 1–2 words, bold white, about 62% height.
- Numbers are the visual anchors. Each key number the coach says appears large on screen as he says it (Observed at 0:13, 0:22, 0:29).

## 3. Cross-video patterns (what makes them work)

| Pattern | Evidence | Confidence |
|---|---|---|
| Hook in the first 2–4 s: a question, a problem, or a contrarian claim | A, C, D, E | Observed |
| Short-phrase captions (1–3 words) that change fast, centred, about 60–65% height, no plate | A, D, E | Observed |
| **Exercise name as a big title** over the movement | A (product), D (every exercise) | Observed |
| **Big number / keyword callouts** restating the spoken number | E | Observed |
| **Inset B-roll card** over a blurred backdrop while the voice continues | E | Observed |
| Split screen for two angles of one movement | A | Observed |
| A cut-away every 3–10 s in talking-head videos; 1–2 s cuts in music montages | all | Observed (scene detection) |
| Low-key, cool-shadow grade with practical lights in frame | A, D, E | Observed |
| Mastered to about −14 LUFS | all | Measured |
| Captions translated to another language (A: Arabic speech, English text) | A | Observed. **Conflicts with OSM's "verbatim captions" rule** |
| AI/3D-generated anatomy imagery | C | Observed. **Conflicts with OSM brand rules** |
| Neon tracing and particle/glow FX | A, D, E | Observed. **Limited by OSM's effects budget** |

## 4. Contradictions and differences between videos
- **Captions:** A shows translated English captions, D and E show same-language Arabic captions, and B and C have none. The OSM choice is same-language,
  verbatim captions. A translated second track is only possible if it is human-checked (never machine-translated, per the brand book).
- **Effects density:** A and C are effects-heavy ads. D and E are restrained education. OSM's personality (calm, premium, not flashy) matches D and E.
- **CTA:** D ends on "DM for prices", C on a promo code, A on a moral, B on emotion. OSM's book forbids prices and payment steps in app-facing
  content and prefers "Start with OSM".

## 5. Unknowns
- Which editing software the creators used, and whether title glows are tracked or 2D (it doesn't matter for OSM).
- The exact fonts in the references (geometric bold sans). OSM uses its own brand fonts regardless.
- Whether music in A, D and E is licensed library music (only light underscoring was heard; B is a vocal track).
- Whether B's cuts are beat-matched (Inferred, not measured).
