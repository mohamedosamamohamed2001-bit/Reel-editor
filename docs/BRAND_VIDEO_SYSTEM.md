# OSM — Video Design System & Brand Compliance Checklist

Source: **OSM Brand Guidelines v1.0 (October 2026)**, all 32 pages read, including the page images.
Values are in `brand/tokens.json`. This file turns the book into rules for video.

The book tags how certain each rule is: VERIFIED, SAMPLED, PROPOSED, CONCEPT. **PROPOSED** and
**CONCEPT** items are not approved yet. Where an unapproved item conflicts with something verified,
the verified item wins.

---

## 0. LOCKED CAPTION RULE (Coach Osama, 2026-10-16, permanent)
Applies to every video automatically, until he explicitly asks for a change:
- **Caption background: `#56A0FB`** (official OSM brand blue). This exact hex is mandatory; no other shade.
- **Caption text: white**, every word, including the keyword (the keyword keeps its underline, in white).
- **Font: the approved brand font**, unchanged: IBM Plex Sans Arabic 700 for Arabic, Inter for English terms,
  at the same size, line height and padding.
- **Editing system: locked.** Keep the approved style, timing, transitions, SFX, music, graphics, animations, caption
  timing and positions, and end card. Change any of them only on his explicit request.
- Before every render, check that the caption bar is exactly `#56A0FB`: sample a rendered still (PNG, before encoding).

## 1. What the brand is (what the edit must communicate)

- **Positioning:** "A method, not an app." The app carries the plan, and the coach carries the result.
- **Archetype:** *The Coach.* Disciplined (not rigid), confident (not arrogant), motivating (not hype),
  expert (not academic), approachable, premium (not flashy).
- **Tone dials:** fairly conversational, mostly serious, **calm rather than hype**, simple, very personal.
  Social posts can be "a notch more energetic". The voice itself stays the same.
- **Writing rules:** one message per piece (one hook, one benefit, one action). Numbers beat adjectives.
  Speak to one person ("your plan"). Only real urgency. **At most one emoji**, and only where it adds meaning.
- **Language:** Egyptian Arabic for marketing and client content, keeping English gym terms where people
  actually say them (set, rep, cardio). **Never machine-translated.**
- **Taglines:** the hero line is "Train with a coach, not an app." (live).
  The signature is "Train with a Method. / اتمرّن بنظام." (**pending approval**). The launch CTA is "OSM Coach Osama".
- **Values:** Structure · Honesty · Personal · Consistency · Measured progress.

## 2. How this translates to editing style

| Brand trait | Editing consequence |
|---|---|
| Calm, not hype | Motivated cuts, not constant jump-zooms. No shake, flash frames or whoosh barrage. |
| Premium, not flashy | Restrained motion: short eased moves (≈8–14 frames). One focal point per frame. |
| Expert, not academic | Graphics carry **numbers** (sets, reps, RIR, kg, grams), not paragraphs. |
| Structure / method | Visible structure: numbered points, eyebrow labels, title + blue bar. Consistent placement. |
| Honest | No fake urgency, guarantees, before/after, or invented stats. Graphics only restate what the coach says. |
| Real coaching, real light | Keep real footage dominant. Grade: blacks lifted toward Night, cool shadows, warm highlights, natural skin. |

## 3. Practical design system for video

### Colour roles (strict)
- **Night `#0A0F16`** is the base for graphic backgrounds and plates (about 62% of graphic area).
- **Core Blue `#56A0FB`** is for actions, progress, and the **single** highlighted keyword in a headline.
  Text on Core Blue is always **Night**, never white (white fails at 2.7:1).
- **Method Copper `#C9935F`** is for **earned** moments only: points, streaks, PRs, rewards, winners.
  It never goes on an ordinary button or highlight.
