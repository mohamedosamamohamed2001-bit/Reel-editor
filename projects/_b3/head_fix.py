"""Coach Osama 2026-10-15: no text on or above his head, in all 12 batch-3 videos.

    python3 projects/_b3/head_fix.py projects/<p>      (after tools/head_check.py --keep)

Reads renders/_head_check.json and fixes every overlay it blames:
  - kineticTitle (the "head captions": big titles above / behind his head) -> removed;
  - any other text graphic -> moved straight down to just under his chin (the lowest chin while it is on screen),
    above the caption bar; icon tiles that don't fit the gap are scaled down to fit (never under 60 %);
    if it still doesn't fit -> removed.
Nothing else changes: timing, SFX, captions, cuts and the rest of the graphics stay as they are.
The same change is written into renders/_props.json (so the check can re-run without rebuilding plates) and logged in
headfix.json, which projects/_b3/common3.py applies whenever build.py is re-run.
"""
import json
import sys
from pathlib import Path

H, W = 1920, 1080
SIDE = 72  # theme safe.side
CAP_MAX = 0.74  # captions never lower than this (Reels UI at the bottom)
MARGIN = 18  # px between his beard and the graphic, and between the graphic and the caption bar


def cap_top(edit, at, dur):
    zones = (edit.get("captions") or {}).get("zones", [])
    tops = [z["top"] for z in zones if z["at"] < at + dur and z["at"] + z["dur"] > at] or [0.6]
    return min(tops) * H


def plan(edit, report):
    fixes = []
    for r in report:
        o = edit["overlays"][r["index"]]
        key = {"index": r["index"], "type": o["type"], "at": o["at"]}
        if o["type"] == "kineticTitle":
            fixes.append(dict(key, action="remove", why="title on / above his head"))
            continue
        if r["box"] is None:
            continue  # never alone on screen: measured on the next pass, once the title next to it is gone
        chin = r["chin_y"] * H + MARGIN
        bottom_limit = cap_top(edit, o["at"], o["dur"]) - MARGIN
        y0, y1 = r["box"][1], r["box"][3]
        off = y0 - (o.get("top") or 0) * H  # drawn box vs. declared top (icon rings, float)
        hb = y1 - y0
        gap = bottom_limit - chin
        if hb <= gap:
            fixes.append(dict(key, action="move", top=round((chin - off) / H, 3)))
            if o["type"] in ("stepBadge", "lowerLabel"):  # white type now sits on his shirt: caption-bar plate, no shadow
                fixes[-1]["plate"] = True
        elif o["type"] == "iconPop" and gap / hb >= 0.6:
            k = gap / hb
            fixes.append(dict(key, action="move", top=round((chin - off * k) / H, 3), size=int(o["size"] * k)))
        elif o["type"] == "iconPop" and side_fit(r):
            # no room under his chin (tight close-up): beside his head, never over it or above it
            k, align = side_fit(r)
            f = dict(key, action="move", top=o["top"], align=align)
            if k < 1:
                f["size"] = int(o["size"] * k)
            fixes.append(f)
        else:
            fixes.append(dict(key, action="remove", why=f"no room between his chin and the captions ({gap:.0f}px < {hb}px)"))
    return fixes


def side_fit(r):
    """(scale, "left"|"right") if the icon row fits beside his head (scaled down to >= 60 %), else None."""
    bw = r["box"][2] - r["box"][0]
    best = None
    for align, space in (("left", r["head_x"][0] - MARGIN - SIDE + 20), ("right", W - SIDE + 20 - r["head_x"][1] - MARGIN)):
        k = min(1.0, space / bw)
        if k >= 0.6 and (best is None or k > best[0]):
            best = (k, align)
    return best


def fix_captions(edit, hits):
    """Captions that would touch his beard (tight close-up) move down, only in the zones where that happens."""
    if not hits:
        return None
    need = (max(x["head"][3] for x in hits) + MARGIN) / H
    ts = [x["t"] for x in hits]
    out = []
    for i, z in enumerate(edit["captions"]["zones"]):
        if z["at"] <= max(ts) and z["at"] + z["dur"] >= min(ts) and z["top"] < need:
            out.append({"zone": i, "top": round(min(CAP_MAX, need), 3)})
    return out


