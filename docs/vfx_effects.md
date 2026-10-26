# Video effects pack (`tools/vfx.py`)

The Claude Video Effects pack (42 face- and matte-aware effects, MIT) is integrated into the studio render. Each effect is a per-frame image
operation on footage. It runs on a clip's **plate** (the JPEG frame sequence `render_edit.py` builds), *before* Remotion adds
captions, titles and overlays. Vendor code is in `vendor/claude-video-effects/` (see its `OSM_NOTES.md`). The OSM status of every effect is in
`tools/vfx_effects.json`.

## Using it in an edit
`edit.json` needs top-level `"plates"`. Add effects per clip. Times are **clip-local output seconds**:
```json
{"src": "main", "in": 12.0, "out": 16.5,
 "vfx": [{"fx": "lean-in", "start": 1.2, "end": 2.4, "zoom": 1.3}]}
```

**What happens in the render:**
- `render_edit.py` validates every `vfx` list before making plates and stops with the reasons if any entry is invalid.
- It then writes a cached, derived plate. Frames outside the effect windows are hard links to the original plate (pixel-identical).
- Renders with `vfx` need `.venv/bin/python tools/render_edit.py …` (OpenCV + onnxruntime). Edits without `vfx` are unchanged and still run on the system `python3`.

**Planning commands:**
- `python3 tools/vfx.py list`: the effects allowed under the OSM rules. Add `--all` to include blocked ones.
- `python3 tools/vfx.py describe NAME`: options, ranges, requirements, OSM conditions and the rule behind each.
- `python3 tools/vfx.py validate projects/<p>/edit.json`: run it at the blueprint stage, before any render.

## OSM status (`tools/vfx_effects.json`)
| Status | Effects |
|---|---|
| **approved** | `lean-in` (fast punch-in on a word) |
| **restricted** (the condition in `describe` must hold, and it must serve the beat) | camera: `locked-on` (no text tag), `slow-push` (no text on screen: background blur) · lighting: `spotlight` (no text, no `look=sparkle`; changes the look, so only on request) · grade: `moody`, `swipe`, `timeline` (only when he asks for a look) · graphics: `todo`, `pause-point`, `reject-stamp`, `scribble`, `checklist`, `tier-list` (his own text, never the default "Claude" content; clear of his head) · ui-mock: `tap`, `reel-frame`, `apple-toggles` (`pos=below` only) · transitions: `uninstall`, `rabbit-hole`, `dot-reveal` (sparingly) · compositing: `noise`, `orbit`, `carousel-spin`, `profile-wall`, `phone-fan`, `check-pills`, `broll-split` (his own thumbnails or b-roll, no prices) · typography: `headline-box` (clear of his head) |
| **blocked** (refused unless the entry has `"osmOverride": "<his approval>"`) | text above or behind his head: `lineup`, `backdrop-word`, `the-bill`, `shortcut-rain`, `countdown-flip`, `cover-star`, `red-collage`, `split-headline`, `pastel-word`, `headline-wall`, `match-cut`, `comment-box` · glow or frosted glass behind text: `glass-widgets`, `liquid-glass-graph`, `led-sign`, `glitter-spotlight` |

The blocks come straight from the locked rules in `CLAUDE.md`: no text on or above his head, behind-the-head titles withdrawn, no blur, haze or glow behind text, natural colour by default, no third-party branding. Several effects duplicate studio features. Prefer the studio version, which is already in OSM style: the clip `zoom`/`settle`/`beats` punch-ins, the `checklist` overlay, `splitStack`/`insetCard`, and the clip `zoom: [from, to]` push.

## Adapter differences from upstream
- **Tracking:** MODNet person matte (studio model) + YuNet face. No MediaPipe, which has no wheel for this Python 3.13 venv.
- **Fonts:** sans and display fonts are remapped to Inter / Barlow Condensed. The serif, hand and mono looks keep the pack's OFL fonts, which are off-brand.
- **Arabic text in effect options is refused.** The pack draws each string in one Latin font. Put Arabic in the Remotion captions or titles instead.
- **8-bit SDR RGB on plates:** the same as every studio plate. HLG/HDR sources go through the plate grade first.
- **Validation:** effect names, aliases and looks, time windows, option types, ranges and enums, OSM policy, and camera-effect order.

## Verification (2026-10-26)
- **`tools/vfx.py selftest`: 27 passed, 0 failed.** It uses synthetic inputs only, no footage and no video render. It covers:
  - the registry matching the engine;
  - the exec hook being disabled;
  - the fonts;
  - 15 validation cases;
  - the MODNet + YuNet tracker;
  - all 42 effects and their looks on synthetic frames at 3 times each;
  - the derived plate (frame count, hard links, cache, original untouched);
  - `render_edit.make_plates` wiring with a stubbed plate maker.
- **Studio typecheck:** passes before and after the change.
- **`py_compile` of `tools/*.py`:** passes before and after (23 → 24 files).
- **`render_edit.py`:** still imports and runs `--help` under the system Python with the effects code untouched. None of the 50 existing `edit.json` files uses `vfx`.
- **Not verified:** how the effects look on real footage, and render speed; neither has been measured. For reference, the studio's MODNet cut-out took about 0.7 s per frame at 512 px. The adapter tracks only frames within ±0.5 s of each effect, at 540 px. Check a still before the first real use.
