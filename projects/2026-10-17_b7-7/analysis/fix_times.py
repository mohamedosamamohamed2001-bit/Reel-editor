"""Word times re-anchored on his original burned-in captions (plate onsets, read at 10 fps) where Whisper drifted."""
import json, sys
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "work/tx/aligned.words.json"
d = json.loads(p.read_text())
ws = [w for s in d["segments"] for w in s["words"]]
FIX = [("نوعية", 76.6, 76.8), ("الهدوم", 78.4, 77.2), ("تيشيرت", 78.6, 77.8), ("مثلًا", 78.6, 78.3), ("ده", 78.8, 79.0)]
for text, near, new in FIX:
    w = min((w for w in ws if w["w"] == text), key=lambda w: abs(w["start"] - near))
    w["start"] = new
for a, b in zip(ws, ws[1:]):
    if a["end"] > b["start"] or b["start"] - a["start"] < 1.0 and a["end"] < a["start"]:
        a["end"] = b["start"]
    a["end"] = max(a["end"], a["start"] + 0.08) if a["end"] <= a["start"] else a["end"]
p.write_text(json.dumps(d, ensure_ascii=False, indent=1))
print("fixed", len(FIX))
