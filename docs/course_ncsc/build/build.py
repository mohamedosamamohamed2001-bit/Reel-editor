"""Build the three OSM PDFs + the editable DOCX.  python3 docs/course_ncsc/build/build.py OUTDIR"""
import subprocess, sys, shutil
from pathlib import Path
import phase1, phase2, manual

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]).resolve()
TMP = OUT / "_html"
TMP.mkdir(parents=True, exist_ok=True)


def render(html, name, mode):
    f = TMP / f"{name}.html"
    f.write_text(html, encoding="utf-8")
    pdf = TMP / f"{name}.pdf"
    subprocess.run(["node", str(HERE / "render.js"), str(f), str(pdf), mode], check=True)
    return pdf


for mod, name, label in [(phase1, "OSM – Phase 1 Summary", "Phase 1 Summary"), (phase2, "OSM – Phase 2 Summary", "Phase 2 Summary"),
                         (manual, "OSM – Complete Client Assessment Manual", "Complete Client Assessment Manual")]:
    c = render(mod.build_cover(), name + "_cover", "cover")
    body = render(mod.build(), name + "_body", label)
    subprocess.run(["pdfunite", str(c), str(body), str(OUT / f"{name}.pdf")], check=True)
    print("wrote", OUT / f"{name}.pdf")

# editable master: same content, Word-friendly (no absolute-positioned cover)
ed = TMP / "OSM – Complete Client Assessment Manual (Editable).html"
h = manual.build(editable=True).replace("<table", '<table border="1" cellspacing="0" cellpadding="4" width="100%"').replace('style="width:70mm"', 'width="260" style="width:70mm"')
ed.write_text(h, encoding="utf-8")
subprocess.run(["soffice", "--headless", "--convert-to", "docx:MS Word 2007 XML", "--outdir", str(TMP), str(ed)], check=True, capture_output=True)
shutil.copy(TMP / (ed.stem + ".docx"), OUT / (ed.stem + ".docx"))
print("wrote", OUT / (ed.stem + ".docx"))