def cards_on_face(edit, props, faces):
    """Picture cards (visualCard mode card) whose card covers his face -> full-screen cutaway (03's rule)."""
    out = []
    for i, (o, po) in enumerate(zip(edit["overlays"], props["edit"]["overlays"])):
        if o["type"] != "visualCard" or o.get("mode", "card") != "card":
            continue
        sw, sh = po.get("srcW", 1000), po.get("srcH", 1000)
        cw = o.get("width", 860)
        ch = min(H * 0.36, cw * sh / sw)
        bw = min(cw, ch * sw / sh)
        y0 = o["top"] * H if o.get("top") is not None else 0.14 * H + 10
        box = [(W - bw) / 2, y0, (W + bw) / 2, y0 + ch]
        for t, fx0, fy0, fx1, fy1 in faces:
            if o["at"] - 0.7 <= t < o["at"] + o["dur"] + 0.7 and box[0] < fx1 and box[2] > fx0 and box[1] < fy1 and box[3] > fy0 + 0.15 * (fy1 - fy0):
                out.append({"index": i, "type": "visualCard", "at": o["at"], "action": "full", "why": "picture card covered his face"})
                break
    return out


def apply_captions(captions, cap_fixes):
    for f in cap_fixes:
        captions["zones"][f["zone"]]["top"] = max(captions["zones"][f["zone"]]["top"], f["top"])


def apply(overlays, fixes):
    """Apply fixes to an overlay list (indices refer to the ORIGINAL list from build.py)."""
    drop = set()
    for f in fixes:
        o = overlays[f["index"]]
        assert o["type"] == f["type"] and abs(o["at"] - f["at"]) < 1e-6, f
        if f["action"] == "remove":
            drop.add(f["index"])
        else:
            if "top" in f:
                o["top"] = f["top"]
            if "size" in f:
                o["size"] = f["size"]
            if f.get("plate"):
                o["plate"] = True
            if "align" in f:
                o["align"] = f["align"]
            if f["action"] == "full":
                o["mode"] = "full"
                o.pop("width", None)
                o.pop("top", None)
    return [o for i, o in enumerate(overlays) if i not in drop]


def main():
    P = Path(sys.argv[1]).resolve()
    report = json.loads((P / "renders/_head_check.json").read_text())
    cap_hits = [x for x in report["frames"] if x["captions"]]
    log_p = P / "headfix.json"
    log = json.loads(log_p.read_text()) if log_p.exists() else {"original_overlays": None, "fixes": []}
    log.setdefault("captions", [])
    edit_p, props_p = P / "edit.json", P / "renders/_props.json"
    edit, props = json.loads(edit_p.read_text()), json.loads(props_p.read_text())
    if log["original_overlays"] is None:
        log["original_overlays"] = len(edit["overlays"])
    # the check reports indices into the CURRENT overlay list: map them back to the original list
    removed = sorted(f["index"] for f in log["fixes"] if f["action"] == "remove")
    cur2orig = [i for i in range(log["original_overlays"]) if i not in removed]
    cf = fix_captions(edit, cap_hits)
    if cf:
        for f in cf:
            print(f"  captions zone {f['zone']} -> top {f['top']} (his beard reaches the caption bar)")
        log["captions"] += cf
        apply_captions(edit["captions"], cf)
        apply_captions(props["edit"]["captions"], cf)
        new = []  # re-check the graphics against the new caption position on the next pass
    else:
        new = plan(edit, report["overlays"]) + cards_on_face(edit, props, report.get("faces", []))
    for f in new:
        f["index"] = cur2orig[f["index"]]
        print(f"  {f['action']:6s} #{f['index']} {f['type']} @{f['at']}" + (f" top={f['top']}" if "top" in f else "") +
              (f" size={f['size']}" if "size" in f else "") + (f"  ({f['why']})" if "why" in f else ""))
    # moves replace earlier moves of the same overlay
    keep = {f["index"]: f for f in log["fixes"]}
    for f in new:
        if f["index"] in keep and keep[f["index"]].get("plate"):
            f["plate"] = True
        keep[f["index"]] = f
    log["fixes"] = sorted(keep.values(), key=lambda f: f["index"])
    # re-apply everything to the original lists: edit.json keeps a pristine copy of the build's overlays
    orig_p = P / "work/overlays.original.json"
    if not orig_p.exists():
        orig_p.write_text(json.dumps({"edit": edit["overlays"], "props": props["edit"]["overlays"]}, ensure_ascii=False))
    orig = json.loads(orig_p.read_text())
    edit["overlays"] = apply(json.loads(json.dumps(orig["edit"])), log["fixes"])
    props["edit"]["overlays"] = apply(json.loads(json.dumps(orig["props"])), log["fixes"])
    edit_p.write_text(json.dumps(edit, ensure_ascii=False, indent=1))
    props_p.write_text(json.dumps(props, ensure_ascii=False))
    log_p.write_text(json.dumps(log, ensure_ascii=False, indent=1))
    print(f"{P.name}: {len(new)} fix(es), {len(log['fixes'])} total")


if __name__ == "__main__":
    main()
