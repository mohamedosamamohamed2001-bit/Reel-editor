# Main footage analysis: `v3.mp4`

## Technical (measured)
- 3840×2160 (16:9), 29.97 fps, H.264 Constrained Baseline, 26.41 s, AAC 48 kHz stereo. sha256 `ec5cf4de…4a82a`.
- **One static camera, one continuous take.** Medium shot of Coach Osama at a white desk. Bright, colourful set (brick wall,
  warm practical spot, dartboard, pink/cyan shelves), with **an OSM poster on the wall** at about 32–40% of the width.
- Face at about 50% across and 30% down. Hands stay central. White T-shirt (affects caption legibility).
- Audio is clean: noise floor about −47 dB, RMS about −21 dB, no clipping. Speech is fast and nearly continuous. The only real pause
  is 8.59–8.89 s. No noise reduction needed.

## Transcript (faster-whisper large-v3, vocabulary-guided; times in source seconds)
| Time | Speech |
|---|---|
| 0.05–2.65 | عايز تجرب OSM قبل ما تشترك معايا؟ |
| 2.65–5.93 | في OSM هخليك تجرب التمرين معايا اسبوع فري، |
| 5.93–8.43 | وكمان عاملك حاجة فري هتساعدك. |
| 8.43–10.45 | ادخل جرب **القبل(?)** مدة اسبوع، |
| 10.45–12.31 | وشوف الميثود بتاعتي بنفسك. |
| 12.31–14.67 | وانا كمان عامل **معادلة(?)** اسمها **Calories(?)** Calculator، |
| 14.67–17.43 | ادخل جربها for free، اكتب كل بياناتك، |
| 17.43–21.65 | وهتعرف احتياج جسمك سواء عايز تزيد، او تخس، او **تحافظ(*)** على وزنك. |
| 21.65–25.35 | **وجرب(*)** الوركاوت بتاعتك، وشوف النظام، وبعدها قرر. |

(?) = low confidence or uncertain. (*) = corrected from the model's output ("تتحافظ" → "تحافظ", "واجرب" → "وجرب").
**I can't listen to audio, so Coach Osama must confirm these by ear.** "القبل" is inside the section that was cut.

## Content
- **Message:** try OSM before subscribing. A free week of training with Coach Osama, plus the free Calorie Calculator
  that tells you your body's needs for gaining, losing or maintaining. Try it, see the system, then decide.
- **Strongest opening:** the first line is already a direct question to the viewer → used as the hook.
- **Repetition:** 5.93–10.45 restates what comes before and after it ("عاملك حاجة فري" ≈ "عامل معادلة اسمها…",
  "جرب … اسبوع" ≈ "اسبوع فري"). Cutting 6.06 → 10.58 (both inside real silences) keeps every idea and reads as
  "…اسبوع فري، وشوف الميثود بتاعتي بنفسك."
- **B-roll opportunity:** 13.4–21.6 describes the calculator step by step (open it → enter your data → see gain/lose/maintain).
  The screen recording shows exactly this, so it is the B-roll.
- **Keep clean:** the closing line (21.65–25.70) returns to the speaker for the decision moment.

## Brand and claims flags
- He states the **trial length ("اسبوع فري")**. CLAUDE.md says not to *state* the trial length until the backend rule is confirmed.
  These are Coach Osama's own words, so they stay in audio and verbatim captions. **No graphic emphasises it. Confirm the 7-day trial is live before posting.**
- "قبل ما تشترك" mentions subscribing, but **no prices or payment steps** appear. It's fine for Instagram. Don't use this cut inside the iOS app.
- He says the calculator is free ("for free"). That is his claim, kept verbatim. Confirm it matches the live access rules.

## Final duration
21.18 s of speech + 2.5 s end card = **23.7 s**.
