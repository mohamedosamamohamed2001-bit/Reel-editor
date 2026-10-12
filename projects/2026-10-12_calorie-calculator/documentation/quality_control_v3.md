# Quality control: `exports/final_instagram_reel_v3.mp4` (motion graphics + sound design)

sha256 `b8f6b152ad297ac8139a81076d2ea292c216d460213a4b8df8965db9df5b861d`. v1 (`ca7b6a34…`), v2 (`1ac27e5a…`) and both sources re-hashed unchanged.
Plan: `analysis/upgrade_plan_v3.md`. `work/edit.v2.json` re-renders v2 (every v3 feature is opt-in).

## What was added
| Area | Change |
|---|---|
| Captions | Word-synced: each word lights from 45% to 100% on its spoken start. The Method underline draws on the word itself |
| Cuts | 4% punch "settle" on the two jump cuts (2.64 s, 6.04 s) |
| App card | 2.5D entrance (10° tilt, 1.5% overshoot, shadow deepens), card opaque within 5 frames; lift-and-tilt exit |
| Highlights | Check mark (disc pop + stroke draw) on each goal card as he names it |
| End card | Logo fast fade + 4% settle (no mask: a wipe would crop the letters, which the brand forbids); **1-frame gap before the end card fixed** (frame 634 showed bare background in v1/v2) |
| Sound | 25 frame-locked cues, all synthesised in-house (`tools/sfx.py`, no third-party samples): sub open, punch air ×2, Method accent, swell + whoosh + thump on card arrival, tap click, page swipe, 7 keystroke ticks, results chime, 3 ascending highlight blips, card exit air, end swell → layered impact → CTA click |

## Audio (measured on the final file)
| Check | Result |
|---|---|
| Integrated loudness | **−14.4 LUFS** |
| True peak | **−1.3 dBTP** (sample peak −1.4 dBFS) |
| Voice level vs v2 | master gain +6.1 dB (v2 dialogue-only: +6.0), so **the voice is at the same level**; SFX add ≈0.1 dB integrated |
| Voice vs SFX at each cue (momentary, during speech) | minor 21–28 dB under, medium 13–24 dB under, major 13–16 dB under. The voice wins at every cue. SFX bus: HPF 40 Hz, −4 dB @ 2.5 kHz, sidechain-ducked 2:1 by the dialogue |
| SFX placement | 25/25 hits on their intended frames (max 0.014 frame, log rounding) |
| Dialogue sync vs source | −5 ms in all 5 clips |
| Click check | every synthesised sound ends at exactly 0 with no DC; end-of-layer clicks found in the spectrograms were fixed |

## Video
1080×1920, 29.97 fps, 710 frames, 23.690 s video = audio. No black frames. Frozen = static end card only (from 21.99 s). Full decode clean.
Reviewed: 14 key frames around every new motion event, plus the full-mix spectrogram with cue markers. **Sampled, not every frame.**

## Limitations
- **I can't listen.** Sound quality was judged from spectrograms, waveforms and loudness measurements, not by ear.
  Please listen on phone speakers and on headphones. Every level is one `gain_db` number in `edit.json`.
- Synthesised SFX are clean and original but simpler than a commercial library. Licensed library sounds can replace any cue later.
- No music (no licensed library here). Instagram's library can add it at upload: keep it low under the voice.
- Captions still need your by-ear check (معادلة, Calories, تحافظ, وجرب).
