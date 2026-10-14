#!/usr/bin/env python3
"""Find and download openly licensed images (Openverse: Wikimedia Commons, Flickr, …) with their attribution.

    python3 tools/fetch_asset.py search "raw steak" [--license cc0,pdm,by,by-sa] [-n 10]
    python3 tools/fetch_asset.py get OPENVERSE_ID OUT_FILE [--manifest MANIFEST.json]

`get` downloads through Openverse's own image proxy (full size), because Wikimedia/Flickr rate-limit this container's
IP; animated GIFs come back as a still. Every download is appended to the manifest with title, creator, licence,
licence URL, source page and Openverse's ready-made attribution text: the video's credits and the post caption are
built from it. Only commercial-use-friendly licences are allowed by default (no NC/ND).
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

API = "https://api.openverse.org/v1/images/"
OK = "cc0,pdm,by,by-sa"


def get_json(url):
    for i in range(4):
        out = subprocess.run(["curl", "-s", "-A", "OSM-Video-Studio/1.0", url], capture_output=True, text=True).stdout
        try:
            d = json.loads(out)
            if "results" in d or "id" in d:
                return d
        except json.JSONDecodeError:
            pass
        time.sleep(3 * (i + 1))
    raise SystemExit(f"openverse not answering: {out[:200]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("q")
    s.add_argument("--license", default=OK)
    s.add_argument("-n", type=int, default=10)
    g = sub.add_parser("get")
    g.add_argument("id")
    g.add_argument("out")
    g.add_argument("--manifest", default=None)
    a = ap.parse_args()
    if a.cmd == "search":
        d = get_json(f"{API}?q={urllib.parse.quote(a.q)}&license={a.license}&page_size={a.n}")
        for r in d["results"]:
            print(f"{r['id']}  {r['license']}-{r['license_version']}  {r['source']:9s} {r['width']}x{r['height']}  {r['title'][:60]}")
        return
    meta = get_json(f"{API}{a.id}/")
    if meta["license"] not in OK.split(","):
        raise SystemExit(f"licence {meta['license']} not allowed")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    code = subprocess.run(["curl", "-s", "-o", str(out), "-w", "%{http_code}", f"{API}{a.id}/thumb/?full_size=true"],
                          capture_output=True, text=True).stdout
    if code != "200":
        raise SystemExit(f"download failed: HTTP {code}")
    rec = {"file": out.name, "openverse_id": a.id, "title": meta["title"], "creator": meta.get("creator"),
           "license": f"{meta['license'].upper()} {meta['license_version']}", "license_url": meta.get("license_url"),
           "source": meta["source"], "landing": meta.get("foreign_landing_url"), "attribution": meta.get("attribution")}
    if a.manifest:
        m = Path(a.manifest)
        data = json.loads(m.read_text()) if m.exists() else []
        data = [x for x in data if x["file"] != out.name] + [rec]
        m.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
