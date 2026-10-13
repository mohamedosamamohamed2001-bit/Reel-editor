# QA: comeback (العودة من بعد الغياب 2.MP4)

## Measured (tools/qa_render.py, tools/sync_check.py, export checks)
| Check | Result |
|---|---|
| Video | h264 1080x1920 30.000fps yuv420p, 23.1 s |
| Audio | aac 48000Hz 2ch; -14.0 LUFS, LRA 1.1 LU, true peak -2.0 dBTP |
| Black frames | none |
| Frozen frames | [{'start': 21.4333, 'end': None}] = the static end card (expected) |
| Dialogue sync (per clip, cross-correlation) | worst |lag| 2.0 ms -> PASS |
| Source unchanged | sha256 66d2c7b836d0… matches the download |
| Export `OSM_01_back-to-training.mp4` | h264 1080x1920 30/1, 693 frames, 19.5 MB, full decode OK |
| Export `OSM_01_back-to-training_no-music.mp4` | h264 1080x1920 30/1, 693 frames, 19.5 MB, full decode OK |

## Looked at
- Contact sheets of the whole render (2–4 fps) and frame-by-frame strips of every transition.
- Caption band sweep (every 4th frame, tools/band_sweep.py): no burned-in text from the old edit visible.
- Effect-frame scan (brightness/warmth per frame): every flagged frame is one of the new transitions or the end card; the old light leaks are gone.
- Mix measured per bus before rendering (tools/mix_report.py): music ≈13 dB under the voice while he talks.

## Not checked / needs a human
- **Listening.** I can't hear audio: the music, SFX balance and the separated voice's quality were checked by measurement and spectrogram only.
- **Captions by ear.** Words come from your original captions, aligned to the voice; any word the original captions got wrong is still wrong.
- Playback on a phone (Instagram UI overlap, brightness).
