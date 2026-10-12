#!/usr/bin/env python3
"""Suggest number callouts from a transcript (reference E: each number appears on screen as it is spoken).

Usage:
    python3 tools/suggest_callouts.py WORDS_JSON [--clips EDIT_JSON]

Prints candidate {"type":"callout",...} entries. With --clips, times are mapped through the edit's cuts to
OUTPUT time; without it they are SOURCE times. These are suggestions only: check each number against the
audio before using it (transcripts can mishear numbers) and keep the ones that carry the message.
"""
import argparse
import json
import re
from pathlib import Path

DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")  # book: Western digits on screen
NUM = re.compile(r"^\d+([.,]\d+)?$")


def to_output(clips, t):
    off = 0.0
    for c in clips:
        if c["in"] <= t < c["out"]:
            return off + t - c["in"]
        off += c["out"] - c["in"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words_json")
    ap.add_argument("--clips", default=None, help="edit.json whose clips define the cuts")
    a = ap.parse_args()

    data = json.loads(Path(a.words_json).read_text())
    words = [w for s in data["segments"] for w in s["words"]]
    clips = json.loads(Path(a.clips).read_text())["clips"] if a.clips else None

    out = []
    for i, w in enumerate(words):
        token = w["w"].translate(DIGITS).strip(".,،؟?!")
        if not NUM.match(token):
            continue
        unit = words[i + 1]["w"].strip(".,،؟?!") if i + 1 < len(words) else ""
        at = to_output(clips, w["start"]) if clips else w["start"]
        if at is None:
            continue  # this moment was cut out
        out.append({"type": "callout", "at": round(max(0.0, at - 0.1), 2), "dur": 2.0, "number": token,
                    "unit": unit, "position": "top", "_heard": f"{w['w']} {unit}", "_check": w.get("check", False)})
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"# {len(out)} candidate(s); times are {'OUTPUT' if clips else 'SOURCE'} seconds. Remove _heard/_check after review.")


if __name__ == "__main__":
    main()
