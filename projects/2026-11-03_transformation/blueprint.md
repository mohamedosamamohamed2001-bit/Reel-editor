# Blueprint: client transformation (scoliosis · individualized training), 2026-11-03

## Sources (sha256 in source_sha256.txt)
- `main_video.mov` (886×1920, 63.6 s): screen recording. Audio = his VO (0–7.2 s, 55.4–63.6 s) + the client's real WhatsApp voice
  notes (7.2–54.6 s, played at WhatsApp **1.5x**). **Picture never used**: it shows the client's name, photo and chat.
- His new clips IMG_8381/8382/8384/8385/8386/8392/8397 (HEVC HLG, 9:16) + library IMG_2254 (walk-in), 2256 (rower), 2257 (box).

## Creative direction
A real-client story told only by real voices: cold open on her words ("I went to the doctor on Thursday… he was shocked by
the result"), then the coach introduces the case, a music-only training beat, her testimonial, and his closing CTA
("send me the word تدريب"). His own script note is followed: position = **individualized training**, never "treating scoliosis".
Graphics restate the voices; no numbers (degrees, months) are shown because none were verified.

| Out (s) | Voice | Picture |
|---|---|---|
| 0–7.4 | her A + B2 | 3D spine: assessment scan, traced curve vs straight reference |
| 7.4–11.0 | his opening | IMG_2254 walk-in + "Coach Osama · OSM Head Coach" label |
| 11.0–15.3 | his opening | case card (anonymous) → 01 ASSESS → 02 INDIVIDUAL PLAN |
| 15.3–18.3 | music | box / machine / cable hits |
| 18.3–21.3 | her B1 | anonymous voice-note card, waveform = her real voice envelope |
| 21.3–30.4 | her C + D | 3D spine: muscle bands grow, curve eases (partly) |
| 30.4–40.3 | her F + H | his clips 8384 / 8397 / 2256 / 8381 |
| 40.3–46.9 | her J + K | BEFORE (years of trying) vs NOW (individual plan) |
| 46.9–55.9 | his closing | IMG_8386 → one plan out of nine identical programs → DM "تدريب" |
| 55.9–58.3 | – | end card (his end artwork) |

## Motion plan
3D (three.js, `spine3d.html`): physically based vertebrae, Core Blue rim light, eased orbit/dolly; scan = assessment metaphor;
muscle tubes = her doctor's words. 2D (`piece.html`): springs, staggered reveals, one idea per scene. Every cut has a transition
and an SFX hit; music sections follow the story (intro / groove / drop / break / build / drop / outro).

## Privacy
No chat UI, no name, no avatar, no messages, no dates. Her first name is never shown; she says his name ("يا أسامة").
The voice note is rebuilt as an anonymous card ("Name, photo and chat hidden for privacy").

## Colour
`plates.grade: "auto"` (HLG decoded properly); motion scenes are SDR graphics (`format=yuv420p`).

## Risks / to confirm by ear
Caption words chosen from Whisper medium where it drifted (see `vo.py` UNSURE): عايزة, اتصدم, ما وصلت, قعدت, يا كوتش, بخطة.
Unclear phrases were cut (not guessed). Her lines about her doctor are her own testimony; no medical claim is made in graphics.
