# Quality control: `exports/final_instagram_reel.mp4`

sha256 `ca7b6a34f3d682d7ce0fb05bb37fc87b476ea6a54b2c2a336a5f25b5b1b995d7` · 28.1 MB · rendered 2026-10-12

## Technical (automated, all on the final file)
| Check | Result | How |
|---|---|---|
| Opens / valid streams | **Pass**: H.264 High yuv420p BT.709 TV range + AAC-LC 256 kbps 48 kHz stereo | ffprobe |
| Resolution / aspect | **Pass**: 1080×1920 (9:16) | ffprobe |
| Frame rate | **Pass**: 29.97 (source rate kept) | ffprobe |
| Duration | **Pass**: video 23.690 s (710 frames) = audio 23.690 s | ffprobe `-count_frames` |
| Black frames | **Pass**: none | blackdetect |
| Frozen frames | **Expected**: one interval, 22.02 s → end = static end card | freezedetect |
| Loudness | **Pass**: −14.3 LUFS integrated (target −14 ±1) | ebur128 |
| True peak | **Pass**: −1.4 dBTP (max −1.0) | ebur128 |
| Clipping | **Pass**: sample peak −1.7 dBFS | astats |
| A/V sync | **Pass**: dialogue is −5 ms from the source in all 5 clips (corr 0.955–0.977). Picture offset 0 to −33 ms (frame resolution) | cross-correlation, audio vs source + motion-energy correlation, video vs source crop |
| Clicks at cuts | **Pass**: the real cut (6.06 s) has a max sample step of 0.002 (silence). Framing-only joins are one continuous waveform | sample-step scan |
| Silence | 21.18 s → end = end card (no music by design) | silencedetect |

## Visual (inspected)
- Contact sheet (20 frames) + full-resolution stills at 0.3, 3.5, 6.1, 9.6, 13.0, 14.5, 15.3, 15.5, 16.2, 19.0 and 22.5 s.
  Previews were also inspected at 0.5, 6.4, 8.5, 9.3, 10.6, 12.2, 14.4, 17.6, 20.4 and 22.4 s.
- **Sampled, not every frame.** No frame-by-frame review of all 710 frames was done.
- Framing: face and hands in frame in every sampled frame. Punch-ins ≤1.27× of a 4K source (no visible softening).
- Arabic: correctly joined, RTL, upright, no clipped words. Mixed Arabic/English phrases ("اسمها Calories Calculator") order correctly.
- App card: status bar, Dynamic Island, keypad and tab bar cropped out. All three goal cards are visible while he says تزيد / تخس / تحافظ.

## Brand checklist (`docs/BRAND_VIDEO_SYSTEM.md` §4)
| Mandatory | Result |
|---|---|
| Name exactly OSM | Pass ("OSM" in captions; wordmark on end card) |
| Logo unaltered, on Night, clear space, ≥120 px | Pass (640 px, Night background, `lighten` composite only hides the JPEG box) |
| Emblem and wordmark not together | Pass (wordmark only) |
| Text on Core Blue is Night | Pass (CTA) |
| Copper only for earned moments | Pass (not used) |
| Arabic not italic or spaced, Western digits | Pass |
| No text in top/bottom 14% | Pass (captions at 60% / 75%; end card centred) |
| Captions verbatim | **Pending human check**: machine transcript (large-v3) with 2 corrections and 2 low-confidence words, listed in `analysis/main_footage_analysis.md` |
| No guarantees, fake urgency, invented claims | Pass. No added claims. Spoken claims ("اسبوع فري", calculator "for free") are his words; **confirm they match the live rules** |
| No prices or payment steps | Pass. "قبل ما تشترك" mentions subscribing only. Instagram use only, not inside the iOS app |
| Face and body unaltered, no AI people | Pass (no retouching, grading or warping; crops and scale only) |
| No flares, smoke, particles; ≤1 glow per frame | Pass (CTA glow only) |
| Avoided vocabulary | Pass (none in captions or graphics) |

## Not checked
- Playback inside Instagram on a phone (needs upload), and how the IG interface overlaps on the user's device.
- **Caption accuracy by ear.** I can't listen to audio. Coach Osama must review it before publishing.
