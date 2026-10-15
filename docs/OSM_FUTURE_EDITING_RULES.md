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
- Use 3D type where it improves the scene: real depth, perspective, lighting (hard extrusion). **No soft/blurred
  shadows, glows or haze behind any text** (2026-10-15, section 7).
- Must look premium, never cartoonish or cheap. Not on every caption.
- Brand fonts and colours only; captions stay clean and readable.

## 3. Behind-the-head typography (head/body occlusion) — WITHDRAWN 2026-10-15
- **Coach Osama 2026-10-15: no text on, behind or above his head, ever.** Behind-the-head titles are not used any more (section 7).
- (Original rule, kept for history:)
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

## 7. Corrections 2026-10-15 (Coach Osama, applied to all 12 batch-3 videos, and binding for every new video)
- **No text on or above his head.** Nothing (titles, captions, icons, badges, labels) may sit over his head or in the
  column above it. Big titles that were above/behind the head are removed (not moved); other graphics sit just below
  his chin, above the caption bar. Check every render with `tools/head_check.py` (YuNet face + text-only pass);
  `projects/_b3/head_fix.py` applies the batch-3 fixes. A full-frame title card (no head visible) is fine.
- **No moving blur / haze / fog / translucent layer behind text.** Text has no soft box-shadows, glows, blurred cast
  shadows or blur in its entrance/exit (smooth titles, badges, labels, icon tiles, captions). Readability on a light
  shirt comes from a solid caption-bar plate (`plate: true` on stepBadge/lowerLabel), never from a soft shadow.
  The footage behind text stays clean and untouched.
- Picture cards: no full-frame dimming layer when a card appears, no blur in/out, no soft shadow/glow; full-screen
  pictures have no dark gradient behind the captions. A picture card that would cover his face becomes a full-screen
  cutaway. Graphics with no room under his chin (tight close-ups) sit beside his head (`iconPop.align`), never over
  or above it; captions move down only where his beard would reach the bar (`headfix.json` "captions").
