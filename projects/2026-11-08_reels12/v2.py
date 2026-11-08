"""VIDEO 2: "3 things to get faster" (clips labelled 2 + his own running B-roll from the warm-up and clip 1_d).

Fast, beat-locked edit at 120 bpm (a beat = 15 frames): every chapter starts on a bar (4.0 / 8.0 / 12.0 s), his talking takes
alternate punch-ins, B-roll cutaways (120 fps slow motion, speed ramps) every 1-1.5 s, a live speed-curve graph that draws
ACCELERATION then MAX VELOCITY, and an original phonk track (tools/music.py) ducked under his voice. Footage colours untouched.

    python3 projects/2026-11-08_reels12/v2.py [--preview]
"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E  # noqa: E402
from script_words import W, KEYWORDS, BREAKS  # noqa: E402

S = E.snap
P = Path(__file__).resolve().parent

SPINE = [
    dict(src="2_b", a=0.0, b=S("2_b", 3.96)),                      # "الـRunning لوحده مش كفاية، لازم تشتغل على 3 حاجات عشان تزوّد سرعتك في الملعب"
    dict(src="2_a", a=0.0, b=S("2_a", 3.64), at=4.0),              # "أول حاجة الـAcceleration، ودي إنك توصل لسرعة عالية في أقل وقت"
    dict(src="2_d", a=0.0, b=S("2_d", 3.52), at=8.0),              # "تاني حاجة دي الـMaximum Velocity، ودي أقصى سرعة جسمك يقدر يوصل لها"
    dict(src="2_c", a=0.0, b=S("2_c", 7.02), at=12.0),             # "وتالت حاجة هي أهم حاجة اللي هي Running Mechanics..."
    dict(src="2_e", a=0.0, b=S("2_e", 5.14), at=20.5),             # "وده أهم حاجة عشان تعلّم جسمك إزاي يجري صح..."
]
PUNCH, WIDE = (1.28, 1.34), (1.0, 1.08)
PICTURE = [
    dict(src="wu", a=13.6, ramp=[(0.35, 1.6), (9, 0.4)], z=(1.12, 1.18), fy=.45, until=0.7),     # hook: him running at the lens, ramp into slow motion
    dict(sync=True, z=PUNCH, until=2.0),
    dict(src="1_d", a=2.2, speed=0.5, z=(1.1, 1.16), fy=.45, until=2.7),
    dict(sync=True, z=WIDE, until=4.0),
    dict(sync=True, z=PUNCH, tin=("zoomin", 0.25), until=5.2),                                    # 01 ACCELERATION (bar 3)
    dict(src="1_c", a=0.1, speed=0.5, z=(1.05, 1.12), fy=.45, until=6.4),
    dict(sync=True, z=WIDE, until=8.0),
    dict(sync=True, z=PUNCH, tin=("smoothleft", 0.22), until=9.2),                                # 02 MAX VELOCITY (bar 5)
    dict(src="wu", a=12.3, speed=1.0, z=(1.15, 1.22), fy=.45, until=10.4),
    dict(sync=True, z=WIDE, until=12.0),
    dict(sync=True, z=PUNCH, tin=("zoomin", 0.25), until=13.4),                                   # 03 RUNNING MECHANICS (bar 7, the drop)
    dict(src="wu", a=11.8, ramp=[(0.3, 1.0), (9, 0.3)], z=(1.2, 1.26), fy=.45, until=15.0),
    dict(sync=True, z=WIDE, until=16.5),
    dict(src="1_d", a=3.0, speed=0.4, z=(1.15, 1.2), fy=.45, until=18.0),
    dict(sync=True, z=PUNCH, until=19.1),
    dict(src="wu", a=13.0, speed=0.35, z=(1.2, 1.28), fy=.45, tin=("hblur", 0.12), until=20.5),
    dict(sync=True, z=PUNCH, tin=("zoomin", 0.22), until=22.0),                                   # the lesson
    dict(src="wu", a=12.6, speed=0.5, z=(1.15, 1.2), fy=.45, until=22.7),
    dict(sync=True, z=WIDE, until=None),
]
MUSIC = {"bpm": 120, "key": "E", "mode": "minor", "style": "phonk", "seed": 12,
         "sections": [{"type": "drop", "bars": 2}, {"type": "groove", "bars": 2}, {"type": "groove", "bars": 1},
                      {"type": "build", "bars": 1, "stop": True}, {"type": "drop", "bars": 4}, {"type": "groove", "bars": 3},
                      {"type": "outro", "bars": 2}]}


def build(preview=False):
    tl, sp, end_f, total_f = E.plan(SPINE, PICTURE, 2.4)
    ot = lambda src, t: E.out_time(sp, src, t)
    end = end_f / E.FPS
    titles = [
        dict(at=0.08, dur=1.85, lines=["RUNNING", "ISN'T <span class='k'>ENOUGH</span>"], size=124, hit=True),
        dict(at=ot("2_b", 2.06), dur=1.85, lines=["<span class='k'>3</span> THINGS"], eyebrow="TO GET FASTER", size=170, hit=True),
        dict(at=4.0, dur=1.15, lines=["ACCELERATION"], eyebrow="01", size=112, hit=True),
        dict(at=8.0, dur=1.15, lines=["MAX", "<span class='k'>VELOCITY</span>"], eyebrow="02", size=118, hit=True),
        dict(at=12.0, dur=1.3, lines=["THE MOST", "<span class='k'>IMPORTANT</span>"], eyebrow="03", size=112, hit=True),
        dict(at=ot("2_c", 2.2), dur=1.5, lines=["RUNNING", "<span class='k'>MECHANICS</span>"], eyebrow="03", size=116),
        dict(at=ot("2_e", 2.28), dur=1.3, lines=["RUN <span class='k'>RIGHT.</span>"], size=150, hit=True),
        dict(at=ot("2_e", 2.28) + 1.36, dur=end - ot("2_e", 2.28) - 1.38, lines=["FOLLOW", "FOR <span class='k'>MORE</span>"], eyebrow="EACH ONE · ITS OWN VIDEO", size=118),
    ]
    graph = {"top": 1000, "show": [[5.2, 7.95], [9.2, 11.95], [ot("2_c", 3.9), 20.45]],
             "draw": [[5.3, 7.2, 0, 0.42], [9.3, 11.0, 0.42, 1.0], [ot("2_c", 3.9), ot("2_c", 3.9) + 0.6, 0, 1.0]],
             "hl": [[5.6, "acc"], [9.3, "max"], [ot("2_c", 3.9), ""], [ot("2_c", 4.28), "acc"], [ot("2_c", 6.26), "max"], [19.1, "both"]]}
    # no title while the graph card is up (the card is the graphic there)
    titles = [t for t in titles if not any(a < t["at"] + t["dur"] and t["at"] < b for a, b in graph["show"])]
    cue = lambda at, s, g, **k: {"at": round(at, 4), "sound": s, "gain_db": g, **k}
    cues = [cue(0.0, "impact", -10), cue(0.02, "whoosh_in", -14), cue(0.35, "whoosh_out", -18)]
    for s in tl[1:]:                                                    # every picture change gets a move
        t = s["start"] / E.FPS
        if s.get("tin"):
            cues.append(cue(t, "whip" if s["tin"][0] != "zoomin" else "whoosh_in", -13))
        elif not s.get("sync") or s["src"] != "2_e":
            cues.append(cue(t, "whoosh_in" if not s.get("sync") else "air", -19 if not s.get("sync") else -22))
    cues += [cue(t["at"], "slam" if t.get("hit") else "accent", -12 if t.get("hit") else -16) for t in titles]
    cues += [cue(5.3 + i * 0.25, "key", -24) for i in range(8)] + [cue(9.3 + i * 0.25, "key", -24) for i in range(7)]
    cues += [cue(ot("2_c", 4.28), "blip", -18), cue(ot("2_c", 6.26), "blip", -18), cue(19.1, "chime", -18)]
    cues += [cue(10.0, "swell", -16, dur=2.0)]
    cues += [cue(end, "boom", -9), cue(end, "reverse_hit", -14, dur=0.6), cue(end + 0.45, "click", -17)]
    total = total_f / E.FPS
    mspec = dict(MUSIC, duration=round(total, 3))
    mdir = P / "work" / "v2_speed"; mdir.mkdir(parents=True, exist_ok=True)
    (mdir / "music.json").write_text(json.dumps(mspec))
    mwav = mdir / "music.wav"
    subprocess.run([str(E.ROOT / ".venv/bin/python"), str(E.ROOT / "tools/music.py"), str(mdir / "music.json"), str(mwav)], check=True)
    music = {"path": str(mwav), "gain_db": -12, "duck_ratio": 8, "duck_threshold": 0.01, "voice_dip_db": -5}   # measured: music >= 12 dB under his voice in 90% of speech
    W_, tl2, sp2, end_f2, total_f2 = E.render("v2_speed", SPINE, PICTURE, W, KEYWORDS, {"titles": titles, "graph": graph}, breaks=BREAKS)
    return E.encode("v2_speed", W_, tl2, sp2, end_f2, total_f2, cues, music=music, preview=preview)


if __name__ == "__main__":
    out = build(preview="--preview" in sys.argv)
    E.sheet(out, out.with_suffix(".sheet.jpg"), every=0.5)
