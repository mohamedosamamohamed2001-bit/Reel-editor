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
- **No blur, no frosted glass, no extra box behind the text** (Coach Osama, 2026-10-14). The footage stays clear and
  fully visible behind the captions; the only thing behind the words is the narrow blue bar above.
- **Re-editing a finished video: the old burned-in captions are ERASED, not covered** (Coach Osama, 2026-10-14).
  `.venv/bin/python tools/erase_text.py projects/<p>` writes `work/clean/original.clean.mp4` (same frames and timing as
  the source, which is never modified) and `common2.finish()` points the edit at it (`CLEAN_SOURCE`). Only the new
  captions are visible. Check its `--test t1,t2,…` before/after PNGs first; per-video `erase_params.json` handles
  coloured words (`color_windows`) and keeps clothing prints out (`y_min`).
- The old-caption map (covers, kind `"anchor"`) still places the new captions: positions stay where they were approved.
  A project's `covers.pinned.json` freezes them.

## 4. Motion graphics
| Element | Use |
|---|---|
| `kineticTitle` | hook (slam-in, 2.5D tilt) and section titles; Barlow Condensed caps / Plex Arabic; one Core Blue accent line + 112° bar |
| `stepBadge` | numbered points, ✓ / ✗ (right vs wrong), + / – (pros/cons) |
| `lowerLabel` | exercise name / setup / "MOVE 01"; sets counter (3 × 15) |
| `checklist` | his listed words as chips (row or column) |
| `trackedLabel` | label pinned to an object (`tools/track.py`) |
| `visualCard` | supporting image: full-screen cutaway or picture-in-picture card, slam-in, slow push, anatomy markers (pulsing blue rings + labels) |
| End card | Coach Osama's end artwork `brand/end/osm-end-photo.jpg` (full width, unaltered, fade + scale, never masked) + "OSM Coach Osama" pill, 2.4 s. `endCard.image`; set by `common2.END_IMAGE` |

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

## Batch 3 additions (2026-10-15, approved direction: more motion graphics, more B-roll)
- Every spoken object / food / muscle / exercise / concept gets a visual: licensed image (full-screen cutaway, or a
  card that never covers his face) or an `iconPop` illustration tile. Icons sit on the chest or beside him.
- Every cut of the old edit gets a transition (whip / zoom punch / flash) with a hit SFX; the old edit's flashes and
  glitches are replaced by a clean held frame under the new transition.
- Titles: smooth motion (no fast zooms), `depth` for 3D type, `occlude` to sit behind his head when the head is in
  the top of the frame.
- Captions: unchanged system (narrow blue bar, karaoke, exact words). Old captions erased; his face is never retouched.

