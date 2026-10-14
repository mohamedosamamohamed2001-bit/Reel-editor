#!/usr/bin/env python3
"""Fetch many openly licensed images at once (Openverse via tools/fetch_asset.py) and make a labelled contact sheet.

    python3 tools/fetch_batch.py LIST.tsv OUT_DIR [--pick name=N ...]

LIST.tsv: one "name<TAB>query" per line. For each, CC0 / public domain results are tried first, then CC BY / BY-SA
(credited on screen). The first result at least 700 px on its short side is downloaded to OUT_DIR/name.jpg and
recorded in OUT_DIR/manifest.json (title, creator, licence, source). --pick name=N takes the N-th candidate instead
(after looking at the sheet). Existing files are kept. Writes OUT_DIR/_sheet.jpg to check relevance by eye.
"""
import argparse
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_asset import API, get_json  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def candidates(q):
    out = []
    for lic, src in (("cc0,pdm", "&source=rawpixel,stocksnap"), ("cc0,pdm", ""), ("by,by-sa", "")):
        d = get_json(f"{API}?q={urllib.parse.quote(q)}&license={lic}&page_size=12{src}")
        for r in d.get("results", []):
            if min(r.get("width") or 0, r.get("height") or 0) >= 700 and r.get("source") != "wikimedia":
                out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list")
    ap.add_argument("out")
    ap.add_argument("--pick", nargs="*", default=[])
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    picks = dict(p.split("=") for p in a.pick)
    done = []
    for line in Path(a.list).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, q = line.split("\t")
        dst = out / f"{name}.jpg"
        if dst.exists() and name not in picks:
            done.append(name)
            continue
        c = candidates(q)
        k = int(picks.get(name, 0))
        if len(c) <= k:
            print(f"{name}: no result for '{q}'")
            continue
        r = c[k]
        if dst.exists():
            dst.unlink()
        res = subprocess.run([sys.executable, str(ROOT / "tools/fetch_asset.py"), "get", r["id"], str(dst), "--manifest",
                              str(out / "manifest.json")], capture_output=True, text=True)
        print(f"{name}: {r['license']} {r['source']} {r['width']}x{r['height']} {r['title'][:50]} {res.stdout.strip()[:40]}")
        done.append(name)
    # labelled sheet
    names = [n for n in done if (out / f"{n}.jpg").exists()]
    if names:
        cols, tw, th = 6, 300, 220
        sheet = Image.new("RGB", (cols * tw, ((len(names) + cols - 1) // cols) * (th + 22)), "black")
        d = ImageDraw.Draw(sheet)
        for i, n in enumerate(names):
            try:
                im = Image.open(out / f"{n}.jpg").convert("RGB")
            except Exception:
                continue
            im.thumbnail((tw - 6, th))
            x, y = (i % cols) * tw, (i // cols) * (th + 22)
            sheet.paste(im, (x + 3, y + 20))
            d.text((x + 4, y + 3), n, fill="yellow")
        sheet.save(out / "_sheet.jpg", quality=80)


if __name__ == "__main__":
    main()
