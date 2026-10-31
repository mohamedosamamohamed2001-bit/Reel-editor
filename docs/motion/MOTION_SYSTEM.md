# OSM motion system

**Sources:** the two specifications Coach Osama asked to be adopted permanently (2026-10-31). They are kept verbatim in this folder:
- `SPEC_1_PROMPT_MOTION_3D_GALLERY.md`: the 3D gallery. As he provided it, it also ends with the showreel brief.
- `SPEC_2_MOTION_SHOWREEL.md`: the showreel.

This file holds what they teach, how it maps onto the OSM brand, where it's implemented, and how it's checked. Locked OSM rules still win wherever they conflict (see section 6).

## 1. What the specs teach
**Story and structure**
- **One signature moment, and build everything toward it.** In Spec 1 it's the pull-back that resolves into the wordmark. Name the concept in one line before building, and storyboard beat by beat.
- **Every shot is made out of the previous one.** Shapes, type and colour transform into the next scene; never cut or crossfade between scenes inside a motion piece.
- **Range with an equal share of time:** kinetic type → shape morph → data/UI → 2D-to-3D → end title. The first bar is the hook; the last full bar is the strongest moment; the final half bar is the end title. The last frame matches the first, so it loops.
- **Rhythm:** 120 BPM, something happens on every beat, and no hold longer than half a second.

**Camera**
- A film camera, not orbit controls.
- One named move per shot: dolly, crane, orbit, push-in or rack focus, eased in and out.
- One consistent camera language for the whole piece.
- The camera never passes through geometry.

**Physics**
- Things react to each other: what's hit moves, what's near lights up.
- Motion is driven by springs, simple physics or exponential easing, all as functions of time.
- Never linear tweens, never bouncy easing.
- Blur follows speed and direction on fast moves only.

**Light and material (3D)**
- Key, fill and rim lights with soft shadows.
- An environment map for reflections, and fog for depth.
- Physically based materials with varied roughness, and ACES tone mapping.
- Nothing may look like a default material.

**Determinism**
- Every frame is computed from time: seeded randomness, no clock, no timers, no CSS animations, no state carried between frames.
- So a preview equals the render, and any frame can be rendered in any order.

**Process**
- Render one frame per beat or shot first, and look at it.
- Fix anything flat, aliased, clipping, cluttered, off the beat, overlapping or hard to read.
- Only then do the full render.

**Banned:**
- default materials or lighting
- floating text labels
- glows
- a slowly spinning object as the whole idea
- tech-demo looks
- particle bursts
- lens flares
- camera shake
- RGB split
- crossfades
- generic gradients
- bouncy easing
- holds over 0.5 s
- anything that looks like a template

**Gotchas:**
- Set the shadow bias, or shadows get striped acne.
- Keep the near and far planes tight, or distant surfaces flicker.
- Seed every random number.

