"""Whisper large-v3 put "كل" (of "كل تمرينة") at 16.4 s, before 5 s of silence; it is spoken at 21.25 s (medium)."""
import json
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "work/tx/aligned.words.json"
d = json.loads(p.read_text())
for s in d["segments"]:
    for w in s["words"]:
        if w["w"] == "كل" and abs(w["start"] - 16.4) < 0.3:
            w["start"], w["end"] = 21.25, 21.5
p.write_text(json.dumps(d, ensure_ascii=False, indent=1))
