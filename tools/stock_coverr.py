#!/usr/bin/env python3
"""Search Coverr (free stock video, https://coverr.co/license) and download REAL footage only.

    python3 tools/stock_coverr.py search "meal prep" [--n 20]          list hits (non-AI, non-premium)
    python3 tools/stock_coverr.py get OUT_DIR SLUG|baseFilename ...    download 1080p + record in OUT_DIR/manifest.json

The search page embeds its API answer (Angular "ng-state" JSON). Every hit carries isAiGenerated and isPremium:
only hits with isAiGenerated == false and isPremium == false are listed or downloaded (OSM rule: no AI visuals,
no paid services). The manifest keeps title, page URL, file URL, sha256 and the licence for each clip.
"""
import hashlib
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path

LICENSE = "Coverr License (free for commercial use, no attribution required) https://coverr.co/license"


def search(q, pages=1):
    hits = []
    for page in range(1, pages + 1):
        url = f"https://coverr.co/s?q={urllib.parse.quote(q)}" + (f"&page={page}" if page > 1 else "")
        html = subprocess.run(["curl", "-sL", url], capture_output=True, text=True).stdout
        tag = '<script id="ng-state" type="application/json">'
        a = html.find(tag)
        if a < 0:
            break
        a += len(tag)
        state = json.loads(html[a:html.find("</script>", a)])
        for v in state.values():
            if isinstance(v, dict) and v.get("u", "").endswith("public-api.coverr.co/videos"):
                hits += v["b"]["hits"]
    out = []
    for h in hits:
        if h.get("isAiGenerated") is not False or h.get("isPremium") is not False:
            continue
        out.append({"title": h["title"], "slug": h["slug"], "base": h["baseFilename"], "dur": float(h["duration"]),
                    "aspect": h["aspectRatio"], "vertical": h.get("isVertical"), "max": f"{h['maxWidth']}x{h['maxHeight']}",
                    "mp4": h["urls"]["mp4"], "thumb": h["thumbnail"], "desc": h.get("description", "")})
    return out


def main():
    cmd = sys.argv[1]
    if cmd == "search":
        n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 30
        for h in search(sys.argv[2])[:n]:
            print(f"{h['base']:60s} {h['dur']:5.1f}s {h['aspect']:5s} {h['max']:9s} {h['title']}")
        return
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    man_p = out / "manifest.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else []
    for base in sys.argv[3:]:
        q = base.replace("coverr-", "").rsplit("-", 1)[0].replace("-", " ")
        hit = next((h for h in search(q) if base in (h["base"], h["slug"])), None)
        if hit is None:
            print(f"{base}: not found as a free, non-AI hit (searched '{q}')", file=sys.stderr)
            continue
        dst = out / f"{hit['base']}.mp4"
        if not dst.exists():
            subprocess.run(["curl", "-sL", "--fail", hit["mp4"], "-o", str(dst)], check=True)
        sha = hashlib.sha256(dst.read_bytes()).hexdigest()
        man = [m for m in man if m["file"] != dst.name] + [{
            "file": dst.name, "title": hit["title"], "page": f"https://coverr.co/videos/{hit['slug']}", "url": hit["mp4"],
            "sha256": sha, "isAiGenerated": False, "isPremium": False, "license": LICENSE}]
        print(f"{dst.name}: {dst.stat().st_size / 1e6:.1f} MB")
    man_p.write_text(json.dumps(man, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
