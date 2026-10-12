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
docs/             brand video system + checklist; reference analysis, implementation plan/report
studio/           Remotion compositor: src/components (brand overlays), src/lib (tokens, fonts, edit schema)
tools/            transcribe, suggest_callouts, render_edit (render+master+QA), qa_render
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
- `.venv/bin/python tools/transcribe.py VIDEO --out DIR --lang ar` produces word-level `<stem>.words.json` + `.srt` (faster-whisper
  medium, local CPU). It's a **draft**: words with `"check": true` are low confidence. Verify captions by ear.
- `python3 tools/suggest_callouts.py WORDS_JSON [--clips edit.json]` lists number callouts at the moment each number is spoken.
- `python3 tools/render_edit.py projects/<p> [--preview] [--frames A-B]` links media into `studio/public/media/<p>`
  (hard link, source untouched), renders `ReelEdit`, masters audio to −14 LUFS / −1 dBTP (two-pass loudnorm, video copied), then runs QA.
  Edit format: `projects/_template/edit.example.json` and `studio/src/lib/edit.ts`.
  Speed: about 2 min for a 32 s preview (540×960) on 4 CPUs.
- `tools/qa_render.py VIDEO [--expect WxH --fps N --lufs -14 --tp -1]` reports specs, black and frozen frames, loudness,
  true peak, clipping and silences, and makes a contact sheet. Writes `<video>_qa/qa.json`. Exit code 1 on a hard failure.
  Tested against a synthetic clip with planted black, frozen and silent sections (all detected).

## Dependencies
| Dependency | Why | Status |
|---|---|---|
| FFmpeg 6.1 (system) | cutting, encoding, audio processing, QA | pre-installed, verified |
| Inter, Barlow Condensed, IBM Plex Sans Arabic (`brand/fonts`, OFL) | brand typography | downloaded from google/fonts, verified files |
| Remotion 4.0.525 + React 18.3.1 (`studio/`, pinned) | animated overlays, Arabic text shaping via Chromium | verified: smoke still, typecheck, end-to-end render. Licence: free for individuals / companies ≤3 people |
| faster-whisper 1.2.1 (`.venv`, `requirements.txt`) | word-timed transcripts for captions | verified on 5 videos. Audio decoded via FFmpeg because PyAV in this env rejects faster-whisper's `metadata_errors` argument |

## Decisions log
- 2026-10-12: Brand book v1.0 analysed into `docs/BRAND_VIDEO_SYSTEM.md`. The logo files are raster crops from the PDF
  (dark backgrounds only) until vector files exist.
- 2026-10-12: Five reference Reels analysed (`docs/reference-product-analysis.md`). Adopted: 1–3-word captions, exercise
  titles, number callouts on the spoken number, inset B-roll cards, split screens, −14 LUFS. Rejected for OSM: AI/3D anatomy
  (brand: no AI people), neon rotoscoping and particles (effects budget), translated captions without human check, price/promo-code CTAs.
- Compositor = Remotion (Arabic shaping, reusable components). Transcription = faster-whisper medium (free, local).
- Logo on Night uses `mix-blend-mode: lighten` to hide the JPEG's black box. Logo pixels are unchanged.
- Remotion renders full-range yuvj420p by default. The config forces yuv420p + BT.709.
- Remotion does not follow file symlinks in `public/`, so media is hard-linked. (The `public/brand` *directory* symlink works.)
- QA "frozen frames" over a static end card is expected. Treat it as INFO when it starts at the end card.
- Deferred until real footage: colour-grade preset, dialogue cleanup chain, beat-synced montage cutting.

## Setup in a fresh container
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` and `cd studio && npm ci`.

## New video workflow
1. Copy `projects/_template` → `projects/YYYY-MM-DD_slug`, then fill in `project.json` (Drive id, platform, language).
2. Download the source and record its sha256. Probe it with `tools/qa_render.py` (source QA = technical audit).
3. Transcribe it (`tools/transcribe.py`), fix flagged words by ear, and build a timecoded map (segments, purpose, visual opportunities, risks).
4. Write `blueprint.md`: creative direction, and why it suits this video.
5. Write `edit.json` (cuts + overlays), render with `--preview`, inspect the contact sheet and stills, fix, then do the final render (QA runs automatically).
6. Deliver the final file plus a QA summary. Update this file only if the studio itself changed.
