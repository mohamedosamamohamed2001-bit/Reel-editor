#!/usr/bin/env python3
"""Put human-checked caption text onto Whisper's word timings.

    python3 tools/align_words.py WORDS_JSON REFERENCE.txt OUT_JSON

Whisper (large-v3) gives good word TIMES but mishears Egyptian Arabic (it drifts to Standard Arabic, splits or merges
words, and can hallucinate an outro like "اشتركوا في القناة"). The reference text (e.g. the client's own approved
captions, or a by-ear correction) gives the right WORDS. This aligns the two with a Needleman-Wunsch word alignment on
normalised Arabic (alef/ya/ta-marbuta forms unified, diacritics and punctuation removed):
  - a reference word matched to a Whisper word takes its start/end (merged/split words widen to cover them);
  - an unmatched reference word is placed between its matched neighbours, in proportion to its length;
  - unmatched Whisper words are dropped (hallucinations, misheard fillers).
Output has the same shape as tools/transcribe.py (`segments[].words[]`), plus "matched": false on placed words and a
report of every substitution so the result can be reviewed.
"""
import json
import re
import sys
from difflib import SequenceMatcher


def norm(w):
    w = re.sub(r"[ً-ْـ]", "", w)  # diacritics, tatweel
    w = re.sub(r"[.,!?،؟:;\"'()]", "", w).lower()
    w = re.sub("[أإآ]", "ا", w).replace("ة", "ه").replace("ى", "ي")
    return w


# how English terms sound in Egyptian Arabic, so "Cardio" can match Whisper's "كارديو"
ALIASES = {
    "cardio": ["كارديو"], "calories": ["كالوريز", "كالوريس"], "crossfit": ["كروسفيت", "كروس فيت"], "jump": ["جامب"],
    "supplement": ["سبلمنت", "سبلمين", "سبليمنت", "سبلم"], "stretch": ["استرتش", "استريتش"], "range": ["رينج"],
    "motion": ["موشن"], "chest": ["تشيست", "شيست"], "triceps": ["ترايسبس", "ترايسيبس", "try"], "whey": ["واي", "وي"],
    "protein": ["بروتين"], "concentric": ["كونسنتريك"], "eccentric": ["اكسنتريك"],
}


def _core(w):
    w = norm(w)
    for pre in ("وال", "بال", "فال", "ال"):  # the article and its common prefixes don't decide a match
        if w.startswith(pre) and len(w) > len(pre) + 2:
            return w[len(pre):]
    return w


def sim(a, b):
    a0, b0 = norm(a), norm(b)
    if not a0 or not b0:
        return 0.0
    if a0 == b0:
        return 1.0
    def r(x, y):  # ratio, discounted when one word is much shorter (a 2-letter word half-matching a long one)
        return SequenceMatcher(None, x, y).ratio() * (min(len(x), len(y)) / max(len(x), len(y))) ** 0.5
    best = max(r(a0, b0), r(_core(a), _core(b)))
    for alias in ALIASES.get(a0, []):
        best = max(best, r(norm(alias), _core(b)), r(norm(alias), b0))
    return best


def align(ref, hyp):
    n, m = len(ref), len(hyp)
    GAP = -0.45
    S = [[0.0] * (m + 1) for _ in range(n + 1)]
    B = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        S[i][0], B[i][0] = S[i - 1][0] + GAP, "u"
    for j in range(1, m + 1):
        S[0][j], B[0][j] = S[0][j - 1] + GAP, "l"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d = S[i - 1][j - 1] + (sim(ref[i - 1], hyp[j - 1]["w"]) * 2 - 0.9)
            u = S[i - 1][j] + GAP
            left = S[i][j - 1] + GAP
            S[i][j], B[i][j] = max((d, "d"), (u, "u"), (left, "l"))
    pairs, i, j = [], n, m
    while i > 0 or j > 0:
        b = B[i][j]
        if b == "d":
            pairs.append((i - 1, j - 1)); i -= 1; j -= 1
        elif b == "u":
            pairs.append((i - 1, None)); i -= 1
        else:
            pairs.append((None, j - 1)); j -= 1
    return pairs[::-1]


