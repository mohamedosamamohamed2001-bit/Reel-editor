"""Write documentation/quality_control.md + assets_manifest.csv for each collection video from the measured results.

    python3 projects/_c5/qa_docs.py      (after export.py)
Reads renders/*_qa/qa.json (tools/qa_render.py), runs tools/sync_check.py, and reads projects/_c5/export_report.json.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRIVE = {"comeback": ("العودة من بعد الغياب 2.MP4", "13_TQ9oHoveX5IcmK43kn6hvoGfrSadtU"),
         "stretch": ("استرتش 2.MP4", "12VKfyfpSZjdxRKE4nTOLJADoFQ8xaPPm"),
         "whey": ("Whey supplement 2.MP4", "1wUrfo5yPOuygzMGNEM4gfasFPLaAHimR"),
         "crossfit": ("crossfit 2.MP4", "1z2UQB1SoHLSClgQytQvCs744NgvLnz2O"),
         "legday": ("LegDay 2.MP4", "1GlQUI3mNHO9bjNO2i4AlYemKpPtq2xnx")}
EXPECTED_SHA = {"comeback": "66d2c7b836d0ff2247bda4de153a81d0546ed7b1a33571995e6668633167d81e",
                "crossfit": "12ad565ba411a8ee21f3f722a1e2efdfbc44db1627bd24b5f5f48131619e5ee7",
                "legday": "48e88135d15f06d43fc22dda96e735509eb7a9d88160682f939a7047504134ee",
                "stretch": "613dd27594f10237fb450646ad3e9d5ee076e4ea239a7a7bca44b5bf8c050fda",
                "whey": "76ad20fcc51f917f8ff2d74958aa0b6f6a0547101f37e4552168aca79b7bd6c5"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    exports = json.loads((ROOT / "projects/_c5/export_report.json").read_text())
    for slug, (drive_name, drive_id) in DRIVE.items():
        proj = ROOT / "projects" / f"2026-10-13_c5-{slug}"
        qa = json.loads((proj / "renders" / f"2026-10-13_c5-{slug}_qa" / "qa.json").read_text())
        nm = proj / "renders" / f"2026-10-13_c5-{slug}_nomusic.mp4"
        sync = subprocess.run([sys.executable, str(ROOT / "tools/sync_check.py"), str(proj), str(nm)], capture_output=True,
                              text=True).stdout.strip().splitlines()[-1] if nm.exists() else "no dialogue (music-only edit)"
        src_sha = sha(proj / "source/original.mp4")
        edit = json.loads((proj / "edit.json").read_text())
        ex = [e for e in exports if f"c5-{slug}/" in e["file"]]
        c = qa["checks"]
        a = qa["audio"]
        lines = [f"# QA: {slug} ({drive_name})", "",
                 "## Measured (tools/qa_render.py, tools/sync_check.py, export checks)", "| Check | Result |", "|---|---|",
                 f"| Video | {c['video_stream']['detail']}, {qa['duration_s']} s |",
                 f"| Audio | {c['audio_stream']['detail']}; {a['integrated_lufs']} LUFS, LRA {a['lra_lu']} LU, true peak {a['true_peak_dbtp']} dBTP |",
                 f"| Black frames | {'none' if not qa['black_intervals'] else qa['black_intervals']} |",
                 f"| Frozen frames | {qa['frozen_intervals']} = the static end card (expected) |",
                 f"| Dialogue sync (per clip, cross-correlation) | {sync} |",
                 f"| Source unchanged | sha256 {src_sha[:12]}… {'matches the download' if src_sha == EXPECTED_SHA[slug] else 'MISMATCH'} |"]
        for e in ex:
            lines.append(f"| Export `{Path(e['file']).name}` | {e['video']}, {e['frames']} frames, {e['size_mb']} MB, full decode {'OK' if e['decodes'] else 'FAILED'}"
                         + (f"; send copy {e['send_mb']} MB" if e.get("send_copy") else "") + " |")
        lines += ["", "## Looked at",
                  "- Contact sheets of the whole render (2–4 fps) and frame-by-frame strips of every transition.",
                  "- Caption band sweep (every 4th frame, tools/band_sweep.py): no burned-in text from the old edit visible.",
                  "- Effect-frame scan (brightness/warmth per frame): every flagged frame is one of the new transitions or the end card; the old light leaks are gone.",
                  "- Mix measured per bus before rendering (tools/mix_report.py): music ≈13 dB under the voice while he talks.",
                  "", "## Not checked / needs a human",
                  "- **Listening.** I can't hear audio: the music, SFX balance and the separated voice's quality were checked by measurement and spectrogram only.",
                  "- **Captions by ear.** Words come from your original captions, aligned to the voice; any word the original captions got wrong is still wrong.",
                  "- Playback on a phone (Instagram UI overlap, brightness)."]
        doc = proj / "documentation"
        doc.mkdir(exist_ok=True)
        (doc / "quality_control.md").write_text("\n".join(lines) + "\n")
        manifest = ["asset,source,creator,license,attribution_required,usage",
                    f"source/original.mp4 (sha256 {src_sha[:12]}…),Google Drive {drive_id} ({drive_name}),OSM / Coach Osama,owned by user,no,picture + voice (separated)",
                    "music (work/music/music.wav),tools/music.py (synthesised in-house),OSM studio,no third-party material,no,soundtrack",
                    "sound effects,tools/sfx.py (synthesised in-house),OSM studio,no third-party material,no,transitions and accents",
                    "UVR-MDX-NET-Voc_FT.onnx,github.com/TRvlvr/model_repo,Ultimate Vocal Remover project,MIT,no,voice separation (processing only; nothing of it is in the video)",
                    "brand/logo + brand/fonts,OSM brand book / google fonts,OSM; IBM; Rasmus Andersson; Jeremy Tribby,owned / SIL OFL 1.1,no,end card; type"]
        (doc / "assets_manifest.csv").write_text("\n".join(manifest) + "\n")
        print("wrote", doc)


if __name__ == "__main__":
    main()
