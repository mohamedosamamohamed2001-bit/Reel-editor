#!/usr/bin/env python3
"""Builds edit.json for this video. All overlay/SFX times derive from clip frame boundaries (Remotion rounds each
clip to round(dur*fps) frames), so nothing can land between frames or leave a bare frame."""
import json
FPS = 29.97          # composition fps (matches source 30000/1001 closely; renderer rounds per clip with this value)
F = 30000 / 1001     # real frame rate for times
# (src in, src out, framing, role)
Q = dict(zoom=1.32, focusX=0.505, focusY=0.32, settle=1.04)   # the "client" asking (tight)
A = dict(zoom=1.0, focusX=0.48, focusY=0.5, settle=1.04)       # the coach answering (wide)
M = dict(zoom=1.1, focusX=0.49, focusY=0.42, settle=1.04)      # answer, medium
clips_spec = [
    (0.00, 3.40, dict(zoom=[1.18, 1.24], focusX=0.505, focusY=0.34), "hook"),
    (3.40, 4.94, Q, "Q: هو يعني ايه Full Access؟"),
    (4.94, 10.40, A, "A"),
    (10.70, 16.38, dict(zoom=1.0, focusX=0.48, focusY=0.5), "A under Challenges/Points card"),
    (16.38, 18.66, Q, "Q: وعمل Upgrade ازاي بقى؟"),
    (18.66, 26.02, M, "A (+ Website card from 21.38)"),
    (26.40, 28.82, dict(zoom=1.1, focusX=0.49, focusY=0.42), "A under Payments card"),
    (28.82, 30.76, Q, "Q: اممم، وبعدين؟"),
    (30.76, 34.62, dict(zoom=1.1, focusX=0.49, focusY=0.42), "A under proof card"),
    (34.90, 35.72, Q, "Q: بس كده؟"),
    (35.72, 36.62, dict(zoom=[1.0, 1.05], focusX=0.48, focusY=0.5, settle=1.03), "A: بس كده"),
]
clips, starts, fr = [], [], 0
for a, b, framing, note in clips_spec:
    starts.append(fr)
    fr += round((b - a) * FPS)
    clips.append({"src": "main", "in": a, "out": b, **framing})
total_clip_frames = fr

def out(src_t):
    """source time -> output time (seconds), through the cut list"""
    for (a, b, *_), f0 in zip(clips_spec, starts):
        if a <= src_t < b:
            return f0 / F + (src_t - a)
    raise ValueError(src_t)

def t(n):  # frame -> seconds
    return round(n / F, 4)

def snap(x):
    return round(round(x * F) / F, 4)

# ---- screen cards (times relative to card start) ----
cardD_at, cardD_end = t(starts[3]), t(starts[4])
cardW_at, cardW_end = snap(out(21.38)), t(starts[7])
cardP_at, cardP_end = t(starts[8]), t(starts[9])
rel = lambda src_t, at: round(out(src_t) - at, 3)

D = {"type": "screenCard", "at": cardD_at, "dur": round(cardD_end - cardD_at, 4), "src": "rec2", "plate": True,
     "entrance": "tilt", "checks": True, "width": 820, "top": 290,
     "region": {"x": 0, "y": 0.05, "w": 1, "h": 0.68},
     "segments": [{"in": 0.45, "rate": 1, "dur": round(out(12.0) - cardD_at, 3)},
                  {"in": 8.45, "rate": 0.45, "dur": round(cardD_end - out(12.0), 3)}],
     "highlights": [{"at": rel(11.46, cardD_at), "dur": round(out(12.0) - out(11.46), 3), "box": {"x": 0.03, "y": 0.112, "w": 0.94, "h": 0.57}},
                    {"at": rel(12.54, cardD_at), "dur": 1.8, "box": {"x": 0.03, "y": 0.118, "w": 0.94, "h": 0.25}}]}
