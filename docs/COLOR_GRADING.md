# Premium cinematic colour grading: the permanent Reel Studio standard

Adopted from Coach Osama's directive of 2026-10-31. Every new reel is graded before its final export.
- **Tools:** `tools/grade.py` does the grading; `tools/scopes.py` measures the result.
- **Hook:** `plates.grade: "auto"` in `edit.json` (render_edit).
- **Skill:** `.claude/skills/osm-color-grading`.

## 1. Root cause of the dull, yellow exports (measured)
- **Most of his footage is iPhone HDR:** HLG transfer with BT.2020 primaries, and Dolby Vision 8.4 on top.
- **The old default** (`plates.grade: "format=yuv420p"`, 2026-10-20) read those HLG/BT.2020 code values as if they were BT.709. That desaturates everything, flattens contrast and biases neutrals and skin toward yellow.

**On b7-1 (blue shirt, gym):**

| Metric | Old pipeline | Correct HLG → BT.709 decode | After the full grade |
|---|---|---|---|
| Colourfulness | 35 | 83 | 79–81 |
| Neutral b* (yellow cast) | +4.4 | | +1.7 |
| Skin hue | 57–76° (yellow) | | 36–51° (natural) |

**Validation against the camera itself:** the same red-orange tank, filmed by the phone in plain SDR (IMG_7129), measures hue 41° / chroma 58.
- New HDR decode: 47° / 55, a match.
- Old pipeline: 64° / 40, yellow and washed out.

**SDR sources** (finished 720p exports, 4K SDR takes) had smaller problems, so the grade does less there:
- mild yellow or magenta casts;
- grey blacks (p0.5 luma 10–16);
- low chroma.

