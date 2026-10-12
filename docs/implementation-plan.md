# Implementation Plan — reference techniques → OSM video studio

## Where this is implemented, and why
- The references show an **editing style**, not app features (see `reference-product-analysis.md`).
- The only repository in this session is `Reel-editor`, the OSM video studio. **No OSM app codebase is attached**, so no app
  code was inspected or changed. Nothing here touches subscriptions, payments, trials, points or rewards.
- The target is therefore the studio: reusable, brand-compliant building blocks that reproduce what makes the reference reels
  work, adapted to `docs/BRAND_VIDEO_SYSTEM.md`.

## Existing architecture (before this work)
Python/FFmpeg tooling (`tools/qa_render.py`), brand tokens, fonts and logo files in `brand/`, docs, and a project template.
There was no compositor and no transcription.

## Technical decisions
| Need (from references) | Choice | Why / alternatives rejected |
|---|---|---|
| Animated titles, callouts, cards, split screens, Arabic text | **Remotion 4.0.525** (React → Chromium → FFmpeg), pinned | Chromium shapes Arabic correctly (verified: joined letters, shadda, RTL). Components are reusable React. *Rejected:* ASS subtitles (weak for cards and layouts), Pillow (no Arabic shaping without raqm), After Effects (not scriptable here). **Licence:** free for individuals and companies of ≤3 people. Coach Osama qualifies today. A paid company licence is needed if OSM grows past that. |
| Word-timed captions | **faster-whisper `medium`**, local CPU, MIT | Free, offline, word timestamps, good Egyptian Arabic. Audio is decoded with system FFmpeg (works around a PyAV version clash). *Rejected:* paid cloud speech APIs (cost and approval). |
| Audio loudness | FFmpeg two-pass `loudnorm` → −14 LUFS / −1 dBTP | All five references measure −14.1 to −14.6 LUFS. Already installed. |
| QA | existing `tools/qa_render.py` | Reused unchanged. |
| Delivery encoding | H.264 CRF 18, yuv420p, BT.709 TV range, AAC 256k 48 kHz | Standard for Instagram, TikTok and phones. Full-range `yuvj420p` (Remotion's default) was found and fixed. |

## Feature inventory (studio capabilities)
| ID | Feature | Reference evidence | OSM adaptation | Status |
|---|---|---|---|---|
| F1 | Short-phrase captions, 1–3 words | A, D, E (about 62% height) | Brand fonts. Arabic never italic, line-height 1.7. One Core Blue keyword max. Verbatim transcript only | **Done** |
| F2 | Exercise-name title | D (every exercise), A | Inter Black Italic caps, last word Core Blue, cyan eyebrow, blue bar draws in. Arabic → bold upright | **Done** |
| F3 | Number/keyword callout | E (0:07–0:30) | Barlow Condensed numbers. Copper only if `earned` | **Done** |
| F4 | Inset B-roll card | E | Rounded card, Line border, Night-blurred backdrop + 112° hairlines | **Done** |
| F5 | Two-angle split | A 0:28 | Night divider | **Done** |
| F6 | End card + CTA | D, C (adapted) | Untouched wordmark on Night, "ابدأ مع OSM" / "Start with OSM". No prices or promo codes | **Done** |
| F7 | Cut list with caption remapping | all | Captions follow the cuts automatically | **Done** |
| F8 | Loudness mastering | measured | −14 LUFS / −1 dBTP | **Done** |
| F9 | Transcription | needed for F1 | Draft quality; low-confidence words flagged | **Done** |
| F10 | Callout suggestions from spoken numbers | E pattern | `tools/suggest_callouts.py` | **Done** |
| F11 | Beat-synced montage cutting | B | Needs licensed music + beat detection | Deferred until a montage is requested |
| F12 | Colour grade preset | A, D, E | Cool shadows, warm highlights, lifted blacks | Deferred: must be tuned on Osama's real footage |
| F13 | Dialogue cleanup (hum, noise, EQ) | — | Per-footage measurement first | Deferred: depends on the mic and room |
| — | AI/3D anatomy visuals | C | **Omitted:** brand forbids AI-generated people. It would also need paid generation | Omitted |
| — | Neon tracing over machines | A | **Omitted for now:** needs per-shot rotoscoping. It also conflicts with the effects budget | Omitted |
| — | Translated captions | A | Only with a human-checked translation (brand: never machine-translated) | Not automated |
| — | Prices or promo-code end screens | C, D | Brand and iOS rules forbid prices in app-facing content | Omitted |

## Functional requirements (testable)
1. Given `edit.json` with clips, the output duration equals Σ(out−in) + tail (±1 frame).
2. A caption word whose source time was cut out never appears. Remaining words appear at `offset + (t − clip.in)`.
3. Caption phrases have ≤ `maxWords` (default 3) words and ≤ `maxChars` (default 22) characters, and break on pauses over 0.35 s.
4. No caption, title or callout text sits inside the top or bottom 14% (269 px at 1920).
5. Arabic text renders RTL, upright, unspaced, in IBM Plex Sans Arabic. Latin titles render in Inter 900 italic.
6. The end-card CTA text on blue is Night (#0A0F16). The logo is not resized out of proportion and has no glow.
7. Final file: 1080×1920, 30 fps, yuv420p BT.709, −14 ±1 LUFS, true peak ≤ −1 dBTP, no black frames outside intended fades.

## Plan and status
1. Compositor and fonts: install, smoke test, verify Arabic shaping. **Done**
2. Edit schema and timeline (F7). **Done**
3. Components F1–F6. **Done**
4. Render, mastering and QA pipeline (`tools/render_edit.py`). **Done**
5. Test on reference footage (internal only) and fix the defects found. **Done**, see the report
6. First real OSM video: waiting for Coach Osama's footage. F12 and F13 get tuned on it.

**Rollback:** everything is additive (`studio/`, new `tools/`). Delete `studio/` and the three new tools to return to the previous state.
