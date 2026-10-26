# Vendored: Claude Video Effects (by @vibha.in.progress)

**Source:** `claude-video-effects-main.zip` (sha256 d93503ee…2b5b), uploaded by Coach Osama on 2026-10-26.

**Licences:**
- Code: MIT (`LICENSE`).
- Fonts: SIL OFL, Apache-2.0 for Permanent Marker (`fonts/*.txt`).
- Models: YuNet (MIT), MediaPipe Selfie Segmenter (Apache-2.0).

**Kept:**
- `scripts/fx.py` (the effect engine)
- `fonts/`
- `models/`
- `LICENSE`
- `UPSTREAM_README.md`
- `UPSTREAM_SKILL.md.txt`, renamed so it does not load as a Claude skill: it tells the agent to install software and render right away.

**Not imported:**
- `scripts/setup.sh`: creates its own venv and pip-installs MediaPipe.
- `scripts/words.py`: pip-installs faster-whisper at runtime, and `tools/transcribe.py` already does this job.
- `requirements.txt`
- `assets/preview.jpg`: marketing image.

**Patch (the only change to `fx.py`):** the line that `exec()`s any `scripts/fx_private.py` found next to it is commented out. That was arbitrary code execution, and the file is not part of the pack.

**Use it through `tools/vfx.py` only.** That adapter swaps MediaPipe for the studio's MODNet matte, maps fonts to OSM, validates against the OSM rules and runs on plate frames. Don't run `fx.py` directly: it renders its own SDR H.264 file next to the input and bypasses the studio pipeline. `selfie_segmenter.tflite` is unused; it's kept with its licence for completeness.