## 2. The pipeline (`tools/grade.py`, one grade per clip range, measured on 5 frames of that range)
| Pass | What it does | How it decides |
|---|---|---|
| 0 Input | HLG/PQ BT.2020 → BT.709: `zscale` to linear at 203-nit reference white, `tonemap=mobius` (desat 0, highlight roll-off), BT.709. SDR: correct input matrix (709/601). | from ffprobe colour tags |
| 1 Technical | White balance + tint: RGB gains from near-neutral pixels (70 % of the cast, 85 % if strong; gains normalised so no channel is pushed up, which means no new clipping). Levels: grey blacks pulled to ~7; dim highlights lifted toward 242. | neutral-pixel RGB means, luma percentiles |
| 2 Contrast | One master curve: levels + filmic S (strength from the shot's L* RMS contrast) + highlight shoulder (identity again at 92 %, so the roll-off is kept). | measured contrast |
| 3 Saturation | `vibrance` (lifts weak colours, protects saturated ones): the strongest level that stays gamut-safe. That means no new channel clipping, chroma ≤ 30, and skin within limits. Correctly decoded HDR often needs none. | iterated measurement |
| 4 Separation | Yellows −12 % (no yellow contamination), reds −3 %, blues/cyans +8 % (dropped automatically when saturated blues already sit at the limit). Then a white-balance refinement measured on the graded frames (up to 2 iterations). Then skin protection: red+yellow hue nudge and trim until skin chroma ≤ 31 and hue is in 30–65°. Then a richness top-up outside skin hues (greens, cyans, blues, magentas) when skin protection held the gain back. | measured skin from YuNet face boxes |
| 5 Verify | Checks: neutral \|a*\|,\|b*\| ≤ 2.5; no new luma clipping; no new channel clipping; no crushed blacks; colourfulness ≥ 1.25× the old pipeline (≥ 1.1× when the old image carried a strong cast, because removing a cast lowers that number legitimately); chroma ≤ 32; skin in range. | report in `work/grades.json` |

**Adaptive by construction:** every clip gets its own numbers from its own pixels.
- Bright gym: clean whites, richness added.
- Dark or night: no shadow crushing.
- Blue-lit set: the cast is neutralised in the whites, the blue practicals stay blue.
- Saturated wardrobe: no clipping push.
- Skin: always protected.

**Never graded:** captions, titles, overlays and brand graphics. Remotion composites them after the plates. Measured: the caption bar was #569FFA (= #56A0FB after H.264) with and without the grade. Screen-recording cards aren't graded either.

**No LUT is used anywhere in the studio.** Nothing to inspect or stack.

## 3. Using it
- **New edits:** set `"plates": {"grade": "auto", "sharpen": "cas=strength=0.22"}`. This is the template default. A per-clip `"grade"` still overrides (for example, a screen recording or an approved look).
- **Before the full render:**
  - `.venv/bin/python tools/grade.py SRC --in A --out B --compare DIR` writes before/after stills with scopes (waveform, RGB parade, vectorscope, histogram).
  - `--sample DIR` writes a synced before/after video (side by side + split wipe) for 5–10 s.
  - Look at them at full resolution, not just the numbers.
- **Run `.venv/bin/python tools/scopes.py FILE --t T --out DIR`** for metrics and the scope sheet of any frame.
- **QA:** every `"grade": "auto"` clip writes its checks to `work/grades.json` and prints PASS/CHECK during the render. A CHECK must be looked at and fixed or explained before delivery.
- **Delivered videos are not re-graded unless he asks.** Their edits keep their existing grades; the shared presets (`_b7`, `_tips`, …) are unchanged.

## 4. Validation (2026-10-31, real footage, 10 shots / 8 sources)

**HLG gym, night event, studio set and SDR exports: all 10 pass every check.**

| Shot | Colourfulness (old → new) | Neutral b* (old → new) | Skin (hue°/chroma) |
|---|---|---|---|
| b7-1 blue shirt (2 ranges) | 36 → 79 / 35 → 81 | 4.6 → 1.7 | 46/31, 36/29 |
| gym-1 teal top | 22 → 40 | 1.9 → 0.6 | 28/25 |
| hyrox night SkiErg | 28 → 44 | 3.0 → 1.0 | 40/31 |
| tip-1 | 19 → 37 | 2.6 → 1.3 | 36/31 |
| gym-2 | 18 → 35 | 0.5 → −1.1 | 42/31 |
| r1 (SDR 4K, blue/magenta set) | 60 → 75 | −5.9 → −1.8 (a* 4.1 → −0.6) | 30/26 |
| c5-legday (SDR export) | 26 → 33 | 1.1 → 0.5 | 47/32 |
| n4-pulldown (SDR export) | 32 → 41 | 1.4 → 0.0 | 34/31 |
| 7129 (SDR night) | 34 → 42 | 3.9 → 0.3 | 38/31 |

**End to end through `render_edit`** (8.9 s, b7-1 footage, captions on):
- All render QA passes: 1080×1920, 30 fps, −14.2 LUFS, −1.9 dBTP, 267 frames in both versions.
- Synced before/after videos and scopes are in `deliveries/grading_2026-10-31/`.
- Frame metrics (before → after):
  - colourfulness 40 → 76
  - chroma 11 → 19
  - neutral b* 4.6 → 2.0
  - black p0.5 7.6 → 4.2
  - skin hue 76° → 51°
  - luma clipping 0 → 0
- Fixtures: `projects/_grade_test` (auto) and `projects/_grade_test_before` (old grade). Sources are hard links.

**Problems found and fixed while testing:**
- `vibrance` pushed saturated blues to the channel limit (0.9 % → 13.9 % clipped). The saturation search is now gamut-safe.
- The skin trim only covered reds, while skin at 46° sits between red and yellow. It now covers both.
- Removing a cast lowers "colourfulness". The richness check is now cast-aware.
- Skin protection could hold the overall gain back. A non-skin top-up was added.

## 5. Limits
- **Dolby Vision RPU metadata isn't used.** HLG is the base layer; the conversion follows the HLG standard (203-nit reference white).
- **Skin metrics need a detected face** (YuNet). Shots without a face rely on the neutral, clipping and chroma checks.
- **The grade is per clip range,** not per frame. A clip whose light changes a lot inside it should be split into separate clips in the edit.
- **Render cost:** about 20–40 s of analysis per clip, cached in `work/grades.json`. The plates take longer than with the old plain grade because of the 16-bit processing.

## Fix log
- 2026-11-01, g9: the tone curve is applied with `curves=...:interp=pchip`. The default natural cubic spline can overshoot between a
  black point near 0 and the next knot, and the overshoot wrapped into false colours (found on a stock bench-press clip in
  `projects/2026-11-01_voiceover2`; the numeric checks still said PASS). pchip is monotonic, so it cannot overshoot.
