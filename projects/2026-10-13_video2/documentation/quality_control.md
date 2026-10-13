# QA: exports/final_instagram_reel.mp4 (2026-10-13)

## Measured (tools/qa_render.py + checks)
| Check | Result |
|---|---|
| Video | h264 1080×1920, 29.97 fps, yuv420p BT.709, 38.205 s (1145 frames) ✅ |
| Audio | AAC 48 kHz stereo, −14.2 LUFS, LRA 3.3, true peak −1.9 dBTP, no clipping ✅ |
| Black frames | none ✅ |
| Frozen frames | from 36.44 s = static end card (expected, INFO) |
| Silence | 37.16–38.21 s = end card tail (expected) |
| Dialogue sync | −2 ms in every clip (cross-correlation vs source) ✅ |
| Full decode | ffmpeg decode to null, no errors ✅ |
| Sources | sha256 unchanged (manifest) ✅ |

## Looked at
- Contact sheet + full sheet every 0.5 s (all 77 frames): captions readable, no collisions, cards cropped cleanly.
- Privacy sweep every 4th frame across cards W and P: all account numbers covered by blur.
- Typecheck of the studio (tsc) passes.

## Not checked / needs a human
- **Captions by ear** (I can't listen). English terms set in English: Full Access, App, Challenges, Points, Access, Upgrade, Payment, Website, Package, Free.
- SFX balance by ear (levels set by measurement).
- Minor: at ~24.5–25.0 s the site's hero image loads during the splash hold (darker frames), not an error.