- **Signal Cyan `#7DD2EC`** is for eyebrow labels only.
- **Text White `#E5EBF1`** is for primary text. **Muted `#8C98AA`** is for secondary text.
- **Green, amber and red** are for status only, and always come with a word or icon.

### Typography
- **Titles and hooks:** Inter Black (900) *Italic*, CAPS, tracking −2%, with the short Core Blue bar underneath.
- **Eyebrows:** Inter Bold caps, +22% tracking, Signal Cyan, small.
- **Body text and captions:** Inter Regular/SemiBold, sentence case.
- **Numbers and stats:** Barlow Condensed SemiBold/Bold, tabular figures.
- **Arabic:** IBM Plex Sans Arabic. **Never italic, never letter-spaced.** 1–2 px larger than the
  Latin equivalent, line-height about 1.7, right-aligned, and Western digits (0–9). Italic caps titles become
  **bold upright** Arabic.
- A layout never mixes condensed and wide title styles.

### Captions (spoken subtitles)
- They must be the speaker's exact words (Egyptian Arabic as spoken). No paraphrasing and no invented lines.
- Inter / IBM Plex Sans Arabic in Text White, either on a Night plate (about 75–85% opacity, radius 16–20) or with a
  soft shadow. **One** keyword at a time may switch to Core Blue. Copper is used only if the word is an earned number such as "+20 pts".
- Keep them out of the **top and bottom 14%** of a 9:16 frame and away from the face. Use two lines at most.
- Accessibility rule: every video has captions (Arabic + English where feasible).

### Logo in video
- **End card:** the wordmark JPEG on Night (`#0A0F16`) or a dark, calm photo area. Full clear space, where
  X = half the height of the "O" on every side. Minimum 120 px wide on screen.
- **Corner bug (optional):** the wordmark, bottom-left, with clear space respected and at least 120 px wide.
- **Emblem:** used only as large hero art (≥240 px). Never at icon size, and never side by side with the wordmark.
- **Never:** stretch, recolour, glow, rotate, outline/invert, lower its opacity, crop the letters, retype "OSM" in
  a font, edit the figure, or place it on light, Core Blue or busy backgrounds.
