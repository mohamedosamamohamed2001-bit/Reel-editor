---
name: osm-reel-cover
description: Mandatory Instagram Reel cover for EVERY finished OSM video (Coach Osama 2026-11-01). Use whenever a video edit in this repo reaches its final render or delivery, or a cover, thumbnail, reel cover or profile grid comes up. The cover is delivered with the video without being asked.
---

# OSM Reel cover (automatic last step of every video)

1. Read `docs/COVER_SYSTEM.md`. The design is fixed (`motion/cover/cover.html`); only the photo and the words change.
2. Write `projects/<p>/cover.json`: his strongest shot from the edit (`frame.media` + source `from`/`to`, or a photo used in the edit),
   a hook from his own words, one accent word, a cyan `TOPIC × TOPIC` eyebrow, chips that match the cited facts exactly.
   Use a different photo from the previous video's cover.
3. `.venv/bin/python tools/make_cover.py projects/<p>`: it must print `"fails": []`.
4. Look at `work/cover/check_sheet.jpg` (cover + profile-grid crop) and a full-res crop of his face. Fix and re-run if anything is off.
5. Copy `renders/<p>_cover.jpg` + `.png` into `deliveries/<name>/` next to the video, push through Git LFS, verify the download,
   attach the JPG, and report the cover together with the video (photo used, headline, checks).
