# v3 upgrade plan: motion graphics and sound design

**Base:** v2 (approved). Cuts, framing, captions text, grade, colour and timing stay exactly as they are.
Everything below is **additive and opt-in** in `edit.json`; `work/edit.v2.json` re-renders v2 unchanged.
Times are output seconds on the 29.97 fps timeline (frame = round(t × 29.97)). Event times were measured,
not guessed: Remotion sequence frames, caption word timestamps, and keystrokes detected in the screen recording.

## Audit: what already works (keep)
- The hook is his own question on a tight push. The structure is clean: offer → Method → app demo → decision → end card.
- Captions: plated, readable, Method/Workout in English, one blue keyword.
- The app card is the visual centrepiece: tap ripple, results highlights synced to تزيد/تخس/تحافظ.
- Grade and sharpness (v2).

## Audit: what feels unfinished
1. **Silence under the visuals.** No sound design at all, so graphics land without weight and the cut into the app feels flat.
2. **Captions animate per phrase.** The spoken word isn't tracked, so the eye isn't led and keywords don't land on the word.
3. **Hard punch cuts** (2.64 s, 6.04 s) on a single static camera read as jump cuts.
4. **The card enters and exits as a 2D fade/scale.** No depth, and the exit is just a fade.
5. **The highlights** say "this one" but don't confirm it.
6. **The end card fades in** with no arrival moment; the strongest beat of the video has no punctuation.

## Timestamped plan (priority order: impact × fit)
| # | Time (s) | Now | Motion upgrade | Sound (layers) | Intent | Implementation |
|---|---|---|---|---|---|---|
| 1 | whole video | phrase captions | **word-synced captions**: upcoming words at 45%, each word lights up on its exact start time (3-frame ease) | none (captions never get SFX) | lead the eye, rhythm with his voice | `Captions` gets per-word times from `groupCaptions` (`karaoke: true`) |
| 2 | 8.40 → 9.31 | 2D fade/scale in | **2.5D entrance**: card rises with a 10° X-tilt settling flat, 1.5% controlled overshoot, shadow deepens | reverse **swell** into an **air whoosh** peaking at card arrival + soft **low thump** at settle (9.31) | the biggest scene change gets the biggest transition | `ScreenCard entrance: "tilt"` + SFX cues |
| 3 | 21.19 → 21.79 | fade-in end card | **logo wipe reveal** (clip mask from centre, logo pixels untouched) + CTA rise | swell from "قرر" into a **deep layered impact** (transient + 55 Hz body + short tail) at logo arrival (21.32), soft **click** as the CTA lands (21.79) | the payoff: strongest audio-visual beat | `EndCard reveal: "wipe"` + SFX |
| 4 | 14.55 / 15.15 / 15.98 | outline + dim | + **check mark draws** on the active card (SVG stroke) | **3 ascending select blips** on the exact highlight frames | confirm each goal as he names it | `ScreenCard` check + SFX |
| 5 | 12.66 | results appear | none (UI already animates) | soft two-note **confirm chime** | reward the data entry | SFX |
| 6 | 11.10–12.66 | sped-up typing | none | 7 **micro key ticks** on the detected keystrokes (−30 dB) | makes the fast-forward feel tactile | SFX |
| 7 | 9.58 / 9.70 | tap ripple, page change | none | **tap click** on the ripple frame + soft **swipe** on the page change | physical UI feedback | SFX |
| 8 | 6.47 | underline draws with the phrase | underline draws **on the word "Method"** | soft **tonal accent** + sub tap | brand word lands on the beat | karaoke timing + SFX |
| 9 | 2.64 / 6.04 | hard punch cuts | **settle**: 4% scale ease-out over 10 frames (camera-like inertia) | very soft **air** under each cut | turn jump cuts into intentional punches | `clip.settle` + SFX |
| 10 | 16.85 → 17.12 | fade out | **exit**: card lifts and tilts away, blur releases onto the speaker | short **air whoosh out** | clean return to the speaker | `ScreenCard` exit |
| 11 | 0.00 / 0.85 | — | — | soft **sub open** at frame 0, quiet **tick** on "OSM" | premium first frame without a logo | SFX |

**Deliberately not added:** music (no licensed library here, and voice-only suits a direct-to-camera offer; add Instagram library
music at upload if wanted), SFX on captions, extra text, HUD/particles/glows (brand effects budget), graphics on the trial
length (brand rule), anything over his face.

## Sound design system
- **All sounds are synthesised in-house** (`tools/sfx.py`, numpy): no third-party samples, so licensing is clean.
- **Layers:** transient (definition) + tonal/texture (character) + sub (weight, major moments only) + short tail.
- **Hierarchy:** major (card in, end card), medium (Method, tap, highlights, confirm), minor (punch air, ticks).
- **Dialogue wins:**
  - The SFX bus is high-passed at 40 Hz, with a −4 dB dip at 2.5 kHz (speech presence).
  - It is **sidechain-ducked by the dialogue**.
  - The final mix goes through the existing measured gain + limiter loop (−14 LUFS / −1 dBTP).
- **Sync:** every cue is a frame time from the visual it belongs to. Each sound defines its own "hit" sample, so whoosh peaks
  and impact transients land on the visual frame, not the file start.