## 2. Rules learned while building and testing it (2026-10-31)
- **An impact must start fast.** A critically damped spring starts at rest, so a "hit" on a beat is invisible for the first frames. Use `expoOut` (or a spring with initial velocity) for impacts; springs for settles.
- **A travelling wave needs a near-constant speed** (sine ease). `expoInOut` crosses the visible area in about 0.2 s and is never seen. Derive each element's reaction time from the same curve.
- **Discrete content changes once per frame.** Counters and swapped text use `frameTime(t)`, or the subframe blur ghosts two numbers on top of each other.
- **CSS 3D:** every wrapper between the world and a 3D object needs `transform-style: preserve-3d`, or that branch is flattened (that's what hid the extruded column faces). A top face is `rotateX(-90deg)` from the top edge; side faces are `rotateY(±90deg)` from their edge.
- **The camera model** is a film camera aimed at a target. At the default camera the z = 0 plane renders 1:1, so a 2D layout and its 3D continuation are the same pixels, and the 2D-to-3D hand-off is invisible. Crane = pitch (+ looks down), orbit = yaw, push-in = z.
- **Hand-offs between techniques:** at the hand-off frame, the outgoing element (an SVG morph) and the incoming one (DOM columns) must be pixel-identical. Swap them on that frame. It isn't a cut.

## 3. OSM adaptation
| Spec says | OSM uses |
|---|---|
| Geist / Inter / one display face | Inter (English: Inter, Black Italic caps for titles); IBM Plex Sans Arabic 700 for Arabic; Barlow Condensed for numbers |
| black & white + one orange accent | Night `#0A0F16` / White + **Core Blue `#56A0FB`** as the one accent (copper `#C9935F` only for earned/reward moments) |
| soft daylight, white space (3D) | light neutral studio (`#E4E7EB`) for 3D scenes, or Night for 2D brand pieces; never a generic gradient |
| video posters on cards | his own approved stills / reel frames only (never AI imagery, never people other than him without consent) |
| wordmark + URL end title | the OSM wordmark (raster, `mix-blend-mode: lighten` on Night) or "OSM / OSAMA STRENGTH METHOD" set in Inter; no prices, no trial length |
| 1920×1080 | 1080×1920 for Reels (both supported: `--size`) |

## 4. Where it lives
| Capability | Implementation |
|---|---|
| Time-based math: springs (closed form), expo easing, beat grid, seeded `rand`, `motionBlur`, named camera moves (`cameraAt`, `MOVE_KEYS`), CSS camera (`cssWorld`), depth of field (`dofBlur`), shape morphing (`resample`/`morph`), `countUp`, `frameTime` | `studio/src/lib/motionCore.ts`. One source: Remotion imports it; motion pieces get it as `/osm/motion-core.js`, transpiled by the harness. |
| Deterministic render harness: `window.seek(t)`, Playwright, 60 fps × 3 subframes → ffmpeg `tmix` motion blur, per-beat stills, determinism test, audio mux | `tools/seek_render.js` |
| Soundtrack in code: OfflineAudioContext kick on every beat, riser into the last bar, hit on scene changes, WAV | `motion/lib/audio.js` (`renderSoundtrack`) |
| Unit tests of the core maths (springs, easing, beat grid, rand, camera rules, morph, blur, frameTime) | `node tools/motion_selftest.js` (18 tests) |
| Numeric QC: holds > 0.5 s, change on every beat (visual + audio onset), loop first = last, per-beat sheet | `tools/motion_qc.py` |
| 2D brand piece with every Spec 2 technique (reference + template) | `motion/pieces/osm_sting/piece.html` ("The bar becomes the word becomes the build", 9 s, 120 BPM, loops) |
| three.js physically based pipeline (Spec 1 lights, materials, shadows, fog, ACES, named camera, reacting wave) | `motion/pieces/gallery3d_test/piece.html` (three@0.160.0 from jsdelivr, pinned) |

**Using a piece in a reel:**
1. Render the piece to MP4.
2. Copy it into the project's `source/`.
3. Add it to `edit.json` as a normal clip (`media` + `clips`, `plates` for 1:1 framing): a hook, chapter card, data moment or outro.
4. Sound comes from the studio mix (`sfx.cues`, music), so render the piece without `--audio` for reels. `--audio` is for standalone stings.

## 5. Applying it to every new video (creative judgment, not a checklist)
During the blueprint stage, go through the transcript beat by beat and note, for each spoken idea, whether one of these serves it:

| Script signal | Technique |
|---|---|
| a hook / first 1–2 s | kinetic type from the first word, or a shape that becomes the subject |
| a number, %, sets/reps, kcal, a before→after value | a data/UI moment: count-up, bar or ring with springs (real numbers only) |
| a list or steps | kinetic type per beat, one item per beat |
| a concept turning into a practice ("principle → your training plan") | a shape morph: the caption bar → icon → card |
| structure, anatomy, "how it's built", program architecture | a 2D-to-3D moment: plane → extruded columns / stacked cards, one named camera move |
| app or features | a UI moment: screen card with one camera move (studio `screenCard`) + a reacting element |
| an ending or CTA | an end title that matches the opening frame (loop), in brand type |

**Restraint:**
- Use at most one motion piece per 15–20 s of talking head.
- Never cover his face.
- Never place text on or above his head.
- The footage stays the main subject.
- "No opportunity" is a valid answer. Write it in the blueprint.

**Default parameters:**
- 120 BPM grid for motion pieces, or the song's BPM if music is chosen.
- Springs `freq` 2.2–3.2, `damping` 1 (UI/type) or 0.75–0.9 (objects with mass).
- Impacts `expoOut` 0.3–0.6 s.
- Camera moves eased with `expoInOut`, one per shot.
- Motion blur from 3 subframes.

## 6. Conflicts and precedence
- **Locked OSM rules win:** caption bars `#56A0FB` with white text, no text on or above his head, no haze, blur or glow behind text, natural camera colour, no AI people.
- **Existing studio features versus the spec bans:**
  - `shakes` (camera shake), `flashes`, the `KineticTitle` slam blur and white-flash transitions are part of the approved, locked editing system. They stay available and are never removed from delivered videos.
  - For new motion pieces the spec bans apply: no shake, no glow, no flash-as-transition, no crossfades.
- **Delivered videos are never re-edited with these techniques unless he asks.**

## 7. QC (every motion piece, and every edit that contains one)
1. Render stills first: `node tools/seek_render.js PIECE.html DIR --beats 120`. Look at the sheet and fix it before the full render.
2. Full render: `node tools/seek_render.js PIECE.html OUT.mp4 [--audio] [--size 1080x1920] [--sub 3]`.
3. Run `python3 tools/motion_qc.py OUT.mp4 --bpm 120 --loop`. Holds, beats and loop must pass; look at `beats.jpg`.
4. Run `node tools/seek_render.js PIECE.html - --determinism` to confirm the same frame comes out regardless of render order.
5. Brand check: palette, fonts, nothing on or above his head, no banned effects. Then, for a reel, the usual `qa_render.py` + `head_check.py`.

**Measured on this container (4 CPUs, no GPU, SwiftShader WebGL):**
- 2D CSS/SVG piece, 1080×1920, 9 s, 60 fps × 3 subframes: about 2.3 min.
- three.js piece with 2048 px soft shadows, 1080×1920, 4 s, 60 fps × 3: about 7.8 min (0.65 s per subframe).
- Preview with `--sub 1 --fps 30`. Keep the final 3D pieces short, or lower the shadow map size.

## 8. Not implemented yet
- Depth of field in three.js (BokehPass); `dofBlur` covers CSS layers.
- Transparent (alpha) output for motion overlays on footage: pieces are full-frame inserts for now.
- Geist isn't in `brand/fonts`. That's intentional, because OSM type is Inter.
- The full Spec 1 gallery (20 s) and the Spec 2 showreel (15 s) as deliverables: the pipeline for both is built and tested. A brand-specific version is a separate creative job when he asks for it.
