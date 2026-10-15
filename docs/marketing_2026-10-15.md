# OSM marketing Reels — 2026-10-15

Six Reels from the marketing plan, made without new filming. Everything in them is real: Coach Osama's own voice and
footage, the real OSM app, and free stock footage that is not AI-generated.

| # | Reel | Voice | Picture | Length |
|---|---|---|---|---|
| 1 | **Coach, not an app** (hero) | his own voice (n2-training + osm-reel takes) | gym footage, his face in sync, the app: workout demos, diet swaps, coach chat | ~21 s + end card |
| 2 | **Every exercise has a demo** | his full osm-reel line | his face in sync, the app's exercise demo videos, gym footage | ~20 s + end card |
| 3 | **Swap it** | none (music-led) | Coverr food clips + the real diet screen with the swap list | ~14.5 s + end card |
| 4 | **Daily challenge** | none (music-led) | gym footage + challenge, points rules, badges screens | ~14.5 s + end card |
| 5 | **The scale isn't the whole story** | his n3-scale take | his face in sync, gym footage, the Progress screen | ~19 s + end card |
| 6 | **Calorie Calculator** | his calorie-calculator take | his face in sync, the calculator typed in and showing its 3 targets | ~12 s + end card |

## Sources
- **Voice:** his recorded takes only, cut on word boundaries. Captions are his exact words, from the hand-checked
  transcripts. No AI voice was used. No actor was available, and his own voice is the brand.
  Lines with a trial length or prices were left out; he says "اسبوع فري" in the calculator take, and that line is not used.
- **Gym footage:** the 3 Drive folders from the gym edits (projects/2026-10-15_gym-*), with the same approved looks.
- **App:** `tools/app_record.js` films the real web app (osm.sotech.website) on an iPhone-13-sized screen at 3x
  (1170×2532, 30 fps) from the demo account, **read-only**:
  - nothing was logged, chosen, uploaded or sent, and the Payments screen was never opened;
  - the calculator was typed into but not saved; it is a calculator and has no save;
  - headless Chromium can't decode H.264, so the app's own demo MP4s were served to the page as WebM (same picture)
    and play on screen as they do in the app.
- **Stock:** `tools/stock_coverr.py` uses only Coverr hits with `isAiGenerated: false` and `isPremium: false`.
  The licences and sha256 hashes are in `projects/_mkt/stock/manifest.json` (Coverr License: free for commercial use, no attribution).

## Studio additions
- `voiceTrack` (render_edit): a voice-over track timed to the output replaces the clip-derived dialogue.
- `captions.outputTime`: the caption words are already in output time.
- per-clip `grade`: mixed sources (HDR phone clips, SDR stock and talking heads) in one edit.
- `screenCard.backdrop: "none"`: no blur or darkening behind the phone card.
- `projects/_mkt/promo.py` (the Promo cursor timeline: gym / stock / talk / app / say + graphics).
- `projects/_mkt/bg_night.mp4`: a static Deep Navy → Night background behind the phone card.

## Known limits
- The demo account is nearly empty: 0 points, 0 streak, no badges, and no open check-in. The Reels don't show those
  numbers, and the leaderboard (it shows a participant's name) is not used.
- The talking-head takes for n2/n3 exist only as 720p finished exports, so they are sharp on a phone but softer than
  the 4K takes.
- Stock clips are landscape 1080p cropped to 9:16 and are used for 1.3–2 s at a time.