w_pay = round(t(starts[6]) - cardW_at, 3)   # payments page starts at the hidden cut (src 26.40)
W = {"type": "screenCard", "at": cardW_at, "dur": round(cardW_end - cardW_at, 4), "src": "rec1", "plate": True,
     "entrance": "tilt", "checks": True, "width": 860, "top": 290,
     "region": {"x": 0, "y": 0.06, "w": 1, "h": 0.60},
     "segments": [{"in": 2.9, "rate": 0.5, "dur": 3.0},                        # Safari -> OSM splash, slowed
                  {"in": 4.4, "rate": 0.03, "dur": round(w_pay - 3.0, 3)},    # hold the splash (hero starts at 4.5)
                  {"in": 16.4, "rate": 0.3, "dur": round(cardW_end - cardW_at - w_pay, 3)}],
     "highlights": [{"at": rel(27.72, cardW_at), "dur": round(cardW_end - out(27.72) - 0.05, 3), "box": {"x": 0.03, "y": 0.29, "w": 0.94, "h": 0.445}}],
     "masks": [{"at": w_pay, "dur": round(cardW_end - cardW_at - w_pay, 3), "box": {"x": 0.05, "y": 0.888, "w": 0.32, "h": 0.05}}]}
p_final = round(out(32.40) - cardP_at, 3)
P = {"type": "screenCard", "at": cardP_at, "dur": round(cardP_end - cardP_at, 4), "src": "rec1", "plate": True,
     "entrance": "tilt", "checks": True, "width": 860, "top": 290,
     "region": {"x": 0, "y": 0.185, "w": 1, "h": 0.62},
     "segments": [{"in": 16.6, "rate": 0.2, "dur": p_final}, {"in": 19.2, "rate": 0.02, "dur": round(cardP_end - cardP_at - p_final, 3)}],
     "highlights": [{"at": rel(31.2, cardP_at), "dur": round(p_final - rel(31.2, cardP_at), 3), "box": {"x": 0.03, "y": 0.081, "w": 0.94, "h": 0.427}},
                    {"at": p_final, "dur": round(rel(33.42, cardP_at) - p_final, 3), "box": {"x": 0.03, "y": 0.548, "w": 0.94, "h": 0.2}},
                    {"at": rel(33.42, cardP_at), "dur": round(cardP_end - out(33.42) - 0.05, 3), "box": {"x": 0.03, "y": 0.768, "w": 0.94, "h": 0.065}}],
     "masks": [{"at": 0, "dur": p_final, "box": {"x": 0.05, "y": 0.655, "w": 0.32, "h": 0.05}},
               {"at": 0, "dur": p_final, "box": {"x": 0.05, "y": 0.825, "w": 0.32, "h": 0.05}},
               *[{"at": p_final, "dur": round(cardP_end - cardP_at - p_final, 3), "box": {"x": 0.05, "y": y, "w": 0.42, "h": 0.05}} for y in (0.112, 0.283, 0.45)]]}

