# Video 2 + Video 1 audio + OSM caption (2026-10-25)

**Sources:** Drive folder `1t7KGCoFIulGdPvYgA9x3tPWojgl6GUF6`. The sha256 values are in `projects/2026-10-25_audioswap/sha256.txt`.
- **Video 1** (audio source only): a screen recording of another account's Instagram post (@mennahmed5), 24.03 s. Only its audio is used.
- **Video 2** (main): Coach Osama's AlphaX footage. HEVC 10-bit, HLG/BT.2020 with Dolby Vision 8.4, 1080×1920, 30 fps, 687 frames, 22.9 s. Its own audio is digital silence.

**Audio:**
- Video 1's sound is 22.883 s long, from sample 17625 (0.400 s) to 23.283 s. Before and after it is digital silence.
- The sound is placed 8 ms into Video 2 and ends 9 ms before its end. No word is cut.
- No gain, EQ or limiting. Encoded AAC 320k.
- Check: lag 0 samples, correlation 0.99995 with Video 1's audio. The residual of −40 dB comes from the AAC encode only.

**Caption:**
- Text: the exact wording from `caption.txt`. Visual line breaks after "إحنا" and "حياتنا", three lines. The words are unchanged: the rendered text equals the file.
- Locked OSM style: IBM Plex Sans Arabic 700, 66 px, line-height 1.7, white #FFFFFF text on a solid #56A0FB bar, radius 20, padding 6/30/10. No shadow, glow, blur or haze. Emoji in Noto Color Emoji.
- Position: 0.588–0.773 of the frame height. Below every face in 0–7 s (YuNet: the lowest face bottom is 0.513) and above the Reels UI.
- Timing: shown from frame 0, with a 0.2 s fade ending at 7.0 s. Gone from frame 210.
- HDR placement: the sRGB caption is converted to HLG per BT.2408 (white = 75 % HLG, code 721). The round trip gives back #56A0FB / #FFFFFF exactly. In the encoded export the bar decodes to #569EF9 (4:2:0 + 10-bit encode).
- No OSM logo added: none was requested, and "do not overcrowd" applies.

**Picture:**
- Video 2's frames, kept as 10-bit HLG. No grade, no crop, no reframe.
- libx265 CRF 10, preset slow.
- Frames 210–686 measure ≥ 47.2 dB PSNR-Y (mean 53.0) against Video 2.
- The Dolby Vision RPU is not carried over (no dovi_tool): the export plays as HLG HDR.

**Delivery:** `deliveries/osm_audioswap_2026-10-25/OSM_Video2_Final.mp4` (73,067,803 bytes, sha256 df4c363c…1256). Sent as an in-app attachment and pushed with Git LFS.
