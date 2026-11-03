"""Voice track for the transformation reel, from the ONE source that carries both voices: source/main_video.mov.

Coach Osama (his own recorded VO, 1x) + the client's real WhatsApp voice notes. In the screen recording the voice notes play
at WhatsApp 1.5x (the player shows "1.5x"; at 1x her rate is ~5 syllables/s = natural speech), so her takes are restored to
1x with atempo (pitch unchanged). Only lines that are clear in all transcription passes are used; unclear phrases are cut,
never guessed. Nothing is invented, re-ordered within a sentence, or synthesised.

    python3 projects/2026-11-03_transformation/vo.py     -> work/vo.wav, work/vo.words.json, work/vo_plan.json
"""
import json, subprocess
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent
SRC = P / "source/main_video.mov"
SR = 48000
CLIENT_T0, CLIENT_SPEED = 6.8, 1.5          # client file client_slow.wav = original from 6.8 s, slowed by 1/1.5

# text = exact words (Egyptian Arabic as spoken, English terms in English); times = word starts from Whisper medium
# (coach: source seconds; client: slowed-timeline seconds). seg = [start, end] in the same timeline.
COACH_OPEN = dict(who="coach", seg=[0.00, 7.22], words=[
    ("بدأت", 0.0), ("مع", 0.56), ("Client", 0.74), ("عنده", 1.16), ("Scoliosis", 1.54), ("وده", 2.08), ("كان", 2.5), ("محتاج", 2.62),
    ("مننا", 3.14), ("نفهم", 3.64), ("الحالة", 4.12), ("كويس", 4.58), ("ونشتغل", 5.02), ("بخطة", 5.58), ("تدريب", 5.88), ("مناسبة", 6.44), ("ليه", 6.96)])
COACH_CLOSE = dict(who="coach", seg=[55.42, 63.60], words=[(w, 55.0 + t) for w, t in [
    ("كل", 0.48), ("Client", 0.72), ("بيكون", 1.26), ("ليه", 1.54), ("احتياجات", 1.68), ("مختلفة", 2.16), ("ومش", 2.78), ("كل", 3.14),
    ("الناس", 3.32), ("ينفع", 3.68), ("معاها", 4.02), ("نفس", 4.34), ("البرنامج", 4.6), ("ابعتلي", 5.32), ("كلمة", 5.72), ("تدريب", 6.12),
    ("ويلا", 6.6), ("نبدأ", 6.88), ("مع", 7.22), ("بعض", 7.4), ("بطريقة", 7.7), ("علمية", 8.1)]])
C = lambda key, seg, words: dict(who="client", key=key, seg=seg, words=words)
CLIENT = {
    "A": C("A", [0.60, 3.25], [("أنا", 0.6), ("رحت", 1.12), ("للدكتور", 1.9), ("يوم", 2.36), ("الخميس", 2.54)]),
    "B1": C("B1", [3.95, 6.62], [("عايزة", 4.1), ("أقولك", 4.46), ("يا", 4.86), ("أسامة", 5.02), ("ما", 5.8), ("شاء", 6.06), ("الله", 6.28)]),
    "B2": C("B2", [6.62, 10.75], [("هو", 6.68), ("أصلًا", 6.9), ("اتصدم", 7.72), ("من", 9.12), ("النتيجة", 9.94)]),
    "C": C("C", [11.85, 18.05], [("قال", 11.96), ("لي", 12.34), ("ما", 12.48), ("شاء", 12.6), ("الله", 12.8), ("يعني", 13.0), ("إن", 13.46),
                                  ("الـspine", 14.06), ("كله", 14.64), ("بقى", 15.0), ("حواليه", 15.26), ("muscles", 15.62), ("والدنيا", 16.12), ("مظبوطة", 17.34)]),
    "D": C("D", [19.38, 21.45], [("والكيرف", 19.48), ("نفسه", 20.28), ("أصلًا", 20.6), ("تحسن", 20.94)]),
    "F": C("F", [31.68, 34.68], [("بجد", 31.74), ("تحفة", 32.16), ("يا", 32.6), ("كوتش", 32.74), ("ما", 33.36), ("شاء", 33.5), ("الله", 33.62),
                                  ("ما", 33.78), ("شاء", 33.92), ("الله", 34.1), ("ما", 34.28), ("شاء", 34.4), ("الله", 34.5)]),
    "H": C("H", [40.40, 46.40], [("الوضع", 40.5), ("اللي", 41.22), ("احنا", 41.34), ("وصلنا", 41.5), ("له", 41.84), ("ده", 42.06), ("أنا", 42.6),
                                  ("معرفش", 42.96), ("إزاي", 43.28), ("من", 44.2), ("عند", 44.54), ("ربنا", 44.75), ("الحمد", 45.02), ("لله", 45.4),
                                  ("الحمد", 45.72), ("لله", 46.04)]),
    "J": C("J", [53.98, 56.45], [("لأني", 54.04), ("عمري", 54.5), ("في", 54.86), ("حياتي", 55.0), ("ما", 55.36),
                                  ("وصلت", 55.4), ("للنتيجة", 55.72), ("دي", 56.18)]),
    "K": C("K", [57.78, 61.30], [("دي", 57.84), ("أنا", 58.08), ("قعدت", 58.4), ("سنين", 58.74), ("عشان", 59.58), ("أوصل", 59.98), ("لها", 60.24),
                                  ("ووصلتلهاش", 60.44)]),
}
# words a human must confirm by ear (Whisper medium disagreed or the dialect form was chosen)
UNSURE = {"عايزة": "Whisper: عايز (female speaker -> عايزة)", "اتصدم": "Whisper: صدم", "ما وصلت": "'ما' is very short / partly elided",
          "قعدت": "Whisper: وعدت (Cairene ق = hamza)", "يا كوتش": "Whisper: كوتشو", "بخطة": "Whisper: بخط"}

