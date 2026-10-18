# OSM Video Studio — instructions for Claude Code

This repo is Coach Osama's reusable video-editing studio for **OSM — Osama Strength Method**.
The goal is publication-ready edits that follow the OSM brand, built by a reproducible pipeline.

## Read first, every session
1. `docs/BRAND_VIDEO_SYSTEM.md`: the video design system, the brand compliance checklist, and the open brand conflicts.
2. `brand/tokens.json`: exact colours, fonts, type scale, safe areas and logo rules.
3. The `projects/<name>/project.json` of the video being worked on.
4. `docs/OSM_FUTURE_EDITING_RULES.md`: Coach Osama's rules for NEW videos (smooth readable caption motion, selective
   premium 3D type, kinetic hierarchy; section 7: NO text on/above his head, NO haze behind text). Additions only; never applied to delivered videos unless asked.

## Layout
```
brand/            logo files (raster, from the brand book), OFL fonts, tokens.json
docs/             brand video system + checklist; reference analysis, implementation plan/report
studio/           Remotion compositor: src/components (brand overlays), src/lib (tokens, fonts, edit schema)
tools/            transcribe, suggest_callouts, render_edit (render+master+QA), qa_render
projects/<name>/  one folder per video: project.json, edit.json, analysis/, documentation/
  source/ work/ renders/ exports/   ← git-ignored (footage, transcripts' audio and renders never go in git)
```

## Environment facts (verified 2026-10-12, cloud container)
- 4 CPU cores, 15 GB RAM, ~31 GB free disk, **no GPU** (NVENC/QSV/VAAPI are listed by FFmpeg but have no hardware).
  Encode with libx264 on the CPU. Iterate on low-res previews and render full resolution only at checkpoints.
- FFmpeg/FFprobe 6.1.1 (libass, drawtext, loudnorm, ebur128, afftdn, arnndn, blackdetect, freezedetect),
  Python 3.13 (numpy, pillow), Node 22, ImageMagick 6, Chromium at /opt/pw-browsers.
- The container is ephemeral. Anything worth keeping must be committed (code/docs) or uploaded (renders).
- The Google Drive connector can search and download the user's files. Never bypass Drive permissions.

## LOCKED BRAND RULE (Coach Osama 2026-10-16, applies to ALL videos until he says otherwise)
- **Caption bar `#56A0FB` (exact hex), caption text WHITE (keyword too, underline kept), original brand font**
  (IBM Plex Sans Arabic 700 / Inter for English, same size and padding). In an edit: `textPlate: "#56A0FB"`,
  `captions.style: "plate"`, `captions.plateColor: "#56A0FB"`, `captions.keywordColor: "#FFFFFF"`, no `light`.
  Presets: `projects/_r16/reel.py` (`CAPTION_BAR`).
- **The approved editing system is locked.** Do not redesign or rebuild it. Change only what he asks for.
- Before rendering, sample a Remotion still (PNG) and confirm the bar pixels are `#56A0FB`.
  This supersedes the white bars of the 2026-10-16 entry in the decisions log.

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
  **Audio is not rendered by Remotion** (`--muted`): the dialogue is cut from the sources with FFmpeg (sample-accurate,
  8 ms fades only at real cuts), gained to −14 LUFS with a peak limiter, re-measured, and muxed once as AAC.
  Clip options: `zoom` (number or [from,to] slow push), `focusX/focusY` (0–1). Top-level `plates` {grade, sharpen}
  pre-frames footage with FFmpeg (always use it for camera footage). Overlay `screenCard` shows an app screen recording
  with `region` crop, re-timed `segments`, `plate: true`, `taps` and speech-synced `highlights`. Caption options:
  `style: "plate"`, `zones` (move captions), `replace` (exact-word fixes, English terms).
  Speed: 4K source, 24 s reel: preview about 3 min, full 1080×1920 about 6–7 min on 4 CPUs.
- `tools/sfx.py` is the in-house sound kit (numpy only, no samples, no licences): air, whoosh_in/out, swell, thump, impact, click,
  key, blip, chime, accent. Each sound has a "hit" sample that lands on the cue time. `edit.json` `sfx.cues` = [{at, sound,
  gain_db, …kwargs}]. Cue times snap to frames. render_edit mixes the bus (HPF 40 Hz, −4 dB @ 2.5 kHz, sidechain-ducked 2:1
  by dialogue) before mastering. `python3 tools/sfx.py DIR` writes every sound for auditioning.
