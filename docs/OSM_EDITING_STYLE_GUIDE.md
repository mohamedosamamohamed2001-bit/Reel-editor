# OSM Editing Style Guide (approved preset)

The reusable house style for **OSM — Osama Strength Method** Reels, approved by Coach Osama on 2026-10-14 after the
five-video collection (`projects/2026-10-13_c5-*`). Every new video starts from this preset; the code lives in
`projects/_c5/common.py` (collection base) and `projects/_n6/common2.py` (current preset: narrow blue bars + supporting
visuals). Brand rules come from `docs/BRAND_VIDEO_SYSTEM.md` and `brand/tokens.json`.

## 1. Format
- 1080×1920, 30 fps, H.264 (CRF 18, yuv420p, BT.709), AAC 256 kb/s. Master −14 LUFS integrated, ≤ −1 dBTP.
- Text and graphics inside the 14 % top/bottom safe areas; nothing over his face.

## 2. Look
- One grade for the whole collection (`GRADE`): contrast 1.05, saturation 0.95, cool shadows / neutral highlights,
  gentle S-curve, soft vignette; CAS 0.22 sharpening (light: most sources are 720p).
- Never alter his face or body; no AI people; no interpolated slow motion (speed ramps blend real frames).

## 3. Captions (approved 2026-10-14)
- His exact words (Egyptian Arabic as spoken), 1–3 words per phrase, word-by-word highlight (karaoke).
- IBM Plex Sans Arabic Bold 66 px; English terms in English (Inter), one isolated LTR run; no Arabic "ال" glued to an
  English term (Stretch, Glutes, Triceps, Supplement …).
- **Background: OSM blue #56A0FB, narrow** — the bar fits the words with clean padding (6/30/10 px), rounded 20 px.
  Keyword + underline in Night #0A0F16 (blue on blue would vanish).
- Re-editing a finished video: old burned-in captions are hidden by a soft per-phrase blur (feathered mask), not by
  a wide bar.

## 4. Motion graphics
| Element | Use |
|---|---|
| `kineticTitle` | hook (slam-in, 2.5D tilt) and section titles; Barlow Condensed caps / Plex Arabic; one Core Blue accent line + 112° bar |
| `stepBadge` | numbered points, ✓ / ✗ (right vs wrong), + / – (pros/cons) |
| `lowerLabel` | exercise name / setup / "MOVE 01"; sets counter (3 × 15) |
| `checklist` | his listed words as chips (row or column) |
| `trackedLabel` | label pinned to an object (`tools/track.py`) |
| `visualCard` | supporting image: full-screen cutaway or picture-in-picture card, slam-in, slow push, anatomy markers (pulsing blue rings + labels) |
| End card | OSM wordmark (fade + scale, never masked) + "OSM Coach Osama", 2.4 s |

## 5. Transitions (powerful, never soft)
- Whip (directional motion blur, mirrored edges), zoom punch + flash, settle punch-ins, speed ramps, freeze frames.
- Every old light-leak / flash / glitch is replaced: a clean held frame rides the new transition.
- Camera-shake on major hits. 1 major transition per section, not on every cut.

## 6. Sound
- Original music (`tools/music.py`), 120 bpm, energetic (trap or four-on-the-floor drive), sections end exactly on
  the cuts, drops on the big moments. Music sits ≈ 13–15 dB under his voice while he talks (4:1 duck), comes up between
  lines. A no-music version is always exported too (for Instagram-library music).
- Sound design (`tools/sfx.py`): boom on hooks/drops/end card, whip on whips, riser/reverse-hit into zooms, slam on
  titles/badges, mech/click on labels and chips. Levels: transitions −9…−13 dB, accents −15…−19 dB.

## 7. Supporting visuals
- Only when they explain what he says, at the word: food → the food, a muscle → anatomy with the muscle marked, a tool
  → the tool, right/wrong technique → his own demo labelled ✓ / ✗ (or a split of his own footage).
- Sources: CC0 / public domain first (Rawpixel, public-domain anatomy atlases), then CC BY (with an on-screen credit).
  No NC/ND licences, no AI images. Every asset is logged in `projects/_n6/assets/manifest.json`
  (`tools/fetch_asset.py`), and CC BY credits also go in the post caption.

## 8. Workflow
probe → separate voice/music (`tools/separate.py`) → find old captions (`tools/burned_text.py`) → transcribe
(large-v3, one short dialect prompt) → align to the approved caption text (`tools/align_words.py`) → `build.py`
→ preview → full render (+ no-music) → QA: `qa_render`, `sync_check` (≤ 10 ms), `mix_report`, `band_sweep` (no old
text), effect-frame scan → export → deliver.