# the story order on the output timeline (gap = silence before the take, seconds)
ORDER = [("A", 0.0), ("B2", 0.30), ("OPEN", 1.05), ("B1", 3.0), ("C", 0.35), ("D", 0.40), ("F", 0.55), ("H", 0.45), ("J", 0.55), ("K", 0.35), ("CLOSE", 0.70)]
COACH_FX = ("highpass=f=75,afftdn=nf=-46:nr=10:tn=1,equalizer=f=220:t=q:w=1.1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,"
            "equalizer=f=9000:t=h:w=0.7:g=1.5,acompressor=threshold=-21dB:ratio=2.6:attack=6:release=90:makeup=1.5")
CLIENT_FX = ("highpass=f=95,lowpass=f=10500,afftdn=nf=-38:nr=14:tn=1,equalizer=f=260:t=q:w=1.0:g=-2.5,equalizer=f=3000:t=q:w=1.1:g=3,"
             "acompressor=threshold=-22dB:ratio=3:attack=5:release=80:makeup=2")
TARGET_LUFS = -16.0


def ff(args, **kw):
    return subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True, **kw)


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(r.rsplit("I:", 1)[1].split("LUFS")[0])


def main():
    w = P / "work"
    w.mkdir(exist_ok=True)
    raw = w / "main_48k.wav"
    ff(["-i", str(SRC), "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", str(raw)])
    takes = {"OPEN": COACH_OPEN, "CLOSE": COACH_CLOSE, **CLIENT}
    pieces, plan, t, words = [], [], 0.0, []
    for key, gap in ORDER:
        tk = takes[key]
        t += gap
        if tk["who"] == "coach":
            a, b = tk["seg"]
            src_a, src_b, spd, wmap = a, b, 1.0, (lambda x, a=a: x - a)
        else:
            a, b = tk["seg"]
            src_a, src_b, spd = CLIENT_T0 + a / CLIENT_SPEED, CLIENT_T0 + b / CLIENT_SPEED, CLIENT_SPEED
            wmap = (lambda x, a=a: x - a)
        out = w / f"take_{key}.wav"
        fx = COACH_FX if tk["who"] == "coach" else CLIENT_FX
        tempo = f"atempo={1 / spd:.7f}," if spd != 1 else ""
        # 12 ms fades at every cut; processing on the slowed audio so the denoiser sees the real voice
        ff(["-ss", f"{src_a:.4f}", "-to", f"{src_b:.4f}", "-i", str(raw), "-af", f"{tempo}{fx},afade=t=in:d=0.012,areverse,afade=t=in:d=0.04,areverse",
            "-ar", str(SR), "-c:a", "pcm_f32le", str(out)])
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout)
        pieces.append((out, t, tk["who"]))
        plan.append({"take": key, "who": tk["who"], "at": round(t, 4), "dur": round(dur, 4), "src": [round(src_a, 3), round(src_b, 3)], "speed_restored": spd})
        ws = tk["words"]
        for i, (word, st) in enumerate(ws):
            s = t + wmap(st)
            e = t + (wmap(ws[i + 1][1]) if i + 1 < len(ws) else dur - 0.04)
            words.append({"w": word, "start": round(max(t, s), 3), "end": round(min(t + dur, e), 3), "who": tk["who"]})
        t += dur
    total = t
    # level each voice to the same loudness (measured on that voice only), then lay the takes on the output timeline
    for who in ("coach", "client"):
        cat = w / f"_cat_{who}.wav"
        lst = w / f"_cat_{who}.txt"
        lst.write_text("".join(f"file '{p}'\n" for p, _, wh in pieces if wh == who))
        ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "pcm_f32le", str(cat)])
        g = TARGET_LUFS - lufs(cat)
        for i, (p, at, wh) in enumerate(pieces):
            if wh == who:
                tmp = p.with_suffix(".g.wav")
                ff(["-i", str(p), "-af", f"volume={g:.2f}dB", "-c:a", "pcm_f32le", str(tmp)])
                tmp.replace(p)
        cat.unlink(); lst.unlink()
        print(f"{who}: gain {g:+.2f} dB -> {TARGET_LUFS} LUFS")
    inputs, filt = [], []
    for i, (p, at, _) in enumerate(pieces):
        inputs += ["-i", str(p)]
        filt.append(f"[{i}:a]adelay={int(round(at * 1000))}:all=1[d{i}]")
    filt.append("".join(f"[d{i}]" for i in range(len(pieces))) + f"amix=inputs={len(pieces)}:normalize=0,apad=whole_dur={total + 0.5:.3f}[o]")
    ff([*inputs, "-filter_complex", ";".join(filt), "-map", "[o]", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", str(w / "vo.wav")])
    (w / "vo.words.json").write_text(json.dumps({"segments": [{"words": [{k: v for k, v in x.items() if k != "who"} for x in words]}]}, ensure_ascii=False))
    (w / "vo_plan.json").write_text(json.dumps({"total": round(total, 4), "takes": plan, "words": words, "unsure": UNSURE}, ensure_ascii=False, indent=1))
    print(f"vo: {total:.2f} s, {len(words)} words")
    for p in plan:
        print(f"  {p['take']:5} {p['who']:6} at {p['at']:6.2f}  dur {p['dur']:5.2f}  src {p['src']}")


if __name__ == "__main__":
    main()