- v3 motion options (all opt-in): `captions.karaoke`, `clip.settle`, `screenCard.entrance:"tilt"` + `checks`, `endCard.reveal:"wipe"`
  (= fade + scale settle, never a mask on the logo).
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
| onnxruntime 1.31 (`.venv`) + UVR-MDX-NET-Voc_FT.onnx (github.com/TRvlvr/model_repo, cached in ~/.cache/osm-models, sha256 534b2070…e111) | `tools/separate.py`: split a finished mix into voice + music bed | verified on 5 videos (clean spectrograms). Demucs weights host (dl.fbaipublicfiles.com) is blocked here (403) |
| scipy 1.18 (`.venv`) | filters for `tools/music.py` | verified |
| opencv-python-headless 5.0.0.93 (`.venv`) | `tools/erase_text.py`: inpaint old burned-in captions away | verified on 18 videos (before/after stills) |
| MODNet ONNX (Xenova/modnet, Apache-2.0) + YuNet ONNX (OpenCV zoo, MIT), ~/.cache/osm-models | person matte for behind-the-head titles; face guard in the eraser | verified on batch 3 stills |
| lucide-react 0.460.0 (`studio/`, ISC) | icons for `IconPop` motion graphics | verified (typecheck, renders) |

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
- 2026-10-12 (first real edit, `projects/2026-10-12_calorie-calculator`): found and fixed in the pipeline:
  Remotion ignores the AAC priming edit list, so dialogue was ~42 ms late → audio now built with FFmpeg (−5 ms measured).
  loudnorm linear mode under-delivered (−15.2 LUFS) → measured gain + limiter loop. `-shortest` with video copy dropped
  4 frames → removed. Caption words are mapped by midpoint (word edges drift past cut points), phrases <0.35 s are merged,
  consecutive English words stay together, and phrases break at caption-zone edges.
- Use the `large-v3` model with `--prompt` vocabulary for final captions (medium misheard "OSM" as "usm").
- A white shirt or bright background needs `captions.style: "plate"` (Night plate). Shadow-only captions are unreadable there.
- No licensed music/SFX library is available. Recommend adding music from Instagram's library at upload.
- 2026-10-12 (v2): **never show footage through `<OffthreadVideo>`.** Its frame extraction measured ~7x softer
  (face Laplacian variance 311 → 44 on the same frame; `<Video>` 151, `<Img>` 343). Footage goes through `plates`:
  FFmpeg crop → grade → Lanczos → CAS into JPEG q1 4:4:4 frame sequences, shown with `<Img>` (FramedVideo/ScreenCard
  handle `frames`). Plates start on the exact source frame (`-ss (first-0.25)/fps`, `-frames:v`). A plain `-ss` was 1 frame late.
  Remotion frames are PNG (JPEG q80 softened text). Caption timing maps through `clip.orig` (source in/out) when plated.
- English terms in Arabic captions stay English (`captions.replace`, e.g. الميثود → Method, الوركاوت → Workout), are set in Inter,
  and each English run is one isolated LTR span (per-word LTR spans reversed "Calories Calculator").
- 2026-10-12 (v3): SFX levels were set by measuring voice-vs-SFX momentary loudness at each cue (not by guessing). Targets
  during speech: minor 22–28 dB under the voice, medium 15–22, major 10–16. Cues >30 dB under are inaudible. A 2:1 sidechain is enough.
- Overlay `at` times must be frame-exact against the clip total: clip lengths round per clip (here 634 frames ≠ 21.18 s × fps),
  and an end card placed at 21.18 s left one bare frame. Put the end card at the first frame after the last clip.
- Never animate a mask/crop over the logo (brand: no cropped letters). Use opacity + uniform scale.
- Grade used on the first studio set (bright, cool-lit, white shirt): `colorbalance=rs=-0.02:bs=0.025:rm=-0.05:bm=0.015:rh=0.02:gh=0.005:bh=-0.025`
  + gentle S-curve + `cas=strength=0.4`. Warming highlights fixes the shirt. Pulling midtone red keeps the skin from going pink.

- 2026-10-13 (collection upgrade, `projects/2026-10-13_c5-*`, `docs/collection_2026-10-13.md`): re-editing FINISHED exports.
  New tools: `separate.py` (voice/music split), `burned_text.py` (find burned-in captions per frame) + `caption_strips.py`
  (read them), `align_words.py` (put the client's approved caption text onto Whisper word times; Whisper large-v3 drifts
  to Standard Arabic and hallucinates outros like "اشتركوا في القناة"; a LONG --prompt made it hallucinate, keep prompts
  to one short dialect sentence), `music.py` (original 120 bpm tracks, sections end exactly on cut times), `track.py`
  (template-matching tracker), `mix_report.py` (voice / ducked music / SFX levels per window, before rendering).
  New edit options: clip `speed` (tmix blur, no interpolation), `freeze`, `hold` (still frame while the dialogue plays,
  hides old light-leak frames), `tin` transitions (whip with sub-frame motion blur + mirrored edges, zoom, flash),
  top-level `covers` (frosted Night plates baked into the plates over old captions; captions anchor onto them),
  `audio` (dialogue from another file), `dialogueFx`, `dialogueLufs` (normalise voice before the mix; separated stems
  ranged −10…−17 LUFS), `music`, `shakes`; overlays `kineticTitle` (+`backdrop` full-frame card under the captions),
  `stepBadge`, `lowerLabel`, `trackedLabel`, `checklist.row`; `--alt-nomusic` writes a voice+SFX version.
  Mix targets that worked: music ≈13 dB under the voice while talking (4:1 duck), SFX transitions −9…−11 dB gain.
