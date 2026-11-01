# +1 kg on the scale in one day is not fat: voice-over reel (2026-11-01)

Video: `deliveries/scale_2026-11-01/OSM_scale_plus1kg_2026-11-01.mp4` (Git LFS), sha256 d71c4affe7d64c646541bc60d80b137d1e6387f00a3d834e41ad12ec0ab9e527
1080x1920, 30 fps, H.264, 52.7 s (50.3 s voice-over + end card). His voice-over unchanged; -14.0 LUFS, -1.7 dBTP.
Cover: `deliveries/scale_2026-11-01/OSM_scale_plus1kg_cover_1080x1920.{jpg,png}` (tools/make_cover.py, all checks pass).
The script screenshot in the source is not used anywhere.

## Research (PubMed)
- Hall 2008, Int J Obes 32:573-576: the 3,500 kcal/lb rule (~7,700 kcal/kg) is a rule of thumb. doi:10.1038/sj.ijo.0803720
- Orsama et al. 2014, Obes Facts 7:36-47: 80 adults, 4,657 daily weigh-ins; weight higher after weekends, lower in the week. doi:10.1159/000356147
"3-4 times a week", "every 2 weeks", "2-3 weeks" are his coaching rules, shown as such.

## Visuals
10 OSM motion scenes (`motion/pieces/scale_science`, all pass motion_qc), 2 Coverr clips (pizza, salt), his B-roll library
(`library/broll`): IMG_8385 (mid hook), IMG_7565 (progress photo + CTA), IMG_7546 (flex), IMG_7542 (online coaching).

## QA
qa_render PASS except frozen frames = end card only (51.03 s -> end). Caption bar sampled #569FFA (= #56A0FB).
Grade: all PASS except salt "richer" CHECK (cool cast removed on a black/white shot) and IMG_8385 skin CHECK (mint top + blue gym
light; face looked natural on the frames checked).
Captions to confirm by ear: حابس, اتوزن, لو (18.1 s).
head_check: 14 frames flagged at 4.27-5.87 s = pizza toppings (no face in the frame, checked): false positive.
