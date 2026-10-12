# OSM Video Studio — instructions for Claude Code

This repo is Coach Osama's reusable video-editing studio for **OSM — Osama Strength Method**.
The goal is publication-ready edits that follow the OSM brand, built by a reproducible pipeline.

## Read first, every session
1. `docs/BRAND_VIDEO_SYSTEM.md`: the video design system, the brand compliance checklist, and the open brand conflicts.
2. `brand/tokens.json`: exact colours, fonts, type scale, safe areas and logo rules.
3. The `projects/<name>/project.json` of the video being worked on.

## Layout
```
brand/            logo files (raster, from the brand book), OFL fonts, tokens.json
docs/             brand video system + checklist; per-decision notes
tools/            reusable scripts (QA, probing, audio, rendering)
projects/<name>/  one folder per video: project.json, blueprint.md, transcript, edit source
  source/ work/ renders/   ← git-ignored (footage and renders never go in git)
```

## Environment facts (verified 2026-10-12, cloud container)
- 4 CPU cores, 15 GB RAM, ~31 GB free disk, **no GPU** (NVENC/QSV/VAAPI are listed by FFmpeg but have no hardware).
  Encode with libx264 on the CPU. Iterate on low-res previews and render full resolution only at checkpoints.
- FFmpeg/FFprobe 6.1.1 (libass, drawtext, loudnorm, ebur128, afftdn, arnndn, blackdetect, freezedetect),
  Python 3.13 (numpy, pillow), Node 22, ImageMagick 6, Chromium at /opt/pw-browsers.
- The container is ephemeral. Anything worth keeping must be committed (code/docs) or uploaded (renders).
- The Google Drive connector can search and download the user's files. Never bypass Drive permissions.

## Studio rules
- **Never modify source footage.** Copy it into `projects/<name>/source/`, record its sha256, and work on copies.
- Analyze before acting: probe → transcribe → timecoded map → blueprint → base edit → graphics → audio → render → QA.
- Install only what the current video needs. Record every dependency added (and why) under "Dependencies" below.
- No paid APIs, stock services or subscriptions without the user's explicit approval.
- Captions must be the speaker's exact words (Egyptian Arabic as spoken). Never paraphrase in captions.
- Never alter Coach Osama's face or body. No AI-generated people.
- Run `python3 tools/qa_render.py <render> --expect 1080x1920 --fps 30` on every render, **look at the contact
  sheet and the key frames**, then run the brand checklist. Report what was checked, what was sampled, and what wasn't checked.
- On-screen name is "Coach Osama" until the Mohamed/Mohammed spelling is decided.
  Don't state the free-trial length. No prices or payment steps in app-facing video.

## Tools
- `tools/qa_render.py VIDEO [--expect WxH --fps N --lufs -14 --tp -1]` reports specs, black and frozen frames, loudness,
  true peak, clipping and silences, and makes a contact sheet. Writes `<video>_qa/qa.json`. Exit code 1 on a hard failure.
  Tested against a synthetic clip with planted black, frozen and silent sections (all detected).

## Dependencies
| Dependency | Why | Status |
|---|---|---|
| FFmpeg 6.1 (system) | cutting, encoding, audio processing, QA | pre-installed, verified |
| Inter, Barlow Condensed, IBM Plex Sans Arabic (`brand/fonts`, OFL) | brand typography | downloaded from google/fonts, verified files |

## Decisions log
- 2026-10-12: Brand book v1.0 analysed into `docs/BRAND_VIDEO_SYSTEM.md`. The logo files are raster crops from the PDF
  (dark backgrounds only) until vector files exist.
- The compositor/graphics framework and transcription engine are **not chosen yet**. They will be picked when
  the first footage is analysed. Record the choice and the reason here.

## New video workflow
1. Copy `projects/_template` → `projects/YYYY-MM-DD_slug`, then fill in `project.json` (Drive id, platform, language).
2. Download the source and record its sha256. Probe it with `tools/qa_render.py` (source QA = technical audit).
3. Transcribe it and build a timecoded map (segments, purpose, visual opportunities, risks).
4. Write `blueprint.md`: creative direction, and why it suits this video.
5. Build the edit, render a preview, QA it, fix, then do the final render and QA.
6. Deliver the final file plus a QA summary. Update this file only if the studio itself changed.