def main():
    words_json, ref_txt, out_json = sys.argv[1:4]
    data = json.load(open(words_json))
    hyp = [w for s in data["segments"] for w in s["words"]]
    ref = open(ref_txt).read().split()
    pairs = align(ref, hyp)
    out = [None] * len(ref)
    report = []
    last_ref = None
    pending_start = None
    for r, h in pairs:
        if r is not None and h is not None:
            out[r] = {"w": ref[r], "start": pending_start if pending_start is not None else hyp[h]["start"], "end": hyp[h]["end"], "matched": True}
            pending_start = None
            if norm(ref[r]) != norm(hyp[h]["w"]):
                report.append(f"{hyp[h]['start']:6.2f}  {hyp[h]['w']}  ->  {ref[r]}")
            last_ref = r
        elif h is not None:
            # unmatched Whisper word: if it sits right after a matched reference word, that word was split in two
            # by Whisper (e.g. "هيضمر لك" for "هيدمرلك"): widen the reference word to cover it; else drop it
            if norm(hyp[h]["w"]) in ("و", "ف", "ب", "ال"):  # a detached conjunction belongs to the NEXT word ("و ده" = "وده")
                pending_start = hyp[h]["start"] if pending_start is None else pending_start
                report.append(f"{hyp[h]['start']:6.2f}  {hyp[h]['w']}  ->  (start of next word)")
                continue
            # only short fragments extend a word (لك / لها / من): a long unmatched word is a hallucination, dropped
            if last_ref is not None and out[last_ref] and 0 <= hyp[h]["start"] - out[last_ref]["end"] < 0.12 \
                    and hyp[h]["end"] - out[last_ref]["start"] < 1.2 and len(norm(hyp[h]["w"])) <= 3:
                out[last_ref]["end"] = hyp[h]["end"]
                report.append(f"{hyp[h]['start']:6.2f}  {hyp[h]['w']}  ->  (part of {ref[last_ref]})")
                continue
            report.append(f"{hyp[h]['start']:6.2f}  {hyp[h]['w']}  ->  (dropped)")
        else:
            report.append(f"   ---  (missing)  ->  {ref[r]}")
    # place unmatched reference words between matched neighbours, proportional to their length
    i = 0
    while i < len(out):
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < len(out) and out[j] is None:
            j += 1
        a = out[i - 1]["end"] if i > 0 else (out[j]["start"] - 0.3 * (j - i) if j < len(out) else 0.0)
        b = out[j]["start"] if j < len(out) else a + 0.3 * (j - i)
        if b - a < 0.08 * (j - i):  # no room: borrow from the neighbours' edges
            mid = (a + b) / 2
            a, b = mid - 0.06 * (j - i), mid + 0.06 * (j - i)
        lens = [max(1, len(norm(ref[k]))) for k in range(i, j)]
        tot = sum(lens)
        t = a
        for k, L in zip(range(i, j), lens):
            d = (b - a) * L / tot
            out[k] = {"w": ref[k], "start": round(t, 3), "end": round(t + d, 3), "matched": False}
            t += d
        i = j
    # keep times monotonic
    for k in range(1, len(out)):
        if out[k]["start"] < out[k - 1]["start"]:
            out[k]["start"] = out[k - 1]["start"]
        if out[k]["end"] < out[k]["start"]:
            out[k]["end"] = out[k]["start"] + 0.05
    json.dump({"source": words_json, "reference": ref_txt, "segments": [{"start": out[0]["start"], "end": out[-1]["end"], "words": out}],
               "report": report}, open(out_json, "w"), ensure_ascii=False, indent=1)
    matched = sum(1 for w in out if w["matched"])
    print(f"{matched}/{len(out)} reference words matched to Whisper timings; {len(report)} differences:")
    print("\n".join(report))


if __name__ == "__main__":
    main()
