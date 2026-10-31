<direction>
Build the Prompt Motion gallery, reimagined as a 3D space of video cards on curved walls, as one self-contained HTML page with three.js.
Style: soft daylight and white space in Prompt Motion's own: black and white, Geist, one orange accent.
The signature shot is the pull back where the corridors of cards resolve into the letters PROMPT MOTION seen from above. Build everything toward it.
Camera: a film camera, not orbit controls. Every shot uses one named move (dolly, crane, orbit, push-in, rack focus), eased in and out, and the camera never passes through geometry.
Light and materials: a key, fill and rim light with soft shadows, an environment map for reflections, fog for depth, physically based materials with varied roughness, ACES tone mapping. Nothing should look like a default material.
Motion: things react to each other (what's hit moves, what's near lights up), driven by springs or simple physics, never linear tweens.
Banned: default materials and lighting, floating text labels, glows on everything, a slowly spinning object as the whole idea, anything that looks like a tech demo.
</direction>
<structure>
Shots, about three seconds each:
1. Macro on the edge of one card in soft light, then rack focus onto its playing video (a real poster from the site). 2. Dolly back: it's one of hundreds of cards on a gently curved wall, all playing; a wave of orange light runs along the wall and each card tilts slightly as it passes. 3. Crane up and over the wall: behind it, more walls form corridors. 4. One card unhinges, swings toward the camera with weight and settles; its prompt is printed on its back and lifts off as 3D type, line by line. 5. The signature shot: pull far back and up while the orange light traces the O. 6. Settle on the wordmark and prompt-motion.com.
</structure>
<build>
1. One HTML file, three.js from a CDN, no build step. Model everything in code; no downloaded models, and no textures except the site's own video posters for the cards.
2. Use MeshPhysicalMaterial, a PMREM environment from RoomEnvironment, soft shadows, ACES tone mapping and antialiasing. Add depth of field only on shots that need it.
3. Hold 60fps on a laptop.
4. Add a ?render mode where every frame is computed from time (seeded randomness, no clock), so it can be captured with Playwright into an MP4 at 1920x1080.
5. Capture one frame per shot, look at it, and fix anything flat, aliased, clipping or hard to read.
</build>
<gotchas>
Set shadow bias, or surfaces get striped acne. Keep near and far planes tight, or distant surfaces flicker. Seed every random number, or the render won't match the preview.
</gotchas>
<start>
Describe the signature shot and the shot list in a few lines, then build it without asking me anything else. Give me the HTML file and a 20-second MP4 captured with the ?render mode.
</start>
<direction>
A 15-second motion design showreel that proves you are a world-class motion designer. Concept: your pick (e.g. "ink becomes type becomes architecture"). Commit to it and name it in one line before you start. Every shot is made out of the previous one: shapes, type and color transform into the next scene instead of cutting or fading.
One typeface (Geist, Inter or a bold display face from Google Fonts), a palette of at most three colors plus black and white, one consistent camera language.
Show range: kinetic type, shape morphing, a 2D-to-3D moment, a data or UI moment, and an end title. Give each one an equal share of the time.
Banned: particle bursts, glows, lens flares, camera shake, RGB split, crossfades, generic gradients, bouncy easing, holds longer than half a second, anything that looks like a template.
</direction>
<structure>
120 BPM, something happens on every beat.
First bar: hook. Then one technique per bar, each flowing out of the last. Last full bar: the strongest moment. Final half bar: end title, and the final frame matches the first so it loops.
</structure>
<build>
1. One HTML file at 1920x1080. Every style is computed from time inside window.seek(t): no CSS animations, no timers, no state carried between frames.
2. Use spring and exponential easing written as functions of time. Blur follows speed and direction on fast moves.
3. Write a soundtrack in code with the Web Audio API (OfflineAudioContext): a kick on every beat, a riser into the last full bar, a hit on each scene change. Render it to WAV.
4. Render with Playwright at 60fps, 3 subframes per frame blended with ffmpeg tmix for motion blur, then mux the audio.
5. Before the full render, render one frame per beat and look at them. Fix anything cluttered, off the beat, overlapping or hard to read.
</build>
<start>
Tell me the concept and show a beat-by-beat storyboard, then build it without asking me anything else. Give me the final MP4.
</start>
