# OSM — future video editing rules (Coach Osama, 2026-10-14)

**Scope: NEW videos only.** These rules are additions to `docs/OSM_EDITING_STYLE_GUIDE.md` and the decisions in
`CLAUDE.md`, not replacements. Never re-edit, re-render or change an existing/delivered video (including batch 2,
OSM_06–OSM_11) to apply them unless Coach Osama asks for that video explicitly. Approved caption wording, layouts,
backgrounds (narrow #56A0FB bars, no blur), erased old captions and the end card stay exactly as approved.

## 1. Caption timing & readability
- Captions never zoom or scale up fast. Entrances are smooth and controlled (eased, no snap/overshoot pops).
- Every caption stays on screen long enough to read comfortably; timing follows the voice naturally but readability wins.
- No aggressive zooms, rushed transitions or distracting text movement. Premium, cinematic, easy to follow.

## 2. Premium 3D typography (selective)
- Use 3D type where it improves the scene: real depth, perspective, lighting, soft shadows, subtle reflections.
- Must look premium, never cartoonish or cheap. Not on every caption.
- Brand fonts and colours only; captions stay clean and readable.

## 3. Behind-the-head typography (head/body occlusion)
- When a title passes behind his head or body, the subject occludes the text as if the text were in real 3D space.
- Correct depth, perspective and lighting; his appearance and proportions unchanged; text never covers his face
  unnaturally or important facial features.
- Needs a precise per-frame person mask (segmentation/rotoscoping). **Not built or verified in this studio yet**
  (CPU-only container). Before using it on a video: test a local segmentation model on that footage and check the
  mask edges (hair, hands, motion blur) frame by frame. If the result isn't convincing, tell Coach Osama the
  limitation instead of shipping a poor imitation.

## 4. Kinetic typography & hierarchy
- Premium kinetic type where appropriate: words/phrases animated with intent and clear hierarchy, synced to the message.
- Controlled motion, clean transitions, no excess effects. Readability and a high-end fitness-brand look first.

## 5. Brand consistency
- OSM — Osama Strength Method colours, fonts, caption style and identity (`brand/tokens.json`, brand video system).
- Keep approved layouts and techniques; don't introduce styles that conflict with the brand.

## 6. Existing rules stay intact
- Combine these with every previously approved rule. Don't remove, overwrite or simplify existing instructions.
- Don't change approved caption wording, layouts, backgrounds or end cards unless explicitly asked.
