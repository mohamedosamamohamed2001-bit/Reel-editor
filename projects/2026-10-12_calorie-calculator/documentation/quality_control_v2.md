# Quality control: `exports/final_instagram_reel_v2.mp4`

sha256 `1ac27e5a56f9ece4880d693d6c0572976a87815f3c7fc68b2600522669f3d7b4` · 27.1 MB · rendered 2026-10-12.
v1 (`final_instagram_reel.mp4`, sha256 `ca7b6a34…`) and both sources (`ec5cf4de…`, `407b6cf8…`) are unchanged, re-hashed after export.

## What changed from v1 (all verified)
| Change | Evidence |
|---|---|
| "الميثود" → **Method**, "الوركاوت" → **Workout** (English, Inter), via `captions.replace` in edit.json | Every caption reviewed at 0.5 s steps and full-res stills at 6.6 s and 18.0 s. No other transliterated English exists in the transcript ("Calories Calculator" and "for free" were already English) |
| English phrases kept as one LTR run in RTL captions | "Calories Calculator" and "for free" read in the correct order (a reversal bug found during review was fixed) |
| Footage clarity: FFmpeg plates (crop → grade → Lanczos → CAS 0.4) shown as image frames | Face detail (Laplacian variance, averaged over 10 frames): v1 → v2 = 30→51, 51→175, 37→143, 42→75 (0–2, 3–5, 6–8, 18–20 s). Root cause in v1: Remotion's `<OffthreadVideo>` frame extraction (same frame: 311 → 44) |
| Grade: highlight warm, midtone red down, gentle S-curve | Shirt R−B −23 → −15 (less blue cast). Blue-channel clipping 21.5% → 0.2% of pixels. Cheek R−B +24 → +29 (natural, not pushed red). No skin smoothing, no reshaping |
| Lossless PNG frames in Remotion (was JPEG q80) | Config change |
| Motion graphics: "Method" underline draw, tap ripple on the Calorie Calculator tile, highlights moving Lean Bulk → Shred → Maintain synced to تزيد / تخس / تحافظ, blur-in card entrance, slow 2% card push | Full-res stills at 9.62, 15.6 s and the 0.5 s contact sheet |
| Frame-exact plate trims | Picture − audio offset per clip computed from the timeline: 0, 0, +18, −16, −16 ms (≤ half a frame) |

## Technical (automated, final file)
| Check | Result |
|---|---|
| Streams | H.264 High yuv420p BT.709 TV range, 1080×1920 (9:16), 29.97 fps, 710 frames · AAC-LC 48 kHz stereo |
| Duration | video 23.690 s = audio 23.690 s |
| Full decode | no errors (`ffmpeg -f null`) |
| Black frames | none |
| Frozen frames | only 22.02 s → end = static end card (intended) |
| Loudness / true peak / clipping | −14.3 LUFS · −1.4 dBTP · sample peak −1.7 dBFS |
| Audio vs source | −5 ms in all 5 clips (cross-correlation) |

## Visual review
- Whole video at 0.5 s steps (48 frames) + 7 full-res stills + a 2× halo check at the beard/shirt edge (no halos).
- **Sampled, not every frame.**

## Limitations (not fixable in post)
- The source is "4K" at only 6.3 Mbps. Compression blocking inside the dark beard and soft fine texture are baked in.
  Sharpening can't restore them, and AI upscaling would invent facial detail, so it wasn't used (the brand rule is never to alter his face).
- Captions still need Coach Osama's by-ear check: معادلة, Calories, تحافظ, وجرب (see `analysis/main_footage_analysis.md`).
- Not tested inside the Instagram app on a phone.
