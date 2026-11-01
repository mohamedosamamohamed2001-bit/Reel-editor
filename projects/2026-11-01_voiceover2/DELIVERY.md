# No perfect sitting posture: voice-over reel (2026-11-01)

Final: `deliveries/posture_2026-11-01/OSM_no_perfect_posture_2026-11-01.mp4` (Git LFS), sha256 6a8ba04aae95ffd0af29c3815601420653b67bf8eb7cfd67a7acf5798ee733d8
1080x1920, 30 fps, H.264, 42.4 s (40.0 s voice-over + end card). His voice-over unchanged; -14.2 LUFS, -1.8 dBTP.
The script screenshot in the source is not used anywhere.

## Research (PubMed)
- Swain et al. 2019, J Biomech 102:109312, umbrella review of 41 systematic reviews: no consensus that posture/physical exposure causes LBP. doi:10.1016/j.jbiomech.2019.08.006
- Slater et al. 2019, JOSPT 49(8):562-564, "Sit up straight": time to re-evaluate. doi:10.2519/jospt.2019.0610
- Shiri et al. 2018, Am J Epidemiol 187(5):1093-1101: exercise alone -33 % LBP risk (8 RCTs, n=1,634); strengthening 2-3x/week. doi:10.1093/aje/kwx337
"Every 30-45 minutes" is his coaching advice and is shown as such (no study attached to it).

## Visuals
7 OSM motion scenes (`motion/pieces/posture_science`, all pass motion_qc), 11 Coverr stock clips (non-AI, free licence,
`source/stock/manifest.json`), his own IMG_2258 (gym walk), IMG_2253 (training) and IMG_3324 photo.

## QA
qa_render PASS except frozen frames = end card only (40.77 s -> end). Caption bar sampled #569FFA (= #56A0FB). head_check clean.
Grade: all PASS except neutral-cast CHECKs on the warm desk clip (b* 7.1 -> 2.5, 5.7 -> 2.6: warm practical lamps) and IMG_2258
(b* 4.1 -> 2.8, warm gym light), photo "richer" check (cast removed). Studio fix: grade.py g9 (curves interp=pchip).
Captions to confirm by ear: بتبقى قاعدة مايلة, مع (only one model hears it), عشان.

## Cover
`deliveries/posture_2026-11-01/OSM_no_perfect_posture_cover_1080x1920.{jpg,png}` from `cover.json` + `tools/make_cover.py`:
IMG_2258 at 1.50 s (his gym shot from the reel, the reel's own grade), scale 1.32, hook "مفيش قعدة مثالية", chip 41 = Swain 2019
("مفيش إجماع" = no consensus). Checks: grid crop, head column, blue chip #56A0FB all pass.
