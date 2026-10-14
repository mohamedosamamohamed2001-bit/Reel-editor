"""OSM Reel: "every exercise in OSM is explained on video" (main talking head + OSM app screen recording as B-roll).

Brief (Coach Osama 2026-10-14): the MAIN video opens and carries the Reel; its speech and timing are untouched
(one continuous take, only punch-ins on the same shot). Converted to 9:16 1080x1920 by cropping (no stretch).
The screen recording is B-roll ONLY, from inside the app (1.6 s on: "Day 1 push" -> play -> demo video), never the
phone's home screen, shown as a phone card while he says "every exercise in OSM is explained on video".
No blur behind text. Future-video rules (docs/OSM_FUTURE_EDITING_RULES.md): smooth readable motion. Titles sit on his white T-shirt
(dark ink): in 9:16 his head fills the top third, and text must never cover his face.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_n6"))
from common2 import END_IMAGE, captions_block, visual  # noqa: E402
from common import DIALOGUE_FX, END_DUR, FPS, Timeline, cue, end_card, end_card_sfx, load_words, make_music, word_time, write_edit  # noqa: E402

P = Path(__file__).resolve().parent
words = load_words(P / "work/tx/main.words.json")
media = {"main": "source/main.mp4", "rec": "source/broll.mp4"}

# one take, kept whole (0 - 17.6 s; speech ends 17.26). Zoom changes only = punch-ins on the same shot.
tl = Timeline()
tl.add("main", 0.00, 5.00, zoom=[1.0, 1.04], focusY=0.36)
tl.add("main", 5.00, 11.90, zoom=[1.04, 1.07], focusY=0.36)       # mostly behind the app card
iC = len(tl.clips); tl.add("main", 11.90, 14.36, zoom=[1.12, 1.14], focusY=0.33, settle=1.16)  # "بشرحك ... بصوتي"
iD = len(tl.clips); tl.add("main", 14.36, 17.60, zoom=[1.0, 1.04], focusY=0.36)
T = tl.total()
o = tl.out
tC, tD = tl.start_of(iC), tl.start_of(iD)

t_online = o(word_time(words, "الأونلاين"))
t_wrong = o(word_time(words, "غلط"))
t_kol = o(word_time(words, "كل"))                 # "كل تمرين في OSM ..."
t_video = o(word_time(words, "مشروح"))
t_voice = o(word_time(words, "بصوتي"))

# B-roll: recording 1.6 s (inside the app) -> 8.5 s, real time. Card from "كل تمرين" for the recording's length.
CARD_AT, CARD_IN, CARD_DUR = round(t_kol - 0.04, 3), 1.6, 6.9
REGION = {"x": 0, "y": 0.035, "w": 1, "h": 0.735}   # no status bar, no tab bar
rel = lambda y: round((y - REGION["y"]) / REGION["h"], 3)

overlays = [
    visual(P, media, "v_phone", "phone1.jpg", t_online - 0.1, t_wrong - t_online - 0.1, mode="card", width=600, top=0.66,
           srcW=1024, srcH=683),  # below the captions, never over his face
    {"type": "stepBadge", "at": round(t_wrong - 0.06, 3), "dur": round(CARD_AT - t_wrong - 0.1, 3), "mark": "✗", "label": "التمرين غلط", "top": 0.15},
    {"type": "screenCard", "at": CARD_AT, "dur": CARD_DUR, "src": "rec", "plate": True, "entrance": "tilt", "checks": True,
     "width": 760, "top": 250, "region": REGION, "segments": [{"in": CARD_IN, "rate": 1, "dur": CARD_DUR}],
     "taps": [{"at": round(2.9 - CARD_IN, 3), "x": 0.5, "y": rel(0.49)}],                      # the real tap on play
     "highlights": [{"at": round(t_video - CARD_AT - 0.05, 3), "dur": 1.7, "box": {"x": 0.07, "y": rel(0.20), "w": 0.86, "h": rel(0.78) - rel(0.20)}}]},
    {"type": "kineticTitle", "at": round(tC + 0.05, 3), "dur": round(tD - tC - 0.1, 3), "eyebrow": "كل تمرين",
     "lines": [{"text": "TIPS"}, {"text": "بصوتي", "accent": True, "size": 120}], "top": 0.67, "motion": "smooth", "ink": "dark"},
    {"type": "kineticTitle", "at": round(tD + 0.05, 3), "dur": round(T - tD - 0.05, 3), "eyebrow": "OSM COACHING",
     "lines": [{"text": "مش هتكون بتتمرن"}, {"text": "لوحدك", "accent": True, "size": 130}], "top": 0.67, "motion": "smooth", "ink": "dark"},
    dict(end_card(T), image=END_IMAGE),
]

cues = [
    cue(0.0, "swell", -16), cue(t_online - 0.1, "whoosh_in", -18),
    cue(t_wrong - 0.06, "thump", -14),
    cue(CARD_AT, "riser", -18, dur=0.35), cue(CARD_AT, "whoosh_in", -12), cue(CARD_AT + 0.25, "click", -19),
    cue(CARD_AT + 2.9 - CARD_IN, "key", -18),                           # the tap
    cue(t_video - 0.05, "blip", -19),
    cue(CARD_AT + CARD_DUR - 0.05, "whoosh_out", -14),
    cue(tC, "impact", -15), cue(t_voice, "chime", -21),
    cue(tD, "whoosh_in", -15),
    *end_card_sfx(T),
]
music = make_music(P, {
    "bpm": 120, "key": "D", "mode": "minor", "style": "drive", "seed": 41,
    "sections": [{"type": "intro", "until": CARD_AT - 1.0}, {"type": "build", "until": CARD_AT, "stop": True},
                 {"type": "drop", "until": tC}, {"type": "groove", "until": T},
                 {"type": "outro", "until": T + END_DUR}],
    "duration": T + END_DUR}, gain_db=-12)

cap = captions_block("work/tx/main.words.json", ["غلط", "osm", "بالفيديو", "بصوتي", "لوحدك"])
cap.pop("anchorPlate")  # no old captions here: captions use the normal zones
cap["replace"] = {"الأونلاين": "Online", "كوتشنج": "Coaching", "التبس": "Tips"}
cap["zones"] = [{"at": CARD_AT - 0.05, "dur": CARD_DUR + 0.05, "top": 0.8}]   # below the phone card

write_edit(P, {
    "title": "OSM: every exercise explained on video", "fps": FPS, "width": 1080, "height": 1920, "media": media,
    "audio": {"main": "source/main.mp4"}, "dialogueFx": DIALOGUE_FX, "dialogueLufs": -16.0,
    # original colours kept: no grade, only a light sharpen after the downscale
    "plates": {"grade": None, "sharpen": "cas=strength=0.25"}, "clips": tl.clips,
    "captions": cap, "overlays": overlays, "sfx": {"cues": cues}, "music": music, "tail": END_DUR,
    "textPlate": "#56A0FB",
})
print(f"T={T:.3f} card {CARD_AT}-{CARD_AT + CARD_DUR:.2f} titles {tC:.2f}/{tD:.2f}")
