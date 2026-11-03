"""Client transformation story (scoliosis, individualized training): marketing Reel built ONLY on real voices.

Voices: source/main_video.mov (his recorded VO + the client's real WhatsApp voice notes, restored 1.5x -> 1x), cut and cleaned by vo.py.
The screen recording itself is NEVER shown (client name / photo / chat). Chat content is rebuilt as anonymous OSM motion scenes
(motion/pieces/scoliosis_story: 3D spine + 2D scenes). Footage: his 7 new clips + B-roll library (IMG_2254/2256/2257).

    python3 projects/2026-11-03_transformation/vo.py
    .venv/bin/python projects/2026-11-03_transformation/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-03_transformation
"""
import json, math, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[0] / "_c5"))
sys.path.insert(0, str(P.parents[0] / "_n6"))
from common import END_DUR, cue, end_card, end_card_sfx, make_music, write_edit  # noqa: E402
from common2 import END_IMAGE  # noqa: E402

GFX = "format=yuv420p"
fr = lambda x: math.floor(x * 30 + 0.5) / 30

# (start, end, media, source in, options) on the OUTPUT timeline (see work/vo_plan.json for the voice takes)
SHOTS = [
    (0.00, 7.40, "m_hook", 0.0, dict(grade=GFX)),                                                        # her: doctor visit / "he was shocked"
    (7.40, 11.00, "b_2254", 0.6, dict(zoom=[1.0, 1.06], focusY=0.4, tin={"type": "flash"})),            # coach intro (walk-in)
    (11.00, 15.32, "m_case", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "left"})),                # "understand the case ... plan for her"
    (15.32, 16.32, "b_2257", 4.3, dict(zoom=[1.04, 1.1], focusY=0.45, tin={"type": "zoom"})),           # music-only training montage
    (16.32, 17.32, "b_8392", 1.2, dict(zoom=[1.02, 1.08], focusX=0.45, tin={"type": "whip", "dir": "right"})),
    (17.32, 18.32, "b_8382", 0.8, dict(zoom=[1.0, 1.06], focusY=0.4, tin={"type": "whip", "dir": "up"})),
    (18.32, 21.25, "m_voice", 0.0, dict(grade=GFX, tin={"type": "zoom"})),                              # her real voice note (anonymous)
    (21.25, 30.35, "m_muscle", 0.0, dict(grade=GFX, tin={"type": "flash"})),                            # spine + muscles, curve improved
    (30.35, 33.90, "b_8384", 0.4, dict(zoom=[1.0, 1.05], focusY=0.38, tin={"type": "whip", "dir": "left"})),  # "really amazing, coach"
    (33.90, 36.10, "b_8397", 0.6, dict(zoom=[1.02, 1.08], focusY=0.42, tin={"type": "whip", "dir": "right"})),
    (36.10, 38.20, "b_2256", 6.0, dict(zoom=[1.0, 1.06], focusY=0.45, tin={"type": "whip", "dir": "up"})),
    (38.20, 40.30, "b_8381", 0.1, dict(zoom=[1.0, 1.05], focusY=0.4, tin={"type": "zoom"})),
    (40.30, 46.90, "m_years", 0.0, dict(grade=GFX, tin={"type": "flash"})),                             # "never reached this result ... years"
    (46.90, 49.75, "b_8386", 1.0, dict(zoom=[1.0, 1.07], focusY=0.4, tin={"type": "whip", "dir": "left"})),  # his closing: every client is different
    (49.75, 52.35, "m_individual", 0.0, dict(grade=GFX, tin={"type": "zoom"})),
    (52.35, 55.90, "m_cta", 0.0, dict(grade=GFX, tin={"type": "whip", "dir": "up"})),                   # "send me the word تدريب"
]
MEDIA = {**{f"b_{n}": f"source/IMG_{n}.MOV" for n in ("8381", "8382", "8384", "8385", "8386", "8392", "8397", "2256", "2257")},
         "b_2254": "source/IMG_2254.mov",
         **{f"m_{n}": f"work/motion/{n}.mp4" for n in ("hook", "case", "voice", "muscle", "years", "individual", "cta")}}
