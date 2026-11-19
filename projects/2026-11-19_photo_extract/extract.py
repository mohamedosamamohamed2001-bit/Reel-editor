"""Extract every photo tile from his screen recording (sportograf.com results page, 2-column grid), one file per photo.

Exact pixels only: each photo is a straight crop of one recorded frame (no resize, no retouch, no enhancement). The site's
watermarks are part of the previews and stay. For every frame: find the tiles (non-white blocks separated by pure-white page gaps)
that are COMPLETELY visible and clear of every overlay (phone status bar, the "Help" bubble, the bottom button bar), group the
appearances of the same photo across frames by pixel comparison (strict, so burst shots stay separate), keep the sharpest
appearance (the page at rest = least compression smear), and write them in page order.

    .venv/bin/python -I projects/2026-11-19_photo_extract/extract.py
"""
import json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image

P = Path(__file__).resolve().parent
SRC = P / "source/screenrec.mp4"
W, H = 1320, 2868
COLS = {"L": (48, 624), "R": (696, 1272)}       # measured column x ranges (576 px)
TOP = 190                                        # below the status bar / browser chrome
BOTTOM = {"L": 2190, "R": 2330}                  # left: the Help bubble starts ~2199; right: the button bar fade starts ~2340


def frames():
    # BT.709 full range as tagged; accurate rounding + full-resolution chroma for the cleanest RGB the recording holds
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(SRC), "-sws_flags", "lanczos+accurate_rnd+full_chroma_int", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-fps_mode", "passthrough", "-"],
                         stdout=subprocess.PIPE)
    n = W * H * 3
    i = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield i, np.frombuffer(b, np.uint8).reshape(H, W, 3)
        i += 1
    p.wait()


def tiles(f):
    out = []
    for c, (x0, x1) in COLS.items():
        strip = f[:, x0:x1].min(axis=2)
        white_frac = (strip >= 245).mean(axis=1)
        row = white_frac < 0.97                      # a row inside a photo
        # gap columns just outside the tile must be page white (a photo tile, not a banner spanning the page)
        y, lim = TOP, BOTTOM[c]
        while y < lim:
            if row[y]:
                y0 = y
                while y < lim and row[y]:
                    y += 1
                y1 = y
                # complete tile only: white page gap above and below, inside the clean zone
                if y0 > TOP + 2 and y1 < lim - 2 and not row[y0 - 1] and not row[y1] and y1 - y0 > 150:
                    side = np.concatenate([f[y0:y1, x0 - 6:x0 - 1], f[y0:y1, x1 + 1:x1 + 6]], axis=1).min(axis=2)
                    if (side >= 245).mean() > 0.98:
                        out.append((c, y0, y1))
            y += 1
    return out


def portrait(h):
    return h > 600


def sig(crop):
    """size-independent signature: grey, fixed 48 x 72 (portrait) / 48 x 32 (landscape), so a tile measured 1-4 px taller while
    the page scrolls (blended edge rows) still matches its resting version"""
    h = crop.shape[0]
    true_h = 864 if portrait(h) else 384
    c = crop[(h - true_h) // 2:(h - true_h) // 2 + true_h] if h > true_h else crop
    return np.asarray(Image.fromarray(c).convert("L").resize((48, 72 if portrait(h) else 32), Image.BILINEAR), float)


T = 6.0
# page scroll per frame (px, measured by aligning each frame's row profile with the previous one): identity of a tile =
# its column + its position on the page. (Matching by look merged two near-identical burst shots.)
SCROLL = np.load(P / "work/scroll.npy")


def main():
    W_ = P / "work/best"; W_.mkdir(parents=True, exist_ok=True)
    dets = []                                        # (frame, group id, col, y0) for every complete detection
    groups = []                                      # {sig, shape, best_sharp, frame, col, y0, y1, first_frame, first_y}
    for i, f in frames():
        for c, y0, y1 in tiles(f):
            x0, x1 = COLS[c]
            crop = f[y0:y1, x0:x1]
            s = sig(crop)
            g = crop.astype(np.float32).mean(axis=2)
            sharp = float(np.var(g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]))
            exact = crop.shape[0] in (864, 384)          # page at rest on whole pixels: crisp edges, the true size
            page_y = int(y0) + int(SCROLL[i])
            match = None
            for gr in groups:
                if gr["col"] == c and abs(gr["page_y"] - page_y) <= 8:
                    match = gr; break
            if match is None:
                match = {"sig": s, "portrait": portrait(crop.shape[0]), "shape": crop.shape, "sharp": -1, "exact": False, "page_y": page_y,
                         "first_frame": i, "col": c, "n": 0, "id": len(groups)}
                groups.append(match)
            match["n"] += 1
            dets.append((i, match["id"], c, int(y0), int(crop.shape[0])))
            better = (exact and not match["exact"]) or (exact == match["exact"] and sharp > match["sharp"])
            if better:
                match["exact"] = exact; match["shape"] = crop.shape
                match.update(sharp=sharp, frame=i, y0=y0, y1=y1)
                Image.fromarray(crop).save(W_ / f"g{match['id']:02d}.png")
        if i % 100 == 0:
            print("frame", i, "photos so far", len(groups), flush=True)
    rep = [{k: v for k, v in g.items() if k != "sig"} for g in groups]
    for r in rep:
        r["shape"] = list(r["shape"])
    (P / "work/groups.json").write_text(json.dumps(rep, indent=1))
    (P / "work/detections.json").write_text(json.dumps(dets))
    print(len(groups), "distinct photos")
    d = np.full((len(groups), len(groups)), 999.0)
    for a in range(len(groups)):
        for b in range(len(groups)):
            if a != b and groups[a]["portrait"] == groups[b]["portrait"]:
                d[a, b] = np.abs(groups[a]["sig"] - groups[b]["sig"]).mean()
    print("nearest other photo per photo:", [round(float(x), 1) for x in d.min(axis=1)])


def finalize():
    """Trim the page's own white gap rows that the detector kept at an edge (values ~250), check the true tile size, write the
    photos in page order (top to bottom, left then right) as lossless PNG, and zip them."""
    import zipfile
    g = json.loads((P / "work/groups.json").read_text())
    out = P / "output"; out.mkdir(exist_ok=True)
    for f in out.glob("*"):
        f.unlink()
    order = sorted(g, key=lambda r: (round(r["page_y"] / 40), r["col"]))
    names = []
    for k, r in enumerate(order, 1):
        a = np.asarray(Image.open(P / "work/best" / f"g{r['id']:02d}.png").convert("RGB"))
        m = a.astype(int).mean(axis=2)
        while (m[0] >= 240).mean() > 0.9:
            a, m = a[1:], m[1:]
        while (m[-1] >= 240).mean() > 0.9:
            a, m = a[:-1], m[:-1]
        assert a.shape[:2] in ((864, 576), (384, 576)), (r["id"], a.shape)
        name = f"Photo {k:02d}.png"
        Image.fromarray(a).save(out / name, optimize=True)
        names.append((name, r["id"], a.shape[1], a.shape[0], r["frame"]))
    with zipfile.ZipFile(out / "Photos.zip", "w", zipfile.ZIP_STORED) as z:
        for n, *_ in names:
            z.write(out / n, n)
    (P / "work/final.json").write_text(json.dumps(names, indent=1))
    for n in names:
        print(n)


if __name__ == "__main__":
    main()
    finalize()
