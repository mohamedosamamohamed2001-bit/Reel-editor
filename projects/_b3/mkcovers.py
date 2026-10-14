"""Old-caption regions for erasing (tools/erase_text.py --covers): the video's caption band (erase_params "band")
while he speaks (aligned words, ±0.5 s, gaps < 0.8 s merged) + detections + manual extras (erase_extra.json)."""
import json, sys
from pathlib import Path
P = Path(sys.argv[1])
prm = json.loads((P / "erase_params.json").read_text()) if (P / "erase_params.json").exists() else {}
band = prm.get("band", [0.35, 0.92])
wf = P / "work/tx/aligned.words.json"
words = [w for s in json.load(open(wf))["segments"] for w in s["words"]] if wf.exists() else []
spans = []
for w in words:
    a, b = max(0.0, w["start"] - 0.5), w["end"] + 0.5
    if spans and a - spans[-1][1] < 0.8:
        spans[-1][1] = max(spans[-1][1], b)
    else:
        spans.append([a, b])
cv = [{"src": "main", "at": round(a, 3), "dur": round(b - a, 3), "box": [0.0, band[0], 1.0, band[1]]} for a, b in spans]
extra = P / "erase_extra.json"
if extra.exists():
    cv += json.loads(extra.read_text())
(P / "work/clean").mkdir(parents=True, exist_ok=True)
(P / "work/clean/covers.json").write_text(json.dumps(cv))
print(P.name, len(cv), "regions", [(round(c["at"],1), round(c["at"]+c["dur"],1)) for c in cv][:6])