KEYWORDS = ["الدكتور", "اتصدم", "Scoliosis", "الحالة", "تدريب", "muscles", "تحسن", "تحفة", "سنين", "مختلفة", "علمية", "ووصلتلهاش"]


def main():
    plan = json.loads((P / "work/vo_plan.json").read_text())
    clips = []
    for a, b, key, sin, kw in SHOTS:
        a, b, sin = fr(a), fr(b), fr(sin)
        c = {"src": key, "in": round(sin, 4), "out": round(sin + (b - a), 4)}
        c.update(kw)
        clips.append(c)
    T = sum(round((c["out"] - c["in"]) * 30) for c in clips) / 30          # frame-exact clip total -> end card on the next frame
    assert T >= plan["total"] - 0.05, (T, plan["total"])
    ov = [
        {"type": "lowerLabel", "at": 8.05, "dur": 2.8, "title": "Coach Osama", "eyebrow": "OSM · HEAD COACH", "top": 0.62, "plate": True},
        dict(end_card(T), image=END_IMAGE),
    ]
    cuts = [fr(s[0]) for s in SHOTS[1:]]
    cues = [cue(0.0, "swell", -16, dur=1.2), cue(0.05, "air", -22), cue(0.45, "blip", -24), cue(1.0, "accent", -22)]     # hook: scan starts
    for i in range(6):
        cues.append(cue(0.45 + i * 0.45, "click", -30))                                                                  # scan ticks
    cues += [cue(3.6, "chime", -20), cue(7.40, "impact", -11), cue(7.42, "boom", -15)]
    for a, b, key, sin, kw in SHOTS[2:]:
        t = kw.get("tin", {}).get("type")
        cues.append(cue(fr(a), {"whip": "whip", "flash": "click", "zoom": "whoosh_in"}[t], {"whip": -15, "flash": -12, "zoom": -16}[t]))
    cues += [cue(11.74, "accent", -18), cue(13.68, "accent", -17)]                                  # case steps 01 / 02
    cues += [cue(15.32, "impact", -10), cue(16.32, "thump", -13), cue(17.32, "thump", -13)]       # montage hits
    cues += [cue(18.6, "blip", -20)]                                                                 # voice note play
    cues += [cue(23.25, "swell", -19, dur=1.4), cue(28.15, "chime", -19)]                          # muscle grows / curve improves
    cues += [cue(40.3 + 3.6 + i * 0.25, "thump", -21) for i in range(3)] + [cue(40.3 + 2.5, "accent", -17)]
    cues += [cue(49.75 + 0.55, "click", -20), cue(49.75 + 1.45, "impact", -13)]
    cues += [cue(52.35 + 0.84, "key", -18), cue(52.35 + 1.0, "blip", -18)]
    cues += end_card_sfx(T)
    mus = make_music(P, {"bpm": 100, "key": "D", "mode": "minor", "style": "trap", "seed": 311, "duration": round(T + END_DUR, 3),
                         "sections": [{"type": "intro", "until": 7.4}, {"type": "groove", "until": 15.32}, {"type": "drop", "until": 18.32},
                                      {"type": "break", "until": 40.3}, {"type": "build", "until": 46.9}, {"type": "drop", "until": round(T, 3)},
                                      {"type": "outro", "until": round(T + END_DUR, 3)}]}, gain_db=-12)
    edit = {"title": "Client transformation (scoliosis, individualized training)", "fps": 30, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": ov,
            "shakes": [], "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "music": mus, "tail": END_DUR,
            "voiceTrack": "work/vo.wav", "dialogueLufs": -16.0,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "plateColor": "#56A0FB", "keywordColor": "#FFFFFF", "keywords": KEYWORDS,
                         "zones": [{"at": round(a, 3), "dur": round(b - a, 3), "top": 0.74} for a, b in zip([0.0] + cuts, cuts + [round(T + 0.01, 3)])]}}
    write_edit(P, edit)
    print(f"clips cover {T:.3f}s (VO {plan['total']}s), end card at {T:.3f}")


if __name__ == "__main__":
    main()
