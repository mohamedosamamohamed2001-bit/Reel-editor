---
name: osm-motion-design
description: OSM motion-design standard (Spec 1 3D gallery + Spec 2 showreel, adopted permanently by Coach Osama). Use in EVERY video, reel, motion graphic, title, transition, data/number moment, intro/outro, sting or 3D request in this repo, at blueprint/storyboard, animation and QC stages, even when motion design is not mentioned.
---

# OSM motion design

These capabilities apply to every Reel Studio production automatically.

1. **Read `docs/motion/MOTION_SYSTEM.md`.** It holds the principles, the OSM brand mapping, the trigger table, the precedence rules and the QC steps. The original specs are kept verbatim next to it.
2. **Blueprint (`blueprint.md`):** add a `## Motion plan` section.
   - Go through the transcript beat by beat with the trigger table (section 5) and decide, with judgment, which techniques serve the content.
   - Name the concept or signature moment in one line, and storyboard each motion piece beat by beat.
   - "No motion piece here, because …" is a valid answer and must be written.
   - Never force a technique in. The footage stays the subject. Locked OSM rules win (section 6).
3. **Build:**
   - A motion piece is one HTML file with `window.ready` and `window.seek(t)`. Start from `motion/pieces/osm_sting/piece.html` for 2D, or `motion/pieces/gallery3d_test/piece.html` for three.js.
   - Use `/osm/motion-core.js` (= `studio/src/lib/motionCore.ts`) for springs, expo easing, the beat grid, seeded `rand`, `motionBlur`, `cameraAt` (one named move per shot), `cssWorld`, `morph`, `countUp` and `frameTime`.
   - Remotion components import the same module from `../lib/motionCore`.
4. **Stills first:** run `node tools/seek_render.js PIECE.html DIR --beats 120` and look at `DIR/sheet.jpg`. Fix anything flat, cluttered, off the beat, overlapping, hard to read, or on or above his head.
5. **Render:** run `node tools/seek_render.js PIECE.html OUT.mp4 [--audio]`. Use `--audio` only for standalone stings; reels get their sound from the studio mix. Then put the MP4 into the edit as a clip.
6. **QC:**
   - `python3 tools/motion_qc.py OUT.mp4 --bpm 120 [--loop]` must pass, and look at its `beats.jpg`.
   - `node tools/seek_render.js PIECE.html - --determinism` must pass.
   - Then the normal reel QA: `qa_render.py`, `head_check.py` and the brand checklist.
7. **Report:** which techniques were used and why, which were considered and rejected, and the QC numbers.