- The current files are **raster crops with a black box baked in**, so they only work on dark backgrounds. A vector
  redraw is pending (book p.32 #03).

### Graphic elements (approved toolkit)
- Diagonal hairline texture at **112°**, 3–5% white, quiet.
- Title bar: cyan eyebrow, Black Italic caps title, short glowing blue bar.
- Cards: radius 16–20, 1 px Line border, Surface fill.
- Status chips, a progress ring, and data bars (copper = PR or target).
- **Effects budget:** one glow per frame at most. **No** lens flares, smoke, particles or light leaks
  outside the emblem artwork. Icons are outline style (Lucide-like, 1.75 px stroke).
- Copper chevron divider: CONCEPT, so use it sparingly and treat it as unapproved.

### Motion principles (derived, since the book doesn't specify motion)
- Ease-out entrances and ease-in exits, about 8–14 frames at 30 fps. Short slides of 24–48 px plus fades. No bounce or elastic.
- The title bar draws left to right *after* the title lands. Numbers may count up (Barlow).
- Graphics enter on the beat of the spoken phrase they restate, and leave when the thought ends.
- Transitions are cuts by default. Short dissolves or match-moves only where they carry meaning.
  No spins, glitches or zoom-blur packs.
- Respect "reduce motion": nothing pulses or glows in a loop.

### Formats and safe areas
- Reels/Stories/TikTok: 1080×1920, 9:16. **No text in the top and bottom 14%** (≈269 px each).
- Feed: 1080×1350 (4:5). YouTube/thumbnail: 16:9. Grid crop: 1:1.
- Reel cover: the centre 1:1 area is the grid-crop safe zone.

### Photography and footage treatment
- Low-key lighting with blacks lifted slightly toward Night, never crushed. Cool shadows and warm highlights.
- **Never alter Coach Osama's face, body or proportions.** No beauty filters, no reshaping, no AI stand-ins.
- Clients only appear with written consent. No stock "smiling fitness model" B-roll.

---

## 4. Brand compliance checklist (run on every video)

### A. Mandatory (a failure blocks delivery)
- [ ] Brand name is exactly **OSM** / **Osama Strength Method**. The tagline's full stops appear only inside the logo artwork.
- [ ] Logo: the wordmark or emblem file is used unaltered (no stretch, recolour, glow, rotation, opacity change, cropping or retyping).
- [ ] Logo sits on Night or a dark, calm area only, with full clear space, at ≥120 px (wordmark) or ≥240 px (emblem).
- [ ] Emblem and wordmark never appear in the same frame.
- [ ] Text on Core Blue is Night, never white.
- [ ] Copper is used only for earned moments (points, streaks, rewards, PRs, winners).
- [ ] Arabic is never italic or letter-spaced, uses Western digits, and is right-aligned with correct shaping.
- [ ] No text in the top or bottom 14% of 9:16 frames. Captions never cover the face.
- [ ] Captions are verbatim: the speaker's real words, with no invented or paraphrased "quotes".
- [ ] No guarantees, miracle timelines, fake urgency, before/after without consent, competitor bashing,
      or invented credentials, client counts or results. Only the credentials the book lists (~7 yrs, B.PE, ISSA CFT +
      Nutrition, Head Coach at DFN Gym, studying NCSC Phase 1).
- [ ] No prices, packages or payment instructions in content meant for the iOS app or App Store.
- [ ] Coach Osama's face and body are unaltered. No AI-generated people.
- [ ] No lens flares, smoke, particles or light leaks. At most one glow per frame.
- [ ] Avoided vocabulary never appears ("guaranteed results", "shred in 30 days", "secret/hack/magic",
      "fat-burning foods", "no excuses", "beast mode", "AI-generated plan", "before/after in 2 weeks", "best coach in Egypt").

### B. Recommended
- [ ] One message per video. Headlines in Inter Black Italic caps with **one** blue keyword at most.
- [ ] Numbers over adjectives (sets, reps, RIR, kg, grams). Grams marked **raw** or **cooked**.
- [ ] Wordmark end card. CTA "Start with OSM / ابدأ مع OSM" or "OSM Coach Osama".
- [ ] 8 px grid, generous margins, one focal point per frame.
- [ ] Grade: cool shadows, warm highlights, blacks lifted toward Night.
- [ ] Emoji: one at most, and only where it means something.
- [ ] Eyebrow labels in cyan for section and context labels.

### C. Optional creative opportunities
- [ ] Diagonal 112° hairline texture on graphic plates.
- [ ] Barlow Condensed counters for stats (e.g. "4 × 8", "+20 pts").
- [ ] Progress ring or data bars for progress or tracking stories.
- [ ] Copper chevron divider (CONCEPT, unapproved, use rarely).
- [ ] App screen inserts (Today, workout, challenge), following the iOS caution below.

---

## 5. Open conflicts and how I handle them (until you decide)

| Issue (book page) | Safest interpretation used |
|---|---|
| Name spelling "Mohamed" vs "Mohammed" is undecided (p.4, p.32) | On-screen name: **"Coach Osama"** only, until you choose. |
| Signature "Train with a Method." is pending approval (p.12, p.31) | Used only on the end card when appropriate, and flagged in the delivery notes. Removable in one line. |
| Wordmark is a raster crop with a black box (p.13) | Placed on Night or dark footage only, never on light or blue. |
| Fonts are approximated from screenshots (p.18) | Inter + Barlow Condensed + IBM Plex Sans Arabic, as the book recommends. |
| Free-trial length is unverified (p.28) | Never state "7 days" in video copy. |
| iOS external-link and purchase caution (p.24, p.28) | No prices, store links or payment steps in any video destined for the app or App Store. |
