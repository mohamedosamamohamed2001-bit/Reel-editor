"""Back "LOVE" trend (Coach Osama 2026-11-16): his clip (source/pose.mp4) recut to the reference trend (ref/Trent1.mp4, reference only,
never in the output).

Reference, measured (screen recording of the Reel, 60 fps capture of 30 fps video): Reel length 12.467 s (it loops at 12.468 s).
  A 0.000-7.300  one continuous shot: the entrance (she walks in, sits, settles), colour
  B 7.300-10.300 hard cut to ONE frozen frame of the flex, black and white, exactly 3.0 s, no zoom
  C 10.300-12.467 the same moment in colour, moving again, slow (about half speed)
  Letters L / O / (V slot empty) / E: white bold serif, static from frame 0 to the end, stacked down her spine; her V-shaped back
  is the V. Positions / sizes: letters.py.
His version: A = shirt off + relaxed back (src 0.0-4.4, slowed to 7.3 s = 0.603x, 60 fps source so the slow motion is real frames,
stops before his clip's own light-leak at 4.5 s); B = the lat spread at src 22.95 s (sharpest frame, clearest V-taper) frozen in
black and white; C = the same lat spread from 22.95 s at 0.5x in colour. Colour: his own white balance (auto WB pushed the skin
magenta under the single warm light) + the measured contrast curve and gentle vibrance from tools/grade.py.
Output: 1080x1920 30 fps, video only (he adds the trend's song in Instagram with "Use audio"; the song starts at 0:00).

    .venv/bin/python projects/2026-11-16_back_trend/build.py
"""
import subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import letters  # noqa: E402

FPS = 30
SRC = P / "source/pose.mp4"
A_FR, B_FR, C_FR = 219, 90, 65                       # 7.300 s, 3.000 s, 2.167 s -> 374 frames = 12.467 s
A_IN, A_OUT = 0.0, 4.4
FREEZE = 22.95
CURVE = "curves=master='0/0 0.1961/0.1719 0.3922/0.4775 0.5882/0.7564 0.7216/0.8786 0.7843/0.9550 1/1':interp=pchip"
LOOK = f"{CURVE},vibrance=intensity=0.20"
BW = f"{CURVE},hue=s=0,eq=contrast=1.06"
UP = "scale=1080:1920:flags=lanczos,cas=strength=0.4"


def ff(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], check=True)


def main():
    W = P / "work"; W.mkdir(exist_ok=True); (P / "renders").mkdir(exist_ok=True)
    letters.render(W / "letters.png")
    sp = (A_OUT - A_IN) / (A_FR / FPS)
    c_len = C_FR / FPS * 0.5
    g = (f"[0:v]trim=start={A_IN}:end={A_OUT + 0.2},setpts=(PTS-STARTPTS)/{sp:.5f},fps={FPS},trim=end_frame={A_FR},setpts=PTS-STARTPTS,{LOOK},{UP}[a];"
         f"[0:v]trim=start={FREEZE}:end={FREEZE + 0.1},setpts=PTS-STARTPTS,trim=end_frame=1,{BW},{UP},loop=loop={B_FR - 1}:size=1:start=0,"
         f"setpts=N/{FPS}/TB,trim=end_frame={B_FR}[b];"
         f"[0:v]trim=start={FREEZE}:end={FREEZE + c_len + 0.2},setpts=(PTS-STARTPTS)/0.5,fps={FPS},trim=end_frame={C_FR},setpts=PTS-STARTPTS,{LOOK},{UP}[c];"
         f"[a][b][c]concat=n=3:v=1:a=0,format=yuv420p[v0];[v0][1:v]overlay=0:0:format=auto,format=yuv420p,"
         f"setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv[v]")
    out = P / "renders/back_love.mp4"
    ff(["-i", str(SRC), "-loop", "1", "-i", str(W / "letters.png"), "-filter_complex", g, "-map", "[v]", "-frames:v", str(A_FR + B_FR + C_FR),
        "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", "-an", str(out)])
    n = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0",
                        str(out)], capture_output=True, text=True).stdout.strip()
    print("output", out, "frames", n)


if __name__ == "__main__":
    main()
