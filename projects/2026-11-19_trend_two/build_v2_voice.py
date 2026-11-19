"""V2 (IMG_9205, green T-shirt) with HIS OWN original sound (Coach Osama 2026-11-19), instead of the trend's song.

His clip's sound = the gym's background music + his "Heyyy!" at 1.1-1.7 s (mouth wide open on camera). To keep the voice in sync
with his lips the clip plays at REAL speed in every repeat (the trend version slows it to the song's 2.167 s loop): 7 repeats x
52 frames (1.733 s) = 12.13 s, the clip's own audio under each repeat (8 ms fades at the cuts only, no clicks), mastered to
-14 LUFS / -1 dBTP. Same 7 captions, same style and place (under his chin), same grade as the trend version.

    .venv/bin/python projects/2026-11-19_trend_two/build_v2_voice.py
"""
import subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P)); sys.path.insert(0, str(P.parents[1] / "tools"))
import build as B          # noqa: E402  (captions, grade, constants of the trend version)
import render_edit as R    # noqa: E402

N = 52                     # whole clip, 1.733 s at 30 fps
REPS = len(B.LINES)


def main():
    W = P / "work"
    v = B.VERSIONS["v2"]
    src = P / "source" / v["src"]
    clip = W / "v2v_clip.mkv"
    B.ff(["-i", str(src), "-vf", f"fps={B.FPS},{v['grade']},scale=1080:1920:flags=lanczos,format=yuv420p", "-frames:v", str(N), "-an",
          "-c:v", "libx264", "-crf", "10", "-preset", "medium", str(clip)])
    B.text_pngs(W / "v2v_text", v["cap_top"])
    ins = ["-i", str(clip)] + sum((["-i", str(W / "v2v_text" / f"line_{i}.png")] for i in range(REPS)), [])
    g = [f"[0:v]split={REPS}" + "".join(f"[r{i}]" for i in range(REPS))]
    for i in range(REPS):
        g.append(f"[r{i}]setpts=PTS-STARTPTS[c{i}];[c{i}][{i + 1}:v]overlay=0:0[s{i}]")
    g.append("".join(f"[s{i}]" for i in range(REPS)) + f"concat=n={REPS}:v=1:a=0,format=yuv420p,"
             "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]")
    silent = W / "v2v_silent.mp4"
    B.ff([*ins, "-filter_complex", ";".join(g), "-map", "[v]", "-r", str(B.FPS), "-c:v", "libx264", "-crf", "14", "-preset", "slow",
          "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
          "-movflags", "+faststart", str(silent)])
    # his own sound: the clip's stereo AAC (stream 2; stream 1 is Apple's spatial audio), cut to exactly N frames per repeat
    d = N / B.FPS
    a = [f"[0:2]atrim=end={d:.6f},asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={d:.6f},atrim=end={d:.6f},"
         f"afade=t=in:d=0.008,afade=t=out:st={d - 0.008:.6f}:d=0.008,asplit={REPS}" + "".join(f"[a{i}]" for i in range(REPS)),
         "".join(f"[a{i}]" for i in range(REPS)) + f"concat=n={REPS}:v=0:a=1[o]"]
    mix = W / "v2v_audio.wav"
    B.ff(["-i", str(src), "-filter_complex", ";".join(a), "-map", "[o]", "-c:a", "pcm_s24le", str(mix)])
    out = P / "renders" / "trend_v2_own_voice.mp4"
    R.master_audio(mix, out, -14.0, -1.0, video=silent)
    print("output", out)


if __name__ == "__main__":
    main()
