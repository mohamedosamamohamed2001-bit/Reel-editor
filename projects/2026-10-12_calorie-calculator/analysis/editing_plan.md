# Editing plan: "Try OSM first" (Calorie Calculator)

**Format:** 9:16, 1080×1920, 29.97 fps (source rate kept), H.264 CRF 18 yuv420p BT.709, AAC 256 kbps 48 kHz.
**Duration:** 23.7 s. **Source of truth:** `edit.json` (render: `python3 tools/render_edit.py projects/2026-10-12_calorie-calculator`).

## Hook: three concepts considered
| Concept | Verdict |
|---|---|
| A. Open on his own question "عايز تجرب OSM قبل ما تشترك معايا؟", tight punch-in with a slow push | **Chosen.** It's a real line, addressed to the viewer, needs no setup, and names the brand in the first second |
| B. Open on the app's calorie results, then the question | Visually strong, but the numbers belong to a sample profile and would read as a promise before any context |
| C. Open on "وهتعرف احتياج جسمك…" | Changes his order and meaning, so rejected |

## Narrative
Hook question → the offer (free week) → "see my method yourself" → the free tool, shown in the real app → the decision. One message: *try it before you decide*.

## Timeline
| Out time | Source | In → Out (src s) | Shot / framing | Graphics and captions | Purpose |
|---|---|---|---|---|---|
| 0.00–2.65 | main | 0.00 → 2.65 | **Tight** 1.20→1.27× slow push, focus (0.505, 0.34) | Captions on Night plate. "OSM" in Core Blue | Hook |
| 2.65–6.06 | main | 2.65 → 6.06 | **Wide** 1.0×, focus (0.48, 0.5). OSM poster in frame | Captions. "OSM" blue | Offer. The scale change refreshes attention |
| 6.06–8.85 | main | 10.58 → 13.37 | **Tight** 1.18×. *Jump cut hidden by the punch-in* | "الميثود" blue | Brand idea: the method |
| 8.85–17.13 | screen (+ main audio) | screen 0.5→2.6 @1×, 3.9→10.1 @3.1×, 10.3→14.48 @1× | **App card** 920 px wide, radius 52, over the blurred, darkened speaker + 112° hairlines | Captions move to 75% height under the card | Show, don't tell: open → type data → gain/lose/maintain, synced to his words |
| 17.13–21.18 | main | 21.65 → 25.70 | **Wide** 1.0→1.08× slow push | Captions | Decision line |
| 21.18–23.68 | — | — | **End card**: wordmark on Night, CTA "ابدأ مع OSM" (Night text on Core Blue) | — | Brand + action |

Cut points sit in measured silences (6.00–6.22 s and 10.48–10.68 s), so no syllable is clipped.

## Strategies
- **B-roll:** only the user-supplied app recording (real product). No stock footage, no AI imagery.
- **Motion graphics:** deliberately restrained (brand: calm, premium; one glow per frame). Card enters with a short ease and scale. Captions pop in 4 frames.
  No exercise title or callouts: there are no exercise names here, and the only numbers are the sample profile's, which shouldn't be presented as claims.
- **Typography:** IBM Plex Sans Arabic Bold, upright, 66 px, Night plate at 80% (his white shirt makes shadow-only captions unreadable).
  Inter for the English words ("Calories Calculator", "for free"). One Core Blue keyword per phrase.
- **Audio:** original dialogue only. Gain to −14 LUFS + peak limiter, verified by re-measurement. **No music or SFX**: no licensed library is
  available in this environment. Add a track from Instagram's built-in music library at upload, at a low level under the voice.
- **Colour:** source kept as is. It's a clean, bright studio look with natural skin. The brand's low-key grade would fight this set, so it wasn't forced.
- **Safe areas:** captions at 60% height (75% under the card), all text between 14% and 86% of the height, max width 80%.

## Known limitations
- Captions need a by-ear check (see `main_footage_analysis.md`).
- There's no second camera angle, so variety comes from punch-ins (max 1.27×, so the 4K source is never visibly upscaled) and the app card.
