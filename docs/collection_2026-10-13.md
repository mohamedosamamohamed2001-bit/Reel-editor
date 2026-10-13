# OSM collection upgrade (2026-10-13): five re-edited Reels

Source: Google Drive folder `1MnE8wtys9dFmM9vWf-NwGM2GCOjx0kmj`, five previously edited videos. All five were downloaded and analysed:

| Drive file | Project | Length | Source | Content |
|---|---|---|---|---|
| العودة من بعد الغياب 2.MP4 | `2026-10-13_c5-comeback` | 22.2 s | 720×1280, 30 fps | Back to training after injury / time off: 3 rules |
| استرتش 2.MP4 | `2026-10-13_c5-stretch` | 27.9 s | 720×1280, 60 fps container (≈30 unique) | Stretching done right: Concentric / Eccentric, Chest and Triceps examples |
| Whey supplement 2.MP4 | `2026-10-13_c5-whey` | 31.8 s | 720×1280, 60 fps container (≈30 unique) | Whey protein: worth the money? |
| crossfit 2.MP4 | `2026-10-13_c5-crossfit` | 39.9 s | 720×1280, 30 fps | CrossFit or gym, pros and cons |
| LegDay 2.MP4 | `2026-10-13_c5-legday` | 46.0 s | 720×1280, 60 fps container (≈30 unique) | Gym vlog, 8 leg exercises, music only |

## What the files actually are (and what that limits)
They are **finished exports**, not raw footage: captions, colour, light-leak/glitch transitions and music are burned in, and
voice and music are one mixed track. So:
- **Music** could only be replaced after separating the voice: `tools/separate.py` (UVR MDX-Net Voc_FT, open model, local
  CPU). The separated voice is clean in the spectrograms (no music pulses; the bed has no speech formants).
- **Old captions** can't be removed from the pixels without AI inpainting (which would alter the footage), so they are
  **covered** by frosted Night plates baked into the footage (`covers`), and the new captions sit on those plates.
- **Old light leaks, flashes, the colour-bar glitch and the viewfinder intro** are cut out, replaced by held clean frames,
  or hidden under the new transitions / title cards.
- Resolution: 720×1280 sources, delivered at 1080×1920 (Lanczos upscale, light sharpening). The upscale adds no detail;
  it is there so the new type and graphics render natively sharp at Instagram's delivery size. Frame rate: 30 fps for all
  five (the 60 fps files repeat most frames: legday has 179 unique frames in its first 360).
- Legday's soundtrack was a commercial rap track with explicit lyrics; it is gone (copyright and brand risk).
- The other four had unidentified music beds; all replaced by original tracks.

## Collection system (identical in all five)
| Element | Spec |
|---|---|
| Grade | `common.GRADE`: contrast 1.05, sat 0.95, cool shadows / neutral highlights, gentle S-curve, soft vignette; CAS 0.22 |
| Captions | IBM Plex Sans Arabic Bold 66 px, 1–3 words, word-synced (karaoke), one Core Blue keyword with the 112° bar; English terms in Inter, isolated LTR |
| Caption text | the client's own approved captions (read off the frames), aligned to the voice with `tools/align_words.py`; English loanwords in English (Stretch, CrossFit, Cardio, Calories, Whey Protein, Supplement, Range of Motion, Concentric, Eccentric, Chest, Triceps, Jump) |
| Hook | `kineticTitle`: Barlow Condensed caps slam-in (scale 1.7→1 + motion blur, 3-frame stagger), 2.5D tilt, Core Blue accent line + 112° bar, boom + slam on frame 1 |
| Chapters / points | `stepBadge` (outlined numeral fills Core Blue behind a 112° slash), `checklist` chips (his exact words), `lowerLabel` (exercise + sets counter), `trackedLabel` (pinned to an object) |
| Title cards | full-frame `kineticTitle` with `backdrop` (Night + drifting 112° hairlines), used only where an old light leak sat mid-sentence |
| Transitions | whip (directional motion blur from 8–28 sub-frames, mirrored edges), zoom punch (zoom blur + exposure bloom), flash (white core, Core Blue rim), speed ramps (frame-blended, never interpolated), freeze frame, settle punch-ins; camera-shake on major hits |
| Sound design | `tools/sfx.py` (all synthesised): whip, boom, riser, slam, mech, bass_drop, reverse_hit + the v3 kit. Every transition has its sound on the exact frame. |
| Music | `tools/music.py` original tracks, 120 bpm grid (a beat = 15 frames), sections end exactly on the cuts (tempo flexes ≤8 %), drops on the big moments, sidechain-ducked 4:1 by the voice |
| Mix | voice normalised to −16 LUFS before the mix; music ≈13 dB under the voice while he talks (measured per video with `tools/mix_report.py`), up to voice level between lines; master −14 LUFS / ≤ −1 dBTP |
| End card | OSM wordmark (fade + scale settle, never masked) + "OSM Coach Osama" pill, 2.4 s, reverse hit → boom → click |

Per-video creative treatments differ on purpose: comeback = numbered rules; stretch = technique with train→stretch pairs;
whey = tracked product label + food chips + verdict cases; crossfit = definition chips, pros/cons; legday = beat-cut montage
with ramps and a freeze frame.

## Deliverables per video
`exports/OSM_<n>_<slug>.mp4` (with music) and, for the four talking videos, `exports/OSM_<n>_<slug>_no-music.mp4`
(voice + SFX only, for adding a track from Instagram's library instead).
