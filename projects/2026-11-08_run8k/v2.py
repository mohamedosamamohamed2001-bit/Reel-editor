"""VIDEO 2: original creative edit of the 8 KM run: "YOUR MIND vs YOU".

Cold open on the voice of his mind ("بلاش، بلاش تجهد نفسك" from the unused 4922 take), a speed-ramped montage with a racing km
counter (the window for the Instagram song), the run in acts: the start, THE WALL at km 4-7 and the turn ("بس لأ، ما ينفعش"),
the finish (watch at 8 km, the collapse in real 0.5x slow motion from his 60 fps footage, "8 كيلو موت"), and his lesson.
Same HDR-preserving engine (footage colours untouched). No music.

    python3 projects/2026-11-08_run8k/v2.py [--preview]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E  # noqa: E402
from script_words import W, KEYWORDS, BREAKS  # noqa: E402

S = E.snap


def sh(src, a, b, **k):
    return dict(src=src, a=a, b=b, **k)


SHOTS = [
    sh("4922", S("4922", 12.85, side="in"), S("4922", 15.65), z=(1.0, 1.16), fy=0.42),                  # 0 cold open: "بلاش، بلاش تجهد نفسك"
    sh("4919", 0.3, 2.3, speed=1.25, z=(1.06, 1.14), tin=("fadeblack", 0.2)),                          # 1 montage (music window)
    sh("4922", 17.45, 19.05, speed=1.3, z=(1.0, 1.08), tin=("smoothleft", 0.22)),                      # 2
    sh("4924", 18.6, 20.05, speed=1.35, z=(1.1, 1.02), tin=("smoothup", 0.22)),                        # 3
    sh("4922", 19.3, 21.4, speed=1.45, z=(1.0, 1.1), tin=("smoothright", 0.22)),                       # 4
    sh("4923", 14.1, 15.3, speed=1.2, z=(1.08, 1.0), tin=("zoomin", 0.25)),                            # 5
    sh("4915", 0.15, S("4915", 2.85), z=(1.0, 1.06), tin=("fadeblack", 0.24)),                          # 6 ACT 1 "رحلة الـ8 كيلو"
    sh("4920", 0.15, 3.95, z=(1.02, 1.08), tin=("slideup", 0.28)),                                     # 7 "أول 4 كيلو" + watch
    sh("4922", 0.0, S("4922", 3.7), z=(1.0, 1.04), tin=("zoomin", 0.32)),                              # 8 ACT 2 "7 كيلو، بقى كيلو"
    sh("4922", S("4922", 4.15, side="in"), S("4922", 10.95), z=(1.12, 1.12)),                          # 9 "عايز أقول لكم... والعقل بيقول لي خلاص، كده كفاية"
    sh("4922", S("4922", 11.0, side="in"), S("4922", 12.85), z=(1.0, 1.0)),                            # 10 "أسبوع واحد على الكومبتيشن"
    sh("4923", S("4923", 22.4, side="in"), 26.3, z=(1.0, 1.18), tin=("hblur", 0.14)),                  # 11 "فهنا عقلي قال لي خلاص، بس لأ، ما ينفعش"
    sh("4925", 0.2, 5.9, z=(1.0, 1.05), tin=("zoomin", 0.35), cap=False, gain_db=-4),                  # 12 ACT 3 watch: 8 km
    sh("4926", 1.8, 4.6, speed=0.5, z=(1.0, 1.08), tin=("smoothup", 0.3)),                             # 13 the collapse, 0.5x slow motion
    sh("4926", S("4926", 8.75, side="in"), 10.9, z=(1.06, 1.12)),                                      # 14 "8 كيلو موت"
    sh("4924", S("4924", 1.25, side="in"), S("4924", 7.75), z=(1.0, 1.04), tin=("fadeblack", 0.3)),    # 15 ACT 4 "لو في كل لحظة عقلك بيقولك لأ..."
    sh("4924", S("4924", 14.7, side="in"), S("4924", 16.75), z=(1.12, 1.12)),                          # 16 "لأ، صدق نفسك"
    sh("4924", S("4924", 23.7, side="in"), 26.1, z=(1.0, 1.1)),                                        # 17 "بس متخليش عقلك يتغلب عليك"
    sh("4926", S("4926", 28.2, side="in"), 33.25, z=(1.0, 1.12), tin=("smoothup", 0.25)),             # 18 "تحكم في عقلك..."
]


def build(preview=False):
    tl, end_f, total_f = E.plan(SHOTS, 2.4)
    ot = lambda src, t: E.out_time(tl, src, t)
    st = lambda i: tl[i]["start"] / E.FPS
    mont0, mont1 = st(1), st(6)
    titles = [
        dict(at=0.15, dur=st(1) - 0.1, lines=["YOUR MIND", "SAYS <span class='k'>STOP</span>"], eyebrow="KM 4", size=124, top=1060),
        dict(at=mont0 + 0.05, dur=1.4, lines=["8 <span class='k'>KM</span>"], eyebrow="COACH OSAMA · OSM", size=240, top=1000, hit=True),
        dict(at=st(4), dur=mont1 - st(4), lines=["ME", "<span class='k'>VS</span> MY MIND"], size=120, top=1060, hit=True),
        dict(at=st(8) + 0.1, dur=1.6, lines=["THE <span class='k'>WALL</span>"], eyebrow="KM 4 → 7", size=150, top=1100),
        dict(at=ot("4923", 24.8), dur=1.6, lines=["BUT <span class='k'>NO.</span>"], size=200, top=1070, hit=True),
        dict(at=st(12) + 3.6, dur=st(13) - st(12) - 3.6 + 0.6, lines=["8 KM. <span class='k'>DONE.</span>"], size=150, top=1150, hit=True),
        dict(at=ot("4926", 31.15), dur=end_f / E.FPS - ot("4926", 31.15), lines=["CONTROL", "YOUR <span class='k'>MIND</span>"], eyebrow="THE LESSON", size=128, top=1040),
    ]
    titles = E.place_titles(tl, titles)
    hud = {"show": [[mont0 + 1.45, st(6)], [st(7) + 0.3, st(8) + 3.6], [st(12) + 0.3, st(12) + 3.55]], "top": 1532,
           "segments": [[mont0 + 1.5, mont1, 0, 3], [st(7) + 1.0, st(7) + 2.0, 3, 4], [st(8) + 0.4, st(8) + 0.9, 4, 7], [st(12) + 0.4, st(12) + 2.2, 7, 8]]}
    lower = {"at": st(6) + 0.3, "dur": st(7) - st(6) + 0.2, "top": 1532}
    cue = lambda at, s, g, **k: {"at": round(at, 4), "sound": s, "gain_db": g, **k}
    cues = [cue(0.0, "air", -20), cue(0.1, "swell", -18, dur=1.6)]
    cues += [cue(mont0, "impact", -9), cue(mont0 + 0.02, "boom", -12)]
    for i, s in enumerate(tl[2:], 2):
        tin = s.get("tin")
        if tin:
            snd = {"smoothleft": "whip", "smoothright": "whip", "slideup": "whoosh_in", "zoomin": "whoosh_in", "smoothup": "whip", "hblur": "whip", "fadeblack": "air"}[tin[0]]
            cues.append(cue(s["start"] / E.FPS, snd, -14 if snd == "whip" else -17))
    cues += [cue(mont0 + 1.5 + i * 0.3, "key", -22) for i in range(int((mont1 - mont0 - 1.5) / 0.3))]          # counter ticks 0 -> 3
    cues += [cue(st(4), "slam", -11)]
    cues += [cue(st(7) + 1.0 + i * 0.25, "key", -22) for i in range(4)] + [cue(st(7) + 2.0, "blip", -18)]
    cues += [cue(st(8) + 0.4, "blip", -18), cue(st(8) + 0.1, "thump", -16)]
    cues += [cue(ot("4923", 24.8), "slam", -8), cue(ot("4923", 24.82), "boom", -13)]
    cues += [cue(st(12) + 0.4 + i * 0.45, "key", -22) for i in range(4)] + [cue(st(12) + 3.6, "impact", -10), cue(st(12) + 3.62, "chime", -18)]
    cues += [cue(st(13) + 0.2 + i * 0.9, "thump", -16, freq=50, dur=0.4) for i in range(6)]                       # heartbeat under the slow motion
    cues += [cue(st(13) + 0.1, "air", -16)]
    cues += [cue(st(14), "thump", -12)]
    cues += [cue(ot("4924", 24.1), "accent", -16), cue(ot("4926", 31.15), "swell", -15, dur=1.2)]
    cues += [cue(end_f / E.FPS, "reverse_hit", -12, dur=0.7), cue(end_f / E.FPS, "boom", -8), cue(end_f / E.FPS + 0.5, "click", -17)]
    W_, tl2, end_f2, total_f2, spec = E.render("v2_creative", SHOTS, W, KEYWORDS, titles, hud, lower, cues, breaks=BREAKS)
    return E.encode("v2_creative", W_, tl2, end_f2, total_f2, cues, preview=preview)


if __name__ == "__main__":
    out = build(preview="--preview" in sys.argv)
    E.sheet(out, out.with_suffix(".sheet.jpg"))
