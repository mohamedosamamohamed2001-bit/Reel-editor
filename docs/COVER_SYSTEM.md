# OSM Instagram Reel cover system (permanent, Coach Osama 2026-11-01)

**Every finished video ships with its cover.** Nobody has to ask for it: video edit → cover → deliver BOTH.

## Design system (fixed, `motion/cover/cover.html`)
First used on the creatine reel (`motion/pieces/creatine_cover`), now a template. Each cover changes only the photo and the words.
- 1080 × 1920. His photo fills the top ~60 %, then a SOLID Night fade (no blur, no haze) into a hairline grid.
- Core Blue (#56A0FB) viewfinder brackets around his face, two angled blue slashes, cyan eyebrow `TOPIC × TOPIC` (Inter 800 caps).
- Arabic headline, IBM Plex Sans Arabic 700, 134 px, white with ONE Core Blue accent word: his own words / the video's hook.
- Chip row: Barlow numbers (the blue chip carries Night text, never white: brand contrast rule) + one short Arabic line.
- OSM wordmark: top-left on a dark field; on a bright background it moves under the chips (lighten blend needs dark pixels).
- Profile-grid safe area: everything that matters inside the centre 3:4 crop (y 240–1680). No text on or above his head.

## Photo rules
- A frame of HIM from the edited video (the shot as used in the edit) or a photo used in the edit. Never an AI person, never a changed face/body.
- `make_cover.py` picks the sharpest frame with a confident face in the shot's range, applies that clip's own measured grade from
  `work/grades.json` (same colours as the reel), then only crop + uniform scale. Upscale ≤ 1.6× (else pick a closer frame).
- Make each cover different on the profile grid: don't reuse the same photo as the previous cover.

## Words
- Hook = the video's main claim in ≤ 3–4 Arabic words (often his first sentence). Facts in chips must match the cited research
  exactly (e.g. "no consensus", not "no evidence"). No prices, payment steps or free-trial length.

## Run
```
projects/<p>/cover.json   (see the docstring of tools/make_cover.py)
.venv/bin/python tools/make_cover.py projects/<p>     -> renders/<p>_cover.png + .jpg (q97 4:4:4), work/cover/check_sheet.jpg
```
Automatic checks (exit 1 on a failure): size, every text/logo box inside the grid crop, nothing in the head column, the blue chip
samples exactly #56A0FB, upscale limit. Then LOOK at `check_sheet.jpg` (full cover + grid crop) and a full-resolution face crop.
Deliver the JPG (upload) and PNG (lossless) next to the video in `deliveries/<name>/`.

## Log
- 2026-11-01 creatine reel: first cover (studio photo IMG_3324, hand-built piece).
- 2026-11-01 posture reel: first cover from the template (IMG_2258 gym frame at 1.50 s, scale 1.32, logo moved under the chips).