end_at = t(total_clip_frames)
edit = {
    "title": "OSM — Full Access: how to upgrade (payment on the website)",
    "fps": FPS, "width": 1080, "height": 1920,
    "media": {"main": "source/v6.mp4", "rec1": "source/screen_215516.mp4", "rec2": "source/screen_215700.mp4"},
    "plates": {  # same camera, set and shirt as projects/2026-10-12_calorie-calculator: same verified grade
        "grade": "colorbalance=rs=-0.02:bs=0.025:rm=-0.05:bm=0.015:rh=0.02:gh=0.005:bh=-0.025,curves=all='0/0 0.25/0.235 0.5/0.5 0.75/0.765 1/1'",
        "sharpen": "cas=strength=0.4"},
    "clips": clips,
    "captions": {
        "wordsFile": "work/large/v6.words.json", "karaoke": True, "style": "plate", "maxWords": 3, "maxChars": 23,
        "keywords": ["full access", "upgrade", "payment", "osm.sotech.website"],
        "replaceSeq": [
            {"from": ["واس", "ام", "دوت", "سوتيك", "دوت", "ويب", "سايت"], "to": "osm.sotech.website."},
            {"from": ["الفول", "اكسس؟"], "to": "Full Access؟"}, {"from": ["فول", "اكسس؟"], "to": "Full Access؟"},
            {"from": ["الويب", "سايت"], "to": "Website"}],
        # word starts measured from the audio (onset above -35 dB): the transcript put these inside cut-out pauses
        "replaceAt": [{"at": 10.24, "start": 10.77}, {"at": 25.84, "start": 26.44}, {"at": 34.50, "start": 35.17},
                      {"at": 21.10, "to": "App."}],
        "replace": {"الاب": "App", "لتشالنجز": "Challenges،", "البوينتز": "Points،", "الاكسس": "Access", "اوبجريد": "Upgrade",
                    "البيمنت": "Payment", "الباكتج": "Package", "الفري": "Free،",
                    "أطول": "أطول.", "الاب": "App"},
        # zones start/end 0.05 s early: caption times are exact seconds, cards sit on rounded frame boundaries
        "zones": [{"at": round(cardD_at - 0.05, 4), "dur": round(cardD_end - cardD_at, 4), "top": 0.8},
                  {"at": round(cardW_at - 0.05, 4), "dur": round(cardW_end - cardW_at, 4), "top": 0.77},
                  {"at": round(cardP_at - 0.05, 4), "dur": round(cardP_end - cardP_at, 4), "top": 0.78}]},
    "overlays": [
        {"type": "exerciseTitle", "at": t(starts[1]), "dur": round(t(starts[2]) - t(starts[1]), 4), "title": "Full Access", "eyebrow": "OSM"},
        {"type": "checklist", "at": snap(out(8.24)), "dur": round(t(starts[3]) - snap(out(8.24)), 4),
         "items": [{"at": 0, "text": "نظام التمرين"}, {"at": round(out(8.98) - snap(out(8.24)), 3), "text": "نظام التغذية"}]},
        D, W, P,
        {"type": "endCard", "at": end_at, "dur": 2.5, "cta": "ابدأ مع OSM", "sub": "osm.sotech.website", "reveal": "wipe"},
    ],
    "tail": 2.5,
}
# ---- sound design (frame-locked) ----
cue = lambda at, sound, g, **kw: {"at": round(at, 4), "sound": sound, "gain_db": g, **kw}
c = [cue(0, "thump", -23)]
for i in (1, 4, 7, 9):             # client-voice cuts: quick air in
    c.append(cue(t(starts[i]), "air", -24, lo=2400, hi=700))
for i in (2, 5, 10):               # back to the coach: soft air out
    c.append(cue(t(starts[i]), "air", -25))
c.append(cue(t(starts[1]) + 3 / F, "accent", -22))                 # FULL ACCESS title lands
for it in edit["overlays"][1]["items"]:
    c.append(cue(edit["overlays"][1]["at"] + it["at"], "blip", -18, freq=783.99 if it["at"] == 0 else 987.77))
for card in (D, W, P):
    a = card["at"]
    c += [cue(a, "swell", -17), cue(a + 14 / F, "whoosh_in", -14), cue(a + 14 / F, "thump", -22),
          cue(a + card["dur"] - 9 / F, "whoosh_out", -21)]
    for k, h in enumerate(card["highlights"]):
        c.append(cue(a + h["at"], "blip", -16, freq=[783.99, 880.0, 987.77][k % 3]))
c += [cue(W["at"] + w_pay, "air", -26, dur=0.28, lo=1200, hi=3200),               # jump to Payments
      cue(P["at"] + P["highlights"][2]["at"] + 0.03, "chime", -20)]               # "Submit for review" = done
c += [cue(end_at, "swell", -23, dur=0.5, root=146.83), cue(end_at + 2 / F, "impact", -13), cue(end_at + 18 / F, "click", -26, freq=1800)]
edit["sfx"] = {"cues": sorted(c, key=lambda x: x["at"])}
json.dump(edit, open("edit.json", "w"), ensure_ascii=False, indent=2)
print(f"clip frames {total_clip_frames} ({end_at}s) + end card; cards D {cardD_at}-{cardD_end} W {cardW_at}-{cardW_end} P {cardP_at}-{cardP_end}; {len(c)} sfx cues")
