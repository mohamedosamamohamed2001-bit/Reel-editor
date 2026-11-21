"""HYROX pacing Reel (Coach Osama 2026-11-21): "why you get slower in the later runs".

Main footage: 7 talking clips filmed in his car (iPhone HLG 9:16). Story order (his message, nothing changed):
  5614 hook: km 1 in 5 min, km 5 in 7 min | 5616 the problem isn't that you're not fast enough |
  5623 you're not trained to hold your pace under fatigue | 5625 running fast vs repeating it 6-7 times at the same quality |
  5603 you don't just need to be faster, you need to hold your speed the whole race | 5601 that's exactly what to work on |
  5607 CTA: more HYROX videos coming.
His voice = one continuous track on the output timeline (voiceTrack), each line trimmed to its measured voice span (+ breath).
Picture: his face for the hook, the punchlines and the CTA; B-roll from HIS HYROX Cairo race footage (projects/2026-11-15_hyrox_race,
and the Red Bull station run from 2026-11-20) exactly on the words it illustrates. No music (he adds trending audio), SFX only.
Captions: the locked OSM bar (#56A0FB, white), his exact Egyptian words (Whisper large-v3 + medium consensus; dialect fixes noted).

    .venv/bin/python -I projects/2026-11-21_hyrox_pacing/build.py && .venv/bin/python tools/render_edit.py projects/2026-11-21_hyrox_pacing
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "projects/_c5"))
from common import end_card, end_card_sfx, cue, write_edit, END_DUR  # noqa: E402

FPS = 30
fr = lambda t: round(t * FPS) / FPS
# measured voice span per clip (tools: energy onset/offset on the clip's AAC track)
VOICE = {"5601": (0.0, 2.62), "5603": (0.33, 5.04), "5607": (0.0, 4.42), "5614": (0.31, 4.66), "5616": (0.25, 3.0),
         "5623": (0.0, 4.04), "5625": (0.69, 6.5)}
DUR = {"5601": 3.32, "5603": 5.12, "5607": 5.82, "5614": 5.34, "5616": 3.70, "5623": 4.82, "5625": 6.96}
def aac_index(path):
    """index of the stereo AAC stream (iPhone files also carry an undecodable spatial-audio stream, its index varies)"""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index,codec_name",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return next(int(l.split(",")[0]) for l in out.split() if l.endswith(",aac"))
# caption words = his speech (one entry per Whisper word, same count, so the times carry over)
WORDS = {
    "5614": "في الهايروكس أول كيلو بتجري بخمس دقايق، ولما تجري الكيلو الخامس بتجري بسبع دقايق.",
    "5616": "المشكلة مش بالضرورة إنك مش سريع كفاية.",
    "5623": "المشكلة هنا إنك مش متدرب إنك تحافظ على البيس بتاعك تحت التعب.",
    "5625": "فيه فرق كبير جداً إنك تجري بسرعة، وإنك تقدر تكرر ده 6 أو 7 مرات بنفس الكفاءة.",
    "5603": "مش محتاج إنك تبقى أسرع بس، محتاج إن أنت تقدر تحافظ على سرعتك طول السباق.",
    "5601": "بالظبط اللي لازم تشتغل عليه لو إنت بتلعب هايروكس.",
    "5607": "في الفترة الجاية هنزل لكم فيديوهات كتير تساعدكم إنكم تقدروا تطوروا في رياضة الهايروكس.",
}
ORDER = ["5614", "5616", "5623", "5625", "5603", "5601", "5607"]
# B-roll on words [i, j) of a line: (i, j, media, source in, speed, zoom, focusY)
BROLL = {
    "5614": [(4, 7, "r5025", 2.4, 1.0, [1.05, 1.12], .5),          # "بتجري بخمس دقايق": the field running fresh
             (8, 14, "r2149", 3.3, 0.7, [1.0, 1.08], .5)],         # "الكيلو الخامس ... بسبع دقايق": him, later, heavier
    "5623": [(6, 10, "r5026", 9.4, 1.0, [1.45, 1.55], .55),        # "تحافظ على البيس بتاعك": sled push
             (10, 12, "r5058", 8.4, 0.5, [1.55, 1.65], .45)],      # "تحت التعب": wall balls, slow
    "5625": [(4, 7, "r5032", 0.4, 1.0, [1.1, 1.18], .5),           # "إنك تجري بسرعة"
             (11, 13, "r5025", 0.9, 1.0, [1.1, 1.15], .5),         # "6 أو" : repeat 1
             (13, 15, "r5032", 2.2, 1.0, [1.1, 1.15], .5)],        # "7 مرات": repeat 2
    "5603": [(10, 15, "rrun", 0.3, 0.5, [1.0, 1.06], .5)],         # "تحافظ على سرعتك طول السباق": him, steady, slow motion
    "5601": [(6, 9, "r5038", 27.6, 1.0, [1.05, 1.12], .5)],        # "لو إنت بتلعب هايروكس": HYROX CAIRO wall
}
MEDIA = {**{f"t{n}": f"source/IMG_{n}.MOV" for n in ORDER},
         "r5025": "source/r_IMG_5025.MOV", "r5032": "source/r_IMG_5032.MOV", "r2149": "source/r_IMG_2149.mov",
         "r5026": "source/r_IMG_5026.mov", "r5058": "source/r_IMG_5058.mov", "r5038": "source/r_IMG_5038.MOV",
         "r5071": "source/r_IMG_5071.mov", "rrun": "source/r_run5050.mov"}


def whisper(n):
    d = json.loads((P / f"work/tx/e_large-v3_{n}/IMG_{n}.words.json").read_text())
    return [w for s in d["segments"] for w in s["words"]]


def main():
    W = P / "work"; W.mkdir(exist_ok=True)
    clips, words, overlays, cues, voice = [], [], [], [], []
    T = 0.0
    for li, n in enumerate(ORDER):
        on, off = VOICE[n]
        a, b = fr(max(0.0, on - 0.10)), fr(min(DUR[n], off + 0.15))
        L = b - a
        ww = whisper(n); txt = WORDS[n].split()
        assert len(ww) == len(txt), (n, len(ww), len(txt))
        w0, w1 = ww[0]["start"], ww[-1]["end"]
        m = lambda t: on + (t - w0) * (off - on) / (w1 - w0)        # whisper times -> measured voice span
        out_t = lambda t: T + (m(t) - a)
        for k, wd in enumerate(ww):
            words.append({"w": txt[k], "start": round(out_t(wd["start"]), 3), "end": round(out_t(wd["end"]), 3)})
        voice.append((n, a, b, T))
        # picture: talk, with B-roll windows on their words
        cuts = []
        for (i, j, src, sin, sp, z, fy) in BROLL.get(n, []):
            s = fr(out_t(ww[i]["start"]) - 0.04)
            e = fr(out_t(ww[j]["start"]) - 0.04) if j < len(ww) else fr(T + L)
            cuts.append((s, e, src, sin, sp, z, fy))
        t = T
        for k, (s, e, src, sin, sp, z, fy) in enumerate(cuts):
            if s - t > 0.45:
                clips.append({"src": f"t{n}", "in": fr(a + t - T), "out": fr(a + s - T), "zoom": [1.0, 1.04] if li % 2 else [1.04, 1.0],
                              "focusY": .4, **({"tin": {"type": "zoom", "frames": 4}} if clips and clips[-1]["src"].startswith("r") else {})})
            else:
                s = t
            d = e - s
            clips.append({"src": src, "in": sin, "out": round(sin + d * sp, 4), **({"speed": sp} if sp != 1 else {}), "zoom": z,
                          "focusY": fy, "tin": {"type": "whip", "dir": "left" if k % 2 == 0 else "right", "frames": 4}})
            cues.append(cue(s, "whoosh_in", -16))
            if sp < 1:
                cues.append(cue(s + 0.05, "thump", -14, freq=48, dur=0.5))
            t = e
        if T + L - t > 0.05:
            clips.append({"src": f"t{n}", "in": fr(a + t - T), "out": fr(b), "zoom": [1.0, 1.05] if li % 2 == 0 else [1.05, 1.0],
                          "focusY": .4, **({"tin": {"type": "zoom", "frames": 4}} if clips and clips[-1]["src"].startswith("r") else {})})
        if li and not BROLL.get(n):
            cues.append(cue(T, "click", -20))
        T = fr(T + L)
    # motion graphics on the hook's numbers, on the spoken word
    hook = [w for w in words if w["w"] in ("بخمس", "بسبع")]
    overlays.append({"type": "callout", "at": round(hook[0]["start"], 3), "dur": 1.1, "number": "5:00", "unit": "KM 1", "position": "top"})
    overlays.append({"type": "callout", "at": round(hook[1]["start"], 3), "dur": 1.2, "number": "7:00", "unit": "KM 5", "position": "top"})
    cues += [cue(hook[0]["start"], "impact", -13), cue(hook[1]["start"], "impact", -11)]
    # the lesson, as a title card on "بالظبط اللي لازم تشتغل عليه"
    t5601 = next(w for w in words if w["w"] == "بالظبط")["start"]
    overlays.append({"type": "kineticTitle", "at": round(t5601, 3), "dur": 1.5, "eyebrow": "THE GOAL",
                     "lines": [{"text": "HOLD YOUR"}, {"text": "PACE", "accent": True}], "backdrop": True, "motion": "smooth", "depth": True})
    cues += [cue(t5601 - 0.25, "swell", -16, dur=0.5), cue(t5601, "slam", -14)]
    # end card: his end artwork + the OSM pill
    overlays.append(dict(end_card(T), image="brand/end/osm-end-photo.jpg"))
    cues += end_card_sfx(T)
    # voice track
    ins, parts = [], []
    for i, (n, a, b, at) in enumerate(voice):
        ins += ["-i", str(P / MEDIA[f"t{n}"])]
        d = b - a
        parts.append(f"[{i}:{aac_index(P / MEDIA[f't{n}'])}]atrim=start={a:.4f}:duration={d:.4f},asetpts=PTS-STARTPTS,aresample=48000,"
                     f"aformat=channel_layouts=stereo,afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.03):.4f}:d=0.03,"
                     f"adelay={int(round(at * 1000))}:all=1[v{i}]")
    g = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(voice))) + f"amix=inputs={len(voice)}:normalize=0[o]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", g, "-map", "[o]", "-t", f"{T + END_DUR:.3f}",
                    "-c:a", "pcm_s24le", str(W / "vo.wav")], check=True)
    (W / "vo.words.json").write_text(json.dumps({"segments": [{"words": words}]}, ensure_ascii=False))
    edit = {"title": "HYROX pacing", "fps": FPS, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": overlays,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "plateColor": "#56A0FB",
                         "keywordColor": "#FFFFFF", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "keywords": ["البيس", "التعب", "الكفاءة", "السباق"],
                         "replace": {"البيس": "الـPace", "هايروكس.": "HYROX.", "الهايروكس": "الـHYROX", "الهايروكس.": "الـHYROX."},
                         "zones": [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.62}]},
            "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "tail": END_DUR, "voiceTrack": "work/vo.wav",
            "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5", "dialogueLufs": -16.0}
    write_edit(P, edit)
    print(f"T={T:.2f}s + end {END_DUR}s, {len(clips)} clips, {len(words)} words")


if __name__ == "__main__":
    main()