- Burned-text detection fails where white garment details sit in the caption band (whey: jacket stripes): use
  speech-span plates of fixed size there. Restrict `--band` when false lines stack above the caption.
- `reverse_hit`/`riser` hit = LAST sample: cue them AT the cut, never before it.
- `pkill -f <pattern>` inside a Bash call can match that call's own command line and kill it: use `pgrep` + `kill PID`.

## Setup in a fresh container
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` and `cd studio && npm ci`.

## New video workflow
1. Copy `projects/_template` → `projects/YYYY-MM-DD_slug`, then fill in `project.json` (Drive id, platform, language).
2. Download the source and record its sha256. Probe it with `tools/qa_render.py` (source QA = technical audit).
3. Transcribe it (`tools/transcribe.py`), fix flagged words by ear, and build a timecoded map (segments, purpose, visual opportunities, risks).
4. Write `blueprint.md`: creative direction, and why it suits this video.
5. Write `edit.json` (cuts + overlays), render with `--preview`, inspect the contact sheet and stills, fix, then do the final render (QA runs automatically).
6. Deliver the final file plus a QA summary. Update this file only if the studio itself changed.
- 2026-10-13 (video 2, `projects/2026-10-13_video2`): Drive files shared "anyone with link" download directly with
  `curl -L "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t"` (the MCP download returns base64,
  unusable for large video). New edit options: `captions.replaceSeq` (merge multi-word phrases, e.g. a spoken URL),
  `captions.replaceAt` (fix/retime ONE word by start time ±0.06 s; use measured audio onsets when whisper drops a word's start),
  `screenCard.masks` (privacy blur, e.g. account numbers), overlay `checklist`, `endCard.sub`.
  Caption zones start 0.05 s before the card so no 1-frame fragment appears. The master limiter now runs at 4× oversampling
  (true peak was −0.3 dBTP at 48 kHz). Blur payment account numbers, emails and personal greetings in screen recordings.
- 2026-10-14 (batch 2 v2, Coach Osama): **no blur / frosted background behind text, ever.** Covers kept as caption
  positions only (`kind: "anchor"`, render_edit draws nothing for them); no `blurMask`. Captions, bars, positions and
  timing unchanged. The end card shows his end artwork `brand/end/osm-end-photo.jpg` (sha256 ee0e9772…1676) via
  `endCard.image` (1080 px wide, `lighten` blends its near-black background into Night) with the CTA pill below;
  it replaces the wordmark file. Template: `projects/_n6/common2.py` (`NO_BLUR`, `END_IMAGE`).
- 2026-10-14 (batch 2 v3, Coach Osama): **old burned-in captions are erased, never covered.** `tools/erase_text.py`
  (OpenCV Telea inpainting, `opencv-python-headless` in `.venv`) masks only the old glyph pixels: white + low-saturation
  + a dark outline within 3 px, inside the cover regions (full width), kept only if the same pixel is text 0.15 s
  before or after (captions are static, clothing stripes move), then line-shaped clusters only (h 8–200 px,
  density 0.08–0.75), grown 4 px. Coloured words need `color_windows` from a colour scan. LaMa (big-lama ONNX) was
  tested and rejected: ~6 s/frame on this CPU (20+ h for a batch). Output is x264 CRF 10, same 60 fps frame count.
- 2026-10-14 (`projects/2026-10-14_osm-reel`, first video under the future rules): `kineticTitle.motion: "smooth"`
  (no slam: eased 14-frame settle, 4-frame stagger, soft exit), `depth` (extruded 3D face + cast shadow) and
  `ink: "dark"` (Night text for light backgrounds). In 9:16 a centred talking head fills the top third: titles at top
  0.13 covered his eyes, so titles go on the T-shirt (dark ink, top ~0.67) and cards below the captions
  (`visualCard.top` is a FRACTION of the height). Screen-recording B-roll starts inside the app (never the home screen).
  Behind-the-head occlusion not attempted yet (needs a tested person-matte step).
- 2026-10-15 (batch 3, 12 videos, `docs/batch3_2026-10-15.md`, preset `projects/_b3/common3.py`): erase_text v2 with a
  YuNet **face guard** (face + beard never touched; text on his face → full-frame title card / cutaway instead),
  behind-the-head titles (`tools/cutout.py` MODNet + `kineticTitle.occlude`), `iconPop` tiles (lucide-react, ISC),
  transitions + SFX on every old cut, held frames over old flashes. Icons/cards go on the chest (top ≥ 0.42 in
  talking-head shots) or full-screen, never over his face. AAC can raise true peak ~1 dB: re-limit if QA flags it.
  Wait loops: never `pgrep -f` a pattern that also matches the waiting command itself.

- 2026-10-15 (batch 3 corrections, Coach Osama): **no text on or above his head** and **no moving blur / haze behind
  text**, for all videos. Studio-wide: no soft box/text shadows, glows or entrance/exit blur on captions, smooth titles
  (hard 3D extrusion kept), badges, labels, icon tiles, checklists. `tools/head_check.py` (renders a text-only and a
  picture-only QA pass via `edit.debugLayer`, YuNet face → forbidden zone = head + column above it) must be clean on
  every render; `render_edit.py --props-only` prepares plates/props for it. Batch-3 fixes: `projects/_b3/head_fix.py`
  (titles over the head removed, other graphics moved under the chin with a solid `plate`), logged per project in
  `headfix.json` and re-applied by `common3.Story.finish`. Behind-the-head `occlude` titles are withdrawn.

- 2026-10-15 (marketing Reels, `docs/marketing_2026-10-15.md`, `projects/_mkt/promo.py`, `projects/2026-10-15_mkt-1..6`):
  - No new filming and no AI voice: narration is his own recorded voice, cut from earlier takes (`voiceTrack`, `captions.outputTime`).
  - The real app is filmed read-only by `tools/app_record.js`. Credentials come only from env vars, the storage state lives in /tmp, H.264 demos are served as WebM, and Payments is never filmed.
  - Stock comes only from `tools/stock_coverr.py` (isAiGenerated false, isPremium false, manifest).
  - Per-clip `grade` mixes HDR, SDR and screen sources. `screenCard.backdrop: "none"` puts the card on `_mkt/bg_night.mp4`.
  - Rebuilding after head_fix: delete `work/overlays.original.json` first, or stale overlays win.
  - Never use the calorie-calculator line with "اسبوع فري" (trial length).
  - The n3/n2 clean exports carry old baked-in graphics after ~1.9 s: use his face only before that point.

- 2026-10-16 (3 landscape takes → 9:16, `docs/reels_2026-10-16.md`, `projects/_r16/reel.py`, `projects/2026-10-16_r1..3`):
  **white caption bars** (`captions.plateColor: "#FFFFFF"`, `light: true` = Night text, Core Blue keyword).
  - His take is the unbroken voice track (output time = source time). Cutaways fill shots "until" a word.
  - Arabic-prefixed English words ("الـApp") render as Arabic prefix + isolated English part. Keep multi-word names as one English run (`replace` "الـApple" → "Apple").
  - When a graphic has no room between his chin and the captions, head_fix removes it: put that beat on a clean brand card (`Reel.card`).
- 2026-10-16 (correction, Coach Osama): the 3 Reels were re-rendered with ONLY the caption colours changed (bar `#56A0FB`,
  white text). The edit.json diff was checked against the approved versions: captions.plateColor / light / keywordColor only.
  A Remotion still was sampled: the bar is exactly #56A0FB. New option: `captions.keywordColor`.
- 2026-10-17 (batch 7, 7 videos, `docs/batch7_2026-10-17.md`, preset `projects/_b7/b7.py`): raw exercise demos in his
  BLUE shirt: titles over the footage go white (`lock(P, blue_shirt=True)`; Core Blue accents and eyebrows vanish into the
  shirt), labels/badges on the solid plate, silent reps kept (`Tip(end=…)`). Handheld selfie with burned-in solid plates:
  `tools/erase_plates.py --matched --neck 0.12 --face-score 0.85`, chunks ≤ 300 frames (550 was OOM-killed).
  A landscape take with his phone screen beside him: alternate his face crop and the panel as a `screenCard` (region of the
  same file), voice unbroken except deliberate cuts (`projects/2026-10-17_b7-6/build.py`). Payment / admin screens are cut.
  When no room is left between his chin and the captions, use `kineticTitle` `backdrop: true` cards (head check skips them).
  Studio/public/media keeps hard links to plates: delete both to free disk.
