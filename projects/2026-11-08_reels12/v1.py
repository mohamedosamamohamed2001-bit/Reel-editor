"""VIDEO 1: the RAMP warm-up (clips labelled 1 + the warm-up clip + his 120 fps box-jump clip from the B-roll library).

Story: hook question -> RAMP reveal (R-A-M-P lands letter by letter on the beat while the four phases flash) -> RAISE ->
ACTIVATE -> MOBILIZE -> POTENTIATE, each with his own demo B-roll and its minutes, a RAMP phase bar that fills as he goes ->
"15 MIN" -> better performance, fewer injuries. Phase starts sit on the 120 bpm beat grid; original trap/phonk track ducked under
his voice; footage colours untouched.

    python3 projects/2026-11-08_reels12/v1.py [--preview]
"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E  # noqa: E402
from script_words import W, KEYWORDS, BREAKS  # noqa: E402

S = E.snap
P = Path(__file__).resolve().parent

SPINE = [
    dict(src="1_c", a=S("1_c", 0.78, side="in"), b=S("1_c", 4.9)),                    # "قبل ما تبدأ تجري أو تتمرن، هل بتجهز جسمك صح ولا بتجري على طول؟"
    dict(src="1_h", a=0.0, b=S("1_h", 3.42), at=4.42),                               # "في طريقة للتسخين اسمها RAMP، دي متقسمة لأربع مراحل"  (RAMP lands on 6.0 s)
    dict(src="1_h", a=S("1_h", 5.12, side="in"), b=S("1_h", 6.47)),                   # "دي اللي بتهيئ جسمك للتمرين"
    dict(src="1_b", a=S("1_b", 0.32, side="in"), b=S("1_b", 5.62), at=9.5),           # RAISE: "أول مرحلة اسمها Raise، دي احنا بنعلّي الـHeart Rate بتاعنا، بنعمل مثلًا جري خفيف"
    dict(src="1_b", a=S("1_b", 6.32, side="in"), b=S("1_b", 7.32)),                   # "لقدام"
    dict(src="1_b", a=S("1_b", 8.16, side="in"), b=S("1_b", 8.85)),                   # "لجنب"
    dict(src="1_b", a=S("1_b", 9.58, side="in"), b=S("1_b", 10.76)),                  # "من 3 لـ4 دقايق"
    dict(src="1_g", a=0.0, b=S("1_g", 4.66), at=18.0),                               # ACTIVATE: "تاني مرحلة اسمها Activate، احنا بنأكتف كل العضلات اللي احنا هنحتاجها، يعني مثلًا هنعمل"
    dict(src="1_g", a=S("1_g", 5.4, side="in"), b=S("1_g", 6.66)),                   # "One Leg Squat"
    dict(src="1_a", a=S("1_a", 1.14, side="in"), b=S("1_a", 2.16)),                  # "من دقيقتين لتلاتة"
    dict(src="1_a", a=S("1_a", 2.16, side="in"), b=S("1_a", 6.8), at=25.5),           # MOBILIZE: "في تالت مرحلة احنا بنعمل Mobilize، بنعمل Mobility لكل المفاصل، يعني مثلًا"
    dict(src="1_a", a=S("1_a", 7.3, side="in"), b=S("1_a", 8.05)),                   # "زي كده"
    dict(src="1_a", a=S("1_a", 11.19, side="in"), b=S("1_a", 13.58)),                # "وبرضه ممكن نعمل 90/90"
    dict(src="1_a", a=S("1_a", 21.02, side="in"), b=S("1_a", 23.64)),                # "والمرحلة دي بتاخد من خمس لست دقايق"
    dict(src="1_f", a=0.0, b=S("1_f", 1.92), at=36.5),                               # POTENTIATE: "وآخر مرحلة معانا هتبقى Potentiate"
    dict(src="1_f", a=S("1_f", 3.1, side="in"), b=S("1_f", 11.1)),                   # "هعمل Sprints 20 متر، هعمل أول Sprint مثلًا 70%... 80%... 90%"
    dict(src="1_f", a=S("1_f", 11.12, side="in"), b=S("1_f", 15.6)),                 # "لو أنا هعمل Session فيها Jump ممكن أعمل Pogos"
    dict(src="1_f", a=S("1_f", 16.57, side="in"), b=S("1_f", 17.12)),                # "أو Broad Jump"
    dict(src="1_e", a=0.0, b=S("1_e", 8.66), at=52.0),                               # "آخر مرحلة دي بتاخد من 3 لـ4 دقايق... الربع ساعة... من أي إصابات"
]
PUNCH, WIDE = (1.28, 1.34), (1.0, 1.08)
B = dict(fy=.45)
PICTURE = [
    dict(src="box", a=3.85, ramp=[(0.2, 1.0), (9, 0.35)], z=(1.05, 1.1), **B, until=0.9),        # hook: explosive box jump into slow motion
    dict(sync=True, z=WIDE, until=2.4),                                                             # he runs in, asking
    dict(src="wu", a=39.0, speed=1.3, z=(1.25, 1.3), **B, until=3.05),
    dict(sync=True, z=PUNCH, until=4.42),
    dict(sync=True, z=PUNCH, tin=("zoomin", 0.25), until=6.0),                                     # "...اسمها RAMP"
    dict(sync=True, z=WIDE, until=6.45),
    dict(src="wu", a=12.0, speed=1.2, z=(1.2, 1.25), **B, until=6.8),                              # four phases flash
    dict(src="wu", a=18.5, speed=1.0, z=(1.25, 1.3), **B, until=7.15),
    dict(src="1_a", a=13.0, speed=1.0, z=(1.3, 1.35), fy=.55, until=7.5),
    dict(src="box", a=4.0, speed=0.5, z=(1.05, 1.1), **B, until=7.85),
    dict(sync=True, z=WIDE, until=9.5),
    dict(sync=True, z=PUNCH, tin=("smoothup", 0.22), until=11.6),                                  # RAISE
    dict(src="wu", a=4.5, speed=1.0, z=(1.2, 1.25), **B, until=12.6),
    dict(sync=True, z=WIDE, until=13.7),
    dict(src="wu", a=11.0, speed=1.0, z=(1.15, 1.22), **B, until=15.84),
    dict(src="wu", a=7.0, speed=1.0, z=(1.35, 1.4), fy=.45, until=16.56),
    dict(sync=True, z=PUNCH, until=18.0),
    dict(sync=True, z=WIDE, tin=("zoomin", 0.22), until=19.3),                                    # ACTIVATE
    dict(src="wu", a=30.5, speed=1.0, z=(1.25, 1.3), **B, until=20.6),
    dict(sync=True, z=PUNCH, until=21.8),
    dict(src="wu", a=18.0, speed=1.0, z=(1.25, 1.32), **B, until=23.94),
    dict(sync=True, z=WIDE, until=25.5),
    dict(sync=True, z=PUNCH, tin=("smoothleft", 0.22), until=27.3),                               # MOBILIZE
    dict(src="wu", a=41.0, speed=1.0, z=(1.2, 1.26), **B, until=28.8),
    dict(sync=True, z=WIDE, until=30.16),
    dict(src="1_a", a=7.6, speed=1.0, z=(1.15, 1.2), **B, until=30.93),
    dict(src="1_a", a=12.6, speed=1.3, z=(1.3, 1.36), fy=.55, until=33.36),
    dict(sync=True, z=WIDE, until=36.5),
    dict(sync=True, z=PUNCH, tin=("zoomin", 0.25), until=38.44),                                   # POTENTIATE
    dict(src="wu", a=11.4, speed=1.6, z=(1.15, 1.2), **B, until=39.6),
    dict(sync=True, z=WIDE, until=41.6),
    dict(sync=True, z=PUNCH, until=46.5),                                                           # 70% / 80% / 90%
    dict(src="box", a=0.85, ramp=[(0.25, 1.0), (9, 0.35)], z=(1.05, 1.1), **B, until=48.0),
    dict(sync=True, z=WIDE, until=49.4),
    dict(src="box", a=3.9, ramp=[(0.2, 1.0), (9, 0.35)], z=(1.05, 1.1), **B, until=51.0),
    dict(src="box", a=8.95, speed=0.4, z=(1.08, 1.12), **B, until=52.0),
    dict(sync=True, z=PUNCH, tin=("zoomin", 0.25), until=54.47),
    dict(src="wu", a=12.0, speed=1.0, z=(1.2, 1.25), **B, until=55.13),                            # "الربع ساعة": all four phases
    dict(src="wu", a=19.0, speed=1.0, z=(1.25, 1.3), **B, until=55.8),
    dict(src="1_a", a=14.0, speed=1.0, z=(1.3, 1.35), fy=.55, until=56.47),
    dict(src="box", a=4.0, speed=0.5, z=(1.05, 1.1), **B, until=57.13),
    dict(sync=True, z=WIDE, until=59.47),
    dict(sync=True, z=PUNCH, until=None),
]
MUSIC = {"bpm": 120, "key": "D", "mode": "minor", "style": "trap", "seed": 7,
         "sections": [{"type": "drop", "bars": 1}, {"type": "groove", "bars": 1}, {"type": "build", "bars": 1, "stop": True},
                      {"type": "drop", "bars": 2}, {"type": "groove", "bars": 4}, {"type": "groove", "bars": 4}, {"type": "groove", "bars": 4},
                      {"type": "build", "bars": 2, "stop": True}, {"type": "drop", "bars": 4}, {"type": "groove", "bars": 3},
                      {"type": "break", "bars": 2}, {"type": "drop", "bars": 2}, {"type": "outro", "bars": 2}]}


def build(preview=False):
    tl, sp, end_f, total_f = E.plan(SPINE, PICTURE, 2.4)
    ot = lambda src, t: E.out_time(sp, src, t)
    end = end_f / E.FPS
    ph = [ot("1_b", 1.76), ot("1_g", 0.78), ot("1_a", 3.40), ot("1_f", 1.30)]
    chip = lambda i, at, name, mins: dict(at=at - 0.05, dur=1.6, lines=[f"<span class='k'>{name}</span>"], eyebrow=f"PHASE 0{i}", chip=mins, size=124, hit=True)
    titles = [
        dict(at=0.1, dur=2.2, lines=["WARM-UP", "<span class='k'>RIGHT?</span>"], size=130, hit=True),
        chip(1, ph[0], "RAISE", "3–4 MIN"), chip(2, ph[1], "ACTIVATE", "2–3 MIN"),
        chip(3, ph[2], "MOBILIZE", "5–6 MIN"), chip(4, ph[3], "POTENTIATE", "3–4 MIN"),
        dict(at=ot("1_g", 5.4), dur=1.3, lines=["ONE-LEG", "<span class='k'>SQUAT</span>"], size=120),
        dict(at=ot("1_a", 12.35), dur=1.5, lines=["<span class='k'>90/90</span>"], size=190, hit=True),
        dict(at=ot("1_f", 4.54), dur=1.4, lines=["<span class='k'>20 M</span> SPRINTS"], size=130, hit=True),
        dict(at=ot("1_f", 7.38), dur=0.95, lines=["<span class='k'>70%</span>"], size=230, hit=True),
        dict(at=ot("1_f", 9.18), dur=0.95, lines=["<span class='k'>80%</span>"], size=230, hit=True),
        dict(at=ot("1_f", 10.22), dur=1.1, lines=["<span class='k'>90%</span>"], size=230, hit=True),
        dict(at=ot("1_f", 14.44), dur=1.2, lines=["<span class='k'>POGOS</span>"], size=170, hit=True),
        dict(at=ot("1_f", 16.6), dur=1.0, lines=["BROAD", "<span class='k'>JUMP</span>"], size=150, hit=True),
        dict(at=ot("1_e", 2.69), dur=1.9, lines=["<span class='k'>15</span> MIN"], eyebrow="THE WHOLE WARM-UP", size=210, hit=True),
        dict(at=ot("1_e", 5.87), dur=1.55, lines=["BETTER", "<span class='k'>PERFORMANCE</span>"], size=112),
        dict(at=ot("1_e", 7.47), dur=end - ot("1_e", 7.47), lines=["FEWER", "<span class='k'>INJURIES</span>"], size=130, hit=True),
    ]
    reveal = {"at": 6.0, "dur": 1.85, "step": 0.25, "top": 1050}
    ramp = {"show": [[ph[0] - 0.4, ot("1_f", 17.1) + 0.4], [ot("1_e", 2.47), ot("1_e", 5.1)]], "phases": ph + [ot("1_e", 2.47)]}
    titles = [t for t in titles if not (reveal["at"] - 0.1 < t["at"] + t["dur"] and t["at"] < reveal["at"] + reveal["dur"])]
    cue = lambda at, s, g, **k: {"at": round(at, 4), "sound": s, "gain_db": g, **k}
    cues = [cue(0.0, "impact", -10), cue(0.02, "whoosh_in", -14), cue(0.2, "thump", -14)]
    for s in tl[1:]:
        t = s["start"] / E.FPS
        if s.get("tin"):
            cues.append(cue(t, "whip" if s["tin"][0] != "zoomin" else "whoosh_in", -13))
        else:
            cues.append(cue(t, "whoosh_in" if not s.get("sync") else "air", -19 if not s.get("sync") else -22))
    cues += [cue(t["at"], "slam" if t.get("hit") else "accent", -12 if t.get("hit") else -16) for t in titles]
    cues += [cue(reveal["at"] + 0.25 * k, "impact" if k == 0 else "thump", -11 if k == 0 else -15) for k in range(4)]
    cues += [cue(p, "blip", -17) for p in ph]
    cues += [cue(4.0, "swell", -16, dur=2.0), cue(34.0, "swell", -16, dur=4.0)]
    cues += [cue(end, "boom", -9), cue(end, "reverse_hit", -14, dur=0.6), cue(end + 0.45, "click", -17)]
    total = total_f / E.FPS
    mdir = P / "work" / "v1_ramp"; mdir.mkdir(parents=True, exist_ok=True)
    (mdir / "music.json").write_text(json.dumps(dict(MUSIC, duration=round(total, 3))))
    mwav = mdir / "music.wav"
    subprocess.run([str(E.ROOT / ".venv/bin/python"), str(E.ROOT / "tools/music.py"), str(mdir / "music.json"), str(mwav)], check=True)
    music = {"path": str(mwav), "gain_db": -9, "duck_ratio": 4, "voice_dip_db": -4}
    W_, tl2, sp2, end_f2, total_f2 = E.render("v1_ramp", SPINE, PICTURE, W, KEYWORDS, {"titles": titles, "reveal": reveal, "ramp": ramp}, breaks=BREAKS)
    return E.encode("v1_ramp", W_, tl2, sp2, end_f2, total_f2, cues, music=music, preview=preview)


if __name__ == "__main__":
    out = build(preview="--preview" in sys.argv)
    E.sheet(out, out.with_suffix(".sheet.jpg"), every=1.0)
