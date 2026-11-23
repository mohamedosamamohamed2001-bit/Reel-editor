"""iFit Reel, version 1 = MAIN (Coach Osama 2026-11-23).

His main take (source/main.MOV: on the plyo box, unboxing the iFit order) is the voice, continuous 0-18.9 s:
  "iFit عاملين حاجة جامدة جداً، عاملين لو انت اشتريت بـ5000 جنيه، بتدخل على سحب نص جنيه دهب، فادخلوا على العرض ده أولاً،
   ثانياً فيه عروض جامدة جداً بسبب Black Friday، ثالثاً ما تنساش كود خصم OSAMA10."
Picture: his take, cut with B-roll on the words it shows: the iFit "OPEN UP" box + his surprised reaction (fun.MOV) on the hook,
iFit's own slot-machine animation (IFIT.mp4, cropped clear of the Instagram UI, text-free part only) on "سحب", the products shown to
camera during his pause, the product close-up on "عروض". OSM graphics: 5,000 EGP callout, GOLD DRAW in Method Copper (brand: copper
= rewards / winners), step badges 01-03 on أولاً/ثانياً/ثالثاً, OSAMA10 code card at the end. Locked caption bar. No music (SFX only).
Ending: the code card (no app outro, no logo screen).

    .venv/bin/python -I projects/2026-11-23_ifit/build_v1.py && .venv/bin/python tools/render_edit.py projects/2026-11-23_ifit
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT / "projects/_c5"))
from common import cue, write_edit  # noqa: E402

FPS = 30
fr = lambda t: round(t * FPS) / FPS
VOICE_END = 18.95
TAIL = 1.6                       # the code card holds after his last word
# his words (one per Whisper large-v3 word, same count) -> times carry over
SPOKEN = ("iFit عاملين حاجة جامدة جداً، عاملين لو انت اشتريت بـ 5000 جنيه، بتدخل على سحب نص جنيه دهب، فادخلوا على العرض ده "
          "أولاً، ثانياً فيه عروض جامدة جداً بسبب Black Friday، ثالثاً ما تنساش كود خصم OSAMA10.")
MEDIA = {"main": "source/main.MOV", "fun": "source/fun.MOV", "ifit": "work/derived/ifit_clean.mp4", "t54": "source/IMG_5654.MOV"}
# picture plan on the OUTPUT timeline (= main time): (from, to, src, src_in, options)
PLAN = [
    (0.00, 1.05, "fun", 16.05, dict(zoom=[1.0, 1.06])),                          # iFit "OPEN UP" box: "iFit"
    (1.05, 2.55, "fun", 17.75, dict(zoom=[1.05, 1.0], focusY=.35)),              # his reaction: "حاجة جامدة جداً"
    (2.55, 7.40, "main", 2.55, dict(zoom=[1.0, 1.05], focusY=.42)),              # "عاملين لو انت اشتريت بـ5000 جنيه"
    (7.40, 9.40, "ifit", 0.50, dict(grade="null")),                              # "بتدخل على سحب": iFit slot machine
    (9.40, 10.40, "main", 9.40, dict(zoom=[1.06, 1.1], focusY=.4)),              # "نص جنيه دهب"
    (10.40, 12.30, "fun", 5.20, dict(zoom=[1.0, 1.05], focusY=.4)),              # pause: the products to camera
    (12.30, 13.80, "main", 12.30, dict(zoom=[1.0, 1.04], focusY=.42)),           # "العرض ده أولاً"
    (13.80, 15.00, "fun", 11.60, dict(zoom=[1.0, 1.05])),                        # "فيه عروض جامدة": product close-up
    (15.00, VOICE_END + TAIL, "main", 15.00, dict(zoom=[1.0, 1.06], focusY=.42)),  # "بسبب Black Friday ... OSAMA10"
]


def aac_index(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index,codec_name", "-of", "csv=p=0",
                          str(path)], capture_output=True, text=True).stdout
    return next(int(l.split(",")[0]) for l in out.split() if l.endswith(",aac"))


def main():
    W = P / "work"; W.mkdir(exist_ok=True)
    d = json.loads((W / "tx/l_main/main.words.json").read_text())
    ww = [w for s in d["segments"] for w in s["words"]]
    # Whisper split "iFit" into "I -FIT" and "0 .5": rebuild the word list to his spoken words
    times = []
    i = 0
    raw = [w["w"] for w in ww]
    while i < len(ww):
        if raw[i] == "I" and i + 1 < len(ww) and raw[i + 1].startswith("-"):
            times.append((ww[i]["start"], ww[i + 1]["end"])); i += 2
        elif (raw[i] == "0" and i + 1 < len(ww) and raw[i + 1].startswith(".")) or (raw[i] == "بـ" and i + 1 < len(ww)):
            times.append((ww[i]["start"], ww[i + 1]["end"])); i += 2
        else:
            times.append((ww[i]["start"], ww[i]["end"])); i += 1
    spoken = SPOKEN.split()
    spoken = [w for w in spoken if w != "بـ"]           # "بـ 5000" is one spoken word in the transcript ("بـ" + number joined below)
    spoken[spoken.index("5000")] = "بـ5000"
    # "نص" stands where Whisper wrote "0 .5"
    assert len(spoken) == len(times), (len(spoken), len(times), spoken)
    words = [{"w": w, "start": round(a, 3), "end": round(b, 3)} for w, (a, b) in zip(spoken, times)]
    T = fr(VOICE_END + TAIL)
    clips, cues = [], []
    for k, (a, b, src, sin, o) in enumerate(PLAN):
        a, b = fr(a), fr(b)
        c = {"src": src, "in": round(sin, 4), "out": round(sin + (b - a), 4), **o}
        if k:
            c["tin"] = {"type": "whip", "dir": "left" if k % 2 else "right", "frames": 4} if src != "main" else {"type": "zoom", "frames": 4}
            cues.append(cue(a, "whoosh_in", -16))
        clips.append(c)
    at = lambda w: next(x["start"] for x in words if x["w"].startswith(w))
    ov = []
    ov.append({"type": "callout", "at": at("بـ5000"), "dur": 1.4, "number": "5,000", "unit": "EGP", "position": "center"})
    cues.append(cue(at("بـ5000"), "impact", -13))
    ov.append({"type": "callout", "at": at("سحب"), "dur": 2.0, "text": "GOLD DRAW", "earned": True, "position": "center"})
    cues += [cue(at("سحب"), "chime", -15), cue(at("سحب"), "impact", -14)]
    for n, w in (("01", "أولاً،"), ("02", "ثانياً"), ("03", "ثالثاً")):
        t = at(w)
        lab = {"01": "THE OFFER", "02": "BLACK FRIDAY DEALS", "03": "DISCOUNT CODE"}[n]
        ov.append({"type": "stepBadge", "at": t, "dur": 1.3 if n != "03" else 1.1, "mark": n, "label": lab, "top": 0.78, "plate": True})
        cues.append(cue(t, "click", -15))
    tc = at("OSAMA10")
    ov.append({"type": "kineticTitle", "at": tc, "dur": round(T - tc, 3), "eyebrow": "iFit DISCOUNT CODE",
               "lines": [{"text": "OSAMA10", "accent": True, "size": 200}], "top": 0.36, "backdrop": True, "motion": "smooth", "depth": True})
    cues += [cue(tc - 0.3, "swell", -16, dur=0.4), cue(tc, "slam", -12)]
    # voice: the main take's own sound, 0 -> end of his last word, then silence under the card
    src = P / MEDIA["main"]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-filter_complex",
                    f"[0:{aac_index(src)}]atrim=end={VOICE_END},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                    f"afade=t=out:st={VOICE_END - 0.06}:d=0.06,apad[o]", "-map", "[o]", "-t", f"{T:.3f}", "-c:a", "pcm_s24le",
                    str(W / "vo.wav")], check=True)
    (W / "vo.words.json").write_text(json.dumps({"segments": [{"words": words}]}, ensure_ascii=False))
    edit = {"title": "iFit main", "fps": FPS, "width": 1080, "height": 1920, "media": MEDIA,
            "plates": {"grade": "auto", "sharpen": "cas=strength=0.25"}, "clips": clips, "overlays": ov,
            "captions": {"wordsFile": "work/vo.words.json", "outputTime": True, "style": "plate", "plateColor": "#56A0FB",
                         "keywordColor": "#FFFFFF", "karaoke": True, "maxWords": 3, "maxChars": 22,
                         "keywords": ["سحب", "دهب", "OSAMA10."],
                         "zones": [{"at": 0, "dur": round(T + 0.01, 3), "top": 0.62}]},
            "sfx": {"cues": sorted(cues, key=lambda c: c["at"])}, "tail": 0, "voiceTrack": "work/vo.wav",
            "dialogueFx": "highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120:makeup=1.5", "dialogueLufs": -16.0}
    write_edit(P, edit)
    print(f"T={T:.2f}s, {len(clips)} clips, {len(words)} words")


if __name__ == "__main__":
    main()
