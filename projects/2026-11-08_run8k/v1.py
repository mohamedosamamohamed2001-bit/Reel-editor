"""VIDEO 1: professional re-edit of his "ME" edit (same idea, same order of the run), tightened and finished.

ME (101 s) = 4915, 4919, 4920, 4923, 4924, 4925, 4926 back to back. Here: a hook from the finish ("8 كيلو موت") and a rewind to
km 0, the same story in his order, breaths and dead air removed (jump cuts disguised by alternating punch-ins), a km HUD,
his key lines as titles, sound design on every move, OSM end card. No music (one Instagram song is recommended separately).

    python3 projects/2026-11-08_run8k/v1.py [--preview]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E  # noqa: E402
from script_words import W, KEYWORDS  # noqa: E402

S = E.snap
P1, P2 = 1.0, 1.12      # alternating framing for jump cuts inside a take


def sh(src, a, b, **k):
    return dict(src=src, a=a, b=b, **k)


SHOTS = [
    sh("4926", S("4926", 8.75, side="in"), 10.9, z=(1.0, 1.08), fy=0.4),                                         # hook: "8 كيلو موت"
    sh("4926", 2.0, 8.7, rev=True, speed=5.0, mute=True, tin=("hblur", 0.12)),                          # rewind to the start
    sh("4915", 0.15, S("4915", 2.85, side="out"), z=(1.0, 1.06), tin=("fadeblack", 0.24)),                          # "رحلة الـ8 كيلو"
    sh("4919", 0.4, 2.9, z=(1.04, 1.1), tin=("smoothleft", 0.3), gain_db=-6),                           # walk-out (no speech)
    sh("4920", 0.15, 3.95, z=(1.0, 1.05), tin=("slideup", 0.3)),                                        # "أول 4 كيلو" + watch
    sh("4923", 0.0, S("4923", 4.15, side="out"), z=(P1, P1), tin=("zoomin", 0.35)),                                 # "كده خلص 7 كيلو وبقى كيلو واحد"
    sh("4923", S("4923", 4.2, side="in"), S("4923", 9.95), z=(P2, P2)),                                            # "...أنا من الكيلو الرابع وعقلي بيقول لي خلاص"
    sh("4923", S("4923", 10.15, side="in"), S("4923", 14.05), z=(P1, P1)),                                         # "كده كده لسه أسبوع كومبتيشن..."
    sh("4923", S("4923", 15.4, side="in"), S("4923", 17.9), z=(P2, P2)),                                           # "أقول لكم أنا بقالي مثلًا أسبوعين"
    sh("4923", S("4923", 18.7, side="in"), S("4923", 22.1), z=(P1, P1)),                                           # "بتمرن 6 أيام في الأسبوع..."
    sh("4923", S("4923", 22.4, side="in"), 26.3, z=(1.0, 1.14)),                                                   # "فهنا عقلي قال لي خلاص، بس لأ، ما ينفعش"
    sh("4924", S("4924", 1.25, side="in"), S("4924", 7.75), z=(P2, P2), tin=("smoothup", 0.25)),                  # "لو في كل لحظة عقلك بيقولك لأ..."
    sh("4924", S("4924", 7.85, side="in"), S("4924", 14.6), z=(P1, P1)),                                           # "أياً كان في إيه..."
    sh("4924", S("4924", 14.7, side="in"), S("4924", 16.75), z=(P2, P2)),                                          # "لأ، صدق نفسك"
    sh("4924", S("4924", 17.55, side="in"), S("4924", 18.6), z=(P1, P1)),                                          # "واشتغل"
    sh("4924", S("4924", 20.1, side="in"), S("4924", 20.95), z=(P2, P2)),                                          # "واعمل"
    sh("4924", S("4924", 21.9, side="in"), S("4924", 23.65), z=(P1, P1)),                                          # "كل حاجة انت تقدر"
    sh("4924", S("4924", 23.7, side="in"), 26.1, z=(1.0, 1.14)),                                                   # "بس متخليش عقلك يتغلب عليك"
    sh("4925", 0.2, 5.9, z=(1.0, 1.04), tin=("zoomin", 0.35), cap=False),                               # watch: 8 km
    sh("4926", 1.6, S("4926", 8.75, side="out"), z=(1.0, 1.05), tin=("smoothup", 0.3), cap=False),                 # the finish: collapse on the grass
    sh("4926", S("4926", 13.85, side="in"), S("4926", 23.2), z=(P1, 1.06)),                                        # "مش كل حاجة عقلك هيقولك عليها تسمعها..."
    sh("4926", S("4926", 24.85, side="in"), S("4926", 27.6), z=(P2, P2)),                                          # "أي حاجة انت تقدر تعملها، بس"
    sh("4926", S("4926", 28.2, side="in"), 33.25, z=(1.0, 1.1)),                                                   # "تحكم في عقلك..."
]


def build(preview=False):
    tl, end_f, total_f = E.plan(SHOTS, 2.4)
    ot = lambda src, t: E.out_time(tl, src, t)
    st = lambda i: tl[i]["start"] / E.FPS
    rw0, rw1 = st(1), st(2)
    titles = [
        dict(at=0.12, dur=st(1) - 0.12, lines=["8 <span class='k'>KM</span>"], eyebrow="COACH OSAMA · OSM", size=230, top=1010, hit=True),
        dict(at=rw0 + 0.05, dur=rw1 - rw0 + 0.1, lines=["◀◀ KM 0"], size=110, top=1180, hit=True),
        dict(at=ot("4923", 24.8), dur=1.55, lines=["BUT <span class='k'>NO.</span>"], size=190, top=1080, hit=True),
        dict(at=ot("4924", 24.1), dur=2.0, lines=["DON'T LET", "YOUR <span class='k'>MIND</span> WIN"], size=104, top=1080),
        dict(at=st(18) + 3.6, dur=1.9, lines=["8 KM. <span class='k'>DONE.</span>"], size=150, top=1150, hit=True),
        dict(at=ot("4926", 31.15), dur=end_f / E.FPS - ot("4926", 31.15), lines=["YOU BEAT", "YOUR <span class='k'>MIND</span>"], size=120, top=1050),
    ]
    hud = {"show": [[st(3) + 0.2, st(5) + 4.0], [st(18) + 0.3, st(18) + 3.55]], "top": 1240,
           "segments": [[st(3) + 0.3, st(3) + 0.31, 0, 0], [st(4) + 1.0, st(4) + 2.0, 0, 4], [ot("4923", 0.7), ot("4923", 1.2), 4, 7],
                        [st(18) + 0.4, st(18) + 2.2, 7, 8]]}
    lower = {"at": st(2) + 0.3, "dur": st(3) - st(2) + 0.4, "top": 1190}
    C = E.R.__dict__.get("cue") or (lambda at, s, g, **k: {"at": round(at, 4), "sound": s, "gain_db": g, **k})
    cue = lambda at, s, g, **k: {"at": round(at, 4), "sound": s, "gain_db": g, **k}
    cues = [cue(0.0, "boom", -10), cue(0.1, "impact", -12), cue(rw0, "reverse_hit", -14, dur=0.7), cue(rw0 + 0.05, "whoosh_out", -16)]
    cues += [cue(rw0 + 0.1 + i * 0.16, "key", -24) for i in range(7)]
    cues += [cue(rw1, "thump", -12)]
    for i, s in enumerate(tl[1:], 1):
        tin = s.get("tin")
        if tin and i > 1:
            snd = {"smoothleft": "whip", "slideup": "whoosh_in", "zoomin": "whoosh_in", "smoothup": "whip", "hblur": "whip", "fadeblack": "air"}[tin[0]]
            cues.append(cue(s["start"] / E.FPS, snd, -15 if snd == "whip" else -17))
    cues += [cue(st(4) + 1.0 + i * 0.25, "key", -22) for i in range(4)] + [cue(st(4) + 2.0, "blip", -18)]           # km 0 -> 4
    cues += [cue(ot("4923", 0.75), "blip", -18)]                                                                    # km 7
    cues += [cue(ot("4923", 24.8), "slam", -9), cue(ot("4923", 24.82), "boom", -14)]                              # BUT NO.
    cues += [cue(ot("4924", 24.1), "accent", -16)]
    cues += [cue(st(18) + 0.4 + i * 0.45, "key", -22) for i in range(4)] + [cue(st(18) + 3.6, "impact", -11), cue(st(18) + 3.62, "chime", -18)]
    cues += [cue(st(19) + 1.7, "thump", -10), cue(st(19) + 1.72, "bass_drop", -14)]                               # hits the grass
    cues += [cue(st(19) + 2.4 + i * 0.85, "thump", -20, freq=52, dur=0.35) for i in range(5)]                     # heartbeat
    cues += [cue(ot("4926", 31.15), "swell", -16, dur=1.2)]
    cues += [cue(end_f / E.FPS, "reverse_hit", -12, dur=0.7), cue(end_f / E.FPS, "boom", -8), cue(end_f / E.FPS + 0.5, "click", -17)]
    W_, tl2, end_f2, total_f2, spec = E.render("v1_me_reedit", SHOTS, W, KEYWORDS, titles, hud, lower, cues)
    return E.encode("v1_me_reedit", W_, tl2, end_f2, total_f2, cues, preview=preview)


if __name__ == "__main__":
    out = build(preview="--preview" in sys.argv)
    E.sheet(out, out.with_suffix(".sheet.jpg"))
