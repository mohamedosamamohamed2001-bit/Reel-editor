# Implementation Report — 2026-10-12

## 1. Reference analysis
Five third-party fitness Reels were inspected through frame sheets, key frames, scene detection, loudness measurement and
local transcription. They demonstrate an **editing style**, not an app. Full breakdown: `reference-product-analysis.md`.

## 2. Existing project assessment
`Reel-editor` held the OSM brand system, the QA tool and docs from the previous step. No OSM app codebase is in this session,
so app code, subscriptions, payments and points were neither inspected nor changed.

## 3. Technical decisions
See `implementation-plan.md`: Remotion 4.0.525 (pinned), faster-whisper `medium` (local), FFmpeg loudnorm. No paid services.

## 4. What was implemented
- **`studio/`**: a Remotion project. `ReelEdit` renders any `edit.json`: cut list, captions, and overlays
  (`exerciseTitle`, `callout`, `insetCard`, `split`, `endCard`), all on brand tokens and fonts.
- **`tools/transcribe.py`**: word-level transcript JSON + SRT. Low-confidence words are flagged.
- **`tools/render_edit.py`**: links media → renders → two-pass loudness master → QA. `--preview` renders at half size.
- **`tools/suggest_callouts.py`**: proposes number callouts at the moment each number is spoken.

## 5. Changed files
| File | Change |
|---|---|
| `studio/package.json`, `package-lock.json`, `tsconfig.json`, `remotion.config.ts` | new: compositor project, pinned versions, H.264/yuv420p/BT.709 output |
| `studio/src/index.ts`, `Root.tsx`, `ReelEdit.tsx` | new: composition with duration computed from the edit |
| `studio/src/lib/{theme,fonts,motion,edit}.ts(x)` | new: tokens from `brand/tokens.json`, blocking font loader, easing, edit schema + caption remapping |
| `studio/src/components/*.tsx` | new: Captions, ExerciseTitle, Callout, InsetCard, SplitStack, EndCard, Hairlines |
| `studio/public/brand` | symlink to `../../brand` (fonts and logo) |
| `tools/transcribe.py`, `tools/render_edit.py`, `tools/suggest_callouts.py` | new |
| `docs/reference-product-analysis.md`, `implementation-plan.md`, `implementation-report.md` | new |
| `CLAUDE.md`, `.gitignore` | updated: studio usage, dependencies, decisions; ignore node_modules, venv, media |

## 6. Testing results (actually run)
| Check | Result |
|---|---|
| `npx tsc --noEmit` (studio) | **Pass** |
| Remotion smoke still: Inter Black Italic + Arabic shaping | **Pass** (inspected visually) |
| Transcription on 5 videos | **Pass** after two fixes (PyAV decode clash → FFmpeg decode; numpy types → JSON). Arabic detected at ≥0.996 confidence |
| End-to-end render of an internal test edit (reference video A, 2 clips, all 5 overlay types, Arabic captions), preview 540×960 | **Pass**: renders in about 1 min 54 s on 4 CPUs |
| QA on that render | Resolution, fps, no black frames: pass. Loudness **−14.0 LUFS**, true peak **−1.2 dBTP**: pass. "Frozen" 30.2 s→end and silence 29.4 s→end = **the static, silent end card** (intended) |
| Visual check, 20-frame contact sheet + 4 full-res stills | Captions follow cuts. Title, card, split, callout and end card positioned inside safe areas |
| Full-resolution render of the same edit (1080×1920) | **Pass**: yuv420p, 30 fps, −14.0 LUFS, −1.2 dBTP, no black frames. Only "frozen" interval = end card (30.2 s → end) |
| Callout suggester on reference E | 12 candidates. They match the numbers the creator showed on screen (12, 8, 15) |

**Defects found during testing and fixed:**
1. The wordmark JPEG's black box was visible on Night → composited with `lighten` (logo pixels unchanged).
2. Captions could collide with exercise titles → captions moved to 60% height, title anchored above the bottom safe line.
3. Output was full-range `yuvj420p` → forced `yuv420p` BT.709 TV range (verified with ffprobe).
4. Remotion doesn't follow file symlinks in `public/` → media is hard-linked (or copied), so the source stays untouched.

**Not tested:** playback on a phone or inside Instagram,
and anything on Coach Osama's own footage (none supplied yet).

## 7. Remaining issues and limitations
- Captions are only as good as the transcript: **every word must be checked by ear** before publishing. Whisper misheard
  several words in the references (e.g. "كدفك" for "كتفك").
- The callout suggester doesn't detect numbers spoken as words ("العشرة").
- A static end card triggers the QA "frozen" check by design. Read it as INFO when it starts at the end card.
- The wordmark is still a raster crop (780 px source shown at 640 px is fine; larger sizes need the vector redraw).
- F11–F13 (montage beat-sync, grade preset, dialogue cleanup) are deferred until real footage exists.

## 8. Recommended next steps
1. Send the first OSM video. That tunes the grade (F12) and dialogue chain (F13) on real footage.
2. Decide the name spelling and the "Train with a Method." signature (end-card option).
3. Commission the vector wordmark (brand book p.32).
4. Pick a royalty-free music source you're licensed for, if you want music beds or montages (F11).

## 9. Reference → OSM comparison
Reproduced: short-phrase captions, exercise titles, number callouts, inset B-roll cards, split screens, loudness.
Adapted: colours, fonts, glow budget, CTA. Omitted: AI anatomy, neon rotoscoping, translated captions, prices and promo codes. Reasons are in the plan.

## 10. Handover
```
# one-time setup in a fresh container
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd studio && npm ci && cd ..

# per video
cp -r projects/_template projects/2026-10-20_my-video     # put footage in source/
.venv/bin/python tools/transcribe.py projects/<p>/source/main.mp4 --out projects/<p>/work --lang ar
python3 tools/suggest_callouts.py projects/<p>/work/main.words.json      # optional
# write projects/<p>/edit.json (see projects/_template/edit.example.json)
python3 tools/render_edit.py projects/<p> --preview   # fast check
python3 tools/render_edit.py projects/<p>             # final + QA
cd studio && npx remotion studio                       # optional live preview in a browser
```
