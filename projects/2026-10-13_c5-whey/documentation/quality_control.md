# QA: whey (Whey supplement 2.MP4)

## Measured (tools/qa_render.py, tools/sync_check.py, export checks)
| Check | Result |
|---|---|
| Video | h264 1080x1920 30.000fps yuv420p, 33.367 s |
| Audio | aac 48000Hz 2ch; -14.2 LUFS, LRA 1.8 LU, true peak -1.9 dBTP |
| Black frames | none |
| Frozen frames | [{'start': 31.7, 'end': None}] = the static end card (expected) |
| Dialogue sync (per clip, cross-correlation) | worst |lag| 2.0 ms -> PASS |
| Source unchanged | sha256 76ad20fcc51f… matches the download |
| Export `OSM_03_whey-protein.mp4` | h264 1080x1920 30/1, 1001 frames, 22.3 MB, full decode OK |
| Export `OSM_03_whey-protein_no-music.mp4` | h264 1080x1920 30/1, 1001 frames, 22.3 MB, full decode OK |

## Looked at
- Contact sheets of the whole render (2–4 fps) and frame-by-frame strips of every transition.
- Caption band sweep (every 4th frame, tools/band_sweep.py): no burned-in text from the old edit visible.
- Effect-frame scan (brightness/warmth per frame): every flagged frame is one of the new transitions or the end card; the old light leaks are gone.
- Mix measured per bus before rendering (tools/mix_report.py): music ≈13 dB under the voice while he talks.

## Not checked / needs a human
- **Listening.** I can't hear audio: the music, SFX balance and the separated voice's quality were checked by measurement and spectrogram only.
- **Captions by ear.** Words come from your original captions, aligned to the voice; any word the original captions got wrong is still wrong.
- Playback on a phone (Instagram UI overlap, brightness).
