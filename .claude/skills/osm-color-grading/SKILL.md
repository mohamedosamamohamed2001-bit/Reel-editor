---
name: osm-color-grading
description: Premium cinematic colour grading standard for every OSM reel (Coach Osama 2026-10-31). Use whenever footage is edited, rendered or exported in this repo, or colour, grade, LUT, saturation, contrast, skin tone, white balance, yellow/dull/washed-out footage, HDR/HLG or scopes come up.
---

# OSM colour grading

Every new reel is graded before its final export. Never deliver dull, yellow, flat or washed-out footage.

1. **Read `docs/COLOR_GRADING.md`.** It covers the root cause, the 5-pass pipeline, the checks and the limits.
2. **Probe each source** (`ffprobe` colour_transfer). His iPhone footage is HLG/BT.2020. It must go through the HDR → BT.709 conversion, never plain `format=yuv420p`.
3. **New edits:** `"plates": {"grade": "auto", ...}`. Every clip is then graded from its own measured pixels (white balance and tint first, then contrast, gamut-safe saturation, separation, skin protection, verification). A per-clip `"grade"` overrides only for screen recordings or an approved look.
4. **Before the full render:**
   - `.venv/bin/python tools/grade.py SRC --in A --out B --compare DIR`, and `--sample DIR` for a synced 5–10 s before/after.
   - Look at the stills and scopes at full resolution.
   - If anything still looks dull, yellow or washed out, fix it before going on. A higher number alone doesn't count as approval.
5. **During the render,** each clip prints `grade … PASS` or `CHECK [...]`. The report is in `work/grades.json`. Every CHECK must be fixed or explained in the delivery report.
6. **Never grade graphics.** Captions and overlays are composited after the plates. Still sample the caption bar (#56A0FB).
7. **Don't re-grade delivered videos unless he asks.** Keep resolution, frame rate and audio untouched.
8. **Report:** colourfulness, neutral cast, skin and clipping before → after for each clip, plus what was looked at.
