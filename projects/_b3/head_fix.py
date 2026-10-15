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

H = 1920
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
        else:
            fixes.append(dict(key, action="remove", why=f"no room between his chin and the captions ({gap:.0f}px < {hb}px)"))
    return fixes


def apply(overlays, fixes):
    """Apply fixes to an overlay list (indices refer to the ORIGINAL list from build.py)."""
    drop = set()
    for f in fixes:
        o = overlays[f["index"]]
        assert o["type"] == f["type"] and abs(o["at"] - f["at"]) < 1e-6, f
        if f["action"] == "remove":
            drop.add(f["index"])
        else:
            o["top"] = f["top"]
            if "size" in f:
                o["size"] = f["size"]
            if f.get("plate"):
                o["plate"] = True
    return [o for i, o in enumerate(overlays) if i not in drop]


def main():
    P = Path(sys.argv[1]).resolve()
    report = json.loads((P / "renders/_head_check.json").read_text())
    log_p = P / "headfix.json"
    log = json.loads(log_p.read_text()) if log_p.exists() else {"original_overlays": None, "fixes": []}
    edit_p, props_p = P / "edit.json", P / "renders/_props.json"
    edit, props = json.loads(edit_p.read_text()), json.loads(props_p.read_text())
    if log["original_overlays"] is None:
        log["original_overlays"] = len(edit["overlays"])
    # the check reports indices into the CURRENT overlay list: map them back to the original list
    removed = sorted(f["index"] for f in log["fixes"] if f["action"] == "remove")
    cur2orig = [i for i in range(log["original_overlays"]) if i not in removed]
    new = plan(edit, report["overlays"])
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
    if report.get("caption_hits"):
        print(f"  NOTE captions on the head at {report['caption_hits'][:5]}...: fix by hand")
    print(f"{P.name}: {len(new)} fix(es), {len(log['fixes'])} total")


if __name__ == "__main__":
    main()
